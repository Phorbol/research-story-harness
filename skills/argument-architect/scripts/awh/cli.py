import argparse
import copy
import difflib
import json
import sys
from pathlib import Path

from .contracts import ContractError, KINDS, read_json, validate
from .runtime import Project
from .verify import closure, compare_record, impact, index, text_digest


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def parser():
    p = argparse.ArgumentParser(description='Evidence-linked local academic writing harness (no LLM/network).')
    p.add_argument('--project', default='.', help='Research project directory, default current directory')
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('init', 'audit', 'status', 'snapshot', 'history', 'capabilities'):
        sub.add_parser(name)
    put = sub.add_parser('put', help='Register or update an entity from a JSON file; versions are managed')
    put.add_argument('kind', choices=KINDS)
    put.add_argument('file')
    for name in ('assess', 'review-unit', 'propose'):
        sub.add_parser(name).add_argument('file')
    for name in ('deps', 'impact'):
        sub.add_parser(name).add_argument('ids', nargs='+')
    sub.add_parser('inspect').add_argument('id')
    sub.add_parser('diff').add_argument('patch_id')
    accept = sub.add_parser('accept')
    accept.add_argument('patch_id')
    accept.add_argument('--review', required=True)
    reject = sub.add_parser('reject')
    reject.add_argument('patch_id')
    reject.add_argument('--reason', required=True)
    export = sub.add_parser('export')
    export.add_argument('output')
    export.add_argument('--clean', action='store_true', help='Scientific prose only; may combine with --final without changing approval checks')
    export_mode = export.add_mutually_exclusive_group()
    export_mode.add_argument('--final', action='store_true')
    export_mode.add_argument('--blind', action='store_true', help='Prose only, without harness review metadata or unit IDs; no final approval implied')
    for name in ('stop', 'resume', 'budget'):
        control = sub.add_parser(name)
        control.add_argument('--reason', required=True)
        if name == 'budget':
            control.add_argument('--max-accepts', required=True, type=int)
    sub.add_parser('restore-prose').add_argument('checkpoint')
    schema = sub.add_parser('validate')
    schema.add_argument('schema')
    schema.add_argument('file')
    pair = sub.add_parser('compare-records')
    pair.add_argument('asserted')
    pair.add_argument('recorded')
    template = sub.add_parser('review-template')
    template.add_argument('id')
    return p


def run(args):
    project = Project(args.project)
    command = args.command
    if command == 'capabilities':
        return {'implemented': ['strict bundled JSON schemas', 'exact attributed record comparison',
            'raw file drift detection', 'transitive version invalidation', 'single writer lock',
            'atomic checkpoint pointer', 'candidate diff', 'issue-specific acceptance',
            'forward prose restore', 'blind review prose export', 'clean final prose export', 'accepted-patch budget', 'explicit stop', 'repeat-text stop'],
            'not_implemented': ['automatic scientific entailment', 'NLP proposition extraction',
                'automatic literature search', 'PDF parsing/OCR', 'LLM orchestration',
                'host hooks/tool isolation', 'parallel worker scheduling', 'automatic retries',
                'token/dollar/time budget enforcement', 'proof of reviewer independence'],
            'review_origin': 'Human or agent supplied; stored checks are attestations, not independent evidence.'}
    if command == 'validate':
        validate(read_json(args.file), args.schema)
        return {'valid': True, 'schema': args.schema}
    if command == 'compare-records':
        return compare_record(read_json(args.asserted), read_json(args.recorded))
    if command == 'init':
        return project.init()
    if command == 'put':
        return project.put(args.kind, read_json(args.file))
    if command in ('audit', 'status'):
        return project.status()
    if command == 'assess':
        return project.assess(read_json(args.file))
    if command == 'review-unit':
        return project.review_unit(read_json(args.file))
    if command == 'propose':
        return project.propose(read_json(args.file))
    if command == 'accept':
        return project.accept(args.patch_id, read_json(args.review))
    if command == 'reject':
        return project.reject(args.patch_id, args.reason)
    if command == 'export':
        return project.export(args.output, args.final, blind=args.blind, clean=args.clean)
    if command in ('stop', 'resume', 'budget'):
        return project.control(command, args.reason, getattr(args, 'max_accepts', None))
    if command == 'restore-prose':
        return project.restore(args.checkpoint)
    state = project.load()
    if command == 'snapshot':
        return state
    if command == 'history':
        return {'events': state['events'], 'checkpoints': sorted(p.name for p in (project.meta / 'checkpoints').glob('*.json'))}
    if command == 'deps':
        return closure(state, args.ids)
    if command == 'impact':
        closure(state, args.ids)
        return impact(state, args.ids)
    if command == 'inspect':
        found = index(state).get(args.id)
        if not found:
            raise ContractError('Unknown ID: ' + args.id)
        return {'kind': found[0], 'entity': found[1], 'dependencies': closure(state, [args.id])}
    if command == 'diff':
        saved = state['patches'].get(args.patch_id)
        if not saved:
            raise ContractError('Unknown patch: ' + args.patch_id)
        diffs = {}
        for unit in saved['candidate']['replacements']:
            old = state['entities']['unit'][unit['id']]
            diffs[unit['id']] = ''.join(difflib.unified_diff(old['text'].splitlines(True),
                unit['text'].splitlines(True), fromfile='current/' + unit['id'], tofile='candidate/' + unit['id']))
        return {'patch_id': args.patch_id, 'status': saved['status'], 'diffs': diffs}
    if command == 'review-template':
        found = index(state).get(args.id)
        if not found or found[0] not in ('claim', 'unit'):
            raise ContractError('Review templates are available for claims or units')
        kind, entity = found
        result = {'reviewer': '', 'rationale': '',
            'checks': {k: 'unknown' for k in ('support', 'scope', 'attribution', 'alternatives', 'uncertainty')},
            'source_checks': [{'source_id': key, 'locator': '', 'observation': '', 'interpretation': ''}
                for key in closure(state, [args.id]) if key in state['entities']['source'] and
                'scientific_evidence' in state['entities']['source'][key]['purposes']]}
        if kind == 'claim':
            result.update({'claim_id': args.id, 'status': 'not_assessed'})
        else:
            result.update({'unit_id': args.id, 'text_sha256': text_digest(entity['text']),
                           'extracted_propositions': []})
        return result
    raise ContractError('Unknown command')


def main():
    try:
        emit(run(parser().parse_args()))
        return 0
    except (ContractError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
