"""Production manual-point measurement; no game/test operation or native art mutation."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent; BASE=OUT.parent.parent
ART=OUT/'REGION-C-v3.png'; STRUCT=BASE/'planning/structures/REGION-C-structure.json'
r=json.loads(STRUCT.read_text());origin=r['originMap'];q=math.sqrt(.5);st=math.sin(math.radians(62.5))
def axis(p):
 x,y=p[0]-origin[0],p[1]-origin[1];return [(x-y)*q,(x+y)*q*st]
def c(id,map,pixel,confidence,fit,note,unc=12):return dict(id=id,sourceMap=map,imagePx=pixel,confidence=confidence,usedInFit=fit,manualPixelUncertainty=unc,observation=note)
controls=[
 c('J-1623821663',[-1611.54,155.21],[555,339],'high',True,'Centre of restored upper T, clear road crossing.',10),
 c('J-1623821721',[-1546.47,184.88],[767,820],'high',True,'Restored lower junction crossing, all branches visible.',10),
 c('EDGE-149397380-left',[-1636.1963176064444,244],[20,628],'medium',True,'Main road left exit centre, generated silhouette approximate.'),
 c('EDGE-149397380-upper',[-1603.6841238379232,124],[827,233],'medium',False,'Main road upper-right exit centre.'),
 c('EDGE-149396514-right',[-1532.6138418519963,124],[1201,590],'medium',False,'Lower transverse road right exit centre.'),
 c('EDGE-149396750-bottom',[-1549.278932330827,244],[423,1092],'medium',False,'Restored lower branch near lower-left boundary; original junction now visible.'),
 c('EDGE-149397463-right',[-1520,182.6603989145183],[898,929],'medium',False,'Right branch exit beyond new row housing.'),
 c('EDGE-1047748330-upper',[-1640,137.72630350194555],[568,122],'medium',False,'Distinct narrow service lane entrance, separate from through spur.'),
 c('END-1047748330',[-1614.26,142.19],[660,260],'medium',False,'Service lane dead end turnaround, no join to main road.'),
 c('EDGE-149397509-upper',[-1640,153.31650355169694],[472,186],'medium',False,'Separate T spur at upper-left outline.'),
 c('EDGE-1046196060-first',[-1520,242.33549646017698],[578,1187],'low',False,'Short bottom roadway visible, ambiguous exact boundary; no continuity assertion.',20),
 c('EDGE-1046196060-last',[-1533.3680810234541,244],[480,1100],'low',False,'Other short-road end close to lower branch but source is separate within render bounds.',20),
]
fit=[v for v in controls if v['usedInFit']];a=[axis(v['sourceMap'])for v in fit];b=[v['imagePx']for v in fit];ma=[sum(v[k]for v in a)/len(a)for k in [0,1]];mb=[sum(v[k]for v in b)/len(b)for k in [0,1]]
s=sum(sum((x[k]-ma[k])*(y[k]-mb[k])for k in [0,1])for x,y in zip(a,b))/sum(sum((x[k]-ma[k])**2 for k in [0,1])for x in a);anchor=[mb[k]-s*ma[k]for k in [0,1]]
def project(p):return [anchor[k]+s*axis(p)[k]for k in [0,1]]
for v in controls:v['projectedPx']=project(v['sourceMap']);v['errorPixels']=math.dist(v['imagePx'],v['projectedPx'])if v['imagePx']else None
errors=[v['errorPixels']for v in fit];allerr=[v['errorPixels']for v in controls if v['imagePx']]
# Existing narrow internal upper-main-road corridor; not seam or full-route acceptance.
coverage=[[-1613.63,165],[-1630.03,225],[-1631.23,225],[-1614.83,165]]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
info=dict(nativePixelsPerUnit=s,anchorMap=origin,anchorPixel=anchor,anchorUV=[x/1254 for x in anchor],fitControlCount=len(fit),fitRmsResidualPixels=math.sqrt(sum(e*e for e in errors)/len(errors)),fitMaxResidualPixels=max(errors),allObservedMaxResidualPixels=max(allerr),method='fixed62.5/45; uniform scale and translation only; two junctions and one medium edge',nonUniformScale=False)
record=dict(id='REGION-C-v3-registration',sourceArt=dict(file=str(ART),sha256=sha(ART),nativeSize=[1254,1254]),sourceGeometry=dict(file=str(STRUCT),sha256=sha(STRUCT)),fit=info,controlPoints=controls,routeCoverageMapPolygon=coverage,status='preview-only',limitations=['Manual observations 10–20px uncertainty.','Upper and lower source topology restored visibly, residual shape distortion remains.','New service road/short-road are manually paired with medium/low certainty; no surveyed ground truth.','No ownership or seam closure, no game testing.'])
(OUT/'measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id='REGION-C',file='REGION-C-v3.png',sha256=sha(ART),nativeSize=[1254,1254],anchorMap=origin,anchorUV=info['anchorUV'],nativePixelsPerUnit=s,sortOrder=2,registration=dict(status='preview-only',evidence=str(OUT/'measurement.json'),controlPoints=[dict(map=v['sourceMap'],pixel=v['imagePx'],confidence=v['confidence'],residualPixels=v['errorPixels'])for v in controls if v['imagePx']],maxResidualPixels=max(allerr),routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='Native whole-scene repaired C3. PM selects ready only after seam/coverage review.')
(OUT/'region-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
im=Image.new('RGB',(1254,1254),'#303038');art=Image.open(ART);im.paste(art,mask=art.getchannel('A'));d=ImageDraw.Draw(im)
for road in r['roads']:
 for seg in road['displaySegments']:d.line([tuple(project(p))for p in seg],fill='#00ffee',width=3)
for i,v in enumerate(controls):
 if v['imagePx']:
  x,y=v['imagePx'];d.ellipse((x-5,y-5,x+5,y+5),outline='yellow',width=2);d.line([tuple(v['imagePx']),tuple(v['projectedPx'])],fill='red',width=2);d.text((x+5,y+5),f'{i}:{v["errorPixels"]:.1f}px',fill='white')
d.line([tuple(project(p))for p in coverage+[coverage[0]]],fill='#ff00ff',width=2)
im.save(OUT/'C-v3-road-diagnostic.png');print(json.dumps(info,indent=2));print([(v['id'],round(v['errorPixels'],1))for v in controls])
