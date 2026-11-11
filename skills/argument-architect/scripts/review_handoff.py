#!/usr/bin/env python3
import argparse,json,sys
from awh.contracts import read_json
from awh.handoff import check_handoff
if __name__=='__main__':
 p=argparse.ArgumentParser(description='Check declared factual-source coverage before blind review');p.add_argument('input');a=p.parse_args()
 try:
  d=read_json(a.input);print(json.dumps(check_handoff(d['required'],d['available']),ensure_ascii=False,indent=2))
 except (ValueError,OSError,KeyError,TypeError) as e:
  print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
