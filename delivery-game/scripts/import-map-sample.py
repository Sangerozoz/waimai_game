"""Convert a bounded OSM XML extract into offline Cocos map geometry and graph.

No geometric crossing is promoted to a junction: source node identity is retained.
Speed and roughness are explicitly fictional game tuning values.
"""
import json, math, pathlib, sys, xml.etree.ElementTree as ET
from collections import Counter

SOUTH, WEST, NORTH, EAST = 36.18, 137.92, 36.29, 138.05
LAT, LON = (SOUTH+NORTH)/2, (WEST+EAST)/2
X_SCALE, Y_SCALE = 111320*math.cos(math.radians(LAT)), 111320
WIDTH, HEIGHT = (EAST-WEST)*X_SCALE, (NORTH-SOUTH)*Y_SCALE
roots=[ET.parse(p).getroot() for p in [sys.argv[1],*sys.argv[3:]]]
nodes = {n.attrib['id']: [round((float(n.attrib['lon'])-LON)*X_SCALE,2),round((float(n.attrib['lat'])-LAT)*Y_SCALE,2)] for root in roots for n in root.findall('node')}
ways={w.attrib['id']:w for root in roots for w in root.findall('way')}
def inside(p): return abs(p[0]) <= WIDTH/2 and abs(p[1]) <= HEIGHT/2
def area(points): return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2
def touches(points): return any(inside(p) for p in points)
classes = {'primary':(11,7.5,.13),'secondary':(10,7,.08),'tertiary':(8,6.5,.18),'residential':(5,6,.55),'unclassified':(5,6,.42),'service':(3.6,4.8,.75),'living_street':(4,5,.40),'cycleway':(3,5.5,.12)}
roads=[]; buildings=[]; areas=[]; waterways=[]; used=set(); labels=[]
for way in sorted(ways.values(),key=lambda w:w.attrib['id']):
    tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
    ids=[n.attrib['ref'] for n in way.findall('nd') if n.attrib['ref'] in nodes]
    points=[nodes[i] for i in ids]
    if len(points)<2 or not touches(points): continue
    highway=tags.get('highway','')
    if highway in classes and tags.get('access') not in ('no','private') and tags.get('bicycle')!='no' and tags.get('area')!='yes':
        width,speed,roughness=classes[highway]
        oneway=tags.get('oneway','yes' if tags.get('junction')=='roundabout' else 'no')
        direction=1 if oneway in ('yes','1','true') else -1 if oneway=='-1' else 0
        if tags.get('oneway:bicycle')=='no':direction=0
        run=[];runs=[]
        for ref in ids:
            if inside(nodes[ref]):run.append(ref)
            else:
                if len(run)>1:runs.append(run)
                run=[]
        if len(run)>1:runs.append(run)
        for j,run in enumerate(runs):
            roads.append(dict(id=way.attrib['id']+'-'+str(j),nodes=run,kind=highway,direction=direction,width=width,speed=speed,roughness=roughness,bridge=tags.get('bridge','no')!='no'))
            used.update(run)
    if tags.get('building') and len(points)>=4 and area(points)>12:buildings.append(points)
    if tags.get('natural')=='water' or tags.get('water') or tags.get('landuse') in ('reservoir','basin'):
        if len(points)>3:areas.append(dict(kind='water',points=points))
    elif tags.get('leisure') in ('park','garden','playground') or tags.get('landuse') in ('forest','grass','meadow','recreation_ground'):
        if len(points)>3:areas.append(dict(kind='green',points=points))
    elif tags.get('landuse') in ('commercial','retail','industrial'):
        if len(points)>3:areas.append(dict(kind='commercial',points=points))
    if tags.get('waterway') in ('river','stream','canal'):waterways.append(points)

# POIs use the largest strongly connected component: pickup and delivery must work both ways.
adj={n:set() for n in used};reverse={n:set() for n in used}
for r in roads:
    for a,b in zip(r['nodes'],r['nodes'][1:]):
        if r['direction']!=-1:adj[a].add(b);reverse[b].add(a)
        if r['direction']!=1:adj[b].add(a);reverse[a].add(b)
visited=set();finish=[]
for seed in sorted(used):
    if seed in visited:continue
    stack=[(seed,False)]
    while stack:
        n,done=stack.pop()
        if done:finish.append(n);continue
        if n in visited:continue
        visited.add(n);stack.append((n,True))
        stack.extend((v,False) for v in sorted(adj[n],reverse=True) if v not in visited)
components=[];remaining=set(used)
for seed in reversed(finish):
    if seed not in remaining:continue
    component={seed};stack=[seed];remaining.remove(seed)
    while stack:
        for n in reverse[stack.pop()]:
            if n in remaining:remaining.remove(n);component.add(n);stack.append(n)
    components.append(component)
largest=max(components,key=len)
def nearest(x,y,pool=largest):return min(pool,key=lambda n:((nodes[n][0]-x)**2+(nodes[n][1]-y)**2,n))
# Place fictional premises around dense street junctions rather than remote service-road ends.
junctions={n for n in largest if len(adj[n]|reverse[n])>=3}
junction_cells=Counter((math.floor(nodes[n][0]/600),math.floor(nodes[n][1]/600)) for n in junctions)
place_candidates={n for n in junctions if junction_cells[(math.floor(nodes[n][0]/600),math.floor(nodes[n][1]/600))]>=4}
if len(place_candidates)<128:raise ValueError('Not enough connected urban junctions for delivery addresses')
legacy_file=pathlib.Path(sys.argv[1]).with_name('legacy-pois.json')
pois=json.loads(legacy_file.read_text()) if legacy_file.exists() else []
for p in pois:
    if p['node'] not in largest:
        xy=nodes.get(p['node'],[0,0]);p['node']=nearest(*xy)
selected={p['node'] for p in pois}
districts=['清溪','松岭','云岸','榕树','文昌','青禾','新桥','南门','长宁']
homes=['春和里','怡景花园','嘉园公寓','晴川小区','商务中心','河畔新村','锦绣花园','创意园']
shops=['面馆','家常菜','小馆','咖啡','饭铺','烧腊店','汤粉店']
for iy in range(10):
    for ix in range(12):
        if len(pois)>=128:break
        x=(ix/11-.5)*WIDTH*.90;y=(iy/9-.5)*HEIGHT*.90
        candidates=place_candidates-selected
        n=nearest(x,y,candidates);selected.add(n)
        index=len(pois);district=districts[(iy//4)*3+min(2,ix//4)]
        kind='restaurant' if index%5==0 else ('office' if index%4==0 else 'home')
        name=district+shops[(index//5)%len(shops)] if kind=='restaurant' else district+homes[index%len(homes)]+f'·{index//8+1}栋'
        if any(p['name']==name for p in pois):name+=f' {index}号'
        pois.append(dict(name=name,node=n,kind=kind))
for iy in range(3):
    for ix in range(3):labels.append(dict(text=districts[iy*3+ix]+'片区',x=(ix-1)*WIDTH*.31,y=(iy-1)*HEIGHT*.31,kind='district'))
street_names=['清溪路','槐荫路','文昌路','南门街','长宁路','榕树街','望江路','青禾路','云杉巷','白鹭街','福安路','新桥街']
anchors=[]
for r in sorted(roads,key=lambda r:sum(math.dist(nodes[a],nodes[b]) for a,b in zip(r['nodes'],r['nodes'][1:])),reverse=True):
    if r['kind'] not in ('primary','secondary','tertiary','residential'):continue
    ps=[nodes[n] for n in r['nodes']];mid=ps[len(ps)//2]
    if any(math.dist(mid,p)<450 for p in anchors):continue
    length=sum(math.dist(a,b) for a,b in zip(ps,ps[1:]))
    if length<100:continue
    a,b=ps[max(0,len(ps)//2-1)],ps[min(len(ps)-1,len(ps)//2+1)]
    angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]));angle=((angle+90)%180)-90
    labels.append(dict(text=street_names[len(anchors)%len(street_names)],x=mid[0],y=mid[1],kind='street',angle=angle));anchors.append(mid)
    if len(anchors)>=100:break
data=dict(title='澄川',width=round(WIDTH,2),height=round(HEIGHT,2),nodes=[dict(id=n,x=nodes[n][0],y=nodes[n][1]) for n in sorted(used)],roads=roads,buildings=buildings,areas=areas,waterways=waterways,labels=labels,pois=pois)
out=pathlib.Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print(json.dumps(dict(nodes=len(used),roads=len(roads),buildings=len(buildings),areas=len(areas),waterways=len(waterways),components=len(components),largestComponent=len(largest),bytes=out.stat().st_size,classes=Counter(r['kind'] for r in roads)),ensure_ascii=False))
