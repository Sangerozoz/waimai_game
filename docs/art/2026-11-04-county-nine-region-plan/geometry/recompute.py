#!/usr/bin/env python3
"""Recompute planning data/SVG only; never edits source geometry or generated pixels.
Run from repository root: python3 docs/art/2026-11-04-county-nine-region-plan/geometry/recompute.py
"""
from pathlib import Path
import hashlib
import html
import json
import math

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PATHS = {
    'city': 'delivery-game/assets/resources/map-sample/city.json',
    'zoning': 'docs/art/2026-11-02-county-zoning/selection.json',
    'previousPlan': 'docs/art/2026-11-03-county-region-atlas/planning/atlas-plan.json',
    'projection': 'delivery-game/county-region-project/assets/scripts/Projection.ts',
    'userBuildingReference': 'docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png',
}
def read(key):
    return json.loads((ROOT / PATHS[key]).read_text())
def dump(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
def box(points):
    return dict(minX=min(p[0] for p in points), maxX=max(p[0] for p in points),
                minY=min(p[1] for p in points), maxY=max(p[1] for p in points))
def intersects(a, b):
    return a['minX'] <= b['maxX'] and a['maxX'] >= b['minX'] and a['minY'] <= b['maxY'] and a['maxY'] >= b['minY']
def inside(p, b):
    return b['minX'] <= p[0] <= b['maxX'] and b['minY'] <= p[1] <= b['maxY']
def intersection(a, b):
    return dict(minX=max(a['minX'], b['minX']), maxX=min(a['maxX'], b['maxX']),
                minY=max(a['minY'], b['minY']), maxY=min(a['maxY'], b['maxY']))
def corners(b):
    return [[b['minX'], b['minY']], [b['maxX'], b['minY']],
            [b['maxX'], b['maxY']], [b['minX'], b['maxY']]]
def clip(a, b, bounds):
    dx, dy = b[0]-a[0], b[1]-a[1]
    lo, hi = 0., 1.
    for p, q in [(-dx,a[0]-bounds['minX']), (dx,bounds['maxX']-a[0]),
                 (-dy,a[1]-bounds['minY']), (dy,bounds['maxY']-a[1])]:
        if abs(p) < 1e-12:
            if q < 0: return None
        elif p < 0: lo = max(lo, q/p)
        else: hi = min(hi, q/p)
    if lo > hi: return None
    return [[a[0]+lo*dx,a[1]+lo*dy], [a[0]+hi*dx,a[1]+hi*dy]]
def point_in_polygon(p, polygon):
    crossing = False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>p[1]) != (b[1]>p[1]) and p[0] < (b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:
            crossing = not crossing
    return crossing
def polygon_intersects_box(polygon, bounds):
    if not intersects(box(polygon),bounds): return False
    if any(inside(p,bounds) for p in polygon): return True
    if any(clip(a,b,bounds) is not None for a,b in zip(polygon,polygon[1:]+polygon[:1])): return True
    return any(point_in_polygon(p,polygon) for p in corners(bounds))

city, zoning, old = read('city'), read('zoning'), read('previousPlan')
zones = {k:v['worldBoundsMetresApprox'] for k,v in zoning['regions'].items()}
red, blue, green = zones['map'], zones['city'], zones['urban']
q = math.sqrt(.5)
s, c = math.sin(math.radians(62.5)), math.cos(math.radians(62.5))
def project(p): return [(p[0]-p[1])*q, (p[0]+p[1])*q*s]
nodes = {n['id']:[n['x'],n['y']] for n in city['nodes']}
roads = [(r, [nodes[n] for n in r['nodes']]) for r in city['roads']]
roadboxes = {r['id']:box(pts) for r,pts in roads}
def road_segments(bounds):
    result = []
    for road, pts in roads:
        if not intersects(roadboxes[road['id']], bounds): continue
        for i,(a,b) in enumerate(zip(pts,pts[1:])):
            part = clip(a,b,bounds)
            if part is not None:
                result.append(dict(roadId=road['id'], sourceSegmentIndex=i,
                    sourceNodeIds=road['nodes'][i:i+2], widthMetres=road.get('width',5), map=part))
    return result
def source_ids(bounds):
    road_parts = road_segments(bounds)
    buildings = [i for i,p in enumerate(city['buildings']) if p and intersects(box(p),bounds)]
    exact_buildings = [i for i in buildings if polygon_intersects_box(city['buildings'][i],bounds)]
    return dict(roadIds=sorted({r['roadId'] for r in road_parts}),
        roadNodeIds=sorted({n for r in road_parts for n in r['sourceNodeIds']}),
        nodeIdsInside=[n for n,p in nodes.items() if inside(p,bounds)],
        buildingIndices=buildings,
        exactFootprintIntersectingBuildingIndices=exact_buildings,
        exactWholeFootprintReferences=[dict(sourceBuildingIndex=i,footprint=city['buildings'][i]) for i in exact_buildings],
        buildingCounts=dict(bboxCandidates=len(buildings),exactFootprintIntersecting=len(exact_buildings),
            whollyInsideRegion=sum(all(inside(p,bounds) for p in city['buildings'][i]) for i in exact_buildings),
            crossingRegionBoundary=sum(not all(inside(p,bounds) for p in city['buildings'][i]) for i in exact_buildings),
            blueEligibleWholeFootprints=sum(all(inside(p,blue) for p in city['buildings'][i]) for i in exact_buildings)),
        blueEligibleWholeBuildingIndices=[i for i in buildings if all(inside(p,blue) for p in city['buildings'][i])],
        blueExcludedBuildingIndices=[i for i in buildings if not all(inside(p,blue) for p in city['buildings'][i])],
        areaIndices=[i for i,a in enumerate(city['areas']) if a.get('points') and intersects(box(a['points']),bounds)],
        waterwayIndices=[i for i,line in enumerate(city['waterways']) if any(clip(a,b,bounds) for a,b in zip(line,line[1:]))])

width, height = red['maxX']-red['minX'], red['maxY']-red['minY']
xs = [red['minX']+width*i/3 for i in range(4)]
ys = [red['minY']+height*i/3 for i in range(4)]
halo = 32
regions, grid = [], {}
for row in range(3):
    for col in range(3):
        j = 2-row  # row 1 is source north, not projected screen top
        core = dict(minX=xs[col],maxX=xs[col+1],minY=ys[j],maxY=ys[j+1])
        expanded = dict(minX=core['minX']-halo,maxX=core['maxX']+halo,
                        minY=core['minY']-halo,maxY=core['maxY']+halo)
        render = intersection(expanded,red)
        projected = box([project(p) for p in corners(render)])
        entry = dict(id=f'NR-{row+1}{col+1}', rowNorthToSouth=row+1,columnWestToEast=col+1,
            coreBoundsMetres=core, corePolygonMetres=corners(core),
            renderBoundsMetres=render, renderPolygonMetres=corners(render),
            renderGroundSizeMetres=[render['maxX']-render['minX'],render['maxY']-render['minY']],
            projectedGroundSpanAtUnitScale=[projected['maxX']-projected['minX'],projected['maxY']-projected['minY']],
            zonesIntersecting=[k for k,b in zones.items() if intersects(core,b)],
            coreSourceIds=source_ids(core),renderSourceIds=source_ids(render),neighbors={})
        regions.append(entry); grid[(row,col)]=entry

seams=[]
for (row,col),r in grid.items():
    for direction,dr,dc in [('north',-1,0),('south',1,0),('west',0,-1),('east',0,1)]:
        if (row+dr,col+dc) in grid: r['neighbors'][direction]=grid[(row+dr,col+dc)]['id']
    for direction,dr,dc in [('south',1,0),('east',0,1)]:
        n=grid.get((row+dr,col+dc))
        if not n: continue
        a,b=r['coreBoundsMetres'],n['coreBoundsMetres']
        edge = [[a['maxX'],a['minY']],[a['maxX'],a['maxY']]] if dc else [[a['minX'],a['minY']],[a['maxX'],a['minY']]]
        overlap=intersection(r['renderBoundsMetres'],n['renderBoundsMetres'])
        crossings=road_segments(box(edge))
        seams.append(dict(id=r['id']+'__'+n['id'],regions=[r['id'],n['id']],sharedCoreEdgeMetres=edge,
            overlapBoundsMetres=overlap,overlapWidthMetres=halo*2,
            sharedSourceRoadSegments=road_segments(overlap), sourceRoadBoundaryCrossings=crossings,
            status='source-geometry-only;no-generated-image-registration'))
manifest=[dict(role=k,file=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for k,p in PATHS.items()]
plan=dict(version=1,status='nine-region-source-plan-only;no-new-art;not-engine-integrated',
    source=manifest,coordinateUnit='unaltered-source-ground-metres',zones=zones,
    projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True,
        axisX=[q,s*q],axisY=[-q,s*q],axisZ=[0,-c],formula='u=(x-y)/sqrt(2); v=(x+y)*sin(62.5deg)/sqrt(2)-z*cos(62.5deg)'),
    production=dict(imageCount=9,absoluteImageCountLimit=16,layout='3x3 red boundary complete coverage',
        supersedesProductionOnly='previous 1056-region production scheme; sources/art/history retained',
        previousPlanRegionCount=len(old['regions']),coreSizeMetres=[width/3,height/3],haloEachSideMetres=halo,
        adjacentOverlapMetres=halo*2,renderClippedToRedBoundary=True,
        coreOwnership='min-inclusive/max-exclusive; red outer maximum inclusive; boundary source IDs intentionally shared as references',
        buildingSeamRule='Use shared complete footprint and a single owner for whole building silhouette; ground core mask is not permission to cut a building. Resolve overhang before integrating.',
        sourceIdConvention='roads/nodes use original IDs; buildings/areas/waterways use zero-based indices in pinned city.json; bbox polygon lists are conservative candidates, not exact occupied-area intersections',
        roadsOutsideBlue='source reference/landscape context only; no delivery extension',
        artAuthority=PATHS['userBuildingReference'],aiCandidateAuthority=False,
        generationCadence='one whole region then user review; no batch generation; no 1056-small-image-to-nine composite'),
    regions=regions,seams=seams,
    summary=dict(regionCount=9,seamCount=len(seams),coreAreaSquareMetres=width*height,
        coveredRedBoundsMetres=red,sourceRoadsModified=False,sourceBuildingGeometryModified=False,
        stageTests='not-triggered-not-run'))
dump('nine-regions.json',plan)

# Optimistic ground-only fit; margins/building heights can only reduce this density.
sizes=[1254,2048,4096,8192]
target=7.13458
metrics=[]
for r in regions:
    u,v=r['projectedGroundSpanAtUnitScale']; span=max(u,v)
    item=dict(regionId=r['id'],groundSizeMetres=r['renderGroundSizeMetres'],projectedGroundSpan=[u,v],
        nativeSquareForTargetGroundOnly=math.ceil(span*target),
        nativeSquareForTargetWithTenPercentCanvasReserve=math.ceil(span*target/.9),scenarios=[])
    for px in sizes:
        scale=px/span
        item['scenarios'].append(dict(nativeSquare=px,groundScalePxPerProjectionUnit=scale,
            projected8mVectorPixelsRange=[8*s*scale,8*scale],
            apparent8mRoadWidthPixelsRange=[8*s*scale,8*scale],
            projected8mAlongWorldXorY=8*math.hypot(q,q*s)*scale,
            projected20mBuildingWidthPixelsRange=[20*s*scale,20*scale],
            projected20mAlongWorldXorY=20*math.hypot(q,q*s)*scale))
    metrics.append(item)
dump('resolution-metrics.json',dict(status='mathematical-estimate-only;native-size-support-unverified',
    targetPixelsPerProjectionUnit=target,targetProvenance='task-supplied approximate A scale; not new image registration',
    nativeSquareSizes=sizes,canvasReserveAssumedForBaseTable=0,
    vectorFormula='L*scale*sqrt(cos(theta-45deg)^2+sin(elevation)^2*sin(theta-45deg)^2)',
    apparentRoadWidthFormula='W*scale*sin(elevation)/sqrt(cos(theta-45deg)^2+sin(elevation)^2*sin(theta-45deg)^2); perpendicular separation of parallel projected road edges',
    directionNote='world X/Y length factor sqrt((1+sin(elevation)^2)/2); global range sin(elevation)..1; road-normal vector length and apparent perpendicular road width differ for individual directions',
    heightReserveFormula='at target scale, z metres adds at most z*cos(62.5deg)*target pixels above ground; choose final padding after tallest buildings/shadows fixed',regions=metrics))

def svg(projected=False):
    transform=project if projected else lambda p:[p[0],-p[1]]
    ext=box([transform(p) for p in corners(red)])
    k=1100/(ext['maxX']-ext['minX']); margin=70
    H=(ext['maxY']-ext['minY'])*k+140
    def xy(p):
        t=transform(p);return [(t[0]-ext['minX'])*k+margin,(t[1]-ext['minY'])*k+margin]
    def points(pts):return ' '.join(f'{x:.3f},{y:.3f}' for x,y in map(xy,pts))
    chunks=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="{H:.0f}" viewBox="0 0 1240 {H:.3f}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="30" y="25" font-family="sans-serif" font-size="17">9-region SOURCE GEOMETRY ONLY / NOT ARTWORK</text>']
    palette=['#eff4f8','#f5f3ef','#eef5ef']
    for i,r in enumerate(regions):
        chunks.append(f'<polygon points="{points(corners(r["coreBoundsMetres"]))}" fill="{palette[i%3]}"/>')
    for segment in road_segments(red):
        chunks.append(f'<polyline points="{points(segment["map"])}" fill="none" stroke="#646c73" stroke-width="{max(.4,segment["widthMetres"]*k*.7):.3f}"/>')
    for line in city['waterways']:
        for a,b in zip(line,line[1:]):
            part=clip(a,b,red)
            if part: chunks.append(f'<polyline points="{points(part)}" fill="none" stroke="#71a5c7" stroke-width="1.2"/>')
    for r in regions:
        chunks.append(f'<polygon points="{points(corners(r["renderBoundsMetres"]))}" fill="none" stroke="#969fa6" stroke-dasharray="3 5" stroke-width=".8"/>')
        chunks.append(f'<polygon points="{points(corners(r["coreBoundsMetres"]))}" fill="none" stroke="#37434e" stroke-width="1.7"/>')
        b=r['coreBoundsMetres']; x,y=xy([(b['minX']+b['maxX'])/2,(b['minY']+b['maxY'])/2])
        chunks.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="22" text-anchor="middle" fill="#111" stroke="white" stroke-width="4" paint-order="stroke">{r["id"]}</text>')
    for name,color in [('map','#cf3333'),('city','#2475ca'),('urban','#189d48')]:
        chunks.append(f'<polygon points="{points(corners(zones[name]))}" fill="none" stroke="{color}" stroke-width="3.5"/>')
    chunks.append(f'<text x="30" y="{H-18:.0f}" font-family="sans-serif" font-size="13">Red=display / Blue=delivery-city / Green=dense urban / Dashed=32m render halo; road coordinates unchanged</text></svg>')
    (OUT/('nine-regions-projected.svg' if projected else 'nine-regions-source.svg')).write_text('\n'.join(chunks))
svg();svg(True)

lines=['# 九区几何与分辨率可行性','',
    '仅生成独立规划JSON、可复算脚本与SVG结构示意；未生图、未改源道路/三层框、未接引擎，未运行测试/typecheck/浏览器/构建/Git。运行本脚本属于资料计算。', '',
    '## 范围与接缝','',
    f'红框 {width:.2f} × {height:.2f} m；3×3均分，每张core约 {width/3:.2f} × {height/3:.2f} m。正好9张、12条共享边。行号按源北→南、列号西→东；斜投影屏幕方向以SVG为准。',
    '内边界每侧32m背景重叠（邻图64m），约为单区边长的5.8%；外边界render裁到红框。边角render约1139.83×1139.82m，边中约1171.83×1139.82m（或反向），中央1171.83×1171.82m。此重叠是同一世界内容，不是新造平行道路。',
    '原始road/node ID不变；无ID数组用钉住SHA的city.json零基索引。JSON同时列core/render源对象和每条共享边的原路交点、共享道路线段。道路端点纳入边界，源引用可重复；地面最终归属用半开core。建筑跨区保留整栋轮廓，不能按core裁半楼；跨蓝框建筑整栋不进入经营建筑。多边形bbox候选列表是保守筛选，不能当精确相交面积。',
    '旧1056块仅作为来源历史，不再作为生产拆分；禁止先生产1056小图再拼9张冒充减量。每次只出一张完整区图交用户检查，收到反馈后才开展下一张/修订。', '',
    '## 固定投影的理论像素','',
    '采用原Projection等价正交投影：u=(x-y)/√2，v=(x+y)sin62.5°/√2-z cos62.5°。px/m均指投影前统一比例参数；不是每个地面方向都有相同像素密度。无余白的正方形完整装下地面菱形，是最乐观上限。加入建筑高度、阴影和透明边距后更低。',
    '任意朝向地面线段的长度因子范围0.8870～1；源X/Y方向约0.9451。8m路宽下表按投影平行路缘的垂直距离给范围；单个方向的路宽与其法向线段长度不同。20m建筑宽按地面线段长度推算，不含屋顶/层高。', '',
    '|区号|render地面m|地面投影跨度(u×v)|1254原生：8m路/20m楼 px|2048原生|4096原生|8192原生|维持A约7.13458：最小方图边长|',
    '|---|---|---|---|---|---|---|---|']
for m in metrics:
    vals=[]
    for a in m['scenarios']:
        road=a['apparent8mRoadWidthPixelsRange']; build=a['projected20mBuildingWidthPixelsRange']
        vals.append(f'{road[0]:.1f}–{road[1]:.1f} / {build[0]:.1f}–{build[1]:.1f}')
    lines.append('|'+ '|'.join([m['regionId'],'×'.join(f'{v:.2f}' for v in m['groundSizeMetres']),
        '×'.join(f'{v:.2f}' for v in m['projectedGroundSpan']),*vals,str(m['nativeSquareForTargetGroundOnly'])])+'|')
lines += ['',
    '1254/2048/4096/8192仅为假设原生输出尺寸的数学情景，未核实任何生图工具是否支持这些尺寸，不能当能力承诺。不得把插值放大的小图当原生大图。',
    f'若保留画布每边5%（合计10%）余量，维持目标比例需约 {min(m["nativeSquareForTargetWithTenPercentCanvasReserve"] for m in metrics)}～{max(m["nativeSquareForTargetWithTenPercentCanvasReserve"] for m in metrics)} px方图；还要确认最高建筑、地形和阴影是否超出余量。每100m高度在目标比例下约额外向上329px。', '',
    '## 明显冲突与可执行边界','',
    '九张整县同时保持A近景细节，需要约1.15～1.18万像素的原生方图（尚未留高度/边距）；8192情景的密度仍低于A，1254情景的8m路仅约5～6px、20m楼仅约13～16px，无法凭提示词补回近景结构。该物理冲突需在真实工具原生能力核实后决定交付画面密度；不通过偷偷恢复小块、放大或改原路解决。',
    '3×3会切过部分原建筑和道路，重叠区可共同约束但不能保证生图一致。中央区跨较多繁华内容而外角包含较多自然背景，城市细节需求不均。若3×3实际生成效果不足，可研究9个不规则核心：把外部自然景观合并成较大的四周区域，把蓝框内分给更多较小区域；它只能重新分配像素，不能消除全县总细节预算，且需重新计算边界/完整覆盖/共享路口。当前不输出第二套生产边界，默认仍是这9区。',
    '美术权威为用户原始参考，尤其 ../2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png；AI候选（含review-001、A）不能升级为新风格母版。A约7.13458仅作任务指定的尺度比较，不意味着继承其色彩、楼型或灯光。此几何包不增加来源不明的楼型/灯光/色彩规则。', '',
    '复算：从仓库根目录运行 `python3 docs/art/2026-11-04-county-nine-region-plan/geometry/recompute.py`。输出仅写本geometry目录；source清单保留输入SHA。']
lines += ['', '## 原始源建筑数量（没有新增虚构建筑）', '',
    '下表按完整源足迹与矩形精确相交（含边界接触）；JSON保留整栋原始足迹。core跨界的同栋楼可在邻区同时计为参考，不能相加当去重全县总数。蓝框整栋合资格列要求所有顶点在蓝框内，跨蓝框整栋排除。源建筑并不覆盖所有未来布景需求。', '',
    '|区号|core相交整栋参考|其中完全落core|其中跨core|render相交整栋参考|core中蓝框整栋合资格|',
    '|---|---:|---:|---:|---:|---:|']
for r in regions:
    a,b=r['coreSourceIds']['buildingCounts'],r['renderSourceIds']['buildingCounts']
    lines.append(f'|{r["id"]}|{a["exactFootprintIntersecting"]}|{a["whollyInsideRegion"]}|{a["crossingRegionBoundary"]}|{b["exactFootprintIntersecting"]}|{a["blueEligibleWholeFootprints"]}|')
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(regions=len(regions),seams=len(seams),coreSize=[width/3,height/3],
    requiredNativeGroundOnly=[min(m['nativeSquareForTargetGroundOnly'] for m in metrics),max(m['nativeSquareForTargetGroundOnly'] for m in metrics)]),ensure_ascii=False))
