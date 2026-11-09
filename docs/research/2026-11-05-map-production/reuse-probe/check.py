"""Offline nominal geometry probe. No image edits, game execution or source mutations."""
import json, math, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
citypath=ROOT/'delivery-game/assets/resources/map-sample/city.json'
c=json.loads(citypath.read_text()); l=json.loads((ROOT/'docs/art/2026-11-03-high-camera-city/scene-layout.json').read_text())
z=json.loads((ROOT/'docs/art/2026-11-02-county-zoning/selection.json').read_text())['regions']['city']['worldBoundsMetresApprox']
nodes={n['id']:(n['x'],n['y']) for n in c['nodes']}
def inside(p,poly):
 x,y=p; yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
def pointdist(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1]; t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def intersects(a,b,p,q):
 return cross(a,b,p)*cross(a,b,q)<=0 and cross(p,q,a)*cross(p,q,b)<=0 and max(min(a[0],b[0]),min(p[0],q[0]))<=min(max(a[0],b[0]),max(p[0],q[0])) and max(min(a[1],b[1]),min(p[1],q[1]))<=min(max(a[1],b[1]),max(p[1],q[1]))
def polydist(a,b,poly):
 if inside(a,poly) or inside(b,poly):return 0
 d=1e9
 for p,q in zip(poly,poly[1:]+poly[:1]):
  if intersects(a,b,p,q):return 0
  d=min(d,pointdist(a,p,q),pointdist(b,p,q),pointdist(p,a,b),pointdist(q,a,b))
 return d
segs=[]
for r in c['roads']:
 for i,(u,v) in enumerate(zip(r['nodes'],r['nodes'][1:])):
  if u not in nodes or v not in nodes:continue
  a,b=nodes[u],nodes[v]
  if a==b:continue
  if max(a[0],b[0])<z['minX']-50 or min(a[0],b[0])>z['maxX']+50 or max(a[1],b[1])<z['minY']-50 or min(a[1],b[1])>z['maxY']+50:continue
  segs.append((r['id'],i,a,b,float(r['width'])))
origin=l['projection']['originMap'];along=l['parcels'][0]['localAxes']['alongRoadNorth'];target=math.atan2(along[1],along[0]);results=[];qualified=0
for rid,i,a,b,width in segs:
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<30:continue
 angle=abs((math.atan2(dy,dx)-target+math.pi/2)%math.pi-math.pi/2)
 if angle>math.radians(3):continue
 # Keep original-width frontage gap; other widths require changing relative placement.
 if abs(width-8)>.1:continue
 center=((a[0]+b[0])/2,(a[1]+b[1])/2)
 if math.dist(center,origin)<80:continue
 qualified+=1;shift=(center[0]-origin[0],center[1]-origin[1]);polys=[]
 for parcel in l['parcels']:
  polys.append([(p[0]+shift[0],p[1]+shift[1]) for p in parcel['artBoundaryMapCandidate']])
 if not all(z['minX']<=x<=z['maxX'] and z['minY']<=y<=z['maxY'] for poly in polys for x,y in poly):continue
 clearance=1e9;collision=None
 for poly in polys:
  for other,j,u,v,w in segs:
   if max(u[0],v[0])+w/2<min(p[0] for p in poly) or min(u[0],v[0])-w/2>max(p[0] for p in poly) or max(u[1],v[1])+w/2<min(p[1] for p in poly) or min(u[1],v[1])-w/2>max(p[1] for p in poly):continue
   gap=polydist(u,v,poly)-w/2
   if gap<clearance:clearance=gap;collision={'roadId':other,'segment':j}
 results.append({'roadId':rid,'segment':i,'center':center,'translation':shift,'angleMismatchDegrees':math.degrees(angle),'length':length,'nominalRoadClearanceMetres':clearance,'nearestRoad':collision,'nominalRoadOverlap':clearance<0})
results.sort(key=lambda r:r['nominalRoadClearanceMetres'],reverse=True)
out={'status':'offline-candidate-screen-only-not-placement-acceptance','sourceSha256':hashlib.sha256(citypath.read_bytes()).hexdigest(),'criteria':{'translationOnly':True,'roadWidth':8,'maxAngleMismatchDeg':3,'minSegmentLength':30,'minDistanceFromOriginal':80,'twoParcelsTogether':True,'search':'segment midpoints in blue bounds; not exhaustive placements'},'candidateSegmentsBeforeBoundaryFilter':qualified,'candidates':results,'limits':['artBoundaryMapCandidate is manually estimated, not exact alpha footprint','no source building/waterway/POI collision check; no occlusion/entrance/image/visual validation','some source bridges/overpasses need vertical interpretation; roads treated conservatively as planar','two existing block types cannot demonstrate county-wide visual diversity']}
Path(__file__).with_name('result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('qualified',qualified,'within blue',len(results),'nominal no road overlap',sum(not r['nominalRoadOverlap'] for r in results));print(json.dumps(results[:3],ensure_ascii=False,indent=2))
