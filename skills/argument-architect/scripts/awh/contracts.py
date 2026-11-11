"""Validate the deliberately small JSON Schema vocabulary used by this kit."""

import json
import math
import re
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parents[2] / 'schemas'
KINDS = ('source', 'evidence', 'claim', 'context', 'dissection', 'plan', 'unit', 'issue')


class ContractError(ValueError):
    pass


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ContractError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    def invalid(value):
        raise ContractError('Non-finite JSON number: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=_pairs, parse_constant=invalid)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def validate(value, name):
    schema = read_json(SCHEMAS / (name + '.schema.json'))
    _validate(value, schema, '$')


def _validate(value, schema, path):
    supported = {'$schema', 'title', '$ref', 'type', 'properties', 'required', 'additionalProperties',
                 'items', 'minItems', 'uniqueItems', 'minLength', 'minimum', 'enum', 'pattern'}
    unknown = set(schema) - supported
    if unknown:
        raise ContractError('Unsupported schema keywords: ' + ', '.join(sorted(unknown)))
    if '$ref' in schema:
        ref = schema['$ref']
        if not re.fullmatch(r'[a-z-]+\.schema\.json', ref):
            raise ContractError('Only bundled schema references are supported')
        return _validate(value, read_json(SCHEMAS / ref), path)
    types = {
        'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
        'string': lambda v: isinstance(v, str),
        'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
        'number': lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v),
    }
    kind = schema.get('type')
    if kind and (kind not in types or not types[kind](value)):
        raise ContractError(path + ': expected ' + str(kind))
    if 'enum' in schema and value not in schema['enum']:
        raise ContractError(path + ': value outside enum')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                raise ContractError(path + ': missing ' + key)
        props = schema.get('properties', {})
        extra = schema.get('additionalProperties', True)
        for key, child in value.items():
            if key in props:
                _validate(child, props[key], path + '.' + key)
            elif extra is False:
                raise ContractError(path + ': unexpected field ' + key)
            elif isinstance(extra, dict):
                _validate(child, extra, path + '.' + key)
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            raise ContractError(path + ': too few items')
        if schema.get('uniqueItems') and len({canonical(v) for v in value}) != len(value):
            raise ContractError(path + ': duplicate items')
        for index, child in enumerate(value):
            _validate(child, schema.get('items', {}), path + '[' + str(index) + ']')
    elif isinstance(value, str):
        if len(value.strip()) < schema.get('minLength', 0):
            raise ContractError(path + ': empty string')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ContractError(path + ': invalid identifier')
    elif kind in ('number', 'integer') and value < schema.get('minimum', -math.inf):
        raise ContractError(path + ': below minimum')
