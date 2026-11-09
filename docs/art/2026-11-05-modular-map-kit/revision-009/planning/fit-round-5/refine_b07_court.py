#!/usr/bin/env python3
"""Keep initial file immutable; replace generic U-court floor with checked partial-void patch."""
from pathlib import Path
# refuse frozen v2 overwrite
if (Path(__file__).resolve().parent/'fifth-expansion-batch-v2.json').exists():
 raise SystemExit('Frozen v2 exists; do not rebuild; consume import-contract.json.')
exec(compile(Path(__file__).with_name('plan_fifth.py').read_text().split('for idx in sorted(localids')[0],'readonly-local-context','exec'),globals())
f=O/'fifth-expansion-batch.json';oldsha=sha(f);b=read(f);changes=[]
for host in b['buildings']:
 if host['assetId']!='B07':continue
 pid=host['id'];scale=host['uniformScale'];anchor=host['anchorMap'];void=host['courtyardVoidPolygonMap'];body=host['footprintPolygonMap'];removed=[s for s in b['groundSurfaces'] if s['owner']==pid and '-walk-'not in s['id']];b['groundSurfaces']=[s for s in b['groundSurfaces'] if s not in removed]
 p=[add(add(anchor,mul(u,x*scale)),mul(n,y*scale)) for x,y in [(-1,1),(3,1),(3,4),(-1,4)]]
 assert all(inside(v,void) for v in p) and pp(p,body)>.15
 q=audit(p,host['clusterOfSource']['sourceIndices'],[x['footprintPolygonMap'] for x in b['buildings'] if x['id']!=pid]);assert good(q)
 assert any(pp(p,w)==0 for w in host['visualApproach']['polygonsMap'])
 surface={'id':pid+'-partial-inner-court','owner':pid,'materialId':'S01-paving','polygonMap':p,'purpose':'12sqm partial courtyard meeting patch inside actual U void; remainder unfilled; attached to native-step walk','staticClearance':q,'ownOccupiedUGapMetres':pp(p,body),'doesNotFillWholeVoid':True}
 b['groundSurfaces'].append(surface)
 scene=next(s for s in b['scenes'] if s['moduleIds'][0]==pid);scene['groundSurfaceIds']=[s['id'] for s in b['groundSurfaces'] if s['owner']==pid];changes.append({'owner':pid,'removedSurfaceIds':[s['id'] for s in removed],'addedSurfaceId':surface['id'],'reason':'generic carrier court/apron would not distinguish U-shaped occupied body from open void; replace with checked partial-void patch','nativeGroundBodyUnchanged':True})
b['version']='009-fit-round5-local-infill-v2';b['supersedesInitialGroundOnly']={'path':str(f),'sha256':oldsha,'changes':changes};write('fifth-expansion-batch-v2.json',b)
summary=read(O/'joint-fit-summary.json');summary['final']['groundPolygons']=len(b['groundSurfaces']);summary['final']['stableBatchFile']='fifth-expansion-batch-v2.json';summary['final']['stableBatchSHA256']=sha(O/'fifth-expansion-batch-v2.json');summary['b07GroundRefinement']=changes;write('joint-fit-summary.json',summary)
contract=read(O/'import-contract.json');contract['batchSHA256']=sha(O/'fifth-expansion-batch-v2.json');contract['stableBatchFile']='fifth-expansion-batch-v2.json';write('import-contract.json',contract);write('b07-court-refinement.json',{'initialBatchSHA256':oldsha,'refinedBatchSHA256':contract['batchSHA256'],'changes':changes});assert sha(f)==oldsha and all(sha(f)==h for f,h in protected.items());print('REFINED',contract['batchSHA256'],len(b['groundSurfaces']))
