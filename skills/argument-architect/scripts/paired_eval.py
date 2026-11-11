#!/usr/bin/env python3
"""Summarize externally supplied scientific-writing experiment annotations,no model calls."""
import argparse,json,sys
from awh.contracts import read_json
from awh.paired_eval import analyze
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');a=p.parse_args()
 try:
  data=read_json(a.input)
  print(json.dumps(analyze(data['cells'], data['reviews'], data['version_order']),ensure_ascii=False,indent=2,allow_nan=False))
 except (ValueError,OSError,KeyError,TypeError) as e:
  print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
