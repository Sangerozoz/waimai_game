#!/usr/bin/env python3
"""Save Tiled -> isolated existing-Cocos visual preview. Never writes input/user/main maps."""
import argparse,copy,json,math,shutil,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def props(o):return{p['name']:p['value']for p in o.get('properties',[])}
def finite(v):
 if type(v)not in(int,float)or not math.isfinite(v):raise ValueError('Only finite numeric geometry is supported')
 return v
def project(p):
 dx,dy=[p[k]-PROJ['originMap'][k]for k in(0,1)];return[896+16*(dx*PROJ['axisX'][k]+dy*PROJ['axisY'][k])for k in(0,1)]
def unproject(q):
 x,y=[(q[k]-896)/16 for k in(0,1)];a,b=PROJ['axisX'];c,d=PROJ['axisY'];det=a*d-b*c;return[PROJ['originMap'][0]+(d*x-c*y)/det,PROJ['originMap'][1]+(-b*x+a*y)/det]
def layers(ls,show=True,offset=(0,0)):
 for l in ls:
  vis=show and l.get('visible',True);off=[offset[k]+finite(l.get(('offsetx','offsety')[k],0))for k in(0,1)]
  if l.get('opacity',1)!=1:raise ValueError('Partial opacity unsupported; use layer visibility')
  if l['type']=='group':yield from layers(l.get('layers',[]),vis,off)
  elif l['type']=='objectgroup'and vis:yield l,off
  elif l['type']not in ['group','objectgroup']:raise ValueError('Only the supplied object-layer map is supported')
def export(args):
 global PROJ
 src=Path(args.map).resolve();output=Path(args.output).resolve();doc=read(src);base=read(HERE/'metadata/base-scene.json');PROJ=base['projection'];catalog={a['id']:a for a in read(HERE/'metadata/catalog.json')['assets']};oldblocks={b['persistentId']:b for b in base['blocks']};gids={}
 if output in [HERE,HERE/'preview']or HERE not in output.parents:raise ValueError('Output must be an isolated child directory such as preview-user; frozen preview/user-layout cannot be overwritten')
 if src==output or output in src.parents:raise ValueError('Output cannot contain the input map')
 for ts0 in doc['tilesets']:
  ts=read(src.parent/ts0['source'])if 'source'in ts0 else ts0
  for t in ts['tiles']:gids[ts0['firstgid']+t['id']]=props(t)['assetId']
 baseidentity=read(HERE/'metadata/base-object-identity.json')
 blocks=[];grounds=[];assets=[copy.deepcopy(a)for a in read(HERE/'preview/assets/asset-manifest.json')['assets']if a['kind']in['material','rider']];seen=set();objectids=set();mapping=[];warnings=[]
 for layer,offset in layers(doc['layers']):
  objs=layer.get('objects',[])
  if layer.get('draworder','topdown')=='topdown':objs=sorted(objs,key=lambda o:o.get('y',0))
  elif layer['draworder']!='index':raise ValueError('Unsupported draw order')
  for orig in objs:
   oid=orig['id']
   if oid in objectids:raise ValueError('Tiled object ID must remain unique')
   objectids.add(oid);o=copy.deepcopy(orig);aid=None
   if 'template'in o:
    tp=(src.parent/o['template']).resolve();tpl=read(tp);default=tpl['object'];o={**default,**o};o['properties']=default.get('properties',[])+orig.get('properties',[]);aid=props(o).get('assetId')
   if not o.get('visible',True):continue
   if o.get('rotation',0)!=0 or o.get('opacity',1)!=1:raise ValueError('Rotation/opacity unsupported; visual positive uniform size and visibility supported')
   x=finite(o.get('x',0))+offset[0];y=finite(o.get('y',0))+offset[1];pr=props(o)
   if 'polygon'in o:
    mat=pr.get('surfaceAssetId');id=o.get('name')or 'user-surface-'+str(oid)
    if id in seen:raise ValueError('Duplicate ground/user visual ID')
    seen.add(id);poly=[unproject([x+finite(q['x']),y+finite(q['y'])])for q in o['polygon']]
    if len(poly)<3:raise ValueError('Polygon requires3 points')
    if mat not in {s['materialId']for s in base['groundSurfaces']}:raise ValueError('Unknown ground material; reuse supplied ground objects')
    grounds.append({'id':id,'materialId':mat,'polygonMap':poly});continue
   if not aid:
    gid=o.get('gid',0)
    if gid&0xf0000000:raise ValueError('Mirror/rotation flags unsupported')
    aid=gids.get(gid)
   if aid not in catalog:raise ValueError('Missing asset definition, no blank fallback')
   a=copy.deepcopy(catalog[aid]);w,h=finite(o['width']),finite(o['height']);cw,ch=a['worldSizeUnits'];sx=w/(16*cw);sy=h/(16*ch)
   if not sx>0 or not math.isclose(sx,sy,rel_tol=1e-5):raise ValueError('Keep positive uniform aspect ratio (Tiled lock aspect ratio)')
   u,v=a['anchorUV'];anchor=unproject([x+u*w,y-(1-v)*h]);original=pr.get('persistentId');explicit=pr.get('userVisualId');pid=explicit or original or 'user-object-'+str(oid);copied=pr.get('copiedFrom')
   if not explicit and original in oldblocks and baseidentity.get(str(oid))!=original:copied=original;pid='user-object-'+str(oid)
   if explicit and pid in seen:raise ValueError('Explicit userVisualId duplicated')
   if pid in seen:copied=original;pid='user-object-'+str(oid)
   if pid in seen:raise ValueError('Generated visual ID collision; set unique userVisualId')
   seen.add(pid);isold=pid in oldblocks
   if original and not isold:copied=copied or original
   a['file']=Path(a['packageFile']).name;a['id']='instance-'+pid;a['worldSizeUnits']=[w/16,h/16]
   # Runtime metadata is visual only. No per-instance original-native/provenance payload.
   a={k:a[k]for k in['id','file','kind','nativeSize','sha256','worldSizeUnits','anchorUV','nativePixelsPerUnit']if k in a};a.setdefault('nativePixelsPerUnit',1);assets.append(a)
   b={'assetId':a['id'],'sourceAssetId':aid,'persistentId':pid,'anchorMap':anchor,'sortMap':anchor,'editorRenderOrder':len(blocks),'userVisualOnly':True,'tiledObjectId':oid}
   if copied:b['copiedFrom']=copied
   if isold:b['originalBindingReferenceOnly']=pid
   blocks.append(b);mapping.append({'tiledObjectId':oid,'persistentId':pid,'copiedFrom':copied,'libraryAssetId':aid,'anchorMap':anchor,'worldSizeUnits':a['worldSizeUnits'],'nodeScale':1,'uniformScaleFromCanonical':sx,'newBusinessOrNavigationBinding':False})
   if a['kind']not in['material','rider']and '候选' in catalog[aid]['deliveryStatus']:warnings.append(pid+': candidate asset; body/camera not confirmed, user placement permitted')
 if not blocks:raise ValueError('No visible visual instances')
 layout=copy.deepcopy(base);layout.update({'blocks':blocks,'groundSurfaces':grounds,'userLayoutSource':src.name,'userVisualEditing':True,'status':'user-editable-rough-prototype-not-final-accepted'})
 # Original source/road/POI/rider metadata remains the frozen reference, never cloned
 # into new visual instances. Source bindings are historical source evidence only.
 layout['originalBindingsAreReadonlyReferences']=True
 if 'sourceAccounting'in layout:layout['originalSourceAccountingReadonly']=layout.pop('sourceAccounting')
 layout['userVisualStatistics']={'visibleInstances':len(blocks),'newBusinessBindings':0,'sourceReferenceOnly':True}
 selected=set(args.focus_id.split(','))if args.focus_id else set()
 camera=copy.deepcopy(base['cameraViews']['compound-market'])
 if selected:
  ext=[]
  for b in blocks:
   if b['persistentId']not in selected:continue
   a=next(a for a in assets if a['id']==b['assetId']);q=project(b['anchorMap']);w,h=[v*16 for v in a['worldSizeUnits']];u,v=a['anchorUV'];ext.extend([[q[0]-u*w,q[1]-v*h],[q[0]+(1-u)*w,q[1]+(1-v)*h]])
  if not ext:raise ValueError('focus IDs not present')
  lo=[min(q[k]for q in ext)for k in(0,1)];hi=[max(q[k]for q in ext)for k in(0,1)];camera={'focusMap':unproject([(lo[k]+hi[k])/2 for k in(0,1)]),'fitWidthUnits':max(22,(hi[0]-lo[0])/16*1.2),'fitHeightUnits':max(20,(hi[1]-lo[1])/16*1.2),'screenOffset':[0,0]}
 fw,fh=camera['fitWidthUnits'],camera['fitHeightUnits'];vh=max(fh,fw/2);vw=vh*2.1;q=project(camera['focusMap']);pts=[unproject([q[0]+16*dx,q[1]+16*dy])for dx in[-vw/2,vw/2]for dy in[-vh/2,vh/2]]
 bounds={'minX':min(p[0]for p in pts)-5,'maxX':max(p[0]for p in pts)+5,'minY':min(p[1]for p in pts)-5,'maxY':max(p[1]for p in pts)+5};region={'id':'user-preview-ground','bounds':bounds,'surfaceIds':[s['id']for s in grounds],'roadIds':[r['id']for r in base['roads']],'includeAllSceneReferences':True,'maxCanvasEdge':2048};camera['activeGroundRegionIds']=[region['id']];layout['groundRegions'].append(region);layout['cameraViews']['user']=camera
 # All validation finishes before replacing isolated output. User input never written.
 if not output.exists():shutil.copytree(HERE/'preview',output,ignore=shutil.ignore_patterns('*.png','scene-layout.json','asset-manifest.json'))
 used={a['file']:a for a in assets}
 for f in(output/'assets').glob('*.png'):
  if f.name not in used:f.unlink()
 for f,a in used.items():
  source=next((HERE/r['packageFile']for r in catalog.values()if Path(r['packageFile']).name==f),None)
  if source is None:raise ValueError('Referenced PNG missing')
  if hashlib.sha256(source.read_bytes()).hexdigest()!=a['sha256']:raise ValueError('Canonical PNG SHA changed')
  shutil.copyfile(source,output/'assets'/f)
 write(output/'assets/scene-layout.json',layout);write(output/'assets/asset-manifest.json',{'schemaVersion':1,'projection':PROJ,'assets':assets})
 write(output/'user-export-report.json',{'input':str(src),'instances':len(blocks),'grounds':len(grounds),'uniquePNG':len(used),'PNGBytes':sum((output/'assets'/f).stat().st_size for f in used),'instancesMapping':mapping,'warnings':warnings+['Placement/collision is user-controlled; no automatic repositioning or precision-layout acceptance.'],'inputMapWritten':False,'originalRoadsSourceBindingsRiderMetadataUnchanged':True})
 print(json.dumps({'output':str(output),'entry':'?view=user','instances':len(blocks),'uniquePNG':len(used),'inputUnchanged':True},ensure_ascii=False))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--map',default=str(HERE/'user-layout.tmj'));parser.add_argument('--output',default=str(HERE/'preview-user'));parser.add_argument('--focus-id',default='');export(parser.parse_args())
