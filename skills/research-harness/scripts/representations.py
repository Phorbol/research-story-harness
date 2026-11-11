"""Track external shared-story inputs across media; freshness is not semantic approval."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text())


def fingerprint(path):
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def capture(project, mapping, output):
    root = Path(project).resolve()
    mapping = Path(mapping).resolve()
    research = read(root / 'research.json')
    known = {c['id'] for c in research.get('claims', [])}
    shared = [root / 'research.json', root / 'story.json', root / 'brief.txt', mapping]
    shared = list(dict.fromkeys(shared))
    if any(not p.is_file() for p in shared):
        raise ValueError('Shared research.json, story.json, brief.txt and mapping are required')
    items = []
    ids = set()
    for item in read(mapping)['representations']:
        if item['id'] in ids:
            raise ValueError('Duplicate representation ID')
        ids.add(item['id'])
        if not item.get('claim_ids') or set(item['claim_ids']) - known:
            raise ValueError(f"Unregistered or missing claims: {item['id']}")
        paths = [root / item['path'], *(root / p for p in item.get('source_paths', []))]
        if any(not p.is_file() for p in paths):
            raise ValueError(f"Missing artifact or source: {item['id']}")
        items.append({**item, 'inputs': {str(p.resolve()): fingerprint(p) for p in paths}})
    result = {'schema_version': 1, 'project': str(root),
              'shared_inputs': {str(p): fingerprint(p) for p in shared},
              'representations': items,
              'meaning': 'Byte freshness only. No scientific, semantic, visual or user approval.'}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


def check(record):
    state = read(record)
    shared = [p for p, value in state['shared_inputs'].items() if fingerprint(p) != value]
    items = []
    for item in state['representations']:
        changed = [p for p, value in item['inputs'].items() if fingerprint(p) != value]
        items.append({'id': item['id'], 'needs_review': bool(shared or changed),
                      'changed_shared': shared, 'changed_local': changed})
    return {'representations': items, 'needs_review': any(i['needs_review'] for i in items),
            'meaning': 'Conservative file dependency check, not semantic proof; no artifacts changed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    c = sub.add_parser('capture')
    c.add_argument('--project', required=True)
    c.add_argument('--map', required=True)
    c.add_argument('--out', required=True)
    c = sub.add_parser('check')
    c.add_argument('record')
    args = parser.parse_args()
    try:
        result = capture(args.project, args.map, args.out) if args.command == 'capture' else check(args.record)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get('needs_review') else 0


if __name__ == '__main__':
    raise SystemExit(main())
