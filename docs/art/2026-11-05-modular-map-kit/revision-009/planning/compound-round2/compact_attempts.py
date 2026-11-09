"""Reduce repeated per-route clearance rows; preserve counts, body rows and rejection witnesses."""
import json,hashlib,sys
from collections import Counter
from pathlib import Path
O=Path(__file__).parent

def compact(d):
 for r in d['records']:
  routes=r.pop('routeAttempts',None)
  if routes is None:continue
  counts=Counter((q['strategy'],q['roadId'],tuple(q['nodeRangeInclusive']),tuple(q['rejectedBy'])) for q in routes)
  r['routeAttemptsSummary']=[{'strategy':s,'roadId':road,'nodeRangeInclusive':list(nr),'rejectedBy':list(bad),'attemptCount':n} for (s,road,nr,bad),n in counts.items()]
  r['totalRouteAttempts']=len(routes)
  accepted=[q for q in routes if not q['rejectedBy']]
  if accepted:r['acceptedRouteEvidence']=accepted
 d['detailPolicy']='Each native asset@scale/anchor body row retained; repetitive route clearance vectors reduced to exact counted strategy/road/reject patterns. Full first failure witness per rule and accepted route/option polygons retained. Not a historical log copy.'
 return d
if __name__=='__main__':
 for arg in sys.argv[1:]:
  f=O/f'source-{int(arg):04d}-attempts.json';d=json.loads(f.read_text());f.write_text(json.dumps(compact(d),ensure_ascii=False,indent=2)+'\n')
