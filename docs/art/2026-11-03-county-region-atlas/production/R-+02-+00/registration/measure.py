"""Recompute production annotation only. No art mutation, source edits or game execution."""
import json, math, hashlib
from pathlib import Path
from PIL import Image
BASE=Path('docs/art/2026-11-03-county-region-atlas'); P=BASE/'production/R-+02-+00'; OUT=P/'registration'
S=P/'input/structures/R-+02-+00-structure.json'; ART=P/'art/R-+02-+00-v1.png'
r=json.loads(S.read_text()); origin=r['originMap']; q=math.sqrt(.5); st=math.sin(math.radians(62.5))
def axis(p):return [(p[0]-origin[0]-p[1]+origin[1])*q,(p[0]-origin[0]+p[1]-origin[1])*q*st]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Native 1254-square hand observations, not guide pixels. Edge controls are less certain than junction.
raw=[('J-central',[-1369.14,79.98],[595,624],'high',6,True,'Visible four-way street centre; nearby source nodes merge into crossing.'),('W-edge',[-1432,91.32238333909437],[250,414],'medium',10,True,'Centre of asphalt where left/up branch meets ground silhouette.'),('N-edge',[-1379.8140599455041,20],[864,307],'medium',10,True,'Centre of upper/right main-road opening at ground silhouette.'),('S-edge',[-1360.236592920354,140],[333,928],'medium',10,False,'Lower/left main-road opening, before projecting foreground buildings.'),('E-edge',[-1312,70.71974780282765],[941,840],'medium',12,False,'Lower/right transverse-road opening beside projecting right building.'),('B-overlap-interior',[-1416,88.42158831662634],[346,473],'estimated',16,False,'Approximate visible lane centre within straight left branch; longitudinal position inferred, not independent feature.'),('node-5342500894',[-1370.8,71.69],None,'unpaired',None,False,'No distinct street junction at this source node; do not assign a fabricated pixel.')]
points=[dict(id=i,sourceMap=p,imagePx=px,confidence=c,manualPixelUncertainty=u,usedInFit=f,observation=n,hiddenEstimate=False) for i,p,px,c,u,f,n in raw]
fit=[e for e in points if e['usedInFit']]; a=[axis(e['sourceMap']) for e in fit]; b=[e['imagePx'] for e in fit]; ma=[sum(v[k] for v in a)/len(a) for k in (0,1)];mb=[sum(v[k] for v in b)/len(b) for k in (0,1)]
s=sum(sum((x[k]-ma[k])*(y[k]-mb[k]) for k in (0,1)) for x,y in zip(a,b))/sum(sum((x[k]-ma[k])**2 for k in (0,1)) for x in a); anchor=[mb[k]-s*ma[k] for k in (0,1)]
def project(p):return [anchor[k]+s*axis(p)[k] for k in (0,1)]
for e in points:
 e['projectedPx']=project(e['sourceMap']); e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in (0,1)] if e['imagePx'] else None;e['errorPixels']=math.dist(e['projectedPx'],e['imagePx']) if e['imagePx'] else None
errs=[e['errorPixels'] for e in fit]; allerr=[e['errorPixels'] for e in points if e['imagePx']]
# Narrow observed main-road interior only, excluding unassigned seam strips and transverse exits.
coverage=[[-1375.2,55],[-1371.2,55],[-1362.9,112],[-1366.9,112]]
info=dict(method='fixed 62.5/45 axes; positive uniform least-squares scalar plus translation; three noncollinear manual controls',anchorMap=origin,anchorPixel=anchor,anchorUV=[v/1254 for v in anchor],nativePixelsPerUnit=s,rotationDegrees=0,nonUniformScale=False,fitControlCount=3,fitMaxResidualPixels=max(errs),fitRmsResidualPixels=math.sqrt(sum(e*e for e in errs)/3),allObservedMaxResidualPixels=max(allerr))
provenance=[]
for p in [ART,S,P/'input/guides/R-+02-+00-structure-neutral.png',P/'input/prompts/R-+02-+00-v1.json',P/'generation-record.json',P/'input/source-manifest.json',BASE/'images/REGION-B-v4.png',BASE/'registration/registration-B-v4.json']:
 provenance.append(dict(file=str(p),sha256=sha(p)))
seams=[]
for seam in r['neighborSharedRoadControls']:
 seams.append(dict(**seam,seamReady=False,actualCorrespondence='B overlap road is visually present in both images; longitudinal interior point estimated, no unique matching ground feature or complementary ownership. Other neighbors not inspected in this task.' if 'REGION-B' in seam['regions'] else 'Only source geometry recorded; no actual neighbor-art correspondence established.',ownershipPolygonUV=None,complementaryNeighborOwnership=None,wholeBuildingOwnership='unresolved; do not cut a facade at nominal 8m halo midpoint'))
record=dict(schemaVersion=1,id='R-+02-+00',status='measured-preview-only',nativeSize=list(Image.open(ART).size),provenance=provenance,projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=info,controlPoints=points,routeCoverageMapPolygon=coverage,coverageNote='Conservative candidate main-road strip between y55 and112 only; not runtime authorized. Source road, blue boundary and PM gate remain authoritative.',hiddenEstimates=[],limitations=['Edge imagePx are approximate silhouette road centres, not surveyed intersections.','No unique landmark at B shared strip interior; estimate does not prove seamlessness.','Small paving discrepancies accepted; maxima are diagnostics, not rejection thresholds.','No native image alteration, game tests, runtime inspection, deployment or PM ready decision.'],seamReady=False)
(OUT/'measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id='R-+02-+00',file=str(ART),sha256=sha(ART),nativeSize=record['nativeSize'],anchorMap=origin,anchorUV=info['anchorUV'],nativePixelsPerUnit=s,sortOrder=0,registration=dict(status='preview-only',evidence=str(OUT/'measurement.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence'],residualPixels=e['errorPixels']) for e in points],maxResidualPixels=max(allerr),routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='Measured candidate, PM alone decides ready. File is checkout-relative; packaging must copy byte-identical art and set relative runtime filename. Seam ownership unresolved.')
(OUT/'region-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n');(OUT/'seam-diagnostics.json').write_text(json.dumps(seams,ensure_ascii=False,indent=2)+'\n')
# Vector diagnostic referencing original bytes: never changes raster art pixels.
svg=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1254" height="1254" viewBox="0 0 1254 1254">','<rect width="1254" height="1254" fill="#202027"/>','<image xlink:href="../art/R-+02-+00-v1.png" width="1254" height="1254"/>']
for road in r['roads']:
 for seg in road['displaySegments']: svg.append('<polyline points="'+ ' '.join(','.join(str(v) for v in project(p)) for p in seg)+'" fill="none" stroke="cyan" stroke-width="2"/>')
for e in points:
 if e['imagePx']:
  x,y=e['imagePx'];u,v=e['projectedPx'];svg.append(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="yellow"/><path d="M{x},{y} L{u},{v}" stroke="red"/><text x="{x+9}" y="{y}" fill="white" font-size="14">{e["id"]} {e["errorPixels"]:.1f}px</text>')
svg.append('</svg>');(OUT/'road-diagnostic.svg').write_text('\n'.join(svg))
print(json.dumps(info,indent=2))
