"""Build a bounded, visible-road navigation sample; no game or legacy writes."""
import hashlib
import heapq
import json
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def graph(nodes, specs, source, size):
    edges=[]
    for u,v,mids in specs:
        ps=[nodes[u],*mids,nodes[v]]
        edges.append({'id':u+'--'+v,'from':u,'to':v,'points':ps,
                      'lengthPixels':sum(math.dist(a,b) for a,b in zip(ps,ps[1:])),
                      'navigationAllowed':True,'surfaceObservation':'visible-asphalt-manual-trace',
                      'bidirectionalAssumption':True,'trafficVerified':False})
    return {'source':source,'nativeSize':size,'coordinateUnit':'native source pixels',
            'nodes':nodes,'edges':edges,'metreCalibration':None,'trafficVerified':False,
            'bidirectionalAssumption':True,'fullStreetInventoryComplete':False,
            'tracePrecisionNote':'manually sampled visible asphalt, roughly 2-3px placement precision; geometric lengths are not surveying accuracy'}


def actual005():
    n={'NW':[0,159],'NT':[678,129],'ND':[1087,227],'NE':[1375,310],'NP':[1520,223],'NTop':[584,0],
       'MW':[0,550],'M1':[355,560],'ML':[606,448],'MS':[760,430],'MD':[1096,440],
       'MI':[1274,490],'ME':[1468,498],'MP':[1520,501],
       'SW':[0,841],'SL':[246,820],'SM':[640,738],'SB':[1004,817],
       'J':[1247,631],'SBranch':[1405,574],'SP':[1520,634],'SBottom':[920,941]}
    s=[
       ('NW','NT',[[105,170],[239,177],[351,167],[485,146],[596,129]]),
       ('NT','ND',[[824,131],[932,156],[1027,197]]),
       ('ND','NE',[[1181,269],[1256,295],[1317,311]]),
       ('NE','NP',[[1430,298],[1478,265]]),
       ('NTop','NT',[[585,32],[609,73],[640,104]]),
       ('NT','ML',[[681,168],[659,211],[632,263],[616,317],[610,379]]),
       ('ND','MD',[[1064,260],[1050,300],[1051,346],[1069,400]]),
       ('NE','ME',[[1380,359],[1404,410],[1437,450]]),
       ('MW','M1',[[109,558],[232,560]]),
       ('M1','ML',[[427,536],[492,509],[556,476]]),
       ('ML','MS',[[657,430],[707,426]]),
       ('MS','MD',[[854,430],[940,434],[1021,441]]),
       ('MD','MI',[[1157,460],[1215,478]]),
       ('MI','ME',[[1334,496],[1397,498]]),
       ('ME','MP',[[1494,499]]),
       ('SW','SL',[[85,847],[171,840]]),
       ('SL','SM',[[343,799],[433,765],[528,744]]),
       ('SM','SB',[[765,745],[890,785]]),
       ('SB','J',[[1090,791],[1165,713]]),
       ('J','SBranch',[[1324,580],[1365,569]]),
       ('SBranch','SP',[[1450,604]]),
       ('M1','SL',[[332,633],[290,731]]),
       ('MS','SM',[[767,470],[756,533],[723,603],[680,684]]),
       ('MI','J',[[1281,526],[1270,568]]),
       ('ME','SBranch',[[1440,532]]),
       ('SB','SBottom',[[965,877]])]
    g=graph(n,s,'native.png',[1671,941])
    g['designDeviations']=[{'designRoad':'N1-M1','actualObservation':'paved courtyard / pedestrian-scale passage between buildings, not a clearly continuous asphalt street','navigationIncluded':False},
                           {'designPlot':'narrow southeast design enclosure','actualObservation':'small channelizing island between roads; no owned buildings','countedAsStreetBlock':False}]
    return g


def partial004():
    n={'MP':[0,501],'R1':[454,453],'R2':[975,323],'R3':[1243,361],'R4':[1515,318]}
    s=[('MP','R1',[[55,480],[120,463],[208,454],[304,455],[396,460]]),
       ('R1','R2',[[500,439],[550,420],[610,400],[680,384],[752,365],[828,345],[902,329]]),
       ('R2','R3',[[1033,326],[1090,335],[1148,342],[1204,353]]),
       ('R3','R4',[[1315,362],[1380,352],[1450,337]])]
    g=graph(n,s,'../organic-layout-004/native.png',[1672,941])
    g['scope']='only the main visible street used by this bounded adjacent navigation sample;004 full tracing and block inventory remain incomplete'
    return g


def pair_graph(w,e):
    n={};edges=[]
    for prefix,g,dx in [('W',w,0),('E',e,1520)]:
        nodeid=lambda k:'join-main' if k=='MP' else prefix+'-'+k
        for k,(x,y) in g['nodes'].items():
            key=nodeid(k);p=[x+dx,y]
            if key in n:assert n[key]==p
            n[key]=p
        for ed in g['edges']:
            edges.append({**ed,'id':prefix+'-'+ed['id'],'from':nodeid(ed['from']),'to':nodeid(ed['to']),
                          'points':[[x+dx,y] for x,y in ed['points']],'sourceRegion':prefix,'offsetAppliedOnce':[dx,0]})
    return {'source':'assembly/pair-diagnostic.png','nativeSize':[3192,941],'nodes':n,'edges':edges,
            'coordinateUnit':'native diagnostic pixels','metreCalibration':None,'trafficVerified':False,
            'bidirectionalAssumption':True,'fullStreetInventoryComplete':False,
            'joinSemantics':'a common visible asphalt handoff point, not a claimed zero-residual centreline fit',
            'formalMapAdmission':False}


def analyse(g):
    n=g['nodes'];edges=g['edges'];segs=[];adj=defaultdict(list);directed={}
    for e in edges:
        assert e['points'][0]==n[e['from']] and e['points'][-1]==n[e['to']]
        for i,(a,b) in enumerate(zip(e['points'],e['points'][1:])):
            assert a!=b
            segs.append((e['id'],i,tuple(a),tuple(b)))
        for u,v,ps in [(e['from'],e['to'],e['points']),(e['to'],e['from'],e['points'][::-1])]:
            adj[u].append((math.atan2(ps[1][1]-ps[0][1],ps[1][0]-ps[0][0]),v));directed[u,v]=ps
    ori=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    endpoints={e['id']:{e['from'],e['to']} for e in edges};pairs=0
    for i,(eid,ix,a,b) in enumerate(segs):
        for fid,jx,c,d in segs[i+1:]:
            pairs+=1
            if max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]) or max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1]):continue
            o=[ori(a,b,c),ori(a,b,d),ori(c,d,a),ori(c,d,b)]
            if o[0]*o[1]<=0 and o[2]*o[3]<=0:
                shared=set((a,b))&set((c,d));assert len(shared)==1,(eid,ix,fid,jx,'intersection')
                p=next(iter(shared));assert (eid==fid and abs(ix-jx)==1) or p in {tuple(n[k]) for k in endpoints[eid]&endpoints[fid]},(eid,fid,'unmerged vertex')
                if all(v==0 for v in o):
                    aa=next(x for x in (a,b) if x!=p);bb=next(x for x in (c,d) if x!=p)
                    assert (aa[0]-p[0])*(bb[0]-p[0])+(aa[1]-p[1])*(bb[1]-p[1])<=0,'overlap'
    pending=set(n);components=0
    while pending:
        components+=1;stack=[pending.pop()]
        while stack:
            for _,v in adj[stack.pop()]:
                if v in pending:pending.remove(v);stack.append(v)
    for v in adj.values():v.sort()
    seen=set();faces=[]
    for start in directed:
        if start in seen:continue
        edge=start;cycle=[];ps=[]
        while edge not in seen:
            seen.add(edge);u,v=edge;cycle.append(u);ps+=directed[u,v][:-1]
            ns=[v for _,v in adj[v]];edge=(v,ns[(ns.index(u)-1)%len(ns)])
        assert edge==start
        a=sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(ps,ps[1:]+ps[:1]))/2
        if a>0:faces.append({'nodeCycle':cycle,'polygon':ps,'centrelineEnclosedPixels2':a})
    assert len(faces)==len(edges)-len(n)+components
    return {'nodes':len(n),'edges':len(edges),'components':components,'segments':len(segs),'segmentPairsExamined':pairs,'boundedFaces':len(faces),'unexpectedIntersections':[]},faces


def route(g,start,end,excluded=None):
    adj=defaultdict(list)
    for e in g['edges']:
        if not e['navigationAllowed'] or e['id']==excluded:continue
        adj[e['from']].append((e['to'],e));adj[e['to']].append((e['from'],e))
    q=[(0,start)];dist={start:0};prev={}
    while q:
        d,u=heapq.heappop(q)
        if d!=dist[u]:continue
        if u==end:break
        for v,e in adj[u]:
            nd=d+e['lengthPixels']
            if nd<dist.get(v,math.inf):dist[v]=nd;prev[v]=(u,e);heapq.heappush(q,(nd,v))
    assert end in dist
    nodes=[end];eds=[];ps=[];v=end
    while v!=start:
        u,e=prev[v];eds.append(e);nodes.append(u);v=u
    nodes.reverse();eds.reverse()
    for u,e in zip(nodes,eds):
        pts=e['points'] if e['from']==u else e['points'][::-1]
        ps+=pts if not ps else pts[1:]
    return {'from':start,'to':end,'excludedEdge':excluded,'nodeSequence':nodes,'edgeIds':[e['id'] for e in eds],'points':ps,'lengthPixels':dist[end],'metres':None,'geometricBidirectionalAssumption':True}


def props(d):
    return [{'name':k,'type':'bool' if isinstance(v,bool) else 'float' if isinstance(v,float) else 'string','value':v} for k,v in d.items()]


def polyobj(i,name,ps,properties):
    x,y=ps[0]
    return {'id':i,'name':name,'type':'pixel-polyline','x':x,'y':y,'width':0,'height':0,'rotation':0,'visible':True,
            'polyline':[{'x':px-x,'y':py-y} for px,py in ps],'properties':props(properties)}


def tmj(g,images,include_design=False):
    layers=[];lid=1;oid=1
    for name,image,w,h,x,y in images:
        layers.append({'id':lid,'type':'imagelayer','name':name,'image':image,'imagewidth':w,'imageheight':h,'offsetx':x,'offsety':y,'opacity':1,'visible':True,'locked':True});lid+=1
    objs=[]
    for e in g['edges']:
        objs.append(polyobj(oid,e['id'],e['points'],{k:e[k] for k in ['from','to','lengthPixels','navigationAllowed','surfaceObservation','bidirectionalAssumption','trafficVerified']}));oid+=1
    layers.append({'id':lid,'type':'objectgroup','name':'visible-asphalt-trace','draworder':'index','color':'#d22f88','visible':True,'opacity':1,'objects':objs});lid+=1
    for key,col in [('main','#148a72'),('alternative','#d8871d')]:
        if key in g.get('routes',{}):
            r=g['routes'][key];o=polyobj(oid,key,r['points'],{'lengthPixels':r['lengthPixels'],'trafficVerified':False});oid+=1
            layers.append({'id':lid,'type':'objectgroup','name':key+'-route','draworder':'index','color':col,'visible':False,'opacity':1,'objects':[o]});lid+=1
    if include_design:
        ds=json.loads((HERE/'structure-guide.json').read_text());objs=[]
        for e in ds['roads']:
            objs.append(polyobj(oid,e['id'],e['points'],{'designOnly':True,'navigationAllowed':False,'kind':e['kind']}));oid+=1
        layers.append({'id':lid,'type':'objectgroup','name':'design-only-hidden-not-navigation','draworder':'index','color':'#9aa2a1','visible':False,'opacity':1,'objects':objs});lid+=1
    return {'type':'map','version':'1.10','tiledversion':'1.12.2','orientation':'orthogonal','renderorder':'right-down','infinite':False,
            'width':g['nativeSize'][0],'height':g['nativeSize'][1],'tilewidth':1,'tileheight':1,'tilesets':[],
            'layers':layers,'nextlayerid':lid,'nextobjectid':oid,'properties':props({'unit':'native pixels','metreCalibration':'unestablished','fullStreetInventoryComplete':False,'trafficVerified':False,'formalGameTests':False,'ordinaryRegionAdmitted':False})}


def write_owned(outputs):
    manifest=HERE/'generated-files.json'
    old=json.loads(manifest.read_text()) if manifest.exists() else {}
    for rel,raw in outputs.items():
        p=HERE/rel
        if p.exists():assert rel in old and sha(p)==old[rel]['sha256'],f'Changed or unowned output: {rel}'
        p.parent.mkdir(parents=True,exist_ok=True)
    for rel,raw in outputs.items():(HERE/rel).write_bytes(raw)
    manifest.write_text(json.dumps({rel:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for rel,raw in sorted(outputs.items())},indent=2)+'\n')


def main():
    assert sha(HERE/'native.png')=='e7f8394a9f9b83d907fea7587f5a725348baa2f13df6edf155ebb637ff5775cc'
    assert sha(HERE.parent/'organic-layout-004/native.png')=='dd6390062ddd54d1270dc0b2c3e86b49d2ff45abd9191b93ad6e6fd791ffbc30'
    w=actual005();e=partial004();p=pair_graph(w,e)
    for g in [w,e,p]:g['statistics'],g['boundedFaceGeometry']=analyse(g)
    assert w['statistics']['boundedFaces']==5
    for f in w['boundedFaceGeometry']:
        island=set(f['nodeCycle'])=={'MI','ME','SBranch','J'}
        f['classification']='channelizing-island-no-buildings' if island else 'visible-street-block-enclosure'
    assert sum(f['classification']=='channelizing-island-no-buildings' for f in w['boundedFaceGeometry'])==1
    w['demonstratedStreetBlockEnclosures']=4
    p['routes']={'main':route(p,'W-MW','E-R4'),'alternative':route(p,'W-MW','E-R4','W-M1--ML')}
    assert p['routes']['main']['edgeIds']!=p['routes']['alternative']['edgeIds']
    w['routes']={'main':route(w,'MW','MP'),'alternative':route(w,'MW','MP','M1--ML')}
    contacts={'translation005RelativeTo004':[-1520,0],'sharedBandPixelExact':False,'wholeSeamRegistrationComplete':False,
              'method':'choose an observed common asphalt handoff point inside both native corridor images; this is not a zero-residual road-centreline fit',
              'contactCentrelineResidualPixels':None,'manualPixelPlacementPrecisionApprox':3,'metreCalibration':None,'contacts':[]}
    old=Image.open(HERE.parent/'organic-layout-004/native.png');new=Image.open(HERE/'native.png')
    for name,y in [('north-oblique',223),('main-curved',501),('south-oblique',634)]:
        contacts['contacts'].append({'id':name,'point005':[1520,y],'point004':[0,y],'pointPair':[1520,y],
                                    'nativeRGB005':list(new.getpixel((1520,y))),'nativeRGB004':list(old.getpixel((0,y))),
                                    'visibleAsphaltObservedInBoth':True,'crossRegionRouteUsesThis':name=='main-curved'})
    docs={'actual-005-graph.json':w,'004-main-trace.json':e,'actual-pair-graph.json':p,'contacts.json':contacts,
          'tiled/native005.tmj':tmj(w,[('005-native','../native.png',1671,941,0,0)],True),
          'tiled/native004-partial.tmj':tmj(e,[('004-native','../../organic-layout-004/native.png',1672,941,0,0)]),
          'tiled/organic-pair.tmj':tmj(p,[('005-native','../native.png',1671,941,0,0),('004-native','../../organic-layout-004/native.png',1672,941,1520,0)])}
    docs['viewer-data.json']={'graphs':{'005':w,'004':e,'pair':p},'contacts':contacts,'sourceSHA256':{'005':sha(HERE/'native.png'),'004':sha(HERE.parent/'organic-layout-004/native.png')}}
    outputs={k:(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode() for k,v in docs.items()}
    import io
    for name,g,im in [('005',w,new),('004-partial',e,old),('pair',p,Image.open(HERE/'assembly/pair-diagnostic.png'))]:
        annotated=im.copy();draw=ImageDraw.Draw(annotated)
        for ed in g['edges']:draw.line([tuple(v) for v in ed['points']],fill='#df369b',width=2)
        for k,(x,y) in g['nodes'].items():draw.ellipse((x-3,y-3,x+3,y+3),fill='#ffffff',outline='#df369b');draw.text((x+4,y+2),k,fill='#b1006d')
        buf=io.BytesIO();annotated.save(buf,format='PNG');outputs['verification/trace-overlay-'+name+'.png']=buf.getvalue()
    outputs['verification/builder-check.json']=(json.dumps({'graphs':{k:g['statistics'] for k,g in [('005',w),('004partial',e),('pair',p)]},'routes':{k:{'lengthPixels':r['lengthPixels'],'edges':r['edgeIds']} for k,r in p['routes'].items()},'005StreetBlocksDemonstrated':4,'channelizingIslandExcludedFromBlocks':True,'designOmittedRoadExcludedFromNavigation':True,'formalGameTests':False},ensure_ascii=False,indent=2)+'\n').encode()
    write_owned(outputs)
    print(json.dumps({'statistics':p['statistics'],'mainPixels':p['routes']['main']['lengthPixels'],'alternativePixels':p['routes']['alternative']['lengthPixels'],'demonstrated005Blocks':4,'004FullTraceComplete':False},ensure_ascii=False))


if __name__=='__main__':main()
