#!/usr/bin/env python3
"""Seven unknown sources + strict scene-owned multi-module pilot. Static only."""
import ast,json,math,hashlib,itertools,html
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;PL=O.parent;K=PL.parent.parent;ROOT=next(x for x in O.parents if (x/'delivery-game/assets/resources/map-sample/city.json').exists())
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
B=K/'revision-009/baselines/visible156';sf=B/'scene-layout.json';scene=read(sf);parent=read(B/'parent-check.json');assert len(scene['blocks'])==156 and len(scene['groundSurfaces'])==497
cf=ROOT/'delivery-game/assets/resources/map-sample/city.json';zf=ROOT/'docs/art/2026-11-02-county-zoning/selection.json';c=read(cf);z=read(zf);P=scene['projection'];g=read(K/'revision-003/road-constraint.json');u=g['streetTangentMap'];n=[-u[1],u[0]]
lib=read(B/'asset-library.json');assets={a['id']:a for a in lib['assets']};C143=K/'revision-009/baselines/visible143';cal={a['id']:a for a in read(C143/'asset-calibration.json')['assets']};oldmanifest={a['id']:a for a in read(C143/'asset-manifest.json')['assets']};review=read(K/'revision-008/calibration/footprint-review.json');U=next(x for x in review['assets'] if x['id']=='B07');contractfile=K/'revision-009/scenic-scene-contract.md';auditdir=K/'revision-009/review/placement-capacity-audit';classification=read(auditdir/'classification.json');examples=read(auditdir/'examples.json')
# AST pure math only; never import or execute historical planning/writing modules.
tree=ast.parse((K/'revision-006/planning/build_plan.py').read_text());names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'};exec(compile(ast.Module(body=[t for t in tree.body if isinstance(t,ast.FunctionDef) and t.name in names],type_ignores=[]),'<pure-polygon-functions>','exec'))
protected={str(f):sha(f) for folder in [B,C143,PL/'fit-round-5',auditdir] for f in folder.iterdir() if f.is_file()};protected.update({str(f):sha(f) for f in [cf,zf,contractfile,K/'revision-008/calibration/footprint-review.json',K/'revision-003/road-constraint.json',PL/'fit-round-4/usage-contracts.json',K/'revision-009/source-entry-semantics.md',K/'revision-006/integration/batch-009-r5/009r5-derived-plan.json',K/'revision-006/planning/build_plan.py']});protected.update({a['runtimeDerivation']['source']:sha(a['runtimeDerivation']['source']) for a in assets.values() if a['id'] in ['B01','B05']});write('input-sha-before.json',protected)
# Keep two digest concepts distinct even if this parent check happens to publish equal values.
digest={'snapshotSerializedActualSHA256':sha(sf),'parentDeclaredSerializedSHA256':parent['serializedSnapshotSHA256'],'parentDeclaredPublishedSHA256':parent['publishedSceneSHA256'],'method':parent['snapshotMethod'],'differentConceptsNotInterchanged':True};assert sha(sf)==parent['serializedSnapshotSHA256'];write('baseline-provenance.json',digest)
nodes={p['id']:[p['x'],p['y']] for p in c['nodes']};bound=set()
for rec in scene['visualReplacements']:
 v=rec.get('visualReplacementOf',rec);bound.update(v.get('sourceIndices',rec.get('sourceIndices',[])));i=v.get('sourceIndex',rec.get('sourceIndex'))
 if i is not None:bound.add(i)
assert len(bound)==81
reserved={i for r in read(PL/'fit-round-4/usage-contracts.json')['reservations'] for i in r['sourceIndices']}
def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def bgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def center(p):return [sum(v[k] for v in p)/len(p) for k in (0,1)]
def area(p):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in edges(p)))/2
def at(anchor,s,t):return add(add(anchor,mul(u,s)),mul(n,t))
def pixelmap(px,anchor,co,scale=1):
 ap=co.get('anchorPixel',co.get('originalAnchorPixel'));ppu=co.get('nativePixelsPerUnit',co.get('sourceNativePPU'));sx,sy=[(px[k]-ap[k])/ppu*scale for k in (0,1)];a,b=P['axisX'],P['axisY'];D=a[0]*b[1]-a[1]*b[0];return add(anchor,[(sx*b[1]-sy*b[0])/D,(a[0]*sy-a[1]*sx)/D])
def footprint(aid,anchor,scale):
 if aid=='B07':return [at(anchor,v[0]*scale,v[1]*scale) for v in U['conservativeOccupiedPolygonLocalTN']]
 co=cal[aid];ps=co.get('occupiedGroundOutlinePixel') or co.get('groundCornersPixelLeftFrontRightRear') or [[198,910],[438,1229],[1055,931],[815,612]];return [pixelmap(v,anchor,co,scale) for v in ps]
doors={'B01':[973,965],'B02':[750,970],'B03':[740,1060],'B04':[775,905],'B05':[810,1070],'B06':cal['B06']['entryPixel'],'B07':[704,609],'B08':cal['B08']['entryPixel']}
bs=[(i,p,bbox(p)) for i,p in enumerate(c['buildings'])];allsegments=[(r,j,nodes[a],nodes[b],bbox([nodes[a],nodes[b]])) for r in c['roads'] for j,(a,b) in enumerate(zip(r['nodes'],r['nodes'][1:]))];water=[a['points'] for a in c['areas'] if a.get('kind')=='water' and len(a.get('points',[]))>=3];wl=[(a,b) for w in c['waterways'] for a,b in zip(w,w[1:])];pois=[(i,p,nodes[p['node']]) for i,p in enumerate(c['pois']) if p.get('node')in nodes]
oldground=[{'id':s['id'],'poly':s['polygonMap'],'material':s.get('materialId'),'purpose':s.get('purpose','frozen existing surface; ownership from snapshot')} for s in scene['groundSurfaces']];oldbody=[]
# New13 comparison/r5 records have actual exported ground controls; use them directly. Canonical retained old source controls remain hand estimates, never billboard corners.
r5=read(K/'revision-006/integration/batch-009-r5/009r5-derived-plan.json');r5b={v['persistentId']:v for v in r5['buildings']}
for bl in scene['blocks']:
 aid=bl['sourceAssetId'];anchor=bl['anchorMap'];scope=None
 if bl.get('footprintPolygonMap'):poly=bl['footprintPolygonMap'];scope='frozen exported native hand ground outline'
 elif bl.get('groundContactPolygonMap'):poly=bl['groundContactPolygonMap'];scope='frozen contact polygon; root uncertainty retained'
 elif bl['persistentId']in r5b:poly=r5b[bl['persistentId']]['footprintPolygonMap'];scope='completed r5 actual ground derivation'
 elif aid in doors:
  sc=bl.get('uniformScaleCandidate',1);a=oldmanifest.get(bl['assetId'])
  if a and aid in assets and a.get('worldSizeUnits'):sc=a['worldSizeUnits'][0]/assets[aid]['worldSizeUnits'][0]
  poly=footprint(aid,anchor,sc);scope='manual native ground controls; hidden rear inferred; not roof billboard'
 else:poly=rect(anchor,1.4 if aid.startswith('T') else 1,1.4 if aid.startswith('T') else 1);scope='conservative root/fixture proxy, not surveyed contact'
 oldbody.append({'id':bl['persistentId'],'poly':poly,'scope':scope})
write('old156-ground-evidence.json',oldbody)
# Local scene windows keep exact global half-width segments crossing a window even if both endpoints lie outside.
windows={i:bbox(rect(center(c['buildings'][i]),90,90)) for i in [586,125,590,588,430,580,429]}
def nearset(ids):
 polys=[c['buildings'][i] for i in ids];b=bbox([v for p in polys for v in p]);return {'segments':[(r,j,a,d) for r,j,a,d,bb in allsegments if bgap(b,bb)<80],'sources':[(i,p) for i,p,bb in bs if i not in ids and bgap(b,bb)<80],'water':[p for p in water if bgap(b,bbox(p))<80],'lines':[(a,d) for a,d in wl if bgap(b,bbox([a,d]))<80],'oldGround':[p for p in oldground if bgap(b,bbox(p['poly']))<80],'oldBody':[p for p in oldbody if bgap(b,bbox(p['poly']))<80]}
def nearest(poly,items):
 if not items:return [9999,None]
 d,item=min((pp(poly,p['poly']),p['id']) for p in items);return [d,item]
def audit(poly,N):
 sb=min([(pp(poly,p),i) for i,p in N['sources']]+[(9999,None)]);road=min([(pl(poly,a,d)-r['width']/2,(r['id'],j)) for r,j,a,d in N['segments']]+[(9999,None)]);wb=min([pp(poly,p) for p in N['water']]+[pl(poly,a,d)-3 for a,d in N['lines']]+[9999]);ground=nearest(poly,N['oldGround']);body=nearest(poly,N['oldBody']);pg=min([(0 if inside(q,poly) else min(ps(q,a,d) for a,d in edges(poly)),i) for i,p,q in pois]);return {'otherSourceGap':sb[0],'otherSourceIndex':sb[1],'roadEdgeGap':road[0],'roadSegment':road[1],'waterSafetyGap':wb,'oldGroundGap':ground[0],'oldSurfaceId':ground[1],'oldBodyGap':body[0],'oldBodyId':body[1],'POIclearance':pg[0],'nearestPOIIndex':pg[1],'blue':all(inbounds(v,'city') for v in poly)}
def failures(q,body):
 req={'otherSourceGap':2 if body else .15,'roadEdgeGap':2 if body else -.001,'waterSafetyGap':5,'oldGroundGap':1 if body else .15,'oldBodyGap':1 if body else .15,'POIclearance':.15};return [k for k,v in req.items() if q[k]<v]+([] if q['blue'] else ['blue'])
def strip(a,b,w=1.5):
 D=math.dist(a,b)
 if D<.001:return None
 v=[-(b[1]-a[1])/D,(b[0]-a[0])/D];return [add(a,mul(v,w/2)),add(b,mul(v,w/2)),add(b,mul(v,-w/2)),add(a,mul(v,-w/2))]
def foot(p,a,b):
 v=[b[k]-a[k] for k in (0,1)];D=sum(x*x for x in v);t=max(0,min(1,sum((p[k]-a[k])*v[k] for k in (0,1))/D)) if D else 0;return [a[k]+t*v[k] for k in (0,1)],t
single=[];trials=[];bySource={};inventory=[]
for idx in [590,125,588,430,580,429,586]:
 src=c['buildings'][idx];C=center(src);N=nearset([idx]);A=area(src);own=idx not in bound|reserved;inv={'sourceIndex':idx,'sourcePolygonMap':src,'areaSquareMetres':A,'originalSemanticStatus':'unknown','scenicProgramme':'PM-designed small neighbourhood shared service-and-residential court' if A>200 else 'PM-designed low-rise frontage/courtyard' if A>40 else 'PM-designed limited non-building landscape residue, no forced house','programmeEvidence':{'PMContractPath':str(contractfile),'contractSHA256':sha(contractfile),'basis':'user approved scenic diversity; source function/door/business binding absent and remains unknown'},'blue':all(inbounds(v,'city') for v in src),'zone':zone(C),'unboundUnreserved':own,'nearbyOriginalRoads':[{**r,'sourceNodeIds':r['nodes'],'nodes':[nodes[nid] for nid in r['nodes']]} for r in {r['id']:r for r,j,a,b in N['segments']}.values()]};inventory.append(inv)
 if not own:bySource[idx]={'status':'excluded-bound-or-reserved'};continue
 # For13sqm source test footprints but do not quietly spill out to fit a house. Every module anchor and at least half its body corners must be in owned carrier.
 local=[[sum((v[k]-C[k])*u[k] for k in (0,1)),sum((v[k]-C[k])*n[k] for k in (0,1))] for v in src];s0,s1=min(v[0] for v in local),max(v[0] for v in local);t0,t1=min(v[1] for v in local),max(v[1] for v in local)
 anchors=[at(C,s,t) for s in range(math.ceil(s0),math.floor(s1)+1,4) for t in range(math.ceil(t0),math.floor(t1)+1,4) if inside(at(C,s,t),src)];anchors=sorted(anchors,key=lambda p:math.dist(p,C))[:30]
 if not anchors:anchors=[C]
 fits=[];counter=Counter();attempts=Counter();routecount=Counter();witness={};triallog=[]
 for aid in ['B05','B01','B06','B04','B03','B02','B08','B07']:
  for scale in ([1] if aid=='B01' else [.9,1,1.1]):
   for anchor in anchors:
    attempts[f'{aid}@{scale}']+=1;poly=footprint(aid,anchor,scale);reason=[]
    if A<30 or sum(inside(p,src) for p in poly)<len(poly)/2:reason.append('owned-carrier-insufficient-support;not-spill-to-unowned-land')
    q=audit(poly,N);reason+=failures(q,True);tr={'assetId':aid,'uniformScale':scale,'anchorMap':anchor,'bodyClearance':q,'bodyRejectedBy':reason,'routes':[]};triallog.append(tr)
    if reason:
     counter.update(reason)
     for rr in reason:witness.setdefault(rr,{'asset':aid,'scale':scale,'anchorMap':anchor,'polygonMap':poly,'clearance':q})
     continue
    entry=pixelmap(doors[aid],anchor,cal[aid],scale);start=pixelmap([713,626],anchor,cal[aid],scale) if aid=='B07' else entry;prefix=[start]+([at(anchor,0,7*scale)] if aid=='B07' else []);found=None
    for r,j,a,b in sorted(N['segments'],key=lambda z:math.dist(start,foot(start,z[2],z[3])[0]))[:4]:
     qp,param=foot(prefix[-1],a,b);D=math.dist(prefix[-1],qp)
     if D<r['width']/2+2 or D>55:continue
     normal=[(qp[k]-prefix[-1][k])/D for k in (0,1)];end=add(qp,mul(normal,-(r['width']/2+.03)));out=add(prefix[-1],mul(n,1.2));mid=add(out,mul(u,sum((end[k]-out[k])*u[k] for k in (0,1))))
     for name,pts in [('direct',prefix+[end]),('side-L',prefix+[out,mid,end])]:
      routecount[aid+':'+name]+=1;pts=[p for k,p in enumerate(pts) if k==0 or math.dist(p,pts[k-1])>.001];polys=[strip(a,b) for a,b in zip(pts,pts[1:])]+[rect(p,1.5,1.5) for p in pts[1:-1]];bad=[];aq=[]
      for p in polys:
       qq=audit(p,N);aq.append(qq);bad+=['approach:'+v for v in failures(qq,False)]
      if aid=='B07' and any(pp(p,poly)<.05 for p in polys):bad.append('approach:own-U-entity')
      elif aid!='B07':
       cut=add(start,mul([(pts[1][k]-start[k])/math.dist(start,pts[1]) for k in (0,1)],.6));p0=strip(cut,pts[1]);bad+=['approach:own-body-after-threshold'] if p0 is None or pp(p0,poly)<.05 or any(pp(p,poly)<.05 for p in polys[1:]) else []
      tr['routes'].append({'strategy':name,'roadId':r['id'],'nodeRangeInclusive':[j,j+1],'centrelineMap':pts,'widthMetres':1.5,'clearances':aq,'rejectedBy':bad})
      if bad:
       counter.update(bad)
       for rr in bad:witness.setdefault(rr,{'asset':aid,'scale':scale,'anchorMap':anchor,'entryPixel':doors[aid],'approachPolygonsMap':polys,'approachClearances':aq})
       continue
      if not all(inbounds(nodes[v],'city') for v in r['nodes'][j:j+2]):counter['approach:source-segment-cross-blue']+=1;continue
      found={'sourceIndices':[idx],'assetId':aid,'uniformScale':scale,'anchorMap':anchor,'footprintPolygonMap':poly,'entryMap':entry,'entryPixel':doors[aid],'walkStartMap':start,'approachPolygonsMap':polys,'centrelineMap':pts,'roadId':r['id'],'roadNodeRangeInclusive':[j,j+1],'bodyClearance':q,'approachClearances':aq};break
     if found:break
    if found:fits.append(found)
    tr['outcome']='body-rejected' if reason else 'accepted-single-option' if found else 'bounded-door-search-rejected'
   # keep enough different positions for true two-module joint fitting; do not stop at first asset pose.
 bySource[idx]={'status':'single-module-options' if fits else 'bounded-single-search-no-fit','singleOptionCount':len(fits),'assetScaleAnchorAttempts':dict(attempts),'approachAttempts':dict(routecount),'rejectedByRuleAttempts':dict(counter),'firstWitnessPerRule':witness,'testedAnchorCount':len(anchors),'originalSemanticStatus':'unknown','metadataAbsenceNeverARejectRule':True}
 write(f'attempt-source-{idx:04d}.json',{'sourceIndex':idx,'nativeFootprintConstruction':'plan_compound.py footprint; actual pixels and source calibration; not nominal dimensions','records':triallog});single+=fits;write('seven-source-attempts.json',{'rows':bySource,'scope':'all7 sources directly tested, no automatic metadata deferral; bounded4m grid and existing scales','options':single});write('seven-source-inventory.json',inventory);print('SOURCE',idx,'fits',len(fits),flush=True)
# Joint same-source ownership, actual bodies/doors/courts still obstacles to peers.
compound=None;pairrecords=[]
for idx in [590,125,588,430,580,429,586]:
 opts=[o for o in single if o['sourceIndices']==[idx]];pairs=0;rejects=Counter();witness=None
 for a,b in itertools.combinations(opts,2):
  if a['assetId']==b['assetId']:continue
  pairs+=1;gap=pp(a['footprintPolygonMap'],b['footprintPolygonMap'])
  if gap<2:rejects['peer-module-body-gap<2']+=1;continue
  walkgap=min([pp(p,b['footprintPolygonMap']) for p in a['approachPolygonsMap']]+[pp(p,a['footprintPolygonMap']) for p in b['approachPolygonsMap']])
  if walkgap<.15:rejects['peer-door-approach-body-gap<.15']+=1;continue
  compound={'sourceIndices':[idx],'modules':[a,b],'jointBodyGapMetres':gap,'peerWalkBodyGapMetres':walkgap};break
 pairrecords.append({'sourceIndices':[idx],'modulePairAttempts':pairs,'rejectedByRule':dict(rejects),'jointPassed':compound is not None})
 if compound:break
write('compound-joint-attempts.json',{'sameSourcePairResults':pairrecords,'sourceCountSeparateFromModuleCount':True});write('feasible-compound-raw.json',compound)
assert all(sha(f)==h for f,h in protected.items());print('COMPOUND',None if compound is None else (compound['sourceIndices'],[m['assetId'] for m in compound['modules']]),flush=True)
