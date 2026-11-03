"""Production geometry only. Never reads/modifies generated art pixels."""
from pathlib import Path
import json, math, hashlib, collections
from PIL import Image,ImageDraw
R=Path('docs/art/2026-11-03-county-region-atlas/planning'); R.mkdir(parents=True,exist_ok=True)
S=Path('delivery-game/assets/resources/map-sample/city.json'); Z=Path('docs/art/2026-11-02-county-zoning/selection.json'); L=Path('docs/art/2026-11-03-county-expansion/county-scene-layout.json')
city=json.loads(S.read_text());zoning=json.loads(Z.read_text());layout=json.loads(L.read_text());nodes={n['id']:[n['x'],n['y']] for n in city['nodes']};zones={k:v['worldBoundsMetresApprox'] for k,v in zoning['regions'].items()}
def save(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def intersects(a,b):return a['minX']<b['maxX'] and a['maxX']>b['minX'] and a['minY']<b['maxY'] and a['maxY']>b['minY']
def intersection(a,b):return dict(minX=max(a['minX'],b['minX']),maxX=min(a['maxX'],b['maxX']),minY=max(a['minY'],b['minY']),maxY=min(a['maxY'],b['maxY']))
def box(pts):return dict(minX=min(p[0] for p in pts),maxX=max(p[0] for p in pts),minY=min(p[1] for p in pts),maxY=max(p[1] for p in pts))
def inside(p,b):return b['minX']<=p[0]<=b['maxX'] and b['minY']<=p[1]<=b['maxY']
def clip(a,b,bb):
 dx,dy=b[0]-a[0],b[1]-a[1];lo,hi=0.,1.
 for p,q in [(-dx,a[0]-bb['minX']),(dx,bb['maxX']-a[0]),(-dy,a[1]-bb['minY']),(dy,bb['maxY']-a[1])]:
  if abs(p)<1e-12:
   if q<0:return None
  elif p<0:lo=max(lo,q/p)
  else:hi=min(hi,q/p)
 return None if lo>hi else [[a[0]+lo*dx,a[1]+lo*dy],[a[0]+hi*dx,a[1]+hi*dy]]
def rid(i,j):return {(0,0):'REGION-A',(1,0):'REGION-B',(0,1):'REGION-C',(1,1):'REGION-D'}.get((i,j),f'R-{i:+03d}-{j:+03d}')
base=[-1632,28];step=104;halo=8;red=zones['map'];imin=math.floor((red['minX']-base[0])/step);imax=math.ceil((red['maxX']-base[0])/step)-1;jmin=math.floor((red['minY']-base[1])/step);jmax=math.ceil((red['maxY']-base[1])/step)-1
# Absorb sub-halo boundary slivers into the last neighboring ownership core.
if 0 < red['maxX']-(base[0]+step*imax) <= halo: imax-=1
if 0 < red['maxY']-(base[1]+step*jmax) <= halo: jmax-=1
regions=[];bygrid={}
for j in range(jmin,jmax+1):
 for i in range(imin,imax+1):
  core=dict(minX=base[0]+step*i,maxX=base[0]+step*(i+1),minY=base[1]+step*j,maxY=base[1]+step*(j+1));ext=dict(minX=core['minX']-halo,maxX=core['maxX']+halo,minY=core['minY']-halo,maxY=core['maxY']+halo)
  zone='denseUrban' if intersects(core,zones['urban']) else 'suburb' if intersects(core,zones['city']) else 'outerLandscape';theme={'denseUrban':'繁华城区：多样住宅、沿街商业、办公、学校/公共庭院及口袋绿化；不整片刷公园','suburb':'完整郊区：低中层住宅、学校、社区服务、运动场和设计过的绿地；密度低于核心','outerLandscape':'经营蓝框之外：低山、树林、河谷、草甸连续背景；禁止经营街区和配送点'}[zone]
  display=intersection(core,red)
  if i==imax:display['maxX']=red['maxX']
  if j==jmax:display['maxY']=red['maxY']
  x=dict(id=rid(i,j),grid=[i,j],coreBounds=core,renderBounds=ext,displayClip=display,zone=zone,theme=theme,mixedBlueBoundary=intersects(core,zones['city']) and intersection(core,zones['city'])!=core,mixedGreenBoundary=intersects(core,zones['urban']) and intersection(core,zones['urban'])!=core,artStatus='approved-style-reference-unregistered' if (i,j)==(0,0) else 'not-generated',priority=abs(i)+abs(j));regions.append(x);bygrid[(i,j)]=x
seams=[]
for r in regions:
 i,j=r['grid'];r['neighbors']={}
 for direction,di,dj in [('east',1,0),('west',-1,0),('north',0,1),('south',0,-1)]:
  n=bygrid.get((i+di,j+dj))
  if n:r['neighbors'][direction]=n['id']
 for direction,di,dj in [('east',1,0),('north',0,1)]:
  n=bygrid.get((i+di,j+dj))
  if n:seams.append(dict(id=r['id']+'__'+n['id'],regions=[r['id'],n['id']],overlapBounds=intersection(r['renderBounds'],n['renderBounds']),overlapWidthMeters=16,ownership='core half-open at source-world boundary; overlap is painting constraint, not double-owned road',sharedRoadControlsStatus='on-demand source extraction; not generated-art correspondence',stitchStatus='not-made'))
counts=collections.Counter(r['zone'] for r in regions)
summary=dict(redGridCount=len(regions),gridColumns=imax-imin+1,gridRows=jmax-jmin+1,blueIntersectingCoreCount=sum(intersects(r['coreBounds'],zones['city']) for r in regions),greenIntersectingCoreCount=sum(intersects(r['coreBounds'],zones['urban']) for r in regions),zoneCounts=dict(counts),seamCount=len(seams))
plan=dict(version=1,status='source-grid-produced;not-art-complete;A-unregistered',source=[dict(file=str(p),sha256=sha(p)) for p in [S,Z,L]],zones=zones,coordinateUnit='source-ground-metres',camera=dict(elevationDeg=62.5,azimuthDeg=45,fixed=True),production=dict(coreSizeMeters=[104,104],renderSizeMeters=[120,120],haloEachSideMeters=8,neighborOverlapMeters=16,outerSliverPolicy='Absorb red boundary remainder <=8m into existing neighboring image halo; never allocate a standalone 0.05m tile.',gridOriginCoreMin=base,anchorAOriginMap=[-1580,80],guideSizePixels=[1536,1536],nativeCandidateSizePixels=[1254,1254],nativeApproxPixelsPerMapUnit=7.8*1254/1536,warning='This is a source-space partition only; A-v3 still needs measured image correspondence. No source road is changed to fit generated art.'),summary=summary,regions=regions,seams=seams,completion=dict(nativeArtRegions=1,sourceRegisteredRegions=0,stitchedSeams=0,engineAtlasDeployed=False,stageTests='not-triggered-not-run'))
save(R/'atlas-plan.json',plan)
q=math.sqrt(.5);s=math.sin(math.radians(62.5));c=math.cos(math.radians(62.5));P=7.8;offset=[768,810]
def make_region(i,j):
 r=bygrid[(i,j)];ident=r['id'];bb=r['renderBounds'];origin=[(bb['minX']+bb['maxX'])/2,(bb['minY']+bb['maxY'])/2]
 def project(p):
  x,y=p[0]-origin[0],p[1]-origin[1];zz=p[2] if len(p)>2 else 0
  return [offset[0]+P*(x-y)*q,offset[1]+P*((x+y)*s*q-zz*c)]
 roads=[];controls=[]
 for road in city['roads']:
  points=[nodes[n] for n in road['nodes']];parts=[seg for a,b in zip(points,points[1:]) if (seg:=clip(a,b,bb))]
  if not parts:continue
  item=dict(id=road['id'],sourceNodeIds=road['nodes'],nodes=points,width=road.get('width',5),direction=road.get('direction',0),kind=road.get('kind'),displaySegments=parts);roads.append(item)
  for seg in parts:
   for p in seg:
    if min(abs(p[0]-bb['minX']),abs(p[0]-bb['maxX']),abs(p[1]-bb['minY']),abs(p[1]-bb['maxY']))<1e-5:controls.append(dict(kind='source-road-render-edge',roadId=road['id'],map=p,guidePixel=project(p)))
  for nid,p in zip(road['nodes'],points):
   if inside(p,bb):controls.append(dict(kind='source-road-node',sourceNodeId=nid,roadId=road['id'],map=p,guidePixel=project(p)))
 buildings=[]
 for n,foot in enumerate(city['buildings']):
  if intersects(box(foot),bb) and all(inside(p,zones['city']) for p in foot):buildings.append(dict(sourceReferenceIndex=n,footprint=foot,heightNominal=[12,15,18,15,12][n%5],wholeBuilding=True,extendsRenderBoundary=not all(inside(p,bb) for p in foot)))
 added=[b for b in layout['addedBuildings'] if intersects(box(b['footprint']),bb)]
 parcels=[dict(id=p['id'],landUse=p['landUse'],name=p.get('name'),center=p['center']) for p in layout['parcels'] if intersects(box([pt for ring in p['rings'] for pt in ring]),bb)]
 water=[a['points'] for a in city['areas'] if a.get('kind')=='water' and intersects(box(a['points']),bb)]
 waterways=[]
 for line in city['waterways']:
  parts=[seg for a,b in zip(line,line[1:]) if (seg:=clip(a,b,bb))]
  if parts:waterways.extend(parts)
 shared=[]
 for other in plan['seams']:
  if ident not in other['regions']:continue
  ob=other['overlapBounds'];segments=[]
  for road in roads:
   for a,b in road['displaySegments']:
    seg=clip(a,b,ob)
    if seg:segments.append(dict(roadId=road['id'],width=road['width'],map=seg,guidePixels=[project(p) for p in seg]))
  shared.append(dict(seamId=other['id'],regions=other['regions'],overlapBounds=ob,sourceRoadSegments=segments,paintingStatus='not-generated-not-stitched'))
 im=Image.new('RGBA',(1536,1536),(0,0,0,0));dr=ImageDraw.Draw(im);ground=[[bb['minX'],bb['minY']],[bb['maxX'],bb['minY']],[bb['maxX'],bb['maxY']],[bb['minX'],bb['maxY']]];dr.polygon([tuple(project(p)) for p in ground],fill='#dfdad1')
 def corridor(part,width,color):
  a,b=part;dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
  if length<1e-8:return
  nx,ny=-dy/length*width/2,dx/length*width/2;pts=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]];dr.polygon([tuple(project(p)) for p in pts],fill=color)
 for w in water:dr.polygon([tuple(project(p)) for p in w],fill='#9fb6bd')
 for w in waterways:corridor(w,4,'#9fb6bd')
 for road in roads:
  for seg in road['displaySegments']:corridor(seg,road['width']+3.6,'#c4bfae')
 for road in roads:
  for seg in road['displaySegments']:corridor(seg,road['width'],'#828887')
 guide_buildings=buildings+[dict(footprint=b['footprint'],heightNominal=b['heightMetres'],plannedId=b['id']) for b in added]
 for b in sorted(guide_buildings,key=lambda b:sum(project(p)[1] for p in b['footprint'])/len(b['footprint'])):
  foot=b['footprint'];h=b['heightNominal'];top=[p+[h] for p in foot];faces=[]
  for k in range(len(foot)):
   l=(k+1)%len(foot);faces.append(([foot[k],foot[l],top[l],top[k]],sum(project(p)[1] for p in [foot[k],foot[l]])))
  for face,_ in sorted(faces,key=lambda f:f[1]):dr.polygon([tuple(project(p)) for p in face],fill='#d0cbbf',outline='#9f9d94')
  dr.polygon([tuple(project(p)) for p in top],fill='#f4f0e7',outline='#989c96',width=2)
 out=R/'guides'/f'{ident}-structure-neutral.png';out.parent.mkdir(exist_ok=True);im.save(out)
 structure=dict(id=ident,atlasGrid=[i,j],bounds=bb,coreBounds=r['coreBounds'],originMap=origin,projection=dict(elevationDeg=62.5,azimuthDeg=45,canvasYDown=True,axisX=[q,s*q],axisY=[-q,s*q],axisZ=[0,-c],nativePixelsPerUnit=P,originPixel=offset),source=dict(file=str(S),sha256=sha(S)),roads=roads,buildingReferences=buildings,plannedAddedBuildings=added,landUseParcels=parcels,waterPolygons=water,waterwaySegments=waterways,controlPoints=controls,neighborSharedRoadControls=shared,guide=dict(file=str(out),sha256=sha(out),nativeSize=[1536,1536]),notes=['Structural code-native drawing only; not generated final art.','Full source footprints retained; viewport clipping is not an architectural design change.','New-region artwork not yet generated; no pixel alignment to A is claimed.','Neutral areas require complete planned urban content, not blanket paving or park.'])
 save(R/'structures'/f'{ident}-structure.json',structure)
 prompt=f'''Use case: stylized-concept. Asset: complete continuous county game map REGION {ident}, not a collection of separate building sprites. Generate one whole 120m by 120m multi-block region with streets, sidewalks, architecture, entrances, courtyard planting and fixed painted shadows in one image.\nReference image 1 is this region's neutral source-geometry guide: it is the sole authority for original road positions, relative widths, intersections, water and edge connections. Reference image 2 is user-approved REGION-A-v3: use ONLY its bright modern Japanese urban anime painterly rendering, material richness, greenery balance, 62.5-degree elevated orthographic camera, 45-degree azimuth, building scale, soft fixed daylight and detailed streetscape. Do not copy its buildings or road arrangement into this different region. Guide boxes indicate location and camera, not identical architecture.\nSource region world bounds {json.dumps(bb)}. Guide is 1536 square, origin-map {origin}, ground pixels/unit 7.8, origin pixel [768,810]. Preserve its exact diamond framing, camera axes and original roads, including roads that enter/exit the edge. Do not add a new grid or straighten source curves to make prettier blocks. Region core {json.dumps(r['coreBounds'])}; 8m each-side halo and 16m neighbor overlap are real shared world content. Coordinate with the supplied A edge and shared source roads; no isolated vignette border or decorative base.\nTheme: {r['theme']}. Local planned uses: {', '.join(sorted(set(p['landUse'] for p in parcels)))}. Complete all urban plots with varied mid-rise/low-rise residential, L/U courtyards, offices, shops, school/public facilities as supported by this local plan. Architectural diversity must involve massing, height, roof profiles and uses, not just different color on repeated apartment slabs. Ground greenery is measured visually against approved A-v3 and latest reference about 0.9; no giant parks, blanket green lawns, empty plazas, or rooftop trees. Keep rider streets visibly open; typically building setbacks 6–10m. Slightly larger buildings allowed, no arbitrary new hard height limit.\nDo not draw rider, vehicles, characters, HUD, text, labels, tile outlines or registration marks. Keep transparent outside the actual region ground/art silhouette and preserve complete buildings that project beyond its ground edge. No black background, watermarks, 3D low-poly substitute, repeated-window program boxes, mirrored art, flat-color final diagram or screenshot UI. Do not sacrifice approved building detail to shrink an entire county into this region.\nThis prompt is a production request, not evidence that geometry/seams already match. Save full native RGBA source; never script-edit generated pixels. Final control-point registration and seam review follow generation.'''
 save(R/'prompts'/f'{ident}-v1.json',dict(id=ident+'-v1',status='prompt-ready-not-generated',prompt=prompt,referenceImages=[dict(file=str(out),role='source-geometry-only',sha256=sha(out)),dict(file='docs/art/2026-11-03-whole-region-map/REGION-A-v3.png',role='approved-style-and-neighbor-reference',sha256='4e266eb23f4d165828fabc6c51ab0334a5d38db02a411ac84008f52ea949911e')],structureFile=str(R/'structures'/f'{ident}-structure.json'),sharedControls=shared))
 print(ident,len(roads),len(buildings),len(controls),str(out),flush=True)
for ij in [(1,0),(0,1),(1,1)]:make_region(*ij)
save(R/'source-manifest.json',dict(date='2026-11-03',productionType='code-native-source-geometry-input',generatedArtReadOrChanged=False,sources=plan['source'],outputs=[dict(file=str(p),sha256=sha(p)) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='source-manifest.json']))
print(json.dumps(summary))
