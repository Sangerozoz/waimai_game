"""Render clean design roads and independently inspect sampled segment topology."""
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent


def signed_area(ps):
    return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(ps,ps[1:]+ps[:1]))/2


def orientation(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def topology(data):
    roads=data['roads']; segments=[]
    endpoints={e['id']:{e['from']:tuple(round(x*100000) for x in e['points'][0]),
                        e['to']:tuple(round(x*100000) for x in e['points'][-1])} for e in roads}
    for road in roads:
        for i,(a,b) in enumerate(zip(road['points'],road['points'][1:])):
            a=tuple(round(x*100000) for x in a); b=tuple(round(x*100000) for x in b)
            assert a!=b
            segments.append((road['id'],i,a,b))
    pairs=0; unexpected=[]
    for i,(eid,ix,a,b) in enumerate(segments):
        for fid,jx,c,d in segments[i+1:]:
            pairs+=1
            if max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]) or max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1]):
                continue
            shared=set((a,b))&set((c,d))
            o=[orientation(a,b,c),orientation(a,b,d),orientation(c,d,a),orientation(c,d,b)]
            if o[0]*o[1]<=0 and o[2]*o[3]<=0:
                if len(shared)==1:
                    shared_point=next(iter(shared))
                    common_nodes=set(endpoints[eid])&set(endpoints[fid])
                    explicit_points={endpoints[eid][n] for n in common_nodes}
                    legitimate=(eid==fid and abs(ix-jx)==1) or (eid!=fid and shared_point in explicit_points)
                    if not legitimate:
                        unexpected.append([eid,ix,fid,jx,'unmerged-shared-vertex'])
                        continue
                    # Collinear overlap beyond the shared endpoint is forbidden too.
                    if all(x==0 for x in o):
                        s=next(iter(shared)); aa=next(p for p in (a,b) if p!=s); bb=next(p for p in (c,d) if p!=s)
                        if (aa[0]-s[0])*(bb[0]-s[0])+(aa[1]-s[1])*(bb[1]-s[1])>0:
                            unexpected.append([eid,ix,fid,jx,'overlap'])
                    continue
                unexpected.append([eid,ix,fid,jx,'intersection'])
    assert not unexpected, unexpected[:5]
    outgoing=defaultdict(list); directed={}
    for e in roads:
        for u,v,ps in [(e['from'],e['to'],e['points']),(e['to'],e['from'],list(reversed(e['points'])))]:
            angle=math.atan2(ps[1][1]-ps[0][1],ps[1][0]-ps[0][0])
            outgoing[u].append((angle,v)); directed[u,v]=ps
    for v in outgoing.values(): v.sort()
    seen=set(); faces=[]
    for start in directed:
        if start in seen: continue
        edge=start; walk=[]; poly=[]
        while edge not in seen:
            seen.add(edge); u,v=edge; walk.append(u); poly+=directed[u,v][:-1]
            neighbours=[x[1] for x in outgoing[v]]
            edge=(v,neighbours[(neighbours.index(u)-1)%len(neighbours)])
        assert edge==start
        if signed_area(poly)>0: faces.append({'nodes':walk,'area':signed_area(poly)})
    assert len(faces)==8
    assert {frozenset(f['nodes']) for f in faces}=={frozenset(b['nodeCycle']) for b in data['blocks']}
    area_errors=[abs(next(f['area'] for f in faces if set(f['nodes'])==set(b['nodeCycle']))-b['designEnclosedPixels2']) for b in data['blocks']]
    assert max(area_errors)<1e-6
    return {'segments':len(segments),'pairsExamined':pairs,'unexpectedCrossingsOrOverlaps':unexpected,
            'independentBoundedFaces':len(faces),'maximumFaceAreaErrorPx2':max(area_errors),
            'degreeHistogram':dict(Counter(len(v) for v in outgoing.values())),
            'designLargestToSmallestEnclosureRatio':max(b['designEnclosedPixels2'] for b in data['blocks'])/min(b['designEnclosedPixels2'] for b in data['blocks'])}


def main():
    data=json.loads((HERE/'structure-guide.json').read_text())
    checked=topology(data)
    w,h=data['canvas']; s=3
    im=Image.new('RGB',(w*s,h*s),'#d8ded0'); draw=ImageDraw.Draw(im)
    px=lambda ps:[(round(x*s),round(y*s)) for x,y in ps]
    water=[]
    for i in range(121):
        t=i/120; a=(1652,-30); b=(1680,300); c=(1595,720); d=(1430,990)
        water.append([(1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in range(2)])
    draw.line(px(water),fill='#8fb9c4',width=42*s,joint='curve')
    for b in data['blocks']: draw.polygon(px(b['polygon']),fill=b['color'])
    extensions=[('primary',[[-40,575],[40,565],[120,560]]),('collector',[[510,-30],[505,50],[510,115]]),
                ('collector',[[1500,160],[1490,60],[1470,-30]]),('collector',[[1090,850],[1040,910],[1030,980]]),
                ('local',[[100,720],[35,750],[-40,790]])]
    roads=data['roads']+[{'kind':k,'points':ps} for k,ps in extensions]
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="#d8ded0"/>']
    svg.append('<polyline points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in water)+'" stroke="#8fb9c4" fill="none" stroke-width="42"/>')
    for b in data['blocks']:
        svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in b['polygon'])+f'" fill="{b["color"]}"/>')
    for extra,color in [(12,'#bec2bf'),(0,'#687074')]:
        for e in roads:
            width=data['roadHierarchyWidths'][e['kind']]+extra
            ps=px(e['points']); draw.line(ps,fill=color,width=width*s,joint='curve')
            for x,y in (ps[0],ps[-1]):
                r=width*s/2; draw.ellipse((x-r,y-r,x+r,y+r),fill=color)
            svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in e['points'])+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    destination=HERE/'structure-input.png'
    with destination.open('xb') as f: im.resize((w,h),Image.Resampling.LANCZOS).save(f,format='PNG')
    with (HERE/'structure-input.svg').open('x') as f: f.write('\n'.join(svg+['</svg>']))
    fingerprints=json.loads((HERE/'input-fingerprints.json').read_text())
    fingerprints[0].update(path=str(destination.relative_to(HERE.parents[3])),
                           sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),bytes=destination.stat().st_size,
                           role='clean pixel structure guide, no junction markers; not measured road tracing or metres')
    (HERE/'input-fingerprints.json').write_text(json.dumps(fingerprints,ensure_ascii=False,indent=2)+'\n')
    with (HERE/'structure-check.json').open('x') as f:
        json.dump({'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'passed-design-only',
                   'nativeArtworkOrActualTracingValidated':False,**checked},f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(checked))


if __name__=='__main__': main()
