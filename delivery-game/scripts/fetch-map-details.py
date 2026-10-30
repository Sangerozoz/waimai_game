"""Fetch bounded public OSM scenery tiles, preserving complete reproducible responses."""
import argparse, hashlib, json, pathlib, subprocess, time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

parser=argparse.ArgumentParser()
parser.add_argument('--tile',type=int)
parser.add_argument('--grid',type=int,default=4)
parser.add_argument('--quadrant',type=int,choices=range(4))
parser.add_argument('--endpoint',default='https://overpass-api.de/api/interpreter')
args=parser.parse_args()
folder=pathlib.Path(__file__).resolve().parents[1]/'data/map-sample/details'
folder.mkdir(parents=True,exist_ok=True)
S,W,N,E=36.18,137.92,36.29,138.05
tiles=[args.tile] if args.tile is not None else range(args.grid*args.grid)
def fetch(number,quadrant=None):
    row,col=divmod(number,args.grid)
    if not 0<=number<args.grid*args.grid:raise ValueError('Invalid tile')
    bounds=[round(S+(N-S)*row/args.grid,7),round(W+(E-W)*col/args.grid,7),round(S+(N-S)*(row+1)/args.grid,7),round(W+(E-W)*(col+1)/args.grid,7)]
    def quadrant_bounds(q):
        south,west,north,east=bounds;middle_lat=round((south+north)/2,7);middle_lon=round((west+east)/2,7)
        return [south if q<2 else middle_lat,west if q%2==0 else middle_lon,middle_lat if q<2 else north,middle_lon if q%2==0 else east]
    if quadrant is None and all((folder/f'tile-{number:02}-{q}.json').exists() and (folder/f'tile-{number:02}-{q}.osm').exists() for q in range(4)):
        for q in range(4):
            part=folder/f'tile-{number:02}-{q}.osm';record=json.loads(part.with_suffix('.json').read_text())
            if record['bboxSouthWestNorthEast']!=quadrant_bounds(q) or hashlib.sha256(part.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Cached quadrant does not match requested bounds')
        print(json.dumps({'tile':number,'status':'retained four complete quadrants'}),flush=True);return
    if quadrant is not None:bounds=quadrant_bounds(quadrant)
    bbox=','.join(map(str,bounds))
    query=f'''[out:xml][timeout:45];(way["building"]({bbox});way["waterway"~"^(river|stream|canal)$"]({bbox});way["natural"="water"]({bbox});way["landuse"~"^(forest|grass|meadow|recreation_ground|reservoir|basin|commercial|retail|industrial|farmland|orchard|residential)$"]({bbox});way["leisure"~"^(park|garden|playground)$"]({bbox}););(._;>;);out body;'''
    prefix=folder/(f'tile-{number:02}'+('' if quadrant is None else f'-{quadrant}'))
    osm=prefix.with_suffix('.osm');meta=prefix.with_suffix('.json')
    if osm.exists() and meta.exists():
        content=osm.read_bytes();record=json.loads(meta.read_text())
        if record['bboxSouthWestNorthEast']!=bounds or hashlib.sha256(content).hexdigest()!=record['sha256']:raise ValueError(f'Existing source bounds/hash changed: {osm}')
        print(json.dumps({'tile':number,'status':'retained','bytes':len(content)}),flush=True);return
    started=time.monotonic()
    # macOS curl uses the system trust store; the bundled Python has a separate CA store.
    result=subprocess.run(['/usr/bin/curl','--fail','--show-error','--silent','--max-time','65','--user-agent','CountyDeliveryMap/1.0 (offline game scenery extraction)','--data-urlencode','data@-',args.endpoint],input=query.encode(),capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr.decode('utf8','replace').strip())
    content=result.stdout
    tree=ET.fromstring(content)
    if tree.tag!='osm' or tree.find('remark') is not None:raise ValueError('Incomplete or failed OSM response: '+content[-1000:].decode('utf8','replace'))
    ways=tree.findall('way')
    if not ways:raise ValueError('Empty scenery source')
    prefix.with_suffix('.query.txt').write_text(query+'\n')
    osm.write_bytes(content)
    record={'source':'OpenStreetMap via Overpass','url':args.endpoint,'retrieved':'2026-10-28','bboxSouthWestNorthEast':bounds,'queryFile':prefix.with_suffix('.query.txt').name,'file':osm.name,'sha256':hashlib.sha256(content).hexdigest(),'licence':'ODbL 1.0','nodes':len(tree.findall('node')),'ways':len(ways),'bytes':len(content)}
    meta.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'tile':number,'status':'downloaded','seconds':round(time.monotonic()-started,1),**record}),flush=True)

if args.tile is not None:
    fetch(args.tile,args.quadrant)
else:
    if args.quadrant is not None:parser.error('--quadrant requires --tile')
    failures=[]
    with ThreadPoolExecutor(max_workers=1) as executor:
        jobs={executor.submit(fetch,number):number for number in tiles}
        for job in as_completed(jobs):
            try:job.result()
            except Exception as error:
                failures.append(jobs[job]);print(json.dumps({'tile':jobs[job],'status':'failed','error':str(error)}),flush=True)
    if failures:raise SystemExit('Incomplete tiles: '+','.join(map(str,failures)))
