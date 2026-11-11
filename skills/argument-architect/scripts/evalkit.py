#!/usr/bin/env python3
import argparse
import json
import sys

from awh.contracts import ContractError, read_json
from awh.evalkit import summarize

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Summarize supplied manuscript-level evaluation annotations')
    parser.add_argument('annotations')
    args = parser.parse_args()
    try:
        print(json.dumps(summarize(read_json(args.annotations)), ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
