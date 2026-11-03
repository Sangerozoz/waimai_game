"""Production-only native-outline ownership and shared-world diagnostics, never edits sources."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,math,hashlib,copy
BASE=Path('docs/art/2026-11-03-county-region-atlas');OUT=BASE/'repairs/north-A/ownership'
package=json.loads((BASE/'runtime-package-ab/region-atlas.json').read_text());A,B=copy.deepcopy(package['regions']);N=json.loads((BASE/'production/R-+00--01/registration/region-entry.json').read_text())
ART_A=Path('docs/art/2026-11-03-whole-region-map/REGION-A-v3.png');ART_B=BASE/'images/REGION-B-v4.png';ART_N=BASE/'repairs/north-A/R-+00--01-v2.png'
q=2**-.5;t=math.sin(math.radians(62.5))
def tr(e):
 r=A['nativePixelsPerUnit']/e['nativePixelsPerUnit'];dx=e['anchorMap'][0]-A['anchorMap'][0];dy=e['anchorMap'][1]-A['anchorMap'][1];return r,[A['anchorUV'][0]*1254+A['nativePixelsPerUnit']*(dx-dy)*q-e['anchorUV'][0]*1254*r,A['anchorUV'][1]*1254+A['nativePixelsPerUnit']*(dx+dy)*q*t-e['anchorUV'][1]*1254*r]
def pxpoly(e):return [(u*1254,v*1254) for u,v in e['ownershipPolygonUV']]
def mask(poly):
 m=Image.new('L',(1254,1254));ImageDraw.Draw(m).polygon(poly,fill=255);return m
oldA,oldB=pxpoly(A),pxpoly(B)
# Existing AB split retained from the actual registered native points.
joinA=(1221.,655.);rB,oB=tr(B);joinB=((joinA[0]-oB[0])/rB,(joinA[1]-oB[1])/rB)
def skyline(path,legacy,xlo,xhi):
 alpha=Image.open(path).getchannel('A');owned=ImageChops.multiply(alpha,mask(legacy)).point(lambda v:255 if v>=128 else 0);ImageDraw.floodfill(owned,(600,600) if path==ART_A else (800,800),128);owned=owned.point(lambda v:255 if v==128 else 0);points=[]
 # 4px blocks use minimum actual alpha Y, padded 1px upward: retain complete roof/tree silhouettes.
 for x in range(math.floor(xlo),math.ceil(xhi),4):
  xe=min(x+4,math.ceil(xhi));ys=[]
  for xx in range(max(0,x),min(1254,xe)):
   col=owned.crop((xx,0,xx+1,1254));box=col.getbbox()
   if box:ys.append(box[1])
  y=max(0,min(ys)-1) if ys else 1254
  points.extend([(max(xlo,x),y),(min(xhi,xe),y)])
 return points
sa=skyline(ART_A,oldA,0,joinA[0]);sa[-1]=joinA
# A polygon starts with actual upper silhouette, then the UNCHANGED AB split below join.
idx=next(i for i,p in enumerate(oldA) if abs(p[0]-1221)<.01 and abs(p[1]-655)<.01)
newA=sa+oldA[idx+1:]
sb=skyline(ART_B,oldB,joinB[0],1254);sb[0]=joinB
# B top is actual owned silhouette, remainder follows old bottom/AB boundary exactly.
ib=min(range(len(oldB)),key=lambda i:math.dist(oldB[i],joinB))
newB=sb+[(1254,1254),(0,1254)]+oldB[3:ib+1]+[joinB]
A['ownershipPolygonUV']=[[x/1254,y/1254] for x,y in newA];B['ownershipPolygonUV']=[[x/1254,y/1254] for x,y in newB]
# Shared N lower boundary is the same actual A/B skyline, expressed once in A-native world units.
seam=sa+[(x*rB+oB[0],y*rB+oB[1]) for x,y in sb[1:]]
rN,oN=tr(N)
np=[((-1000-oN[0])/rN,(-1000-oN[1])/rN),((3000-oN[0])/rN,(-1000-oN[1])/rN)]+[((x-oN[0])/rN,(y-oN[1])/rN) for x,y in reversed(seam)]
def clip(poly,axis,bound,keep):
 out=[]
 for p,z in zip(poly,poly[1:]+poly[:1]):
  ip=(p[axis]-bound)*keep>=0;iz=(z[axis]-bound)*keep>=0
  if ip:out.append(p)
  if ip!=iz:
   k=(bound-p[axis])/(z[axis]-p[axis]);out.append(tuple(p[j]+k*(z[j]-p[j]) for j in (0,1)))
 return out
for axis,bound,keep in [(0,0,1),(0,1254,-1),(1,0,1),(1,1254,-1)]:np=clip(np,axis,bound,keep)
N['ownershipPolygonUV']=[[x/1254,y/1254] for x,y in np];N['file']=str(ART_N);N['sha256']=hashlib.sha256(ART_N.read_bytes()).hexdigest();N['sortOrder']=-1
# All entries are candidates; original ready AB authorization and corridors stay archived in source package.
for e in (A,B,N):
 e['registration']['status']='preview-only';e['ownershipEvidence']=str(OUT/'ownership-record.json');e['note']='Candidate actual-outline ownership. AB source authorization preserved; PM decides readiness.'
# N2 actually observed unchanged main junctions; retain old uniform transform, don't refit to hide boundary residuals.
measurement=json.loads((BASE/'production/R-+00--01/registration/measurement.json').read_text());measurement['sourceArt']={'file':str(ART_N),'sha256':N['sha256'],'nativeSize':[1254,1254]};measurement['fit']['method']='Inherited N1 uniform transform; N2 primary junctions visually reobserved unchanged. No refit after native edit.'
# Boundary patch was edited: do NOT carry unverifiable old overlap readings as new observation.
for e in measurement['controlPoints']:
 if e['id']=='A-main-overlap':
  e['imagePx']=[378,825];e['confidence']='estimated';e['manualPixelUncertainty']=12;e['observation']='Same visible main street at shared side; along-road read only, not independent junction.'
 if e['id']=='west-overlap':e['manualPixelUncertainty']=12;e['observation']='N2 perimeter street centre reobserved [61,596]; edge mismatch remains, no full seam closure claim.'
 e['reobservedOnVersion']='N2'
for c in measurement['controlPoints']:
 dx=c['sourceMap'][0]-N['anchorMap'][0];dy=c['sourceMap'][1]-N['anchorMap'][1]
 c['projectedPx']=[N['anchorUV'][0]*1254+N['nativePixelsPerUnit']*(dx-dy)*q,N['anchorUV'][1]*1254+N['nativePixelsPerUnit']*(dx+dy)*q*t]
 c['errorVectorPixels']=[c['projectedPx'][k]-c['imagePx'][k] for k in (0,1)] if c['imagePx'] else None
 c['errorPixels']=math.dist(c['projectedPx'],c['imagePx']) if c['imagePx'] else None
paired=[c for c in measurement['controlPoints'] if c['imagePx']];fitted=[c for c in paired if c['usedInFit']]
measurement['fit']['fitRmsResidualPixels']=math.sqrt(sum(c['errorPixels']**2 for c in fitted)/len(fitted));measurement['fit']['fitMaxResidualPixels']=max(c['errorPixels'] for c in fitted);measurement['fit']['allObservedMaxResidualPixels']=max(c['errorPixels'] for c in paired)
measurement['runtimeStatus']='preview-only';measurement['seamReady']=False;measurement['ownershipEvidence']=str(OUT/'ownership-record.json');measurement['limitations'].append('Actual-outline A/B/N ownership authored; N-A route crossing and B-N triangle remain restricted. No game operations.')
(OUT/'N2-measurement.json').write_text(json.dumps(measurement,ensure_ascii=False,indent=2)+'\n')
N['registration']['evidence']=str(OUT/'N2-measurement.json')
N['registration']['controlPoints']=[{'map':e['sourceMap'],'pixel':e['imagePx'],'confidence':e['confidence'],'residualPixels':e.get('errorPixels')} for e in measurement['controlPoints'] if e['imagePx']]
for e,name in [(A,'A-entry-candidate.json'),(B,'B-entry-candidate.json'),(N,'N-entry-candidate.json')]:
 (OUT/name).write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
losses={}
for e,path,old,new in [(A,ART_A,oldA,newA),(B,ART_B,oldB,newB)]:
 alpha=Image.open(path).getchannel('A');lost=ImageChops.subtract(ImageChops.multiply(alpha,mask(old)),ImageChops.multiply(alpha,mask(new)));hist=lost.histogram();losses[e['id']]={'oldOwnedPixelsExcludedAlpha128':sum(hist[128:]),'excludedNonzeroAlpha':sum(hist[1:]),'exclusionBounds':lost.getbbox()}
record={'method':'Largest connected opaque alpha>=128 silhouette measured in 4px blocks, padded upward1px; disconnected stray source pixels intentionally ignored; original AB split from join retained. Single shared world boundary translated to N native; no source resampling outside diagnostic.','ABJoinInANative':joinA,'ABJoinInBNative':joinB,'boundaryInANativePixels':seam,'transforms':{'B':{'scale':rB,'offset':oB},'N':{'scale':rN,'offset':oN}},'lossMeasurements':losses,'defaultStatus':'preview-only','sourceReadyCorridorsUnchanged':True,'NRoute':'Only previous interior corridor, no seam road authorization','BNTriangle':'Native display candidates only; neighboring northeast region still unmade in this package, no full seam claim','nativeSources':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (ART_A,ART_B,ART_N)]}
(OUT/'ownership-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
# Full shared-world diagnostic, applying exactly the ownership polygons shipped above.
shift=(60,530);canvas=Image.new('RGBA',(2100,1900),'#202027')
for e,path in [(N,ART_N),(A,ART_A),(B,ART_B)]:
 im=Image.open(path).convert('RGBA');im.putalpha(ImageChops.multiply(im.getchannel('A'),mask(pxpoly(e))));rr,oo=tr(e);im=im.resize((round(1254*rr),round(1254*rr)),Image.Resampling.LANCZOS);canvas.alpha_composite(im,(round(oo[0]+shift[0]),round(oo[1]+shift[1])))
d=ImageDraw.Draw(canvas);d.text((20,20),'A/B/N ACTUAL OWNERSHIP MATERIAL DIAGNOSTIC - NOT GAME SCREENSHOT',fill='white');canvas.convert('RGB').save(OUT/'ABN-ownership-diagnostic.jpg')
d.line([(x+60,y+530) for x,y in seam],fill='#ff44cc',width=2);canvas.convert('RGB').save(OUT/'ABN-boundary-diagnostic.jpg')
print(json.dumps(losses));print('A/B/N polygon vertices',len(newA),len(newB),len(np))
