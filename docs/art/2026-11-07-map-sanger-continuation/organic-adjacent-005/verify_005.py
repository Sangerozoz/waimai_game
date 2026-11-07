"""Independently verify bounded005 evidence. --read-only never writes a report."""
import argparse
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CHECKS=[]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def read(rel):return json.loads((HERE/rel).read_text())


def need(name,ok,details=None):
    CHECKS.append({'name':name,'passed':bool(ok),'details':details})
    if not ok:raise AssertionError((name,details))


def geometry(g,label):
    nodes=g['nodes'];edges=g['edges'];adj=defaultdict(list);lines=[];directed={}
    need(label+' unique edge IDs',len({e['id'] for e in edges})==len(edges))
    for e in edges:
        ps=e['points'];u=e['from'];v=e['to']
        need(label+' edge '+e['id'],u in nodes and v in nodes and u!=v and len(ps)>=2
             and ps[0]==nodes[u] and ps[-1]==nodes[v]
             and math.isclose(e['lengthPixels'],sum(math.dist(a,b)for a,b in zip(ps,ps[1:])),abs_tol=1e-9)
             and e['navigationAllowed'] is True and e['surfaceObservation']=='visible-asphalt-manual-trace'
             and e['trafficVerified'] is False and e['bidirectionalAssumption'] is True)
        for i,(a,b) in enumerate(zip(ps,ps[1:])):
            need(label+' nonzero segment '+e['id']+':'+str(i),a!=b)
            lines.append((e['id'],i,tuple(a),tuple(b),{u,v}))
        for u,v,ps in [(u,v,ps),(v,u,ps[::-1])]:
            adj[u].append(v);directed[u,v]=ps
    def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    pairs=0
    for i,(eid,idx,a,b,ends) in enumerate(lines):
        for fid,jdx,c,d,fends in lines[i+1:]:
            pairs+=1
            if max(a[0],b[0])<min(c[0],d[0])or max(c[0],d[0])<min(a[0],b[0])or max(a[1],b[1])<min(c[1],d[1])or max(c[1],d[1])<min(a[1],b[1]):continue
            o=[cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)]
            if o[0]*o[1]<=0 and o[2]*o[3]<=0:
                shared={a,b}&{c,d}
                assert len(shared)==1,(label,'crossing',eid,fid)
                p=next(iter(shared))
                assert (eid==fid and abs(idx-jdx)==1)or p in {tuple(nodes[k])for k in ends&fends},(label,'unmerged',eid,fid)
                if all(v==0 for v in o):
                    aa=next(v for v in (a,b)if v!=p);bb=next(v for v in(c,d)if v!=p)
                    assert sum((aa[k]-p[k])*(bb[k]-p[k])for k in(0,1))<=0,(label,'overlap',eid,fid)
    need(label+' segment pairs without unmerged intersections',True,pairs)
    pending=set(nodes);components=0
    while pending:
        components+=1;stack=[pending.pop()]
        while stack:
            for v in adj[stack.pop()]:
                if v in pending:pending.remove(v);stack.append(v)
    # Independent half-edge ordering uses the outgoing first sampled tangent.
    for u,vs in adj.items():vs.sort(key=lambda v:math.atan2(directed[u,v][1][1]-nodes[u][1],directed[u,v][1][0]-nodes[u][0]))
    seen=set();faces=[]
    for start in directed:
        if start in seen:continue
        uv=start;cycle=[];polygon=[]
        while uv not in seen:
            seen.add(uv);u,v=uv;cycle.append(u);polygon+=directed[u,v][:-1]
            ns=adj[v];uv=(v,ns[(ns.index(u)-1)%len(ns)])
        assert uv==start
        area=sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(polygon,polygon[1:]+polygon[:1]))/2
        if area>0:faces.append((cycle,polygon,area))
    def canonical(c):return min(tuple(c[i:]+c[:i])for i in range(len(c)))
    recorded={canonical(f['nodeCycle']):f for f in g['boundedFaceGeometry']}
    need(label+' complete face coverage',len(recorded)==len(g['boundedFaceGeometry'])==len(faces)
         and set(recorded)=={canonical(c)for c,_,_ in faces})
    for c,p,a in faces:
        f=recorded[canonical(c)]
        # Both arrays must preserve all sampled vertices, allowing only a cyclic start.
        need(label+' face '+','.join(c),canonical(f['polygon'])==canonical(p)
             and math.isclose(f['centrelineEnclosedPixels2'],a,abs_tol=1e-8))
    stats={'nodes':len(nodes),'edges':len(edges),'components':components,'segments':len(lines),
           'segmentPairsExamined':pairs,'boundedFaces':len(faces),'unexpectedIntersections':[]}
    need(label+' recorded statistics',g['statistics']==stats and components==1)
    need(label+' Euler identity',len(faces)==len(edges)-len(nodes)+components)
    return stats


def verify_route(g,r,label):
    es={e['id']:e for e in g['edges']};sequence=r['nodeSequence'];ids=r['edgeIds'];points=[];length=0
    need(label+' path shape',len(sequence)==len(ids)+1 and sequence[0]==r['from']and sequence[-1]==r['to'])
    for u,v,eid in zip(sequence,sequence[1:],ids):
        e=es[eid];need(label+' allowed '+eid,e['navigationAllowed']and eid!=r['excludedEdge']and {u,v}=={e['from'],e['to']})
        ps=e['points']if u==e['from']else e['points'][::-1]
        points+=ps if not points else ps[1:];length+=sum(math.dist(a,b)for a,b in zip(ps,ps[1:]))
    need(label+' all sampled points and length',points==r['points']and math.isclose(length,r['lengthPixels'],abs_tol=1e-8))
    # Bellman-Ford relaxation uses recomputed weights, independent of the builder's Dijkstra.
    d={n:math.inf for n in g['nodes']};d[r['from']]=0
    for _ in range(len(d)-1):
        changed=False
        for e in es.values():
            if not e['navigationAllowed']or e['id']==r['excludedEdge']:continue
            w=sum(math.dist(a,b)for a,b in zip(e['points'],e['points'][1:]))
            for u,v in [(e['from'],e['to']),(e['to'],e['from'])]:
                if d[v]>d[u]+w:d[v]=d[u]+w;changed=True
        if not changed:break
    need(label+' shortest in stated graph',math.isclose(r['lengthPixels'],d[r['to']],abs_tol=1e-8)
         and r['metres']is None and r['geometricBidirectionalAssumption']is True)


def properties(obj):
    ps=obj.get('properties',[]);need('property names unique '+obj.get('name','map'),len({p['name']for p in ps})==len(ps))
    need('property JSON types '+obj.get('name','map'),all(
        (p['type']=='bool'and type(p['value'])is bool)or
        (p['type']=='float'and type(p['value'])in(float,int))or
        (p['type']=='string'and type(p['value'])is str)for p in ps))
    return {p['name']:(p['type'],p['value'])for p in ps}


def typed(values):
    return {k:('bool'if isinstance(v,bool)else 'float'if isinstance(v,float)else 'string',v)for k,v in values.items()}


def line_object(obj,points,values,label):
    need(label+' geometry and all vertices',obj['type']=='pixel-polyline'and obj['rotation']==0 and obj['visible']is True
         and obj['width']==obj['height']==0 and len(obj['polyline'])==len(points)
         and [[obj['x']+p['x'],obj['y']+p['y']]for p in obj['polyline']]==points)
    need(label+' full typed property coverage',properties(obj)==typed(values))


def verify_tmj(rel,g,expected_images,design=False):
    m=read(rel);layers=m['layers'];need(rel+' map dimensions',m['width']==g['nativeSize'][0]and m['height']==g['nativeSize'][1]
       and m['tilewidth']==m['tileheight']==1 and m['orientation']=='orthogonal'and m['tilesets']==[])
    imgs=[x for x in layers if x['type']=='imagelayer']
    need(rel+' exact image coverage',len(imgs)==len(expected_images))
    for l,(name,path,w,h,x,y)in zip(imgs,expected_images):
        need(rel+' image '+name,(l['name'],l['image'],l['imagewidth'],l['imageheight'],l['offsetx'],l['offsety'])==(name,path,w,h,x,y)
             and l['visible']is True and l['locked']is True and l['opacity']==1)
        need(rel+' image resolves '+name,(HERE/rel).parent.joinpath(path).resolve().is_file())
    groups={l['name']:l for l in layers if l['type']=='objectgroup'}
    expected_names={'visible-asphalt-trace'}|{k+'-route'for k in g.get('routes',{})}|({'design-only-hidden-not-navigation'}if design else set())
    need(rel+' group coverage',set(groups)==expected_names and len(groups)+len(imgs)==len(layers))
    roads=groups['visible-asphalt-trace'];objs={o['name']:o for o in roads['objects']}
    need(rel+' full edge name coverage',len(objs)==len(roads['objects'])==len(g['edges'])and set(objs)=={e['id']for e in g['edges']}and roads['visible']is True)
    for e in g['edges']:
        values={k:e[k]for k in ['from','to','lengthPixels','navigationAllowed','surfaceObservation','bidirectionalAssumption','trafficVerified']}
        line_object(objs[e['id']],e['points'],values,rel+' '+e['id'])
    for k,r in g.get('routes',{}).items():
        l=groups[k+'-route'];need(rel+' hidden route '+k,l['visible']is False and len(l['objects'])==1 and l['objects'][0]['name']==k)
        line_object(l['objects'][0],r['points'],{'lengthPixels':r['lengthPixels'],'trafficVerified':False},rel+' route '+k)
    if design:
        l=groups['design-only-hidden-not-navigation'];ds=read('structure-guide.json')['roads'];objs={o['name']:o for o in l['objects']}
        need(rel+' design hidden and complete',l['visible']is False and len(objs)==len(ds)==len(l['objects'])and set(objs)=={e['id']for e in ds})
        for e in ds:line_object(objs[e['id']],e['points'],{'designOnly':True,'navigationAllowed':False,'kind':e['kind']},rel+' design '+e['id'])
    allobjects=[o for l in groups.values()for o in l['objects']]
    need(rel+' layer and object IDs',len({l['id']for l in layers})==len(layers)and sorted(l['id']for l in layers)==list(range(1,m['nextlayerid']))
         and sorted(o['id']for o in allobjects)==list(range(1,m['nextobjectid'])))
    need(rel+' diagnostic map properties',properties(m)==typed({'unit':'native pixels','metreCalibration':'unestablished','fullStreetInventoryComplete':False,
         'trafficVerified':False,'formalGameTests':False,'ordinaryRegionAdmitted':False,'evidenceScope':'partial visible-asphalt trace; not a full city street inventory',
         'assemblyStatus':'diagnostic; shared-building ownership unresolved'if len(imgs)>1 else 'single native source; no completed seam claim',
         'wholeSeamRegistrationComplete':False,'completeObjectOwnershipResolved':False}))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--read-only',action='store_true');args=parser.parse_args()
    result=read('result.json');new=Image.open(HERE/'native.png');old=Image.open(HERE.parent/'organic-layout-004/native.png')
    need('005 exact original bytes and declared size',sha(HERE/'native.png')==result['sha256']=='e7f8394a9f9b83d907fea7587f5a725348baa2f13df6edf155ebb637ff5775cc'
         and(HERE/'native.png').read_bytes()==Path(result['toolDefaultOutputPath']).read_bytes()
         and list(new.size)==result['actualSize']==[1671,941]and new.mode==result['modeRGB']=='RGB'and(HERE/'native.png').stat().st_size==result['bytes'])
    need('004 original retained',sha(HERE.parent/'organic-layout-004/native.png')=='dd6390062ddd54d1270dc0b2c3e86b49d2ff45abd9191b93ad6e6fd791ffbc30'and old.size==(1672,941))
    for r in read('input-fingerprints.json'):
        p=ROOT/r['path'];need('input '+r['path'],sha(p)==r['sha256']and p.stat().st_size==r['bytes']and list(Image.open(p).size)==r['size'])
    need('reference crop exact',ImageChops.difference(old.crop((0,0,152,941)),Image.open(HERE/'references/004-west-edge.png')).getbbox()is None)
    pair=Image.open(HERE/'assembly/pair-diagnostic.png')
    need('diagnostic exact source crops',pair.size==(3192,941)and ImageChops.difference(pair.crop((0,0,1520,941)),new.crop((0,0,1520,941))).getbbox()is None
         and ImageChops.difference(pair.crop((1520,0,3192,941)),old).getbbox()is None)
    aa=new.crop((1520,0,1671,941));bb=old.crop((0,0,151,941))
    a=list(zip(*[iter(aa.tobytes())]*3));b=list(zip(*[iter(bb.tobytes())]*3))
    exact=sum(x==y for x,y in zip(a,b));error=sum(abs(u-v)for x,y in zip(a,b)for u,v in zip(x,y))/(len(a)*3)
    strip=read('verification/shared-strip-identity.json')
    need('shared strip disclosed as redrawn',exact==strip['pixelsExactlyEqual']==48 and len(a)==strip['pixels']==142091
         and math.isclose(error,strip['meanAbsoluteRGBError'],abs_tol=1e-12)and strip['fullSeamReady']is False)
    w=read('actual-005-graph.json');e=read('004-main-trace.json');p=read('actual-pair-graph.json')
    stats={k:geometry(g,k)for k,g in [('005',w),('004-partial',e),('pair',p)]}
    need('four traced blocks plus one island',sum(f['classification']=='visible-street-block-enclosure'for f in w['boundedFaceGeometry'])==w['demonstratedStreetBlockEnclosures']==4
         and sum(f['classification']=='channelizing-island-no-buildings'for f in w['boundedFaceGeometry'])==1
         and w['visualInventory']['observedBuildingBearingEnclosures']==5 and w['visualInventory']['exclusiveNewBlockOwnershipResolved']is False)
    need('all graphs remain partial and uncalibrated',all(g['fullStreetInventoryComplete']is False and g['metreCalibration']is None and g['trafficVerified']is False for g in(w,e,p)))
    need('pair remains diagnostic',p['wholeSeamRegistrationComplete']is False and p['completeObjectOwnershipResolved']is False and p['formalMapAdmission']is False)
    for prefix,g,dx in [('W',w,0),('E',e,1520)]:
        for k,point in g['nodes'].items():
            key='join-main'if k=='MP'else prefix+'-'+k
            need('pair node offset once '+key,p['nodes'][key]==[point[0]+dx,point[1]])
        pes={x['id']:x for x in p['edges']}
        for ed in g['edges']:
            q=pes[prefix+'-'+ed['id']]
            expected={**ed,'id':prefix+'-'+ed['id'],'from':'join-main'if ed['from']=='MP'else prefix+'-'+ed['from'],
                      'to':'join-main'if ed['to']=='MP'else prefix+'-'+ed['to'],'points':[[x+dx,y]for x,y in ed['points']],
                      'sourceRegion':prefix,'offsetAppliedOnce':[dx,0]}
            need('pair entire edge '+ed['id'],q==expected)
    need('pair has exactly combined edges and one shared node',len(p['edges'])==len(w['edges'])+len(e['edges'])and len(p['nodes'])==len(w['nodes'])+len(e['nodes'])-1)
    for name,g in [('005',w),('pair',p)]:
        for kind,r in g['routes'].items():verify_route(g,r,name+' '+kind)
    need('specified reroute exclusion',w['routes']['alternative']['excludedEdge']=='M1--ML'and p['routes']['alternative']['excludedEdge']=='W-M1--ML')
    cs=read('contacts.json');need('contact scope',cs['translation005RelativeTo004']==[-1520,0]and cs['wholeSeamRegistrationComplete']is False and cs['contactCentrelineResidualPixels']is None and len(cs['contacts'])==3)
    for c in cs['contacts']:
        need('contact '+c['id'],c['point005']==[1520,c['point004'][1]]and c['point004'][0]==0 and c['pointPair']==c['point005']
             and c['nativeRGB005']==list(new.getpixel(tuple(c['point005'])))and c['nativeRGB004']==list(old.getpixel(tuple(c['point004']))))
    verify_tmj('tiled/native005.tmj',w,[('005-native','../native.png',1671,941,0,0)],True)
    verify_tmj('tiled/native004-partial.tmj',e,[('004-native','../../organic-layout-004/native.png',1672,941,0,0)])
    verify_tmj('tiled/organic-pair.tmj',p,[('005-native','../native.png',1671,941,0,0),('004-native','../../organic-layout-004/native.png',1672,941,1520,0)])
    data=read('viewer-data.json');need('viewer exact graph data',data['graphs']=={'005':w,'004':e,'pair':p}and data['contacts']==cs)
    expected=(HERE/'viewer-template.html').read_text().replace('__VIEWER_DATA__',json.dumps(data,ensure_ascii=False))
    need('viewer generated from current data',expected==(HERE/'index.html').read_text())
    for rel,r in read('generated-files.json').items():need('owned output '+rel,sha(HERE/rel)==r['sha256']and(HERE/rel).stat().st_size==r['bytes'])
    snap=json.loads((ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json').read_text())
    for rel,r in snap['files'].items():need('protected '+rel,(ROOT/rel).is_file()and sha(ROOT/rel)==r['sha256']and(ROOT/rel).stat().st_size==r['bytes'])
    report={'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'passed-bounded-evidence-only','checkCount':len(CHECKS),
            'checks':CHECKS,'graphStatistics':stats,'protectedFilesMatched':len(snap['files']),
            'fullStreetInventoryComplete':False,'wholeSeamReady':False,'objectOwnershipResolved':False,'userArtApproved':False,
            'ordinaryRegionAdmitted':False,'formalGameTestsPerformed':False,'visualAsphaltInspectionCertifiedByThisScript':False}
    if not args.read_only:(HERE/'verification/static-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='checks'},ensure_ascii=False))


if __name__=='__main__':main()
