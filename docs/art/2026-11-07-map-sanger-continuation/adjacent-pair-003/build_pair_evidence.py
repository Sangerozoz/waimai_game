"""Build native-pixel assembly and independent road/Tiled evidence for the pair."""
import hashlib
import heapq
import json
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
GENERATED = {}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    GENERATED[str(p.relative_to(HERE))] = sha(p)


def save_image(p, im):
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p, format='PNG')
    GENERATED[str(p.relative_to(HERE))] = sha(p)


def length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def route(graph, start, goal, excluded=None):
    adj = defaultdict(list)
    for e in graph['edges']:
        if e.get('navigationAllowed') is not True or e['id'] == excluded:
            continue
        adj[e['from']].append((e['to'], e))
        adj[e['to']].append((e['from'], e))
    queue = [(0, start, [], [])]
    seen = set()
    while queue:
        dist, node, ids, points = heapq.heappop(queue)
        if node in seen:
            continue
        seen.add(node)
        if node == goal:
            return {'start': start, 'goal': goal, 'excludedEdge': excluded,
                    'lengthPixels': dist, 'edgeIds': ids, 'points': points,
                    'navigationExcludedEdges': sorted(e['id'] for e in graph['edges'] if e.get('navigationAllowed') is not True),
                    'meaning': 'shortest undirected geometric path using permitted visible-asphalt traces; roof-occluded inferences excluded; no traffic or game simulation'}
        for other, e in adj[node]:
            p = e['points'] if node == e['from'] else list(reversed(e['points']))
            heapq.heappush(queue, (dist + e['lengthPixels'], other, ids + [e['id']], points + p[bool(points):]))
    raise ValueError('Disconnected route')


def local_graph(key):
    if key == 'W':
        coords = [
            [(73,82),(535,82),(1050,82),(1595,82)],
            [(65,479),(550,479),(1072,479),(1606,479)],
            [(64,913),(577,913),(1116,913),(1624,913)],
        ]
        mids = {
            (0,0):[(72,170),(68,350)], (0,1):[(536.5,170),(547.5,350)],
            (0,2):[(1057.5,170),(1074.5,350)], (0,3):[(1597.5,170),(1604,350)],
            (1,0):[(63.5,600),(64,800)], (1,1):[(552.5,600),(565.5,800)],
            (1,2):[(1080.5,600),(1101,800)], (1,3):[(1608.5,600),(1618,800)],
        }
    else:
        coords = [
            [(17,77),(603,77),(1138,77),(1620,77)],
            [(33,495),(606,495),(1155,495),(1638,495)],
            [(49,914),(617,914),(1169,914),(1660,914)],
        ]
        mids = {
            (0,0):[(21.5,170),(29,350)], (0,1):[(603.5,170),(605.5,350)],
            (0,2):[(1144.5,170),(1150,350)], (0,3):[(1627.5,170),(1632,350)],
            (1,0):[(34,600),(42,800)], (1,1):[(609,600),(613,800)],
            (1,2):[(1160,600),(1164,800)], (1,3):[(1646,600),(1654,800)],
        }
    nodes = [{'id':f'{key}-n-{r}-{c}', 'pixel':list(coords[r][c]), 'row':r, 'column':c}
             for r in range(3) for c in range(4)]
    edges = []
    def edge(kind, r, c, a, b, points):
        eid = f'{key}-{kind}-{r}-{c}'
        occluded = eid == 'W-h-0-2'
        edges.append({'id':eid, 'from':a, 'to':b, 'points':[list(p) for p in points],
                      'lengthPixels':length(points), 'source':key, 'bidirectionalAssumption':True,
                      'trafficVerified':False, 'coordinateUnit':'native pixels',
                      'navigationAllowed':not occluded,
                      'surfaceObservation':'roof-occluded-inference' if occluded else 'visible-asphalt-trace'})
    for r in range(3):
        for c in range(3):
            edge('h', r, c, f'{key}-n-{r}-{c}', f'{key}-n-{r}-{c+1}', [coords[r][c], coords[r][c+1]])
    for r in range(2):
        for c in range(4):
            edge('v', r, c, f'{key}-n-{r}-{c}', f'{key}-n-{r+1}-{c}', [coords[r][c], *mids[r,c], coords[r+1][c]])
    return {'coordinateUnit':'native pixels', 'metreCalibration':None,
            'traceScope':'six owned full-block enclosures; W-h-0-2 is an occluded structural inference, excluded from navigation; peripheral fragments/northern staggered exits are not navigation-certified',
            'method':'manual native-image observations, gray-asphalt run diagnostics used only as supporting observations',
            'nativeSHA256':sha(HERE/key/'native.png'), 'nodes':nodes, 'edges':edges,
            'stats':{'nodes':12,'edges':17,'components':1,'boundedFaces':6},
            'navigationStats':{'nodes':12,'edges':16 if key=='W' else 17,'components':1,'boundedFaces':5 if key=='W' else 6},
            'occludedInferenceEdgeIds':['W-h-0-2'] if key=='W' else []}


def props(values):
    return [{'name':k, 'type':'bool' if isinstance(v,bool) else 'float' if isinstance(v,(int,float)) else 'string', 'value':v}
            for k,v in values.items()]


def tiled(size, images, graph, blocks, routes=None):
    layers = []
    for name, path, dims, offset in images:
        layers.append({'id':len(layers)+1, 'name':name, 'type':'imagelayer', 'image':path,
                       'imagewidth':dims[0], 'imageheight':dims[1], 'offsetx':offset[0], 'offsety':offset[1],
                       'opacity':1,'visible':True,'locked':True})
    oid = 0
    def obj(name, kind, points, values):
        nonlocal oid
        oid += 1
        return {'id':oid,'name':name,'type':kind,'x':points[0][0],'y':points[0][1], 'width':0,'height':0,
                'rotation':0,'visible':True,'properties':props(values),
                'polygon' if kind=='owned-block' else 'polyline':[{'x':p[0]-points[0][0],'y':p[1]-points[0][1]} for p in points]}
    def group(name, objects, color, visible):
        layers.append({'id':len(layers)+1,'type':'objectgroup','name':name,'objects':objects,
                       'draworder':'index','color':color,'opacity':1,'visible':visible,'locked':False})
    for name, allowed, color, visible in [('traced-roads',True,'#ef477f',True),
                                         ('occluded-inferences',False,'#9a6fe5',False)]:
        group(name, [obj(e['id'],'pixel-road' if allowed else 'occluded-road-inference',e['points'],
              {'from':e['from'],'to':e['to'],'lengthPixels':e['lengthPixels'],
               'bidirectionalAssumption':True,'trafficVerified':False,
               'navigationAllowed':e['navigationAllowed'],'surfaceObservation':e['surfaceObservation']})
              for e in graph['edges'] if e['navigationAllowed'] is allowed],color,visible)
    group('owned-complete-blocks', [obj(b['id'],'owned-block',b['polygonPixels'],{'programme':b['programme'],
          'densityIntent':b['densityIntent'],'region':b['region'],'designMetresBound':False,
          'enclosureUsesOccludedInference':b['enclosureUsesOccludedInference']}) for b in blocks], '#45afa8',False)
    if routes:
        for name,r in routes.items():
            group(name,[obj(name,'geometric-route',r['points'],{'lengthPixels':r['lengthPixels'],
                  'excludedEdge':r['excludedEdge'] or '', 'trafficVerified':False,
                  'navigationExcludedEdges':','.join(r['navigationExcludedEdges'])})],'#29aa80' if name=='main-route' else '#e7a346',name=='main-route')
    return {'type':'map','version':'1.10','tiledversion':'1.12.2','orientation':'orthogonal','renderorder':'right-down',
            'infinite':False,'width':size[0],'height':size[1],'tilewidth':1,'tileheight':1,'tilesets':[],
            'layers':layers,'nextlayerid':len(layers)+1,'nextobjectid':oid+1,
            'properties':props({'unit':'native pixels','metreCalibration':'unestablished','formalGameTests':False,
                               'userArtApproved':False,'ordinaryRegionAdmitted':False,'trafficVerified':False})}


def main():
    owned = HERE/'generated-files.json'
    if owned.exists():
        for name, ref in json.loads(owned.read_text()).items():
            assert (HERE/name).is_file() and sha(HERE/name)==ref, f'Generated file changed: {name}'
    else:
        for pattern in ('actual-pair-graph.json','assembly-record.json','index.html','tiled/*.tmj','assembly/*.png'):
            assert not list(HERE.glob(pattern)), f'Unowned output exists: {pattern}'
    plan = json.loads((HERE/'pair-plan.json').read_text())
    natives = {k:Image.open(HERE/k/'native.png').convert('RGB') for k in ('W','E')}
    for im in natives.values():
        assert im.size==(1672,941)
    # Native-pixel ownership assembly; no local color edit, resampling, rotation, shear or warp.
    dx, dy, cut, height = 1576, -4, 1608, 937
    boxes = {'W':(0,0,cut,height),'E':(cut-dx,-dy,1672,941)}
    cores = {k:natives[k].crop(boxes[k]) for k in ('W','E')}
    pair_image = Image.new('RGB',(3248,height))
    for k,pos in [('W',(0,0)),('E',(cut,0))]:
        save_image(HERE/'assembly'/f'{k}-native-core.png',cores[k])
        pair_image.paste(cores[k],pos)
    save_image(HERE/'assembly/pair-native-pixels.png',pair_image)
    local = {k:local_graph(k) for k in ('W','E')}
    for k,g in local.items():
        save(HERE/f'{k}/actual-graph.json',g)
    nodes = []
    edges = []
    for k,g in local.items():
        tx,ty = (0,0) if k=='W' else (dx,dy)
        nodes += [{**n,'pixel':[n['pixel'][0]+tx,n['pixel'][1]+ty],'source':k} for n in g['nodes']]
        for e in g['edges']:
            if e['id'].startswith(f'{k}-v-') and int(e['id'].split('-')[-1])==(3 if k=='W' else 0):
                continue
            edges.append({**e,'points':[[p[0]+tx,p[1]+ty] for p in e['points']]})
    lookup = {n['id']:n for n in nodes}
    seam_names = sorted([f'{k}-n-{r}-{3 if k=="W" else 0}' for k in ('W','E') for r in range(3)], key=lambda n:lookup[n]['pixel'][1])
    for i,(a,b) in enumerate(zip(seam_names,seam_names[1:])):
        first,last=lookup[a]['pixel'],lookup[b]['pixel']
        bends = [[1597.5,170],[1604,350],[1608.5,600],[1618,800]]
        points=[first,*[p for p in bends if first[1]<p[1]<last[1]],last]
        edges.append({'id':f'seam-{i}', 'from':a,'to':b,'points':points,'lengthPixels':length(points),
                      'source':'assembled-shared-asphalt','bidirectionalAssumption':True,'trafficVerified':False,'coordinateUnit':'native pixels',
                      'navigationAllowed':True,'surfaceObservation':'visible-asphalt-trace'})
    graph = {'coordinateUnit':'native pixels','metreCalibration':None,'placement':{'EOriginalToW':[dx,dy],
             'cropIsOwnershipNotExtraTranslation':True},'nodes':nodes,'edges':edges,
             'traceScope':'twelve owned full-block enclosures including one roof-occluded structural inference; navigation uses the 34 permitted traces only; peripheral street fragments excluded',
             'junctionPolicy':'keep all six observed shared junction positions as separate nodes; short shared-asphalt segments connect staggered mouths',
             'stats':{'nodes':len(nodes),'edges':len(edges),'components':1,'boundedFaces':len(edges)-len(nodes)+1},
             'navigationStats':{'nodes':len(nodes),'edges':34,'components':1,'boundedFaces':11},
             'occludedInferenceEdgeIds':['W-h-0-2'],
             'trafficVerified':False,'formalGameTestsPerformed':False}
    routes={'main-route':route(graph,'W-n-1-0','E-n-1-3'),
            'alternative-route':route(graph,'W-n-1-0','E-n-1-3','W-h-1-2')}
    graph['routes']=routes
    save(HERE/'actual-pair-graph.json',graph)
    adj=defaultdict(list)
    for e in edges:
        adj[e['from']].append((e['to'],e['points']))
        adj[e['to']].append((e['from'],list(reversed(e['points']))))
    def side(a,b):
        direct=next((p for n,p in adj[a] if n==b),None)
        if direct:return direct
        assert a in seam_names and b in seam_names
        ai,bi=seam_names.index(a),seam_names.index(b)
        seq=seam_names[ai:bi+1] if ai<bi else list(reversed(seam_names[bi:ai+1]))
        out=[]
        for x,y in zip(seq,seq[1:]):
            p=next(p for n,p in adj[x] if n==y);out+=p[bool(out):]
        return out
    blocks=[]
    for k,region in plan['regions'].items():
        first_col=1 if k=='W' else 4
        for b in region['blocks']:
            c=b['column']-first_col;r=4-b['row']
            names=[f'{k}-n-{r}-{c}',f'{k}-n-{r}-{c+1}',f'{k}-n-{r+1}-{c+1}',f'{k}-n-{r+1}-{c}']
            poly=[]
            for a,z in zip(names,names[1:]+names[:1]):
                p=side(a,z);poly+=p[bool(poly):]
            poly=poly[:-1]
            blocks.append({'id':b['id'],'region':k,'programme':b['programme'],'densityIntent':b['densityIntent'],
                           'polygonPixels':poly,'completeOwnedBlockObserved':True,'designMetreMapping':None,
                           'enclosureUsesOccludedInference':k=='W' and r==0 and c==2})
    save(HERE/'actual-blocks.json',blocks)
    mismatch=[]
    for r,label in enumerate(['north-primary','middle-collector','south-local']):
        w=lookup[f'W-n-{r}-3']['pixel'];e=lookup[f'E-n-{r}-0']['pixel']
        mismatch.append({'id':label,'WPixel':w,'ERegisteredPixel':e,'delta':[e[0]-w[0],e[1]-w[1]],
                         'distancePixels':math.dist(w,e),'mergedOrSnapped':False})
    assembly={'status':'native-pixel-adjacent-proof-with-observed-staggered-junctions-not-art-approved',
              'nativeDimensions':{k:list(im.size) for k,im in natives.items()},
              'sourceSHA256':{k:sha(HERE/k/'native.png') for k in natives},
              'singleEOriginalTranslationIntoW':[dx,dy], 'sourceCropBoxes':boxes,
              'coreOffsetsInAssembly':{'W':[0,0],'E':[cut,0]},'assemblySize':[3248,height],
              'ownershipCutX':cut,'noResamplingWarpingOrColorEditing':True,
              'cutObservedInsideSharedRoadCorridor':True,'ownedBuildingsNotCutObserved':True,
              'fullNativeFilesPreserved':True,'sharedJunctionMismatches':mismatch,
              'maxSharedJunctionDistancePixels':max(x['distancePixels'] for x in mismatch),
              'exactOriginalGuideLayoutPreserved':False,'metreCalibration':None,
              'wholeCityCoverageFraction':None,'finalImageCount':None,
              'userArtApproved':False,'ordinaryRegionAdmitted':False,'formalGameTestsPerformed':False,
              'limitations':['staggered mouths/crossing markings remain visible at the seam',
                'W-h-0-2 crosses a visible rooftop at about x1440-1480/y82; preserved only as a structural inference, excluded from navigation',
                'warm storefront details and related apartment vocabulary remain',
                'manual pixel tracing is geometric evidence, not lane/traffic/turn validation',
                'no credible whole-city metre coverage; no full-game tests'],
              'evidenceBoundary':'standalone native-pixel pair, independent navigation and editable Tiled only'}
    save(HERE/'assembly-record.json',assembly)
    save(HERE/'tiled/adjacent-pair.tmj',tiled([3248,height],
         [('W-owned-native-core','../assembly/W-native-core.png',cores['W'].size,(0,0)),
          ('E-owned-native-core','../assembly/E-native-core.png',cores['E'].size,(cut,0))],graph,blocks,routes))
    for k,g in local.items():
        own=[b for b in blocks if b['region']==k]
        if k=='E':own=[{**b,'polygonPixels':[[p[0]-dx,p[1]-dy] for p in b['polygonPixels']]} for b in own]
        # Local block ledger uses the pair's physically traced shared corridor; the local graph remains original-image observations.
        save(HERE/f'tiled/{k}-native.tmj',tiled([1672,941],[(f'{k}-native','../'+k+'/native.png',[1672,941],(0,0))],g,own))
    template=(HERE/'viewer-template.html').read_text()
    data={'graph':graph,'blocks':blocks,'assembly':assembly,
          'native':{k:json.loads((HERE/k/'result.json').read_text()) for k in ('W','E')}}
    (HERE/'index.html').write_text(template.replace('__PAIR_DATA__',json.dumps(data,ensure_ascii=False)))
    GENERATED['index.html']=sha(HERE/'index.html')
    save(HERE/'generated-files.json',GENERATED.copy())
    print(json.dumps({'status':assembly['status'],'stats':graph['stats'],
          'maxJunctionResidualPixels':assembly['maxSharedJunctionDistancePixels'],
          'routes':{n:r['lengthPixels'] for n,r in routes.items()},'generatedFiles':len(GENERATED)},ensure_ascii=False))


if __name__=='__main__':
    main()
