#!/usr/bin/env python3
"""Preserve actual composite footprint/approach hypotheses without changing frozen batch."""
from pathlib import Path
exec(compile(Path(__file__).with_name('fit_round3.py').read_text().split('rows=[];options=[]')[0],'read-only-context','exec'),globals())
import ast
batchfile=O/'third-expansion-batch.json';frozen=sha(batchfile);batch=read(batchfile);protected_polys += [b['footprintPolygonMap'] for b in batch['buildings']]+[s['polygonMap'] for s in batch['groundSurfaces']]
combo_trials=[]
tree=ast.parse((O/'assemble_round3.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='try_group');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<exact-combination-trial>','exec'))
p=next(p for p in legacy['parcels'] if p['id']==next(x['parcelId'] for x in read(O/'combination-evidence.json')['manyToOneActualTrials'] if x['result']=='feasible-design-cluster'))
result=try_group([654,2387],p,'many-source-to-one-approved-scenic-courtyard');multi=[]
originalcode=ast.get_source_segment((O/'assemble_round3.py').read_text(),fn)
for sourceIndex in [1,377]:
 meta=next(x for x in read(O/'combination-evidence.json')['largeCarrierReviews'] if x['sourceIndex']==sourceIndex);parcel=next(p for p in legacy['parcels'] if p['id']==meta['enclosingSameUseParcels'][0]);modules=[];reasons=[]
 for moduleOffset in [-9,0,9]:
  code=originalcode.replace('C=center([v for p in srcs for v in p])','C=add(center([v for p in srcs for v in p]),mul(u,moduleOffset))');exec(compile(code,'<multi-module-trial>','exec'))
  v=try_group([sourceIndex],parcel,'one-source-to-three-residential-or-mixed-modules')
  if v:modules.append(v)
 if len(modules)!=3:reasons.append('one-or-more-module-ground/door-approach-exhausted')
 for a,b in itertools.combinations(modules,2):
  if pp(a['footprintPolygonMap'],b['footprintPolygonMap'])<2 or any(pp(p,b['footprintPolygonMap'])<.15 for p in a['approach']['polygonsMap']) or any(pp(p,a['footprintPolygonMap'])<.15 for p in b['approach']['polygonsMap']):reasons.append('modules-or-their-fixed-door-corridors-overlap')
 multi.append({'sourceIndex':sourceIndex,'parcelId':parcel['id'],'sameUseIntent':parcel['landUse'],'moduleTrialOffsetsAlongFixedU':[-9,0,9],'modules':modules,'jointRejectionRules':reasons,'status':'deferred-joint-layout' if reasons else 'candidate-for-next-packet-not-admitted','uniqueSourceCount':1,'moduleCount':len(modules),'renderedSourceCount':0,'useEvidenceScope':'approved enclosing scenery use, source historical business type still absent'})
write('composite-followup-options.json',{'frozenThirdBatchSHA256':frozen,'manyToOneRecheckAgainstFrozen20':result,'oneToManyActualBoundedTrials':multi,'attempts':combo_trials,'notInFrozenThirdBatch':True,'mustRecheckNextPacketInteractions':True})
assert sha(batchfile)==frozen
print('COMPOSITES',bool(result),[(x['sourceIndex'],len(x['modules']),x['status']) for x in multi])
