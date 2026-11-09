#!/usr/bin/env python3
"""Count every source object, retain explicit unassigned states; never mutate frozen seed."""
import ast,json,math,hashlib,itertools,html
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;K=O.parent.parent;ROOT=next(p for p in O.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists())
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
seedfile=O/'first-expansion-batch.json';frozen=sha(seedfile);seed=read(seedfile);cf=Path(seed['source']['cityPath']);lf=Path(seed['source']['approvedCountyLayoutPath']);c=read(cf);legacy=read(lf);zf=ROOT/'docs/art/2026-11-02-county-zoning/selection.json';z=read(zf);scene=read(seed['protectedExisting']['scenePath']);P=seed['projection'];u=[.23417355683909316,-.9721948082958105];n=[-u[1],u[0]]
assert sha(seed['protectedExisting']['scenePath'])==seed['protectedExisting']['sceneSHA256']
names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'};tree=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),'<pure-geometry>','exec'))
def bbox(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def centroid(p):return [sum(v[i] for v in p)/len(p) for i in (0,1)]
blue=z['regions']['city']['worldPolygonMetresApprox'];red=z['regions']['map']['worldPolygonMetresApprox'];bblue=bbox(blue)
def overlap(a,b):return a[0]<=b[2] and a[2]>=b[0] and a[1]<=b[3] and a[3]>=b[1]
def classify(poly):
 if all(inbounds(v,'city') for v in poly):return 'wholly-blue'
 if overlap(bbox(poly),bblue) and pp(poly,blue)==0:return 'cross-blue'
 if overlap(bbox(poly),bbox(red)) and pp(poly,red)==0:return 'red-outside-blue'
 return 'outside-red'
bound={b['visualReplacementOf']['sourceIndex']:b for b in seed['buildings']};screen=read(O/'source-carrier-screening.json');screenby={x['sourceIndex']:x for x in screen['screened']};raw=[]
for i,poly in enumerate(c['buildings']):
 band=classify(poly);b=bound.get(i);state='assigned' if b else 'deferred' if band=='wholly-blue' else 'excluded'
 why='frozen009 visual replacement candidate, not currently rendered source coverage' if b else 'inside-blue raw source geometry retained; no accepted native assignment yet' if band=='wholly-blue' else 'cross-blue whole building excluded; never clip or shift source footprint' if band=='cross-blue' else 'natural outer display area; no business/navigation expansion; any sparse background residence requires separate scenery approval' if band=='red-outside-blue' else 'outside this red-map display scope'
 raw.append({'sourceId':f'city.buildings[{i}]','sourceArrayIndex':i,'sourceSHA256':sha(cf),'zone':zone(centroid(poly)),'boundaryClass':band,'bounds':bbox(poly),'status':state,'reason':why,'assignedPersistentId':b['persistentId'] if b else None,'renderState':'planned-not-imported' if b else 'source-visual-coverage-not-certified','screening':screenby.get(i),'existingOverlapDoesNotCertifyWholeSourceReplacement':True})
parcelbindings={}
for b in seed['buildings']:parcelbindings.setdefault(b['legacyParcelId'],[]).append(b['persistentId'])
parcels=[]
for i,p in enumerate(legacy['parcels']):
 rings=p['rings'];bb=bbox([v for ring in rings for v in ring]);band=classify(rings[0]);linked=parcelbindings.get(p['id'],[]);visible=[]
 for b in scene['blocks']:
  q=b['anchorMap']
  if bb[0]<=q[0]<=bb[2] and bb[1]<=q[1]<=bb[3] and sum(inside(q,r) for r in rings)%2:visible.append(b['persistentId'])
 state='assigned' if linked else 'deferred' if band=='wholly-blue' else 'excluded'
 parcels.append({'sourceId':p['id'],'sourceArrayIndex':i,'geometrySourceSHA256':sha(lf),'bounds':bb,'zone':p.get('zone',zone(p['center'])),'landUseIntent':p['landUse'],'areaSquareMetresApprox':p.get('areaSquareMetresApprox'),'boundaryClass':band,'status':state,'reason':'partial static seed linkage; remainder of full legacy parcel unrendered/deferred' if linked else 'legacy geometry/function retained, no native-scene coverage assignment' if state=='deferred' else 'outside/cross blue scope; do not enlarge boundary','seedPersistentIds':linked,'existingVisibleAnchorsInsideParcel':visible,'coverageExtent':'partial-only; no whole-parcel completion claim' if linked or visible else 'none-certified','ringFillRule':p.get('ringFillRule','evenodd')})
added=[{'sourceId':b['id'],'sourceArrayIndex':i,'parcelId':b['parcelId'],'bounds':bbox(b['footprint']),'status':'deferred' if classify(b['footprint'])=='wholly-blue' else 'excluded','reason':'legacy decorative volume intent only; refused extrusion/module not reinstated; no raw bitmap asset assignment','legacyModuleIntent':b.get('module'),'rendered':False} for i,b in enumerate(legacy['addedBuildings'])]
counts={'sourceBuildingsTotal':len(raw),'sourceBoundaryClasses':dict(Counter(x['boundaryClass'] for x in raw)),'sourceStatuses':dict(Counter(x['status'] for x in raw)),'legacyParcelsTotal':len(parcels),'parcelStatuses':dict(Counter(x['status'] for x in parcels)),'legacyAddedBuildingIntentsTotal':len(added),'addedIntentStatuses':dict(Counter(x['status'] for x in added)),'existingDisplayedStaticInstances':57,'existingDisplayedGroundPolygons':115,'newSeedBlocks':len(seed['blocks']),'newSeedBuildings':len(seed['buildings']),'newSeedGroundPolygons':len(seed['groundSurfaces']),'newSeedDisplayed':0,'verifiedExistingSourceReplacementBindings':0,'sourceBindingCaveat':'57 displayed instance identities are known; no explicit source-building replacement binding in read-only scene snapshot, so do not infer raw-source completed count from anchor overlap'}
assert sum(counts['sourceStatuses'].values())==len(c['buildings']) and sum(counts['parcelStatuses'].values())==len(legacy['parcels']) and sum(counts['addedIntentStatuses'].values())==len(legacy['addedBuildings'])
area=Counter()
for p in legacy['parcels']:area[p['landUse']]+=p.get('areaSquareMetresApprox',0)
coverage={'schemaVersion':1,'status':'exhaustive-source-index-not-rendered-county','sources':seed['source'],'blueGreenRed':z['regions'],'counts':counts,'sourceBuildings':raw,'legacyParcels':parcels,'legacyAddedBuildingIntents':added,'existingVisibleInstances':[{'persistentId':b['persistentId'],'assetId':b['sourceAssetId'],'anchorMap':b['anchorMap']} for b in scene['blocks']],'residentialAreaPolicy':{'targetDirection':'about50% of overall blue planned block land, not building counts','renderedBlueResidentialAreaQuantified':False,'legacyLandUseAreaProxySquareMetres':dict(area),'denominatorCaveat':'legacy decorative parcel area omits source buildings/roads/water and has mixed courtyard attribution; no claim actual county housing target achieved'},'frozenSeed':{'path':str(seedfile),'sha256':frozen},'invariants':{'allStatusCountsBalance':True,'unpaintedRawBuildingsRemainIndexed':True,'sourceGeometryChanged':False,'blueDeliveryBoundaryWidened':False}}
write('county-coverage-index.json',coverage)
# Measured common source-road direction deficit; not27 directions x all assets.
nodes={p['id']:[p['x'],p['y']] for p in c['nodes']};bins=Counter();examples={}
for r in c['roads']:
 for i,(aa,bb) in enumerate(zip(r['nodes'],r['nodes'][1:])):
  a,b=nodes[aa],nodes[bb]
  if not all(inbounds(v,'city') for v in [a,b]) or math.dist(a,b)<15:continue
  v=[b[k]-a[k] for k in (0,1)];sv=[v[0]*P['axisX'][k]+v[1]*P['axisY'][k] for k in (0,1)];angle=(math.degrees(math.atan2(sv[1],sv[0]))+90)%180-90;delta=(angle+28.486362688849802+90)%180-90
  if abs(delta)>5:
   key=round(angle/10)*10;bins[key]+=1;examples.setdefault(key,[])
   if len(examples[key])<3:examples[key].append({'roadId':r['id'],'nodeRangeInclusive':[i,i+1],'nodeIds':[aa,bb],'angleDeg':angle})
index=read(K/'revision-006/references/approved-25-index.json') if (K/'revision-006/references/approved-25-index.json').exists() else None
ref=next(x for x in index['sources'] if x['imageNumber']==1) if index else None
common=bins.most_common(1)[0]
gaps={'status':'prioritized-evidence-no-production-order','seedCanInstantiateWithoutNewImages':True,'items':[{'rank':1,'kind':'calibration-and-interface','scope':'seed doorway contacts','gap':'read-only actual native door/step rim levels need pipeline admission; first0.6m clear does not certify threshold height or every pixel of first strip','action':'verify imported foot/door controls; reject individual candidate if physical rim fails; no new PNG by default','reference25':ref},{'rank':2,'kind':'native-direction','scope':'expand beyond current3 source-road spans','gap':f'common blue-inner road frontage bin{common[0]}deg has{common[1]} segments>=15m beyond current family tolerance','footprintCandidateMetres':[8,6],'body':'one compact low-rise residential family, new native facing only if needed after fit study','sourceRoadExamples':examples[common[0]],'action':'one common direction first, not27-direction matrix; no rotate/shear PNG','reference25':ref},{'rank':3,'kind':'source-entry-mapping','scope':'preserved original business carriers','gap':'screened original POI carriers deferred until fixed pixel door connects exact unchanged node with source-building geometry exemption and neighbor clearance','action':'mapping/calibration first; not proof new bitmap required','sourcePOICarriers':[x for x in screen['screened'] if x['businessPOIIndices']],'reference25':ref},{'rank':4,'kind':'source-compatible-residential-fit','scope':'nearby northern source carriers631/616/617 not admitted','gap':'existing actual contours/corridors or relative source area failed joint scene selection; six-block residential/public/suburban mix not reached','footprintCandidateMetres':[6,4],'body':'compact roof/low-rise courtyard volume rather than another glass office','action':'first assess positive uniform scale and exact joint placement; new native only if those fail; this dimension is a candidate, not measured source size','reference25':ref}],'heldAssets':['B09','B10','B11'],'P09':'independent garden comparison only','naturalPlants':'county outer landscape remains unassigned; tree-pitT02 must not be mass forest; dedicated natural vegetation later, not blocking this seed'}
write('resource-gaps.json',gaps)
# Readback actual exported seed surfaces / replacement exemptions against other source bodies, original roads, water and protected areas.
static=[]
for b in seed['buildings']:
 idx=b['visualReplacementOf']['sourceIndex'];poly=b['footprintPolygonMap'];walk=b['doorApproach']['polygonMap'];pb=bbox(poly+walk);others=[p for i,p in enumerate(c['buildings']) if i!=idx and bbox(p)[0]<pb[2]+50 and bbox(p)[2]>pb[0]-50 and bbox(p)[1]<pb[3]+50 and bbox(p)[3]>pb[1]-50]
 gp=min([pp(poly,p) for p in others]+[9999]);gw=min([pp(walk,p) for p in others]+[9999]);assert gp>=2.5 and gw>=.15
 assert b['visualReplacementOf']['sourcePolygonMap']==c['buildings'][idx]
 static.append({'persistentId':b['persistentId'],'sourceIndexExemptOnly':idx,'otherSourceFootprintGapMetres':gp,'walkOtherSourceGapMetres':gw,'sourceRawPolygonPreserved':True})
write('static-readback.json',{'frozenSeedSHA256':frozen,'replacementExemptionChecks':static,'note':'same exact double polygon math, no game test; doorway first-strip level uncertainty explicitly unverified'})
# Geometry visualization of actual continuous seed. Raw source buildings remain visible as grey targets.
W,H=1500,1100;focus=[-1594,310];scale=7
xy=lambda v:[750+((v[0]-focus[0])*P['axisX'][0]+(v[1]-focus[1])*P['axisY'][0])*scale,550+((v[0]-focus[0])*P['axisX'][1]+(v[1]-focus[1])*P['axisY'][1])*scale]
im=Image.new('RGB',(W,H),'#f6f4ed');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f6f4ed"/>']
def poly(p,color):
 q=[xy(v) for v in p];dr.polygon(q,fill=color,outline='#888888');svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in q)+f'" fill="{color}" stroke="#888"/>')
def text(p,t):x,y=p;dr.text((x,y),t,fill='#222222');svg.append(f'<text x="{x}" y="{y}" font-size="13" font-family="sans-serif">{html.escape(t)}</text>')
for i,p in enumerate(c['buildings']):
 C=centroid(p)
 if math.dist(C,focus)<200:poly(p,'#e4e0d8')
for r in seed['roads']:
 pts=[xy(v) for v in r['nodes']];dr.line(pts,fill='#aaa69f',width=round(r['width']*scale));svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="#aaa69f" stroke-width="{r["width"]*scale}"/>')
for sf2 in seed['groundSurfaces']:poly(sf2['polygonMap'],'#b4c69d' if 'garden' in sf2['id'] else '#ead8b3')
for b in seed['buildings']:poly(b['footprintPolygonMap'],'#b88f71');text(xy(b['anchorMap']),b['id']+' '+b['assetId'])
dr.rectangle((0,0,W,110),fill='#f6f4ed');svg.append(f'<rect width="{W}" height="110" fill="#f6f4ed"/>');text((24,24),'009 FIRST CONTIGUOUS SEED - STATIC GEOMETRY / NOT GAME SCREENSHOT');text((24,48),'3 consecutive road spans / 4 source visual replacements / 16 grounds. Grey raw targets remain indexed, not claimed painted.');text((24,72),'Actual native contours at scale1; source roads/POI unchanged. Threshold levels and additional6-12 block mix remain deferred.');svg.append('</svg>');(O/'first-batch-projected.svg').write_text('\n'.join(svg));im.save(O/'first-batch-projected.png')
report=f'''# 009首批连续组与全县覆盖盘点

稳定小批 first-expansion-batch.json，SHA {frozen}。已先通知父会话，可独立做导入适配，不等盘点。真实规模为3个连续原路区段、4栋源址视觉替换、16块门前/庭院地面；非6～12街块完成。沿149287903-0第0/1/2段，源索引630/633/634/635，对应B08/B02/B02/B01。631/616/617在新楼/通道联合净距或源/候选面积差下未纳入，不挪路或缩扁补数。现仅商服连续组，住宅/公共/郊区过渡扩量仍欠，不伪称全功能街区交付。

源楼优先：逐个测试完整原生像素地基/PPU、真实门点与源楼中心承载；visualReplacementOf明确真实city.buildings索引，自身原楼仅在该候选避碰中豁免，其他原楼/源半路宽/水/原业务入口不豁免。原源多边形仍在city；未来接入只在通过后隐藏该单一原楼的旧视觉，不能把未画原楼全隐形。业务载体已盘点，尚无固定门到原业务节点的安全映射，deferred并保留原节点，不编POI。旧县布局仅复用地块几何/landUse意图，未恢复程序拉高楼/旧贴图。地面为可见门至原路的1.5m连接及维护庭院边，未称整块历史parcel已画满。

覆盖核算：完整city源建筑{len(raw)}，状态{dict(Counter(x['status'] for x in raw))}；边界分类{counts['sourceBoundaryClasses']}。认可旧布局parcel{len(parcels)}，状态{counts['parcelStatuses']}；补景体量意图{len(added)}逐项deferred/excluded。合计断言成立，每个蓝内未分配目标都保留原因/索引，跨蓝整栋排除，红蓝外自然背景不经营/不导航。旧layout共有1008蓝内源楼等历史数字不直接代替本轮原city重算。住宅约50%为全县蓝内街区用地方向，当前运行住宅面积未量化；历史装饰parcel用途面积只是带分母说明的代理值，不称达标。

当前已实显57静态/115地面保持只读SHA及旧cameraViews；本批新增显示数为0。现有57的实例身份均列出，但无明确原楼替换绑定，不凭点落在parcel就宣称该源楼/parcel完成。主清单区分assigned静态待接入、deferred、excluded与partial范围。first-batch-projected图仅为几何底稿，不代替实际地图。

resource-gaps.json列最多4项优先缺口：原生门槛标定、一个实测常见路向的小住宅、原业务入口映射、邻近紧凑住宅体量匹配。现首批无需新生图；新朝向/新房均先评估现库正等比及联合落位，不是生产指令。B09/B10/B11继续hold；P09不铺县；T03无新增；树池不作自然森林。

执行脚本 build_county_batch.py（冻结小批后不再运行覆盖）、coverage_index.py；static-readback复读替换豁免与他楼净距。来源/保护SHA见protected-inputs.json；未生图/浏览器/服务器/游戏tests/typecheck/回归/业务/存档/提交。所有旧文件未写。
'''
(O/'REPORT.md').write_text(report)
assert sha(seedfile)==frozen
for f,h in read(O/'protected-inputs.json').items():assert sha(f)==h,(f,'source changed')
write('delivery-manifest.json',{'seedFrozenSHA256':frozen,'counts':counts,'allProtectedSHAUnchanged':True,'files':[{'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)} for f in [seedfile,O/'county-coverage-index.json',O/'resource-gaps.json',O/'REPORT.md',O/'first-batch-projected.png']]})
print(json.dumps(counts,ensure_ascii=False,indent=2))
