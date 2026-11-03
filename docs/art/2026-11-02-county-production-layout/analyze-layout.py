"""Read-only geometry inventory for the county planning draft; no game execution."""
from pathlib import Path
from collections import defaultdict, deque, Counter
import csv
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
SOURCE=PROJECT/'delivery-game/assets/resources/map-sample/city.json'
SELECTION=PROJECT/'docs/art/2026-11-02-county-zoning/selection.json'
DATA=json.loads(SOURCE.read_text())
ZONES=json.loads(SELECTION.read_text())
POINTS={n['id']:(n['x'],n['y']) for n in DATA['nodes']}
BOUNDS={k:v['worldBoundsMetresApprox'] for k,v in ZONES['regions'].items()}
SAMPLE={'minX':-1720,'maxX':-1340,'minY':-240,'maxY':200}
VIEW={'minX':-1630,'maxX':-1450,'minY':-210,'maxY':10}
CONTEXT={'minX':-1860,'maxX':-1160,'minY':-450,'maxY':300}

def inside(p,b):
    return b['minX']<=p[0]<=b['maxX'] and b['minY']<=p[1]<=b['maxY']

def clip(a,b,rect):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t0,t1=0.,1.
    for p,q in [(-dx,a[0]-rect['minX']),(dx,rect['maxX']-a[0]),(-dy,a[1]-rect['minY']),(dy,rect['maxY']-a[1])]:
        if abs(p)<1e-12:
            if q<0:return None
        else:
            t=q/p
            if p<0:t0=max(t0,t)
            else:t1=min(t1,t)
            if t0>t1:return None
    if t1-t0<1e-9:return None
    return ((a[0]+dx*t0,a[1]+dy*t0),(a[0]+dx*t1,a[1]+dy*t1),t0,t1)

def visits(adj,start):
    seen={start} if start in adj else set();q=list(seen)
    for n in q:
        for v in adj.get(n,[]):
            if v not in seen:seen.add(v);q.append(v)
    return seen

def classify_side(p,b):
    return min({'N':abs(p[1]-b['maxY']),'E':abs(p[0]-b['maxX']),'S':abs(p[1]-b['minY']),'W':abs(p[0]-b['minX'])},key=lambda k: {'N':abs(p[1]-b['maxY']),'E':abs(p[0]-b['maxX']),'S':abs(p[1]-b['minY']),'W':abs(p[0]-b['minX'])}[k])

def analyze():
    blue=BOUNDS['city'];green=BOUNDS['urban']
    forward=defaultdict(set);reverse=defaultdict(set);weak=defaultdict(set)
    road_segments=[];crossings=[];edge_count=0
    for road in DATA['roads']:
        if road['speed']<=0:continue
        for i in range(1,len(road['nodes'])):
            na,nb=road['nodes'][i-1:i+1];a,b=POINTS.get(na),POINTS.get(nb)
            if not a or not b or a==b:continue
            result=clip(a,b,blue)
            if result:
                ca,cb,t0,t1=result
                road_segments.append({'road':road['id'],'from':na,'to':nb,'a':list(ca),'b':list(cb),'kind':road['kind'],'width':road['width'],'bridge':road['bridge'],'direction':road['direction'],'sourceInsideBothEnds':inside(a,blue) and inside(b,blue)})
                for p,t in [(ca,t0),(cb,t1)]:
                    if 1e-8<t<1-1e-8:
                        crossings.append({'road':road['id'],'edgeIndex':i,'point':[round(p[0],2),round(p[1],2)],'side':classify_side(p,blue),'kind':road['kind'],'width':road['width'],'bridge':road['bridge'],'direction':road['direction']})
            # Conservative planning graph: complete source edges wholly inside blue.
            if not inside(a,blue) or not inside(b,blue):continue
            weak[na].add(nb);weak[nb].add(na)
            forward[na];forward[nb];reverse[na];reverse[nb]
            if road['direction']!=-1:forward[na].add(nb);reverse[nb].add(na);edge_count+=1
            if road['direction']!=1:forward[nb].add(na);reverse[na].add(nb);edge_count+=1
    start=DATA['pois'][0]['node']
    mutually=visits(forward,start)&visits(reverse,start)
    seen=set();components=[]
    for n in weak:
        if n in seen:continue
        component=visits(weak,n);seen.update(component);components.append(component)
    components.sort(key=len,reverse=True)

    # Group adjacent crossings on the same side, e.g. parallel carriageways.
    parents=list(range(len(crossings)))
    def find(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    for i,c in enumerate(crossings):
        for j in range(i):
            d=crossings[j]
            if c['side']==d['side'] and math.dist(c['point'],d['point'])<35:
                parents[find(i)]=find(j)
    grouped=defaultdict(list)
    for i,c in enumerate(crossings):grouped[find(i)].append(c)
    rank={'primary':0,'secondary':1,'tertiary':2,'unclassified':3,'residential':4,'service':5,'cycleway':6}
    gates=[]
    for group in grouped.values():
        point=[sum(c['point'][k] for c in group)/len(group) for k in [0,1]]
        main=min(group,key=lambda c:rank.get(c['kind'],99))
        gates.append({'side':main['side'],'point':[round(v,2) for v in point],'highestKind':main['kind'],'roads':sorted({c['road'] for c in group}),'sourceCrossings':group,'bridge':any(c['bridge'] for c in group),'priority':'main-road' if rank.get(main['kind'],99)<=2 else 'local-road','treatment':'边界内最近合法转向/末端节点收口，沿原有道路不扩大经营范围' if rank.get(main['kind'],99)<=2 else '支路在最近合适街区边缘收口；外围不保留可行驶延伸'})
    gates.sort(key=lambda g:({'N':0,'E':1,'S':2,'W':3}[g['side']],g['point'][0] if g['side']=='N' else -g['point'][1] if g['side']=='E' else -g['point'][0] if g['side']=='S' else g['point'][1]))
    for i,g in enumerate(gates,1):g['id']=f'B{i:02}'
    raw_pois=[]
    for p in DATA['pois']:
        point=POINTS[p['node']]
        if inside(point,blue):raw_pois.append({**p,'point':list(point),'zone':'urban' if inside(point,green) else 'suburb','mutuallyReachableFromStart':p['node'] in mutually})
    buildings=[]
    for i,p in enumerate(DATA['buildings']):
        if not p:continue
        center=(sum(v[0] for v in p)/len(p),sum(v[1] for v in p)/len(p))
        if inside(center,blue):buildings.append({'sourceIndex':i,'zone':'urban' if inside(center,green) else 'suburb','inSample':inside(center,SAMPLE),'center':center})
    degree={n:len(v) for n,v in weak.items()}
    junctions=[{'node':n,'point':list(POINTS[n]),'degree':d} for n,d in degree.items() if d>=3 and inside(POINTS[n],SAMPLE)]
    disconnected=[{'nodeCount':len(c),'bounds':{'minX':min(POINTS[n][0] for n in c),'maxX':max(POINTS[n][0] for n in c),'minY':min(POINTS[n][1] for n in c),'maxY':max(POINTS[n][1] for n in c)}} for c in components if start not in c]
    summary={'blueSourceGraphNodes':len(weak),'blueDirectedEdgeRecords':edge_count,'weakComponentCount':len(components),'largestWeakComponentNodes':len(components[0]) if components else 0,'startMutuallyReachableNodes':len(mutually),'boundaryCrossingSourceRecords':len(crossings),'boundaryCrossingGroups':len(gates),'mainRoadCrossingGroups':sum(g['priority']=='main-road' for g in gates),'rawPOIsInsideBlue':len(raw_pois),'rawPOIsMutuallyReachable':sum(p['mutuallyReachableFromStart'] for p in raw_pois),'sourceBuildingCentersInsideBlue':len(buildings),'sourceBuildingCentersInsideGreen':sum(b['zone']=='urban' for b in buildings),'sourceBuildingCentersInsideSample':sum(b['inSample'] for b in buildings),'sampleJunctionSourceNodes':len(junctions)}
    output={'date':'2026-11-02','status':'static-source-data-planning-inventory-not-game-test-or-runtime-implementation','source':str(SOURCE.relative_to(PROJECT)),'sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'selectionSource':str(SELECTION.relative_to(PROJECT)),'selectionSHA256':hashlib.sha256(SELECTION.read_bytes()).hexdigest(),'bounds':BOUNDS,'sample':{'productionBoundsMetres':SAMPLE,'areaSquareMetres':(SAMPLE['maxX']-SAMPLE['minX'])*(SAMPLE['maxY']-SAMPLE['minY']),'groundViewPlaceholderMetres':VIEW,'contextBoundsMetres':CONTEXT,'startNode':start,'startPoint':list(POINTS[start]),'note':'首批样板范围/镜头占位为本轮PM布局建议，未在引擎中制作或验证镜头。'},'summary':summary,'boundaryGroups':gates,'rawPOIs':raw_pois,'disconnectedWeakComponents':disconnected,'sampleJunctions':junctions,'mainConnectedNodes':sorted(mutually),'roadSegmentsClippedForDrawingOnly':road_segments,'notes':['连通统计只使用蓝框内完整原始路段，保持原始单行方向及speed>0，交叉线不自动加连接。','蓝框外不作为绕行通道；道路端点裁切仅供本目录绘图，不修改city.json。','POI为原始128条目录的范围盘点，不等同于prepareCity运行时动态经营目录。','边界聚合以同边35米内交点合并，分组是审阅用，不是交通设施数量。','建筑统计按既有轮廓中心计，仅盘点数据，不代表精修量或必须保留所有重复附件。']}
    (ROOT/'layout-data.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    with (ROOT/'boundary-crossings.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f);writer.writerow(['编号','边','世界X米','世界Y米','最高道路级别','优先级','原道路ID','建议处理'])
        for g in gates:writer.writerow([g['id'],g['side'],*g['point'],g['highestKind'],g['priority'],';'.join(g['roads']),g['treatment']])
    (ROOT/'sample-layout.json').write_text(json.dumps(output['sample'],ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'summary':summary,'mainRoadGates':[{k:g[k] for k in ['id','side','point','highestKind']} for g in gates if g['priority']=='main-road'],'rawPOIs':raw_pois,'disconnectedComponents':disconnected[:12]},ensure_ascii=False))

if __name__=='__main__':analyze()
