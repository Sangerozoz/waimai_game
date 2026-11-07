"""Read isolated pair files and write a reproducible evidence report, no game run."""
import hashlib
import itertools
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CHECKS = []


def check(name, ok, details=None):
    CHECKS.append({'name':name,'passed':bool(ok),'details':details})
    assert ok, (name,details)


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def connected(g, excluded=None):
    adj=defaultdict(set)
    for e in g['edges']:
        if e['id']!=excluded:
            adj[e['from']].add(e['to']);adj[e['to']].add(e['from'])
    seen=set(); stack=[g['nodes'][0]['id']]
    while stack:
        n=stack.pop()
        if n in seen:continue
        seen.add(n);stack.extend(adj[n]-seen)
    return len(seen)==len(g['nodes'])


def cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def on(a,b,c):
    return cross(a,b,c)==0 and all(min(a[i],b[i])<=c[i]<=max(a[i],b[i]) for i in (0,1))


def intersect(a,b,c,d):
    ab_c,ab_d,cd_a,cd_b=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
    return ((ab_c>0>ab_d or ab_d>0>ab_c) and (cd_a>0>cd_b or cd_b>0>cd_a)) or any([
        ab_c==0 and on(a,b,c),ab_d==0 and on(a,b,d),cd_a==0 and on(c,d,a),cd_b==0 and on(c,d,b)])


def graph_geometry(g):
    nodes={n['id']:tuple(Fraction(v) for v in n['pixel']) for n in g['nodes']}
    check('unique nodes',len(nodes)==len(g['nodes']))
    check('unique edge IDs',len({e['id'] for e in g['edges']})==len(g['edges']))
    segments=[]
    for e in g['edges']:
        pts=[tuple(Fraction(v)for v in p)for p in e['points']]
        check(e['id']+' endpoints',pts[0]==nodes[e['from']] and pts[-1]==nodes[e['to']])
        distance=sum(math.dist(a,b)for a,b in zip(pts,pts[1:]))
        check(e['id']+' length',math.isclose(distance,e['lengthPixels'],abs_tol=1e-9))
        for i,(a,b)in enumerate(zip(pts,pts[1:])):
            check(e['id']+f' segment{i} nonzero',a!=b)
            segments.append((e,i,a,b))
    invalid=[];examined=0
    for (e,i,a,b),(f,j,c,d) in itertools.combinations(segments,2):
        examined+=1
        if not intersect(a,b,c,d):continue
        allowed={nodes[n]for n in {e['from'],e['to']}&{f['from'],f['to']}}
        if e['id']==f['id'] and abs(i-j)==1:allowed|={a,b}&{c,d}
        touches={p for p in (a,b,c,d) if on(a,b,p)and on(c,d,p)}
        overlap=cross(a,b,c)==0 and cross(a,b,d)==0 and len(touches)>1
        if overlap or not touches or not touches<=allowed:invalid.append([e['id'],i,f['id'],j])
    check('no unmerged crossings or overlaps',not invalid,{'examinedSegmentPairs':examined,'invalid':invalid})
    check('connected',connected(g))
    check('all single-edge exclusions stay connected',all(connected(g,e['id'])for e in g['edges']))
    return examined


def shortest_distance(g,start,goal,excluded):
    # Bellman-Ford is intentionally independent of the builder's Dijkstra implementation.
    dist={n['id']:float('inf')for n in g['nodes']};dist[start]=0
    for _ in range(len(g['nodes'])-1):
        changed=False
        for e in g['edges']:
            if e['id']==excluded:continue
            for a,b in [(e['from'],e['to']),(e['to'],e['from'])]:
                d=dist[a]+e['lengthPixels']
                if d<dist[b]:dist[b]=d;changed=True
        if not changed:break
    return dist[goal]


def check_route(g,r):
    byid={e['id']:e for e in g['edges']};n=r['start'];points=[];distance=0
    for eid in r['edgeIds']:
        e=byid[eid];check(eid+' route continuity',n in (e['from'],e['to']))
        p=e['points']if n==e['from']else list(reversed(e['points']))
        points+=p[bool(points):];distance+=e['lengthPixels'];n=e['to']if n==e['from']else e['from']
    check('route endpoint and exact coordinates',n==r['goal']and points==r['points'])
    check('excluded route edge absent',r['excludedEdge']not in r['edgeIds'])
    independent=shortest_distance(g,r['start'],r['goal'],r['excludedEdge'])
    check('independent shortest path distance',math.isclose(distance,r['lengthPixels'],abs_tol=1e-8)and math.isclose(distance,independent,abs_tol=1e-8))


def area(poly):
    return abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1])))/2


def bounded_faces(g):
    lookup={n['id']:n['pixel']for n in g['nodes']};adj=defaultdict(list)
    for e in g['edges']:
        adj[e['from']].append((e['to'],e['points']))
        adj[e['to']].append((e['from'],list(reversed(e['points']))))
    for n,values in adj.items():values.sort(key=lambda v:math.atan2(v[1][1][1]-lookup[n][1],v[1][1][0]-lookup[n][0]))
    visited=set();faces=[]
    for a,links in adj.items():
        for b,_ in links:
            if(a,b)in visited:continue
            start=(a,b);u,v=a,b;points=[]
            while(u,v)not in visited:
                visited.add((u,v));p=next(p for n,p in adj[u]if n==v);points+=p[bool(points):]
                reverse=next(i for i,(n,p)in enumerate(adj[v])if n==u)
                u,v=v,adj[v][(reverse-1)%len(adj[v])][0]
            check('half-edge face closes',(u,v)==start)
            poly=points[:-1]
            signed=sum(x[0]*y[1]-x[1]*y[0]for x,y in zip(poly,poly[1:]+poly[:1]))/2
            if signed>0:faces.append(poly)
    return faces


def roundtrip(p,g,blocks,route_data=None):
    d=read(p);ids=[o['id']for l in d['layers']if l['type']=='objectgroup'for o in l['objects']]
    check(p.name+' unique IDs',len(ids)==len(set(ids)))
    road_layer=next(l for l in d['layers']if l['name']=='traced-roads')
    objects=road_layer['objects'];expected={e['id']:e for e in g['edges']}
    check(p.name+' complete road-name coverage',len(objects)==len(expected)and{e['name']for e in objects}==set(expected))
    for o in objects:
        e=expected[o['name']];coords=[[o['x']+q['x'],o['y']+q['y']]for q in o['polyline']]
        values={p['name']:p['value']for p in o['properties']}
        check(p.name+' '+o['name']+' all vertices/properties',coords==e['points']and values=={
            'from':e['from'],'to':e['to'],'lengthPixels':e['lengthPixels'],'bidirectionalAssumption':True,'trafficVerified':False})
    land=next(l for l in d['layers']if l['name']=='owned-complete-blocks')
    check(p.name+' complete block coverage',len(land['objects'])==len(blocks)and{o['name']for o in land['objects']}=={b['id']for b in blocks})
    for o in land['objects']:
        b=next(b for b in blocks if b['id']==o['name']);poly=[[o['x']+q['x'],o['y']+q['y']]for q in o['polygon']]
        check(p.name+' '+b['id']+' polygon exact',poly==b['polygonPixels'])
    if route_data:
        for name,r in route_data.items():
            objects=next(l for l in d['layers']if l['name']==name)['objects']
            check(name+' single object',len(objects)==1)
            o=objects[0];poly=[[o['x']+q['x'],o['y']+q['y']]for q in o['polyline']]
            check(name+' all coordinates exact',poly==r['points'])


def main():
    assembly=read(HERE/'assembly-record.json');g=read(HERE/'actual-pair-graph.json');blocks=read(HERE/'actual-blocks.json')
    natives={k:Image.open(HERE/k/'native.png').convert('RGB')for k in ('W','E')}
    for k,im in natives.items():
        result=read(HERE/k/'result.json');original=Path(result['toolDefaultOutputPath'])
        check(k+' real native size/mode',im.size==(1672,941)and Image.open(HERE/k/'native.png').mode=='RGB')
        check(k+' real hash/bytes',sha(HERE/k/'native.png')==result['sha256']and(HERE/k/'native.png').stat().st_size==result['bytes'])
        check(k+' copied tool bytes exact',sha(original)==result['sha256'])
        core=Image.open(HERE/'assembly'/f'{k}-native-core.png').convert('RGB');crop=im.crop(assembly['sourceCropBoxes'][k])
        check(k+' ownership crop pixel exact',core.size==crop.size and ImageChops.difference(core,crop).getbbox()is None)
    joined=Image.open(HERE/'assembly/pair-native-pixels.png').convert('RGB')
    check('assembly actual size',joined.size==tuple(assembly['assemblySize']))
    for k,offset in assembly['coreOffsetsInAssembly'].items():
        core=Image.open(HERE/'assembly'/f'{k}-native-core.png').convert('RGB')
        crop=joined.crop([*offset,offset[0]+core.width,offset[1]+core.height])
        check(k+' assembly source pixels exact',crop.size==core.size and ImageChops.difference(core,crop).getbbox()is None)
    examined=graph_geometry(g)
    for k in ('W','E'):graph_geometry(read(HERE/k/'actual-graph.json'))
    check('pair has twelve bounded faces',len(g['edges'])-len(g['nodes'])+1==12)
    faces=bounded_faces(g)
    check('independent planar face count',len(faces)==12,{'count':len(faces)})
    check('all block areas match actual graph faces',all(math.isclose(a,b,abs_tol=1e-6)for a,b in zip(sorted(map(area,faces)),sorted(area(b['polygonPixels'])for b in blocks))))
    check('twelve unique owned blocks',len(blocks)==12 and len({b['id']for b in blocks})==12)
    plan=read(HERE/'pair-plan.json')
    check('all planned full-block names covered',{b['id']for b in blocks}=={b['id']for r in plan['regions'].values()for b in r['blocks']})
    for r in g['routes'].values():check_route(g,r)
    roundtrip(HERE/'tiled/adjacent-pair.tmj',g,blocks,g['routes'])
    for k in ('W','E'):
        own=[b for b in blocks if b['region']==k]
        if k=='E':
            dx,dy=assembly['singleEOriginalTranslationIntoW'];own=[{**b,'polygonPixels':[[p[0]-dx,p[1]-dy]for p in b['polygonPixels']]}for b in own]
        roundtrip(HERE/f'tiled/{k}-native.tmj',read(HERE/k/'actual-graph.json'),own)
    for r in assembly['sharedJunctionMismatches']:
        check(r['id']+' unhidden mismatch',r['delta']==[r['ERegisteredPixel'][i]-r['WPixel'][i]for i in(0,1)]and math.isclose(r['distancePixels'],math.dist(r['WPixel'],r['ERegisteredPixel']),abs_tol=1e-9)and not r['mergedOrSnapped'])
    check('no fake scope or production claim',assembly['metreCalibration']is None and assembly['wholeCityCoverageFraction']is None and assembly['finalImageCount']is None and not assembly['ordinaryRegionAdmitted']and not assembly['formalGameTestsPerformed'])
    protected=read(ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json')
    bad=[n for n,r in protected['files'].items()if not(ROOT/n).is_file()or sha(ROOT/n)!=r['sha256']]
    check('all protected sources unchanged',not bad,{'matched':len(protected['files'])-len(bad),'mismatched':bad})
    report={'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','checks':CHECKS,
            'checkCount':len(CHECKS),'pairSegmentPairsExamined':examined,'independentBoundedFaces':len(faces),
            'nativeFiles':{k:{'sha256':sha(HERE/k/'native.png'),'size':list(im.size)}for k,im in natives.items()},
            'protectedFilesMatched':len(protected['files']),'formalGameTestsPerformed':False,
            'visualRoadAndBuildingSemanticsNotEstablishedByTheseChecks':True}
    out=HERE/'verification/static-checks.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('checks','nativeFiles')},ensure_ascii=False))


if __name__=='__main__':main()
