#!/usr/bin/env python3
"""Recompute planning data/SVG only; never edits source geometry or generated pixels.
Run from repository root: python3 docs/art/2026-11-04-county-twentyfive-region-plan/geometry/recompute.py
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
    'userBuildingReference': 'docs/art/2026-11-03-map-production-method-review/user-region-map-reference.png',
    'sixteenRegionPlan': 'docs/art/2026-11-04-county-sixteen-region-plan/geometry/sixteen-regions.json',
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
xs = [red['minX']+width*i/5 for i in range(6)]
ys = [red['minY']+height*i/5 for i in range(6)]
halo = 32
regions, grid = [], {}
for row in range(5):
    for col in range(5):
        j = 4-row  # row 1 is source north, not projected screen top
        core = dict(minX=xs[col],maxX=xs[col+1],minY=ys[j],maxY=ys[j+1])
        expanded = dict(minX=core['minX']-halo,maxX=core['maxX']+halo,
                        minY=core['minY']-halo,maxY=core['maxY']+halo)
        render = intersection(expanded,red)
        projected = box([project(p) for p in corners(render)])
        entry = dict(id=f'TR-{row+1}{col+1}', rowNorthToSouth=row+1,columnWestToEast=col+1,
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
plan=dict(version=1,status='twentyfive-region-source-plan-only;no-new-art;not-engine-integrated',
    source=manifest,coordinateUnit='unaltered-source-ground-metres',zones=zones,
    projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True,
        axisX=[q,s*q],axisY=[-q,s*q],axisZ=[0,-c],formula='u=(x-y)/sqrt(2); v=(x+y)*sin(62.5deg)/sqrt(2)-z*cos(62.5deg)'),
    production=dict(imageCount=25,conditionalAlternative=True,layout='5x5 red boundary complete coverage',
        alternativeScope='candidate alternative to 4x4 sixteen-region scheme; sources/art/history retained; no batch production authorization',
        previousPlanRegionCount=len(old['regions']),coreSizeMetres=[width/5,height/5],haloEachSideMetres=halo,
        adjacentOverlapMetres=halo*2,renderClippedToRedBoundary=True,
        coreOwnership='min-inclusive/max-exclusive; red outer maximum inclusive; boundary source IDs intentionally shared as references',
        buildingSeamRule='Use shared complete footprint and a single owner for whole building silhouette; ground core mask is not permission to cut a building. Resolve overhang before integrating.',
        sourceIdConvention='roads/nodes use original IDs; buildings/areas/waterways use zero-based indices in pinned city.json; bbox polygon lists are conservative candidates, not exact occupied-area intersections',
        roadsOutsideBlue='source reference/landscape context only; no delivery extension',
        artAuthority=PATHS['userBuildingReference'],aiCandidateAuthority=False,
        generationCadence='one whole region then user review; no batch generation; no small-image composite'),
    regions=regions,seams=seams,
    summary=dict(regionCount=25,seamCount=len(seams),coreAreaSquareMetres=width*height,
        coveredRedBoundsMetres=red,sourceRoadsModified=False,sourceBuildingGeometryModified=False,
        stageTests='not-triggered-not-run'))
dump('twentyfive-regions.json',plan)

# Optimistic ground-only fit; margins/building heights can only reduce this density.
sizes=[1254,2048,4096,8192]
target=7.13458
sixteen = read('sixteenRegionPlan')
sixteen_spans = [max(r['projectedGroundSpanAtUnitScale']) for r in sixteen['regions']]
def edge_count(r, n):
    return int(r['rowNorthToSouth'] in (1,n)) + int(r['columnWestToEast'] in (1,n))
metrics=[]
for r in regions:
    u,v=r['projectedGroundSpanAtUnitScale']; span=max(u,v)
    item=dict(regionId=r['id'],groundSizeMetres=r['renderGroundSizeMetres'],projectedGroundSpan=[u,v],
        nativeSquareForTargetGroundOnly=math.ceil(span*target),
        linearDensityGainVsSixteenSameEdgeClass=max(max(t['projectedGroundSpanAtUnitScale']) for t in sixteen['regions'] if edge_count(t,4)==edge_count(r,5))/span,
        linearDensityGainVsSixteenSameNativeSizeRange=[min(sixteen_spans)/span,max(sixteen_spans)/span],
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
        '<text x="30" y="25" font-family="sans-serif" font-size="17">25-region SOURCE GEOMETRY ONLY / NOT ARTWORK</text>']
    palette=['#eff4f8','#f5f3ef','#eef5ef']
    for i,r in enumerate(regions):
        chunks.append(f'<polygon points="{points(corners(r["coreBoundsMetres"]))}" fill="{palette[i%3]}"/>')
    for segment in road_segments(red):
        chunks.append(f'<polyline points="{points(segment["map"])}" fill="none" stroke="#646c73" stroke-width="{max(.4,segment["widthMetres"]*k*.7):.3f}"/>')
    for line in city['waterways']:
        for a,b in zip(line,line[1:]):
            part=clip(a,b,red)
            if part: chunks.append(f'<polyline points="{points(part)}" fill="none" stroke="#71a5c7" stroke-width="1.2"/>')
    for footprint in city['buildings']:
        if footprint and polygon_intersects_box(footprint,red):
            chunks.append(f'<polygon points="{points(footprint)}" fill="#bac0c5" stroke="#858c93" stroke-width=".3"/>')
    for r in regions:
        chunks.append(f'<polygon points="{points(corners(r["renderBoundsMetres"]))}" fill="none" stroke="#969fa6" stroke-dasharray="3 5" stroke-width=".8"/>')
        chunks.append(f'<polygon points="{points(corners(r["coreBoundsMetres"]))}" fill="none" stroke="#37434e" stroke-width="1.7"/>')
        b=r['coreBoundsMetres']; x,y=xy([(b['minX']+b['maxX'])/2,(b['minY']+b['maxY'])/2])
        chunks.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="22" text-anchor="middle" fill="#111" stroke="white" stroke-width="4" paint-order="stroke">{r["id"]}</text>')
    for name,color in [('map','#cf3333'),('city','#2475ca'),('urban','#189d48')]:
        chunks.append(f'<polygon points="{points(corners(zones[name]))}" fill="none" stroke="{color}" stroke-width="3.5"/>')
    chunks.append(f'<text x="30" y="{H-18:.0f}" font-family="sans-serif" font-size="13">Red=display / Blue=delivery-city / Green=dense urban / Dashed=32m render halo; road coordinates unchanged</text></svg>')
    (OUT/('twentyfive-regions-projected.svg' if projected else 'twentyfive-regions-source.svg')).write_text('\n'.join(chunks))
svg();svg(True)


lines = ['# 5×5二十五区几何备选包', '',
    '仅独立规划资料，未生图、部署、配准或操作游戏/测试/构建/Git；源city、道路、建筑、三框不修改。', '',
    f'红框完整覆盖 {width:.2f}×{height:.2f}m；25个core各 {width/5:.2f}×{height/5:.2f}m。TR-11至TR-55，行北到南、列西到东；共40条相邻共享边。每侧32m halo，邻区重叠64m，外缘裁到红框。',
    'JSON保留原路/节点ID、源建筑完整足迹与零基索引、蓝框整栋资格、各区core/render参考、三框与共享边原道路交点。跨区建筑不能裁半栋，跨蓝框整栋排除经营。投影保持俯角62.5°、方位45°。SVG是结构示意，颜色没有美术权威。', '',
    '唯一风格原参考：用户 /Users/sanger/Downloads/11/地图效果图.png 的原字节归档 docs/art/2026-11-03-map-production-method-review/user-region-map-reference.png；SHA见source清单。AI候选不递归作为风格母版。住宅约占蓝框内规划街区用地50%（含设施庭院/社区公园，排除道路、水域及外围背景），非楼栋数或全图面积；功能/建筑类型共同丰富。绿植颜色略深，密度相对NR-22-v3保留约90%；此包只记录约束，不制作美术。', '',
    '每次只生产一张整区新图交用户检查，反馈后再出下一张或修订；本包不触发生图。', '',
    '## 分辨率计算', '',
    '现有实际生图输出1254×1254。下表2048/4096/8192仅数学情景，工具支持未经核实。无留白完整容纳地面投影的乐观上限；建筑高度、阴影及边距会进一步降低密度。8m路宽为投影平行路缘垂距范围，20m楼为地面线段宽度范围。不可将插值当原生清晰度。', '',
    '|区号|render地面m|1254：8m路 / 20m楼 px|同原生尺寸较16图线性密度倍数范围|维持旧A约7.13458px/m所需原生边长|',
    '|---|---|---|---|---|']
for m in metrics:
    a=m['scenarios'][0]; road=a['apparent8mRoadWidthPixelsRange']; build=a['projected20mBuildingWidthPixelsRange']; gain=m['linearDensityGainVsSixteenSameNativeSizeRange']
    lines.append(f"|{m['regionId']}|{'×'.join(f'{x:.2f}' for x in m['groundSizeMetres'])}|{road[0]:.2f}–{road[1]:.2f} / {build[0]:.2f}–{build[1]:.2f}|{gain[0]:.4f}–{gain[1]:.4f}|{m['nativeSquareForTargetGroundOnly']}|")
lines += ['', '16图各区halo大小不同，因此比较给出对旧各区的完整范围；core无halo理想提升为5/4=1.25倍，实际render提升见表，并非25/16倍线性清晰度。所有2048/4096/8192详细情景见resolution-metrics.json。',
    f"维持A尺度的纯地面最小方图约{min(m['nativeSquareForTargetGroundOnly'] for m in metrics)}–{max(m['nativeSquareForTargetGroundOnly'] for m in metrics)}px；预留画布合计10%后约{min(m['nativeSquareForTargetWithTenPercentCanvasReserve'] for m in metrics)}–{max(m['nativeSquareForTargetWithTenPercentCanvasReserve'] for m in metrics)}px。A仅是尺度比较，不是风格来源。25图较16图增加56.25%张数；同外缘类别比较的render线性密度约提升23%–24%，不能据此承诺高清。", '',
    '复算（仓库根目录）：python3 docs/art/2026-11-04-county-twentyfive-region-plan/geometry/recompute.py。只写本geometry目录，输入SHA保存在JSON。']
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(regions=len(regions), seams=len(seams), coreSize=[width/5,height/5], requiredNativeGroundOnly=[min(m['nativeSquareForTargetGroundOnly'] for m in metrics),max(m['nativeSquareForTargetGroundOnly'] for m in metrics)])))
