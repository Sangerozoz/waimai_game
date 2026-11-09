#!/usr/bin/env python3
"""Planning geometry and capacity audit only; no image API or game writes."""
import hashlib
import heapq
import json
import math
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
ART = ROOT / 'docs/art'
ZONING = ART / '2026-11-02-county-zoning/selection.json'
CITY = ROOT / 'delivery-game/assets/resources/map-sample/city.json'
SAMPLE = ART / '2026-11-06-city-image-map/compact-three-v1/preview/tiled-cli-three.png'
FONT = '/System/Library/Fonts/STHeiti Medium.ttc'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2

def clip(a, b, rect):
    x0, y0, x1, y1 = rect
    dx, dy = b[0] - a[0], b[1] - a[1]
    lo, hi = 0.0, 1.0
    for p, q in [(-dx, a[0]-x0), (dx, x1-a[0]), (-dy, a[1]-y0), (dy, y1-a[1])]:
        if abs(p) < 1e-12:
            if q < 0: return None
        elif p < 0: lo = max(lo, q/p)
        else: hi = min(hi, q/p)
        if lo > hi: return None
    return [(a[0]+lo*dx, a[1]+lo*dy), (a[0]+hi*dx, a[1]+hi*dy)]

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    before = {str(p): sha(p) for p in [ZONING, CITY, SAMPLE]}
    z = json.loads(ZONING.read_text())
    city = json.loads(CITY.read_text())
    old = z['regions']['map']['worldBoundsMetresApprox']
    ow, oh = old['maxX']-old['minX'], old['maxY']-old['minY']
    W, H = ow/2, oh/2
    def zone(name):
        b = z['regions'][name]['worldBoundsMetresApprox']
        return [(b['minX']-old['minX'])/2, (b['minY']-old['minY'])/2,
                (b['maxX']-old['minX'])/2, (b['maxY']-old['minY'])/2]
    blue, core = zone('city'), zone('urban')
    bx0, by0, bx1, by1 = blue
    xs = [bx0+30+i*(bx1-bx0-60)/8 for i in range(9)]
    ys = [by0+30+j*(by1-by0-60)/8 for j in range(9)]
    pts = {}
    for j in range(9):
        for i in range(9):
            # Gentle layout variation, shared exact intersections, not final road art.
            dx = 0 if i in (0,8) else 8*math.sin(j*.72+i*.38)
            dy = 0 if j in (0,8) else 7*math.sin(i*.71+j*.43)
            pts[i,j] = (xs[i]+dx, ys[j]+dy)
    widths = {'primary': 11, 'collector': 8, 'local': 5}
    def tier(axis, k):
        if k in (0,8) or k in ({3,6} if axis=='v' else {2,5}): return 'primary'
        if k in ({2,5} if axis=='v' else {4,7}): return 'collector'
        return 'local'
    nodes = [{'id': f'j-{i}-{j}', 'designMetres': list(pts[i,j])} for j in range(9) for i in range(9)]
    edges = []
    for axis in ['v','h']:
        for k in range(9):
            t = tier(axis,k)
            for n in range(8):
                a,b = ((k,n),(k,n+1)) if axis=='v' else ((n,k),(n+1,k))
                edges.append({'id':f'{axis}-{k}-{n}', 'corridorId':f'{axis}-{k}',
                              'from':f'j-{a[0]}-{a[1]}','to':f'j-{b[0]}-{b[1]}',
                              'tier':t,'proposedAsphaltWidthMetres':widths[t],
                              'lengthMetres':math.dist(pts[a],pts[b]),'bidirectional':True})
    blocks=[]
    for j in range(8):
        for i in range(8):
            p=[pts[i,j],pts[i+1,j],pts[i+1,j+1],pts[i,j+1]]
            c=(sum(v[0] for v in p)/4,sum(v[1] for v in p)/4)
            blocks.append({'id':f'B-{j+1:02d}-{i+1:02d}','row':j,'column':i,'polygonDesignMetres':[list(v) for v in p],
                           'centre':list(c),'centrelineEnclosedAreaMetres2':area(p)})
    unused={b['id'] for b in blocks};byid={b['id']:b for b in blocks}
    def assign(kind, targets):
        for x,y in targets:
            bid=min(unused,key=lambda k:math.dist(byid[k]['centre'],(x,y)))
            byid[bid]['programme']=kind;unused.remove(bid)
    cx,cy=(core[0]+core[2])/2,(core[1]+core[3])/2
    assign('commercial-office',[(cx+(i%2-.5)*110,cy+(i//2-2)*110) for i in range(10)])
    assign('civic',[(bx0+230,by1-150),(bx1-230,by1-150),(cx,by1-100),(bx1-120,cy+120),
                    (bx0+130,cy),(cx,by0+160),(bx1-230,by0+230),(bx0+320,by0+300)])
    assign('workshop-service',[(bx0+130+i*105,by0+110) for i in range(4)])
    assign('park-community-open',[(bx0+110,by1-130),(bx1-100,by1-280),(bx1-110,by0+120),
                                  (bx0+140,by0+430),(cx,cy),(cx-150,cy+200),(cx+180,cy-180),
                                  (bx0+470,by1-100),(bx1-350,by0+100),(bx0+100,by1-420)])
    for bid in unused:byid[bid]['programme']='residential'
    for b in blocks:
        x,y=b['centre'];b['densityIntent']='high' if core[0]<=x<=core[2] and core[1]<=y<=core[3] else 'transition'
    adj={n['id']:[] for n in nodes}
    for e in edges:
        adj[e['from']].append((e['to'],e['lengthMetres'],e['id']))
        adj[e['to']].append((e['from'],e['lengthMetres'],e['id']))
    seen=set();todo=[nodes[0]['id']]
    while todo:
        u=todo.pop()
        if u in seen:continue
        seen.add(u);todo.extend(v for v,_,_ in adj[u] if v not in seen)
    assert len(seen)==len(nodes) and len(blocks)==len(edges)-len(nodes)+1
    def path(start,end,skip=None):
        q=[(0,start,[])];best={start:0}
        while q:
            d,u,es=heapq.heappop(q)
            if u==end:return {'lengthDesignMetres':d,'edgeIds':es}
            if d!=best.get(u):continue
            for v,l,eid in adj[u]:
                if eid==skip:continue
                if d+l<best.get(v,float('inf')):best[v]=d+l;heapq.heappush(q,(d+l,v,es+[eid]))
        return None
    route=path('j-1-1','j-7-7')
    assert route is not None
    alt=path('j-1-1','j-7-7',route['edgeIds'][len(route['edgeIds'])//2])
    assert alt is not None
    # Explicitly hypothetical capacity estimates, not measurement of existing art.
    elev=math.sin(math.radians(62.5));budget=[]
    for assumed_width in [5,8,11]:
        ppu=54/(assumed_width*elev)
        budget.append({'hypotheticalAsphaltWidthMetres':assumed_width,'observedSampleRoadPixelsReference':54,
                       'assumedElevationDegreesNotMeasured':62.5,'effectiveGroundMegapixelsLowerBound':W*H*ppu*ppu*elev/1e6,
                       'isMeasuredCurrentMapCoverage':False})
    stats={'streetBlocks':len(blocks),'junctionNodes':len(nodes),'geometricRoadSegments':len(edges),
           'axisCorridors':len(set(e['corridorId'] for e in edges)),'components':1,
           'totalRoadCentrelineKm':sum(e['lengthMetres'] for e in edges)/1000,
           'programmeCounts':dict(Counter(b['programme'] for b in blocks))}
    plan={'status':'planning-proposal-only-not-final-art-not-user-approved-not-production-route',
          'confirmedRequirements':['old25 area approximately1quarter','accepted style/colors/clarity/proportions','accepted A2 core-density direction','complete city-scale road/street organisation'],
          'referenceBoundsApprox':old,'oldReferenceSizeMetres':[ow,oh],'targetDesignSizeMetres':[W,H],
          'targetAreaRatio':.25,'targetDesignAreaKm2':W*H/1e6,
          'unitsWarning':'New design metres for a proposal; not calibrated native-image metres or a surveyed new city. Border positions preserve old zoning proportions as a reversible planning default, not a confirmed site or scaled old roads.',
          'blueDesignBounds':blue,'denseCoreDesignBounds':core,'nodes':nodes,'edges':edges,'blocks':blocks,'stats':stats,
          'proposalNotUserRequirements':{'blockCount':len(blocks),'roadPattern':'network quantity/loop hierarchy baseline; align final streets to planned terrain and uses before artwork','roadWidthsMetres':widths,'innerAccessWidthLaterProposal':3.6},
          'residentialRule':'Aim about50percent of blue-zone net developable plot area;32 residential street-block labels are not proof the net area target is met.',
          'routeStructureIllustrationOnly':{'main':route,'alternativeAfterOneEdgeExcluded':alt},
          'existingABC':{'worldScaleEstablished':False,'targetCoverageFraction':None,'doNotDrawFakeCoverageFootprint':True,'classification':'retained art/connection samples, not entire-city scope proof'},
          'capacityAudit':{'scope':'sensitivity estimate, no API capability claim','currentVerifiedNativeSize':[1536,1024],
                           'fourCurrentSizeImagesMegapixels':4*1536*1024/1e6,'sixCurrentSizeImagesMegapixels':6*1536*1024/1e6,
                           'scenarios':budget,'exclusions':'Lower bound for painted ground; excludes overlap, rectangular packing and texture budget. Road width and camera are design hypotheses, not surveyed sample calibration.',
                           'decision':'Do not shrink city to meet4-6. Verify higher true native capability or transparently revise image-count trade-off; no automatic9/16/25 or interpolation.'},
          'productionAllowed':False,'originalInputSHA256':before}
    (HERE/'scope-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    canvas=Image.new('RGB',(2300,1670),'#f4f4ee');dr=ImageDraw.Draw(canvas)
    def f(n):return ImageFont.truetype(FONT,n)
    def text(x,y,s,n=24,color='#263a36'):dr.text((x,y),s,font=f(n),fill=color)
    text(60,30,'整体城市骨架｜规模纠偏草案 v1',44)
    text(60,88,'只审范围、路网和街坊组织；不是新美术图，不是已确认的新经营边界，不恢复生图。',25)
    x0,y0,side=65,185,1320
    scale=side/max(W,H)
    def q(p):return (x0+p[0]*scale,y0+(H-p[1])*scale)
    dr.rectangle([q((0,H)),q((W,0))],fill='#e4ecdc',outline='#bf5f51',width=5)
    dr.rectangle([q((bx0,by1)),q((bx1,by0))],fill='#f1eee3',outline='#327995',width=4)
    colors={'residential':'#e6d7b6','commercial-office':'#d4a787','civic':'#b4c8dc','workshop-service':'#c7c1bc','park-community-open':'#b9cdaa'}
    codes={'residential':'住','commercial-office':'商办','civic':'公建','workshop-service':'服务','park-community-open':'公园'}
    for b in blocks:dr.polygon([q(v) for v in b['polygonDesignMetres']],fill=colors[b['programme']])
    for e in sorted(edges,key=lambda e:widths[e['tier']]):
        a=next(n['designMetres'] for n in nodes if n['id']==e['from']);b=next(n['designMetres'] for n in nodes if n['id']==e['to'])
        col={'primary':'#bc704b','collector':'#527c91','local':'#8c9590'}[e['tier']]
        dr.line([q(a),q(b)],fill=col,width=max(3,round(widths[e['tier']]*scale)))
    for b in blocks:
        x,y=q(b['centre']);label=codes[b['programme']]
        dr.text((x,y),label,font=f(19),fill='#34433d',anchor='mm')
    corebox=[q((core[0],core[3])),q((core[2],core[1]))]
    dr.rectangle(corebox,outline='#885e8d',width=4)
    text(80,160,'新目标范围放大示意（设计坐标；没有把旧道路整体缩小塞进来）',25)
    text(90,1480,'红：总范围　蓝：城市／配送范围意图　紫：高密核心意图',24)
    text(90,1520,'外围自然带不经营；城市感靠蓝框内成片街坊和主次路网，不靠填满外围。',23)
    text(90,1560,'街坊色块只是用途组织；最终建筑、道路细部与分块尚未生产或定稿。',23)
    sx=1460;text(sx,160,'① 原范围与目标：同尺度面积对照',29)
    refside=530;rx,ry=sx+20,220
    dr.rectangle((rx,ry,rx+refside,ry+refside),fill='#e7ebe2',outline='#bc6259',width=4)
    def oldq(p):return (rx+(p[0]-old['minX'])/ow*refside,ry+(old['maxY']-p[1])/oh*refside)
    nodeby={str(n['id']):(n['x'],n['y']) for n in city['nodes']}
    rect=[old['minX'],old['minY'],old['maxX'],old['maxY']]
    for road in city['roads']:
        pp=[nodeby.get(str(n)) for n in road['nodes']]
        for a,b in zip(pp,pp[1:]):
            if a is None or b is None:continue
            line=clip(a,b,rect)
            if line:dr.line([oldq(v) for v in line],fill='#8d9993',width=1)
    d=refside/4
    dr.rectangle((rx+d,ry+d,rx+3*d,ry+3*d),outline='#b3653e',width=6)
    text(sx,770,f'旧近似范围 {ow/1000:.2f} × {oh/1000:.2f} km',24)
    text(sx,808,f'目标约 {W/1000:.2f} × {H/1000:.2f} km；约 {W*H/1e6:.2f} km²',24)
    text(sx,846,'内框仅比较面积大小，不是新城选址已定。',23)
    text(sx,900,'② 推荐的规模起点（尚未让用户确认）',29)
    text(sx,950,f'{stats["streetBlocks"]} 个道路围合街坊；{stats["junctionNodes"]} 个交口',27)
    text(sx,994,f'{stats["axisCorridors"]} 条纵横走廊，含外环与主次支路',25)
    text(sx,1038,f'中心线约 {stats["totalRoadCentrelineKm"]:.1f} km，整网连通',25)
    text(sx,1082,'公建可合并街坊；不是把最终城市锁成棋盘。',23)
    text(sx,1140,'③ 图数必须服从容量，不再反过来缩城市',28)
    text(sx,1190,'6 张现规格原生，合计只有约 9.4 MP。',24)
    text(sx,1230,'保留样板阅读尺度，需要先核真正原生能力。',23)
    text(sx,1270,'更高原生／更多图的取舍，验证后明确提出；',23)
    text(sx,1310,'不承诺4～6张够用，不插值冒高清。',23,color='#a54d36')
    thumb=Image.open(SAMPLE).convert('RGB');thumb.thumbnail((365,210))
    canvas.paste(thumb,(sx,1380));text(sx+390,1400,'现有 A/B/C',23)
    text(sx+390,1438,'仅保留为样板',21);text(sx+390,1476,'覆盖比例未标定',21)
    canvas.save(HERE/'overall-skeleton.png')
    assert before=={str(p):sha(p) for p in [ZONING,CITY,SAMPLE]}
    (HERE/'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{margin:0;padding:0;background:transparent;color:var(--foreground);font:15px/1.65 var(--font-sans,system-ui)}img{max-width:100%;height:auto}a{color:var(--primary)}.note{color:var(--muted-foreground)}</style><a href="overall-skeleton.png" target="_blank"><img src="overall-skeleton.png" alt="整城规模、道路层级和街坊组织草案"></a><p class="note">低成本程序结构草图，不是生图或最终城市；点击原图可看文字。64街坊是PM建议起点，不是用户指定数量；现有A/B/C尚未米数标定，不能画成已覆盖某比例。当前停止所有新美术请求。</p><p><a href="scope-plan.json">完整设计数据、假设和像素预算</a> · <a href="README.md">规范与放行顺序</a></p></html>''')
    (HERE/'README.md').write_text(f'''# 整体规范与规模纠偏草案 v1

这次只产规划图/数据，不调用Images、不改旧图/游戏/存档。

## 已确认与提议分开
- 确认：约旧25图面积1/4；认可的画风、颜色、清晰度、比例及A2核心密度保留。
- 近似参考：旧红框{ow/1000:.2f}×{oh/1000:.2f}km，新同形状目标{W/1000:.2f}×{H/1000:.2f}km；原标注本身非精密测绘。
- 新建议：{stats['streetBlocks']}街坊，{stats['junctionNodes']}交口，{stats['axisCorridors']}纵横走廊，{len(edges)}几何分段、1连通分量；中心线约{stats['totalRoadCentrelineKm']:.1f}km。这是规模/组织基线，不是用户已确认数量或最终棋盘路型。
- 主干11m、次干8m、生活支路5m为设计提案，取自旧工程已有道路宽度档位而非新图实测；内院通路另后续设计。
- 功能安排：住宅32、商办10、公建8、工坊服务4、社区公园/开放10。数量不是净用地面积验收，住宅约半仍须按蓝内净可用地面积检查。
- 新三框位置只按旧分区相对比例构造可逆草案；没有把旧路网/建筑整体压缩，不改原边界，不宣称新经营范围已上线。

## 当前问题的准确位置
现有A/B/C的世界米数没有建立，覆盖目标几成未知。图数3/4不等于面积进度。其艺术与接头成果保留为工艺样板，不能补D就称整城。

## 必须按此顺序放行
1. 先看总体范围、街坊总量、主次路/外环和各功能片区，确认这是需要的城市体量。
2. 选明确的设计标尺，建立图像像素与设计坐标的映射；真实校准与设计假设必须分开。
3. 对已认可的局部阅读尺度做原生容量核查。当前1536×1024的4～6图合计仅{4*1536*1024/1e6:.2f}～{6*1536*1024/1e6:.2f}MP，不能先承诺够用。scope-plan里的5/8/11m道路及62.5度仅敏感性假设，估算不作当前面积测量。
4. 验证真正更高原生能力或明确图数/可读尺度取舍，不擅缩地图、不插值冒高清、不自动恢复9/16/25批量生产。
5. 才按完整骨架设计分区；保道路拓扑、片区功能、尺度与接头走廊，允许不影响这些目标的小像素差。代表整区先验证实际承载的街坊数量/可读性/接头，不能又交几栋楼却称完成大片区域。
6. 接入可编辑Tiled和完整路网，再做按区真实显示/跨区示范。正式游戏测试仍待用户明确阶段完成。

结构图的功能/环路示意不代表游戏经营POI或正式导航已新增；原始输入SHA保持。生成命令：`python3 build_scope_plan.py`。
''')
    print(json.dumps({'status':'planning-artifact-generated-no-Images-call','stats':stats,'targetApproxKm':[W/1000,H/1000],
                      'sourcesUnchanged':True,'output':str(HERE/'overall-skeleton.png')},ensure_ascii=False))

if __name__=='__main__':main()
