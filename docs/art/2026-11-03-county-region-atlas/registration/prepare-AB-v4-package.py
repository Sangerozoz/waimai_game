"""Production AB ownership and measured native B4 entry. Source art stays unchanged."""
import json,math,hashlib,copy
from pathlib import Path
from PIL import Image,ImageDraw
R=Path('docs/art/2026-11-03-county-region-atlas/registration');art=R.parent/'images/REGION-B-v4.png';reg=json.loads((R/'registration-B-v3.json').read_text());A=json.loads((R/'registration-A.json').read_text());old=json.loads((R/'A-B-seam-production.json').read_text());tr=old['BToANativeDiagnosticTransform'];ratio=tr['uniformScale'];off=tr['translation']
reg['id']='REGION-B-v4';reg['sourceArt'].update(file=str(art),sha256=hashlib.sha256(art.read_bytes()).hexdigest());f=reg['fit'];f['method']='Inherited fixed B2 uniform transform, B4 native points reobserved. No refit after native whole-scene edit.'
changes={'J1-1623821610':[231,515],'EDGE-N-149396913':[750,178],'EDGE-W-149396514':[57,622],'SHARED-N-149396913':[488,359],'SHARED-E-149397548':[293,550]}
for e in reg['controlPoints']:
 if e['id'] in changes:e['imagePx']=changes[e['id']]
 if e['id']=='SHARED-N-149396913':e.update(confidence='estimated',manualPixelUncertainty=12,observation='B4 original source line now stays on visible street instead of roof. [488,359] is nearby visually observed centre read; not an independently surveyed vertex.')
 e['errorPixels']=math.dist(e['projectedPx'],e['imagePx']);e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in [0,1]]
f['fitMaxResidualPixels']=max(e['errorPixels'] for e in reg['controlPoints'] if e['usedInFit']);f['allObservedMaxResidualPixels']=max(e['errorPixels'] for e in reg['controlPoints']);reg['status']='usable-interior-corridors-roof-conflict-cleared-local-residual-retained';reg['observedNorthRoadPolylineNative']=[[231,515],[330,459],[420,410],[488,359],[600,280],[700,208],[750,178]]
reg['explicitTargetReadings']=[dict(pixel=[220,509],observation='within broad shared junction asphalt'),dict(pixel=[498,373],observation='at lower asphalt/sidewalk boundary, estimated 15-25px from road centre; no roof'),dict(pixel=[733,208],observation='near upper road side, no roof; border mapping residual retained')]
(R/'registration-B-v4.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
# Actual visual ownership follows shared street/outer transparent ground contour, rather than nominal square.
# A retains top-left side of seam; B retains bottom-right. Source/world coordinates derived from SAME native seam.
seamA=[[1254,625],[1221,655],[1014,851],[722,994],[536.7310279823,1109.793107511],[500,1145],[390,1254]]
aPoly=[[0,0],[1254,0]]+seamA+[[0,1254]]
def a_to_b(p):return [(p[k]-off[k])/ratio for k in [0,1]]
# The complement is formed in A-world canvas then clipped to B native rectangle.
bLarge=[[1254,0],[2200,0],[2200,2100],[-500,2100]]+list(reversed(seamA))+[[1254,0]]
bUnclipped=[a_to_b(p) for p in bLarge]
def clip(poly,axis,value,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ina=a[axis]>=value if greater else a[axis]<=value;inb=b[axis]>=value if greater else b[axis]<=value
  if ina:out.append(a)
  if ina!=inb:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
 return out
bPoly=bUnclipped
for ax,val,gr in [(0,0,True),(0,1254,False),(1,0,True),(1,1254,False)]:bPoly=clip(bPoly,ax,val,gr)
def map_from_A(p):
 u=(p[0]-A['fit']['anchorPixel'][0])/A['fit']['nativePixelsPerUnit'];v=(p[1]-A['fit']['anchorPixel'][1])/A['fit']['nativePixelsPerUnit'];dx=(u/math.sqrt(.5)+v/(math.sin(math.radians(62.5))*math.sqrt(.5)))/2;dy=(v/(math.sin(math.radians(62.5))*math.sqrt(.5))-u/math.sqrt(.5))/2;return [-1580+dx,80+dy]
def toworld(p):return [(p[0]-A['fit']['anchorPixel'][0])/A['fit']['nativePixelsPerUnit'],(p[1]-A['fit']['anchorPixel'][1])/A['fit']['nativePixelsPerUnit']]
def btoa(p):return [p[k]*ratio+off[k] for k in [0,1]]
def bufferline(points,w):
 normals=[]
 for p,q in zip(points,points[1:]):dx,dy=q[0]-p[0],q[1]-p[1];l=math.hypot(dx,dy);normals.append([-dy/l,dx/l])
 left=[];right=[]
 for i,p in enumerate(points):
  if i==0:n=normals[0];m=w
  elif i==len(points)-1:n=normals[-1];m=w
  else:
   n=[normals[i-1][k]+normals[i][k] for k in [0,1]];l=math.hypot(*n);n=[v/l for v in n];m=w/(n[0]*normals[i][0]+n[1]*normals[i][1])
  left.append([p[k]+m*n[k] for k in [0,1]]);right.append([p[k]-m*n[k] for k in [0,1]])
 return left+list(reversed(right))
# Simple road-shaped trust polygons are independent of art clipping.
aRoute=bufferline([[-1582.32,36.57],[-1596.7,96.27],[-1527.0,107.65]],3.5)
bRoute=bufferline([[-1522.94,78],[-1528.97,107.99],[-1433.09,91.52]],3.5)
aEntry=json.loads((R/'region-A-runtime-entry.json').read_text());bEntry=json.loads((R/'region-B-v3-runtime-entry.json').read_text());bEntry.update(file=art.name,sha256=reg['sourceArt']['sha256']);aEntry['ownershipPolygonUV']=[[p[0]/1254,p[1]/1254] for p in aPoly];bEntry['ownershipPolygonUV']=[[p[0]/1254,p[1]/1254] for p in bPoly]
for e,poly,evidence in [(aEntry,aRoute,str(R/'registration-A.json')),(bEntry,bRoute,str(R/'registration-B-v4.json'))]:
 e['registration'].update(status='preview-only',evidence=evidence,routeCoverageMapPolygon=poly)
 e['note']='Measured production entry for PM ready authorization. Ownership is actual shared-street split; route coverage limited to observed interior source-road corridors. Local street-edge/texture mismatch remains, not pixel-perfect seamlessness.'
bEntry['registration'].update(controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence']) for e in reg['controlPoints']],maxResidualPixels=f['allObservedMaxResidualPixels'])
(R/'region-A-AB-v4-runtime-entry.json').write_text(json.dumps(aEntry,ensure_ascii=False,indent=2)+'\n');(R/'region-B-v4-runtime-entry.json').write_text(json.dumps(bEntry,ensure_ascii=False,indent=2)+'\n')
seam=dict(schemaVersion=1,id='REGION-A-v3__REGION-B-v4',ownershipStatus='production-candidate-actual-street-split-awaiting-PM-ready',stitched='corridor-continuity-improved-not-pixel-perfect',nativeSeamOnA=seamA,worldSeamProjectedUnits=[toworld(p) for p in seamA],sourceMapSeam=[map_from_A(p) for p in seamA],ownershipPolygonUV={'REGION-A':aEntry['ownershipPolygonUV'],'REGION-B':bEntry['ownershipPolygonUV']},sourceMapPolygons={'REGION-A':[map_from_A(p) for p in aPoly],'REGION-B':[map_from_A(btoa(p)) for p in bPoly]},routeCoverageMapPolygon={'REGION-A':aRoute,'REGION-B':bRoute},BToANativeDiagnosticTransform=tr,observedMaxResidualPixels={'A':A['fit']['allObservedMaxResidualPixels'],'B':f['allObservedMaxResidualPixels']},limits=['Native street geometry now continuous within accepted local tolerance; no northern roof crossing in B4.','No claim of identical asphalt/sidewalk texture, seamless per-pixel blend, or all-county completion.','Ownership contour must be judged in composed diagnostic. Original building pixels are never altered by this script.','Entry remains preview-only for PM explicit ready switch; no renderer numerical residual threshold.'])
(R/'A-B-v4-production-handoff.json').write_text(json.dumps(seam,ensure_ascii=False,indent=2)+'\n')
# Pixel composite is a labelled DIAGNOSTIC ONLY, never production sprite. Native assets unchanged.
W,H=1850,1800;out=Image.new('RGBA',(W,H),'#20202aff');a=Image.open('docs/art/2026-11-03-whole-region-map/REGION-A-v3.png').convert('RGBA');b=Image.open(art).convert('RGBA');am=Image.new('L',a.size);ImageDraw.Draw(am).polygon([tuple(p) for p in aPoly],fill=255);bm=Image.new('L',b.size);ImageDraw.Draw(bm).polygon([tuple(p) for p in bPoly],fill=255)
from PIL import ImageChops
a.putalpha(ImageChops.multiply(a.getchannel('A'),am));b.putalpha(ImageChops.multiply(b.getchannel('A'),bm));out.alpha_composite(a);b=b.resize((round(1254*ratio),round(1254*ratio)),Image.Resampling.LANCZOS);out.alpha_composite(b,(round(off[0]),round(off[1])));d=ImageDraw.Draw(out);d.text((20,20),'A-v3 / B-v4 SHARED-WORLD OWNERSHIP DIAGNOSTIC - NOT RUNTIME',fill='white');out.convert('RGB').save(R/'diagnostic/A-B-v4-ownership-composite.jpg')
print(json.dumps(dict(fit=f,AownershipVertices=len(aPoly),BownershipVertices=len(bPoly)),indent=2))
