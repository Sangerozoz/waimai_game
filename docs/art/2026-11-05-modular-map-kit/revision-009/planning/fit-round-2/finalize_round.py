#!/usr/bin/env python3
"""Exported geometry verification and conditional measured-direction contract; no engine calls."""
# Reuse read-only setup and pure functions, stopping before bounded placement loop.
from pathlib import Path
context=Path(__file__).with_name('fit_round.py').read_text().split('rows=[];options=[]')[0]
exec(compile(context,'fit_round.py-setup','exec'),globals())
batchfile=O/'second-expansion-batch.json';batch=read(batchfile);frozen=sha(batchfile);summary=read(O/'fit-summary.json');proof=[]
for b in batch['buildings']:
 idx=b['visualReplacementOf']['sourceIndex'];objects=[('body',b['footprintPolygonMap'])]+[(f'walk-{j}',p) for j,p in enumerate(b['visualApproach']['polygonsMap'])]+[(s['id'],s['polygonMap']) for s in batch['groundSurfaces'] if s['id'].startswith(b['id']+'-garden-')]
 checks=[]
 for label,poly in objects:
  pb=bbox(poly);others=[(i,p) for i,p,bb in bs if i!=idx and gapbox(pb,bb)<80];rr=[(r,j,a,d) for r,j,a,d,bb in segments if gapbox(pb,bb)<80]
  near= min([pp(poly,p) for i,p in others]+[9999]);road=min([pl(poly,a,d)-r['width']/2 for r,j,a,d in rr]+[9999]);watergap=min([pp(poly,p) for p in water if gapbox(pb,bbox(p))<80]+[pl(poly,a,d)-3 for a,d in wl if gapbox(pb,bbox([a,d]))<80]+[9999]);prot=min(pp(poly,p) for p in protected_polys)
  assert near>=.099 and road>=-.001 and watergap>=5 and prot>=3 and all(inbounds(v,'city') for v in poly),(b['id'],label,near,road,watergap,prot)
  for other in batch['buildings']:
   if other['id']!=b['id']:assert pp(poly,other['footprintPolygonMap'])>=.099,(b['id'],label,other['id'])
  checks.append({'polygon':label,'otherSourceMetres':near,'roadEdgeMetres':road,'waterSafetyMetres':watergap,'old57AndFrozenSeedProtectionMetres':prot})
 assert b['visualReplacementOf']['sourcePolygonMap']==c['buildings'][idx]
 assert b['navigationStopOriginalWorld']==nodes[b['navigationStopNodeId']]
 proof.append({'persistentId':b['id'],'sourceIndex':idx,'checks':checks,'sourceNavigationStopUnchanged':True})
write('exported-polygon-verification.json',{'secondBatchSHA256':frozen,'sourcesUnique':len({b['visualReplacementOf']['sourceIndex'] for b in batch['buildings']}),'allPolygonsStaticPass':True,'doorThresholdUncertaintyNotCertified':True,'checks':proof})
# Explicitly review three real large carriers as clusters; no inferred land-use context is upgraded to historical building proof.
large=[m for m in strat if m['areaSquareMetres']>500][:3];cluster_review=[]
for meta in large:
 idx=meta['sourceIndex'];C=meta['centerMap'];modules=[]
 for j,offset in enumerate([-9,0,9]):
  anchor=add(C,mul(u,offset));poly=footprint('B05',anchor,.9);pb=bbox(poly)
  others=[p for i,p,bb in bs if i!=idx and gapbox(pb,bb)<60]
  modules.append({'hypothesisModuleId':f'cluster-study-{idx}-{j}','sourceIndex':idx,'assetId':'B05','uniformScale':.9,'anchorMap':anchor,'footprintPolygonMap':poly,'otherSourceGapMetres':min([pp(poly,p) for p in others]+[9999]),'allVerticesBlue':all(inbounds(v,'city') for v in poly),'notAssigned':True})
 cluster_review.append({'source':meta,'clusterOfSource':{'sourceIndices':[idx],'hypotheticalVisualModuleCount':3,'uniqueSourceCount':1},'geometryHypothesisOnly':modules,'remainingSpaceHypothesis':'courtyard/paths only if original functional intent verified','decision':'deferred-function-evidence-before-cluster-placement','reason':'nearby decorative parcel landUse does not establish whether large raw carrier is a factory/campus/residential compound; do not silently replace with small houses','geometricScreeningComplete':False})
write('large-carrier-cluster-review.json',{'sourceCount':len(cluster_review),'rows':cluster_review,'notAddedToBatch':True})
assigned_set={b['visualReplacementOf']['sourceIndex'] for b in batch['buildings']}
summary['postRoundUniqueSourceTotals']={'blueTotal':1008,'previousAssigned':4,'newAssigned':len(assigned_set),'stillDeferred':1004-len(assigned_set),'deferredStages':{'oldFixedScaleOnly':325,'thisRoundProcessedNotAssigned':100-len(assigned_set),'stillNoGeometricScreening':579},'fitOptionSourcesNotAssigned':13-len(assigned_set)}
assert sum(summary['postRoundUniqueSourceTotals']['deferredStages'].values())==summary['postRoundUniqueSourceTotals']['stillDeferred']
for row in summary['sourceRows']:row['assignedToSecondBatch']=row['sourceIndex'] in assigned_set
summary['largeCarrierContextOnlyReviews']=len(cluster_review)
summary['stillNoGeometricScreeningIncludesContextOnlyReviews']=True
write('fit-summary.json',summary)
# Two measurable source sites alongside a common40-degree road. Footprint-only bounded test, not 'all approaches impossible'.
examples=read(OLD/'resource-gaps.json')['items'][1]['sourceRoadExamples'];cases=[];tested=set()
for ex in examples:
 r=next(r for r in c['roads'] if r['id']==ex['roadId']);j=ex['nodeRangeInclusive'][0];a,d=[nodes[r['nodes'][i]] for i in [j,j+1]];mid=[(a[k]+d[k])/2 for k in (0,1)]
 nearest=sorted([(math.dist(center(p),mid),i,p) for i,p,bb in bs if all(inbounds(v,'city') for v in p)])
 if not nearest:continue
 _,idx,src=next((q for q in nearest if q[1]not in tested),nearest[0]);tested.add(idx);C=center(src);sb=bbox(src);others=[(i,p) for i,p,bb in bs if i!=idx and gapbox(sb,bb)<80];rr=[(r,j,a,d) for r,j,a,d,bb in segments if gapbox(sb,bb)<80];reasons=Counter();passes=[]
 for aid in ['B05','B06']:
  for scale in [.9,1,1.1]:
   for du,dn in [(0,0),(-3,0),(3,0),(0,-3),(0,3)]:
    anchor=add(add(C,mul(u,du)),mul(n,dn));p=footprint(aid,anchor,scale)
    if not all(inbounds(v,'city') for v in p):reasons['blue']+=1
    elif any(pp(p,o)<2 for i,o in others):reasons['neighbour-source']+=1
    elif min(pl(p,a,d)-r['width']/2 for r,j,a,d in rr)<2:reasons['source-road-half-width']+=1
    elif any(pp(p,o)<3 for o in protected_polys):reasons['protected']+=1
    else:passes.append({'assetId':aid,'uniformScale':scale,'anchorMap':anchor})
 delta=[d[k]-a[k] for k in (0,1)];length=math.hypot(*delta);t=[v/length for v in delta]
 if projectvector(t)[0]<0:t=[-v for v in t]
 normal=[-t[1],t[0]]
 cases.append({'sourceBuildingId':f'city.buildings[{idx}]','sourceIndex':idx,'sourcePolygonMap':src,'nearestApprovedParcelIntent':strata(idx),'roadId':ex['roadId'],'sourceNodeRangeInclusive':ex['nodeRangeInclusive'],'sourceNodeIds':r['nodes'][j:j+2],'sourceSegmentMap':[a,d],'actualSourceTangentMap':t,'normalMap':normal,'frontageScreenDeg':angle(t),'normalScreenDeg':angle(normal),'projectionZ':P['axisZ'],'currentFamilyBoundedFootprintTrials':30,'rejectedByRule':dict(reasons),'passedBodyConfigurations':passes,'interpretation':'body-only diagnostic; passes still need true-door courtyard/side access checks; failures are not proof new orientation alone fixes neighbours or scale; no false all-family-no-fit claim'})
 if len(cases)==2:break
base=cases[0];t=base['actualSourceTangentMap'];normal=base['normalMap'];corners=[[-4,-3],[4,-3],[4,3],[-4,3]];groundpx=[];roofpx=[]
for ss,tt in corners:
 v=add(mul(t,ss),mul(normal,tt));q=projectvector(v);groundpx.append([768+q[0]*100,900+q[1]*100]);roofpx.append([768+q[0]*100,900+q[1]*100+7.5*P['axisZ'][1]*100])
old5=read(K/'revision-005/planning/mixed-street-layout.json');ref=next(b['sourceSelection'] for b in old5['buildings'] if b['id']=='B05')
contract={'schemaVersion':1,'status':'conditional-direction-study-not-native-production-order','newNativeNeededForSecondBatch':False,'globalResourceDeficitProven':False,'why':'five-source residential/shop increment fits current PNGs; bounded footprint failures and existing body passes do not prove every lawful side approach exhausted','sourceCases':cases,'conditionalOneAssetGeometry':{'role':'one compact low-rise residence only if a future chosen source requires exact front-to-road facing','sourceCaseIndex':0,'footprintCandidateMetres':[8,6],'heightCandidateMetres':7.5,'notSourceMeasurement':True,'frontageTangentMap':t,'depthNormalMap':normal,'fixedProjection':P,'frontageScreenDeg':base['frontageScreenDeg'],'depthScreenDeg':base['normalScreenDeg'],'wallZScreenVector':P['axisZ'],'guide':{'canvas':[1536,1536],'pixelsPerUnitCandidate':100,'anchorPixel':[768,900],'groundCornersPixel':groundpx,'roofCornersPixel':roofpx},'constructionRule':'derive u from actual source-node segment; n perpendicular in world; project each with original axisX/Y and verticalZ; no existing PNG rotation/shear','productionGate':'defer generation; require exact chosen source clearance + true door design + actual25 visual reference inspection before any later native request'},'approved25ArchitectureReference':ref,'referenceUse':'existing B05 complete source selection provenance retained; not a new crop/native production claim','no27DirectionMatrix':True,'naturalPlantCorrection':{'T02':'natural tree without pit','T01':'pit-integrated tree','claim':'T02 reusable in valid natural context; one repeated tree does not constitute multi-species forest'}}
write('direction-native-contract.json',contract)
# Actual exported plan diagram, with per-source neighbourhood cluster and unchanged stop/door separation.
W,H=1500,1000;im=Image.new('RGB',(W,H),'#f6f4ed');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f6f4ed"/>']
groups=[[b for b in batch['buildings'] if b['visualReplacementOf']['sourceIndex']in[602,609,599]],[b for b in batch['buildings'] if b['visualReplacementOf']['sourceIndex']==418],[b for b in batch['buildings'] if b['visualReplacementOf']['sourceIndex']==223]]
def label(pos,txt):x,y=pos;dr.text((x,y),txt,fill='#222222');svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="13">{html.escape(txt)}</text>')
for col,group in enumerate(groups):
 if not group:continue
 layer=Image.new('RGB',(W,H),'#f6f4ed');dr=ImageDraw.Draw(layer);svg.append(f'<defs><clipPath id="panel{col}"><rect x="{col*500}" y="140" width="500" height="860"/></clipPath></defs><g clip-path="url(#panel{col})">')
 pts=[p for b in group for p in b['footprintPolygonMap']+b['visualApproach']['centrelineMap']];C=center(pts);sc=5
 def xy(p):q=projectvector([p[k]-C[k] for k in (0,1)]);return [250+500*col+q[0]*sc,490+q[1]*sc]
 def poly(p,color):
  ps=[xy(v) for v in p];dr.polygon(ps,fill=color,outline='#888888');svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in ps)+f'" fill="{color}" stroke="#888"/>')
 for idx,p,bb in bs:
  if math.dist(center(p),C)<65:poly(p,'#e0dcd5')
 for r in batch['roads']:
  ps=[xy(v) for v in r['nodes']];dr.line(ps,fill='#aaa79e',width=round(r['width']*sc));svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in ps)+f'" fill="none" stroke="#aaa79e" stroke-width="{r["width"]*sc}"/>')
 for sf2 in batch['groundSurfaces']:
  if any(sf2['id'].startswith(b['id']) for b in group):poly(sf2['polygonMap'],'#b1c59f' if 'garden' in sf2['id'] else '#ecdbb8')
 for b in group:
  poly(b['footprintPolygonMap'],'#a98776');label(xy(b['anchorMap']),b['id']+' '+b['assetId']+f" @{b['uniformScale']}");x,y=xy(b['entryMap']);dr.ellipse((x-3,y-3,x+3,y+3),fill='red')
 label((24+col*500,175),'SOURCE-SITE GROUP '+str(col+1)+' / raw source geometry retained')
 im.paste(layer.crop((col*500,140,(col+1)*500,H)),(col*500,140));svg.append('</g>')
dr=ImageDraw.Draw(im)
dr.rectangle((0,0,W,140),fill='#f6f4ed');svg.append(f'<rect width="{W}" height="140" fill="#f6f4ed"/>');label((24,24),'FIT ROUND2 - STATIC GEOMETRY / FIVE SOURCE CANDIDATES, NOT RENDERED');label((24,48),'Door pixels fixed; navigation stop remains separate original road node; no new navigation edge or changed route.');label((24,72),'NaturalT02 has no tree pit; T01 is pit tree. Native door/step registration remains manual; no resource-generation claim.');svg.append('</svg>');(O/'second-batch-projected.svg').write_text('\n'.join(svg));im.save(O/'second-batch-projected.png')
report=f'''# 009适配第二轮：新筛100源，先交5源增量

稳定 second-expansion-batch.json SHA {frozen}；5个唯一源载体602/609/599/418/223、5视觉模块、20地面，B06×2、B01×2、B05×1。住宅与街铺在三组真实源址，不伪报5个完整街区。新住宅仅正等比0.9，B01为1；旧57实例、T01及认可基准完全未改。两处原mixed地块上下文、其余garden装饰上下文逐项记录，近邻地块用途不是原楼历史类型证明。另对3个真实大载体记录一源三模块的足迹假设与唯一源计数；因缺原功能证据保持deferred，不计几何筛查通过。大载体允许一源多模块，但无用途证据者暂不安排，不把大工厂换成小住宅。

从原1004 deferred拆出：旧325仅旧固定尺度有界记录，本轮未重测；原679未筛中已新筛100，579仍未筛。新筛13源有通过选项、87源本轮有界失败；联合选出5源。按源唯一计数与按尝试的拒绝规则分列fit-summary；各asset@scale实际尝试数分源记录。0.9先通过即停止该族，不把未试1.0/1.1说失败，也不称这些新源是从旧scale1失败中救回。正面失败会继续有限侧院L模板；结果仅说明本轮预算，非穷尽无解。

MapPOI.node是原导航/取送停靠节点；图门是真实像素映射的另一个美术点。新增每源列原stop/node/name/原坐标、固定visualDoor及路肩铺地，关联只是新设计接近关系，不声称原schema已有楼-POI绑定；不把门压道路中心，不新增导航边/POI、不改路线。复读导出楼体/铺地对其他源楼、半路宽、水、旧57与冻结首批保护通过；本楼门槛前0.6m人工地脚误差仍需接入实看，不称精密门认证。

40度方向contract给两真实源址、原road/node/tangent及u/n/Z投影、现族30次/源足迹规则证据。当前5源不需要新图；若现族body有通过，也明确写出，不能据高频方向或有界失败声称必缺图。附一款8×6低住宅的条件几何合同及旧25图B05完整选取来源，生产门禁仍hold，后续还需选定源址/门/真实参考核对，不自动生图，不做27方向矩阵。T02已纠正为无树池自然树，T01才树池；自然语境可用T02，但不能把单树复制当多种森林完成。

所有旧009文件、源city、稳定库/校准保护SHA保持。只写fit-round-2；未生图/浏览器/游戏tests/typecheck/回归/业务/存档/提交，未读在写renderer。assigned仅静态候选，渲染/用户验收数为0。
'''
(O/'REPORT.md').write_text(report)
assert sha(batchfile)==frozen and all(sha(f)==h for f,h in protected.items())
write('delivery-manifest.json',{'secondBatchSHA256':frozen,'assignedUniqueSourceCount':5,'protectedUnchanged':True,'files':[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in [batchfile,O/'fit-summary.json',O/'direction-native-contract.json',O/'REPORT.md',O/'second-batch-projected.png']]})
print('FINALIZED',frozen,len(batch['buildings']))
