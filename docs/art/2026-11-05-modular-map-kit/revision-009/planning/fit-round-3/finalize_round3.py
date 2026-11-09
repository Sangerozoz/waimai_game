#!/usr/bin/env python3
"""Final strategy counts, exact provenance checks and geometric overview."""
import json,math,hashlib,html,itertools
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(f,d):(O/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
bf=O/'third-expansion-batch.json';batch=read(bf);frozen='654ccb00f1f75af0f487c9d2d3f7e8f88b06258ca1f73542dcc950978c1a6a12';assert sha(bf)==frozen
summary=read(O/'fit-summary.json');audit=read(O/'fit-progress-strategy-audit.json');assert audit['processedUniqueSources']==587 and len({x['sourceIndex'] for x in audit['testedSources']})==587
rows=audit['testedSources'];assigned=set(batch['sourceIndices']);new=set(read(O/'untested-strata.json')['rows'][i]['sourceIndex'] for i in range(579));assert len(new)==579
first=read(O/'fit-progress.json')['testedSources'];scannedInitial={r['sourceIndex'] for r in first}-set(summary['recheckedOldFitOptionSourceIds']);remainder=read(O/'fit-progress-remainder.json');assert remainder['processedUniqueSources']==379
remainingRows=read(O/'fit-progress-remainder.json')['testedSources'];allrows={r['sourceIndex']:r for r in rows};assert new<=set(allrows)
summary.update(newUniqueSourcesScannedThisRound=579,priorFitOptionRechecks=8,totalUniqueSourcesInStrategyAudit=587,remainingNeverProcessedSourceCount=0,oldFixedScale325Retested=False,remainingWithoutCompletedBodyApproachTrial=sum(r['stage']=='cluster-intent-review' for r in rows),bodyApproachStrategyCompletedSourceCount=sum(r['stage']=='native-footprint-and-approach' for r in rows),strategyAuditOutcomeCounts=dict(Counter(r['result'] for r in rows)),strategyAttemptTotals=dict(sum((Counter(r.get('routeTemplateAttemptCounts',{})) for r in rows),Counter())),assetScaleAttemptTotals=dict(sum((Counter(r.get('attemptedAssetScales',{})) for r in rows),Counter())),rejectedByRuleAttemptTotals=dict(sum((Counter(r['rejectedByRule']) for r in rows),Counter())),uniqueSourceRejectionRulesTriggered=dict(sum((Counter(set(r['rejectedByRule'])) for r in rows),Counter())),initial200ThenRemainder379=True,bodyOrDoorPassDoesNotMeanJointlyAssigned=True,newBatchFrozenSHA256=frozen)
# No remaining source is mislabelled 'no fit' if large/composite actual trial was deferred by semantics.
summary['sourceStageLedger']=[{'sourceIndex':r['sourceIndex'],'origin':'newly-processed' if r['sourceIndex']in new else 'prior-fit-option-recheck','stage':r['stage'],'outcome':r['result'],'assignedToFrozen20':r['sourceIndex']in assigned,'attemptedAssetScales':r.get('attemptedAssetScales',{}),'routeTemplateAttemptCounts':r.get('routeTemplateAttemptCounts',{}),'rejectedByRule':r['rejectedByRule']} for r in rows]
summary['old325Scope']='not retried; old fixed-scale bounded results remain distinct, not proof resource missing';summary['sourceTotals']={'allSourceBuildings':3524,'blueSourceBuildings':1008,'previousAssigned':9,'currentAssigned':20,'cumulativeStaticAssigned':29,'stillUnassigned':979,'renderedFromThisBatch':0,'sourceStageCaveat':'field counts describe processing and static fit, not source completion/rendering; large context-only cases have not completed module search'}
summary['compositeEvidenceFile']='composite-followup-options.json';write('fit-summary.json',summary)
# Preserve future candidate options as an explicit non-admitted queue, not another claimed batch.
queue={}
for candidate in audit['fitOptions']:
 if candidate['sourceIndex'] in assigned:continue
 queue.setdefault(str(candidate['sourceIndex']),[]).append(candidate)
write('next-source-fit-queue.json',{'status':'unadmitted-options-require-joint-check-against-frozen20','sourceCount':len(queue),'sourceOptions':queue,'parentFrozen20SHA256':frozen,'notRendered':True})
# Verify full stored source roads, stop node semantics, runtime file budget and current protection hashes.
c=read(batch['sources']['city']['cityPath']);nodes={p['id']:[p['x'],p['y']] for p in c['nodes']};roadby={r['id']:r for r in c['roads']}
for r in batch['roads']:
 src=roadby[r['id']];assert r['sourceNodeIds']==src['nodes'] and r['nodes']==[nodes[i] for i in src['nodes']]
 for k in ['width','direction','kind']:assert r[k]==src[k]
for b in batch['buildings']:
 assert b['navigationStopOriginalWorld']==nodes[b['navigationStopNodeId']]
 assert all(c['buildings'][i]==q for i,q in zip(b['visualReplacementOf']['sourceIndices'],b['visualReplacementOf']['sourcePolygonsMap']))
keys=[i for b in batch['buildings'] for i in b['clusterOfSource']['sourceIndices']];assert len(set(keys))==len(keys)==20
for f,h in read(O/'protected-inputs.json').items():assert sha(f)==h
assert batch['protection']['visibleStaticCount']==69 and batch['protection']['visibleGroundCount']==135
assert sha(batch['protection']['visible69ScenePath'])==batch['protection']['visible69SceneSHA256']
assert sha(batch['protection']['pendingSecondBatchPath'])==batch['protection']['pendingSecondSHA256']
K=O.parents[2];I=K/'revision-006/integration';lib=read(I/'asset-library.json');deps=[]
for aid in sorted({b['assetId'] for b in batch['buildings']}):
 a=next(v for v in lib['assets'] if v['id']==aid);f=I/'assets'/a['file'];assert sha(f)==a['sha256'] and max(Image.open(f).size)<=280;deps.append({'assetId':aid,'path':str(f),'sha256':sha(f),'dimensions':list(Image.open(f).size),'bytes':f.stat().st_size,'scalePerInstance':[b['uniformScale'] for b in batch['buildings'] if b['assetId']==aid],'sharedImageFrame':True})
write('batch-verification.json',{'frozenSHA256':frozen,'sourceIndicesUnique':True,'fullOriginalRoadsReadback':len(batch['roads']),'staticGeometryEvidenceFile':'topology-clearance-evidence.json','allOldInputsProtectedSHAUnchanged':True,'runtimeDependencies':deps,'bodyAndWalkDoorstepScope':'first0.6m native step/rim manual uncertainty; no engine/level certification'})
# Geometry overview with genuine geographic scale, no fake claim intervening source targets rendered.
P=batch['projection'];pts=[p for b in batch['buildings'] for p in b['footprintPolygonMap']];C=[sum(p[k] for p in pts)/len(pts) for k in (0,1)]
def pr(p):return [(p[0]-C[0])*P['axisX'][k]+(p[1]-C[1])*P['axisY'][k] for k in (0,1)]
qq=[pr(v) for v in pts];lo=[min(p[k] for p in qq)-30 for k in (0,1)];hi=[max(p[k] for p in qq)+30 for k in (0,1)];W,H=1600,1250;scale=min(1450/(hi[0]-lo[0]),1050/(hi[1]-lo[1]))
def xy(p):v=pr(p);return [70+(v[0]-lo[0])*scale,140+(v[1]-lo[1])*scale]
im=Image.new('RGB',(W,H),'#f5f3ec');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f5f3ec"/>']
def poly(ps,color):
 q=[xy(v) for v in ps];dr.polygon(q,fill=color,outline='#aaa79f');svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in q)+f'" fill="{color}" stroke="#aaa79f"/>')
def text(p,t):x,y=p;dr.text((x,y),t,fill='#222222');svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="13">{html.escape(t)}</text>')
bounds=[min(p[k] for p in pts)-50 for k in (0,1)]+[max(p[k] for p in pts)+50 for k in (0,1)]
for idx,p in enumerate(c['buildings']):
 if any(bounds[0]<q[0]<bounds[2] and bounds[1]<q[1]<bounds[3] for q in p):poly(p,'#e4e0d7')
for r in batch['roads']:
 ps=[xy(v) for v in r['nodes']];dr.line(ps,fill='#aaa79f',width=max(1,round(r['width']*scale)));svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in ps)+f'" fill="none" stroke="#aaa79f" stroke-width="{r["width"]*scale}"/>')
for s in batch['groundSurfaces']:poly(s['polygonMap'],'#a9c296' if s['materialId']=='neutral-grass' else '#ead8b0')
for b in batch['buildings']:poly(b['footprintPolygonMap'],'#829e78' if b['assetId']in['B05','B06'] else '#ba936d');text(xy(b['anchorMap']),str(b['clusterOfSource']['sourceIndices'][0])+' '+b['assetId'])
dr.rectangle((0,0,W,115),fill='#f5f3ec');svg.append(f'<rect width="{W}" height="115" fill="#f5f3ec"/>');text([25,20],'ROUND3 - FROZEN20 SOURCE LOTS / 20 MODULES / 96 GROUND POLYGONS - STATIC GEOMETRY, NOT GAME RENDER');text([25,44],'Existing blue-inner directed roads connect all lots; intervening raw sources remain unassigned grey targets.');text([25,68],'Ground use: source-carrier yard / native door approach / individual planted edge. Positive uniform scales only.');text([25,92],'Visible69 + pending5 protected; source indices unique; native doorstep levels and camera occlusion remain unverified.');svg.append('</svg>');(O/'third-batch-projected.svg').write_text('\n'.join(svg));im.save(O/'third-batch-projected.png')
combo=read(O/'composite-followup-options.json');outcomes=summary['strategyAuditOutcomeCounts']
report=f'''# 第三轮：20源稳定批＋剩余源有界扫描

稳定third-expansion-batch.json SHA {frozen}，已先发父会话。20唯一源、20视觉模块、96多边形地面，B01/B02/B05/B06；正等比0.9/1/1.1，旧B01/T01及全部既有对象不改。来源3524/蓝内1008分母不变；累计静态assigned29（前4＋第二5＋本轮20），其余979仍未分配，assigned不是rendered。场景是同一180m源址邻接连通片的部分住宅/商住地块，不把间隔灰色源楼说已画；原有蓝内去回有向道路节点链逐段保留，45完整原路引用，无新导航边/捷径。

每plot有真实原生足迹、固定门、1.5m门路肩连接、可安全落地的原载体庭院与各自种植边；自身源轮廓仅对明确替换索引豁免，其他源楼/车道半宽/水/原69区域/待显示第二5保护均不豁免。多边形净距证据与源映射单独落盘，场景不是一整条复制模板。门到停靠node只作设计接近关联，原node/名称/路线保持；本楼首0.6m门槛地脚误差需运行实看，未称精密台阶或可通行认证。

扫描：先新200＋重评旧8得69源有适配选项，冻结20后继续剩379；另完整策略复算覆盖全部579新源＋8重评源共587。真实结果{outcomes}。大于1000m²源先做组合语义审查，不记作已完成楼体/入口穷尽搜索，实际仍未完成该类几何试算的源数{summary['remainingWithoutCompletedBodyApproachTrial']}；旧325固定尺度有界结果没有被伪装成新一轮失败。各asset@scale、direct/side-L策略实际调用计数及每拒绝根因有attempt/source双口径；先过0.9不等于1.0失败。

组合：按真实认可residential/mixed外环（含源楼孔的设计承载外环）筛非业务邻源，3组实际many-to-one试算。654+2387两源一场景在冻结20保护下复查通过，但在另一地块，不混进本批主片、未多计源完成；详composite-followup-options。另对源1/377两个大型同用途包络实做一源3模块/院落门路试算，均在本轮几何/入口预算下失败，未改厂房语境成住宅以通过。无外环或原功能证据的45大载体语义项逐条deferred，不硬造原业务关联。

当前20源不需要新素材，Top2必要原生需求为空；现有门/体量/路向失败只作有界证据，不能自动推出新朝向生产。B09/B10/B11 hold，P09不铺县；T02是无树池自然树、T01才有树池，自然复用允许但未宣称森林物种多样完成。

稳定保护visible69/scene-layout.json、neighborhood.tmj与第二批5源20面SHA均保持；旧009/二轮文件不写，不读在写viewer、不等待接入。执行fit_round3.py、assemble_round3.py先冻结，scan_remainder.py分批保存，audit_strategies.py补每策略计数，cluster_followup.py补真实组合，finalize_round3.py核对与图表。只写fit-round-3；未生图/浏览器/游戏tests/typecheck/回归/业务/存档/提交。投影图是几何证据，不替代实际地图/用户验收。
'''
(O/'REPORT.md').write_text(report)
assert sha(bf)==frozen
write('delivery-manifest.json',{'frozenBatchSHA256':frozen,'protectedInputsUnchanged':True,'files':[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in [bf,O/'fit-summary.json',O/'source-combination-map.json',O/'composite-followup-options.json',O/'topology-clearance-evidence.json',O/'REPORT.md',O/'third-batch-projected.png']]})
print('FINAL',frozen,outcomes,'context-only',summary['remainingWithoutCompletedBodyApproachTrial'])
