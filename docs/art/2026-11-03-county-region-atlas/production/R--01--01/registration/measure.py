"""Production measurement only: fixed axes, no native art writes, no game execution."""
import json,math,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent; B=D.parent; ROOT=Path.cwd()
def rel(p):return str(p.relative_to(ROOT))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
S=B/'input/structures/R--01--01-structure.json'; A=B/'art/R--01--01-v2.png'; N=B.parent/'R--01-+00/art/R--01-+00-v1.png'
r=json.loads(S.read_text()); origin=r['originMap']; q=math.sqrt(.5); t=math.sin(math.radians(62.5))
def axis(p):return [(p[0]-origin[0]-p[1]+origin[1])*q,(p[0]-origin[0]+p[1]-origin[1])*q*t]
# Native 1254-square manually observed, not guide-derived pixels.
obs=[('west-junction',[-1704.07,24.61],[200,756],'medium',10,True,'Service tee and adjacent junction merge at this drawing scale.'),('service-end',[-1703.12,-29.86],[443,628],'medium',8,True,'Visible rounded dead-end centre, between west glass building and long central block.'),('east-junction',[-1638.05,-66.78],[1085,635],'medium',10,True,'Curving main road meets short branch toward right alpha edge.'),('upper-west-edge',[-1744,-40.379758798917095],[510,160],'medium',10,False,'Main curved road enters upper-left diamond edge.'),('upper-branch-edge',[-1744,-66.22123711340208],[610,63],'low',12,False,'Upper straight road visible entry; contour uncertain.'),('lower-road-bend',[-1637.44,23.58],[555,1120],'low',18,False,'No distinct source bend: nearest drawn lower perimeter road location is a hypothesis.'),('north-edge-unpaired',[-1694.7274285714286,-84],None,'unpaired',None,False,'Generated upper road merges with main curve; exact edge crossing cannot be identified.' )]
e=[dict(id=i,sourceMap=p,imagePx=px,confidence=c,manualPixelUncertainty=u,usedInFit=f,observation=n,hiddenEstimate=False) for i,p,px,c,u,f,n in obs]
f=[x for x in e if x['usedInFit']];aa=[axis(x['sourceMap']) for x in f];bb=[x['imagePx'] for x in f]; ma=[sum(p[k] for p in aa)/3 for k in (0,1)];mb=[sum(p[k] for p in bb)/3 for k in (0,1)]
s=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in (0,1)) for a,b in zip(aa,bb))/sum(sum((a[k]-ma[k])**2 for k in (0,1)) for a in aa);anchor=[mb[k]-s*ma[k] for k in (0,1)]
def project(p):return [anchor[k]+s*axis(p)[k] for k in (0,1)]
for x in e:
 x['projectedPx']=project(x['sourceMap']);x['errorVectorPixels']=[x['projectedPx'][k]-x['imagePx'][k] for k in (0,1)] if x['imagePx'] else None;x['errorPixels']=math.dist(x['projectedPx'],x['imagePx']) if x['imagePx'] else None
fit=dict(method='unweighted least squares positive uniform scale plus translation; fixed elevation 62.5 azimuth 45; no rotation/warp',anchorMap=origin,anchorPixel=anchor,anchorUV=[v/1254 for v in anchor],nativePixelsPerUnit=s,fitRmsResidualPixels=math.sqrt(sum(x['errorPixels']**2 for x in f)/3),fitMaxResidualPixels=max(x['errorPixels'] for x in f),allObservedMaxResidualPixels=max(x['errorPixels'] for x in e if x['imagePx']))
seams=r['neighborSharedRoadControls']
for seam in seams:
 seam['status']='unresolved-no-complementary-ownership';seam['paintingStatus']='this-v2-present; neighbor only R--01-+00 visually inspected';seam['ownershipPolygonUV']=None
record=dict(schemaVersion=1,id=r['id'],sourceArt=dict(file=rel(A),sha256=sha(A),nativeSize=[1254,1254]),sourceGeometry=dict(file=rel(S),sha256=sha(S),citySha256=r['source']['sha256']),neighborArt=dict(file=rel(N),sha256=sha(N)),provenance=dict(generationRecord=rel(B/'generation-record.json'),generationRecordSha256=sha(B/'generation-record.json'),fullPrompts=rel(B/'actual-prompts.json'),fullPromptsSha256=sha(B/'actual-prompts.json'),guideSha256=sha(B/'input/guides/R--01--01-structure-neutral.png')),fit=fit,controlPoints=e,routeCoverageMapPolygon=None,routeCoverageReason='No continuous source-road corridor certified after fixed fit: diagnostic shows significant interior displacement/occlusion. null means unapproved here; preview-only explicitly disables runtime route fallback.',seams=seams,seamReady=False,hiddenEstimates=[],limitations=['Manual 8–18px reading uncertainty; no surveyed claims.','Null crossing is not inferred from guide.','No art pixels changed; no source city edits; no game tests or deployment.'])
(D/'measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id=r['id'],file=rel(A),sha256=sha(A),nativeSize=[1254,1254],anchorMap=origin,anchorUV=fit['anchorUV'],nativePixelsPerUnit=s,sortOrder=0,registration=dict(status='preview-only',evidence=rel(D/'measurement.json'),controlPoints=[dict(map=x['sourceMap'],pixel=x['imagePx'],confidence=x['confidence'],residualPixels=x['errorPixels']) for x in e],maxResidualPixels=fit['allObservedMaxResidualPixels'],routeCoverageMapPolygon=None),ownershipPolygonUV=None,seamReady=False,note='Measured candidate only; PM decides ready. No certified route coverage or complementary ownership. Not deployed.')
(D/'region-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
# SVG diagnostic references immutable native image; no art raster manipulation.
svg=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1254 1254">','<image href="../art/R--01--01-v2.png" width="1254" height="1254"/>']
for road in r['roads']:
 for part in road['displaySegments']:
  svg.append('<polyline points="'+ ' '.join(','.join(str(round(v,2)) for v in project(p)) for p in part)+'" fill="none" stroke="cyan" stroke-width="3"/>')
for x in e:
 if x['imagePx']:
  u,v=x['imagePx'];a,b=x['projectedPx'];svg.append(f'<circle cx="{u}" cy="{v}" r="7" fill="none" stroke="yellow"/><path d="M{u},{v} L{a},{b}" stroke="red"/><text x="{u+8}" y="{v}" fill="red">{x["id"]}: {x["errorPixels"]:.1f}px</text>')
svg.append('</svg>');(D/'road-diagnostic.svg').write_text('\n'.join(svg));print(json.dumps(fit,indent=2))
