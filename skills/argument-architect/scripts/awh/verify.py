"""Structural checks and dependency freshness; semantic reviews remain attestations."""

import hashlib
from pathlib import Path

from .contracts import ContractError, KINDS, canonical, validate


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def text_digest(text):
    return digest_bytes(text.encode('utf-8'))


def index(state):
    return {key: (kind, item) for kind in KINDS for key, item in state['entities'][kind].items()}


def dependencies(kind, item):
    fields = {
        'source': (), 'evidence': ('source_ids',), 'claim': ('evidence_ids',),
        'context': ('source_ids',), 'dissection': ('source_ids',),
        'plan': ('claim_ids', 'context_ids', 'source_ids'),
        'unit': ('claim_ids', 'evidence_ids', 'citation_ids', 'plan_ids'),
        'issue': ('claim_ids', 'evidence_ids'),
    }
    return [v for field in fields[kind] for v in item[field]]


def closure(state, ids):
    all_items = index(state)
    seen = {}
    def visit(key, stack):
        if key in stack:
            raise ContractError('Dependency cycle: ' + key)
        if key in seen:
            return
        if key not in all_items:
            raise ContractError('Unknown dependency: ' + key)
        kind, item = all_items[key]
        seen[key] = item['version']
        for dep in dependencies(kind, item):
            visit(dep, stack + [key])
    for key in ids:
        visit(key, [])
    return dict(sorted(seen.items()))


def local_artifact(root, source):
    value = source['artifact']
    if not value:
        return None
    rel = Path(value)
    path = (Path(root) / rel).resolve()
    if rel.is_absolute() or not path.is_relative_to(Path(root).resolve()):
        raise ContractError('Source artifact must be inside project: ' + value)
    return path


def changed_files(state, root):
    changed = []
    for source in state['entities']['source'].values():
        path = local_artifact(root, source)
        if path is not None and (not path.is_file() or digest_bytes(path.read_bytes()) != source['sha256']):
            changed.append(source['id'])
    return sorted(changed)


def compare_record(asserted, recorded):
    """Exact structural binding; no NLP, inference, tolerance or unit conversion."""
    fields = ('subject', 'metric', 'value', 'unit', 'population', 'conditions', 'analysis_version')
    missing = [key for key in fields if key not in asserted or key not in recorded]
    if missing:
        return {'status': 'unknown', 'missing': missing}
    mismatch = [key for key in fields if
                (set(asserted[key]) != set(recorded[key]) if key == 'conditions' else asserted[key] != recorded[key])]
    return {'status': 'record_mismatch' if mismatch else 'record_matched', 'mismatch': mismatch}


def assertion_checks(state, item):
    out = []
    for assertion in item.get('assertions', []):
        evidence = state['entities']['evidence'].get(assertion['evidence_id'])
        result = compare_record(assertion['record'], evidence.get('record', {}) if evidence else {})
        result['evidence_id'] = assertion['evidence_id']
        # Report presence separately. A matching scalar does not imply attribution or support.
        result['value_found'] = bool(evidence and 'record' in evidence and
                                     assertion['record']['value'] == evidence['record']['value'])
        out.append(result)
    return out


def validate_state(state, root):
    all_items = index(state)
    if len(all_items) != sum(len(state['entities'][kind]) for kind in KINDS):
        raise ContractError('IDs must be unique across entity kinds')
    targets = {'source_ids': 'source', 'evidence_ids': 'evidence', 'claim_ids': 'claim',
               'context_ids': 'context', 'citation_ids': 'source', 'plan_ids': 'plan'}
    for kind in KINDS:
        for key, item in state['entities'][kind].items():
            validate(item, kind)
            if key != item['id']:
                raise ContractError('ID/key mismatch: ' + key)
            for field, target in targets.items():
                for dep in item.get(field, []):
                    if dep not in state['entities'][target]:
                        raise ContractError(key + ': unknown ' + target + ' ' + dep)
            for assertion in item.get('assertions', []):
                if assertion['evidence_id'] not in closure(state, [key]):
                    raise ContractError(key + ': assertion evidence is not a dependency')
            if kind == 'source':
                local_artifact(root, item)
            elif kind == 'context':
                for rule in item['rules']:
                    if rule['source_id'] not in item['source_ids']:
                        raise ContractError(key + ': unlinked rule source')
                    source = state['entities']['source'][rule['source_id']]
                    purpose = {'official_policy': 'venue_policy', 'author': 'author_preference',
                               'pedagogy': 'pedagogical_principle', 'corpus': 'rhetorical_example'}[rule['basis']]
                    if purpose not in source['purposes']:
                        raise ContractError(key + ': rule/source purpose mismatch')
                    if rule['strength'] == 'must' and rule['basis'] not in ('official_policy', 'author'):
                        raise ContractError(key + ': corpus or pedagogy cannot create must rules')
                    if rule['strength'] == 'must' and source['identity_status'] != 'confirmed':
                        raise ContractError(key + ': must rule needs a confirmed policy/preference source')
            elif kind == 'dissection':
                for unit in item['units']:
                    span = unit['span']
                    if span['source_id'] not in item['source_ids']:
                        raise ContractError(key + ': unlinked span source')
                    source = state['entities']['source'][span['source_id']]
                    path = local_artifact(root, source)
                    if not path or not path.is_file():
                        continue  # Retain old annotations when a registered source becomes unavailable.
                    raw = path.read_bytes()
                    text = raw.decode('utf-8')
                    # A historical span may be stale after a source change. Validate exact
                    # extraction when its snapshot is current; preserve older annotations.
                    if (digest_bytes(raw) == source['sha256'] and span['document_sha256'] == source['sha256'] and
                            text[span['start']:span['end']] != span['quote']):
                        raise ContractError(key + ': dissection span mismatch')
            elif kind == 'plan':
                if item['selected_story'] >= len(item['stories']):
                    raise ContractError(key + ': selected_story outside stories')
                for story in item['stories']:
                    if not set(story['claim_ids']) <= set(item['claim_ids']):
                        raise ContractError(key + ': story has unlinked claims')
                for paragraph in item['paragraphs']:
                    if not set(paragraph['claim_ids']) <= set(item['claim_ids']):
                        raise ContractError(key + ': paragraph has unlinked claims')
                    if not set(paragraph['evidence_ids']) <= set(closure(state, item['claim_ids'])):
                        raise ContractError(key + ': paragraph has unlinked evidence')
            elif kind == 'issue':
                if not set(item.get('affected_units', [])) <= set(state['entities']['unit']):
                    raise ContractError(key + ': affected_units contains an unknown unit')
    closure(state, list(all_items))


def review_fresh(state, root, review, ids):
    if not review:
        return False
    expected = closure(state, ids)
    return (review.get('read_dependencies') == expected and
            not set(expected).intersection(changed_files(state, root)))


def stale_bindings(state, root):
    changed = set(changed_files(state, root))
    result = []
    for key, (kind, item) in index(state).items():
        expected = closure(state, dependencies(kind, item))
        if state['bindings'].get(key) != expected or set(expected).intersection(changed) or key in changed:
            result.append(key)
    return sorted(result)


def report(state, root):
    changed = changed_files(state, root)
    stale = stale_bindings(state, root)
    claims = {}
    units = {}
    for key, claim in state['entities']['claim'].items():
        review = state['assessments'].get(key)
        fresh = review_fresh(state, root, review, [key]) and not set(closure(state, [key])).intersection(stale)
        claims[key] = {'status': (review['status'] if fresh else 'stale') if review else 'not_assessed',
                       'assessment_origin': 'supplied_semantic_review' if review else 'none',
                       'record_checks': assertion_checks(state, claim)}
    for key, unit in state['entities']['unit'].items():
        review = state['unit_reviews'].get(key)
        fresh = review_fresh(state, root, review, [key]) and not set(closure(state, [key])).intersection(stale)
        own = ('reviewed' if fresh else 'stale') if review else 'unreviewed'
        blockers = [c for c in unit['claim_ids'] if claims[c]['status'] not in ('supported', 'partial')]
        if review and blockers:
            own = 'stale' if any(claims[c]['status'] == 'stale' for c in blockers) else 'blocked'
        checks = assertion_checks(state, unit)
        units[key] = {'status': own, 'blocking_claims': blockers, 'record_checks': checks,
                      'ready': own == 'reviewed' and not blockers and
                      all(c['status'] == 'record_matched' for c in checks)}
    issues = [i['id'] for i in state['entities']['issue'].values()
              if i['status'] != 'resolved' and i['severity'] in ('major', 'critical')]
    return {'revision': state['revision'], 'changed_source_files': changed, 'stale_entities': stale,
            'claims': claims, 'units': units,
            'unresolved_serious_issues': issues,
            'final_export_ready': bool(units) and all(v['ready'] for v in units.values()) and not issues and not changed,
            'limits': 'Fresh reviews are supplied attestations, not automatic proof of scientific validity.'}


def impact(state, ids):
    result = {}
    for key in index(state):
        if set(ids).intersection(closure(state, [key])):
            result[key] = index(state)[key][0]
    return result
