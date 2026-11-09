"""Read current completed163 scene. Pure AST geometry, no shared importer execution."""
import sys
sys.dont_write_bytecode=True
import ast,json,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;K=O.parents[2];ROOT=next(p for p in O.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists());PL=O.parent
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,value):
 p=(O/name).resolve();assert p.is_relative_to(O);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
sf=K/'revision-006/viewer/assets/scene-layout.json';tf=K/'revision-006/integration/neighborhood.tmj';scene=read(sf);assert sha(sf)=='237252cf5858346686c707335f1a323c0d14261631ec6262b6d403bbfd94b5cc';assert sha(tf)=='26eb9baad3f38a13570c5c23d4cadd5a5f4f4ef29f1c5a174436d3c566fd99e8';assert [len(scene['blocks']),len(scene['groundSurfaces'])]==[163,506]
cf=ROOT/'delivery-game/assets/resources/map-sample/city.json';zf=ROOT/'docs/art/2026-11-02-county-zoning/selection.json';c=read(cf);z=read(zf);P=scene['projection'];g=read(K/'revision-003/road-constraint.json');u=g['streetTangentMap'];n=[-u[1],u[0]];calfile=K/'revision-009/baselines/visible143/asset-calibration.json';cal={a['id']:a for a in read(calfile)['assets']};lf=K/'revision-006/integration/asset-library.json';assets={a['id']:a for a in read(lf)['assets']};revfile=K/'revision-008/calibration/footprint-review.json';U=next(a for a in read(revfile)['assets'] if a['id']=='B07');contractfile=K/'revision-009/scenic-scene-contract.md'
# Only function definitions; no historical script body/writer/importer is executed.
oldgeom=K/'revision-006/planning/build_plan.py';names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'};tree=ast.parse(oldgeom.read_text());exec(compile(ast.Module(body=[t for t in tree.body if isinstance(t,ast.FunctionDef) and t.name in names],type_ignores=[]),'<pure-geometry>','exec'))
prior=PL/'compound-pilot/plan_compound.py';names={'bbox','bgap','center','area','at','pixelmap','footprint','nearset','nearest','audit','failures','strip','foot'};tree=ast.parse(prior.read_text());exec(compile(ast.Module(body=[t for t in tree.body if isinstance(t,ast.FunctionDef) and t.name in names],type_ignores=[]),'<pure-native-geometry>','exec'))
# Source ownership logic AST only, without pilot white-list consumer or importing shared code.
import copy
cc=K/'revision-009/pipeline/compound_contract.py';tree=ast.parse(cc.read_text());exec(compile(ast.Module(body=[t for t in tree.body if isinstance(t,ast.FunctionDef) and t.name in {'require','binding_view','source_accounting'}],type_ignores=[]),'<read-only-ownership>','exec'));accounting=source_accounting(scene);assert accounting['uniqueSourceCount']==82 and accounting['sourceBoundModuleCount']==83;bound=set(accounting['sourceIndices']);resfile=PL/'fit-round-4/usage-contracts.json';reserved={i for r in read(resfile)['reservations'] for i in r['sourceIndices']}
nodes={p['id']:[p['x'],p['y']] for p in c['nodes']};doors={'B01':[973,965],'B02':[750,970],'B03':[740,1060],'B04':[775,905],'B05':[810,1070],'B06':cal['B06']['entryPixel'],'B07':[704,609],'B08':cal['B08']['entryPixel']}
bs=[(i,p,bbox(p)) for i,p in enumerate(c['buildings'])];allsegments=[(r,j,nodes[a],nodes[b],bbox([nodes[a],nodes[b]])) for r in c['roads'] for j,(a,b) in enumerate(zip(r['nodes'],r['nodes'][1:]))];water=[a['points'] for a in c['areas'] if a.get('kind')=='water' and len(a.get('points',[]))>=3];wl=[(a,b) for w in c['waterways'] for a,b in zip(w,w[1:])];pois=[(i,p,nodes[p['node']]) for i,p in enumerate(c['pois']) if p.get('node') in nodes]
evidence=K/'revision-006/integration/batch-009-r5/actual-old-shape-evidence.json';r5=K/'revision-006/integration/batch-009-r5/009r5-derived-plan.json';market=K/'revision-006/integration/market-life/market-layout.json';compound=K/'revision-006/integration/compound-pilot/derived-compound-plan.json'
oldbody=[{'id':r['id'],'poly':r['polygon'],'scope':'completed actual-old-shape evidence; manual/proxy uncertainty retained'} for r in read(evidence)]+[{'id':r['persistentId'],'poly':r['footprintPolygonMap'],'scope':'completed r5 native feet'} for r in read(r5)['buildings']]+[{'id':r['persistentId'],'poly':r['groundContactPolygonMap'],'scope':r['groundContactMethod']} for r in read(market)['newFixtures']]+[{'id':r['persistentId'],'poly':r['footprintPolygonMap'],'scope':'published source125 native manual footline'} for r in read(compound)['buildings']];assert len(oldbody)==163 and {r['id'] for r in oldbody}=={r['persistentId'] for r in scene['blocks']};oldground=[{'id':r['id'],'poly':r['polygonMap']} for r in scene['groundSurfaces']]
inputs=[sf,tf,cf,zf,lf,calfile,revfile,contractfile,oldgeom,prior,cc,resfile,evidence,r5,market,compound,K/'revision-009/pipeline/current-integration-reference.json',K/'revision-009/review/compound-pilot-review/REPORT.md',K/'revision-006/integration/compound-pilot/REPORT.md',PL/'fit-round-3/next-source-fit-queue.json',PL/'fit-round-3/composite-followup-options.json'];protected={str(f):sha(f) for f in inputs}
def assert_protected():assert all(sha(f)==h for f,h in protected.items())
# Exact distance evaluation with bounding-box lower-bound pruning; no obstacle omitted by arbitrary distance.
def exactnearest(poly,items):
 bb=bbox(poly);best=9999;ident=None
 for lower,i,p in sorted((bgap(bb,bbox(p)),i,p) for i,p in items):
  if lower>best:break
  d=pp(poly,p)
  if d<best:best,ident=d,i
 return best,ident
reference_audit=audit
def audit(poly,N):
 sb=exactnearest(poly,N['sources']);ground=exactnearest(poly,[(v['id'],v['poly']) for v in N['oldGround']]);body=exactnearest(poly,[(v['id'],v['poly']) for v in N['oldBody']]);bb=bbox(poly);road=(9999,None);wb=exactnearest(poly,[(i,p) for i,p in enumerate(N['water'])])[0]
 for lower,r,j,a,b in sorted((bgap(bb,bbox([a,b]))-r['width']/2,r['id'],j,a,b) for r,j,a,b in N['segments']):
  if lower>road[0]:break
  rr=next(v for v,jj,aa,dd in N['segments'] if v['id']==r and jj==j);d=pl(poly,a,b)-rr['width']/2
  if d<road[0]:road=(d,(r,j))
 for lower,a,b in sorted((bgap(bb,bbox([a,b]))-3,a,b) for a,b in N['lines']):
  if lower>wb:break
  wb=min(wb,pl(poly,a,b)-3)
 pg=min([(0 if inside(q,poly) else min(ps(q,a,d) for a,d in edges(poly)),i) for i,p,q in pois])
 return {'otherSourceGap':sb[0],'otherSourceIndex':sb[1],'roadEdgeGap':road[0],'roadSegment':road[1],'waterSafetyGap':wb,'oldGroundGap':ground[0],'oldSurfaceId':ground[1],'oldBodyGap':body[0],'oldBodyId':body[1],'POIclearance':pg[0],'nearestPOIIndex':pg[1],'blue':all(inbounds(v,'city') for v in poly)}
