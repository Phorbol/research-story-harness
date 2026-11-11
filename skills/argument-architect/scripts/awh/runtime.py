"""Single-writer, atomic checkpoints and issue-specific candidate acceptance."""

import copy
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .contracts import ContractError, KINDS, canonical, read_json, validate
from .verify import (assertion_checks, changed_files, closure, dependencies, digest_bytes, impact, index,
                     local_artifact, report, stale_bindings, text_digest, validate_state)


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_write(path, content):
    path = Path(path)
    temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8') as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


class Project:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.meta = self.root / '.academic'

    @contextmanager
    def locked(self):
        self.meta.mkdir(parents=True, exist_ok=True)
        lock = self.meta / 'writer.lock'
        try:
            handle = lock.open('x', encoding='utf-8')
        except FileExistsError:
            raise ContractError('Writer lock exists. Inspect its PID; remove only after confirming no writer is running.')
        try:
            with handle:
                handle.write(str(os.getpid()))
                handle.flush()
            yield
        finally:
            lock.unlink()

    def load(self):
        head = self.meta / 'HEAD'
        if not head.exists():
            raise ContractError('Project is not initialized')
        name = head.read_text(encoding='utf-8').strip()
        if Path(name).name != name or not name.endswith('.json'):
            raise ContractError('Invalid checkpoint pointer')
        state = read_json(self.meta / 'checkpoints' / name)
        if state.get('format') != 1:
            raise ContractError('Unsupported project format')
        return state

    def _save(self, state, event):
        state['revision'] += 1
        state['events'].append({'revision': state['revision'], 'time': now(), **event})
        name = '{:06d}-{}.json'.format(state['revision'], uuid.uuid4().hex)
        checkpoints = self.meta / 'checkpoints'
        checkpoints.mkdir(exist_ok=True)
        atomic_write(checkpoints / name, json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        # The pointer is the commit point. A crash before replacement leaves an unused checkpoint.
        atomic_write(self.meta / 'HEAD', name + '\n')

    def init(self):
        with self.locked():
            if (self.meta / 'HEAD').exists():
                raise ContractError('Project already initialized; existing content preserved')
            state = {'format': 1, 'revision': 0, 'entities': {kind: {} for kind in KINDS},
                     'assessments': {}, 'unit_reviews': {}, 'patches': {}, 'bindings': {}, 'events': [],
                     'budget': {'max_accepts': 20, 'accepted': 0, 'stop_reason': ''}}
            self._save(state, {'action': 'init'})
        return self.status()

    def _active(self, state):
        if state['budget']['stop_reason']:
            raise ContractError('Run stopped: ' + state['budget']['stop_reason'] + '. Use resume with a reason.')

    def put(self, kind, payload):
        if kind not in KINDS:
            raise ContractError('Unknown entity kind')
        with self.locked():
            state = self.load()
            self._active(state)
            item = copy.deepcopy(payload)
            key = item.get('id', '')
            old = state['entities'][kind].get(key)
            item['version'] = old['version'] + 1 if old else 1
            if kind == 'source':
                path = local_artifact(self.root, item)
                if path:
                    if not path.is_file():
                        raise ContractError('Missing source artifact: ' + str(path))
                    item['sha256'] = digest_bytes(path.read_bytes())
                else:
                    item['sha256'] = ''
                    if item.get('extraction_status') == 'checked':
                        raise ContractError('Checked extraction requires a local snapshot')
            if kind == 'issue' and item.get('status') == 'resolved':
                raise ContractError('Resolve issues through an accepted patch, not put')
            validate(item, kind)
            if (kind == 'unit' and old and
                    canonical({**item, 'version': old['version']}) != canonical(old)):
                raise ContractError('Existing prose must be changed through a candidate patch')
            binding = closure(state, dependencies(kind, item))
            if (old and canonical({**item, 'version': old['version']}) == canonical(old)
                    and state['bindings'].get(key) == binding):
                return {'changed': False, 'revision': state['revision'], 'id': key}
            state['entities'][kind][key] = item
            state['bindings'][key] = binding
            if kind == 'dissection':
                for unit in item['units']:
                    source = state['entities']['source'].get(unit['span']['source_id'])
                    path = local_artifact(self.root, source) if source else None
                    if not path or not path.is_file():
                        raise ContractError('New dissection needs a current local text snapshot')
                    if (unit['span']['document_sha256'] != source['sha256'] or
                            digest_bytes(path.read_bytes()) != source['sha256']):
                        raise ContractError('New dissection must reference the current source snapshot')
            validate_state(state, self.root)
            self._save(state, {'action': 'put', 'kind': kind, 'id': key, 'version': item['version']})
            return {'changed': True, 'revision': state['revision'], 'id': key,
                    'version': item['version'], 'affected': impact(state, [key])}

    def _source_checks(self, state, ids, supplied, require_all=True):
        deps = closure(state, ids)
        scientific = {key for key in deps if key in state['entities']['source'] and
                      'scientific_evidence' in state['entities']['source'][key]['purposes']}
        checked = {entry['source_id'] for entry in supplied}
        source_ids = set(deps).intersection(state['entities']['source'])
        if not scientific or not checked <= source_ids or (require_all and not scientific <= checked):
            raise ContractError('Review must inspect all linked scientific source snapshots with locators')
        for key in scientific:
            source = state['entities']['source'][key]
            if (source['identity_status'] != 'confirmed' or source['extraction_status'] != 'checked'
                    or not source['artifact']):
                raise ContractError('Source identity or extraction unconfirmed: ' + key)
        if set(deps).intersection(changed_files(state, self.root)):
            raise ContractError('Raw material changed; update source and evidence before review')
        # The current entity is being reviewed; all of its upstream records must
        # already refer to the current raw materials.
        if (set(deps) - set(ids)).intersection(stale_bindings(state, self.root)):
            raise ContractError('Upstream records are stale; refresh evidence/context/plan before review')

    def assess(self, review):
        validate(review, 'assessment')
        with self.locked():
            state = self.load()
            self._active(state)
            key = review['claim_id']
            if key not in state['entities']['claim']:
                raise ContractError('Unknown claim: ' + key)
            claim = state['entities']['claim'][key]
            if review['status'] in ('supported', 'partial'):
                self._source_checks(state, [key], review['source_checks'])
                checks = assertion_checks(state, claim)
                if any(v['status'] == 'record_mismatch' for v in checks):
                    raise ContractError('Attributed numeric record mismatch')
                if review['status'] == 'supported':
                    if not claim['warrant'].strip() or any(v != 'pass' for v in review['checks'].values()):
                        raise ContractError('Supported requires a warrant and all supplied semantic checks to pass')
                    if any(v['status'] != 'record_matched' for v in checks):
                        raise ContractError('Supported requires complete attributed numeric records')
                elif review['checks']['support'] == 'fail':
                    raise ContractError('Failed support cannot be recorded as partial')
            # Review decisions are part of the claim version so downstream prose is reopened.
            claim['version'] += 1
            state['bindings'][key] = closure(state, dependencies('claim', claim))
            state['assessments'][key] = {**review, 'read_dependencies': closure(state, [key]), 'time': now()}
            self._save(state, {'action': 'assess', 'id': key, 'status': review['status'],
                               'origin': 'supplied_semantic_review'})
            return self.status()

    def _unit_review(self, state, review):
        validate(review, 'unit-review')
        key = review['unit_id']
        if key not in state['entities']['unit']:
            raise ContractError('Unknown unit: ' + key)
        unit = state['entities']['unit'][key]
        if review['text_sha256'] != text_digest(unit['text']):
            raise ContractError('Unit review was written for different text: ' + key)
        if any(v != 'pass' for v in review['checks'].values()):
            raise ContractError('Unit semantic review incomplete or failed: ' + key)
        self._source_checks(state, [key], review['source_checks'])
        statuses = report(state, self.root)['claims']
        if any(statuses[c]['status'] not in ('supported', 'partial') for c in unit['claim_ids']):
            raise ContractError('Unit has unassessed, stale or unsupported claims: ' + key)
        if any(v['status'] != 'record_matched' for v in assertion_checks(state, unit)):
            raise ContractError('Unit has mismatched or incomplete attributed records: ' + key)
        binding = closure(state, dependencies('unit', unit))
        if state['bindings'].get(key) != binding:
            unit['version'] += 1
            state['bindings'][key] = binding
        state['unit_reviews'][key] = {**review, 'read_dependencies': closure(state, [key]), 'time': now()}

    def review_unit(self, review):
        with self.locked():
            state = self.load()
            self._active(state)
            self._unit_review(state, review)
            self._save(state, {'action': 'review_unit', 'id': review['unit_id']})
            return {'revision': state['revision'], 'unit_id': review['unit_id'],
                    'origin': 'supplied_semantic_review'}

    def _check_patch(self, state, patch):
        validate(patch, 'patch')
        if patch['claim_delta']:
            raise ContractError('Scientific claim changes must be put and reassessed before a prose patch')
        if patch['base_revision'] > state['revision']:
            raise ContractError('Patch base is in the future')
        replacements = patch['replacements']
        if len({u['id'] for u in replacements}) != len(replacements):
            raise ContractError('Duplicate replacement IDs')
        if set(patch['affected_units']) != {u['id'] for u in replacements}:
            raise ContractError('affected_units must exactly match replacements')
        required = closure(state, patch['affected_units'] + patch['issue_ids'])
        for unit in replacements:
            old = state['entities']['unit'][unit['id']]
            if unit['version'] != old['version'] + 1:
                raise ContractError('Replacement version mismatch: ' + unit['id'])
            # New dependencies must also be included in the read set.
            extra = unit['claim_ids'] + unit['evidence_ids'] + unit['citation_ids'] + unit['plan_ids']
            required.update(closure(state, extra))
        actual = closure(state, patch['read_dependencies'])
        if patch['read_dependencies'] != actual or not set(required) <= set(actual):
            raise ContractError('Incomplete or stale patch read_dependencies')
        if set(actual).intersection(changed_files(state, self.root)):
            raise ContractError('Patch depends on changed source files')
        for issue_id in patch['issue_ids']:
            issue = state['entities']['issue'][issue_id]
            if issue['status'] != 'open':
                raise ContractError('Issue is not open: ' + issue_id)
            if not set(issue.get('affected_units', [])) <= set(patch['affected_units']):
                raise ContractError('Patch omits units required to resolve issue: ' + issue_id)
        staged = copy.deepcopy(state)
        for unit in replacements:
            staged['entities']['unit'][unit['id']] = copy.deepcopy(unit)
            staged['bindings'][unit['id']] = closure(staged, dependencies('unit', unit))
        validate_state(staged, self.root)
        return staged

    def propose(self, patch):
        with self.locked():
            state = self.load()
            self._active(state)
            if patch.get('id') in state['patches']:
                raise ContractError('Patch ID already used')
            self._check_patch(state, patch)
            state['patches'][patch['id']] = {'candidate': copy.deepcopy(patch), 'status': 'proposed'}
            self._save(state, {'action': 'propose', 'id': patch['id']})
            return {'revision': state['revision'], 'patch_id': patch['id'], 'status': 'proposed'}

    def accept(self, patch_id, review):
        validate(review, 'patch-review')
        with self.locked():
            state = self.load()
            self._active(state)
            budget = state['budget']
            if budget['accepted'] >= budget['max_accepts']:
                raise ContractError('Accepted patch budget exhausted; set an explicit new budget to continue')
            saved = state['patches'].get(patch_id)
            if not saved or saved['status'] != 'proposed':
                raise ContractError('Patch is not proposed')
            patch = saved['candidate']
            staged = self._check_patch(state, patch)
            if review['patch_id'] != patch_id:
                raise ContractError('Review patch ID mismatch')
            if review['new_serious_errors'] != 'pass' or review['preserved_correct_content'] != 'pass':
                raise ContractError('Patch invariants not passed')
            resolutions = review['issue_resolutions']
            if ({v['issue_id'] for v in resolutions} != set(patch['issue_ids']) or
                    len(resolutions) != len(patch['issue_ids']) or any(v['result'] != 'pass' for v in resolutions)):
                raise ContractError('Every targeted issue needs its own passing resolution test')
            unit_reviews = review['units']
            if ({v['unit_id'] for v in unit_reviews} != set(patch['affected_units']) or
                    len(unit_reviews) != len(patch['affected_units'])):
                raise ContractError('Review must cover exactly all affected units')
            # Reverting to a previously accepted text needs an explicit scientific decision first.
            for unit in patch['replacements']:
                hashes = [e.get('text_hashes', {}).get(unit['id']) for e in state['events']
                          if e['action'] == 'accept']
                if text_digest(unit['text']) in hashes:
                    raise ContractError('Text oscillation detected; stop and record an author decision')
            for unit_review in unit_reviews:
                self._unit_review(staged, unit_review)
            for issue_id in patch['issue_ids']:
                staged['entities']['issue'][issue_id]['status'] = 'resolved'
                staged['entities']['issue'][issue_id]['version'] += 1
            staged['patches'][patch_id].update({'status': 'accepted', 'review': copy.deepcopy(review)})
            staged['budget']['accepted'] += 1
            self._save(staged, {'action': 'accept', 'id': patch_id,
                'text_hashes': {u['id']: text_digest(u['text']) for u in patch['replacements']}})
            return {'revision': staged['revision'], 'patch_id': patch_id, 'status': 'accepted'}

    def reject(self, patch_id, reason):
        if not reason.strip():
            raise ContractError('Rejection reason is required')
        with self.locked():
            state = self.load()
            saved = state['patches'].get(patch_id)
            if not saved or saved['status'] != 'proposed':
                raise ContractError('Patch is not proposed')
            saved.update({'status': 'rejected', 'reason': reason})
            self._save(state, {'action': 'reject', 'id': patch_id, 'reason': reason})
            return {'revision': state['revision'], 'status': 'rejected'}

    def control(self, action, reason, max_accepts=None):
        if not reason.strip():
            raise ContractError('A reason is required')
        with self.locked():
            state = self.load()
            if action == 'stop':
                state['budget']['stop_reason'] = reason
            elif action == 'resume':
                state['budget']['stop_reason'] = ''
            elif action == 'budget':
                if max_accepts is None or max_accepts < state['budget']['accepted']:
                    raise ContractError('Budget must be at least the accepted count')
                state['budget']['max_accepts'] = max_accepts
            else:
                raise ContractError('Unknown control action')
            self._save(state, {'action': action, 'reason': reason})
            return {'revision': state['revision'], 'budget': state['budget']}

    def restore(self, checkpoint):
        # Forward restore never rewinds evidence or revives old semantic decisions.
        if Path(checkpoint).name != checkpoint:
            raise ContractError('Use a checkpoint filename from history')
        with self.locked():
            state = self.load()
            old = read_json(self.meta / 'checkpoints' / checkpoint)
            if old.get('format') != 1:
                raise ContractError('Unsupported checkpoint')
            restored = []
            for key, unit in old['entities']['unit'].items():
                if key not in state['entities']['unit']:
                    continue
                current = state['entities']['unit'][key]
                if canonical({**unit, 'version': current['version']}) == canonical(current):
                    continue
                state['entities']['unit'][key] = {**unit, 'version': current['version'] + 1}
                state['bindings'][key] = closure(state, dependencies('unit', unit))
                restored.append(key)
                state['unit_reviews'].pop(key, None)
            validate_state(state, self.root)
            self._save(state, {'action': 'restore_prose', 'checkpoint': checkpoint, 'units': restored})
            return {'revision': state['revision'], 'restored_units': restored,
                    'note': 'Current evidence and claims retained. Restored prose needs fresh review.'}

    def status(self):
        state = self.load()
        validate_state(state, self.root)
        return {**report(state, self.root), 'budget': state['budget']}

    def export(self, output, final=False, blind=False, clean=False):
        if final and blind:
            raise ContractError("Blind review export and final publication export are separate modes")
        state = self.load()
        validate_state(state, self.root)
        status = report(state, self.root)
        if final and not status['final_export_ready']:
            raise ContractError('Final export blocked; inspect audit for stale reviews or unresolved issues')
        output = Path(output).resolve()
        if not output.is_relative_to(self.root) or output.is_relative_to(self.meta):
            raise ContractError('Export must be inside the project and outside .academic')
        if output.exists():
            raise ContractError('Export path exists; choose a new versioned filename')
        clean_prose = blind or clean
        lines = [] if clean_prose else ['# Manuscript', '', 'Revision: ' + str(state['revision']), '',
                 'Review state: ' + ('supplied reviews current' if final else 'WORKING DRAFT'), '']
        for key, unit in state['entities']['unit'].items():
            lines += ['## ' + unit['kind'] + ('' if clean_prose else ' — ' + key), '', unit['text'], '']
            if not final and not clean_prose:
                lines += ['<!-- claims: ' + ', '.join(unit['claim_ids']) + '; status: ' +
                          status['units'][key]['status'] + ' -->', '']
        output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation preserves existing deliverables.
        with output.open('x', encoding='utf-8') as handle:
            handle.write('\n'.join(lines))
        return {'path': str(output), 'revision': state['revision'], 'mode': ('final-clean' if final else 'working-clean') if clean else ('blind-review' if blind else ('final' if final else 'working')),
                'limits': status['limits']}
