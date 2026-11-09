#!/usr/bin/env python3
"""Registry/joint protection proof and local geometric draft; frozen scenes never rewritten."""
import context as x
from freeze import validate
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,itertools,html
O=x.O;basefiles=sorted(O.glob('scene-[0-9][0-9][0-9][0-9].json'));files=[f.with_name(f.stem+'-v2.json') if f.with_name(f.stem+'-v2.json').exists() else f for f in basefiles];plans=[x.read(f) for f in files];frozen={str(f):x.sha(f) for f in files};assert 1<=len(plans)<=3
assert len({s['sceneId'] for p in plans for s in p['scenes']})==len(plans)
allsource=[i for p in plans for i in p['sourceIndices']];assert len(allsource)==len(set(allsource)) and not set(allsource)&(x.bound|x.reserved)
entries=[];resources={};directions=[];fullproof=[]
for f,p in zip(files,plans):
 proof=validate(p,[other for other in plans if other is not p]);fullproof.append({'file':str(f),'sha256':x.sha(f),'verification':proof});s=p['scenes'][0];entries.append({'file':str(f),'sha256':x.sha(f),'sceneId':s['sceneId'],'sourceIndices':p['sourceIndices'],'moduleIds':s['moduleIds'],'moduleAssets':[{'id':b['libraryAssetId'],'scaleOnce':b['uniformScale'],'finalWorldSizeUnits':b['worldSizeUnits']} for b in p['buildings']],'grounds':p['groundSurfaceCount'],'sourceAreaSquareMetres':s['sourceCarrierAreaSquareMetres'],'newBodyAreaSquareMetres':s['newOccupiedFootprintAreaSquareMetres'],'programme':s['scenicProgramme'],'legacyUseEvidence':s['programmeEvidence'].get('legacyLandUseIntent'),'zone':s['zoning']['layer'],'renderedNew':0,'userAcceptedNew':0,'importContractPath':str(f.with_name(f.stem+'-import-contract.json'))})
 for b in p['buildings']:
  aid=b['libraryAssetId'];a=x.assets[aid];runtime=x.K/'revision-006/integration/assets'/a['file'];im=Image.open(runtime);assert max(im.size)<=280 and x.sha(runtime)==a['sha256'];native=Path(a['runtimeDerivation']['source']);assert x.sha(native)==a['runtimeDerivation']['sourceSHA256'];resources[aid]={'runtimePath':str(runtime),'runtimeSHA256':x.sha(runtime),'runtimeSize':list(im.size),'runtimeBytes':runtime.stat().st_size,'nativeReadOnlyPath':str(native),'nativeSHA256':x.sha(native),'sharedExistingTexture':True,'newImages':0};ap=b['visualApproach'];r=next(r for r in x.c['roads'] if r['id']==ap['roadId']);j=ap['segmentIndex'];aa,bb=[x.nodes[nid] for nid in r['nodes'][j:j+2]];d=[bb[k]-aa[k] for k in (0,1)];v=[sum(d[k]*x.P['axisX' if k==0 else 'axisY'][t] for k in (0,1)) for t in (0,1)];directions.append({'moduleId':b['id'],'roadId':r['id'],'nodeRangeInclusive':[j,j+1],'nodeIds':r['nodes'][j:j+2],'realSourceEndpoints': [aa,bb],'sourceWorldTangentDeg':math.degrees(math.atan2(d[1],d[0])),'sourceScreenTangentDeg':math.degrees(math.atan2(v[1],v[0])),'nativeFrontageScreenDeg':-28.486,'nativeDepthScreenDeg':55.406,'orientationAdjustmentPNG':'none','approachMethod':ap['strategy'],'worldAndScreenAnglesSeparate':True})
pairs=[]
for a,b in itertools.combinations(plans,2):
 def minimum(aa,bb):return min((x.pp(p,q),i,j) for i,p in aa for j,q in bb)
 ab=[(z['id'],z['footprintPolygonMap']) for z in a['buildings']];bb=[(z['id'],z['footprintPolygonMap']) for z in b['buildings']];ag=[(z['id'],z['polygonMap']) for z in a['groundSurfaces']];bg=[(z['id'],z['polygonMap']) for z in b['groundSurfaces']];row={'sceneA':a['scenes'][0]['sceneId'],'sceneB':b['scenes'][0]['sceneId'],'bodyBodyMinimum':minimum(ab,bb),'bodyGroundMinimum':min(minimum(ab,bg),minimum(bb,ag)),'groundGroundMinimum':minimum(ag,bg),'noSourceReuse':not set(a['sourceIndices'])&set(b['sourceIndices'])};assert row['bodyBodyMinimum'][0]>=2 and row['bodyGroundMinimum'][0]>=1 and row['groundGroundMinimum'][0]>=.15;pairs.append(row)
summary=[]
for f in sorted(O.glob('source-*-attempts.json')):
 d=x.read(f);idx=d['sourceIndex'];opts=x.read(O/f'source-{idx:04d}-options.json');jointfile=O/f'source-{idx:04d}-joint-audit.json';j=x.read(jointfile) if jointfile.exists() else None;summary.append({'sourceIndex':idx,'nativeAssetScaleAnchorAttempts':sum(d['assetScaleAttempts'].values()),'doorStrategiesAttempted':sum(d['routeStrategyAttempts'].values()),'distinctModuleOptions':len(opts),'optionAssetIds':sorted({o['assetId'] for o in opts}),'multiLabelRejectionCounts':d['multiLabelRejectedAttempts'],'jointAudit':j,'wallTimeBudgetReached':d.get('wallTimeBudgetReached',False),'outcome':'frozen-static-scene' if idx in allsource else 'not-selected','unknownOriginalSemanticRetained':True})
registry={'status':'frozen-small-static-compound-set-pending-independent-review-parent-SHA-and-limited-importer-scope-adaptation','inputSHA256':x.protected,'publishedBaseline':{'sceneSHA256':x.sha(x.sf),'tiledSHA256':x.sha(x.tf),'staticCount':163,'groundCount':506,'sourceUnionCount':82,'boundModuleCount':83,'compound125IncludedAndProtected':True,'noSnapshotReplay':True},'counts':{'uniqueSources':len(allsource),'scenes':len(plans),'modules':sum(p['moduleCount'] for p in plans),'grounds':sum(p['groundSurfaceCount'] for p in plans),'renderedNew':0,'userAcceptedNew':0},'sourceIndices':sorted(allsource),'supersededV1NotForCoImport':[{'path':str(f),'sha256':x.sha(f),'reason':'immutable first geometry candidate retained; replace as a whole with corresponding v2; importing both forbidden'} for f in basefiles if f not in files],'designEvidenceSourceSHA256':{str(x.PL/'fit-round-3/fit-progress-strategy-audit.json'):x.sha(x.PL/'fit-round-3/fit-progress-strategy-audit.json')},'entries':entries,'crossSceneProtection':pairs,'sourceAccounting':x.accounting,'roadDirectionEvidence':directions,'resourceDependencies':resources,'screening':summary,'excludedHistoricalReplays':{'source1and377':'not retried; old three-offset failure not rebranded','source590':'not retried; prior bounded failure retained read-only','source654plus2387':'historical candidate read only; ~900m from current focus, no scatter scene added simply to meet count'},'scopeWhiteList':{'currentConsumerOnly125':True,'sharedCodeModified':False,'thisIsNotGeometryRejection':True,'requiresIndependentReviewAndExplicitParentSHAApproval':True},'latestSerialImportPolicy':'compare against latest actually completed published scene, protect all previous scene increments, never replay this163 snapshot','oldSurfaceEditPermissionsRequested':[],'newNativeTypeRequests':[],'coverageStatement':'bounded local scenery only; no blue denominator or housing area completion claim'}
x.write('registry.json',registry);x.write('registry-static-verification.json',{'status':'passed-pure-static','frozenSceneSHA256':frozen,'sceneProofs':fullproof,'crossSceneProofs':pairs,'inputSHA256After':{f:x.sha(f) for f in x.protected},'oldInputChanges':[]})
# One locality diagram, plus same projection detail panels for each frozen scene.
W,H=1800,1550;im=Image.new('RGB',(W,H),'#faf9f5');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#faf9f5"/>']
def text(pos,s,size=16,color='#222222'):
 try:font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',size)
 except OSError:font=ImageFont.load_default()
 dr.text(pos,s,font=font,fill=color);svg.append(f'<text x="{pos[0]}" y="{pos[1]+size}" font-size="{size}" font-family="Arial,sans-serif" fill="{color}">{html.escape(s)}</text>')
def projected(q):return [sum(q[k]*x.P['axisX' if k==0 else 'axisY'][j] for k in (0,1)) for j in (0,1)]
colors={'B01':'#7595b8','B02':'#a893c5','B03':'#a181b6','B04':'#c19173','B05':'#d3a15e','B06':'#aa7b7b','B07':'#b6a278','B08':'#b8ba86'}
def panel(box,world,title,selPlans,labels=False):
 bb=x.bbox([projected(v) for v in world]);fac=min((box[2]-box[0])/(bb[2]-bb[0]),(box[3]-box[1])/(bb[3]-bb[1]));cx=(bb[0]+bb[2])/2;cy=(bb[1]+bb[3])/2;tf=lambda q:[(projected(q)[0]-cx)*fac+(box[0]+box[2])/2,(projected(q)[1]-cy)*fac+(box[1]+box[3])/2];b=x.bbox(world);layer=Image.new('RGB',(W,H),'#faf9f5');ld=ImageDraw.Draw(layer);tag='c'+str(box[0])+str(box[1]);svg.append(f'<defs><clipPath id="{tag}"><rect x="{box[0]}" y="{box[1]}" width="{box[2]-box[0]}" height="{box[3]-box[1]}"/></clipPath></defs><g clip-path="url(#{tag})">')
 def poly(po,fill,stroke='#888888',width=1):
  pts=[tf(v) for v in po];ld.polygon(pts,fill=fill);ld.line(pts+[pts[0]],fill=stroke,width=width);svg.append('<polygon points="'+' '.join(f'{q[0]:.2f},{q[1]:.2f}' for q in pts)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
 for z in x.oldground:
  if x.bgap(b,x.bbox(z['poly']))<5:poly(z['poly'],'#d9dfd1','#b9c5b0')
 for r,j,aa,bb,rb in x.allsegments:
  if x.bgap(b,rb)<5:poly(x.strip(aa,bb,r['width']),'#a3a3a2','#909190')
 for i,po,rb in x.bs:
  if x.bgap(b,rb)<2 and i not in allsource:poly(po,'#ece5de','#cfbfb1')
 for z in x.oldbody:
  if x.bgap(b,x.bbox(z['poly']))<3:poly(z['poly'],'#9aafaa','#67877d')
 for p in selPlans:
  for z in p['groundSurfaces']:poly(z['polygonMap'],'#9db783' if z['materialId'].startswith('G0') else '#e6c99c','#a38b61')
  for z in p['buildings']:poly(z['footprintPolygonMap'],colors[z['assetId']],'#454b53',2)
  for i in p['sourceIndices']:
   pts=[tf(v) for v in x.c['buildings'][i]];ld.line(pts+[pts[0]],fill='#a63d75',width=2);svg.append('<polygon points="'+' '.join(f'{q[0]:.2f},{q[1]:.2f}' for q in pts)+'" fill="none" stroke="#a63d75" stroke-width="2" stroke-dasharray="5 3"/>')
 im.paste(layer.crop(box),box[:2]);svg.append('</g>');text((box[0],box[1]-28),title,18)
 for p in selPlans:
  for z in p['buildings']:
   q=tf(z['anchorMap']);text((q[0]+3,q[1]-12),z['assetId'],14);q=tf(z['entryMap']);dr.ellipse([q[0]-3,q[1]-3,q[0]+3,q[1]+3],fill='#bc2d2d');svg.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="3" fill="#bc2d2d"/>')
 if labels:
  for i in [125,587,343,268,352,339]:
   q=tf(x.center(x.c['buildings'][i]));
   if box[0]<q[0]<box[2] and box[1]<q[1]<box[3]:text(q,'source'+str(i),12,'#7e3260')
 dr.rectangle(box,outline='#bdbdb5');svg.append(f'<rect x="{box[0]}" y="{box[1]}" width="{box[2]-box[0]}" height="{box[3]-box[1]}" fill="none" stroke="#bdbdb5"/>')
text((35,20),'COMPOUND ROUND2 / LOCAL GEOMETRIC DRAFT / STATIC ONLY',27)
text((35,62),f'{len(allsource)} sources / {len(plans)} independent scenes / {sum(p["moduleCount"] for p in plans)} modules / {sum(p["groundSurfaceCount"] for p in plans)} surfaces. Current163/506 and source125 fixed.',18)
panel([35,130,865,850],[[-1500,80],[-1275,80],[-1275,255],[-1500,255]],'Same local district: existing market125 west, new courts east',plans,True)
# zone location inset / actual approved approximate bounds, not inferred from crop.
zbox=[950,150,1750,820];world=x.z['regions']['map']['worldPolygonMetresApprox'];bb=x.bbox(world);f=min(720/(bb[2]-bb[0]),650/(bb[3]-bb[1]));tf=lambda q:[950+(q[0]-bb[0])*f,150+(bb[3]-q[1])*f]
text((950,105),'Approved red / blue / green coordinates (world XY locator)',18)
for key,col in [('map','#b64f55'),('city','#3272ad'),('urban','#558c4b')]:
 po=x.z['regions'][key]['worldPolygonMetresApprox'];pts=[tf(q) for q in po];dr.line(pts+[pts[0]],fill=col,width=3);svg.append('<polygon points="'+' '.join(f'{q[0]:.2f},{q[1]:.2f}' for q in pts)+f'" fill="none" stroke="{col}" stroke-width="3"/>')
for p in plans:
 q=tf(x.center(x.c['buildings'][p['sourceIndices'][0]]));dr.ellipse([q[0]-4,q[1]-4,q[0]+4,q[1]+4],fill='#a03562');svg.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="4" fill="#a03562"/>')
for j,p in enumerate(plans):
 polys=[b['footprintPolygonMap'] for b in p['buildings']]+[g['polygonMap'] for g in p['groundSurfaces']];bb=x.bbox([v for po in polys for v in po]);mx=3;world=[[bb[0]-mx,bb[1]-mx],[bb[2]+mx,bb[1]-mx],[bb[2]+mx,bb[3]+mx],[bb[0]-mx,bb[3]+mx]];n=len(plans);left=35+j*1730/n;right=35+(j+1)*1730/n-20;panel([int(left),940,int(right),1415],world,'Source'+str(p['sourceIndices'][0])+': '+','.join(b['assetId'] for b in p['buildings']),[p])
text((35,1450),'Pink = owned original carrier; no exemption for other source buildings. Red dots = unchanged native visible doors.',17)
text((35,1484),'Footlines/hidden rear are manual estimates. Paving is visual only: no new POI, navigation edge or old-surface edits.',17)
svg.append('</svg>');im.save(O/'round2-local-geometry.png');(O/'round2-local-geometry.svg').write_text('\n'.join(svg))
# Defects/failures and count semantics are explicit, no whole-county claim.
rows='\n'.join(f"|{e['sourceIndices']}|{', '.join(v['id']+'@'+str(v['scaleOnce']) for v in e['moduleAssets'])}|{e['grounds']}|{e['sha256']}|" for e in entries)
(O/'REPORT.md').write_text(f'''# 第二轮局部复合场地：静态候选

当前只读发布基线163静态/506面，源并集82、绑定模块83；scene `{x.sha(x.sf)}`，TMJ `{x.sha(x.tf)}`。已真实核源125所有权与两模块/五面，旧单数/数组只读归一化，未回放156/161、未改共享scope、未apply。

冻结{len(plans)}scene / {len(allsource)}源 / {sum(p['moduleCount'] for p in plans)}模块 / {sum(p['groundSurfaceCount'] for p in plans)}面。新增已显示/用户验收0。各JSON与import-contract独立稳定SHA；源数按场景源并集，不按模块数。

|真实源|模块与单次比例|新面|独立JSON SHA256|
|---|---|---|---|
{rows}

范围为市场125东侧约100～200m的同一片区，不用遥远654+2387凑数，源1/377/590未重跑旧失败。343沿旧garden意图做有限坡顶居住/平顶服务院落，268无可靠原用途metadata，显式PM设计公共体量B04+住居B06共享院落。全部位于绿内/蓝内，原用途unknown，不声称源楼历史用途/经营绑定；TR33完整认可图实看过的坡顶/平顶/公共市场庭院混合只作身份参考。

本轮组合保留不同体量和入口策略；没有要求两栋必须接同一node-range。343第一阶段因这个自设筛选拒绝的证据另留stage1，随后只删除该设计预筛，真实净空/道路半宽/邻源/旧面阈值全保留，实际折线与院坪连接通过。原道路完整数组/顺序/width/direction和原停靠点保持。门为真实原生像素，原停靠node不是图门，不新增nav边/POI。

每scene有限门路、共享连接、实心院坪与种植边互相接续，种植不盖步行面；不修改旧场地，不添加未准入道具。几何图实看后发现v1院坪偏道路端、仍像细线，于是保原v1 SHA另做独立v2：343新增40㎡门前共院＋40㎡绿地，268新增40㎡门前共院＋24㎡绿地，两门真实通路直接入共院，绿地只接院而不盖步道。原楼anchor/真门/原路完全不动。v2作为最终推荐，v1仅历史静态证据，二者不可同导。343的867㎡carrier仍仅局部转化，未布置余地后续设计；不声称填满原楼轮廓或整片空地已完成。已有seed125的B01重复也仍是视觉风险，当前public/住宅第二场景用于避免整批复制同一两楼配方。场地仍是几何意图，不以图形取代实际美术实景。

registry-static-verification实际重新校验每包全部原他源、9970路原半宽、492水道(3m+5m安全)、原水polygon、POI、旧163脚点、506面与同scene互查；各包再次彼此查体体2m、体面1m、面/路0.15m。世界尺寸/脚线/门已一次正比例，nodeScale1，B01基准不变。所有运行图实际校SHA且长边<=280，共享既有纹理、新PNG0。脚线/隐后角手估与首0.6m门槛容差保留，不冒充测绘精确。

逐源尝试/拒绝见source-*-attempts.json与joint-audit。339仅B05单模块选项，不强凑不同族复合；352首轮未优化距离循环约10分钟被主动中止，不能称几何失败，后续100秒墙钟重算完成868个asset@scale/anchor尝试，得17个B02/B03/B05选项，90个异型配对均体间/门路互撞；B07仅测4个anchor、B01尚未进入，不能声称已测完8族或源352无解。多规则次数不是不同源计数；未测候选不当无解。没有新朝向或新原生生产请求。

全部输入SHA前后保持，所有旧场景/原图/共享consumer只读。当前consumer仍明确只准125，本批不能直接apply。先独立复审本批具体SHA，再父批准，唯一接入作者扩受限scope；串行入图必须对最新完整发布基线复核，不以本163快照覆盖。未游戏测试/浏览器/服务/业务/存档/提交。

复现：本目录search.py <source> --seconds <budget>生成有限候选；joint.select按已冻包保护选局部组合；freeze.freeze仅在文件不存在时冻结；finalize.py复核并绘制底稿。只读全部历史产物；原生母版不入运行包。
''')
x.assert_protected();assert all(x.sha(f)==h for f,h in frozen.items());x.write('input-sha-after.json',{f:x.sha(f) for f in x.protected});x.write('SHA256.json',{f.name:{'sha256':x.sha(f),'bytes':f.stat().st_size} for f in sorted(O.iterdir()) if f.is_file() and f.name!='SHA256.json'})
print('REGISTRY',registry['counts'],'SHA',x.sha(O/'registry.json'),flush=True)
