#!/usr/bin/env python3
"""Geometric draft only, not sprite-render evidence."""
import json,math,html,hashlib
from PIL import Image,ImageDraw,ImageFont
from compound_context import load
x=load();O=x.O;p=x.read(O/'scene-compound-pilot.json');v=x.read(O/'static-verification.json');inv=x.read(O/'seven-source-inventory.json');a=x.read(O/'seven-source-attempts.json');joint=x.read(O/'compound-joint-attempts.json');scene=p['scenes'][0]
W,H=1700,1150;im=Image.new('RGB',(W,H),'#f8f7f2');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="#f8f7f2"/>']
fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
def text(pos,s,size=16,color='#222222'):
 try:f=ImageFont.truetype(fontpath,size)
 except OSError:f=ImageFont.load_default()
 dr.text(pos,s,font=f,fill=color);svg.append(f'<text x="{pos[0]}" y="{pos[1]+size}" font-size="{size}" font-family="Arial,sans-serif" fill="{color}">{html.escape(s)}</text>')
def projected(q):return [sum(q[k]*p['projection']['axisX' if k==0 else 'axisY'][j] for k in (0,1)) for j in (0,1)]
def panel(box,world):
 qs=[projected(q) for q in world];bb=x.bbox(qs);fac=min((box[2]-box[0])/(bb[2]-bb[0]),(box[3]-box[1])/(bb[3]-bb[1]));cx=(bb[0]+bb[2])/2;cy=(bb[1]+bb[3])/2
 return lambda q:[(projected(q)[0]-cx)*fac+(box[0]+box[2])/2,(projected(q)[1]-cy)*fac+(box[1]+box[3])/2],fac
# Projected bounds encompass actual7 source extents and frozen market context.
windows=[([35,105,825,830],[[-1555,175],[-1390,175],[-1390,299],[-1555,299]],'Seven unknown sources / frozen market context'),([870,105,1665,830],[[-1456,206],[-1433,206],[-1433,232],[-1456,232]],'Source125: native footlines, doors and connected court')]
colors={'B05':'#db9d61','B01':'#769ac4'}
for box,world,title in windows:
 tf,fac=panel(box,world);b=x.bbox(world)
 dr.rectangle(box,outline='#bcbcb2',width=1);svg.append(f'<rect x="{box[0]}" y="{box[1]}" width="{box[2]-box[0]}" height="{box[3]-box[1]}" fill="none" stroke="#bcbcb2"/>');text((box[0],box[1]-28),title,18)
 # clipping shared by SVG/Pillow via temp canvas to keep large road stretches local
 layer=Image.new('RGB',(W,H),'#f8f7f2');ld=ImageDraw.Draw(layer);tag='clip'+str(box[0]);svg.append(f'<defs><clipPath id="{tag}"><rect x="{box[0]}" y="{box[1]}" width="{box[2]-box[0]}" height="{box[3]-box[1]}"/></clipPath></defs><g clip-path="url(#{tag})">')
 def poly(q,fill,stroke='#555555',width=1):
  pts=[tf(v) for v in q];ld.polygon(pts,fill=fill);ld.line(pts+[pts[0]],fill=stroke,width=width);svg.append('<polygon points="'+' '.join(f'{v[0]:.2f},{v[1]:.2f}' for v in pts)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
 for s in x.oldground:
  if x.bgap(b,x.bbox(s['poly']))<25:poly(s['poly'],'#dadccc','#b8c1ab')
 for r,j,aa,bb,rb in x.allsegments:
  if x.bgap(b,rb)<10:poly(x.strip(aa,bb,r['width']),'#999b9c','#777a7c')
 for idx,q,rb in x.bs:
  if x.bgap(b,rb)<10:poly(q,'#e8e4dd','#bfb0a3')
 for bl in x.oldbody:
  if x.bgap(b,x.bbox(bl['poly']))<10:poly(bl['poly'],'#a7b6ad','#6c8277')
 for s in p['groundSurfaces']:poly(s['polygonMap'],'#93b27a' if s['materialId']=='G02-planting' else '#e3ce9b','#887c59')
 for m in p['buildings']:poly(m['footprintPolygonMap'],colors[m['assetId']],'#3e454b',2)
 # Owned source boundary outline above surfaces, not a second obstacle.
 for idx in scene['sourceIndices']:
  pts=[tf(v) for v in x.c['buildings'][idx]];ld.line(pts+[pts[0]],fill='#b1306a',width=2);svg.append('<polygon points="'+' '.join(f'{v[0]:.2f},{v[1]:.2f}' for v in pts)+'" fill="none" stroke="#b1306a" stroke-width="2" stroke-dasharray="6 4"/>')
 im.paste(layer.crop(box),box[:2]);svg.append('</g>')
 for row in inv:
  q=tf(x.center(row['sourcePolygonMap']))
  if box[0]<q[0]<box[2] and box[1]<q[1]<box[3]:text((q[0]+3,q[1]+3),str(row['sourceIndex']),13,'#8a1d4d')
 for m in p['buildings']:
  e=tf(m['entryMap']);dr.ellipse([e[0]-4,e[1]-4,e[0]+4,e[1]+4],fill='#bb2d2d');svg.append(f'<circle cx="{e[0]:.2f}" cy="{e[1]:.2f}" r="4" fill="#bb2d2d"/>')
  q=tf(m['anchorMap']);text((q[0]-16,q[1]-20),m['assetId']+' @'+str(m['uniformScale']),14,'#182939')
 # Direction basis native u/n; non-rotated.
 q=[box[0]+50,box[3]-65];anchor=x.center(world)
 for vec,name,col in [(x.u,'native u','#bd3540'),(x.n,'native n','#3165a8')]:
  q0=projected(anchor);q1=projected(x.add(anchor,x.mul(vec,1)));vv=[q1[k]-q0[k] for k in (0,1)];le=math.hypot(*vv);end=[q[k]+vv[k]/le*44 for k in (0,1)];dr.line([tuple(q),tuple(end)],fill=col,width=3);svg.append(f'<line x1="{q[0]}" y1="{q[1]}" x2="{end[0]}" y2="{end[1]}" stroke="{col}" stroke-width="3"/>');text((end[0],end[1]),name,12,col)
 text((box[0]+12,box[3]-24),'manual ground controls / hidden rear inferred; not a roof billboard',12)
text((35,18),'COMPOUND PILOT - GEOMETRIC DRAFT ONLY - 1 SOURCE / 1 SCENE / 2 MODULES / 5 GROUNDS',24)
text((35,52),'Frozen visible156 /497 grounds protected. Static candidate, not applied / rendered / user accepted.',17)
text((35,860),'B05 pitched-roof dwelling + B01 flat-roof service court | source125 still originalSemanticStatus: unknown',18)
text((35,893),'Body gap 4.691m | peer door-walk/body gap 4.445m | true door pixels B05(810,1070), B01(973,965)',17)
text((35,926),'Road605760963-0 nodes[2..3], full original road retained. 1.5m finite pedestrian surface; no navigation edge.',17)
text((35,959),'Pink = owned source carrier; tan = connected paved court; green = soil bed; red dots = fixed visible native doors.',17)
text((35,990),'Source body area116.354m2; new bodies44.080m2. Carrier overlap22.659m2 (19.47%): scenic reorganization, not survey.',17)
text((35,1022),'All7 inside blue + green. No zoning expansion. Source590 has bounded access failures, not proved impossible.',17)
text((35,1054),'Live market life layer not included: independent review + latest complete baseline recheck required before any import.',17)
text((35,1087),'No old surface edits requested. Initial own threshold0.6m manual tolerance only; every peer/old road/body remains protected.',15)
svg.append('</svg>');(O/'compound-geometry.svg').write_text('\n'.join(svg));im.save(O/'compound-geometry.png')
# Detailed source summary never interprets multi-rule attempt totals as a unique source count.
rows=[]
for row in inv:
 i=row['sourceIndex'];s=a['rows'][str(i)];rows.append({'sourceIndex':i,'areaSquareMetres':row['areaSquareMetres'],'originalSemanticStatus':'unknown','metadataMissingIsRejectRule':False,'nativeBodyAnchorAttemptCount':sum(s['assetScaleAnchorAttempts'].values()),'doorStrategyAttemptCount':sum(s['approachAttempts'].values()),'singleOptions':s['singleOptionCount'],'sourceOutcome':'selected-compound-one-scene-two-modules' if i==125 else 'single-module-options-not-assigned' if s['singleOptionCount'] else 'bounded-search-no-fit-not-proven-impossible','multiLabelRejectCounts':s['rejectedByRuleAttempts'],'fullAttemptsPath':str(O/f'attempt-source-{i:04d}.json')})
summary={'sevenUniqueSourcesScreened':7,'metadataAutoDeferrals':0,'uniqueSourcesWithSingleOptions':sum(r['singleOptions']>0 for r in rows),'sourceWithNoSingleOptionWithinBudget':sum(r['singleOptions']==0 for r in rows),'singleOptionsTotal':sum(r['singleOptions'] for r in rows),'nativeBodyAnchorAttempts':sum(r['nativeBodyAnchorAttemptCount'] for r in rows),'doorStrategyAttempts':sum(r['doorStrategyAttemptCount'] for r in rows),'selectedUniqueSources':1,'selectedScenes':1,'selectedModules':2,'selectedGroundSurfaces':5,'renderedNewSources':0,'userAcceptedNewSources':0,'rows':rows,'jointAttempts':joint,'twoSourceFallbackAttempted':False,'twoSourceFallbackReason':'single-source125 distinct-module compound passed; no need to claim more owned carriers','rejectCountsAreMultiLabelAttemptsNotUniqueSourceTotals':True,'supportPolicy':'anchor in source and >=half body corners inside carrier, area>=30m2; conservative design policy, not user hard limit or geometric impossibility proof','oldSurfacePermissionRequests':[],'source590Explanation':'407.25m2 area is not access certification; body options encountered door-return/self-footline, roadway crossing and old surface/neighbor guards within bounded direct/side-L search. Body passes do not imply door paths pass. No ground exception requested.'};x.write('seven-source-summary.json',summary)
oldreq=[]
for row in rows:
 w=a['rows'][str(row['sourceIndex'])]['firstWitnessPerRule']
 for key,rec in w.items():
  if 'oldGround' not in key:continue
  qs=[rec['clearance']] if 'clearance'in rec else rec.get('approachClearances',[])
  for q in qs:
   if q['oldGroundGap']>= (1 if key=='oldGroundGap' else .15):continue
   old=next(s for s in x.scene['groundSurfaces'] if s['id']==q['oldSurfaceId']);oldreq.append({'sourceIndex':row['sourceIndex'],'blockedRule':key,'candidateAsset':rec['asset'],'scale':rec['scale'],'surfaceId':old['id'],'field':'polygonMap','surfaceSceneOwner':old.get('sceneId',old.get('owner','not explicitly tagged; preserve frozen record and id')),'materialId':old.get('materialId'),'actualGapMetres':q['oldGroundGap'],'reason':'witness intersects or approaches frozen existing pedestrian/court surface','otherFailures':x.failures(q,key=='oldGroundGap'),'requestStatus':'no permission requested or assumed; rejected alternative retained as evidence'})
x.write('old-surface-blockers.json',oldreq)
planSha=x.sha(O/'scene-compound-pilot.json');report=f'''# 复合场地静态试点

稳定候选：`scene-compound-pilot.json`，SHA256 `{planSha}`。只读visible156规划快照，未apply、未显示、未用户验收。唯一写集compound-pilot，旧156物件/497面/81绑定源保持。原city SHA `{x.sha(x.cf)}`；输入前后SHA逐项相同。

7源全部实际试算，0个因旧metadata缺失自动延期。1298次asset@scale/anchor体量核对、3822次入口直接/侧院策略尝试；125有40个单模块选项、430有2个，其余5源本预算无选项。多规则拒绝数不能相加当源数，不代表穷尽无解。完整逐模块记录见`attempt-source-*.json`；7源的原用途仍unknown，scenicProgramme明确PM美术设计。

交付只选择源125：1源→1scene→B05@0.9与B01@1两个不同屋顶/体量模块、5新面（2门路、1共享院坪、1侧院连接、1种植土床）。430的单模块选项未计入交付，不增加散点。本源116.354㎡，新实体合计44.080㎡；落在原carrier内22.659㎡约19.47%，其余是经独立障碍核查的相邻院落空地。不是保形测绘替换；没有豁免其他源。剩余原carrier不再绘作隐形障碍，已用连贯院坪/土床与两模块组织主要场地；未宣称逐平方米覆盖。

两实体净距4.691m，门路到另一实体4.445m。模块距其他源最小13.949m、原路真实半宽外最小2.241m、旧面最小1.312m、旧体最小15.849m；门路路肩余量0.03m、旧面最小3.817m。接触脚线为真实原生像素的手估，隐后角推断，非精密标定；开门第一0.6m自体阈值容差显式保留，不豁免邻体或原道路。新场景铺地连通，地面不穿其他模块，不改旧面，无旧面编辑申请。`old-surface-blockers.json`仅记录被拒其他方案的具体旧面，不授权修改。

源125位于蓝内且绿内；7源均同属denseUrban。真实路605760963-0完整节点/顺序/width/direction原样保存，接入口取节点数组[2..3]；世界切向-89.571°、屏幕-41.148°，现素材frontage屏幕-28.486°，以有限侧院接近解决，不旋转PNG/不假称同路向。真实门B05[810,1070]、B01[973,965]实看完整原生确认；没有强绑远处POI或新增经营/导航边。25图03/TR33-v1已实看，仅借坡顶/平顶低层、服务院落与市场相邻的身份差异，不借其道路。

590约407.25㎡仍未过本预算：实际拒绝含自体门后退冲突、路径穿源半宽、邻源/旧面等；面积大不等于入口可达。586仅13.329㎡，按显式保守carrier政策不硬塞楼；面积/半角支持阈值属于本轮设计筛选，不冒称用户硬限。未跑两源fallback，因125已成立，未碰源1/377。

`verify_static.py`实际执行{v['passedRuleCount']}项通过，包含场景所有权/跨场景源防重、旧单数数组兼容解析、真门反投影、scale只施一次/nodeScale1、完整原路、所有实体/门路/地面净空和局部窗口以外全局障碍bbox下界证明。源数1、scene数1、模块数2分别核对；新增rendered/用户验收均0。静态通过不代表共享导入器已支持同源多模块：先独立复审，再授权适配scene所有权；接入前对市场0587生活层等最新**完成**基线重查，不能用visible156覆盖主图。

复现（不运行游戏/共享导入）：依次`python3 plan_compound.py`、`python3 assemble_pilot.py`、`python3 verify_static.py`、`python3 draw_and_report.py`。两张几何图是底稿，不是运行画面。仅复用B01/B05运行图，长边280、共享纹理，无新素材。
'''
(O/'REPORT.md').write_text(report)
manifest={f.name:{'sha256':x.sha(f),'bytes':f.stat().st_size} for f in sorted(O.iterdir()) if f.is_file() and f.name!='SHA256.json'};x.write('SHA256.json',manifest)
print(json.dumps({'planSHA256':planSha,'pngSize':[W,H],'pngBytes':(O/'compound-geometry.png').stat().st_size,'reportPath':str(O/'REPORT.md')},ensure_ascii=False))
