#!/usr/bin/env python3
"""Make ONE source-geometry production input. Does not generate or edit art.

Reads the immutable planning atlas; writes only --output-dir. Separate workers
must use separate output dirs. Relative paths resolve from the repository root.
"""
from pathlib import Path
import argparse, json, math, hashlib, sys
from PIL import Image, ImageDraw

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
 local_uses=sorted(set(p['landUse'] for p in parcels))
 campus_ids=[p['id'] for p in parcels if p['landUse'] in ['campus','school']]
 community_ids=[p['id'] for p in parcels if p['landUse']=='community']
 facility_policy=('Local school/campus facilities are allowed ONLY inside these original campus/school parcels: '+', '.join(campus_ids)+'. Keep their actual land-use and bounds; do not add a second school or replicate the reference school/basketball complex.' if campus_ids else 'No local school/campus parcel is present: DO NOT invent any standalone school, campus, basketball court or sports stadium.')
 facility_policy+=(' Community-service structures are allowed only inside these original community parcels: '+', '.join(community_ids)+'.' if community_ids else ' No explicit community parcel is present: do not invent a civic center, municipal landmark or community landmark complex.')
 facility_policy+=(' Ordinary residential land can use distinct residential courtyard massings, grouped housing and small convenience storefronts consistent with its land use, without inserting a school/civic landmark. Public facilities are not a mandatory ingredient for every120m region.' if r['zone']!='outerLandscape' else ' This outer landscape has no new residential or civic facility requirement; natural forest/terrain/water forms the complete scene.')
 prompt=f'''Use case: stylized-concept. Asset: complete continuous county game map REGION {ident}, not a collection of separate building sprites. Generate one whole 120m by 120m multi-block region with streets, sidewalks, architecture, entrances, courtyard planting and fixed painted shadows in one image.\nReference image 1 is this region's neutral source-geometry guide: it is the sole authority for original road positions, relative widths, intersections, water and edge connections. Reference image 2 is user-approved REGION-A-v3: MATERIAL AND PAINTING STYLE reference only, for bright modern Japanese urban anime painterly rendering, material richness, approved ground-greenery balance and soft fixed daylight. It is NOT the authority for this region camera, road lines, framing, facility list or layout. STRICT PRIORITY: source geometry guide framing/62.5deg camera/source-road junctions FIRST; actual adjacent ground overlap where consistent with source SECOND; A painting/material style LAST. Do not copy the repeated landmark package of glass tower + L-shaped school/basketball court + arched-roof hall + gray pitched-roof rowhouses into every region. Guide boxes indicate location and source camera, not identical architecture.\nSource region world bounds {json.dumps(bb)}. Guide is 1536 square, origin-map {origin}, guide pixels/unit {P}, origin pixel {offset}. Preserve its exact diamond framing, 62.5deg orthographic camera axes and every original road centerline/width/intersection, including upper road branches and edge entry points. Do not replace an upper road with a low-angle straight line, tilt the upper part of the map, move roads through buildings, copy A street layout or invent a prettier grid. Original source-road controls override style-reference composition. Buildings and their setbacks must be arranged around the original road corridor, never vice versa. Region core {json.dumps(r['coreBounds'])}; 8m each-side halo and 16m neighbor overlap are real shared world content. Coordinate with actual adjacent-region edges only for ids listed in neighborSharedRoadControls and preserve shared source roads; A is not a neighbor for distant regions. No isolated vignette border or decorative base.\nRegion zone: {r['zone']}; local parcel land-use is the only facility authority. Local planned uses: {', '.join(sorted(set(p['landUse'] for p in parcels)))}. {theme_instructions} {facility_policy} ABSOLUTELY NO greenery on any roof: no rooftop trees, shrubs, turf, planters, garden, vine or vegetation. Keep rider streets visibly open; typically building setbacks 6–10m. Slightly larger buildings allowed, no arbitrary new hard height limit.\nDo not draw rider, vehicles, characters, HUD, text, labels, tile outlines or registration marks. Keep transparent outside the actual region ground/art silhouette and preserve complete buildings that project beyond its ground edge. No black background, watermarks, 3D low-poly substitute, repeated-window program boxes, mirrored art, flat-color final diagram or screenshot UI. Do not sacrifice approved building detail to shrink an entire county into this region.\nThis prompt is a production request, not evidence that geometry/seams already match. Save full native RGBA source; never script-edit generated pixels. Final control-point registration and seam review follow generation.'''
 save(R/'prompts'/f'{ident}-v1.json',dict(id=ident+'-v1',status='prompt-ready-not-generated',localParcelLandUses=local_uses,facilityPolicy=facility_policy,prompt=prompt,referenceImages=[dict(file=str(out),role='source-geometry-only',sha256=sha(out)),dict(file='docs/art/2026-11-03-whole-region-map/REGION-A-v3.png',role='approved-material-and-painting-style-only',sha256='4e266eb23f4d165828fabc6c51ab0334a5d38db02a411ac84008f52ea949911e')],structureFile=str(R/'structures'/f'{ident}-structure.json'),sharedControls=shared))
 print(ident,len(roads),len(buildings),len(controls),str(out),flush=True)


def main():
 global R,S,Z,L,city,zoning,layout,nodes,zones,plan,bygrid,q,s,c,P,offset,theme_instructions
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--id',required=True,help='Exact atlas region id, e.g. REGION-B or R-+02-+00')
 parser.add_argument('--output-dir',required=True,help='Dedicated empty worker output directory, normally docs/art/2026-11-03-county-region-atlas/production/<id>')
 parser.add_argument('--neighbor-art',action='append',default=[],metavar='REGION_ID=PATH',help='Actual adjacent native image, repeatable. SHA stored; no pixel manipulation.')
 parser.add_argument('--match-approved-scale',action='store_true',help='Match A registration scale/anchor framing in guide, instead of historical1536 guide framing. Does not fix painted edge drift.')
 args=parser.parse_args()
 repo=Path(__file__).resolve().parents[4]
 planning=Path(__file__).resolve().parent
 R=Path(args.output_dir)
 if not R.is_absolute():R=repo/R
 if R.resolve()==planning.resolve() or planning.resolve() in R.resolve().parents:
  parser.error('Worker output must be isolated from planning/.')
 if R.exists() and any(R.iterdir()):parser.error('Output directory is not empty; use a new versioned directory. Existing inputs never overwritten.')
 plan=json.loads((planning/'atlas-plan.json').read_text());matches=[r for r in plan['regions'] if r['id']==args.id]
 if not matches:parser.error('Region id is absent from atlas-plan.json')
 r=matches[0];bygrid={tuple(x['grid']):x for x in plan['regions']}
 S=repo/'delivery-game/assets/resources/map-sample/city.json';Z=repo/'docs/art/2026-11-02-county-zoning/selection.json';L=repo/'docs/art/2026-11-03-county-expansion/county-scene-layout.json'
 for p in [S,Z,L]:
  expected=next(x['sha256'] for x in plan['source'] if (repo/x['file']).resolve()==p.resolve())
  if sha(p)!=expected:parser.error('Source SHA changed; update source planning explicitly before producing inputs: '+str(p))
 city=json.loads(S.read_text());zoning=json.loads(Z.read_text());layout=json.loads(L.read_text());nodes={n['id']:[n['x'],n['y']] for n in city['nodes']};zones=plan['zones']
 q=math.sqrt(.5);s=math.sin(math.radians(62.5));c=math.cos(math.radians(62.5));P=7.8;offset=[768,810]
 registration=repo/'docs/art/2026-11-03-county-region-atlas/registration/registration-A.json'
 reg=json.loads(registration.read_text()) if registration.exists() else None
 if args.match_approved_scale:
  if not reg:parser.error('A registration evidence missing.')
  factor=1536/reg['sourceArt']['nativeSize'][0];P=reg['fit']['nativePixelsPerUnit']*factor;offset=[v*factor for v in reg['fit']['anchorPixel']]
 if r['zone']=='outerLandscape':
  theme_instructions='Outside the blue delivery boundary create only continuous low wooded hills, forest, valley, grassland and source-water landscape. No NEW urban residential blocks, shops, offices, pickup/dropoff labels or city street extensions. In a shared halo entering blue, preserve only the actual adjacent interior edge if present; do not invent a new city outside blue. Any source-road trace is an inert landscape reference; it never expands delivery territory. Extend neighbor forest/terrain/water silhouettes naturally with fixed daylight. Urban ground-greenery ratio does not apply to forest background.'
 elif r['zone']=='suburb':
  theme_instructions='Complete all plots with varied low/mid-rise suburban residential courtyards and grouped housing following each local parcel land use; no mandatory schools, sports grounds, civic landmark or reference-building package. More open courtyard spacing than urban core, but no unassigned blank lot, blanket paving or one grass fill. Ground greenery follows approved visual balance, no oversized park invented on residential plots.'
 else:
  theme_instructions='Complete urban plots with varied mid-rise/low-rise residences, distinct courtyard massings and local-use-compatible offices/shops; never require a school, civic landmark or sports facility unless that exact parcel explicitly supports it. Diversity must change massing, height, roof profile and use, not simply recolor the same slab. Ground greenery follows approved A-v3 and latest style reference about0.9 visually; no giant parks, blanket lawns or empty plazas.'
 if r['mixedBlueBoundary']:
  theme_instructions+=' This region straddles the BLUE boundary '+json.dumps(zones['city'])+'. Built urban land and delivery roads stay strictly inside it; outside becomes natural landscape. No city block crosses the boundary.'
 if r['mixedGreenBoundary']:
  theme_instructions+=' The GREEN dense-core boundary is '+json.dumps(zones['urban'])+'. Keep a continuous natural density transition to suburb across it; no visible colored zoning line.'
 R.mkdir(parents=True,exist_ok=True)
 make_region(*r['grid'])
 structure=R/'structures'/f"{r['id']}-structure.json";d=json.loads(structure.read_text());d['displayBounds']=zones['map'];d['deliveryBounds']=zones['city'];d['registrationScaleReference']=dict(file=str(registration),sha256=sha(registration) if registration.exists() else None,note='A has 15–42px edge drift. Guide controls are not observed image correspondences; actual shared road/ground overlap required.');save(structure,d)
 prompt_file=R/'prompts'/f"{r['id']}-v1.json";prompt=json.loads(prompt_file.read_text())
 # Rebase references to absolute paths so a worker can run from any cwd.
 for ref in prompt['referenceImages']:
  pp=Path(ref['file']);ref['file']=str(pp if pp.is_absolute() else repo/pp)
 prompt['prompt']+='\nA registration warning: fitted native scale7.1345800795px/m@1254 and anchor[613.8999,640.6815]; its painted edge can deviate15–42px from nominal source square. Copy a complete visible shared road/ground strip from the actual neighbor reference, then measure new art; no promise of automatic seamlessness. Never move source roads. Every roof completely free of trees, shrubs, planters, turf or any vegetation.'
 for spec in args.neighbor_art:
  if '=' not in spec:parser.error('--neighbor-art requires REGION_ID=PATH')
  neighbor_id,neighbor_path=spec.split('=',1)
  if neighbor_id not in r['neighbors'].values():parser.error('Neighbor is not adjacent in source atlas: '+neighbor_id)
  neighbor=Path(neighbor_path)
  if not neighbor.is_absolute():neighbor=repo/neighbor
  if not neighbor.is_file():parser.error('Neighbor native image missing: '+str(neighbor))
  prompt['referenceImages'].append(dict(file=str(neighbor),role='actual-adjacent-region-edge-reference',regionId=neighbor_id,sha256=sha(neighbor)))
  prompt['prompt']+='\nAdditional reference image '+str(len(prompt['referenceImages']))+' is actual adjacent '+neighbor_id+'. Preserve its complete shared road/ground overlap in the source seam specified in structure.neighborSharedRoadControls; match building/terrain silhouettes and fixed shadows at that edge while preserving the source guide camera/framing/road controls as highest priority. Neighbor painted drift is not permission to move the original road. Do not copy its independent interior layout or landmark combinations.'
 prompt['adjacentRegionIds']=list(r['neighbors'].values())
 prompt['neighborReferenceStatus']='actual-neighbor-supplied' if args.neighbor_art else 'needs-real-neighbor-art-before-seam-production'
 prompt['registrationScaleReference']=d['registrationScaleReference'];save(prompt_file,prompt)
 save(R/'source-manifest.json',dict(id=r['id'],status='source-input-produced-not-native-art',atlas=dict(file=str(planning/'atlas-plan.json'),sha256=sha(planning/'atlas-plan.json')),source=plan['source'],matchedApprovedScale=args.match_approved_scale,outputs=[dict(file=str(p.relative_to(R)),sha256=sha(p)) for p in sorted(R.rglob('*')) if p.is_file()],noGeneratedArtPixelsEdited=True))
 print(json.dumps(dict(id=r['id'],outputDir=str(R),structure=str(structure),prompt=str(prompt_file),status='source-input-only'),ensure_ascii=False))

if __name__=='__main__':main()
