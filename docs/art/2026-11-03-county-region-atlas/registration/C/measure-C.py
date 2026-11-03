"""Reproduce manual C correspondence fit; diagnostic overlay only, never art mutation."""
import json, math, hashlib
from pathlib import Path
from PIL import Image, ImageDraw
OUT=Path(__file__).resolve().parent
ATLAS=OUT.parent.parent
ART=ATLAS/'images/REGION-C-v1.png'
STRUCT=ATLAS/'planning/structures/REGION-C-structure.json'
r=json.loads(STRUCT.read_text()); origin=r['originMap']; q=math.sqrt(.5); st=math.sin(math.radians(62.5))
def axis(p):
    x,y=p[0]-origin[0],p[1]-origin[1]
    return [(x-y)*q,(x+y)*q*st]
controls=[
 dict(id='J-1623821663',sourceNodeId='1623821663',sourceMap=[-1611.54,155.21],imagePx=[651,319],confidence='high',manualPixelUncertainty=7,usedInFit=True,observation='Upper transverse T junction; road centre inferred at centreline crossing, not zebra edge.'),
 dict(id='J-1623821721',sourceNodeId='1623821721',sourceMap=[-1546.47,184.88],imagePx=None,confidence='unpaired',manualPixelUncertainty=None,usedInFit=False,observation='Lower expected junction is obscured/replaced by foreground housing; no reliable branch centre can be paired.'),
 dict(id='EDGE-149397380-left',sourceMap=[-1636.1963176064444,244],imagePx=[20,625],confidence='medium',manualPixelUncertainty=12,usedInFit=True,observation='Main 8m road exits left art boundary. Centreline approximate because generated silhouette extends into canvas edge.'),
 dict(id='EDGE-149397380-upper',sourceMap=[-1603.6841238379232,124],imagePx=[824,252],confidence='medium',manualPixelUncertainty=12,usedInFit=False,observation='Main-road upper edge exit; contour not a surveyed square edge.'),
 dict(id='EDGE-149396514-right',sourceMap=[-1532.6138418519963,124],imagePx=[1200,598],confidence='medium',manualPixelUncertainty=12,usedInFit=True,observation='Lower transverse road right edge exit, approximate centre.'),
 dict(id='EDGE-149396750-bottom',sourceMap=[-1549.278932330827,244],imagePx=None,confidence='unpaired',manualPixelUncertainty=None,usedInFit=False,observation='Expected lower branch edge does not match visible bottom stub; no trustworthy correspondence.'),
 dict(id='EDGE-149397463-right',sourceMap=[-1520,182.6603989145183],imagePx=None,confidence='unpaired',manualPixelUncertainty=None,usedInFit=False,observation='Expected continuation from lower T toward right/bottom is covered/replaced by housing; no reliable visible road pair.'),
 dict(id='EDGE-1047748330-upper',sourceMap=[-1640,137.72630350194555],imagePx=None,confidence='unpaired',manualPixelUncertainty=None,usedInFit=False,observation='Source service road has no reliable drawn match near top buildings; do not invent point.'),
]
fit=[c for c in controls if c['usedInFit']];a=[axis(c['sourceMap']) for c in fit];b=[c['imagePx'] for c in fit]
ma=[sum(v[k] for v in a)/len(a) for k in [0,1]];mb=[sum(v[k] for v in b)/len(b) for k in [0,1]]
s=sum(sum((x[k]-ma[k])*(y[k]-mb[k]) for k in [0,1]) for x,y in zip(a,b))/sum(sum((x[k]-ma[k])**2 for k in [0,1]) for x in a)
anchor=[mb[k]-s*ma[k] for k in [0,1]]
def project(p):return [anchor[k]+s*axis(p)[k] for k in [0,1]]
for c in controls:
    c['projectedPx']=project(c['sourceMap']);c['errorPixels']=math.dist(c['projectedPx'],c['imagePx']) if c['imagePx'] else None
errors=[c['errorPixels'] for c in fit];allerrors=[c['errorPixels'] for c in controls if c['imagePx']]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Narrow inner main-road corridor, excluding A overlap and both uncertain exits.
coverage=[[-1619.13,185],[-1627.38,215],[-1628.58,215],[-1620.33,185]]
info=dict(method='fixed 62.5deg/45deg axes, positive uniform scale plus translation; one junction and two medium-confidence road edges',nativePixelsPerUnit=s,anchorMap=origin,anchorPixel=anchor,anchorUV=[x/1254 for x in anchor],fitControlCount=3,fitRmsResidualPixels=math.sqrt(sum(x*x for x in errors)/len(errors)),fitMaxResidualPixels=max(errors),allObservedMaxResidualPixels=max(allerrors),rotationDegrees=0,nonUniformScale=False)
record=dict(id='REGION-C-v1-registration',sourceArt=dict(file=str(ART),sha256=sha(ART),nativeSize=[1254,1254]),sourceGeometry=dict(file=str(STRUCT),sha256=sha(STRUCT)),projection=dict(originMap=origin,elevationDeg=62.5,azimuthDeg=45,canvasYDown=True),fit=info,controlPoints=controls,routeCoverageMapPolygon=coverage,coverageInterpretation='Proposed 30m long, 1.2m x-width interior centre corridor of main road 149397380 only; excludes A overlap, uncertain exits, lower branch, and unpaired service road. PM must decide if tolerable; not automatic route acceptance.',status='preview-only-pending-PM',limitations=['Manual observations have 7–12 native pixel uncertainty.','Only one reliable junction; two other noncollinear fit points are medium-confidence road-edge observations.','Missing service road and branch continuation are real production limitations.','No art warp, rotation, pixel modification, game testing or user acceptance.'])
(OUT/'measurement.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id='REGION-C',file='REGION-C-v1.png',sha256=sha(ART),nativeSize=[1254,1254],anchorMap=origin,anchorUV=info['anchorUV'],nativePixelsPerUnit=s,sortOrder=2,registration=dict(status='preview-only',evidence=str(OUT/'measurement.json'),controlPoints=[dict(map=c['sourceMap'],pixel=c['imagePx'],confidence=c['confidence'],residualPixels=c['errorPixels']) for c in controls if c['imagePx']],maxResidualPixels=max(allerrors),routeCoverageMapPolygon=coverage),ownershipPolygonUV=None,note='Measured uniform fit; PM selects ready status. Missing branches and overlapping buildings preclude seamlessness claim.')
(OUT/'region-C-runtime-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
im=Image.new('RGB',(1254,1254),'#24242a');art=Image.open(ART).convert('RGBA');im.paste(art,mask=art.getchannel('A'));d=ImageDraw.Draw(im)
for road in r['roads']:
    for seg in road['displaySegments']:d.line([tuple(project(p)) for p in seg],fill='#00ffe0',width=3)
d.line([tuple(project(p)) for p in coverage+[coverage[0]]],fill='#ff00ff',width=2)
for i,c in enumerate(controls):
    if c['imagePx']:
        x,y=c['imagePx'];d.ellipse((x-6,y-6,x+6,y+6),outline='yellow',width=2);d.line([tuple(c['imagePx']),tuple(c['projectedPx'])],fill='red',width=2);d.text((x+7,y+7),f'{i}: {c["errorPixels"]:.1f}px',fill='white')
im.save(OUT/'C-road-correspondence-diagnostic.png')
print(json.dumps(info,indent=2))
