#!/usr/bin/env python3
"""Re-read fifth final polygons, source formats, road topology and neighbourhood figures."""
from pathlib import Path
ctx=Path(__file__).with_name('plan_fifth.py').read_text().split('for idx in sorted(localids')[0]
ctx=ctx.replace("# refuse frozen v2 overwrite\nif (Path(__file__).resolve().parent/'fifth-expansion-batch-v2.json').exists():\n raise SystemExit('Frozen v2 exists; do not rebuild; consume import-contract.json.')\n",'')
exec(compile(ctx,'read-only-snapshot-context','exec'),globals())
f=O/'fifth-expansion-batch-v2.json';batch=read(f);frozen=sha(f);newbody=[b['footprintPolygonMap'] for b in batch['buildings']];proof=[];binding=read(O/'baseline-source-bindings.json');assert binding['uniqueSourceCount']==69
for b in batch['buildings']:
 idx=b['clusterOfSource']['sourceIndices'][0];assert idx not in bound|reserved
 assert b['visualReplacementOf']['sourcePolygonsMap'][0]==c['buildings'][idx]
 assert b['navigationStopOriginalWorld']==nodes[b['navigationStopNodeId']]
 assert b['worldSizeUnits']==[v*b['uniformScale'] for v in assets[b['assetId']]['worldSizeUnits']] and b['nodeScale']==1
 actual=footprint(b['assetId'],b['anchorMap'],b['uniformScale']);assert all(math.dist(a,d)<1e-9 for a,d in zip(actual,b['footprintPolygonMap']))
 assert math.dist(pixelmap(b['entryPixel'],b['anchorMap'],cal[b['assetId']],b['uniformScale']),b['entryMap'])<1e-9
 q=audit(actual,[idx],[v['footprintPolygonMap'] for v in batch['buildings'] if v['id']!=b['id']]);assert good(q,True);proof.append({'id':b['id'],'kind':'actual-native-body','clearance':q})
 for w in b['visualApproach']['polygonsMap']:
  q=audit(w,[idx],[v['footprintPolygonMap'] for v in batch['buildings'] if v['id']!=b['id']]);assert good(q)
  proof.append({'id':b['id'],'kind':'door-shoulder-walk','clearance':q})
for s in batch['groundSurfaces']:
 b=next(b for b in batch['buildings'] if b['id']==s['owner']);q=audit(s['polygonMap'],b['clusterOfSource']['sourceIndices'],[v['footprintPolygonMap'] for v in batch['buildings'] if v['id']!=b['id']]);assert good(q)
 if b['assetId']=='B07' and 'partial-inner-court'in s['id']:
  assert all(inside(v,b['courtyardVoidPolygonMap']) for v in s['polygonMap']) and pp(s['polygonMap'],b['footprintPolygonMap'])>.15
 proof.append({'id':s['id'],'kind':'exported-ground','clearance':q})
for r in batch['roads']:
 source=next(v for v in c['roads'] if v['id']==r['id']);assert r['sourceNodeIds']==source['nodes'] and r['nodes']==[nodes[nid] for nid in source['nodes']]
 for k in ['width','direction','kind']:assert r[k]==source[k]
# Directed blue-inner topology from each added local lot to its existing focus source-road node.
from collections import deque
adj={}
for r in c['roads']:
 for a,b in zip(r['nodes'],r['nodes'][1:]):
  if not inbounds(nodes[a],'city') or not inbounds(nodes[b],'city'):continue
  if r['direction']>=0:adj.setdefault(a,[]).append((b,r['id']))
  if r['direction']<=0:adj.setdefault(b,[]).append((a,r['id']))
def bfs(a,b):
 todo=deque([a]);prev={a:None}
 while todo:
  x=todo.popleft()
  if x==b:break
  for y,rid in adj.get(x,[]):
   if y not in prev:prev[y]=(x,rid);todo.append(y)
 if b not in prev:return None
 seq=[b];rs=[]
 while seq[-1]!=a:x,rid=prev[seq[-1]];seq.append(x);rs.append(rid)
 return {'nodeIds':seq[::-1],'roadIdsPerEdge':rs[::-1]}
topology=[]
for b in batch['buildings']:
 ap=b['visualApproach'];r=next(r for r in c['roads'] if r['id']==ap['roadId']);start=r['nodes'][ap['segmentIndex']];focus=regions[b['regionId']];nearest=min([(ps(focus,a,d),rr,j,a,d) for rr,j,a,d,bb in segments],key=lambda x:x[0]);focusnode=nearest[1]['nodes'][nearest[2]];forward=bfs(start,focusnode);back=bfs(focusnode,start);assert forward and back
 topology.append({'persistentId':b['id'],'localRegionId':b['regionId'],'sourceStartNodeId':start,'existingFocusNodeId':focusnode,'forward':forward,'return':back,'noNewNavEdges':True})
write('fifth-static-verification.json',{'stableBatchSHA256':frozen,'nativeSizeFootprintDoorResolvedOnce':True,'sourceIdsDisjointFrom69BindingsAndReserved':True,'bodyWalkGroundProof':proof,'directedBlueInnerLocalRoadTopology':topology,'allFullStoredRoadsOriginal':True,'noLiveViewerRead':True,'doorstepLevelsRemainManualUncertainty':True})
# Exact compatible binding snapshot includes singular old4, no inferred duplicate counts.
bytype=Counter(b['assetId'] for b in batch['buildings']);pictures=[]
for region in regions:
 subset=[b for b in batch['buildings'] if b['regionId']==region];focus=regions[region]
 if not subset:continue
 pts=[p for b in subset for p in b['footprintPolygonMap']+b['visualApproach']['centrelineMap']]+[focus];pr=lambda p:[(p[0]-focus[0])*P['axisX'][k]+(p[1]-focus[1])*P['axisY'][k] for k in (0,1)];ps=[pr(p) for p in pts];lo=[min(p[k] for p in ps)-18 for k in (0,1)];hi=[max(p[k] for p in ps)+18 for k in (0,1)];W,H=1500,1100;scale=min(1350/(hi[0]-lo[0]),900/(hi[1]-lo[1]));xy=lambda p:[60+(pr(p)[0]-lo[0])*scale,140+(pr(p)[1]-lo[1])*scale]
 im=Image.new('RGB',(W,H),'#f5f3ec');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f5f3ec"/>']
 def poly(p,color,stroke='#aaa79f'):
  q=[xy(v) for v in p];dr.polygon(q,fill=color,outline=stroke);svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in q)+f'" fill="{color}" stroke="{stroke}"/>')
 def label(p,t):x,y=p;dr.text((x,y),t,fill='#222222');svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="13">{html.escape(t)}</text>')
 bounds=bbox(pts)
 for idx,p,bb in bs:
  if boxgap(bounds,bb)<25:poly(p,'#e5e1d8')
 for rr,j,a,d,bb in segments:
  if boxgap(bounds,bb)<25:
   q=[xy(a),xy(d)];dr.line(q,fill='#aaa79f',width=max(1,round(rr['width']*scale)));svg.append(f'<line x1="{q[0][0]}" y1="{q[0][1]}" x2="{q[1][0]}" y2="{q[1][1]}" stroke="#aaa79f" stroke-width="{rr["width"]*scale}"/>')
 for s in scene['groundSurfaces']:
  if boxgap(bounds,bbox(s['polygonMap']))<10:poly(s['polygonMap'],'#d7d0bc','#b4a996')
 for bl in oldbody:
  if boxgap(bounds,bbox(bl['footprintPolygonMap']))<10:poly(bl['footprintPolygonMap'],'#abb8c8','#718094');label(xy(centre(bl['footprintPolygonMap'])),bl['persistentId'])
 ids={b['id'] for b in subset}
 for s in batch['groundSurfaces']:
  if s['owner']in ids:poly(s['polygonMap'],'#a6bc91' if s['materialId']=='neutral-grass' else '#ead59c')
 for b in subset:poly(b['footprintPolygonMap'],'#799b72' if b['assetId']in ['B05','B06','B07'] else '#b88c65');label(xy(b['anchorMap']),str(b['clusterOfSource']['sourceIndices'])+' '+b['assetId']);x,y=xy(b['entryMap']);dr.ellipse((x-3,y-3,x+3,y+3),fill='#b43737')
 dr.rectangle((0,0,W,115),fill='#f5f3ec');svg.append(f'<rect width="{W}" height="115" fill="#f5f3ec"/>');label([24,22],f'FIFTH LOCAL INFILL / {region} / STATIC GEOMETRY - NOT GAME SCREENSHOT');label([24,46],'Blue-grey = frozen existing143 bodies / beige = old462 ground; green-brown = new local lots; grey = untouched raw sources.');label([24,70],'Only two fixed140m focus regions. Complete safe court/apron required; native doors/PPU kept, no double scaling.');label([24,94],'B07 partial court is inside reviewed U void; no generic opaque slab filling whole void. Final runtime baseline recheck required.');svg.append('</svg>');stem='fifth-'+region;(O/(stem+'.svg')).write_text('\n'.join(svg));im.save(O/(stem+'.png'));pictures.append(stem+'.png')
summary=read(O/'joint-fit-summary.json');summary['staticVerificationFile']='fifth-static-verification.json';summary['boundFormatAudit']={'legacySingular':sum(v['readFormat']=='singular' for v in binding_evidence),'currentArrays':sum(v['readFormat']=='array' for v in binding_evidence),'uniqueSourceCount':69};summary['stableBatch']={'path':str(f),'sha256':frozen};summary['Top2NativeNeeds']={'requests':[],'reason':'most local rejections are visible143 ground/body, neighbour source or entry clearance; native direction/type necessity not proven; not a claim existing8types satisfy all future art diversity'};write('joint-fit-summary.json',summary)
# Body/ground/stop evidence balanced; no source counted by a module twice.
assert len(batch['sourceIndices'])==len(set(batch['sourceIndices']))==10 and len(batch['buildings'])==10 and len(batch['groundSurfaces'])==31
report=f'''# 第五批：两片邻区补位，10源／10场景／10模块／31面

稳定文件fifth-expansion-batch-v2.json，SHA {frozen}。首版fifth-expansion-batch.json保留不改，仅U院庭院地面语境做独立v2修订。4源在0587市场140m邻区，6源在1735～1739住宅140m邻区；未借远处源凑20。楼型{dict(bytype)}，与邻近已有市场/U院/住宅共同形成不同高低与屋顶/用途关系，不声称所有源都改住宅。

先复用上一完成可行池，仅{summary['initialExistingOptionPool']['uniqueSourcesInsideTwoRegions']}个未绑定/未预留源在两邻区；0176 U院附近没有旧可行未分配选项，本轮不在那里造孤立演示。额外45源局部替代试算，asset@scale、direct/side-L拒绝根因保存，未重扫全县187池历史。根据当前143对象/462面真正地脚与所有其他原楼障碍，联合剔除不安全本体、入口或只剩细长走道而无合法院落/前场的候选。面积比不作硬性拒绝；没有豁免未画出的无关源楼。

地面按实际空间取舍：完整有限维护院落、源址庭院、门前4×3.6m候选apron、后园各自逐面通过才收；失败面单独拒绝，旧场地原样保护。B07首版通用source-court/apron不能明确区分U实体/空腔，因此v2移除这两面，改为真实void内12㎡局部中庭面，与真门11/台阶12的步行线相接，距实体>0.15m，四角inside void；余void不铺满。不是用草地压住未知阴影当精密认证。当前10片不是周边整区美术完成，既有场地进一步连接/装饰建议仅列未实施。

源格式实际兼容：最早4条sourceIndex/sourcePolygon及后来数组sourceIndices/sourcePolygonsMap并读，69唯一绑定逐源去重；新10与69及1731/1383等比较预留无重叠。原city、完整道路节点/顺序/width/direction、原POI/node/名称/业务/导航全部保持；每新源的真实门像素与原停靠node分开，设计关联不冒充源schema原经营绑定。每片到既有焦点沿蓝内原有有向道路去/回节点链已另存；未造捷径或新导航边。

worldSizeUnits、footprint、entryMap都已是canonical×单一正比例后的最终值，uniformScale只记录来源、nodeScale=1，不二次乘。B01/T01认可基准及旧实例不改。B07门11[704,609]、阶12[713,626]及U实体/void保持，旧透明中庭点不作门；隐脚线、原生门槛首0.6m人工误差与实际高差仍需接入实看，不伪称测绘。

基线snapshot scene SHA 9f7adf3e269fc320830b3b5b422797faed5014b453a99d199efd0c76d546bf8f，143静态/462面/69绑定；旧四批和所有快照SHA终核保持。B09/B10/B11/T04 hold不放，B12/B13 clean/T05即使已产也不擅当全量准入，不等待；比较预留仍保护。Top2额外原生需求为空：本轮剩余障碍主要是原楼/旧地面/路径净空，尚不能证明某新朝向即可解决；不因此否认美术类型多样性需求。

实际运行脚本plan_fifth.py→assemble_fifth.py→refine_b07_court.py→finalize_fifth.py，只写fit-round-5，未生图/浏览器/游戏tests/typecheck/回归/FPS/服务器/业务/存档/提交。投影图已标静态几何，非游戏截图；新数据assigned未rendered/用户验收。接入作者须再对包含在途街巷/原生比较的最新稳定实际基线核冲突，不能用本快照重置主图。
'''
(O/'REPORT.md').write_text(report)
# Freeze batch guards on accidental rebuild, while read-only final verification remains callable.
for name in ['plan_fifth.py','assemble_fifth.py','refine_b07_court.py']:
 script=O/name;txt=script.read_text();needle='from pathlib import Path\n'
 if 'refuse frozen v2' not in txt:
  txt=txt.replace(needle,needle+"# refuse frozen v2 overwrite\nif (Path(__file__).resolve().parent/'fifth-expansion-batch-v2.json').exists():\n raise SystemExit('Frozen v2 exists; do not rebuild; consume import-contract.json.')\n",1);script.write_text(txt)
assert sha(f)==frozen and all(sha(f)==h for f,h in protected.items())
write('delivery-manifest.json',{'stableBatchSHA256':frozen,'oldFilesAllSHAUnchanged':True,'files':[{'path':str(x),'sha256':sha(x),'bytes':x.stat().st_size} for x in [f,O/'import-contract.json',O/'joint-fit-summary.json',O/'fifth-static-verification.json',O/'REPORT.md']+[O/p for p in pictures]]})
print('VERIFIED',frozen,len(proof),len(topology))
