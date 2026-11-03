"""Production measurements only. No raster writes, source edits or runtime execution."""
import json, math, hashlib
from pathlib import Path
from PIL import Image
D=Path(__file__).resolve().parent; P=D.parent
S=P/'input/structures/R--01-+00-structure.json'; A=P/'art/R--01-+00-v1.png'
s=json.loads(S.read_text()); origin=s['originMap']; W,H=Image.open(A).size
root=Path.cwd()
def rel(p):return str(p.relative_to(root))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def axes(p):
 x,y=p[0]-origin[0],p[1]-origin[1];return [(x-y)/math.sqrt(2),(x+y)*math.sin(math.radians(62.5))/math.sqrt(2)]
# Native1254 px, manually observed after viewing original art and1536 guide.
obs=[('upper-junction',[-1705.91,24.91],[890,410],'medium',10,'149396505/149396419/149396705 intersection; close source nodes merge in paint.',True),('left-junction',[-1712.49,114.07],[320,695],'high',7,'149396505 crossing bent1047748330; centre of open asphalt intersection.',True),('lower-junction',[-1665.74,129.38],[450,943],'high',7,'1046196059 meets1047748330; centre of lower three-way junction.',True),('inner-elbow',[-1661.22,87.43],[700,748],'medium',10,'Visible elbow of internal service road, between campus forecourt and southern housing.',False),('top-exit',[-1744,25.386765814266486],[621,69],'medium',10,'Centre of road where it leaves upper ground tip.',False),('left-exit',[-1713.966306569343,140],[183,761],'medium',10,'Main road centre at left/lower ground edge.',False),('right-exit',[-1624,26.810874897792324],[1196,649],'medium',12,'Right ground-edge road centre; edge is irregular.',False),('bottom-exit',[-1630.3388970588235,140],[547,1126],'medium',12,'Lower service road exit at protruding ground tip.',False),('A-service-exit',[-1624,93.69208713621492],None,'unpaired',None,'Expected service exit on lower-right edge has no reliable continuous asphalt match; do not infer a point behind buildings.',False),('tiny-upper-stub',[-1703.9895979438222,20],None,'unpaired',None,'Short source branch cannot be distinguished reliably from upper junction/sidewalk.',False)]
f=[o for o in obs if o[-1]]; aa=[axes(o[1]) for o in f]; bb=[o[2] for o in f]; ma=[sum(a[k] for a in aa)/len(f) for k in (0,1)];mb=[sum(b[k] for b in bb)/len(f) for k in (0,1)]
scale=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in (0,1)) for a,b in zip(aa,bb))/sum(sum((a[k]-ma[k])**2 for k in (0,1)) for a in aa)
anchor=[mb[k]-scale*ma[k] for k in (0,1)]
def project(p):return [anchor[k]+scale*axes(p)[k] for k in (0,1)]
controls=[]
for id,p,px,c,u,n,fit in obs:
 pr=project(p);controls.append(dict(id=id,sourceMap=p,imagePx=px,confidence=c,manualPixelUncertainty=u,observation=n,usedInFit=fit,hiddenEstimate=False,projectedPx=pr,errorVectorPixels=[pr[k]-px[k] for k in (0,1)] if px else None,errorPixels=math.dist(pr,px) if px else None))
errs=[c['errorPixels'] for c in controls if c['imagePx']];fe=[c['errorPixels'] for c in controls if c['usedInFit']]
# Conservative central section of main road only. Proposed trust mask, not enabled runtime coverage.
p1=[-1710,80];p2=[-1709,65];corr=[[p1[0]-1,p1[1]],[p2[0]-1,p2[1]],[p2[0]+1,p2[1]],[p1[0]+1,p1[1]]]
fit=dict(method='fixed62.5/45 axes, one uniform positive least-squares scale and translation; no rotation/warp',anchorMap=origin,anchorPixel=anchor,anchorUV=[anchor[0]/W,anchor[1]/H],nativePixelsPerUnit=scale,fitMaxResidualPixels=max(fe),fitRmsResidualPixels=math.sqrt(sum(e*e for e in fe)/len(fe)),allObservedMaxResidualPixels=max(errs))
seams=[]
for seam in s['neighborSharedRoadControls']:
 seams.append(dict(seamId=seam['seamId'],regions=seam['regions'],overlapBounds=seam['overlapBounds'],sourceRoadSegments=seam['sourceRoadSegments'],widthMetres=16,actualPairedImageControls=None,ownershipPolygonUV=None,complementaryNeighborOwnership=None,seamReady=False,note='Source overlap only. No complementary natural building/ground ownership agreed. REGION-A inspected; other neighbor images not inspected in this task.'))
record=dict(schemaVersion=1,id=s['id'],sourceArt=dict(file=rel(A),sha256=sha(A),nativeSize=[W,H],reused=True),sourceStructure=dict(file=rel(S),sha256=sha(S)),provenance=dict(generationRecord=rel(P/'generation-record.json'),generationRecordSHA256=sha(P/'generation-record.json'),fullPrompt=rel(P/'input/prompts/R--01-+00-v1.json'),fullPromptSHA256=sha(P/'input/prompts/R--01-+00-v1.json'),guide=s['guide'],neighbor=dict(file='docs/art/2026-11-03-whole-region-map/REGION-A-v3.png',sha256=sha(Path('docs/art/2026-11-03-whole-region-map/REGION-A-v3.png')))),projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=fit,controlPoints=controls,routeCoverageMapPolygon=None,routeCoverageDecision='No enabled trustworthy polygon established: uniform fit residual must be inspected against open asphalt. Null is deliberate; preview-only disables routes. Do not promote null to ready fallback.',seams=seams,hiddenEstimatePolicy='No hidden image positions used. Unobservable controls remain null.',status='preview-only',seamReady=False)
(D/'measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id=s['id'],file=rel(A),sha256=sha(A),nativeSize=[W,H],anchorMap=origin,anchorUV=fit['anchorUV'],nativePixelsPerUnit=scale,sortOrder=0,registration=dict(status='preview-only',evidence=rel(D/'measurement.json'),controlPoints=[dict(map=c['sourceMap'],pixel=c['imagePx'],confidence=c['confidence'],residualPixels=c['errorPixels']) for c in controls],maxResidualPixels=max(errs),routeCoverageMapPolygon=None),ownershipPolygonUV=None,note='PM decision required. Native art reused. file is checkout-relative; packager must resolve/copy byte-identically. No route/rider coverage approved, no complementary seam ownership.')
(D/'region-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
# Vector diagnostic only; original raster referenced, never rewritten.
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1254" height="1254" viewBox="0 0 1254 1254"><rect width="1254" height="1254" fill="#222"/><image href="../art/R--01-+00-v1.png" width="1254" height="1254"/>']
for road in s['roads']:
 for seg in road['displaySegments']:
  svg.append('<polyline points="'+' '.join(','.join(str(v) for v in project(p)) for p in seg)+'" fill="none" stroke="cyan" stroke-width="2"/>')
for c in controls:
 x,y=c['projectedPx'];svg.append(f'<path d="M{x-5},{y}h10 M{x},{y-5}v10" stroke="cyan"/>')
 if c['imagePx']:
  u,v=c['imagePx'];svg.append(f'<circle cx="{u}" cy="{v}" r="6" fill="none" stroke="yellow"/><path d="M{x},{y}L{u},{v}" stroke="red"/><text x="{u+8}" y="{v}" fill="white" font-size="14">{c["id"]}:{c["errorPixels"]:.1f}</text>')
svg.append('</svg>');(D/'road-diagnostic.svg').write_text('\n'.join(svg));print(json.dumps(fit));print([(c['id'],c['errorPixels']) for c in controls])
