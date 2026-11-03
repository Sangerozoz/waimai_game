"""Recompute manual native-pixel observations. Writes registration data/SVG only; never edits art."""
import json, math, hashlib
from pathlib import Path
R=Path(__file__).resolve().parent; P=R.parent; root=Path.cwd()
S=P/'input/structures/R--02-+00-structure.json'; A=P/'art/R--02-+00-v2.png'
s=json.loads(S.read_text()); origin=s['originMap']; q=math.sqrt(.5); t=math.sin(math.radians(62.5))
def axis(p):
 x,y=p[0]-origin[0],p[1]-origin[1];return [(x-y)*q,(x+y)*q*t]
def item(id,p,px,confidence,note,fit=False):return dict(id=id,sourceMap=p,imagePx=px,confidence=confidence,manualPixelUncertainty=8 if confidence=='medium' else 15,observation=note,usedInFit=fit)
e=[item('J-9634601489',[-1788.73,72.35],[637,603],'medium','Visible lower-side tee into diagonal main road; centre read between curbs, not zebra stripe.',True),item('J-1623821437',[-1799.67,29.36],[841,427],'medium','Visible upper-right crossing centre. Extra top-left continuation is painted beyond source topology.',True),item('E-149396419',[-1728,25.186496635262447],[1165,654],'medium','Centre of road reaching right lower diamond edge, correspondence by continuous branch from crossing.',True),item('E-149396306-south',[-1783.1521064060803,140],[231,810],'medium','Main road lower-left ground boundary crossing.'),item('E-1047748330',[-1728,102.18837923060745],[787,980],'medium','Service branch from central tee exits lower-right ground edge.'),item('E-149396905',[-1848,82.52339159663865],[294,372],'low','Short left-upper road fragment at edge. Interior end hidden behind building/trees; weak correspondence.'),item('H-1623821543',[-1838.67,81.04],None,'unpaired','Short service-road terminus concealed by foreground architecture/trees. No reliable native pixel; hidden endpoint estimate deliberately null.')]
f=[v for v in e if v['usedInFit']]; aa=[axis(v['sourceMap']) for v in f];bb=[v['imagePx'] for v in f];ma=[sum(v[k] for v in aa)/len(aa) for k in (0,1)];mb=[sum(v[k] for v in bb)/len(bb) for k in (0,1)]
scale=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in (0,1)) for a,b in zip(aa,bb))/sum(sum((a[k]-ma[k])**2 for k in (0,1)) for a in aa);anchor=[mb[k]-scale*ma[k] for k in (0,1)]
def proj(p):return [anchor[k]+scale*axis(p)[k] for k in (0,1)]
for v in e:
 v['projectedPx']=proj(v['sourceMap']);v['errorVectorPixels']=[v['projectedPx'][k]-v['imagePx'][k] for k in (0,1)] if v['imagePx'] else None;v['errorPixels']=math.dist(v['projectedPx'],v['imagePx']) if v['imagePx'] else None
# Conservative interior main-road strip only. Proposed trust area; preview-only never enables route.
coverage=[[-1797.7,45],[-1793.7,45],[-1789.9,60],[-1793.9,60]]
fit=dict(method='fixed 62.5/45 axes; least squares positive uniform scale and translation on three observed noncollinear controls',anchorMap=origin,anchorPixel=anchor,anchorUV=[v/1254 for v in anchor],nativePixelsPerUnit=scale,fitMaxResidualPixels=max(v['errorPixels'] for v in f),fitRmsResidualPixels=math.sqrt(sum(v['errorPixels']**2 for v in f)/len(f)),allObservedMaxResidualPixels=max(v['errorPixels'] for v in e if v['imagePx']),rotationDegrees=0,nonUniformScale=False)
def source(p):return dict(file=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
neighbor=root/'docs/art/2026-11-03-county-region-atlas/repairs/R--01-+00/art/R--01-+00-v3.png'
m=dict(schemaVersion=1,id='R--02-+00',sourceArt=source(A),nativeSize=[1254,1254],sourceStructure=source(S),guide=source(Path(s['guide']['file'])),neighbor=source(neighbor),projection=dict(elevationDeg=62.5,azimuthDeg=45,originMap=origin),fit=fit,controlPoints=e,hiddenEstimate=dict(endpointImagePx=None,reason='Only edge stub visible; interior endpoint cannot be paired reliably.'),routeCoverageMapPolygon=coverage,coverageStatus='proposed interior main-road corridor; PM review required, excludes branch exits and hidden stub',seamReady=False,seams=[dict(seamId=v['seamId'],overlapBounds=v['overlapBounds'],sourceRoadSegments=v['sourceRoadSegments'],actualCorrespondence=None,ownershipPolygonUV=None,complementaryNeighborOwnership=None,status='unresolved') for v in s['neighborSharedRoadControls']],limitations=['Manual readings, not surveyed exact points.','Global residual is diagnostic, not a user acceptance threshold.','No complementary ownership exists. Neighbour has independently painted layout; style match is not seam evidence.','Source art and full prompt records reused in place, not regenerated or rewritten.','No deployment, game test, browser, typecheck or source-city change.'])
(R/'measurement.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
entry=dict(id='R--02-+00',file=str(A.relative_to(root)),sha256=m['sourceArt']['sha256'],nativeSize=[1254,1254],anchorMap=origin,anchorUV=fit['anchorUV'],nativePixelsPerUnit=scale,sortOrder=0,registration=dict(status='preview-only',evidence=str((R/'measurement.json').relative_to(root)),controlPoints=[dict(map=v['sourceMap'],pixel=v['imagePx'],confidence=v['confidence'],residualPixels=v['errorPixels']) for v in e if v['imagePx']],maxResidualPixels=fit['allObservedMaxResidualPixels'],routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='Measured candidate only; PM chooses ready and packaging-relative file path. Unresolved seams and hidden short spur retained.')
(R/'region-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1254" height="1254" viewBox="0 0 1254 1254">','<image href="../art/R--02-+00-v2.png" width="1254" height="1254"/>']
for road in s['roads']:
 for seg in road['displaySegments']:svg.append('<polyline points="'+ ' '.join(','.join(map(str,proj(p))) for p in seg)+'" fill="none" stroke="cyan" stroke-width="3"/>')
for i,v in enumerate(e):
 if v['imagePx']:
  x,y=v['imagePx'];a,b=v['projectedPx'];svg.append(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="yellow"/><path d="M{x},{y} L{a},{b}" stroke="red"/><text x="{x+8}" y="{y}" fill="red">{i}: {v["errorPixels"]:.1f}px</text>')
svg.append('</svg>');(R/'road-diagnostic.svg').write_text('\n'.join(svg));print(json.dumps(fit,indent=2))
