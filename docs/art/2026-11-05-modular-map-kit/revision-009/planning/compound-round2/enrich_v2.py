#!/usr/bin/env python3
"""Independent frozen v2 adds a usable door-front inner court; v1 is byte-preserved."""
import context as x
from freeze import validate
import copy,math,itertools
from collections import Counter

def enrich(idx,others=[]):
 oldfile=x.O/f'scene-{idx:04d}.json';oldsha=x.sha(oldfile);p=x.read(oldfile);sid=p['scenes'][0]['sceneId'];mods=p['buildings'];N=x.nearset(p['sourceIndices']);base=x.center([b['entryMap'] for b in mods]);badcounts=Counter();chosen=None;trial=0
 def ground_bad(poly):
  bad=x.failures(x.audit(poly,N),False)
  if min(x.pp(poly,b['footprintPolygonMap']) for b in mods)<.15:bad+=['new-court-vs-native-entity']
  for o in others:
   if min(x.pp(poly,bb['footprintPolygonMap']) for bb in o['buildings'])<.15 or min(x.pp(poly,g['polygonMap']) for g in o['groundSurfaces'])<.15:bad+=['cross-scene-ground-protection']
  return bad
 # Finite wide court must touch both actual door approach polygons near the real door, not just a distant road-end link.
 for dt,ds,w,d in itertools.product([2.5,4,5.5,7],[0,-2,2,-4,4],[10,8,12],[4,6]):
  trial+=1;ctr=x.at(base,ds,dt);court=x.rect(ctr,w,d);bad=ground_bad(court)
  if not all(any(x.pp(court,po)<1e-7 for po in b['visualApproach']['polygonsMap']) for b in mods):bad+=['inner-court-does-not-directly-join-both-doors']
  if max(math.dist(ctr,b['entryMap']) for b in mods)>15:bad+=['court-too-distant-from-real-doors']
  if bad:badcounts.update(bad);continue
  for side,gw,gd in itertools.product(['rear','left','right'],[8,6],[5,4]):
   if side=='rear':gc=x.at(ctr,0,d/2+gd/2)
   elif side=='left':gc=x.at(ctr,-w/2-gw/2,0)
   else:gc=x.at(ctr,w/2+gw/2,0)
   garden=x.rect(gc,gw,gd);bad=ground_bad(garden)
   if any(x.pp(garden,g['polygonMap'])<.05 for g in p['groundSurfaces'] if g['materialId']=='S01-paving'):bad+=['green-room-covers-existing-new-walk']
   if bad:badcounts.update(bad);continue
   chosen=(court,garden,w,d,gw,gd,ctr);break
  if chosen:break
 if not chosen:
  x.write(f'scene-{idx:04d}-v2-design-audit.json',{'status':'no-complete-inner-court-within-budget','courtTrials':trial,'rejectedByRule':dict(badcounts),'v1SHA256':oldsha});return None
 court,garden,w,d,gw,gd,ctr=chosen
 # Original module/road geometry identical; sceneId retained because this v2 supersedes, never imported alongside v1.
 for tag,poly,material,purpose in [('inner-court',court,'S01-paving','finite broad shared inner court at both real doors: community meeting/pause, dwelling/service frontage; not a new road'),('green-room',garden,'G01-lawn','bounded community lawn/green room directly adjoining inner court; landscape reserve without invented plant sprites')]:
  p['groundSurfaces'].append({'id':sid+'-'+tag,'sceneId':sid,'owner':sid,'moduleIds':[m['id'] for m in mods],'materialId':material,'polygonMap':poly,'purpose':purpose,'surfaceClass':'shared-court' if tag=='inner-court' else 'garden','enrichmentV2':True})
 p['groundSurfaceCount']=len(p['groundSurfaces']);s=p['scenes'][0];s['groundSurfaceIds']=[g['id'] for g in p['groundSurfaces']];s['programmeEvidence']['innerCourtDesign']={'doorFrontCourtSizeMetres':[w,d],'courtAreaSquareMetres':x.area(court),'greenRoomSizeMetres':[gw,gd],'greenRoomAreaSquareMetres':x.area(garden),'courtJoinsBothRealDoorPaths':True,'purpose':'readable bounded inner court + adjoining larger green room, rather than only narrow door strips and distant road apron','noNewPropsOrNavigation':True};s['scenicProgramme']+='; v2 includes a broad shared inner court at both real doors and adjoining bounded community green';p['version']+='-v2';p['supersedes']={'v1Path':str(oldfile),'v1SHA256':oldsha,'importTogetherForbidden':True,'why':'actual geometry review found distant road landing and narrow strips inadequate as complete scene; preserve v1 evidence, improve inner court without moving modules/source/roads'}
 for old in p['groundSurfaces']:
  if old['id'].endswith('-shared-court'):old['purpose']='finite original road-end approach landing; interior common court added independently in v2'
 # Explicit garden/court organisation, peer doors remain unmodified.
 for gg in [g for g in p['groundSurfaces'] if g['materialId']=='G01-lawn']:
  assert x.pp(gg['polygonMap'],court)<1e-7
  assert all(x.pp(gg['polygonMap'],g['polygonMap'])>.05 for g in p['groundSurfaces'] if g['materialId']=='S01-paving' and g['id']!=sid+'-inner-court')
 proof=validate(p,others);out=x.O/f'scene-{idx:04d}-v2.json';assert not out.exists();x.write(out.name,p);x.write(out.stem+'-static-verification.json',dict(proof,planSHA256=x.sha(out)));x.write(out.stem+'-import-contract.json',{'status':'independent-review-required-before-explicit-parent-SHA-and-consumer-scope-adaptation','scenePath':str(out),'sceneSHA256':x.sha(out),'counts':{'uniqueSources':p['uniqueSourceCount'],'scenes':1,'modules':p['moduleCount'],'grounds':p['groundSurfaceCount'],'rendered':0,'userAccepted':0},'sceneIds':[sid],'sourceIndices':p['sourceIndices'],'supersedes':p['supersedes'],'importV1AndV2TogetherForbidden':True,'currentConsumerAllowsThis':False,'requiredGates':['Independent review exact v2 SHA','Parent exact SHA approval','Unique importer author restricted scope extension','Latest complete baseline static recheck; no snapshot replay'],'nodeScale':1,'scaleAlreadyResolvedOnce':True,'oldSurfaceEdits':[]});x.write(out.stem+'-design-audit.json',{'status':'broad-near-door-inner-court-and-green-room-found','courtTrials':trial,'rejectedByRule':dict(badcounts),'v1SHA256':oldsha,'v2SHA256':x.sha(out),'innerCourtAreaSquareMetres':x.area(court),'greenRoomAreaSquareMetres':x.area(garden),'moduleGeometryUnchanged':p['buildings']==x.read(oldfile)['buildings'],'roadsUnchanged':p['roads']==x.read(oldfile)['roads']});assert x.sha(oldfile)==oldsha;x.assert_protected();print('V2',idx,x.sha(out),'grounds',len(p['groundSurfaces']),flush=True);return p
if __name__=='__main__':
 a=enrich(343);b=enrich(268,[a] if a else []);assert a and b
