"""Source seam contracts and code-native planning overview; no final art editing."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,json,hashlib
R=Path('docs/art/2026-11-03-county-region-atlas/planning');P=json.loads((R/'atlas-plan.json').read_text());C=json.loads(Path('delivery-game/assets/resources/map-sample/city.json').read_text());L=json.loads(Path('docs/art/2026-11-03-county-expansion/county-scene-layout.json').read_text());nodes={n['id']:[n['x'],n['y']] for n in C['nodes']}
def save(name,obj):(R/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def inside(p,b):return b['minX']<=p[0]<=b['maxX'] and b['minY']<=p[1]<=b['maxY']
def crossing(a,b,axis,val):
 d=b[axis]-a[axis]
 if abs(d)<1e-10:return None
 t=(val-a[axis])/d
 return [a[k]+t*(b[k]-a[k]) for k in range(2)] if 0<=t<=1 else None
contracts=[]
for aa,bb in [('REGION-A','REGION-B'),('REGION-A','REGION-C'),('REGION-B','REGION-D'),('REGION-C','REGION-D')]:
 ra=next(r for r in P['regions'] if r['id']==aa);rb=next(r for r in P['regions'] if r['id']==bb);o=dict(minX=max(ra['renderBounds']['minX'],rb['renderBounds']['minX']),maxX=min(ra['renderBounds']['maxX'],rb['renderBounds']['maxX']),minY=max(ra['renderBounds']['minY'],rb['renderBounds']['minY']),maxY=min(ra['renderBounds']['maxY'],rb['renderBounds']['maxY']));axis=0 if o['maxX']-o['minX']==16 else 1;lo=o['minX'] if axis==0 else o['minY'];hi=o['maxX'] if axis==0 else o['maxY'];nom=(lo+hi)/2
 candidates=[]
 for coord in [lo+2+k for k in range(13)]:
  conflicts=[]
  for i,poly in enumerate(C['buildings']):
   if min(p[axis] for p in poly)<coord<max(p[axis] for p in poly) and any(inside(p,o) for p in poly):conflicts.append({'sourceBuildingIndex':i})
  for b in L['addedBuildings']:
   poly=b['footprint']
   if min(p[axis] for p in poly)<coord<max(p[axis] for p in poly) and any(inside(p,o) for p in poly):conflicts.append({'plannedBuildingId':b['id']})
  candidates.append(dict(sourceCoordinate=coord,groundFootprintConflicts=conflicts,cost=len(conflicts)*100+abs(coord-nom)))
 best=min(candidates,key=lambda c:c['cost']);roads=[]
 for road in C['roads']:
  pts=[nodes[n] for n in road['nodes']]
  for a,b in zip(pts,pts[1:]):
   point=crossing(a,b,axis,best['sourceCoordinate'])
   if point and inside(point,o):roads.append(dict(roadId=road['id'],width=road.get('width',5),map=point,sourceSegment=[a,b]))
 parcels=[dict(id=p['id'],landUse=p['landUse'],name=p.get('name'),rings=p['rings']) for p in L['parcels'] if any(inside(pt,o) for ring in p['rings'] for pt in ring)]
 contracts.append(dict(id=aa+'__'+bb,regions=[aa,bb],overlapBounds=o,sourceAxis=axis,nominalCoreSplitCoordinate=nom,lowGroundConflictCandidate=best,alternatives=candidates,sourceRoadPassages=roads,localParcelBoundaries=parcels,status='source-natural-seam-input-only-not-runtime-ownership',instructions=['Choose actual painted low-ground sidewalk/courtyard/road boundary in this shared overlap, never cut a facade, roof, tree crown or its fixed shadow.','Candidate minimizes SOURCE footprint cuts only; it cannot prove generated A or B image has the same geometry.','Preserve each road passage position/width and continuous markings in both images; assign one owner per shared ground point.','The four-region shared corner requires one consistent ownership solution; do not solve four edges independently and leave a hole/double-drawn junction.','After native generation, annotate observed seam correspondences and supply complementary ownershipPolygonUV to renderer. Do not edit source road nodes or warp art.']))
save('first-four-seam-contracts.json',dict(schemaVersion=1,status='source-contracts-produced-not-art-stitched',seams=contracts))
# A source-space diagram: deliberately flat, labeled as planning, never a final map preview.
im=Image.new('RGB',(1600,1690),'#faf8f3');dr=ImageDraw.Draw(im);bound=P['zones']['map'];scale=1440/(bound['maxX']-bound['minX'])
def proj(p):return (80+(p[0]-bound['minX'])*scale,1600-(p[1]-bound['minY'])*scale)
colors={'outerLandscape':'#e7eddf','suburb':'#e8e4dc','denseUrban':'#dcdfe3'}
for r in P['regions']:
 b=r['displayClip'];dr.rectangle([proj([b['minX'],b['maxY']]),proj([b['maxX'],b['minY']])],fill=colors[r['zone']],outline='#cdd0cc',width=1)
for line in C['waterways']:
 pts=[proj(p) for p in line]
 if any(0<p[0]<1600 and 80<p[1]<1640 for p in pts):dr.line(pts,fill='#9ebac5',width=2)
for road in C['roads']:
 ps=[nodes[n] for n in road['nodes']]
 for a,b in zip(ps,ps[1:]):
  if inside(a,bound) and inside(b,bound):dr.line([proj(a),proj(b)],fill='#b6b8b7',width=1)
for key,col in [('map','#bc675e'),('city','#5681a3'),('urban','#678e5b')]:
 b=P['zones'][key];dr.rectangle([proj([b['minX'],b['maxY']]),proj([b['maxX'],b['minY']])],outline=col,width=4)
for ident in ['REGION-A','REGION-B','REGION-C','REGION-D']:
 r=next(r for r in P['regions'] if r['id']==ident);b=r['coreBounds'];dr.rectangle([proj([b['minX'],b['maxY']]),proj([b['maxX'],b['minY']])],outline='#bd783c',width=3);dr.text(proj([b['minX']+6,b['maxY']-14]),ident.replace('REGION-',''),fill='#623d21')
dr.text((80,26),'COUNTY SOURCE-SPACE REGION PRODUCTION PLAN - NOT FINAL ART',fill='#313a40');dr.text((80,49),f"{P['summary']['redGridCount']} regions / {P['summary']['blueIntersectingCoreCount']} blue / {P['summary']['greenIntersectingCoreCount']} green; 120m render, 104m core, 16m overlap",fill='#313a40');dr.text((80,1634),'Red = full display | Blue = complete delivery boundary | Green = urban core | Orange = first A/B/C/D',fill='#313a40');dr.text((80,1655),'A-v3 native art exists; all other region art and seams remain unproduced. Source roads unchanged.',fill='#313a40');im.save(R/'county-region-production-plan.png')
save('runtime-interface-mapping.json',dict(schemaVersion=1,developerContract='docs/reviews/county-region-20261103/atlas-interface.json',originMap=[-1580,80],displayBounds=P['zones']['map'],deliveryPolygon=[[P['zones']['city']['minX'],P['zones']['city']['minY']],[P['zones']['city']['maxX'],P['zones']['city']['minY']],[P['zones']['city']['maxX'],P['zones']['city']['maxY']],[P['zones']['city']['minX'],P['zones']['city']['maxY']]],mapping={'id':'Same REGION-A/B/C/D and grid IDs across planning and runtime.','anchorMap':'Source region center from structure.originMap.','anchorUV':'Must be observed/fitted in generated native image; guide originPixel is not native art registration.','nativePixelsPerUnit':'Guide 7.8 at1536; 1254 gives nominal6.368 only if composition preserved, not observed. Registration worker owns actual fitted value.','ownershipPolygonUV':'Map nominal core or adjusted natural seam through actual fitted transform; complementary across neighbors. Do not derive from guide alone.','registration':'Only measured report plus >=3 spread observed correspondences can be ready; root PM marks ready.','artAbsent':'Do not include 1055 nonexistent PNGs as ready. Production queue separate from actual runtime regions.','roads':'Original nodes/widths, display clipped to blue if necessary; no source edit.','rider':'Keep independent, gate by ready region plus full blue route.'},firstBatch=[{'id':r['id'],'sourceStructure':str(R/'structures'/f"{r['id']}-structure.json"),'artStatus':r['artStatus']} for r in P['regions'] if r['id'] in ['REGION-B','REGION-C','REGION-D']],status='planning-to-runtime-mapping-only-no-published-atlas'))
manifest=dict(date='2026-11-03',productionType='code-native-source-geometry-input',generatedArtReadOrChanged=False,sources=P['source'],outputs=[dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='source-manifest.json']);save('source-manifest.json',manifest)
print(json.dumps({'seams':[(s['id'],len(s['sourceRoadPassages']),len(s['lowGroundConflictCandidate']['groundFootprintConflicts'])) for s in contracts],'atlas':P['summary']}))
