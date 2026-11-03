"""Manual production measurements; fixed axes only. Run from checkout root. No art pixel writes."""
import json,math,hashlib
from pathlib import Path
ROOT=Path('docs/art/2026-11-03-county-region-atlas/production/R--01-+01'); OUT=ROOT/'registration'
S=ROOT/'input/structures/R--01-+01-structure.json'; A=ROOT/'art/R--01-+01-v1.png'
r=json.loads(S.read_text()); origin=r['originMap']; q=math.sqrt(.5); st=math.sin(math.radians(62.5))
def axis(p):return [(p[0]-origin[0]-p[1]+origin[1])*q,(p[0]-origin[0]+p[1]-origin[1])*q*st]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Coordinates read by eye from native 1254 image, NOT copied from guide projection.
obs=[
('J-1623821778',[-1714.44,148.32],[630,337],'high',8,True,'Upper central four-way crossing, centre enclosed by crosswalks.'),
('J-9621089054',[-1668.12,151.43],[879,540],'high',10,True,'Right-side tee: narrow service branch meets descending through street beside mid-rise.'),
('J-1623821824',[-1719.19,242.74],[128,695],'medium',12,True,'Lower-left road bend/tee; no painted crosswalk, centre estimated from open asphalt.'),
('EDGE-149397380-bottom',[-1636.1963176064444,244],[535,1095],'medium',15,False,'Bottom road strip left endpoint on silhouette; approximate clipped ground boundary.'),
('EDGE-149397509-right',[-1624,154.3899052880821],[1047,751],'medium',12,False,'Descending through street exit beside small right-edge building.'),
('EDGE-149397031-left',[-1744,147.97979539641943],[465,163],'medium',12,False,'Upper-left branch end beside tall top building; silhouette clips road.'),
('EDGE-149396505-top',[-1713.0553576642335,124],[772,219],'medium',12,False,'Upper-right branch from central crossing ends at region ground silhouette.'),
('J-9657208286',[-1665.74,129.38],[993,454],'low',18,False,'Service lane bend near right silhouette, rounded junction inferred from visible asphalt.'),
('EDGE-1046196059-top',[-1665.1603194278903,124],None,'unpaired',None,False,'Short service-road edge cannot be distinguished confidently from irregular upper-right silhouette.'),
('EDGE-1047748330-right',[-1624,140.8616591704148],None,'unpaired',None,False,'Exact service lane end hidden/ambiguous beside right-edge building; no invented pixel.'),
]
points=[dict(id=i,sourceMap=p,imagePx=px,confidence=c,manualPixelUncertainty=u,usedInFit=f,observation=n,hiddenEstimate=False) for i,p,px,c,u,f,n in obs]
f=[e for e in points if e['usedInFit']]; aa=[axis(e['sourceMap']) for e in f];bb=[e['imagePx'] for e in f]
ma=[sum(p[k] for p in aa)/len(aa) for k in range(2)];mb=[sum(p[k] for p in bb)/len(bb) for k in range(2)]
s=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in range(2)) for a,b in zip(aa,bb))/sum(sum((a[k]-ma[k])**2 for k in range(2)) for a in aa)
t=[mb[k]-s*ma[k] for k in range(2)]
def project(p):return [t[k]+s*axis(p)[k] for k in range(2)]
for e in points:
 e['projectedPx']=project(e['sourceMap']);e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in range(2)] if e['imagePx'] else None;e['errorPixels']=math.dist(e['projectedPx'],e['imagePx']) if e['imagePx'] else None
fit=dict(method='Unweighted least squares on three manual noncollinear road observations; fixed 62.5/45 axes; uniform positive scale and translation only',anchorMap=origin,anchorPixel=t,anchorUV=[v/1254 for v in t],nativePixelsPerUnit=s,rotationDegrees=0,nonUniformScale=False,fitControlCount=3,fitMaxResidualPixels=max(e['errorPixels'] for e in f),fitRmsResidualPixels=math.sqrt(sum(e['errorPixels']**2 for e in f)/3),allObservedMaxResidualPixels=max(e['errorPixels'] for e in points if e['imagePx']))
# Conservative 1m-wide interior centre strip on the long unobstructed diagonal road 149397397.
p0=[-1714.44,148.32];p1=[-1719.36,234.75]
def along(v):return [p0[k]+v*(p1[k]-p0[k]) for k in range(2)]
a=along(.18);b=along(.75);dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy);nx=-dy/l*.5;ny=dx/l*.5
coverage=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]]
sources=[A,S,ROOT/'input/guides/R--01-+01-structure-neutral.png',ROOT/'generation-record.json',ROOT/'input/prompts/R--01-+01-v1.json',Path('docs/art/2026-11-03-county-region-atlas/repairs/C/REGION-C-v3.png')]
m=dict(schemaVersion=1,id='R--01-+01',sourceArt=dict(file=str(A),sha256=sha(A),nativeSize=[1254,1254]),sourceGeometry=dict(file=str(S),sha256=sha(S),citySha256=r['source']['sha256']),sources=[dict(file=str(p),sha256=sha(p)) for p in sources],projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=fit,controlPoints=points,routeCoverageMapPolygon=coverage,routeCoverageRationale='Candidate usable interior 1m centre strip on road149397397, away from both junctions and boundaries; visibly open. Not full region trust; PM must choose ready. Boundaries and through-neighbor routes excluded.',hiddenEstimates=[],status='preview-only',seamReady=False,limitations=['Manual readings have 8–18px uncertainty; approximate edge matches are not surveyed points.','No hidden junction pixel was used as a fit control.','Three-point fit does not establish all road shapes or exact whole-image geometry.','No complementary overlap ownership exists; no seam is ready.','No game tests, runtime rendering, image resampling or city modification.'])
(OUT/'measurement.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
entry=dict(id=r['id'],file=str(A.resolve()),sha256=sha(A),nativeSize=[1254,1254],anchorMap=origin,anchorUV=fit['anchorUV'],nativePixelsPerUnit=s,sortOrder=0,registration=dict(status='preview-only',evidence=str(OUT/'measurement.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence'],residualPixels=e['errorPixels']) for e in points if e['imagePx']],maxResidualPixels=fit['allObservedMaxResidualPixels'],routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='Measured candidate only. Absolute file identifies real original; packager may copy byte-identical file and rewrite path. PM alone selects ready. No complementary ownership/seam closure or deployment.')
(OUT/'region-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
# Separate vector diagnostic references unchanged art; never rasterizes or edits art.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1254" height="1254" viewBox="0 0 1254 1254">','<rect width="1254" height="1254" fill="#222"/>','<image href="../art/R--01-+01-v1.png" width="1254" height="1254"/>']
for road in r['roads']:
 for seg in road['displaySegments']:
  coords=' '.join(','.join(str(v) for v in project(p)) for p in seg);svg.append(f'<polyline points="{coords}" fill="none" stroke="cyan" stroke-width="2"/>')
for e in points:
 if e['imagePx']:
  x,y=e['imagePx'];u,v=e['projectedPx'];svg += [f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="yellow"/>',f'<path d="M{x},{y} L{u},{v}" stroke="red"/>',f'<text x="{x+8}" y="{y}" fill="white" font-size="13">{e["id"]}: {e["errorPixels"]:.1f}px</text>']
svg.append('</svg>');(OUT/'road-diagnostic.svg').write_text('\n'.join(svg))
print(json.dumps(fit,indent=2));print('COVERAGE',coverage)
C=Path('docs/art/2026-11-03-county-region-atlas/repairs/C/measurement.json');c=json.loads(C.read_text());cf=c['fit']
def inverse(px,fit):
 u=(px[0]-fit['anchorPixel'][0])/fit['nativePixelsPerUnit'];v=(px[1]-fit['anchorPixel'][1])/fit['nativePixelsPerUnit'];return [fit['anchorMap'][0]+(u/q+v/(q*st))/2,fit['anchorMap'][1]+(v/(q*st)-u/q)/2]
pairMap=[-1636.1963176064444,244]; local=[535,1095];cp=[20,628];lm=inverse(local,fit);cm=inverse(cp,cf)
seams=[]
for seam in r['neighborSharedRoadControls']:
 item=dict(seamId=seam['seamId'],regions=seam['regions'],overlapBounds=seam['overlapBounds'],overlapWidthMetres=16,sourceRoadSegments=seam['sourceRoadSegments'],seamReady=False,ownershipPolygonUV=None,complementaryOwnershipPolygonUV=None,ownershipStatus='unassigned; core rectangle is not a natural building cut',actualCorrespondences=[])
 if 'REGION-C' in seam['regions']:
  item['neighborEvidence']=dict(file=str(C),sha256=sha(C),artFile=str(sources[-1]),artSha256=sha(sources[-1]))
  item['actualCorrespondences']=[dict(sourceMap=pairMap,localImagePx=local,neighborImagePx=cp,confidence='medium',observation='Same main-road bottom render boundary. Local bottom strip and C left road exit visible; C pixel taken from existing manual measurement and visually checked against C3. Boundary correspondence alone does not close entire seam.',localImpliedMap=lm,neighborImpliedMap=cm,impliedMapDifferenceMetres=math.dist(lm,cm)),dict(sourceMap=[-1640,153.31650355169694],localImagePx=None,neighborImagePx=[472,186],confidence='unpaired',observation='No unique local mark at this interior overlap boundary; C has visible upper-left spur. No invented local mark.'),dict(sourceMap=[-1640,137.72630350194555],localImagePx=None,neighborImagePx=[568,122],confidence='unpaired',observation='Narrow service street passes overlap but local boundary is not a visible identifiable junction; no exact pair.')]
  item['naturalOwnershipReview']=['Local far-right small building around native bbox[1110,560,1254,735] extends beyond ground; do not cut at x=-1632 without matching full building identity on C.','C upper-left ground spur and service lane are visually distinct; preserve both source roads and select a ground seam between complete buildings.','Local bottom road strip and C left through road share one actual observed exit only. No complementary whole-building ownership established.']
 else:item['naturalOwnershipReview']=['Neighbor native art not inspected in this assignment; actual correspondence and complementary whole-building ownership pending. Do not infer readiness from source road segments.']
 seams.append(item)
(OUT/'seam-diagnostics.json').write_text(json.dumps(dict(id=r['id'],seamReady=False,seams=seams),ensure_ascii=False,indent=2)+'\n')
print('C shared endpoint implied map separation(m):',math.dist(lm,cm))
