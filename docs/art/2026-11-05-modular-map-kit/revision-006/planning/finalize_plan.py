#!/usr/bin/env python3
"""Finalize static camera envelope, review limitations and artifact inventory."""
import json,hashlib
from pathlib import Path
from PIL import Image
O=Path(__file__).resolve().parent
p=json.loads((O/'next-neighborhood-plan.json').read_text())
if 'entryClosure' in p:
 import runpy
 runpy.run_path(str(O/'finalize_access.py'),run_name='__main__')
 raise SystemExit(0)
s=json.loads((O/'static-check-report.json').read_text());projection=p['projection'];q=[]
for b in p['buildings']:
 for v in b['footprintPolygonMap']:
  for h in [0,b['candidateDimensionsMetres']['height']]:
   q.append([v[0]*projection['axisX'][i]+v[1]*projection['axisY'][i]+h*projection['axisZ'][i] for i in (0,1)])
lo=[min(v[i] for v in q) for i in (0,1)];hi=[max(v[i] for v in q) for i in (0,1)];mid=[(lo[i]+hi[i])/2 for i in (0,1)];a=projection['axisX'];b=projection['axisY'];det=a[0]*b[1]-a[1]*b[0]
p['cameraSuggestions'].update({'focusMap':[(mid[0]*b[1]-mid[1]*b[0])/det,(a[0]*mid[1]-a[1]*mid[0])/det],'overviewWorldWidthCandidate':(hi[0]-lo[0])*1.15,'overviewWorldHeightCandidate':(hi[1]-lo[1])*1.15,'fitBasis':'all planned footprint corners + candidate roof heights under fixed projection; sprite overhang not calibrated'})
(O/'next-neighborhood-plan.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
blocked=[b['id'] for b in p['buildings'] if b['entryAccessAudit']['straightGroundApproachToAssignedRoadSourceBuildingBlockers']]
actual={a['assetId']:a['snapshotRuntimeFiles'] for a in p['resourceDependencies'] if a['snapshotRuntimeFiles']}
summary='\n'.join(f"- {x['id']}：源路 {x['roadId']} 节点下标 {x['nodeIndexRangeInclusive']}（含端点），{len(x['buildingIds'])}栋；实投影路向 {x['projectedFrontageDeg']:.3f}°，相对素材差 {x['differenceFromAssetFrontageDeg']:+.3f}°。" for x in p['streets'])
text=f'''# revision-006 原坐标街段规划（几何底稿）

已实际执行 `build_plan.py` 和 `finalize_plan.py`；只写本 planning 目录。读取完整 city 并确认 schema：42102节点、9970道路，建筑为坐标环，waterways为线；道路 nodes 是有序节点ID。完整原道路/节点/水域/楼形/POI快照在 `source-context.json`，来源SHA见主JSON与核对报告；原路宽度、方向、节点顺序逐值保持。

revision-005 五楼 anchor 和完整候选足迹均在绿框繁华城区，非凭视觉验收猜分区；红/蓝/绿近似矩形、配准依据和SHA已带入主JSON，每栋另列 zoneBasis。原样板保持只读。本批15栋，覆盖B01～B11，不含原样板5栋；以三个原路街段形成住宅庭院/服务混合与商业公共设施两类空间。

{summary}

主JSON保留每栋地块、足迹、anchor、entry、原路节点范围、候选退距及18块ground surfaces、9个树灯/停车位。15栋间最小净距 {s['allBuildingPairsMinMetres']:.3f}m，距源道路边 {s['buildingRoadMinMetres']:.3f}m，距原建筑 {s['buildingToSourceMinMetres']:.3f}m，距水安全范围 {s['buildingWaterMinMetres']:.3f}m，距原业务入口 {s['businessEntranceMinMetres']:.3f}m。树灯车候选地面范围无重叠，最小净距 {s['fixturePairMinimumMetres']:.3f}m。道路用源半宽胶囊，水面按原多边形；水线未提供岸宽，显式加3m保守半径，不是实测岸线。只核静态几何，不宣称游戏/遮挡/路由测试。

已打开总览及图01 TR22-v1、图11 TR32-v1完整原图，SHA复核，观察完整市场拱顶、退台体量和庭院住宅差异，记录在 `references/visual-selection.json`。选框为目测近似，会带少量周边；本角色无生图，也不将裁片当原生。

**未满足项：** N2额外B01因避碰未放，保留4栋；共15栋已达本批规模，不挤占原楼/道路。{len(blocked)}栋直达所指主路的地面线被原建筑挡住，已逐栋 entryAccessAudit 记录：{', '.join(blocked)}。三个街段由原路节点7～15连续连接，但后排院落步行铺地通达尚待单独规划；不新增道路/桥/导航边/POI，也不把停车道具当可行驶接入。27条附近源道路存在超出本批±3°候选容差的线段，orientationGaps列实际路向/节点，后续若朝这些路放楼需新原生朝向，不旋转/镜像PNG。±3°仅规划容差，非用户硬限或原生精确标定。

楼形尺寸为候选包络，anchor为候选地基中心；旧B02～B05接地点包含目测/隐蔽角推定，新B06～B11须以实际原生重测。运行依赖按assetId共享贴图、长边≤280，原生母版不进包；resourceDependencies记实际找到的运行文件/尺寸/字节/SHA与缺失标定，不代替资源验收。住宅约50%按全县蓝内总用地理解，本块未按栋数凑比例。两个PNG/SVG已实际打开检查，均明确是几何底稿；未浏览器/服务器/游戏测试/typecheck/回归，未改Tiled/viewer/源city/边界/存档，未提交推送。不是用户验收或地图完成。

复现：先运行本目录 `build_plan.py`，再运行 `finalize_plan.py`。资源依赖是执行时文件快照；在制素材后续变化须由集成方重新核对。
'''
(O/'REPORT.md').write_text(text)
artifacts=[]
for f in sorted(O.rglob('*')):
 if not f.is_file() or f.name=='artifact-inventory.json':continue
 row={'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 if f.suffix=='.png':
  with Image.open(f) as im:row.update(dimensions=list(im.size),mode=im.mode)
 artifacts.append(row)
(O/'artifact-inventory.json').write_text(json.dumps({'status':'static-planning-artifacts-not-runtime-package','artifacts':artifacts},ensure_ascii=False,indent=2)+'\n')
assert all(hashlib.sha256(Path(v['path']).read_bytes()).hexdigest()==v['sha256'] for v in p['sources'])
print(json.dumps({'buildings':len(p['buildings']),'blockedStraightAccess':len(blocked),'nativeGeneration':False,'sourceHashesUnchanged':True,'pngs':[r for r in artifacts if 'dimensions'in r]},ensure_ascii=False,indent=2))
