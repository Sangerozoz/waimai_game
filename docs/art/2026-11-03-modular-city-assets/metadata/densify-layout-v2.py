"""One bounded static layout pass: copy v1, add five whole native sprites, keep main buildings."""
import json, math, hashlib, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[2]
v1=ROOT/'sample-layout-v1.json'
if not v1.exists(): shutil.copyfile(ROOT/'sample-layout.json',v1)
layout=json.loads(v1.read_text())
city=json.loads((PROJECT/'delivery-game/assets/resources/map-sample/city.json').read_text())
nodes={n['id']:[n['x'],n['y']] for n in city['nodes']}
original={p['assetId']:p for p in layout['placements'] if p['assetId'] in ['B01','B02','B03']}
def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def ptseg(p,a,b):
    x,y=b[0]-a[0],b[1]-a[1]; z=x*x+y*y
    t=max(0,min(1,((p[0]-a[0])*x+(p[1]-a[1])*y)/z)) if z else 0
    return math.hypot(p[0]-a[0]-t*x,p[1]-a[1]-t*y)
def inside(p,poly):
    q=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if ptseg(p,a,b)<1e-8: return True
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]: q=not q
    return q
def intersection(a,b,c,d):
    v=[cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)]
    if v[0]*v[1]<0 and v[2]*v[3]<0: return True
    return any(abs(z)<1e-8 and ptseg(p,q,r)<1e-8 for z,p,q,r in [(v[0],c,a,b),(v[1],d,a,b),(v[2],a,c,d),(v[3],b,c,d)])
def segpoly(a,b,p):
    if inside(a,p) or inside(b,p): return 0
    ds=[]
    for c,d in zip(p,p[1:]+p[:1]):
        if intersection(a,b,c,d):return 0
        ds += [ptseg(a,c,d),ptseg(b,c,d),ptseg(c,a,b),ptseg(d,a,b)]
    return min(ds)
def polydist(p,q):
    if inside(p[0],q) or inside(q[0],p):return 0
    return min(segpoly(a,b,q) for a,b in zip(p,p[1:]+p[:1]))
def bbox(p):return [min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)]
def local(p):
    b=bbox(p)
    return b[0]<-1540 and b[2]>-1625 and b[1]<125 and b[3]>30

additions=[
    ('neighbor-west-south','B03',[-1595.5,59],1.1,[172,173],'Opposite-road street row south, existing source parcel references 172/173.'),
    ('neighbor-west-middle','B01',[-1598.8,73],1.1,[170,171],'Opposite-road street row middle; roughly 2m gap to neighboring whole footprints.'),
    ('neighbor-west-north','B02',[-1601,86],1.1,[169],'Opposite-road street row north; taller narrow building varies the silhouette.'),
    ('neighbor-east-middle','B02',[-1569,79.5],1.1,[144],'Second narrow whole building in wider source144 street block, preserving a small passage.'),
    ('neighbor-east-rear','B03',[-1559,66],1.05,[143],'Rear/east whole building fills open source143 block edge without stretching the original parcel polygon.'),
]
for id,aid,pos,scale,refs,note in additions:
    source=original[aid]
    footprint=[[round(pos[0]+(p[0]-source['map'][0])*scale,6),round(pos[1]+(p[1]-source['map'][1])*scale,6)] for p in source['groundFootprint']]
    layout['placements'].append({'id':id,'assetId':aid,'map':pos,'scale':scale,'layer':10,'groundFootprint':footprint,
        'sourceBuildingReferenceIndices':refs,'role':'neighbor-street-building','notes':[note,'Complete upright reused native sprite. Scale is uniform; no new image, mirror, shear or road movement.']})
for p,i in zip(layout['placements'][:3],[143,144,145]):p['sourceBuildingReferenceIndices']=[i]
layout['revision']=2
layout['bounds']={'minX':-1615,'maxX':-1548,'minY':40,'maxY':112}
layout['displayClip']=dict(layout['bounds'])
layout['cameraFocus']={'placementIds':['building-b01','building-b02','building-b03'],'padding':3,
    'notes':'Default close view of main three and frontage; background neighbors may be cropped. Do not fit all placements into the initial view.'}
layout['notes'] += ['Revision2 adds five whole-building neighbor instances to reduce empty paving. Original three main placements and all manifest assets unchanged.',
    'Existing source buildings 143/144/169/170/171/172/173 are parcel references for these reused instances; overlapping references are not individual source geometry deletion. Source city.json is unchanged.',
    'Background/display bounds extend to 67x72m, but default cameraFocus stays close to the original three main buildings; never auto-zoom out to include every neighbor.']
segments=[]
for r in city['roads']:
    for aa,bb in zip(r['nodes'],r['nodes'][1:]):
        a,b=nodes[aa],nodes[bb]
        if local([a,b]):segments.append((r['id'],r['width'],a,b))
water=[(i,w['points']) for i,w in enumerate(city['areas']) if w.get('kind')=='water' and len(w.get('points',[]))>2 and local(w['points'])]
waterways=[(i,w) for i,w in enumerate(city['waterways']) if len(w)>1 and local(w)]
analyses=[]
for p in layout['placements']:
    if not p['id'].startswith('neighbor-'):continue
    gp=p['groundFootprint'];nearest=min((segpoly(a,b,gp)-width/2,rid) for rid,width,a,b in segments)
    other=[q['id'] for q in layout['placements'] if q['id']!=p['id'] and polydist(gp,q['groundFootprint'])<1e-8]
    wa=[i for i,q in water if polydist(gp,q)==0]
    wl=[i for i,q in waterways if any(segpoly(a,b,gp)==0 for a,b in zip(q,q[1:]))]
    analyses.append({'placementId':p['id'],'map':p['map'],'scale':p['scale'],'sourceBuildingReferenceIndices':p['sourceBuildingReferenceIndices'],
        'nearestRoadId':nearest[1],'carriagewayClearanceMeters':round(nearest[0],4),'carriagewayOverlap':nearest[0]<=0,
        'otherDisplayFootprintOverlaps':other,'waterAreaOverlapIndices':wa,'waterwayCenterlineOverlapIndices':wl})
report={'schemaVersion':1,'status':'bounded-static-layout-candidate-not-engine-reviewed','sourceScreenshot':'engine-v1.jpg',
    'mainPlacementsPreserved':[p['id'] for p in layout['placements'][:3]],'addedBuildings':len(additions),
    'localRoadSegmentsConsidered':len(segments),'analysis':analyses,
    'notes':['Local geometry calculations only, no engine/browser/render/tests. Trees and lamps unchanged, no extra greenery.',
             'Original footprints are manual candidates, hidden rear corners estimated; this does not certify exact artwork contact or user visual acceptance.']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'sample-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
report['sha256']={'sample-layout-v1.json':sha(v1),'sample-layout.json':sha(ROOT/'sample-layout.json'),'asset-manifest.json':sha(ROOT/'asset-manifest.json')}
(ROOT/'metadata/layout-v2-static-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
