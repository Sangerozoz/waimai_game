"""Manual production annotation and fixed-axis fit. Never changes native art/city."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
BASE=Path('docs/art/2026-11-03-county-region-atlas'); OUT=BASE/'registration/D'
ART=BASE/'images/REGION-D-v2.png'; STRUCT=BASE/'planning/structures/REGION-D-structure.json'
s=json.loads(STRUCT.read_text()); origin=s['originMap']; q=math.sqrt(.5); t=math.sin(math.radians(62.5)); size=Image.open(ART).size
# Pixel positions read visually on native 1254-square image. They are hypotheses with stated uncertainty.
E=[]
def add(id,p,px,conf,unc,note,fit=False): E.append(dict(id=id,sourceMap=p,imagePx=px,confidence=conf,manualPixelUncertainty=unc,observation=note,usedInFit=fit))
add('J-east-1623821696',[-1435.92,175.61],[906,749],'high',7,'Distinct centre of central diagonal road and right-side transverse street.',True)
add('J-south-9621089056',[-1436.27,231.91],[626,993],'medium',10,'Lower crossing. Two nearby parallel source roads and 5.54m connector have been visually merged; assigning primary 9621089056 is approximate.',True)
add('EDGE-west-main',[-1536,184.00205427408412],[365,310],'medium',9,'Centre of main diagonal road at upper-left art edge; boundary rendering differs from source square.',True)
add('EDGE-southwest',[-1533.3680810234541,244],[40,589],'medium',10,'Centre of lower-left outer road at image silhouette, not a surveyed common seam vertex.')
add('EDGE-east',[-1433.2571355060034,124],[1194,539],'medium',10,'Right edge continuation centre, inferred from continuous visible branch road.')
add('EDGE-north-stub',[-1532.6138418519963,124],[607,65],'low',16,'Top short road stub appears disconnected from art edge network; low confidence correspondence only.')
add('EDGE-right-1432482914',[-1416,173.47986565341296],[970,804],'low',14,'Short continuation after east crossing; silhouette partly shared with projecting building.')
add('PARALLEL-1189828550',[-1436.18,237.45],None,'unpaired',None,'No distinct visible second parallel road and 5.54m connecting link. Do not invent a separate intersection.')
add('EDGE-bottom-service',[-1432.209209005172,244],None,'unpaired',None,'No reliable separate service-road exit identifiable.')
def axis(p):
 x,y=p[0]-origin[0],p[1]-origin[1]; return [(x-y)*q,(x+y)*t*q]
f=[e for e in E if e['usedInFit']]; a=[axis(e['sourceMap']) for e in f]; b=[e['imagePx'] for e in f]; ma=[sum(v[k] for v in a)/len(a) for k in range(2)]; mb=[sum(v[k] for v in b)/len(b) for k in range(2)]
scale=sum(sum((x[k]-ma[k])*(y[k]-mb[k]) for k in range(2)) for x,y in zip(a,b))/sum(sum((x[k]-ma[k])**2 for k in range(2)) for x in a); anchor=[mb[k]-scale*ma[k] for k in range(2)]
def project(p):return [anchor[k]+scale*axis(p)[k] for k in range(2)]
for e in E:
 e['projectedPx']=project(e['sourceMap']); e['residualPixels']=math.dist(e['projectedPx'],e['imagePx']) if e['imagePx'] else None; e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in range(2)] if e['imagePx'] else None
errs=[e['residualPixels'] for e in E if e['imagePx']]; ferr=[e['residualPixels'] for e in f]
fit=dict(nativePixelsPerUnit=scale,anchorMap=origin,anchorPixel=anchor,anchorUV=[anchor[k]/size[k] for k in range(2)],method='Unweighted least squares; fixed 62.5deg/45deg axes; positive uniform scale and translation only',fitControlCount=len(f),fitRmsResidualPixels=math.sqrt(sum(v*v for v in ferr)/len(ferr)),fitMaxResidualPixels=max(ferr),allObservedMaxResidualPixels=max(errs),rotationDegrees=0,nonUniformScale=False)
# Narrow interior corridor around actually observed main road. Excludes all seams and south ambiguous junction.
coverage=[[-1518,176],[-1444,170],[-1444,181],[-1518,188]]
record=dict(schemaVersion=1,id='REGION-D-v2-registration',sourceArt=dict(file=str(ART),sha256=hashlib.sha256(ART.read_bytes()).hexdigest(),nativeSize=size),sourceGeometry=dict(file=str(STRUCT),sha256=hashlib.sha256(STRUCT.read_bytes()).hexdigest()),projection=s['projection'],fit=fit,controlPoints=E,routeCoverageMapPolygon=coverage,coverageInterpretation='Proposed narrow main-road interior corridor only; excludes ambiguous lower junction, exits, and all B-D/C-D seams. PM must decide whether measured errors permit route use.',runtimeStatus='preview-only-pending-PM',limitations=['Manual image observations, not exact survey.','Road topology merged at lower parallel roads; curve and margin drift remain.','No rotation, nonuniform scale, warp, original art edits, tests or runtime operations.'])
(OUT/'measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id='REGION-D',file=ART.name,sha256=record['sourceArt']['sha256'],nativeSize=size,anchorMap=origin,anchorUV=fit['anchorUV'],nativePixelsPerUnit=scale,sortOrder=3,registration=dict(status='preview-only',evidence=str(OUT/'measurement.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence'],residualPixels=e['residualPixels']) for e in E if e['imagePx']],maxResidualPixels=max(errs),routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='PM alone decides ready. Lower source parallel roads merge; edge seams and building ownership unresolved.')
(OUT/'region-D-runtime-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
im=Image.new('RGB',size,'#202027'); art=Image.open(ART).convert('RGBA'); im.paste(art,mask=art.getchannel('A')); d=ImageDraw.Draw(im)
for road in s['roads']:
 for part in road['displaySegments']:d.line([tuple(project(p)) for p in part],fill='#00ffdd',width=3)
for i,e in enumerate(E):
 x,y=e['projectedPx']; d.line([(x-6,y),(x+6,y)],fill='cyan',width=2);d.line([(x,y-6),(x,y+6)],fill='cyan',width=2)
 if e['imagePx']:
  u,v=e['imagePx'];d.ellipse((u-7,v-7,u+7,v+7),outline='yellow',width=2);d.line([(x,y),(u,v)],fill='red',width=2);d.text((u+8,v+7),str(i)+':'+str(round(e['residualPixels'],1)),fill='white')
d.line([tuple(project(p)) for p in coverage+[coverage[0]]],fill='#ff88ff',width=3)
im.save(OUT/'D-v2-correspondence-diagnostic.png')
print(json.dumps(fit,indent=2))
# Seam diagnostic: manually interpolated D road at B south boundary. Not an independent fit point.
bpath=BASE/'registration/registration-B-v3.json'; br=json.loads(bpath.read_text()); bf=br['fit']
p=[-1433.4969826589595,140]; fraction=(175.61-140)/(175.61-124); dpx=[906+fraction*(1194-906),749+fraction*(539-749)]
bcp=next(e for e in br['controlPoints'] if e['id']=='EDGE-S-149396391'); bpx=bcp['imagePx']
def inverse(px,fit):
 dx=(px[0]-fit['anchorPixel'][0])/fit['nativePixelsPerUnit']; dy=(px[1]-fit['anchorPixel'][1])/fit['nativePixelsPerUnit'];return [fit['anchorMap'][0]+(dx/q+dy/(t*q))/2,fit['anchorMap'][1]+(dy/(t*q)-dx/q)/2]
bmap=inverse(bpx,bf);dmap=inverse(dpx,fit)
seams=dict(B_D=dict(sourceMap=p,BObservedPx=bpx,DObservedPx=dpx,DConfidence='estimated-along-road',DManualPixelUncertainty=14,method='D linear interpolation along visible road from manually observed east crossing to exit; not independent surveyed point',BImpliedMap=bmap,DImpliedMap=dmap,deltaMapMetres=[dmap[k]-bmap[k] for k in range(2)],gapMapMetres=math.dist(bmap,dmap),gapAtDScalePixels=math.dist(bmap,dmap)*scale,note='Single east seam corridor only. West B-D road ends in disconnected D top stub; no reliable shared point, gap null.'),B_D_west=dict(gapMapMetres=None,reason='D top stub disconnected and low-confidence; no reliable shared visible vertex.'),C_D=dict(gapMapMetres=None,reason='C measured native counterpart unavailable in this task. D main west-edge residual retained; cannot report cross-art seam gap.'))
(OUT/'seam-diagnostics.json').write_text(json.dumps(seams,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(seams,indent=2))
