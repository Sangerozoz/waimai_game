#!/usr/bin/env python3
"""Isolated editable Tiled bridge. init refuses reset; export preserves edits."""
import json, math, hashlib, shutil, argparse, subprocess, sys, importlib.util
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode = True
I=Path(__file__).resolve().parent; R=I.parent; B=R.parent; V=R/'viewer'; M=I/'mixed-street.tmj'
spec=importlib.util.spec_from_file_location('bridge',B/'revision-004/tiled_street.py');bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
read=bridge.read;write=bridge.write;sha=bridge.sha;props=bridge.props;properties=bridge.properties
meta=read(B/'revision-004/integration/bridge-meta.json');plan=read(R/'planning/mixed-street-layout.json')
def project(p):return bridge.project(p,meta)
def unproject(p):return bridge.unproject(p,meta)
def snapshot():
 paths=list((R/'native').rglob('*'))+list((B/'revision-004').rglob('*'))+list((R/'runtime-280').rglob('*'))+[B/'revision-003/B01-road-aligned-native-v1.png',B/'revision-003/native-calibration.json',B/'pilot/T01-v1.png',R/'planning/mixed-street-layout.json']
 return {str(p.resolve()):sha(p) for p in paths if p.is_file()}
def init():
 if M.exists() or V.exists():raise ValueError('Refusing reset: editable map/viewer exists; use export')
 write(I/'inputs-before.json',snapshot());(I/'assets').mkdir(exist_ok=True)
 old=read(R/'runtime-280/viewer/assets/asset-manifest.json');assets=[];cal=[];checks=[]
 for aid,oid in [('B01','instance-building-B01'),('T01','instance-tree-west'),('HC-R-NE','HC-R-NE'),('HC-R-SW','HC-R-SW'),('S01-paving','S01-paving'),('S02-asphalt','S02-asphalt')]:
  a=next(dict(a) for a in old['assets'] if a['id']==oid);a['id']=aid;assets.append(a);shutil.copyfile(R/'runtime-280/viewer/assets'/a['file'],I/'assets'/a['file'])
  if aid in ['B01','T01']:cal.append({'id':aid,'status':'retained-accepted-calibration','worldSizeUnits':a['worldSizeUnits'],'anchorUV':a['anchorUV'],'sourceNativePPU':111.2618392940353 if aid=='B01' else 175,'originalAnchorPixel':[626.5,920.5] if aid=='B01' else None})
 # Hand-estimated visible ground corners: left, front, right, inferred rear. NOT registration controls.
 corners={'B02':[[180,878],[399,1147],[1048,811],[829,542]],'B03':[[335,922],[475,1169],[923,945],[783,698]],'B04':[[107,869],[340,1120],[1138,712],[905,461]],'B05':[[180,1060],[420,1233],[1088,879],[848,706]]}
 defs=[(k,f'{k}-001',f'{k}-v1.png',f'{k}-runtime-280.png') for k in corners]+[('T02','T02-free-001','T02-free-v1.png','T02-free-runtime-280.png'),('T03','T03-pine-001','T03-pine-v1.png','T03-pine-runtime-280.png'),('L-near','retry-near-001','L01-road-near-v1.png',None),('L-far','far-001','L01-road-far-v1.png',None)]
 for aid,folder,raw,rt in defs:
  root=R/'native'/folder;raw=root/raw;p=read(root/'provenance.json');source=next(Path(v) for k,v in p.items() if isinstance(v,str) and '/.codex/generated_images/' in v)
  actual=sha(raw);assert sha(source)==actual,(aid,'tool source mismatch');assert actual in json.dumps(p)
  checks.append({'id':aid,'source':str(source),'native':str(raw),'sha256':actual,'actualToolSourceEqual':True})
  if rt:
   rt=root/rt;der=read(rt.with_suffix('.runtime.json'));shutil.copyfile(rt,I/'assets'/rt.name)
  else:
   rt=I/'assets'/f'{aid}-280.png';subprocess.run([sys.executable,str(R/'runtime-size-pilot/export_runtime.py'),'--output-dir',str(I/'assets'),'--max-edge','280','--single-source',str(raw),'--single-target',str(rt)],check=True);der=read(rt.with_suffix('.runtime.json'))
  assert der['sourceSHA256']==actual and sha(I/'assets'/rt.name)==der['sha256'];assert max(Image.open(I/'assets'/rt.name).size)<=280
  if aid in corners:
   co=corners[aid];dims=next(b['dimensionsCandidate'] for b in plan['buildings'] if b['id']==aid)
   u=plan['referenceFrame']['frontageTangent'];n=plan['referenceFrame']['positiveRoadNormal'];p0=project([0,0]);pu=math.dist(project(u),p0);pn=math.dist(project(n),p0)
   lengths=[math.dist(co[1],co[2]),math.dist(co[0],co[1])];units=[dims['frontage']*pu/16,dims['depth']*pn/16];ppu=sum(a*b for a,b in zip(lengths,units))/sum(x*x for x in units);anchor=[sum(c[k] for c in co)/4 for k in (0,1)];notes='manual visible ground corners + inferred hidden rear; scalar edge-length least squares against PM candidate dimensions, not surveyed'
  else:
   co=None;anchor={'T02':[620,1104],'T03':[627,1140],'L-near':[624,1092],'L-far':[626,1090]}[aid];ppu={'T02':175,'T03':175,'L-near':175,'L-far':175}[aid];notes='manual root/foot; candidate tree scale 175 native px/unit; lamp pole ~4 projected world units, candidate only'
  x,y,x2,y2=der['cropBox'];w,h=x2-x,y2-y;uv=[(anchor[0]-x)/w,(anchor[1]-y)/h];world=[w/ppu,h/ppu]
  a={'id':aid,'file':rt.name,'kind':'building' if aid[0]=='B' else 'fixture','nativeSize':der['runtimeSize'],'sha256':der['sha256'],'anchorUV':uv,'nativePixelsPerUnit':1,'worldSizeUnits':world,'projectionId':plan['projection']['id'],'runtimeDerivation':der};assets.append(a)
  cal.append({'id':aid,'status':'hand-estimated-candidate-not-registration-ready','sourceNativeSize':list(Image.open(raw).size),'sourceNativeSHA256':actual,'groundCornersPixelLeftFrontRightRear':co,'anchorPixel':anchor,'nativePixelsPerUnit':ppu,'cropBox':der['cropBox'],'anchorUV':uv,'worldSizeUnits':world,'method':notes,'positiveUniformOnly':True})
 write(I/'provenance-check.json',checks);write(I/'asset-calibration.json',{'status':'candidate-no-user-acceptance','assets':cal});write(I/'asset-manifest.json',{'schemaVersion':1,'projection':plan['projection'],'assets':assets})
 by={a['id']:a for a in assets};ids=['B01','B02','B03','B04','B05','T01','T02','T03','L-near','L-far'];tiles=[]
 for i,aid in enumerate(ids):
  a=by[aid];tiles.append({'id':i,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':properties({'assetId':aid})})
 objs=[];natural=0
 for item in plan['buildings']+plan['fixtures']:
  if 'id'in item:aid=item['id']
  else:
   key=item['assetKey'];aid='T01' if key=='T01-v1' else 'L-near' if 'near' in key else 'L-far' if 'far' in key else 'T02'
   if aid=='T02':
    natural+=1
    # Only two pine comparisons, no pine mass deployment.
    if natural in (2,5):aid='T03'
  a=by[aid];w,h=[x*16 for x in a['worldSizeUnits']];x,y=project(item['anchorMap']);au,av=a['anchorUV'];objs.append({'id':len(objs)+1,'name':item['persistentId'],'type':'sprite','gid':ids.index(aid)+1,'x':x-au*w,'y':y+(1-av)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':properties({'persistentId':item['persistentId'],'assetId':aid})})
 objs.sort(key=lambda o:o['y']-(1-by[props(o)['assetId']]['anchorUV'][1])*o['height'])
 surfs=[]
 for s in plan['groundSurfaces']:
  poly=[project(p) for p in s['polygonMap']];x,y=poly[0];surfs.append({'id':len(objs)+len(surfs)+1,'name':s['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y} for a,b in poly],'properties':properties({'surfaceAssetId':s['materialId']})})
 doc={'type':'map','version':'1.10','tiledversion':'1.11.2','orientation':'orthogonal','renderorder':'right-down','width':96,'height':96,'tilewidth':32,'tileheight':32,'infinite':False,'nextobjectid':100,'nextlayerid':4,'tilesets':[{'firstgid':1,'name':'Five buildings and inward lamps','tilewidth':280,'tileheight':280,'tilecount':len(tiles),'columns':0,'objectalignment':'bottomleft','tiles':tiles}],'layers':[{'id':1,'name':'Controlled ground colours and paving','type':'objectgroup','draworder':'index','objects':surfs},{'id':2,'name':'Static sprites — editable index order','type':'objectgroup','draworder':'index','objects':objs}],'properties':properties({'status':'editable-candidate-not-accepted','projectionId':plan['projection']['id']})}
 shutil.copyfile(B/'revision-004/integration/original-roads.png',I/'original-roads.png');doc['layers'].insert(1,{'id':3,'name':'Original roads — locked reference','type':'imagelayer','image':'original-roads.png','visible':True,'locked':True});write(M,doc);write(I/'bridge-meta.json',meta);export()
def export():
 manifest=read(I/'asset-manifest.json');doc=read(M);originals={a['id']:a for a in manifest['assets']};gids={t['id']+ts['firstgid']:props(t)['assetId'] for ts in doc['tilesets'] for t in ts['tiles']};layout=read(R/'runtime-280/viewer/assets/scene-layout.json');layout.update({'roads':plan['roads'],'projection':plan['projection'],'blocks':[],'groundSurfaces':[],'parcels':[],'bounds':{'minX':-1680,'maxX':-1500,'minY':-115,'maxY':320}});out=[dict(a) for a in manifest['assets'] if a['kind'] in ['material','rider']];report=[]
 for layer,shift in bridge.layers(doc['layers']):
  objs=[o for o in layer['objects'] if o.get('visible',True)]
  if layer.get('draworder','topdown')=='topdown':objs.sort(key=lambda o:o['y'])
  elif layer['draworder']!='index':raise ValueError('unsupported order')
  for o in objs:
   assert not o.get('rotation',0)
   if 'polygon'in o:
    layout['groundSurfaces'].append({'id':o['name'],'materialId':props(o)['surfaceAssetId'],'polygonMap':[unproject([o['x']+shift[0]+v['x'],o['y']+shift[1]+v['y']]) for v in o['polygon']]});continue
   assert not o['gid']&0xf0000000
   a=dict(originals[gids[o['gid']]]);sx=o['width']/(a['worldSizeUnits'][0]*16);sy=o['height']/(a['worldSizeUnits'][1]*16);assert sx>0 and math.isclose(sx,sy,rel_tol=1e-6),'uniform scaling only'
   au,av=a['anchorUV'];anchor=unproject([o['x']+shift[0]+au*o['width'],o['y']+shift[1]-(1-av)*o['height']]);pid=props(o)['persistentId'];
   if gids[o['gid']]=='B01':
    assert math.dist(anchor,plan['referenceFrame']['lockedB01AnchorMap'])<1e-10 and math.isclose(sx,1,abs_tol=1e-10),'B01 anchor/scale locked'
   aid='instance-'+pid;a.update({'id':aid,'worldSizeUnits':[x*sx for x in a['worldSizeUnits']]});out.append(a);idx=len(report);layout['blocks'].append({'assetId':aid,'anchorMap':anchor,'sortMap':anchor,'persistentId':pid,'sourceAssetId':gids[o['gid']],'editorRenderOrder':idx});report.append({'persistentId':pid,'sourceAssetId':gids[o['gid']],'anchorMap':anchor,'uniformScale':sx,'editorRenderOrder':idx,'layerId':layer['id'],'groupOffset':shift})
 assert len({x['persistentId'] for x in report})==len(report)
 ext=[]
 for block in layout['blocks']:
  a=next(a for a in out if a['id']==block['assetId']);px,py=project(block['anchorMap']);px=(px-meta['editorOrigin'][0])/16;py=(py-meta['editorOrigin'][1])/16;w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[px-u*w,py-v*h],[px+(1-u)*w,py+(1-v)*h]])
 xmin=min(p[0] for p in ext);xmax=max(p[0] for p in ext);ymin=min(p[1] for p in ext);ymax=max(p[1] for p in ext)
 focus=unproject([meta['editorOrigin'][0]+(xmin+xmax)*8,meta['editorOrigin'][1]+(ymin+ymax)*8]);layout['camera']={'focusMap':focus,'fitWidthUnits':(xmax-xmin)*1.12,'fitHeightUnits':(ymax-ymin)*1.18,'viewWidthUnits':35,'screenOffset':[0,0]};layout['status']='mixed-street-candidate-not-user-accepted';layout['tiledSourceSHA256']=sha(M)
 if not V.exists():
  shutil.copytree(R/'runtime-280/viewer',V,ignore=shutil.ignore_patterns('*.png','integration-record.json'))
  f=V/'assets/main/index.probe41.js';code=f.read_text();code=code.replace('u.fillStyle=gs.materialId==="S02-asphalt"?g:w','u.fillStyle=({"G01-lawn":"#9da981","G02-planting":"#82906e","G03-meadow":"#a7ae8d"})[gs.materialId]||(gs.materialId==="S02-asphalt"?g:w)')
  # Fixed-height Cocos landscape: fit both projected extents in 1280-high design frame.
  code=code.replace('720/((null!=(o=f.camera.viewWidthUnits)?o:52)*this.ppm)','Math.min(1280/(f.camera.fitHeightUnits*this.ppm),1280*(innerWidth/innerHeight)/(f.camera.fitWidthUnits*this.ppm))*(new URLSearchParams(location.search).get("view")==="close"?1.5:1)')
  f.write_text(code)
  html=V/'index.html';html.write_text(html.read_text().replace('</body>','<div style="position:fixed;top:12px;left:12px;background:#ffffffe8;padding:10px;font:14px system-ui;border-radius:8px">五楼混合街段 · 候选同场检查 <a href="?view=overall">总体</a> · <a href="?view=close">近景</a></div></body>'))
 used={a['file'] for a in out}
 for f in (V/'assets').glob('*.png'):
  if f.name not in used:f.unlink()
 for file in used:shutil.copyfile(I/'assets'/file,V/'assets'/file)
 write(V/'assets/scene-layout.json',layout);write(V/'assets/asset-manifest.json',{'schemaVersion':1,'projection':plan['projection'],'assets':out})
 assert layout['roads']==plan['roads'] and layout['projection']==plan['projection'];before=read(I/'inputs-before.json');after=snapshot();assert before==after,'read-only inputs changed'
 imgs=[{'file':f,'bytes':(V/'assets'/f).stat().st_size,'size':list(Image.open(V/'assets'/f).size),'sha256':sha(V/'assets'/f)} for f in sorted(used)];assert all(max(x['size'])<=280 for x in imgs)
 write(I/'export-report.json',{'objects':report,'surfaces':len(layout['groundSurfaces']),'uniquePNG':len(imgs),'PNGBytes':sum(x['bytes'] for x in imgs),'images':imgs,'roadsProjectionExactlyEqual':True,'allInputSHAPreserved':True,'tiledSHA256':sha(M),'gameTestsRun':False,'status':'export-integrity-only-not-visual-acceptance'})
 print('Exported',len(report),'sprites,',len(layout['groundSurfaces']),'surfaces,',len(imgs),'unique PNG')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['init','export']);args=p.parse_args();init() if args.command=='init' else export()
