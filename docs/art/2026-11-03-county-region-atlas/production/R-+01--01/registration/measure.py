"""Recompute manual production observations; no art pixels or city are modified."""
import json, math, hashlib
from pathlib import Path
R=Path(__file__).resolve().parent; B=R.parent; AT=B.parent.parent
S=B/'input/structures/R-+01--01-structure.json'; A=B/'art/R-+01--01-v1.png'; N=AT/'images/REGION-B-v4.png'
s=json.loads(S.read_text()); origin=s['originMap']; q=math.sqrt(.5); h=math.sin(math.radians(62.5))
def axis(p):return [(p[0]-origin[0]-p[1]+origin[1])*q,(p[0]-origin[0]+p[1]-origin[1])*q*h]
# Native 1254-square observations read visually from unmodified PNG, not guide projections.
obs=[('west-tee',[-1510.24,11.4],[220,640],'medium',12,True,'Centre of visible west tee; broad painted junction, no exact node marker.'),('east-tee',[-1421.12,-49.9],[1020,776],'high',7,True,'Upper long street meets descending-left service street beside rounded building.'),('upper-entry',[-1536,-59.00116926134482],[480,228],'medium',12,True,'Centreline entering silhouette beneath long upper slab; boundary position approximate.'),('west-main-entry',[-1536,9.553991291727138],[151,542],'medium',12,False,'Centre of lower main road at left silhouette.'),('south-main-exit',[-1416,11.566259664089582],[729,1070],'low',18,False,'Main road exits next to lower-right building; silhouette not exact ground boundary.'),('outer-road-exit',[-1416,-67.74144552319308],[1144,716],'medium',12,False,'Outer narrow road at right silhouette near crossing stripes.'),('outer-road-entry',[-1472.5879014308425,-84],[945,382],'low',18,False,'Outer road enters near upper-right cut; ground boundary interpretation uncertain.'),('service-end',[-1424.75,6.79],None,'unpaired',None,False,'Source service ends before main street. Painted connecting junction/foreground building makes exact endpoint unidentifiable; hidden estimate only, excluded from fit.')]
e=[dict(id=i,sourceMap=p,imagePx=px,confidence=c,manualPixelUncertainty=u,usedInFit=f,observation=n) for i,p,px,c,u,f,n in obs]
f=[x for x in e if x['usedInFit']]; aa=[axis(x['sourceMap']) for x in f]; bb=[x['imagePx'] for x in f]; ma=[sum(p[k] for p in aa)/len(f) for k in (0,1)]; mb=[sum(p[k] for p in bb)/len(f) for k in (0,1)]
scale=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in (0,1)) for a,b in zip(aa,bb))/sum(sum((a[k]-ma[k])**2 for k in (0,1)) for a in aa); anchor=[mb[k]-scale*ma[k] for k in (0,1)]
def project(p):return [anchor[k]+scale*axis(p)[k] for k in (0,1)]
for x in e:
 x['projectedPx']=project(x['sourceMap']);x['errorVectorPixels']=[x['projectedPx'][k]-x['imagePx'][k] for k in (0,1)] if x['imagePx'] else None;x['errorPixels']=math.dist(x['projectedPx'],x['imagePx']) if x['imagePx'] else None;x['hiddenEstimatePx']=x['projectedPx'] if x['imagePx'] is None else None
err=[x['errorPixels'] for x in e if x['imagePx']];fe=[x['errorPixels'] for x in f]
fit=dict(method='fixed 62.5/45 axes; least-squares positive uniform scale plus translation; no rotation/warp',anchorMap=origin,anchorPixel=anchor,anchorUV=[v/1254 for v in anchor],nativePixelsPerUnit=scale,fitMaxResidualPixels=max(fe),fitRmsResidualPixels=math.sqrt(sum(v*v for v in fe)/len(fe)),allObservedMaxResidualPixels=max(err),rotationDegrees=0,nonUniformScale=False)
def record(p):return dict(file=str(p.relative_to(Path.cwd())) if p.is_relative_to(Path.cwd()) else str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
# Candidate interior corridor only: lower main street east of west tee, excluding unresolved right endpoint/foreground slab.
coverage=[[-1497,8],[-1441,8],[-1441,15],[-1497,15]]
seams=[]
for n in s['neighborSharedRoadControls']:
 seams.append(dict(seamId=n['seamId'],overlapBounds=n['overlapBounds'],sourceRoadSegments=n['sourceRoadSegments'],actualPairedImagePoints=None,complementaryOwnership=None,seamReady=False,note='16m shared world strip; no measured complementary ownership. REGION-B visually reviewed, other neighbor native art not reviewed in this task.'))
m=dict(schemaVersion=1,id='R-+01--01',sourceArt=record(A),sourceGeometry=record(S),neighborArt=record(N),guide=record(B/'input/guides/R-+01--01-structure-neutral.png'),generationRecord=record(B/'generation-record.json'),fullPrompt=record(B/'input/prompts/R-+01--01-v1.json'),nativeSize=[1254,1254],projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=fit,controlPoints=e,routeCoverageMapPolygon=coverage,routeCoverageStatus='candidate interior lower-main corridor only; PM must decide ready, not runtime-verified',seams=seams,seamReady=False,limitations=['Manual visual hypotheses with 7–18px picking uncertainty; painted ground edge is approximate.','Null endpoint is not an observed match.','No tests/browser/runtime/deployment performed.','No strict all-image residual cutoff: small paving drift is acceptable; inspect major occlusions separately.'])
def save(name,data):(R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
save('measurement.json',m)
save('region-entry.json',dict(id='R-+01--01',file=A.name,sha256=m['sourceArt']['sha256'],nativeSize=[1254,1254],anchorMap=origin,anchorUV=fit['anchorUV'],nativePixelsPerUnit=scale,sortOrder=0,registration=dict(status='preview-only',evidence=str(R.relative_to(Path.cwd())/'measurement.json'),controlPoints=[dict(map=x['sourceMap'],pixel=x['imagePx'],confidence=x['confidence'],residualPixels=x['errorPixels']) for x in e if x['imagePx']],maxResidualPixels=max(err),routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='Reused native v1. PM decides ready; unresolved 16m seams and endpoint ambiguity retained. Not deployed.'))
# Vector-only diagnostics referencing original; no raster editing/resampling.
svg=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1254" height="1254" viewBox="0 0 1254 1254">','<image xlink:href="../art/R-+01--01-v1.png" width="1254" height="1254"/>']
for road in s['roads']:
 for seg in road['displaySegments']:svg.append('<polyline points="'+' '.join(','.join(str(v) for v in project(p)) for p in seg)+'" fill="none" stroke="cyan" stroke-width="2"/>')
for x in e:
 a,b=x['projectedPx'];svg.append(f'<circle cx="{a}" cy="{b}" r="5" fill="cyan"/>')
 if x['imagePx']:
  c,d=x['imagePx'];svg.extend([f'<circle cx="{c}" cy="{d}" r="8" fill="none" stroke="yellow"/>',f'<path d="M {a} {b} L {c} {d}" stroke="red"/>',f'<text x="{c+9}" y="{d}" fill="white" font-size="14">{x["id"]}: {x["errorPixels"]:.1f}</text>'])
svg.append('</svg>');(R/'road-diagnostic.svg').write_text('\n'.join(svg))
print(json.dumps(fit,indent=2));print([(x['id'],x['errorPixels']) for x in e])
