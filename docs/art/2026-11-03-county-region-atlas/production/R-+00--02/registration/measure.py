"""Production measurement only. Run from checkout root; no native raster writes."""
import json,math,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path('docs/art/2026-11-03-county-region-atlas/production/R-+00--02'); OUT=ROOT/'registration'
ART=ROOT/'art/R-+00--02-v1.png'; STRUCT=ROOT/'input/structures/R-+00--02-structure.json'
r=json.loads(STRUCT.read_text()); origin=r['originMap']; size=list(Image.open(ART).size)
def provenance(p):
 p=Path(p);return dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
points=[]
def add(id,p,px,conf,unc,note,fit=False):points.append(dict(id=id,sourceMap=p,imagePx=px,confidence=conf,manualPixelUncertainty=unc,hiddenEstimate=False,usedInFit=fit,observation=note))
add('upper-main-cross',[-1578.03,-173.24],[875,403],'high',8,'Upper-right zebra crossing centre, 277481069 meets 149396620/149396706.',True)
add('central-main-cross',[-1569.94,-130.09],[620,651],'high',8,'Central zebra crossing centre, 277481069 meets 1148703580; nearby northern branch merges visually.',True)
add('upper-road-left-exit',[-1640,-171.2781995297279],[566,75],'medium',15,'149396706 at left/source-minX ground edge. Centre of open asphalt at upper sloping silhouette; boundary is only approximate.',True)
add('lower-main-bend',[-1559.46,-99.12],[510,827],'medium',14,'149397540 meets main road near lower-left bend; no distinct zebra crossing, hence lower confidence.')
add('left-road-edge',[-1638.0465439093484,-68],[19,600],'medium',15,'149396459 open road at leftmost ground edge; boundary correspondence approximate.')
add('right-upper-road-edge',[-1520,-175.1963196615781],[1180,663],'medium',15,'149396620 open road at right ground edge, near small utility building.')
add('north-shared-main-edge',[-1558.4598691955528,-68],None,'unpaired',None,'Shared-band main-road exit is adjacent to projecting lower building; exact source boundary cannot be observed reliably.')
def axis(p):
 x,y=p[0]-origin[0],p[1]-origin[1];return [(x-y)*math.sqrt(.5),(x+y)*math.sin(math.radians(62.5))*math.sqrt(.5)]
f=[e for e in points if e['usedInFit']]; aa=[axis(e['sourceMap']) for e in f];bb=[e['imagePx'] for e in f]
ma=[sum(a[k] for a in aa)/len(aa) for k in (0,1)];mb=[sum(b[k] for b in bb)/len(bb) for k in (0,1)]
s=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in (0,1)) for a,b in zip(aa,bb))/sum(sum((a[k]-ma[k])**2 for k in (0,1)) for a in aa)
t=[mb[k]-s*ma[k] for k in (0,1)]
def project(p):return [t[k]+s*axis(p)[k] for k in (0,1)]
for e in points:
 e['projectedPx']=project(e['sourceMap']);e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in (0,1)] if e['imagePx'] else None;e['errorPixels']=math.dist(e['projectedPx'],e['imagePx']) if e['imagePx'] else None
fit=dict(method='Least squares: fixed 62.5/45 axes; one positive uniform scale and translation; manual readings only',anchorMap=origin,anchorPixel=t,anchorUV=[t[k]/size[k] for k in (0,1)],nativePixelsPerUnit=s,rotationDegrees=0,nonUniformScale=False,fitControlCount=3,fitRmsResidualPixels=math.sqrt(sum(e['errorPixels']**2 for e in f)/3),fitMaxResidualPixels=max(e['errorPixels'] for e in f),allObservedMaxResidualPixels=max(e['errorPixels'] for e in points if e['imagePx']))
# Interior subset of the open 8m road; excludes all edge crossings and adjacent yards.
coverage=None # No complete corridor established under this fit; preview-only is mandatory.
neighbor=Path('docs/art/2026-11-03-county-region-atlas/repairs/north-A/R-+00--01-v2.png')
seams=[]
for seam in r['neighborSharedRoadControls']:
 z=dict(seam);z.update(actualNeighborImageInspected='R-+00--01' in z['regions'],complementaryOwnershipPolygonUV=None,seamReady=False,actualPairedNativePoints=[],note='16m overlap from source; no complementary ownership authored. Native boundary endpoints not identifiable as exact same world points.');seams.append(z)
record=dict(schemaVersion=1,id=r['id'],sourceArt={**provenance(ART), 'nativeSize':size},sourceGeometry=provenance(STRUCT),projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=fit,controlPoints=points,hiddenEstimates=[],routeCoverageMapPolygon=coverage,routeCoverageStatus='none established: central-road offset reaches sidewalk/building setback; do not use null fallback to enable routes',seams=seams,seamReady=False,runtimeStatus='preview-only',provenance=[provenance(p) for p in [neighbor,ROOT/'generation-record.json',ROOT/'input/prompts/R-+00--02-v1.json',ROOT/'input/source-manifest.json',Path(r['guide']['file'])]],limitations=['Observed junctions and edge hypotheses have different confidence; edge points are not survey marks.','No raster modification, source geometry edits, game operations, tests or deployment.','All perimeter routes and north-neighbor crossing excluded from candidate coverage.','Native lower building extends to canvas edge; complete-building ownership remains unresolved.'])
(OUT/'measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id=r['id'],file=str(ART),sha256=record['sourceArt']['sha256'],nativeSize=size,anchorMap=origin,anchorUV=fit['anchorUV'],nativePixelsPerUnit=s,sortOrder=0,registration=dict(status='preview-only',evidence=str(OUT/'measurement.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence'],residualPixels=e['errorPixels']) for e in points if e['imagePx']],maxResidualPixels=fit['allObservedMaxResidualPixels'],routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='Repository-relative file path: PM must rebase when packaging runtime assets. PM alone chooses ready; candidate interior coverage excludes seam crossings. Not deployed.')
(OUT/'region-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
# SVG references byte-identical original art; no modified generated raster is produced.
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{size[0]}" height="{size[1]}" viewBox="0 0 {size[0]} {size[1]}"><image href="../art/{ART.name}" width="{size[0]}" height="{size[1]}"/>']
for road in r['roads']:
 for seg in road['displaySegments']:
  svg.append('<polyline points="'+' '.join(','.join(map(str,project(p))) for p in seg)+'" fill="none" stroke="cyan" stroke-width="2"/>')
for i,e in enumerate(points):
 x,y=e['projectedPx'];svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="cyan"/>')
 if e['imagePx']:
  u,v=e['imagePx'];svg.append(f'<circle cx="{u}" cy="{v}" r="7" fill="none" stroke="yellow"/><path d="M{x},{y} L{u},{v}" stroke="red"/><text x="{u+9}" y="{v}" fill="red">{i}: {e["errorPixels"]:.1f}px</text>')
svg.append('</svg>');(OUT/'road-diagnostic.svg').write_text('\n'.join(svg))
print(json.dumps(fit,indent=2))
