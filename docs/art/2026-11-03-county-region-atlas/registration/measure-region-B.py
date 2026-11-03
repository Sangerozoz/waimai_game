"""B native correspondence and A/B seam-production data; original images unmodified."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path('docs/art/2026-11-03-county-region-atlas/registration');P=Path('docs/art/2026-11-03-county-region-atlas');art=P/'images/REGION-B-v2.png';struct=P/'planning/structures/REGION-B-structure.json';s=json.loads(struct.read_text());A=json.loads((R/'registration-A.json').read_text());q=math.sqrt(.5);st=math.sin(math.radians(62.5));origin=s['originMap'];entries=[]
def axis(p):return [(p[0]-origin[0]-p[1]+origin[1])*q,(p[0]-origin[0]+p[1]-origin[1])*st*q]
def add(id,p,px,conf,err,note,fit=False):entries.append(dict(id=id,sourceMap=p,imagePx=px,confidence=conf,manualPixelUncertainty=err,observation=note,usedInFit=fit))
add('J1-1623821610',[-1528.97,107.99],[246,499],'high',5,'Shared four-way junction with A. Observed native street centre.',True)
add('J2-1623821563',[-1433.09,91.52],[765,846],'high',5,'Right/lower junction with source 149396391.',True)
cp=s['controlPoints'];add('EDGE-S-149396391',cp[0]['map'],[517,1064],'medium',7,'Source south render-edge corridor centre matched to drawn south street endpoint.',True)
add('EDGE-N-149396913',cp[5]['map'],[704,142],'medium',7,'Source north render-edge corridor centre matched to drawn upper street endpoint. Not used in fit; visible drift retained.')
add('EDGE-W-149396514',cp[3]['map'],[69,611],'medium',7,'Shared street at B west render boundary.')
add('EDGE-E-149397381',cp[8]['map'],[865,891],'medium',8,'Right edge of main transverse road.')
add('SHARED-N-149396913',[-1520,63.357642980935594],[478,318],'estimated',12,'Read/interpolated along long unmarked street between source shared junction and north edge; not a unique surveyed vertex.')
add('SHARED-E-149397548',[-1520,106.44915832290363],[295,531],'estimated',10,'Short distance from shared junction toward right main street; manual interpolation, not independent fit control.')
fit=[e for e in entries if e['usedInFit']];ax=[axis(e['sourceMap']) for e in fit];bx=[e['imagePx'] for e in fit];ma=[sum(a[k] for a in ax)/3 for k in [0,1]];mb=[sum(b[k] for b in bx)/3 for k in [0,1]];scale=sum(sum((a[k]-ma[k])*(b[k]-mb[k]) for k in [0,1]) for a,b in zip(ax,bx))/sum(sum((a[k]-ma[k])**2 for k in [0,1]) for a in ax);anchor=[mb[k]-scale*ma[k] for k in [0,1]]
def project(p):return [anchor[k]+scale*axis(p)[k] for k in [0,1]]
for e in entries:e['projectedPx']=project(e['sourceMap']);e['errorPixels']=math.dist(e['projectedPx'],e['imagePx']);e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in [0,1]]
fitinfo=dict(method='fixed 62.5/45 axes, positive scalar+translation; 2 junctions plus south street endpoint; endpoint marked medium confidence',nativePixelsPerUnit=scale,anchorMap=origin,anchorPixel=anchor,anchorUV=[a/1254 for a in anchor],fitMaxResidualPixels=max(e['errorPixels'] for e in fit),allObservedMaxResidualPixels=max(e['errorPixels'] for e in entries),rotationDegrees=0)
record=dict(schemaVersion=1,id='REGION-B-v2',sourceArt=dict(file=str(art),sha256=hashlib.sha256(art.read_bytes()).hexdigest(),nativeSize=[1254,1254]),sourceGeometry=dict(file=str(struct),sha256=hashlib.sha256(struct.read_bytes()).hexdigest()),projection=s['projection'],fit=fitinfo,controlPoints=entries,additionalDrawnStreet=dict(nativeEndpoints=[[545,654],[881,453]],classification='decorative-courtyard-drive-or-pedestrian-route-only',sourceRoadId=None,routeEligible=False),status='measured-seam-edit-required-not-seamless')
(R/'registration-B-v2.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
entry=dict(id='REGION-B',file=art.name,sha256=record['sourceArt']['sha256'],nativeSize=[1254,1254],anchorMap=origin,anchorUV=fitinfo['anchorUV'],nativePixelsPerUnit=scale,sortOrder=1,registration=dict(status='preview-only',evidence=str(R/'registration-B-v2.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence']) for e in entries],maxResidualPixels=fitinfo['allObservedMaxResidualPixels']),ownershipPolygonUV=None,note='Use for measured preview; seam-edit in specified B corridor needed. Decorative unsourced central street is never route-eligible.')
(R/'region-B-runtime-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
# Image B -> image A coordinates in a shared fixed-axis/world scale. Diagnostics only.
pa=A['fit']['nativePixelsPerUnit'];aa=A['fit']['anchorPixel'];delta=[origin[0]-A['fit']['anchorMap'][0],origin[1]-A['fit']['anchorMap'][1]];ratio=pa/scale;offset=[aa[0]+pa*(delta[0]-delta[1])*q-ratio*anchor[0],aa[1]+pa*(delta[0]+delta[1])*st*q-ratio*anchor[1]]
def a_to_b(p):return [(p[k]-offset[k])/ratio for k in [0,1]]
shared=[dict(id='shared-junction-1623821610',sourceMap=[-1528.97,107.99],BCurrent=[246,499],AObserved=[722,994],confidence='high'),dict(id='shared-north-149396913',sourceMap=[-1520,63.357642980935594],BCurrent=[478,318],AObserved=[1014,851],confidence='estimated B read; A medium'),dict(id='shared-main-east-149397548',sourceMap=[-1520,106.44915832290363],BCurrent=[295,531],AObserved=[792,1036],confidence='estimated B read; A medium')]
t=(138.8778114285713-107.99)/(140-107.99);aWest=[722+t*(530-722),994+t*(1114-994)]
shared.append(dict(id='shared-southwest-149396514',sourceMap=[-1536,138.8778114285713],BCurrent=[69,611],AObserved=aWest,confidence='A interpolated between observed shared junction and south endpoint; B medium'))
for e in shared:e['BTargetNativePixel']=a_to_b(e['AObserved']);e['BEditDeltaPixels']=[e['BTargetNativePixel'][k]-e['BCurrent'][k] for k in [0,1]];e['currentWorldMismatchAtANativePixels']=math.dist([ratio*e['BCurrent'][k]+offset[k] for k in [0,1]],e['AObserved'])
seamLine=[[-1528,20],[-1528,45],[-1520,63.357642980935594],[-1528.97,107.99],[-1536,138.8778114285713],[-1536,140]]
aPoly=[[-1640,20]]+seamLine+[[-1640,140]];bPoly=[seamLine[0],[-1416,20],[-1416,140]]+list(reversed(seamLine[1:]))
def world(p):return [(p[0]+1580-p[1]+80)*q,(p[0]+1580+p[1]-80)*st*q]
seam=dict(schemaVersion=1,id='REGION-A__REGION-B',overlapSourceBounds=dict(minX=-1536,maxX=-1520,minY=20,maxY=140),overlapWidthMeters=16,BToANativeDiagnosticTransform=dict(uniformScale=ratio,translation=offset),targets=shared,ownershipCandidate=dict(status='candidate-only-not-runtime-ready',sourceSeamPolyline=seamLine,sourceMapPolygons={'REGION-A':aPoly,'REGION-B':bPoly},worldProjectedUnitPolygons={'REGION-A':[world(p) for p in aPoly],'REGION-B':[world(p) for p in bPoly]},nativeUvPolygons=None,reason='Source partition complementary; generated contour/roof contacts not yet accepted. Apply after B seam edit and actual continuous corridor/roof inspection. Do not claim finished from these polygons.'),stitched=False,sourceRoadsChanged=False)
(R/'A-B-seam-production.json').write_text(json.dumps(seam,ensure_ascii=False,indent=2)+'\n')
# Native B diagnostic copy with projected source roads (not a game asset).
im=Image.new('RGB',(1254,1254),'#22222a');native=Image.open(art).convert('RGBA');im.paste(native,mask=native.getchannel('A'));d=ImageDraw.Draw(im)
for road in s['roads']:
 for seg in road['displaySegments']:d.line([tuple(project(p)) for p in seg],fill='#00ffdd',width=3)
for e in entries:
 x,y=e['imagePx'];xp,yp=e['projectedPx'];d.ellipse((x-6,y-6,x+6,y+6),outline='yellow',width=2);d.line([(x,y),(xp,yp)],fill='#ff5555',width=2)
for e in shared:
 x,y=e['BCurrent'];tx,ty=e['BTargetNativePixel'];d.line([(x,y),(tx,ty)],fill='#ff66ff',width=4);d.ellipse((tx-6,ty-6,tx+6,ty+6),outline='#ff66ff',width=2)
im.save(R/'B-v2-road-and-edit-targets-diagnostic.png')
# Shared-world SVG composed from references; native source pixels remain untouched.
svg='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1900" height="1800" viewBox="0 0 1900 1800"><rect width="1900" height="1800" fill="#22222a"/><image href="../../2026-11-03-whole-region-map/REGION-A-v3.png" width="1254" height="1254"/><image href="../images/REGION-B-v2.png" width="1254" height="1254" transform="translate(%f %f) scale(%f)" opacity="0.75"/>'%(offset[0],offset[1],ratio)
for e in shared:
 x,y=e['AObserved'];u,v=[ratio*e['BCurrent'][k]+offset[k] for k in [0,1]];svg+='<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="red" stroke-width="3"/><circle cx="%f" cy="%f" r="6" fill="none" stroke="yellow"/>'%(x,y,u,v,x,y)
svg+='</svg>';(R/'A-B-shared-world-diagnostic.svg').write_text(svg)
print(json.dumps(dict(fit=fitinfo,targets=shared),indent=2))
