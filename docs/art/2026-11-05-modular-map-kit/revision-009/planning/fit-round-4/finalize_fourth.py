#!/usr/bin/env python3
"""Usage reservations, stage-distinct summary and projected district evidence."""
from pathlib import Path
import ast
O=Path(__file__).resolve().parent
s=(O/'assemble_fourth.py').read_text().split('for idx in targetids:')[0]
exec(compile(s,'read-only-round4-setup','exec'),globals())
batchfile=O/'fourth-expansion-batch.json';batch=read(batchfile);frozen=sha(batchfile);special=read(O/'special-type-progress.json');assert special['processedSources']==100
buildings=batch['buildings'];assigned=set(batch['sourceIndices']);newbodies=[b['footprintPolygonMap'] for b in batch['buildings']];reservations=[]
refs=read(K/'revision-006/references/approved-25-index.json')['sources'];ref11=next(v for v in refs if v['imageNumber']==11);ref3=next(v for v in refs if v['imageNumber']==3)
for r in [ref11,ref3]:assert sha(r['source'])==r['sha256']
# Actual site reservations use ideal catalogue design envelopes only. No claimed image contact/door exists yet.
for aid,intent in [('B12','residential'),('B13','mixed')]:
 item=next(v for v in catalog['items'] if v['id']==aid);w,d,h=item['dimensionsCandidate'];chosen=None
 choices=[x for vals in queue.values() for x in vals if x['sourceIndex']not in assigned and x['sourceIndex']not in previous and x['stratum']['landUseIntent']==intent]
 for x in sorted(choices,key=lambda v:v['score']):
  poly=rect(x['anchorMap'],w+2,d+2);q=audit(poly,[x['sourceIndex']],newbodies)
  if not good(q,True):continue
  if any(pp(poly,r['reservationPolygonMap'])<2 for r in reservations):continue
  # Actual nearby source road/node reference, no assumed door chosen prior to image.
  chosen={'assetId':aid,'state':'reservation-not-assigned-not-ready','sourceIndices':[x['sourceIndex']],'sourcePolygonMap':c['buildings'][x['sourceIndex']],'anchorCandidateMap':x['anchorMap'],'reservationPolygonMap':poly,'catalogueBodyDimensionsCandidate':[w,d,h],'envelopeMeaning':'ideal catalogue design envelope plus1m per side, NOT an actual PNG footprint','doorPixel':None,'doorCalibration':'pending image; future door must have legal courtyard-to-source-shoulder connection; no old door substituted','sourceRoadId':x['approach']['roadId'],'sourceNodeRangeInclusive':[x['approach']['segmentIndex'],x['approach']['segmentIndex']+1],'landUseIntent':intent,'staticSiteReservationClearance':q,'visualDifference':item['visualGap'],'identity':item['identity'],'approved25Reference':ref11 if aid=='B12' else ref3,'referenceObservation':'full source opened; detached low roofs and yards in TR32' if aid=='B12' else 'full source opened; low street shop canopy/door in TR33; not B01 colour/name variant','comparisonPixelBoxApprox':[160,692,233,749] if aid=='B12' else [591,554,692,660],'referenceBoxPrecision':'approximate architecture-context crop, not calibrated source single-sprite ground'};break
 assert chosen,(aid,'no suitable reservation');reservations.append(chosen)
# Plant reservations use explicit legal garden/field context and separation, no reliance on nonexistent native alpha.
for aid in ['T04','T05']:
 item=next(v for v in catalog['items'] if v['id']==aid);w,d,h=item['dimensionsCandidate'];found=None
 for b in batch['buildings']:
  if b['assetId']not in ['B05','B06','B07']:continue
  anchor=b['anchorMap']
  for du,dn in [(0,-12),(-12,0),(12,0),(0,-16),(-16,-8),(16,-8)]:
   pos=add(add(anchor,mul(u,du)),mul(n,dn));poly=rect(pos,w+1,d+1);q=audit(poly,b['clusterOfSource']['sourceIndices'],newbodies)
   if not good(q) or any(pp(poly,r['reservationPolygonMap'])<2 for r in reservations):continue
   if any(pp(poly,p)<.5 for bb in batch['buildings'] for p in bb['visualApproach']['polygonsMap']):continue
   found={'assetId':aid,'state':'reservation-not-assigned-not-ready','sceneId':b['id'],'sourceIndices':b['clusterOfSource']['sourceIndices'],'reservationPolygonMap':poly,'anchorCandidateMap':pos,'catalogueDimensionsCandidate':[w,d,h],'envelopeMeaning':'ideal footprint/canopy reservation, no actual root/alpha/anchor calibration yet','siteUse':'residential courtyard shade tree' if aid=='T04' else 'low planting border beside residential court','visualDifference':item['visualGap'],'identity':item['identity'],'staticSiteReservationClearance':q,'approved25Reference':ref11,'referenceObservation':'full TR32 observed: broad branching yard crowns versus low hedge/ground layers; not tree recolour or shrunk T02','comparisonPixelBoxApprox':[518,407,560,466] if aid=='T04' else [265,832,324,871],'referenceBoxPrecision':'approximate landscape context only'};break
  if found:break
 assert found,(aid,'no plant site');reservations.append(found)
contracts={'schemaVersion':1,'cataloguePath':str(catalogfile),'catalogueSHA256':sha(catalogfile),'status':'visual-type-use-intents-only-not-image-readiness','reservations':reservations,'allFourTypesHaveRealSourceOrSceneIntent':True,'notInFourthBatch':True,'productionStatus':'catalogue planned, no image readiness assumed; do not fill white boxes','geometryVsVisualNeed':'current safe placements do not negate desired one-storey house/shop and broad crown/low-shrub diversity; these are distinct visual roles','otherTop2Requests':[],'additionalProductionRequest':'none proved; existing B03/B04/B07/B08 actual trials saved separately; do not spawn27-direction matrix'}
write('usage-contracts.json',contracts)
initial=read(R3/'fit-summary.json');joint=read(O/'joint-clearance-evidence.json');types=Counter(b['assetId'] for b in batch['buildings']);optionsources={x['sourceIndex'] for vals in queue.values() for x in vals}
summary={'stages':{'priorRound3Initial':{'newSourcesScreened':200,'oldOptionRechecks':8,'remainingUntestedAtThatTime':379,'scope':'historical stage only'},'priorRound3Final':{'newSourcesProcessed':579,'oldOptionRechecks':8,'acceptedFitOptionsUniqueSources':187,'boundedFailureSources':363,'compositeContextOnlySources':37,'remainingNeverProcessed':0},'currentRound4':{'previousUnassignedOptionSources':len(optionsources),'specialTypeSourcesActuallyRetried':100,'specialTypeAssetScaleAttemptTotals':dict(sum((Counter(r['testedAssetScales']) for r in special['rows']),Counter())),'specialTypeApproachAttemptTotals':dict(sum((Counter(r['approachAttempts']) for r in special['rows']),Counter())),'specialTypeRejectionsByRuleAttemptTotals':dict(sum((Counter(r['rejectedByRule']) for r in special['rows']),Counter())),'specialTypePassOptionCounts':dict(Counter(x['assetId'] for x in special['options'])),'assignedSourceCount':len(assigned),'sceneCount':len(batch['buildings']),'moduleCount':len(batch['buildings']),'groundCount':len(batch['groundSurfaces']),'batchVisualTypes':dict(types),'staticAssignedNotRendered':True,'sourceUnique':True}},'frozenPreviousSourceAssignments':len(previous),'newAssignments':len(assigned),'blueTotal':1008,'rawSourceTotal':3524,'cumulativeStaticAssigned':len(previous)+len(assigned),'stillNotAssigned':1008-len(previous)-len(assigned),'frozenCurrentBatchSHA256':frozen,'prior69VsCurrent94':'current protection is frozen visible94 only; priorround3 visible69 remains historical evidence; no in-flight viewer read','actualCurrentRender':{'baselineVisible':94,'baselineGround':260,'thisBatchVisible':0,'userAcceptedThisBatch':False},'specialTypeSourceEvidenceFile':'special-type-progress.json','jointEvidenceFile':'joint-clearance-evidence.json','programmeGate':'B03 denseUrban mixed only; B04/B08 mixed/park; B07 residential/mixed; unknown source>1200sqm programme deferred','sourceMappings':batch['sourceMappings'],'otherNewNativeTop2':[],'usageContractsDoNotMeanAssetsReady':True}
write('joint-fit-summary.json',summary)
# Verify runtime deps / original roads / unique source mapping and protect all frozen files.
for r in batch['roads']:
 source=next(x for x in c['roads'] if x['id']==r['id']);assert r['sourceNodeIds']==source['nodes'] and r['nodes']==[nodes[i] for i in source['nodes']] and r['width']==source['width'] and r['direction']==source['direction']
for b in batch['buildings']:assert b['navigationStopOriginalWorld']==nodes[b['navigationStopNodeId']]
ids=[i for b in batch['buildings'] for i in b['clusterOfSource']['sourceIndices']];assert len(ids)==len(set(ids))
deps=[]
for aid in types:
 a=assets[aid];f=I/'assets'/a['file'];assert f.is_file() and sha(f)==a['sha256'] and max(Image.open(f).size)<=280;deps.append({'id':aid,'path':str(f),'sha256':sha(f),'size':list(Image.open(f).size),'bytes':f.stat().st_size})
write('batch-verification.json',{'frozenSHA256':frozen,'runtimeDependencies':deps,'sourceIdsUnique':True,'sourceRoadsPreserved':True,'guardedBaseline94NotInFlightRenderer':True,'actualBodyAndSurfaceProofFile':'joint-clearance-evidence.json','notPreciseNativeDoorstepCertification':True})
# Geographic overview and selected special-case closeup. Original grey source targets remain visible as unfinished context.
allpts=[p for b in batch['buildings'] for p in b['footprintPolygonMap']];C=center(allpts)
def draw(name,subset,focus,W=1600,H=1200):
 pts=[p for b in subset for p in b['footprintPolygonMap']];proj=lambda p:[(p[0]-focus[0])*P['axisX'][k]+(p[1]-focus[1])*P['axisY'][k] for k in (0,1)];q=[proj(p) for p in pts];lo=[min(p[k] for p in q)-25 for k in (0,1)];hi=[max(p[k] for p in q)+25 for k in (0,1)];scale=min((W-100)/(hi[0]-lo[0]),(H-180)/(hi[1]-lo[1]))
 def xy(p):v=proj(p);return [50+(v[0]-lo[0])*scale,140+(v[1]-lo[1])*scale]
 im=Image.new('RGB',(W,H),'#f5f3ec');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f5f3ec"/>']
 def poly(p,color):
  ps=[xy(v) for v in p];dr.polygon(ps,fill=color,outline='#aaa79f');svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in ps)+f'" fill="{color}" stroke="#aaa79f"/>')
 def label(pos,t):x,y=pos;dr.text((x,y),t,fill='#222222');svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="13">{html.escape(t)}</text>')
 selectedids={b['id'] for b in subset};bb=bbox(pts)
 for i,p,bx in bs:
  if gapbox(bb,bx)<50:poly(p,'#e4e0d8')
 for r in batch['roads']:
  ps=[xy(v) for v in r['nodes']];dr.line(ps,fill='#aaa79f',width=max(1,round(r['width']*scale)));svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in ps)+f'" fill="none" stroke="#aaa79f" stroke-width="{r["width"]*scale}"/>')
 for s in batch['groundSurfaces']:
  if s['owner']in selectedids:poly(s['polygonMap'],'#a5bd93' if s['materialId']=='neutral-grass' else '#ead8ae')
 for b in subset:poly(b['footprintPolygonMap'],'#7f9e7b' if b['assetId']in['B05','B06','B07'] else '#b98f6d');label(xy(b['anchorMap']),str(b['clusterOfSource']['sourceIndices'])+' '+b['assetId'])
 dr.rectangle((0,0,W,115),fill='#f5f3ec');svg.append(f'<rect width="{W}" height="115" fill="#f5f3ec"/>');label([24,22],f'ROUND4 STATIC GEOMETRY / {len(assigned)} SOURCE INDICES / {len(buildings)} DESIGN SCENES - NOT GAME RENDER');label([24,46],'Body contours/doors from existing images; grey raw targets still pending. Different heights/roofs/functions actually evaluated.');label([24,70],'B12/B13/T04/T05 reservations separate; no placeholder renders. Visible94 and all prior batches unchanged.');svg.append('</svg>');(O/(name+'.svg')).write_text('\n'.join(svg));im.save(O/(name+'.png'))
draw('fourth-overview',batch['buildings'],C)
specials=[b for b in batch['buildings'] if b['assetId']in['B03','B04','B07','B08']]
if specials:
 focus=specials[0]['anchorMap'];subset=[b for b in batch['buildings'] if math.dist(b['anchorMap'],focus)<100];draw('fourth-special-neighbourhood',subset,focus)
report=f'''# 第四批：{len(assigned)}源／{len(buildings)}设计场景／{len(buildings)}模块

稳定fourth-expansion-batch.json SHA {frozen}；{len(batch['groundSurfaces'])}实际地面多边形，楼族{dict(types)}。已先交父会话，未渲染/用户验收。冻结visible94/260与前三批全部只读，使用真实地面/原生地脚作保护；r3-overview是取景边界，不误当填满的大障碍。未来作者完成在途街巷后须再次对稳定实际基线复核。

候选来源：上一最终187有选项、363有界失败、37复合审查（579新＋8重评，共587），区别于初阶段剩379。原有167源未选选项作多区联合去重；另对100个旧325/大上下文源实际试B03/B04/B07/B08的原地脚、真实门、0.9/1/1.1及direct/side-L，按asset@scale与路策略计数。特殊族通过选项{dict(Counter(x['assetId'] for x in special['options']))}；programme关再限制B03城区mixed、B04/B08相容mixed/park、B07住宅mixed，不把大未知载体几何能过当可改工厂用途。结果含源集合→场景→模块三类计数，many-to-one只有明确本组原轮廓豁免，非源数灌水。

地面按真实本体与门连接、可合法的源址庭院、不同体量的种植退距逐块组织；不是把整条街重复一套布局。部分不安全庭院/种植面已单独剔除，步行失败不偷偷删路径通过。原始POI/road/node/width/direction、水、红蓝绿边界与既显对象不变；门和导航停靠仅设计接近关联，不声称原楼-POI绑定；无新导航边。特殊门槛/隐后角仍人工误差，B07用11/12真实门阶，旧透明中庭点不用。

usage-contracts.json为B12单层住宅、B13低街铺、T04宽冠自然乔木、T05低灌木分别给真实源址/住宅场景预留，catalogue理想包络不是实际PNG地脚；门像素/alpha/根点尚未生成标定，未入本批。已打开25图11/TR32与03/TR33整图核形态、来源SHA及局部语境框留证，不用本批可放现库否定用户视觉多样需求。低房/低铺不等于缩B05/B01；宽冠/低灌木不等于T02换色或缩树。新增类型Top2为空，当前无另外必要生产证据，非宣称全县视觉已足够。T02无树池、T01树池；森林物种多样性未完成。

只写fit-round-4，未生图/浏览器/服务器/游戏tests/typecheck/回归/业务/存档/提交，不轮询原生或在写renderer。保护SHA终核保持；输出图均为静态几何，非实际地图画面。
'''
(O/'REPORT.md').write_text(report)
assert sha(batchfile)==frozen and all(sha(f)==h for f,h in protected.items())
write('delivery-manifest.json',{'frozenBatchSHA256':frozen,'protectedInputsUnchanged':True,'files':[{'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)} for f in [batchfile,O/'joint-fit-summary.json',O/'usage-contracts.json',O/'REPORT.md',O/'fourth-overview.png']]})
print('FINAL',frozen,len(assigned),types)
