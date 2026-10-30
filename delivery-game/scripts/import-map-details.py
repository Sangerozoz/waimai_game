"""Merge real OSM scenery without mutating the routing graph or its saved identity."""
import argparse, copy, json, math, pathlib
import xml.etree.ElementTree as ET

DEFAULT_BOUNDS=(36.18,137.92,36.29,138.05)

def ring_key(points):
    ring=[tuple(p) for p in points]
    if len(ring)>1 and ring[0]==ring[-1]:ring.pop()
    if not ring:return ()
    choices=[]
    for ordered in (ring,list(reversed(ring))):
        smallest=min(ordered)
        choices.extend(tuple(ordered[i:]+ordered[:i]) for i,p in enumerate(ordered) if p==smallest)
    return min(choices)

def polygon_area(points):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2

def clip_polygon(points,half_width,half_height):
    result=points
    for axis,edge,sign in [(0,-half_width,1),(0,half_width,-1),(1,-half_height,1),(1,half_height,-1)]:
        previous=result;result=[]
        if not previous:break
        a=previous[-1]
        for b in previous:
            a_inside=(a[axis]-edge)*sign>=0;b_inside=(b[axis]-edge)*sign>=0
            if a_inside!=b_inside:
                ratio=(edge-a[axis])/(b[axis]-a[axis])
                result.append([a[0]+(b[0]-a[0])*ratio,a[1]+(b[1]-a[1])*ratio])
            if b_inside:result.append(b)
            a=b
    cleaned=[]
    for p in result:
        rounded=[round(p[0],2),round(p[1],2)]
        if not cleaned or rounded!=cleaned[-1]:cleaned.append(rounded)
    if len(cleaned)>1 and cleaned[0]==cleaned[-1]:cleaned.pop()
    return cleaned

def clip_line(points,half_width,half_height):
    paths=[];current=[]
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];low,high=0.0,1.0
        for p,q in [(-dx,a[0]+half_width),(dx,half_width-a[0]),(-dy,a[1]+half_height),(dy,half_height-a[1])]:
            if p==0:
                if q<0:low,high=1,0;break
            elif p<0:low=max(low,q/p)
            else:high=min(high,q/p)
        if low>high:
            if len(current)>1:paths.append(current)
            current=[];continue
        start=[round(a[0]+dx*low,2),round(a[1]+dy*low,2)];end=[round(a[0]+dx*high,2),round(a[1]+dy*high,2)]
        if start==end:continue
        if current and current[-1]!=start:
            if len(current)>1:paths.append(current)
            current=[]
        if not current:current.append(start)
        current.append(end)
    if len(current)>1:paths.append(current)
    return paths

def add_details(base,sources,bounds=DEFAULT_BOUNDS):
    south,west,north,east=bounds;lat,lon=(south+north)/2,(west+east)/2
    x_scale=111320*math.cos(math.radians(lat));y_scale=111320
    half_width,half_height=base['width']/2,base['height']/2
    nodes={};ways={}
    for source in sources:
        root=ET.parse(source).getroot()
        if root.tag!='osm' or root.find('remark') is not None:raise ValueError(f'Incomplete OSM source: {source}')
        for n in root.findall('node'):
            nodes[n.attrib['id']]=[round((float(n.attrib['lon'])-lon)*x_scale,2),round((float(n.attrib['lat'])-lat)*y_scale,2)]
        for way in root.findall('way'):ways[way.attrib['id']]=way
    result=copy.deepcopy(base)
    seen_buildings={ring_key(p) for p in result['buildings']}
    seen_areas={(a['kind'],ring_key(a['points'])) for a in result['areas']}
    seen_water={min(tuple(map(tuple,p)),tuple(reversed(list(map(tuple,p))))) for p in result['waterways']}
    for identifier,way in sorted(ways.items()):
        tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
        refs=[n.attrib['ref'] for n in way.findall('nd')]
        if any(ref not in nodes for ref in refs):raise ValueError(f'Incomplete way {identifier}')
        points=[nodes[ref] for ref in refs]
        if len(points)<2:continue
        if tags.get('waterway') in ('river','stream','canal'):
            for path in clip_line(points,half_width,half_height):
                key=min(tuple(map(tuple,path)),tuple(reversed(list(map(tuple,path)))))
                if key not in seen_water:result['waterways'].append(path);seen_water.add(key)
        if len(points)<4 or refs[0]!=refs[-1]:continue
        polygon=clip_polygon(points[:-1],half_width,half_height)
        if len(polygon)<3 or polygon_area(polygon)<=12:continue
        key=ring_key(polygon)
        if tags.get('building') and tags.get('building')!='no' and key not in seen_buildings:
            result['buildings'].append(polygon);seen_buildings.add(key)
        kind=None;landuse=tags.get('landuse')
        if tags.get('natural')=='water' or tags.get('water') or landuse in ('reservoir','basin'):kind='water'
        elif tags.get('leisure') in ('park','garden','playground') or landuse in ('forest','grass','meadow','recreation_ground'):kind='green'
        elif landuse in ('farmland','orchard'):kind='farmland'
        elif landuse in ('commercial','retail','industrial'):kind='commercial'
        elif landuse=='residential':kind='residential'
        if kind and (kind,key) not in seen_areas:
            result['areas'].append({'kind':kind,'points':polygon});seen_areas.add((kind,key))
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('base');parser.add_argument('output');parser.add_argument('sources',nargs='+');args=parser.parse_args()
    base=json.loads(pathlib.Path(args.base).read_text());sources=[]
    for pattern in args.sources:
        matches=sorted(pathlib.Path().glob(pattern)) if '*' in pattern else [pathlib.Path(pattern)]
        sources.extend(matches)
    if not sources:raise ValueError('No complete scenery sources')
    result=add_details(base,sources)
    out=pathlib.Path(args.output);temporary=out.with_name(out.name+'.tmp')
    temporary.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')));temporary.replace(out)
    print(json.dumps({k:len(result[k]) for k in ['nodes','roads','pois','buildings','areas','waterways']}))

if __name__=='__main__':main()
