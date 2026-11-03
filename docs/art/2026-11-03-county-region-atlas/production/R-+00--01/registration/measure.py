"""Manual production measurement. Only writes this registration directory; no art editing."""
import json, math, hashlib
from pathlib import Path
from PIL import Image
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=next(p for p in OUT.parents if (p/'AGENTS.md').exists())
def rel(p): return str(p.relative_to(ROOT))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
art=BASE/'art/R-+00--01-v1.png'; struct=BASE/'input/structures/R-+00--01-structure.json';r=json.loads(struct.read_text()); origin=r['originMap'];size=list(Image.open(art).size)
# Native image visually read at full image view, rounded pixel centres. Hypotheses, not survey.
raw=[('NW-main-turn',[-1638.05,-66.78],[540,155],'medium',9,True,'Upper main road corner: transverse road meets short upper-left exit.'),('NE-main-cross',[-1558.66,-60.8],[900,548],'high',6,True,'Large right-hand four-arm zebra crossing.'),('SW-main-cross',[-1573.85,6.91],[465,779],'high',6,True,'Lower-left four-arm zebra crossing; narrow service road joins here.'),('service-bend',[-1607.45,-2.4],[353,580],'medium',9,False,'Service-road elbow with west spur; no distinct zebra crossing.'),('service-end',[-1602.75,-52.16],[631,386],'medium',10,False,'Visible service road dead end near small tower; endpoint centre is partly ambiguous.'),('west-overlap',[-1640,23.61957376557106],[61,596],'medium',10,False,'Road centre at upper-left end of lower perimeter street; A EDGE-05 counterpart.'),('A-main-overlap',[-1577.55159925616,20.0],[378,825],'medium',9,False,'Main road centre in A overlap; A EDGE-08 native [951,393].'),('service-spur-end',[-1617.26,20.89],None,'unpaired',None,False,'No distinct precise endpoint on painted perimeter; retain null rather than using a projected point.')]
q=math.sqrt(.5); st=math.sin(math.radians(62.5))
def axis(p): x,y=p[0]-origin[0],p[1]-origin[1];return [(x-y)*q,(x+y)*q*st]
fit=[v for v in raw if v[5]];aa=[axis(v[1]) for v in fit];bb=[v[2] for v in fit];ma=[sum(v[k] for v in aa)/3 for k in (0,1)];mb=[sum(v[k] for v in bb)/3 for k in (0,1)]
s=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in (0,1)) for a,b in zip(aa,bb))/sum(sum((a[k]-ma[k])**2 for k in (0,1)) for a in aa); anchor=[mb[k]-s*ma[k] for k in (0,1)]
def project(p):return [anchor[k]+s*axis(p)[k] for k in (0,1)]
controls=[]
for id,p,px,c,u,f,n in raw:
 pred=project(p);controls.append(dict(id=id,sourceMap=p,imagePx=px,confidence=c,manualPixelUncertainty=u,usedInFit=f,observation=n,projectedPx=pred,errorVectorPixels=[pred[k]-px[k] for k in (0,1)] if px else None,errorPixels=math.dist(pred,px) if px else None,hiddenEstimate=False))
ferr=[e['errorPixels'] for e in controls if e['usedInFit']];err=[e['errorPixels'] for e in controls if e['imagePx']]
# Narrow source main-road strip, excluding end crossings and all seams. Candidate only.
coverage=[[-1562,-50],[-1558,-50],[-1569,-2],[-1573,-2]]
fitinfo=dict(method='least squares uniform positive scale and translation, fixed 62.5/45 axes',anchorMap=origin,anchorPixel=anchor,anchorUV=[anchor[k]/size[k] for k in (0,1)],nativePixelsPerUnit=s,rotationDegrees=0,nonUniformScale=False,fitRmsResidualPixels=math.sqrt(sum(x*x for x in ferr)/3),fitMaxResidualPixels=max(ferr),allObservedMaxResidualPixels=max(err))
a=ROOT/'docs/art/2026-11-03-whole-region-map/REGION-A-v3.png'
seams=[]
for seam in r['neighborSharedRoadControls']:
 seams.append(dict(seamId=seam['seamId'],regions=seam['regions'],overlapBounds=seam['overlapBounds'],sourceRoadSegments=seam['sourceRoadSegments'],actualNeighborImageInspected='REGION-A' in seam['regions'],complementaryOwnershipPolygonUV=None,seamReady=False,note='16m shared source strip; source controls alone do not establish painted correspondence. Whole-building ownership unresolved.'))
record=dict(schemaVersion=1,id=r['id'],sourceArt=dict(file=rel(art),sha256=sha(art),nativeSize=size),sourceGeometry=dict(file=rel(struct),sha256=sha(struct),city=r['source']),provenance=[dict(file=rel(p),sha256=sha(p)) for p in [a,BASE/'generation-record.json',BASE/'input/prompts/R-+00--01-v1.json',BASE/'input/source-manifest.json',BASE/'input/guides/R-+00--01-structure-neutral.png']],projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=fitinfo,controlPoints=controls,routeCoverageMapPolygon=coverage,coverageStatus='candidate main-road interior only; PM must approve; manual residuals do not guarantee every pixel',seams=seams,hiddenEstimates=[],runtimeStatus='preview-only',seamReady=False,limitations=['Manual correspondences carry explicit uncertainty; no invisible points inferred as observations.','No art pixels changed, no road moved, no game tests or deployment.','Neighbor A inspected but complementary ownership not authored. Other neighbors not inspected.'])
write('measurement.json',record)
entry=dict(id=r['id'],file=rel(art),sha256=sha(art),nativeSize=size,anchorMap=origin,anchorUV=fitinfo['anchorUV'],nativePixelsPerUnit=s,sortOrder=0,registration=dict(status='preview-only',evidence=rel(OUT/'measurement.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence'],residualPixels=e['errorPixels']) for e in controls if e['imagePx']],maxResidualPixels=max(err),routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,seamReady=False,note='PM readiness decision pending. file is checkout-relative; packager must copy byte-identically and rebase. No deployment implied.')
write('region-entry.json',entry)
# Vector diagnostic: native external image reference, no raster rewriting/resampling.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1254" height="1254" viewBox="0 0 1254 1254">','<image href="../art/R-+00--01-v1.png" width="1254" height="1254"/>']
for road in r['roads']:
 for seg in road['displaySegments']:
  pts=' '.join(','.join(str(v) for v in project(p)) for p in seg);svg.append(f'<polyline points="{pts}" fill="none" stroke="cyan" stroke-width="2"/>')
for e in controls:
 x,y=e['projectedPx'];svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="none" stroke="cyan"/>')
 if e['imagePx']:
  u,v=e['imagePx'];svg.append(f'<path d="M{x},{y} L{u},{v}" stroke="red"/><circle cx="{u}" cy="{v}" r="5" fill="yellow"/><text x="{u+8}" y="{v}" fill="red" font-size="14">{e["id"]}: {e["errorPixels"]:.1f}px</text>')
svg.append('</svg>');(OUT/'road-diagnostic.svg').write_text('\n'.join(svg))
print(json.dumps(fitinfo));print([(e['id'],e['errorPixels']) for e in controls])
