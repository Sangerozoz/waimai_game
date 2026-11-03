"""Production correspondence annotation; never mutates native art or source city."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path('docs/art/2026-11-03-county-region-atlas/registration');ROOT.mkdir(parents=True,exist_ok=True)
ART=Path('docs/art/2026-11-03-whole-region-map/REGION-A-v3.png');STRUCT=Path('docs/art/2026-11-03-whole-region-map/region-A-structure.json');CITY=Path('delivery-game/assets/resources/map-sample/city.json')
r=json.loads(STRUCT.read_text());city=json.loads(CITY.read_text());nodes={n['id']:[n['x'],n['y']] for n in city['nodes']};q=math.sqrt(.5);st=math.sin(math.radians(62.5));origin=r['originMap']
def axis(p):
 x,y=p[0]-origin[0],p[1]-origin[1];return [(x-y)*q,(x+y)*st*q]
# Manually read on A-v3 native 1254px measurement grid. Pixel uncertainty is explicit.
entries=[]
def add(id,p,px,conf,uncert,note,fit=False):entries.append(dict(id=id,sourceMap=p,imagePx=px,confidence=conf,manualPixelUncertainty=uncert,observation=note,usedInFit=fit))
add('J1-1623821577',nodes['1623821577'],[446,633],'high',5,'Main 8m road crossing transverse road. Source nearby side-road tee is only ~2m away and visually merged.',True)
add('J2-1623821431',nodes['1623821431'],[831,442],'high',5,'Upper-right main-road junction with branch to top edge.',True)
add('J3-1623821610',nodes['1623821610'],[722,994],'high',5,'Lower junction of transverse road and lower perimeter road.',True)
# Out-of-fit validation controls: visual correspondence hypotheses, never exact surveyed points.
observed={0:([269,437],'medium',7),1:([66,697],'low',12),2:([39,655],'low',12),3:(None,'unpaired',None),4:([530,1114],'medium',7),5:([621,86],'medium',7),6:([1014,851],'medium',7),7:([169,770],'high',5),8:([951,393],'high',5),9:([792,1036],'medium',7)}
for i,(px,conf,unc) in observed.items():
 cp=r['controlPoints'][i]
 add('EDGE-%02d-%s'%(i,cp['roadId']),cp['map'],px,conf,unc,'Source road region-edge intersection; drawn edge/corridor centre read manually. Region-edge ownership is not yet fixed.' if px else 'Sub-metre source road stub at minY boundary has no reliable visible match; do not invent an image point.')
for id,p,px in [('CORNER-N',[-1640,20],[633,60]),('CORNER-E',[-1520,20],[1221,655]),('CORNER-S',[-1520,140],[612,1201]),('CORNER-W',[-1640,140],[22,654])]:add(id,p,px,'low',12,'Nominal square corner matched to approximate visible ground contour; generated boundary is not an exact projected square.')
fit=[e for e in entries if e['usedInFit']];a=[axis(e['sourceMap']) for e in fit];b=[e['imagePx'] for e in fit];ma=[sum(p[k] for p in a)/len(a) for k in [0,1]];mb=[sum(p[k] for p in b)/len(b) for k in [0,1]]
scale=sum(sum((x[k]-ma[k])*(y[k]-mb[k]) for k in [0,1]) for x,y in zip(a,b))/sum(sum((x[k]-ma[k])**2 for k in [0,1]) for x in a);anchor=[mb[k]-scale*ma[k] for k in [0,1]]
def project(p):return [anchor[k]+scale*axis(p)[k] for k in [0,1]]
for e in entries:
 e['projectedPx']=project(e['sourceMap']);e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in [0,1]] if e['imagePx'] else None;e['errorPixels']=math.dist(e['projectedPx'],e['imagePx']) if e['imagePx'] else None
ferr=[e['errorPixels'] for e in fit];allerr=[e['errorPixels'] for e in entries if e['imagePx']];reliable=[e['errorPixels'] for e in entries if e['confidence'] in ['high','medium']]
fitinfo=dict(method='fixed 62.5deg/45deg axes, positive uniform scalar and 2D translation least squares on 3 manually observed junctions',nativePixelsPerUnit=scale,anchorMap=origin,anchorPixel=anchor,anchorUV=[v/1254 for v in anchor],fitControlCount=3,fitMaxResidualPixels=max(ferr),fitRmsResidualPixels=math.sqrt(sum(v*v for v in ferr)/len(ferr)),allObservedMaxResidualPixels=max(allerr),highMediumObservedMaxResidualPixels=max(reliable),rotationDegrees=0,nonUniformScale=False)
record=dict(schemaVersion=1,id='REGION-A-v3-registration',sourceArt=dict(file=str(ART),sha256=hashlib.sha256(ART.read_bytes()).hexdigest(),nativeSize=[1254,1254]),sourceGeometry=dict(file=str(STRUCT),sha256=hashlib.sha256(STRUCT.read_bytes()).hexdigest(),citySha256=hashlib.sha256(CITY.read_bytes()).hexdigest()),projection=dict(originMap=origin,elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=fitinfo,controlPoints=entries,interpretation='Topology broadly corresponding. User accepted art. Interior junction fit supports restrained preview/integration; edge correspondence drifts remain and require seam production, not source road edits.',runtimeStatus='preview-only-pending-PM-choice-of-usable-corridors',limitations=['Manual marks carry 5-12px reading uncertainty. This is not surveyed or automated registration.','Three fit controls do not establish exact all-pixel or all-road registration.','Ground corner observations are rough low-confidence diagnostics and not seam ownership vertices.','No image resampling, rotation, warp, source-road editing, game tests, or runtime rendering performed.'])
(ROOT/'registration-A.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id='REGION-A',file=ART.name,sha256=record['sourceArt']['sha256'],nativeSize=[1254,1254],anchorMap=origin,anchorUV=fitinfo['anchorUV'],nativePixelsPerUnit=scale,sortOrder=0,registration=dict(status='preview-only',evidence=str(ROOT/'registration-A.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence'],residualPixels=e['errorPixels']) for e in entries if e['imagePx']],maxResidualPixels=max(allerr)),ownershipPolygonUV=None,note='Measured fixed-axis uniform fit. Preview-only is a data-agent default, not an art rejection. PM can explicitly authorize route integration using observed interior road corridors, retaining edge residual evidence and without moving source roads.')
(ROOT/'region-A-runtime-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
# Diagnostic copy only; original remains byte-identical.
im=Image.new('RGB',(1254,1254),'#202027');art=Image.open(ART).convert('RGBA');im.paste(art,mask=art.getchannel('A'));d=ImageDraw.Draw(im)
for road in r['roads']:
 for part in road['displaySegments']:d.line([tuple(project(p)) for p in part],fill='#00ffdd',width=3)
for n,e in enumerate(entries):
 x,y=e['projectedPx'];d.line([(x-5,y),(x+5,y)],fill='#00ffdd',width=2);d.line([(x,y-5),(x,y+5)],fill='#00ffdd',width=2)
 if e['imagePx']:
  a,b=e['imagePx'];d.ellipse((a-6,b-6,a+6,b+6),outline='#ffff00',width=2);d.line([(x,y),(a,b)],fill='#ff5555',width=2);d.text((a+8,b+5),str(n)+':'+str(round(e['errorPixels'],1)),fill='white')
im.save(ROOT/'A-v3-road-correspondence-diagnostic.png')
print(json.dumps(fitinfo,indent=2))
