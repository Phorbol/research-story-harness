#!/usr/bin/env python3
"""Validate and summarize an externally generated and blind-rated 2x2 experiment."""
import argparse
import json
import sys
from awh.contracts import read_json
from awh.ablation import summarize

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', help='JSON object with cells and reviews')
    args = parser.parse_args()
    try:
        data = read_json(args.experiment)
        print(json.dumps(summarize(data['cells'], data['reviews']), ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
