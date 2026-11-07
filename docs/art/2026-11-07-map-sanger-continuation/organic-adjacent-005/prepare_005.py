"""One-time preparation of a pixel design and necessary local seam evidence."""
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[3]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def new_json(p, d):
    with p.open('x') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write('\n')


def bezier(a, c, d, b):
    return [[round((1-t)**3*a[k]+3*(1-t)**2*t*c[k]+3*(1-t)*t*t*d[k]+t**3*b[k], 5)
             for k in (0, 1)] for t in [i/16 for i in range(17)]]


def area(ps):
    return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(ps,ps[1:]+ps[:1]))/2


def inspect_graph(roads):
    outgoing=defaultdict(list); directed={}; seg=[]
    for e in roads:
        for u,v,ps in [(e['from'],e['to'],e['points']), (e['to'],e['from'],e['points'][::-1])]:
            outgoing[u].append((math.atan2(ps[1][1]-ps[0][1],ps[1][0]-ps[0][0]),v))
            directed[u,v]=ps
        for i,(a,b) in enumerate(zip(e['points'],e['points'][1:])):
            seg.append((e['id'],i,tuple(round(v*100000) for v in a),tuple(round(v*100000) for v in b)))
    nodes={e['from']:tuple(round(v*100000) for v in e['points'][0]) for e in roads}
    nodes.update({e['to']:tuple(round(v*100000) for v in e['points'][-1]) for e in roads})
    ends={e['id']:{e['from'],e['to']} for e in roads}
    orient=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    pairs=0
    for i,(eid,ix,a,b) in enumerate(seg):
        for fid,jx,c,d in seg[i+1:]:
            pairs+=1
            if max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]) or max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1]): continue
            o=[orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)]
            if o[0]*o[1]<=0 and o[2]*o[3]<=0:
                shared=set((a,b))&set((c,d))
                assert len(shared)==1,(eid,ix,fid,jx,'intersection')
                pt=next(iter(shared))
                assert (eid==fid and abs(ix-jx)==1) or pt in {nodes[n] for n in ends[eid]&ends[fid]},(eid,fid,'unmerged')
                if all(v==0 for v in o):
                    aa=next(p for p in (a,b) if p!=pt);bb=next(p for p in (c,d) if p!=pt)
                    assert (aa[0]-pt[0])*(bb[0]-pt[0])+(aa[1]-pt[1])*(bb[1]-pt[1])<=0,'overlap'
    for a in outgoing.values():a.sort()
    seen=set();faces=[]
    for start in directed:
        if start in seen:continue
        edge=start;ps=[];cycle=[]
        while edge not in seen:
            seen.add(edge);u,v=edge;cycle.append(u);ps+=directed[u,v][:-1]
            ns=[n for _,n in outgoing[v]];edge=(v,ns[(ns.index(u)-1)%len(ns)])
        assert edge==start
        if area(ps)>1e-6:faces.append({'nodeCycle':cycle,'polygon':ps,'designEnclosedPixels2':area(ps)})
    assert len(faces)==6,len(faces)
    return faces,{'nodes':len(outgoing),'edges':len(roads),'sampledSegments':len(seg),'segmentPairsChecked':pairs,'boundedFaces':len(faces),'unexpectedIntersections':[],'coordinateUnit':'design pixels only'}


def main():
    assert ROOT==Path('/Users/sanger/Documents/ChatGPT/taptap 2')
    assert sha(BASE/'organic-layout-004/native.png')=='dd6390062ddd54d1270dc0b2c3e86b49d2ff45abd9191b93ad6e6fd791ffbc30'
    assert json.loads((BASE/'organic-layout-004/user-review-001.json').read_text())['userArtApproved']
    crop=Image.open(HERE/'references/004-west-edge.png')
    assert crop.tobytes()==Image.open(BASE/'organic-layout-004/native.png').crop((0,0,152,941)).tobytes()
    ns={'NW':(0,160),'N1':(300,190),'N2':(720,148),'N3':(1080,212),'N4':(1340,318),'NP':(1520,224),
        'MW':(0,545),'M1':(365,550),'T1':(635,475),'M2':(780,432),'M3':(1150,478),'T2':(1255,495),'M4':(1460,500),'MP':(1520,489),
        'SW':(0,838),'S1':(245,820),'S2':(630,715),'S3':(1010,790),'S4':(1370,550),'SP':(1520,636),
        'NT':(600,0),'ST':(930,941)}
    specs=[
        ('NW','N1',(100,180),(200,185),'collector'),('N1','N2',(440,205),(565,120),'collector'),
        ('N2','N3',(860,128),(955,165),'collector'),('N3','N4',(1160,250),(1220,325),'collector'),
        ('N4','NP',(1420,325),(1480,250),'collector'),
        ('MW','M1',(110,548),(240,565),'primary'),('M1','T1',(470,550),(540,505),'primary'),
        ('T1','M2',(690,455),(730,433),'primary'),('M2','M3',(895,430),(1025,460),'primary'),
        ('M3','T2',(1185,480),(1220,490),'primary'),('T2','M4',(1325,503),(1390,504),'primary'),
        ('M4','MP',(1480,499),(1500,495),'primary'),
        ('SW','S1',(80,845),(180,843),'local'),('S1','S2',(400,795),(485,718),'local'),
        ('S2','S3',(770,705),(870,785),'collector'),('S3','S4',(1160,770),(1250,625),'collector'),
        ('S4','SP',(1440,555),(1465,586),'collector'),
        ('N1','M1',(270,340),(350,420),'local'),('N2','T1',(660,245),(595,345),'local'),
        ('N3','M3',(1010,310),(1030,420),'collector'),('N4','M4',(1355,393),(1410,450),'local'),
        ('M1','S1',(380,640),(305,735),'collector'),('M2','S2',(792,555),(706,638),'local'),
        ('T2','S3',(1265,615),(1150,740),'local'),('M4','S4',(1445,520),(1400,537),'local'),
        ('NT','N2',(590,60),(665,100),'collector'),('S3','ST',(970,835),(955,900),'collector')]
    roads=[{'id':f'{a}-{b}','from':a,'to':b,'kind':kind,'points':bezier(ns[a],c,d,ns[b])} for a,b,c,d,kind in specs]
    faces,check=inspect_graph(roads)
    purposes=[('compact mixed housing','#d1dbcd'),('community library and street shops','#d2dbe0'),('small urban workshops and services','#dccfbe'),('housing of different footprints','#d4ddcf'),('mixed residential and offices','#d1d7d8'),('neighbourhood retail and low homes','#dacec1')]
    # Half-edge traversal orders the faces by first encountered source road.
    for i,(f,(purpose,color)) in enumerate(zip(faces,purposes),1):f.update(id=f'W005-{i:02}',purpose=purpose,color=color)
    data={'recordedAt':datetime.now(timezone.utc).isoformat(),'canvas':[1672,941],'coordinateUnit':'design source pixels; no metres',
          'nodes':{k:list(v) for k,v in ns.items()},'roads':roads,'blocks':faces,'roadHierarchyWidths':{'primary':59,'collector':39,'local':29},
          'eastReferenceStrip':{'crop':[0,0,152,941],'destination':[1520,0],'source':'../organic-layout-004/native.png'},
          'proposedTranslationRelativeTo004':[-1520,0],'actualTracing':False,'completeBlockCountInGeneratedImage':None,'metreCalibration':None}
    new_json(HERE/'structure-guide.json',data);new_json(HERE/'structure-check.json',check)
    im=Image.new('RGB',(1672,941),'#d9dfd2');draw=ImageDraw.Draw(im)
    for f in faces:draw.polygon([tuple(p) for p in f['polygon']],fill=f['color'])
    for extra,col in [(12,'#bfc5bf'),(0,'#6b7174')]:
        for e in roads:
            w=data['roadHierarchyWidths'][e['kind']]+extra;ps=[tuple(p) for p in e['points']]
            draw.line(ps,fill=col,width=w,joint='curve')
            for x,y in (ps[0],ps[-1]):draw.ellipse((x-w/2,y-w/2,x+w/2,y+w/2),fill=col)
    # Only a reference guide uses this native-pixel strip; no final artwork is composited here.
    im.paste(crop,(1520,0))
    with (HERE/'structure-input.png').open('xb') as f:im.save(f,format='PNG')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1672 941">','<rect width="1672" height="941" fill="#d9dfd2"/>']
    for f in faces:svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in f['polygon'])+f'" fill="{f["color"]}"/>')
    for extra,col in [(12,'#bfc5bf'),(0,'#6b7174')]:
        for e in roads:svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in e['points'])+f'" fill="none" stroke="{col}" stroke-width="{data["roadHierarchyWidths"][e["kind"]]+extra}" stroke-linecap="round" stroke-linejoin="round"/>')
    svg.append('<image href="references/004-west-edge.png" x="1520" y="0" width="152" height="941"/>');svg.append('</svg>')
    with (HERE/'structure-input.svg').open('x') as f:f.write('\n'.join(svg))
    new_json(HERE/'authorization.json',{'source':'current direct user message','threadId':'thr_fs5qphhxgc','quote':'这版地图认可，做的还不错，继续吧。','approved004':'../organic-layout-004/user-review-001.json','oneAdjacentImageAuthorized':True,'targetAreaRatioToLegacy25':0.25,'formalGameTestsAuthorized':False,'noCredentialOrBackendChanges':True})
    print(json.dumps(check,ensure_ascii=False))


if __name__=='__main__':main()
