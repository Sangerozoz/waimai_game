#!/usr/bin/env python3
"""Local infill only, no whole-county rescan or live renderer access."""
import ast,json,math,hashlib,itertools,html
from collections import Counter
from pathlib import Path
# refuse frozen v2 overwrite
if (Path(__file__).resolve().parent/'fifth-expansion-batch-v2.json').exists():
 raise SystemExit('Frozen v2 exists; do not rebuild; consume import-contract.json.')
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;OLD=O.parent;K=OLD.parent.parent;ROOT=next(p for p in O.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists())
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(f,d):(O/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
B=K/'revision-009/baselines/visible143';sf=B/'scene-layout.json';scene=read(sf);assert sha(sf)=='9f7adf3e269fc320830b3b5b422797faed5014b453a99d199efd0c76d546bf8f';assert len(scene['blocks'])==143 and len(scene['groundSurfaces'])==462
lib=read(B/'asset-library.json');assets={a['id']:a for a in lib['assets']};cal={a['id']:a for a in read(B/'asset-calibration.json')['assets']};manifest={a['id']:a for a in read(B/'asset-manifest.json')['assets']};cf=ROOT/'delivery-game/assets/resources/map-sample/city.json';c=read(cf);z=read(ROOT/'docs/art/2026-11-02-county-zoning/selection.json');g=read(K/'revision-003/road-constraint.json');P=g['projection'];u=g['streetTangentMap'];n=[-u[1],u[0]];review=read(K/'revision-008/calibration/footprint-review.json');b07=next(x for x in review['assets'] if x['id']=='B07')
names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'};tree=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name in names],type_ignores=[]),'<pure-geometry>','exec'))
protected={str(f):sha(f) for f in B.iterdir() if f.is_file()};protected[str(cf)]=sha(cf)
for folder in [OLD,OLD/'fit-round-2',OLD/'fit-round-3',OLD/'fit-round-4']:
 protected.update({str(f):sha(f) for f in folder.iterdir() if f.is_file()})
write('protected-inputs.json',protected)
nodes={x['id']:[x['x'],x['y']] for x in c['nodes']};bound=set();binding_evidence=[]
for rec in scene['visualReplacements']:
 v=rec.get('visualReplacementOf',rec);ids=v.get('sourceIndices',rec.get('sourceIndices',[]));single=v.get('sourceIndex',rec.get('sourceIndex'));ids=ids+([single] if single is not None else []);bound.update(ids);binding_evidence.append({'persistentId':rec['persistentId'],'sourceIndices':sorted(set(ids)),'readFormat':'singular' if single is not None else 'array'})
assert len(bound)==69
reserved={i for r in read(OLD/'fit-round-4/usage-contracts.json')['reservations'] for i in r['sourceIndices']};reserved|={1731,1383}
def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def centre(p):return [sum(v[k] for v in p)/len(p) for k in (0,1)]
def projectvector(v):return [v[0]*P['axisX'][k]+v[1]*P['axisY'][k] for k in (0,1)]
def pixelmap(px,anchor,co,scale=1):
 ap=co.get('anchorPixel',co.get('originalAnchorPixel'));ppu=co.get('nativePixelsPerUnit',co.get('sourceNativePPU'));sx,sy=[(px[k]-ap[k])/ppu*scale for k in (0,1)];a,b=P['axisX'],P['axisY'];det=a[0]*b[1]-a[1]*b[0];return add(anchor,[(sx*b[1]-sy*b[0])/det,(a[0]*sy-a[1]*sx)/det])
def footprint(aid,anchor,scale):
 if aid=='B07':return [add(add(anchor,mul(u,p[0]*scale)),mul(n,p[1]*scale)) for p in b07['conservativeOccupiedPolygonLocalTN']]
 co=cal[aid];px=co.get('occupiedGroundOutlinePixel') or co.get('groundCornersPixelLeftFrontRightRear') or [[198,910],[438,1229],[1055,931],[815,612]];return [pixelmap(v,anchor,co,scale) for v in px]
# All143 objects protected at their actual final scalar; 462 ground polygons exact. No overview-view bounds treated as physical occupancy.
oldpolys=[s['polygonMap'] for s in scene['groundSurfaces']];oldbody=[]
for bl in scene['blocks']:
 aid=bl['sourceAssetId'];anchor=bl['anchorMap'];a=manifest.get(bl['assetId']);canonical=assets.get(aid)
 scale=a['worldSizeUnits'][0]/canonical['worldSizeUnits'][0] if a and canonical and a.get('worldSizeUnits') and canonical.get('worldSizeUnits') else 1
 if aid in ['B01','B02','B03','B04','B05','B06','B07','B08']:poly=footprint(aid,anchor,scale)
 else:poly=rect(anchor,1.4 if aid.startswith('T') else 1,1.4 if aid.startswith('T') else 1)
 oldbody.append({'persistentId':bl['persistentId'],'assetId':aid,'resolvedScale':scale,'footprintPolygonMap':poly});oldpolys.append(poly)
obs=[(p,bbox(p)) for p in oldpolys];bs=[(i,p,bbox(p)) for i,p in enumerate(c['buildings'])];segments=[(r,j,nodes[a],nodes[b],bbox([nodes[a],nodes[b]])) for r in c['roads'] for j,(a,b) in enumerate(zip(r['nodes'],r['nodes'][1:]))];ww=[p['points'] for p in c['areas'] if p.get('kind')=='water' and len(p.get('points',[]))>=3];wl=[(a,b) for w in c['waterways'] for a,b in zip(w,w[1:])];pois=[(i,p,nodes[p['node']]) for i,p in enumerate(c['pois']) if p.get('node')in nodes]
regions={'market0587':[-1465.64,206.35333333333335],'housing1735-1739':[-1280,-605]};Ucentre=[-1757.4614285714285,224.88857142857142]
queue=read(OLD/'fit-round-3/next-source-fit-queue.json')['sourceOptions'];previous_progress=read(OLD/'fit-round-3/fit-progress-strategy-audit.json');metadata={r['sourceIndex']:r for r in previous_progress['testedSources']};existing=[]
for vals in queue.values():
 for x in vals:
  if x['sourceIndex']in bound or x['sourceIndex']in reserved:continue
  region=min(regions,key=lambda k:math.dist(x['anchorMap'],regions[k]));distance=math.dist(x['anchorMap'],regions[region])
  if distance<=140:x=dict(x,regionId=region,distanceToExistingFocusMetres=distance);existing.append(x)
# No scope drift to many distant empty sites. Only sources within these two fixed140m discs eligible.
localids={i for i,p,bb in bs if all(inbounds(v,'city') for v in p) and i not in bound and i not in reserved and min(math.dist(centre(p),v) for v in regions.values())<=140}
def audit(poly,ids,new=()):
 pb=bbox(poly);sg=min([pp(poly,p) for i,p,bb in bs if i not in ids and boxgap(pb,bb)<80]+[9999]);rg=min([pl(poly,a,b)-r['width']/2 for r,j,a,b,bb in segments if boxgap(pb,bb)<80]+[9999]);wg=min([pp(poly,p) for p in ww if boxgap(pb,bbox(p))<80]+[pl(poly,a,b)-3 for a,b in wl if boxgap(pb,bbox([a,b]))<80]+[9999]);og=min([pp(poly,p) for p,bb in obs if boxgap(pb,bb)<80]+[9999]);ng=min([pp(poly,p) for p in new]+[9999]);return {'otherSourceMetres':sg,'roadEdgeMetres':rg,'waterSafetyMetres':wg,'visible143GroundBodyMetres':og,'otherNewBodyMetres':ng,'allVerticesBlue':all(inbounds(v,'city') for v in poly)}
def good(q,body=False):return q['allVerticesBlue'] and q['otherSourceMetres']>=(2 if body else .15) and q['roadEdgeMetres']>=(2 if body else -.001) and q['waterSafetyMetres']>=5 and q['visible143GroundBodyMetres']>=(1 if body else .15) and q['otherNewBodyMetres']>=(2 if body else .15)
rows=[];fitopts=list(existing)
doors={'B01':[973,965],'B02':[750,970],'B03':[740,1060],'B04':[775,905],'B05':[810,1070],'B06':cal['B06']['entryPixel'],'B07':[704,609],'B08':cal['B08']['entryPixel']}
def strip(a,b,w=1.5):
 D=math.dist(a,b)
 if D<.001:return None
 v=[-(b[1]-a[1])/D,(b[0]-a[0])/D];return [add(a,mul(v,w/2)),add(b,mul(v,w/2)),add(b,mul(v,-w/2)),add(a,mul(v,-w/2))]
def foot(p,a,b):
 v=[b[k]-a[k] for k in (0,1)];den=sum(q*q for q in v);t=max(0,min(1,sum((p[k]-a[k])*v[k] for k in (0,1))/den)) if den else 0;return [a[k]+t*v[k] for k in (0,1)],t
# Local alternative type attempts are bounded45 sources, not another county rescan.
for idx in sorted(localids,key=lambda i:min(math.dist(centre(c['buildings'][i]),v) for v in regions.values()))[:45]:
 src=c['buildings'][idx];C=centre(src);region=min(regions,key=lambda k:math.dist(C,regions[k]));meta=metadata.get(idx);intent=meta['landUseIntent'] if meta else 'unconfirmed-local-context';co=Counter();attempts=Counter();routes=Counter();passes=[];sb=bbox(src);rr=[(r,j,a,b) for r,j,a,b,bb in segments if boxgap(sb,bb)<65]
 if not meta:rows.append({'sourceIndex':idx,'stage':'intent-unknown','decision':'deferred-no-new-function-assumption'});continue
 for aid in ['B05','B06','B01','B03','B04','B07','B08','B02']:
  if aid=='B03' and (intent!='mixed' or zone(C)!='denseUrban') or aid in ['B04','B08'] and intent not in ['mixed','park'] or aid=='B07' and intent not in ['mixed','residential']:co[aid+':programme-context']+=1;continue
  for scale in ([1] if aid=='B01' else [.9,1,1.1]):
   for du,dn in [(0,0),(-3,0),(3,0),(0,-3),(0,3)]:
    attempts[f'{aid}@{scale}']+=1;anchor=add(add(C,mul(u,du)),mul(n,dn));poly=footprint(aid,anchor,scale);q=audit(poly,[idx])
    if not good(q,True):
     for k,v in q.items():
      if k=='allVerticesBlue' and not v or k!='allVerticesBlue' and v<{'otherSourceMetres':2,'roadEdgeMetres':2,'waterSafetyMetres':5,'visible143GroundBodyMetres':1,'otherNewBodyMetres':2}[k]:co[aid+':'+k]+=1
     continue
    entry=pixelmap(doors[aid],anchor,cal[aid],scale);start=pixelmap([713,626],anchor,cal[aid],scale) if aid=='B07' else entry;prefix=[start]+([add(anchor,mul(n,7*scale))] if aid=='B07' else []);found=None
    for r,j,a,b in sorted(rr,key=lambda q:math.dist(start,foot(start,q[2],q[3])[0]))[:3]:
     stop,t=foot(prefix[-1],a,b);D=math.dist(stop,prefix[-1])
     if D<=r['width']/2+2 or D>45:continue
     v=[(stop[k]-prefix[-1][k])/D for k in (0,1)];end=add(stop,mul(v,-(r['width']/2+.03)));out=add(prefix[-1],mul(n,1.1));mid=add(out,mul(u,sum((end[k]-out[k])*u[k] for k in (0,1))))
     for kind,pts in [('direct',prefix+[end]),('side-L',prefix+[out,mid,end])]:
      routes[aid+':'+kind]+=1;pts=[v for k,v in enumerate(pts) if k==0 or math.dist(v,pts[k-1])>.001];polys=[strip(a,b) for a,b in zip(pts,pts[1:])]+[rect(p,1.5,1.5) for p in pts[1:-1]]
      if not all(good(audit(p,[idx])) for p in polys):co[aid+':approach-external']+=1;continue
      if aid=='B07' and any(pp(p,poly)<.05 for p in polys):co[aid+':court-vs-U-body']+=1;continue
      if aid!='B07':
       if any(pp(p,poly)<.05 for p in polys[1:]) or inside(add(start,mul(n,.6)),poly):co[aid+':door-body']+=1;continue
       first=strip(add(start,mul([(pts[1][k]-start[k])/math.dist(start,pts[1]) for k in (0,1)],.6)),pts[1])
       if first is None or pp(first,poly)<.05:co[aid+':door-body']+=1;continue
      found={'sourceIndex':idx,'sourceIndices':[idx],'stratum':meta,'assetId':aid,'anchorMap':anchor,'uniformScale':scale,'footprintPolygonMap':poly,'entryMap':entry,'entryPixel':doors[aid],'approach':{'roadId':r['id'],'segmentIndex':j,'routeTemplate':kind,'centrelineMap':pts,'polygonsMap':polys},'score':D,'regionId':region,'distanceToExistingFocusMetres':math.dist(anchor,regions[region])};break
     if found:break
    if found:passes.append(found);fitopts.append(found);break
   if any(p['assetId']==aid for p in passes):break
 rows.append({'sourceIndex':idx,'regionId':region,'sourceLandUseIntent':intent,'actualAssetScaleAttempts':dict(attempts),'actualApproachAttempts':dict(routes),'rejectedByRule':dict(co),'feasibleTypes':[x['assetId'] for x in passes]});write('local-fit-progress.json',{'rows':rows,'newFitOptions':fitopts,'existingPoolOptions':len(existing),'localSourcesBudget':45})
print('LOCAL COMPLETE',len(rows),len(fitopts),flush=True)
