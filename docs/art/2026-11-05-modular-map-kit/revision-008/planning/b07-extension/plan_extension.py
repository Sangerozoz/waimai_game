#!/usr/bin/env python3
"""Independent B07 comparison site. Never executes or overwrites approved core planner."""
import ast,json,math,hashlib,itertools,html
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;PL=O.parent;K=PL.parent.parent;ROOT=next(p for p in O.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists())
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(f,d):(O/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
corefile=PL/'next-district-plan.json';reviewfile=K/'revision-008/calibration/footprint-review.json';cityfile=ROOT/'delivery-game/assets/resources/map-sample/city.json';zonefile=ROOT/'docs/art/2026-11-02-county-zoning/selection.json'
assert sha(corefile)=='a5412d65a4a9149051f98f43026b8d9e00d4b2e111d3c9366b998a2e4f230758'
assert sha(reviewfile)=='feab3dcbbcbd10e93fe0430af51383b2a981016c29a846485770f558b6626e75'
core=read(corefile);review=read(reviewfile);b=next(a for a in review['assets'] if a['id']=='B07');c=read(cityfile);z=read(zonefile);u=review['localAxes']['T'];n=review['localAxes']['N'];P=review['projection']
names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'};t=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in t.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),'<pure-readonly-geometry>','exec'))
# Record frozen core artifacts, stable review, original city and immutable source image. No viewer reads.
inputs=[corefile,reviewfile,cityfile,zonefile,Path(b['nativePath']),PL/'plan_district.py',PL/'district-projected.svg',PL/'district-projected.png',PL/'REPORT.md',PL/'delivery-manifest.json']
protect={str(f):sha(f) for f in inputs};assert sha(b['nativePath'])==b['nativeSHA256'];write('protected-inputs.json',protect)
site=core['dependencies'][0]['site'];C=site['anchorMap'];nodes={v['id']:[v['x'],v['y']] for v in c['nodes']};r=next(v for v in c['roads'] if v['id']==site['roadId']);seg=site['segmentIndex'];aa,bb=[nodes[r['nodes'][i]] for i in [seg,seg+1]]
def at(p):return add(add(C,mul(u,p[0])),mul(n,p[1]))
def world(poly):return [at(v) for v in poly]
def rectangle(a,t,b,v):return [[a,t],[b,t],[b,v],[a,v]]
def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
bs=[(i,p,bbox(p)) for i,p in enumerate(c['buildings']) if len(p)>=3];wa=[(i,a['points'],bbox(a['points'])) for i,a in enumerate(c['areas']) if a.get('kind')=='water' and len(a.get('points',[]))>=3]
segs=[(rr,i,nodes[a],nodes[d]) for rr in c['roads'] for i,(a,d) in enumerate(zip(rr['nodes'],rr['nodes'][1:])) if boxgap(bbox([nodes[a],nodes[d]]),bbox(site['polygonMap']))<100]
wl=[(a,d) for w in c['waterways'] for a,d in zip(w,w[1:]) if boxgap(bbox([a,d]),bbox(site['polygonMap']))<100];pois=[nodes[p['node']] for p in c['pois'] if p.get('node') in nodes]
occupied=world(b['conservativeOccupiedPolygonLocalTN']);void=world(b['courtyardVoidLocalTN']);clearvoid=world(b['visiblyClearConservativeVoidLocalTN']);reservation=world(b['conservativeReservationPolygonLocalTN']);plot=world(rectangle(-14,-14,14,14));apron=world(rectangle(-4.5,6.2,4.5,10.2))
def nearest(poly,obstacles):
 pb=bbox(poly);best=math.inf;index=None
 for lb,i,p in sorted((boxgap(pb,bb),i,p) for i,p,bb in obstacles):
  if lb>best:break
  d=pp(poly,p)
  if d<best:best,index=d,i
 return best,index
coreGround=[s['polygonMap'] for s in core['groundSurfaces']];coreProtect=core['selectedSite']['polygonMap'];oldProtect=core['protected006']['expandedProtectionPolygonMap']
def audit(poly):
 sb,idx=nearest(poly,bs);wg,_=nearest(poly,wa)
 return {'sourceBuildingGapMetres':sb,'nearestSourceBuildingIndex':idx,'roadEdgeGapMetres':min(pl(poly,a,d)-rr['width']/2 for rr,i,a,d in segs),'waterSafetyGapMetres':min([wg]+[pl(poly,a,d)-3 for a,d in wl]),'approvedCoreSiteGapMetres':pp(poly,coreProtect),'approvedCoreGroundGapMetres':min(pp(poly,q) for q in coreGround),'original43ProtectionGapMetres':pp(poly,oldProtect),'businessEntranceGapMetres':min(0 if inside(p,poly) else min(ps(p,a,d) for a,d in edges(poly)) for p in pois),'allVerticesBlue':all(inbounds(p,'city') for p in poly),'allVerticesOutsideGreen':all(not inbounds(p,'urban') for p in poly)}
for p in [plot,reservation,occupied,apron]:
 q=audit(p);assert q['allVerticesBlue'] and q['allVerticesOutsideGreen'] and q['sourceBuildingGapMetres']>3 and q['roadEdgeGapMetres']>3 and q['waterSafetyGapMetres']>8 and q['approvedCoreGroundGapMetres']>10
points={v['id']:v for v in b['points']};assert points[15]['classification']=='rejected'
# Fixed real door11 -> native step12. New paving begins at observed step front; original stairs are not repainted.
step=points[12]['localTN'];threshold=points[11]['localTN'];route=[step,[step[0],-.5],[0,6.5],[0,10.2],[0,15]]
def strip(a,d,width):
 L=math.dist(a,d);t=[(d[i]-a[i])/L for i in (0,1)];v=[-t[1],t[0]];return [add(a,mul(v,width/2)),add(d,mul(v,width/2)),add(d,mul(v,-width/2)),add(a,mul(v,-width/2))]
polys=[strip(a,d,1.5) for a,d in zip(route,route[1:])]+[rectangle(p[0]-.75,p[1]-.75,p[0]+.75,p[1]+.75) for p in route[1:-1]]
# Original road shoulder link: nearest source-segment foot, full source half-width, 2cm numerical gap.
start=at(route[-1]);v=[bb[j]-aa[j] for j in (0,1)];tt=max(0,min(1,sum((start[j]-aa[j])*v[j] for j in (0,1))/sum(x*x for x in v)));q=[aa[j]+tt*v[j] for j in (0,1)];L=math.dist(start,q);end=add(q,mul([(start[j]-q[j])/L for j in (0,1)],r['width']/2+.02))
worldpolys=[world(p) for p in polys]+[strip(start,end,1.5)]
walkChecks=[]
for i,poly in enumerate(worldpolys):
 gap=pp(poly,occupied);a=audit(poly);assert gap>.05,(i,'U wing/rear collision',gap)
 assert a['roadEdgeGapMetres']>=-.001 and a['sourceBuildingGapMetres']>2 and a['waterSafetyGapMetres']>8 and a['approvedCoreGroundGapMetres']>10 and a['allVerticesBlue'] and a['allVerticesOutsideGreen']
 walkChecks.append({'index':i,'occupiedUGapMetres':gap,'staticClearance':a})
# Small porous court patch, leaving void mostly open. No full rectangular slab under U, no fake ground used as shadow proof.
landscapes=[('008-B07-court-green',rectangle(-2,0,-.5,2),'small planted court inset; remaining void unfilled'),('008-B07-rear-garden',rectangle(-13,-13,13,-10),'rear planting reserve outside inferred closure'),('008-B07-left-garden',rectangle(-13,-9,-12,10),'side green verge outside padded reservation'),('008-B07-right-garden',rectangle(12,-9,13,10),'side green verge outside padded reservation')]
for pid,purposepoly,why in landscapes:assert pp(world(purposepoly),occupied)>.2
surfaces=[{'id':f'008-B07-walk-{i}','materialId':'S01-paving','polygonMap':poly,'purpose':'1.5m pedestrian-only courtyard/mouth/road-shoulder connection; no navigation edge'} for i,poly in enumerate(worldpolys)]
# Apron is outside wing ends and preserves their front clearance; it is not an opaque courtyard floor.
assert pp(apron,occupied)>.05
surfaces.append({'id':'008-B07-mouth-apron','materialId':'S01-paving','polygonMap':apron,'purpose':'4m deep exterior mouth apron beyond wing ends; keep clear'})
for pid,poly,why in landscapes:surfaces.append({'id':pid,'materialId':'neutral-grass','color':'#a3bc8a','polygonMap':world(poly),'purpose':why})
for s in surfaces:
 q=audit(s['polygonMap']);s['staticClearance']=q;assert q['roadEdgeGapMetres']>=-.001 and q['sourceBuildingGapMetres']>2 and q['waterSafetyGapMetres']>8
road={**r,'nodes':[nodes[i] for i in r['nodes']],'sourceNodeIds':r['nodes']}
# Both lots sit on the same unmodified segment. Read-only segment link connects approved core mouth foot to new mouth foot.
plan={'schemaVersion':1,'version':'b07-extension-v1','status':'independent-static-wide-site-comparison-candidate;not-runtime-or-user-accepted','projection':P,'roads':[road],'buildings':[{'id':'008-B07-extension','persistentId':'008-B07-extension','assetId':'B07','libraryAssetId':'B07','anchorMap':C,'anchorUV':b['anchorUV'],'worldSizeUnits':b['candidateWorldSizeUnits'],'nativePixelsPerUnit':b['nativePixelsPerUnit'],'uniformScale':1,'rotation':0,'footprintPolygonMap':occupied,'courtyardVoidPolygonMap':void,'visiblyClearVoidPolygonMap':clearvoid,'reservationPolygonMap':reservation,'reservationIsPhysicalFootprint':False,'parcelPolygonMap':plot,'entryMap':at(threshold),'entryPixel':points[11]['nativePixel'],'doorPointId':11,'nativeStepFrontMap':at(step),'nativeStepFrontPixel':points[12]['nativePixel'],'stepPointId':12,'walkStartMap':at(step),'oldRejectedDoorPixel':points[15]['nativePixel'],'oldRejectedDoorUsed':False,'wallHeightCandidate':b['wallHeightRecheck']['candidateEaveHeights'][0],'wallHeightEvidencePointPairs':b['wallHeightRecheck']['newVisibleVerticalPairs'],'sourceNativeSHA256':b['nativeSHA256'],'staticClearance':audit(occupied),'visualReplacementOf':None}], 'fixtures':[],'groundSurfaces':surfaces,'parkingSpaces':[],'parkedVehicles':[],'pedestrianConnections':[{'id':'008-B07-court-walk','nativeThresholdToStepPointIds':[11,12],'newPavingBeginsAtStepFrontPointId':12,'widthMetres':1.5,'centrelineMap':[at(p) for p in route]+[end],'surfaceIds':[s['id'] for s in surfaces if 'walk-' in s['id']],'checks':walkChecks,'navigationEdgesAdded':0,'doorPixelsMoved':False,'stairsAndLevelChange':'native step retained, not rebuilt; riser height/accessibility unverified'}],'site':site,'plotFrontageDepthCandidate':[28,28],'mouthApronDepthMetres':4,'sourceEvidence':{'corePlanPath':str(corefile),'coreSHA256':sha(corefile),'calibrationPath':str(reviewfile),'calibrationSHA256':sha(reviewfile),'sourceCityPath':str(cityfile),'sourceCitySHA256':sha(cityfile),'zoningPath':str(zonefile),'zoningSHA256':sha(zonefile),'regions':z['regions'],'zone':'blue-minus-green suburb; approximate user bounds','original43SnapshotProtection':core['protected006'],'noCurrentViewerRead':True},'protectedCore':{'polygonMap':coreProtect,'minimumPlotGapMetres':pp(plot,coreProtect),'filesUnchanged':True},'originalRoadConnection':{'sourceRoadId':r['id'],'sourceNodeRangeInclusive':[seg,seg+1],'sourceNodeIds':r['nodes'][seg:seg+2],'direction':r['direction'],'width':r['width'],'sameSegmentAsApprovedCore':True,'bothSegmentEndpointsInsideBlue':all(inbounds(p,'city') for p in [aa,bb]),'existingCoreConnectivityReusedByReference':str(corefile),'newSourceEdges':0},'resourcePolicy':{'runtimeMaxEdge':280,'sharedTexturePerFileSHA':True,'nativeMastersExcluded':True,'B07PPUUVWorldFrameUnchanged':True,'B09B11':'hold; no placement/placeholder'},'risks':['ground points4/8 hidden and inferred;2m padded envelope is reservation only, not surveyed rear guarantee','visible controls +/-8px; polygon clearances are candidate static geometry, not precise native registration','actual doorstep/riser and runtime sorting/occlusion require later same-map comparison; no game or browser validation','wall11.81m uses numbered vertical236px pairs; sprite untouched, not compressed'], 'checks':{'allWalkPolygonsOutsideOccupiedU':True,'minimumWalkOccupiedGapMetres':min(x['occupiedUGapMetres'] for x in walkChecks),'noWholeVoidOpaqueFloor':True,'transparentCourtNotDoor':True,'noRoadBuildingWaterPOIModified':True,'sourceReadbackProtected':True}}
runtime=Path(b['nativePath']).with_name('B07-runtime-280.png')
assert runtime.is_file() and sha(runtime)==b['runtimeSHA256'] and list(Image.open(runtime).size)==b['runtimeSize'] and max(Image.open(runtime).size)<=280
plan['resourceDependencies']=[{'assetId':'B07','path':str(runtime),'sha256':sha(runtime),'dimensions':list(Image.open(runtime).size),'bytes':runtime.stat().st_size,'anchorUV':b['anchorUV'],'worldSizeUnits':b['candidateWorldSizeUnits'],'nativePixelsPerUnit':b['nativePixelsPerUnit'],'sharedImageFrameKey':b['runtimeSHA256'],'nativeMasterNotPackaged':True}]
plan['checks']['allSurfaceStaticChecks']=[{'id':sf['id'],'clearance':sf['staticClearance']} for sf in surfaces]
write('b07-extension-plan.json',plan)
# Project occupied U vs void and actual numbered door/step controls. Inset shows real blue/green positions.
W,H=1600,1150;sc=24
project=lambda p:[(p[0]-C[0])*P['axisX'][j]+(p[1]-C[1])*P['axisY'][j] for j in (0,1)]
def xy(p):q=project(p);return [710+q[0]*sc,530+q[1]*sc]
im=Image.new('RGB',(W,H),'#f6f4ef');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f6f4ef"/>']
def poly(p,fill,stroke='#777777'):
 ps=[xy(v) for v in p];dr.polygon(ps,fill=fill,outline=stroke);svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in ps)+f'" fill="{fill}" stroke="{stroke}"/>')
def label(pos,t):
 x,y=pos;dr.text((x,y),t,fill='#222222');svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="14">{html.escape(t)}</text>')
# Plot/reservation boundaries; keep U void visibly separate from built body.
poly(plot,'#e8e2d8','#aa967c');poly(reservation,'#e3d5bd','#b49062');poly(void,'#f6f4ef','#73a3ae')
for s in surfaces:poly(s['polygonMap'],s.get('color','#ead9a9'))
poly(occupied,'#a98f9d','#654d5b')
# Padded reservation above is a diagnostic guide, not exported ground. Actual scene grounds are only surfaces above.
for id in [1,2,3,4,5,6,7,8,11,12,13]:
 p=at(points[id]['localTN']);x,y=xy(p);dr.ellipse((x-3,y-3,x+3,y+3),fill='red' if id in [11,12] else '#334957');label((x+5,y+3),str(id))
a,bp=xy(aa),xy(bb);dr.line([a,bp],fill='#a6a39d',width=round(r['width']*sc));svg.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{bp[0]}" y2="{bp[1]}" stroke="#a6a39d" stroke-width="{r["width"]*sc}"/>')
label(xy(end),'SOURCE ROAD149665990-0 / segment10')
label((24,22),'B07 EXTENSION - GEOMETRY DRAFT / BLUE INSIDE GREEN OUTSIDE / NOT A GAME SCREENSHOT')
label((24,46),'Purple = actual reviewed U outline; pale void = unbuilt court; tan padded reservation = diagnostic ONLY, not exported floor')
label((24,70),'Door11 [704,609] -> native step12 [713,626]; new1.5m paving starts at step12. OLD [746,825] rejected (transparent void).')
label((24,94),'Plot28x28m + exterior mouth apron4m; hidden rear points4/8 inferred with2m reservation. No PNG rotation / scale change.')
label((1070,170),'WORLD ZONING INSET')
# Real approximate rectangles and both sites; distinguish long-distance world context from local diagram.
for key,color in [('map','#ce7770'),('city','#648db2'),('urban','#76a780')]:
 bbz=z['regions'][key]['worldBoundsMetresApprox'];pts=[(1080+(bbz['minX']+3200)*.14,220+(1506-bbz['maxY'])*.14),(1080+(bbz['maxX']+3200)*.14,220+(1506-bbz['minY'])*.14)];dr.rectangle([pts[0],pts[1]],outline=color,width=2);svg.append(f'<rect x="{pts[0][0]}" y="{pts[0][1]}" width="{pts[1][0]-pts[0][0]}" height="{pts[1][1]-pts[0][1]}" fill="none" stroke="{color}"/>')
for name,p in [('B07',C),('CORE',core['selectedSite']['anchorMap'])]:
 x,y=1080+(p[0]+3200)*.14,220+(1506-p[1])*.14;dr.ellipse((x-3,y-3,x+3,y+3),fill='#222222');label((x+4,y),name)
svg.append('</svg>');(O/'b07-projected.svg').write_text('\n'.join(svg));im.save(O/'b07-projected.png')
assert all(sha(f)==v for f,v in protect.items())
report=f'''# B07独立宽院比较候选

稳定文件 b07-extension-plan.json。使用已预留第二块58×40m场地，anchor={C}，蓝内绿外郊区。实际采用28×28m地块、U形占地/void及2m隐后角预留，院口外4m铺装。与批准核心地块最小距{pp(plot,coreProtect):.3f}m，不改核心JSON/脚本/图/报告，不读接入作者viewer。

校准固定SHA feab3dcbbcbd10e93fe0430af51383b2a981016c29a846485770f558b6626e75。选择真实门11 [704,609]、台阶12 [713,626]；旧746,825是透明中庭，完全不作入口。新1.5m院内/院口铺地从台阶前沿12起，原图门与台阶不动。每块铺地均用多边形对源半路宽/水/源楼/核心/原43保护区核对，U形实体最小净距{plan['checks']['minimumWalkOccupiedGapMetres']:.3f}m。中庭不铺满不透明地板，仅窄步行与小植被块；诊断图的预留底色不是导出地面，不用草地假阴影作认证。

PPU43.283474381889086、anchorUV及22.4566×22.9649图框原样保持。墙高约11.808m来自236px编号控制对16→2、17→3；旧16m估计已纠正，非压图。原路149665990-0完整节点/宽5m/方向0保持；两地块同第10段、节点1626058688→1626058281，均蓝内，沿用核心原有去回连通证据，无新捷径/POI/导航边。

真实风险：4/8为隐后角推断，2m预留非测绘保证；可见点±8px、真实台阶高差、运行排序/遮挡尚未认证。仅B07可进小规模比较，B09/B11继续hold，不用矩形替身。原43用核心内冻结保护多边形与原SHA证据保护，未读取当前在写场景。

脚本plan_extension.py已执行，只写b07-extension。投影图含蓝绿真实分区位置、原路/像素门点/footprint-vs-void。未生图、浏览器/服务器、游戏tests/typecheck/回归、存档或提交。所有保护输入SHA执行末保持。
'''
(O/'REPORT.md').write_text(report)
write('delivery-manifest.json',{'status':plan['status'],'protectedUnchanged':True,'files':[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in [O/'b07-extension-plan.json',O/'b07-projected.png',O/'b07-projected.svg',O/'REPORT.md',O/'plan_extension.py']]})
print('DONE',sha(O/'b07-extension-plan.json'),plan['checks'],flush=True)
