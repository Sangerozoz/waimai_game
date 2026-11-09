#!/usr/bin/env python3
"""Read back exported access polygons, verify against source graph/obstacles, freeze v2."""
import json,hashlib,math,itertools,shutil
from pathlib import Path
from PIL import Image
O=Path(__file__).resolve().parent
exec(compile((O/'build_plan.py').read_text().split('# These are design envelopes')[0],str(O/'build_plan.py'),'exec'),globals())
p=read(O/'next-neighborhood-plan.json');archive=read(O/'backup-entry-before/next-neighborhood-plan.json');s=read(O/'static-check-report.json');by={b['id']:b for b in p['buildings']};proof=[]
for path in p['pedestrianConnections']:
 owner=by[path['buildingId']];entry=owner['entryMap'];normal=owner['entryOutwardNormalMap'];surfaces=[v['polygonMap'] for v in p['groundSurfaces'] if v.get('pedestrianSurfaceId')==path['id']]
 assert surfaces==path['surfacePolygonsMap'] and path['centrelineMap'][0]==entry
 assert owner['entryEvidence']['doorOffsetChosenByRouteSearch'] is False
 q=owner['entryEvidence']['fixedLocalDoorTNMetresCandidate'];expected=add(add(owner['anchorMap'],mul(u,q[0])),mul(n,q[1]));assert math.dist(entry,expected)<1e-9
 minima={'sourceBuildingMetres':9999.,'newBuildingMetres':9999.,'roadEdgeMetres':9999.,'fixtureMetres':9999.,'waterAreaMetres':9999.,'waterLineSafetyMetres':9999.,'businessEntranceMetres':9999.}
 for j,poly in enumerate(surfaces):
  assert all(inbounds(v,'urban') for v in poly)
  for i,ob in sourcebuildings:
   d=pp(poly,ob);minima['sourceBuildingMetres']=min(minima['sourceBuildingMetres'],d);assert d>=.1-1e-7,(path['id'],'source',i,d)
  for ob in locked:
   d=pp(poly,ob);assert d>=.1-1e-7
  for b in p['buildings']:
   if b['id']==owner['id'] and j==0:
    assert all(sum((v[k]-entry[k])*normal[k] for k in (0,1))>=-1e-7 for v in poly);continue
   d=pp(poly,b['footprintPolygonMap']);minima['newBuildingMetres']=min(minima['newBuildingMetres'],d);assert d>=.1-1e-7
  for rid,i,a,b,hw in roadsegments:
   d=pl(poly,a,b)-hw;minima['roadEdgeMetres']=min(minima['roadEdgeMetres'],d);assert d>=-1e-7,(path['id'],rid,i,d)
  for f in p['fixtures']:
   ob=f.get('candidateFootprintPolygonMap') or rect(f['anchorMap'],2*f.get('groundRadiusCandidateMetres',.25),2*f.get('groundRadiusCandidateMetres',.25))
   d=pp(poly,ob);minima['fixtureMetres']=min(minima['fixtureMetres'],d);assert d>=.1-1e-7
  for ob in waterpolys:
   d=pp(poly,ob);minima['waterAreaMetres']=min(minima['waterAreaMetres'],d);assert d>=3
  for a,b in waterlines:
   d=pl(poly,a,b)-3;minima['waterLineSafetyMetres']=min(minima['waterLineSafetyMetres'],d);assert d>=3
  for _,_,pos in pois:
   d=0 if inside(pos,poly) else min(ps(pos,a,b) for a,b in edges(poly));minima['businessEntranceMetres']=min(minima['businessEntranceMetres'],d);assert d>=6
 assert path['staticCollisionCount']==0
 # A path is not just an unconnected picture: successive actual strips share their butt vertices;
 # intermediate turn caps are present in surfacePolygonsMap and verified above.
 assert len(surfaces)==2*len(path['centrelineMap'])-3
 proof.append({'buildingId':owner['id'],'actualExportedPolygonCount':len(surfaces),'staticMinimumClearances':minima,'doorLocalOffsetVerified':True,'activeCollisions':0})
assert len(proof)==len(p['buildings'])==10
assert p['orientationGaps']==archive['orientationGaps'] and len(p['orientationGaps'])==27
context=read(O/'source-context.json');assert context['roads']==c['roads'] and context['nodes']==c['nodes'] and context['pois']==c['pois'] and context['sourceBuildings']==c['buildings']
assert all(sha(x['path'])==x['sha256'] for x in p['sources'])
# Recompute building distances after the two actual anchor translations.
for b in p['buildings']:
 b['staticClearance']=checks(b['footprintPolygonMap'],locked+[other['footprintPolygonMap'] for other in p['buildings'] if other['id']!=b['id']]);assert clear(b['staticClearance'])
s.update(buildings=len(p['buildings']),groundSurfaces=len(p['groundSurfaces']),buildingRoadMinMetres=min(b['staticClearance']['roadEdgeMetres'] for b in p['buildings']),buildingToSourceMinMetres=min(b['staticClearance']['sourceBuildingGapMetres'] for b in p['buildings']),buildingWaterMinMetres=min(b['staticClearance']['waterMetres'] for b in p['buildings']),allBuildingPairsMinMetres=min(pp(a['footprintPolygonMap'],b['footprintPolygonMap']) for a,b in itertools.combinations(p['buildings'],2)),businessEntranceMinMetres=min(b['staticClearance']['businessEntranceMetres'] for b in p['buildings']))
s['earlierBuildingClearances']='recomputed from final active anchors; not baseline values';s['exportedAccessPolygonReadbackProof']=proof
# Completed native/runtime files are source evidence, including deferred assets, never labelled missing.
asset_evidence=[]
for aid in ['B06','B07','B08','B09','B10','B11']:
 base=OUT.parent/'native'/f'{aid}-001';native=base/f'{aid}-v1.png';runtime=base/f'{aid}-runtime-280.png';prov=base/'provenance.json';assert native.is_file() and runtime.is_file() and prov.is_file()
 asset_evidence.append({'id':aid,'nativePath':str(native),'nativeSHA256':sha(native),'nativeSize':list(Image.open(native).size),'runtimePath':str(runtime),'runtimeSHA256':sha(runtime),'runtimeSize':list(Image.open(runtime).size),'provenancePath':str(prov),'provenanceSHA256':sha(prov),'readProvenanceStatus':read(prov).get('status',read(prov).get('candidateStatus')),'present':True,'calibrationStatus':'hand-estimated or deferred shape; production existence does not prove placement envelope'})
 assert max(Image.open(runtime).size)<=280
p['completedCurrentWaveAssetEvidence']=asset_evidence
p['version']='entry-access-subset-v2';p['status']='static-access-connected-candidate;native-ground-calibration-pending;not-runtime-or-user-accepted'
p['entryClosure']['readbackPolygonCollisionCount']=0;p['entryClosure']['stableVersionFile']='next-neighborhood-plan-access-v2.json'
# Overview camera: final static envelopes and candidate heights, with positive fit margin.
proj=p['projection'];ext=[]
for b in p['buildings']:
 for v in b['footprintPolygonMap']:
  for h in [0,b['candidateDimensionsMetres']['height']]:ext.append([v[0]*proj['axisX'][i]+v[1]*proj['axisY'][i]+h*proj['axisZ'][i] for i in (0,1)])
lo=[min(v[i] for v in ext) for i in (0,1)];hi=[max(v[i] for v in ext) for i in (0,1)];mid=[(lo[i]+hi[i])/2 for i in (0,1)];a,b=proj['axisX'],proj['axisY'];det=a[0]*b[1]-a[1]*b[0]
p['cameraSuggestions'].update(focusMap=[(mid[0]*b[1]-mid[1]*b[0])/det,(a[0]*mid[1]-a[1]*mid[0])/det],overviewWorldWidthCandidate=(hi[0]-lo[0])*1.15,overviewWorldHeightCandidate=(hi[1]-lo[1])*1.15,fitBasis='final subset candidate footprint/height envelope; native overhang pending calibration')
write('next-neighborhood-plan.json',p);write('next-neighborhood-plan-access-v2.json',p);write('static-check-report.json',s);write('entry-access-v2-verification.json',{'version':p['version'],'active':len(proof),'activeCollisions':0,'originalSourceGraphBuildingsPOIsEqual':True,'orientationGaps27Preserved':True,'polygons':proof,'nativeRuntimeEvidence':asset_evidence})
excluded='\n'.join('- '+b['id']+'：'+b['reason'] for b in p['excludedCandidates'])
minsrc=min(q['staticMinimumClearances']['sourceBuildingMetres'] for q in proof);minnew=min(q['staticMinimumClearances']['newBuildingMetres'] for q in proof)
report=f'''# 入口收口 v2：10栋候选、0处活动入口阻挡

稳定版本 `next-neighborhood-plan-access-v2.json`；当前别名 `next-neighborhood-plan.json` 内容相同。状态为**静态可接入候选子集，原生地基/门位仍待精密标定**。不是游戏接入/导航/用户验收。旧15栋与原5处直线阻挡证据保留在 `backup-entry-before/`。

三个街段保留 N1四栋、N2三栋、S1三栋。原5处问题中的 N1-04-B06、N2-01-B08、N2-03-B02、N2-04-B04 通过实际空地步行铺地连接原路肩；N2-02-B09 剔除。另剔除 B07两处、B11两处，共5处，详下。27条其他路向gap逐值保留，无旋转/镜像/拉斜PNG。

只移动两个新候选 anchor：N1-04-B06 沿depth法向-2m；S1-01-B10 沿frontage切向+2m。图中门没有编辑；门在楼体内的局部坐标先依据实际PNG目测固定，搜索只平移楼体，不优化门偏移。B01用靠右的地面门，B10用侧墙人员门，不把卷帘或屋顶门当正面人行门。目测门位/候选包络不称精密原生标定。B06～B11原生与280图均已存在，尺寸/SHA/provenance见主JSON completedCurrentWaveAssetEvidence；未读/等待接入线程的在写校准资料。

10条连接导出**1.5m宽真实铺地多边形**（直段矩形+转角外包16边形），复读导出多边形后按源道路半宽胶囊、源楼/005楼、新候选、树灯车、水与原业务入口再次静态核对。路径离源建筑最小 {minsrc:.3f}m、离新楼最小 {minnew:.3f}m（本楼门槛的首段端面接触除外）；终端距原道路铺装边保留0.02m数值安全间隙，不进入车行面。原业务入口留≥6m、水线另加3m安全半径；所有铺地在绿框内。当前楼体距道路边最小 {s['buildingRoadMinMetres']:.3f}m、楼间最小 {s['allBuildingPairsMinMetres']:.3f}m。新路段/桥/POI/导航边均为0，停车仅为静态道具。

剔除项（资源存在，不等于此旧包络可用）：
{excluded}

几何图中黄色为实际步行铺地、红点为固定门位候选、叉号为不进入活动子集的旧占位。已实际打开世界/投影PNG检查。原city、道路、原楼、业务入口与005 SHA保持；完整源道路快照逐值一致。只写本 planning；未生图/浏览器/服务器/游戏测试/typecheck/回归/存档/提交推送。

复现：`python3 build_plan.py` → `python3 close_access.py` → `python3 finalize_access.py`（均在本目录）。最终证据 `entry-access-v2-verification.json`；实际执行日志 `entry-execution-log.txt`。原生校准后形体若不同，须重跑静态布局，不能直接把当前包络当实测足迹。
'''
(O/'REPORT.md').write_text(report);(O/'REPORT-access-v2.md').write_text(report)
# Freeze the actual reviewed geometry with versioned filenames too.
for stem in ['neighborhood-world-geometry','neighborhood-projected-geometry']:
 for suffix in ['.png','.svg']:shutil.copyfile(O/(stem+suffix),O/(stem+'-access-v2'+suffix))
files=[]
for name in ['next-neighborhood-plan-access-v2.json','REPORT-access-v2.md','entry-access-v2-verification.json','neighborhood-world-geometry-access-v2.png','neighborhood-projected-geometry-access-v2.png','close_access.py','finalize_access.py']:
 f=O/name;v={'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)}
 if f.suffix=='.png':v['dimensions']=list(Image.open(f).size)
 files.append(v)
write('access-v2-manifest.json',{'version':p['version'],'activeBuildings':10,'activeEntryBlockers':0,'excludedCandidates':5,'artifacts':files})
print(json.dumps({'active':10,'activeBlockers':0,'excluded':5,'minPathSourceBuilding':minsrc,'minPathNewBuilding':minnew,'minBuildingRoad':s['buildingRoadMinMetres'],'minBuildingPair':s['allBuildingPairsMinMetres'],'files':files},ensure_ascii=False,indent=2))
