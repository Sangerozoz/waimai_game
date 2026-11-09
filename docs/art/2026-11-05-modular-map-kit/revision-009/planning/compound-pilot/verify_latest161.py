#!/usr/bin/env python3
"""Append-only static recheck of frozen compound plan against completed market overlay.
Never reads/replays current shared scene/viewer or writes historical pilot artifacts.
"""
import json,math,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from compound_context import load
x=load();O=x.O;pf=O/'scene-compound-pilot.json';p=x.read(pf);frozenSHA='a5564388f2efb4afc55c8baa50e0f0607b1d0484ded6c2b05b6cc9abda6edb27'
assert x.sha(pf)==frozenSHA
oldmanifest=x.read(O/'SHA256.json');oldfiles={str(O/k):x.sha(O/k) for k in oldmanifest};oldfiles[str(O/'SHA256.json')]=x.sha(O/'SHA256.json')
assert all(x.sha(O/k)==v['sha256'] for k,v in oldmanifest.items())
mf=x.K/'revision-006/integration/market-life/market-layout.json';rf=mf.with_name('REPORT.md');ir=x.K/'revision-009/pipeline/current-integration-reference.json';m=x.read(mf);ref=x.read(ir)
assert x.sha(mf)=='d70ca481d21fb6cb33c37a075c4d146c9013d58f3d6284de443f538b4c2fde14'
assert ref['currentSceneSHA256']=='e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7'
assert ref['currentSceneCounts']==[161,501] and ref['sourceCarrierCount']==81
assert ref['latestBaseSceneSHA256']==m['baselineSceneSHA256']==x.sha(x.sf)
assert m['baselineCounts']==[156,497]
newInputs={str(f):x.sha(f) for f in [mf,rf,ir]};oldInputs=x.read(O/'input-sha-before.json');assert all(x.sha(f)==s for f,s in oldInputs.items())
checks=[]
def check(ok,label,evidence=None):checks.append({'rule':label,'passed':bool(ok),'evidence':evidence})
check(len(m['existingGroundChanges'])==4 and len(m['newGroundSurfaces'])==4 and len(m['newFixtures'])==5,'completed-market-delta-counts')
check(m['oldInstancesChanged']==0 and m['newBusinessPOIs']==0 and m['newNavigationEdges']==0,'old-block-business-nav-not-mutated')
basegrounds={s['id']:s for s in x.scene['groundSurfaces']};overlay=[]
for change in m['existingGroundChanges']:
 sid=change['surfaceId'];before=change['before'];check(sid in m['authorizedOldSurfaceIds'],'explicitly-authorized-market-surface',sid)
 check(all(basegrounds[sid].get(k)==v for k,v in before.items()),'market-before-agrees-with-frozen156',sid)
 after=change['after'];basegrounds[sid]={**basegrounds[sid],**after};overlay.append({'id':sid,'poly':after['polygonMap'],'changeKind':'authorized-four-after','material':after['materialId']})
for s in m['newGroundSurfaces']:
 check(s['id'] not in basegrounds,'new-market-ground-no-ID-reuse',s['id']);basegrounds[s['id']]=s;overlay.append({'id':s['id'],'poly':s['polygonMap'],'changeKind':'new-finite-market-surface','material':s['materialId']})
check(m['immutableWalkId'] not in m['authorizedOldSurfaceIds'] and basegrounds[m['immutableWalkId']]==next(v for v in x.scene['groundSurfaces'] if v['id']==m['immutableWalkId']),'original-market-entry-walk-unchanged')
x.oldground.clear();x.oldground.extend({'id':s['id'],'poly':s['polygonMap'],'material':s.get('materialId'),'purpose':s.get('purpose','frozen existing surface')} for s in basegrounds.values())
for f in m['newFixtures']:
 check(f['persistentId'] not in {b['id'] for b in x.oldbody},'new-market-fixture-no-ID-reuse',f['persistentId']);x.oldbody.append({'id':f['persistentId'],'poly':f['groundContactPolygonMap'],'scope':f['groundContactMethod']})
check([len(x.oldbody),len(x.oldground)]==[161,501],'effective-completed-obstacle-overlay-161-501')
# No source ownership or original-road exception introduced by this recheck.
check(set(p['sourceIndices']).isdisjoint(x.bound|x.reserved),'pilot-source-remains-unbound-unreserved-in-completed-market-overlay')
N=x.nearset(p['sourceIndices']);rechecks=[]
for kind,items in [('module',p['buildings']),('ground',p['groundSurfaces'])]:
 for v in items:
  poly=v['footprintPolygonMap'] if kind=='module' else v['polygonMap'];q=x.audit(poly,N);bad=x.failures(q,kind=='module');check(not bad,'latest161-external-clearance:'+v['id'],{'rejectedBy':bad,'clearance':q});rechecks.append({'id':v['id'],'kind':kind,'polygonMap':poly,'clearance':q,'rejectedBy':bad})
fixturePairs=[]
for r in rechecks:
 for f in m['newFixtures']:
  gap=x.pp(r['polygonMap'],f['groundContactPolygonMap']);limit=1 if r['kind']=='module' else .15
  fixturePairs.append({'pilotId':r['id'],'pilotKind':r['kind'],'marketFixtureId':f['persistentId'],'libraryAssetId':f['libraryAssetId'],'gapMetres':gap,'requiredGapMetres':limit,'passed':gap>=limit,'contactMethod':f['groundContactMethod']});check(gap>=limit,'pilot-vs-new-market-footline:'+r['id']+':'+f['persistentId'],gap)
surfacePairs=[]
for r in rechecks:
 for s in overlay:
  gap=x.pp(r['polygonMap'],s['poly']);limit=1 if r['kind']=='module' else .15;surfacePairs.append({'pilotId':r['id'],'pilotKind':r['kind'],'marketSurfaceId':s['id'],'changeKind':s['changeKind'],'gapMetres':gap,'requiredGapMetres':limit,'passed':gap>=limit});check(gap>=limit,'pilot-vs-market-after-surface:'+r['id']+':'+s['id'],gap)
doorPairs=[]
for b in p['buildings']:
 for f in m['newFixtures']:
  q=b['entryMap'];poly=f['groundContactPolygonMap'];gap=0 if x.inside(q,poly) else min(x.ps(q,a,d) for a,d in x.edges(poly));doorPairs.append({'moduleId':b['persistentId'],'visibleDoorPixel':b['entryPixel'],'marketFixtureId':f['persistentId'],'doorPointToContactGapMetres':gap})
def project(q):return [sum(q[k]*p['projection']['axisX' if k==0 else 'axisY'][j] for k in (0,1)) for j in (0,1)]
def frame(v):
 anchor=project(v['anchorMap']);w,h=v['worldSizeUnits'];uv=v['anchorUV'];return [anchor[0]-uv[0]*w,anchor[1]-uv[1]*h,anchor[0]+(1-uv[0])*w,anchor[1]+(1-uv[1])*h]
framePairs=[]
for b in p['buildings']:
 for f in m['newFixtures']:
  bb,ff=frame(b),frame(f);over=max(0,min(bb[2],ff[2])-max(bb[0],ff[0]))*max(0,min(bb[3],ff[3])-max(bb[1],ff[1]));framePairs.append({'moduleId':b['persistentId'],'marketFixtureId':f['persistentId'],'fullBillboardBBoxGapProjectedUnits':x.bgap(bb,ff),'bboxIntersectionSquareProjectedUnits':over,'meaning':'conservative image-frame diagnostic only, not physical contact; includes transparent margins and crown/roof silhouettes'})
# All original95 static rules retained by immutable artifact hash; exact scene ownership/gates are not relaxed.
check(x.read(O/'static-verification.json')['planSHA256']==frozenSHA and x.read(O/'static-verification.json')['failedRuleCount']==0,'original95-rule-audit-preserved-and-linked')
check(all(x.sha(f)==s for f,s in oldInputs.items()),'initial-frozen-inputs-unchanged-after-recheck')
check(all(x.sha(f)==s for f,s in newInputs.items()),'completed-market-inputs-unchanged-after-recheck')
check(all(x.sha(f)==s for f,s in oldfiles.items()),'all-historical-pilot-artifacts-including-plan-SHA-unchanged')
failed=[r for r in checks if not r['passed']]
result={'status':'passed-latest161-static-only-pending-independent-review' if not failed else 'blocked-latest161-collision-needs-independent-v2','frozenPlanPath':str(pf),'frozenPlanSHA256':frozenSHA,'planOverwritten':False,'newCandidateVersionRequired':bool(failed),'initialAuditRetained':{'path':str(O/'static-verification.json'),'ruleCount':95,'baselineCounts':[156,497]},'completedBaseline':{'publishedSceneSHA256':ref['currentSceneSHA256'],'publishedTiledSHA256':ref['currentTiledSHA256'],'counts':[161,501],'boundUniqueSources':81,'sourceOfTruth':'completed market-layout overlay + parent published current-integration-reference; not serialized/replayed scene snapshot','marketLayoutSHA256':x.sha(mf),'marketLayoutStatusField':m['status'],'statusInterpretation':'market-layout retained prepared-stage wording; completed publish and actual rendered status comes from REPORT/current-integration-reference/parent, not guessed from this old field'},'newInputsSHA256':newInputs,'protectedHistoricalPilotArtifactsSHA256':oldfiles,'effectiveObstacleMethod':'frozen156 body/contact evidence retained; exactly4 authorized market surfaces replaced in memory,4 new grounds+5 actual contact polygons appended; no shared/source writes','passedRuleCount':len(checks)-len(failed),'failedRuleCount':len(failed),'checks':checks,'pilotRechecks':rechecks,'marketFixturePairClearances':fixturePairs,'marketSurfacePairClearances':surfacePairs,'visibleDoorRelationships':doorPairs,'fullImageFrameDiagnostics':framePairs,'counts':{'candidateUniqueSources':1,'candidateScenes':1,'candidateBuildingModules':2,'candidateGrounds':5,'newRendered':0,'newUserAccepted':0},'oldSurfaceEditRequests':[],'remainingRisks':['All footlines/hidden rear are manual estimates, not surveyed. T02 root box is0.4m; T05 root envelope2.2x1.6m is inferred with70px uncertainty.','Original own-door initial0.6m threshold tolerance remains; no new exception.','Scene-aware source ownership requires independent review and limited importer adaptation before apply.','Recheck protects completed161 market baseline only. If another completed increment lands before import, compare against it; never reset scene from planning snapshot.']}
x.write('latest161-recheck.json',result)
# Separate new appendix only; original REPORT/manifest untouched.
nearestFixture=min(fixturePairs,key=lambda v:v['gapMetres']);nearestSurface=min(surfacePairs,key=lambda v:v['gapMetres']);(O/'REPORT-latest161.md').write_text(f'''# 已发布161基线复核附档

冻结候选SHA `{frozenSHA}` 原样保留，主JSON/初始156过程/报告/SHA清单均未覆盖。已读市场完成版layout与REPORT、pipeline/current-integration-reference；市场layout SHA `{x.sha(mf)}`，当前发布scene SHA `{ref['currentSceneSHA256']}`。未读取/回放在途viewer或共享scene。

在内存仅替换获准4面after，追加4个市场新面和T02/P03/P01/P10/T05五件真实接地/保守包络，得到161物/501面障碍集；旧门路仍冻结。完成版layout保留prepared阶段status，不能据此否认已发布；发布状态依父实核及REPORT/current-reference。发布scene SHA与本次内存overlay不混同为序列化SHA。

新增复核{len(checks)}项，失败{len(failed)}项。最近市场新物为 `{nearestFixture['marketFixtureId']}`，至 `{nearestFixture['pilotId']}` 净距{nearestFixture['gapMetres']:.6f}m；最近市场改/新增面 `{nearestSurface['marketSurfaceId']}`，至 `{nearestSurface['pilotId']}` 净距{nearestSurface['gapMetres']:.6f}m。逐门/逐体/逐地面→五新物与8面的完整配对在latest161-recheck.json。两个候选图框对市场五件全图框重叠数为{sum(v['bboxIntersectionSquareProjectedUnits']>0 for v in framePairs)}，只是保守透明图框诊断，不把屋顶/冠幅当接地。

{'当前161静态障碍下通过，不需要v2或旧面修改申请。' if not failed else '存在失败，冻结v1不可直接接入，须另建v2。'}仍为1源/1scene/2模块/5面静态候选，新增已显示/用户验收0。T02树根、T05隐根、原生隐脚线保持估读不确定；不扩T05准入，不改变旧161。独立复审与scene所有权受限适配仍需完成；之后如有新完成增量，接入作者再次核冲突。

复现：`python3 verify_latest161.py`。此脚本只写本次latest161附档与几何底稿，不覆盖初始产物。
''')
# New independent geometric local diagram, no old picture mutation.
W,H=1400,1000;im=Image.new('RGB',(W,H),'#faf8f3');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#faf8f3"/>']
points=[v for r in rechecks for v in r['polygonMap']]+[v for f in m['newFixtures'] for v in f['groundContactPolygonMap']]+[v for s in overlay for v in s['poly']];bb=x.bbox([project(q) for q in points]);scale=min(1280/(bb[2]-bb[0]),700/(bb[3]-bb[1]));cx=(bb[0]+bb[2])/2;cy=(bb[1]+bb[3])/2
TF=lambda q:[(project(q)[0]-cx)*scale+700,(project(q)[1]-cy)*scale+440]
def poly(po,fill,stroke='#555555',width=1):
 pts=[TF(q) for q in po];dr.polygon(pts,fill=fill);dr.line(pts+[pts[0]],fill=stroke,width=width);svg.append('<polygon points="'+' '.join(f'{q[0]:.2f},{q[1]:.2f}' for q in pts)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
def text(at,s,size=16,color='#222222'):
 try:f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',size)
 except OSError:f=ImageFont.load_default()
 dr.text(at,s,font=f,fill=color);svg.append(f'<text x="{at[0]}" y="{at[1]+size}" font-size="{size}" font-family="Arial" fill="{color}">{html.escape(s)}</text>')
for s in x.oldground:
 if x.bgap(x.bbox(points),x.bbox(s['poly']))<3:poly(s['poly'],'#d5ddd2','#acb9a7')
for s in overlay:poly(s['poly'],'#adc4a2' if 'plant'in str(s['material']) or 'lawn'in str(s['material']) else '#dccfae','#7a8a70',2)
for f in m['newFixtures']:poly(f['groundContactPolygonMap'],'#5a8a72','#264b3c',2);q=TF(f['anchorMap']);text((q[0]+5,q[1]+3),f['libraryAssetId'],16,'#234f3d')
for s in p['groundSurfaces']:poly(s['polygonMap'],'#9ebd80' if s['materialId']=='G02-planting' else '#e9c78f','#a17e50')
for b in p['buildings']:
 poly(b['footprintPolygonMap'],'#d58e5a' if b['assetId']=='B05' else '#7d9bc5','#4b505a',2);q=TF(b['anchorMap']);text((q[0]-10,q[1]-10),b['assetId'],19);q=TF(b['entryMap']);dr.ellipse([q[0]-4,q[1]-4,q[0]+4,q[1]+4],fill='#bb2424');svg.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="4" fill="#bb2424"/>')
text((35,20),'COMPOUND PILOT / COMPLETED MARKET161 APPENDIX - GEOMETRIC DRAFT ONLY',24)
text((35,60),'Fixed candidate source125: B05+B01 / existing market0587: T02, P03, P01, P10, T05 + finite surfaces',17)
text((35,850),f'Min new fixture gap {nearestFixture["gapMetres"]:.3f}m | min market overlay surface gap {nearestSurface["gapMetres"]:.3f}m | failed rules {len(failed)}',20)
text((35,890),'Old pale-green grounds retained; dark-green fixture ground controls; tan/orange = candidate surfaces/building.',17)
text((35,925),'Manual ground controls, hidden-root uncertainty. No old161 movement, no scene replay, no apply/render claim.',17)
svg.append('</svg>');im.save(O/'compound-latest161-geometry.png');(O/'compound-latest161-geometry.svg').write_text('\n'.join(svg))
assert all(x.sha(f)==s for f,s in oldfiles.items())
newfiles=['verify_latest161.py','latest161-recheck.json','REPORT-latest161.md','compound-latest161-geometry.png','compound-latest161-geometry.svg'];x.write('SHA256-latest161.json',{f:{'sha256':x.sha(O/f),'bytes':(O/f).stat().st_size} for f in newfiles})
print(json.dumps({'status':result['status'],'frozenPlanSHA256':frozenSHA,'recheckSHA256':x.sha(O/'latest161-recheck.json'),'passed':result['passedRuleCount'],'failed':len(failed),'closestNewFixture':nearestFixture,'closestMarketSurface':nearestSurface,'imageFrameOverlaps':sum(v['bboxIntersectionSquareProjectedUnits']>0 for v in framePairs)},ensure_ascii=False))
if failed:raise SystemExit(2)
