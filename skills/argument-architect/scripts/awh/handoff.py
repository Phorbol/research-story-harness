"""Check declared factual-source coverage before a controlled blind review."""
from .contracts import ContractError

class HandoffError(ContractError): pass

def check_handoff(required,available):
 def collect(rows):
  result={}
  for x in rows:
   key=x['source_id'];version=x['sha256']
   if not isinstance(key,str) or not key.strip() or not isinstance(version,str) or not version.strip():raise HandoffError('Source identity and version must be nonempty strings')
   if key in result:raise HandoffError('Duplicate source identity')
   result[key]=version
  return result
 need=collect(required);have=collect(available)
 missing=sorted(set(need)-set(have));drift=sorted(k for k in need.keys()&have.keys() if need[k]!=have[k])
 if missing or drift:raise HandoffError('Incomplete reviewer source handoff:missing='+repr(missing)+';version_mismatch='+repr(drift))
 return {'covered':True,'required_sources':len(need),'available_sources':len(have),'scope':'Declared factual source identities/versions only;not proof of reading,source truth,access isolation or scientific entailment.'}
