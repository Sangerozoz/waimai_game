#!/usr/bin/env python3
"""Plan-gated editable Tiled -> existing Cocos shell. Never consumes pending plan implicitly."""
import sys
sys.dont_write_bytecode=True
import argparse,copy,math,shutil
from pathlib import Path
import asset_library as lib
I,R,V=lib.I,lib.R,lib.V
read,write,sha=lib.read,lib.write,lib.sha
M=I/'neighborhood.tmj'
META=read(lib.OLD/'integration/bridge-meta.json')
def props(o):return {p['name']:p['value'] for p in o.get('properties',[])}
def properties(d):return [{'name':k,'type':'bool' if isinstance(v,bool) else 'float' if isinstance(v,(int,float)) else 'string','value':v} for k,v in d.items()]
def project(q):
 p=META['projection'];dx,dy=[q[k]-p['originMap'][k] for k in (0,1)];return [META['editorOrigin'][k]+16*(dx*p['axisX'][k]+dy*p['axisY'][k]) for k in (0,1)]
def unproject(q):
 p=META['projection'];x,y=[(q[k]-META['editorOrigin'][k])/16 for k in (0,1)];a,b=p['axisX'];c,d=p['axisY'];det=a*d-b*c;return [p['originMap'][0]+(d*x-c*y)/det,p['originMap'][1]+(-b*x+a*y)/det]
def layer_objects(ls,visible=True,offset=(0,0)):
 for l in ls:
  show=visible and l.get('visible',True);shift=[offset[k]+l.get(('offsetx','offsety')[k],0) for k in (0,1)]
  if show and l.get('opacity',1)!=1:raise ValueError('Partial layer opacity unsupported')
  if l['type']=='group':yield from layer_objects(l.get('layers',[]),show,shift)
  elif show and l['type']=='objectgroup':yield l,shift

def verify_roads(plan):
 assert plan['projection']==META['projection'],'Projection differs from accepted 005'
 ctx=read(R/'planning/source-context.json');city=read(ctx['source']);assert sha(ctx['source'])==ctx['sourceSHA256']
 nodes={n['id']:[n['x'],n['y']] for n in city['nodes']};roads={r['id']:r for r in city['roads']}
 assert plan['roads'] and len({r['id'] for r in plan['roads']})==len(plan['roads'])
 for r in plan['roads']:
  s=roads[r['id']];assert r['nodes']==[nodes[n] for n in s['nodes']],'Road node order/coordinates changed'
  assert r['width']==s['width'] and r['direction']==s['direction'],'Road width/direction changed'
  if 'sourceNodeIds'in r:assert r['sourceNodeIds']==s['nodes']
 return True

def initialize(planpath,approvedsha):
 if M.exists() or V.exists():raise ValueError('Refusing to reset existing editable map/viewer; export instead')
 plan=read(planpath);der=plan.get('derivation',{});parentpath=Path(der.get('parentInputPath',planpath))
 if not approvedsha or sha(parentpath)!=approvedsha or (der and der['parentApprovedSHA256']!=approvedsha):raise ValueError('Requires actual parent-notified original SHA; derived plan has separate SHA')
 verify_roads(plan);lib.validate();assets=read(I/'asset-library.json')['assets'];by={a['id']:a for a in assets};ids=[a['id'] for a in assets if a['kind'] not in ['material','rider']];tiles=[];objects=[]
 aliases={'T01-v1':'T01','T02-v1':'T02','T03-v1':'T03','L01-road-near-v1':'L-near','L01-road-far-v1':'L-far'}
 for n,aid in enumerate(ids):
  a=by[aid];tiles.append({'id':n,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':properties({'assetId':aid})})
 for item in plan.get('buildings',[])+plan.get('fixtures',[])+plan.get('parkedVehicles',[]):
  aid=item.get('libraryAssetId',item.get('assetKey',item.get('id')));aid=aliases.get(aid,aid);assert aid in ids,'Plan must specify libraryAssetId from the 006 library'
  if 'hold' in by[aid].get('availability','') and aid not in plan.get('comparisonAssets',[]):raise ValueError('Held asset requires explicit comparisonAssets entry: '+aid)
  if by[aid]['kind']=='parked-vehicle':
   assert item in plan.get('parkedVehicles',[]) and item.get('parkingSpaceId') in {p['id'] for p in plan.get('parkingSpaces',[])},'V2 only in explicitly planned parking spaces'
  a=by[aid];x,y=project(item['anchorMap']);u,v=a['anchorUV'];w,h=[q*16 for q in a['worldSizeUnits']];pid=item['persistentId'];objects.append({'id':len(objects)+1,'name':pid,'gid':ids.index(aid)+1,'type':'sprite','x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':properties({'assetId':aid,'persistentId':pid,'parkingSpaceId':item.get('parkingSpaceId','')})})
 assert objects,'No actual scene objects in approved plan';objects.sort(key=lambda o:o['y']-(1-by[props(o)['assetId']]['anchorUV'][1])*o['height'])
 surfaces=[]
 for s in plan.get('groundSurfaces',[]):
  q=[project(q) for q in s['polygonMap']];x,y=q[0];surfaces.append({'id':len(objects)+len(surfaces)+1,'name':s['id'],'x':x,'y':y,'polygon':[{'x':a-x,'y':b-y} for a,b in q],'properties':properties({'surfaceAssetId':s['materialId']})})
 doc={'type':'map','version':'1.10','tiledversion':'1.11.2','orientation':'orthogonal','renderorder':'right-down','width':256,'height':256,'tilewidth':32,'tileheight':32,'infinite':False,'nextobjectid':len(objects)+len(surfaces)+1,'nextlayerid':3,'tilesets':[{'firstgid':1,'name':'006 library','tilewidth':280,'tileheight':280,'tilecount':len(tiles),'columns':0,'objectalignment':'bottomleft','tiles':tiles}],'layers':[{'id':1,'name':'Ground — original roads draw after these polygons','type':'objectgroup','draworder':'index','objects':surfaces},{'id':2,'name':'Static editable index order','type':'objectgroup','draworder':'index','objects':objects}]}
 write(I/'approved-plan.json',plan);write(I/'plan-gate.json',{'planPath':str(parentpath.resolve()),'approvedSHA256':approvedsha,'runtimePlanPath':str(Path(planpath).resolve()),'runtimePlanSHA256':sha(planpath),'derivation':der,'status':'parent-notified-plan-snapshot','roadsCheckedAgainstFullCity':True,'snapshotSHA256':sha(I/'approved-plan.json')});write(M,doc);export()

def export():
 gate=read(I/'plan-gate.json');plan=read(I/'approved-plan.json');assert sha(I/'approved-plan.json')==gate['snapshotSHA256']
 # Verify parent-approved original path has not silently changed since gate creation.
 assert sha(gate['planPath'])==gate['approvedSHA256'],'Stable plan changed; await parent update'
 assert sha(gate['runtimePlanPath'])==gate['runtimePlanSHA256'],'Derived subset changed'
 from suburb_regions import increment_plan
 plan=increment_plan(sys.modules[__name__],plan)
 from b07_region import increment_plan as increment_b07
 plan=increment_b07(sys.modules[__name__],plan)
 from north_region import increment_plan as increment_north
 plan=increment_north(sys.modules[__name__],plan)
 from round2_region import increment_plan as increment_round2
 plan=increment_round2(sys.modules[__name__],plan)
 from round3_region import increment_plan as increment_round3
 plan=increment_round3(sys.modules[__name__],plan)
 from round4_region import increment_plan as increment_round4
 plan=increment_round4(sys.modules[__name__],plan)
 from native_comparison_region import increment_plan as increment_native_comparison
 plan=increment_native_comparison(sys.modules[__name__],plan)
 from round5_region import increment_plan as increment_round5
 plan=increment_round5(sys.modules[__name__],plan)
 from compound_region import increment_plan as increment_compound
 plan=increment_compound(sys.modules[__name__],plan)
 verify_roads(plan);lib.validate();doc=read(M);library=read(I/'asset-library.json');by={a['id']:a for a in library['assets']};gids={ts['firstgid']+t['id']:props(t)['assetId'] for ts in doc['tilesets'] for t in ts['tiles']};assets=[copy.deepcopy(a) for a in library['assets'] if a['kind'] in ['material','rider']];blocks=[];surfaces=[];report=[];seen=set()
 for l,shift in layer_objects(doc['layers']):
  objects=[o for o in l['objects'] if o.get('visible',True)]
  if l.get('draworder','topdown')=='topdown':objects.sort(key=lambda o:o['y'])
  elif l['draworder']!='index':raise ValueError('Unsupported draw order')
  for o in objects:
   assert not o.get('rotation',0) and o.get('opacity',1)==1
   if 'polygon'in o:
    mat=props(o)['surfaceAssetId'];assert mat in ['S01-paving','S02-asphalt','G01-lawn','G02-planting','G03-meadow','G04-suburb-lawn','G05-garden-soil','G06-b07-garden','G07-north-garden','G08-r2-courtyard','G09-r3-planted','G10-r3-courtyard','G11-r4-courtyard','G12-r4-planted','G13-r5-garden'];surfaces.append({'id':o['name'],'materialId':mat,'polygonMap':[unproject([o['x']+shift[0]+q['x'],o['y']+shift[1]+q['y']]) for q in o['polygon']]});continue
   assert not o['gid']&0xf0000000,'Mirroring unsupported';aid=gids[o['gid']];a=copy.deepcopy(by[aid]);
   if a['kind']=='parked-vehicle':assert props(o).get('parkingSpaceId') in {p['id'] for p in plan.get('parkingSpaces',[])},'Unplanned parking rejected'
   sx=o['width']/(16*a['worldSizeUnits'][0]);sy=o['height']/(16*a['worldSizeUnits'][1]);assert sx>0 and math.isclose(sx,sy,rel_tol=1e-6),'Positive uniform scale only';u,v=a['anchorUV'];anchor=unproject([o['x']+shift[0]+u*o['width'],o['y']+shift[1]-(1-v)*o['height']]);pid=props(o)['persistentId'];assert pid and pid not in seen;seen.add(pid)
   if aid in ['B01','T01']:assert math.isclose(sx,1,abs_tol=1e-9),'Accepted B01/T01 scale fixed'
   if pid=='mixed-building-B01':assert math.dist(anchor,[-1596.5787045725883,58.400981377657935])<1e-9,'Accepted B01 anchor fixed'
   if 'hold' in a.get('availability','') and aid not in plan.get('comparisonAssets',[]):raise ValueError('Held asset not approved as comparison: '+aid)
   a.update({'id':'instance-'+pid,'worldSizeUnits':[q*sx for q in a['worldSizeUnits']]});assets.append(a);idx=len(blocks);blocks.append({'assetId':a['id'],'sourceAssetId':aid,'persistentId':pid,'anchorMap':anchor,'sortMap':anchor,'editorRenderOrder':idx});report.append({'persistentId':pid,'libraryAssetId':aid,'anchorMap':anchor,'uniformScale':sx,'editorRenderOrder':idx,'layerId':l['id'],'groupOffset':shift})
 assert blocks,'No visible scene objects';layout=read(lib.OLD/'viewer/assets/scene-layout.json');layout.update({'roads':plan['roads'],'projection':plan['projection'],'blocks':blocks,'groundSurfaces':surfaces,'parcels':[],'status':'006-scene-candidate-not-user-accepted','tiledSourceSHA256':sha(M)})
 pts=[q for s in surfaces for q in s['polygonMap']]+[b['anchorMap'] for b in blocks];layout['bounds']={'minX':min(q[0] for q in pts)-25,'maxX':max(q[0] for q in pts)+25,'minY':min(q[1] for q in pts)-25,'maxY':max(q[1] for q in pts)+25}
 ext=[];byinst={a['id']:a for a in assets}
 for b in blocks:
  a=byinst[b['assetId']];x,y=project(b['anchorMap']);x=(x-META['editorOrigin'][0])/16;y=(y-META['editorOrigin'][1])/16;w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ext.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
 lo=[min(q[k] for q in ext) for k in (0,1)];hi=[max(q[k] for q in ext) for k in (0,1)];focus=unproject([META['editorOrigin'][k]+8*(lo[k]+hi[k]) for k in (0,1)]);layout['camera']={'focusMap':focus,'fitWidthUnits':(hi[0]-lo[0])*1.12,'fitHeightUnits':(hi[1]-lo[1])*1.18,'screenOffset':[0,0]}
 layout['cameraViews']={'overall':copy.deepcopy(layout['camera'])}
 for name,prefixes in [('N1',['N1-']),('near',['N2-','mixed-']),('details',['N2-']),('rest',['N2-04-B04','N2-life-','N2-rest-']),('S1',['S1-']),('005',['mixed-'])]:
  ex=[]
  for b in blocks:
   if not any(b['persistentId'].startswith(k) for k in prefixes):continue
   a=byinst[b['assetId']];x,y=project(b['anchorMap']);x=(x-META['editorOrigin'][0])/16;y=(y-META['editorOrigin'][1])/16;w,h=a['worldSizeUnits'];u,v=a['anchorUV'];ex.extend([[x-u*w,y-v*h],[x+(1-u)*w,y+(1-v)*h]])
  if name in ['S1','rest']:
   for surf in surfaces:
    if (name=='S1' and surf['id'].startswith('S1-')) or (name=='rest' and (surf['id'].startswith('N2-04-B04-walk') or surf['id'].startswith('N2-public-rest'))):
     for q in surf['polygonMap']:
      px=project(q);ex.append([(px[k]-META['editorOrigin'][k])/16 for k in (0,1)])
  if not ex:continue
  ll=[min(q[k]for q in ex)for k in (0,1)];hh=[max(q[k]for q in ex)for k in (0,1)];ff=unproject([META['editorOrigin'][k]+8*(ll[k]+hh[k])for k in (0,1)]);layout['cameraViews'][name]={'focusMap':ff,'fitWidthUnits':max(20,(hh[0]-ll[0])*1.16),'fitHeightUnits':max(18,(hh[1]-ll[1])*1.25),'screenOffset':[0,0]}
 if 'rider' in plan:layout['rider']=plan['rider']
 from suburb_regions import add_regions
 add_regions(sys.modules[__name__],layout,plan,blocks,surfaces,byinst)
 from b07_region import add_region as add_b07_region
 add_b07_region(sys.modules[__name__],layout,blocks,surfaces,byinst)
 from north_region import add_region as add_north_region
 add_north_region(sys.modules[__name__],layout,blocks,surfaces,byinst)
 from round2_region import add_regions as add_round2_regions
 add_round2_regions(sys.modules[__name__],layout,blocks,surfaces,byinst)
 from round3_region import add_regions as add_round3_regions
 add_round3_regions(sys.modules[__name__],layout,blocks,surfaces,byinst)
 from central_life import apply as apply_central_life
 apply_central_life(sys.modules[__name__],layout,blocks,surfaces,byinst,report)
 from round4_region import add_regions as add_round4_regions
 add_round4_regions(sys.modules[__name__],layout,blocks,surfaces,byinst,report)
 from native_comparison_region import apply as apply_native_comparison
 apply_native_comparison(sys.modules[__name__],layout,blocks,surfaces,byinst,report)
 from round5_region import add_regions as add_round5_regions
 add_round5_regions(sys.modules[__name__],layout,blocks,surfaces,byinst,report)
 from market_life import apply as apply_market_life
 apply_market_life(sys.modules[__name__],layout,blocks,surfaces,byinst,report)
 from compound_region import apply as apply_compound
 apply_compound(sys.modules[__name__],layout,blocks,surfaces,byinst,report)
 assert layout['rider']['forwardAssetId']=='HC-R-NE' and layout['rider']['reverseAssetId']=='HC-R-SW','Only original D rider authorized'
 if not V.exists():
  shutil.copytree(lib.OLD/'viewer',V,ignore=shutil.ignore_patterns('*.png','scene-layout.json','asset-manifest.json'))
  html=V/'index.html';html.write_text(html.read_text().replace('五楼混合街段','006邻区街段'))
 patch_shell()
 from suburb_regions import patch as patch_regions
 patch_regions(sys.modules[__name__])
 from b07_region import patch as patch_b07
 patch_b07(sys.modules[__name__])
 from north_region import patch as patch_north
 patch_north(sys.modules[__name__])
 from round2_region import patch as patch_round2
 patch_round2(sys.modules[__name__])
 from round3_region import patch as patch_round3
 patch_round3(sys.modules[__name__])
 from central_life import patch as patch_central_life
 patch_central_life(sys.modules[__name__])
 from round4_region import patch as patch_round4
 patch_round4(sys.modules[__name__])
 from native_comparison_region import patch as patch_native_comparison
 patch_native_comparison(sys.modules[__name__])
 from round5_region import patch as patch_round5
 patch_round5(sys.modules[__name__])
 from market_life import patch as patch_market_life
 patch_market_life(sys.modules[__name__])
 from compound_region import patch as patch_compound
 patch_compound(sys.modules[__name__])
 files={a['file'] for a in assets}
 for p in (V/'assets').glob('*.png'):
  if p.name not in files:p.unlink()
 for f in files:shutil.copyfile(lib.A/f,V/'assets'/f)
 write(V/'assets/scene-layout.json',layout);write(V/'assets/asset-manifest.json',{'schemaVersion':1,'projection':plan['projection'],'assets':assets});assert layout['roads']==plan['roads'] and layout['projection']==plan['projection'];write(I/'export-report.json',{'status':'exported-not-yet-opened','objects':report,'groundSurfaces':len(surfaces),'uniquePNG':len(files),'PNGBytes':sum((V/'assets'/f).stat().st_size for f in files),'roadsProjectionPreserved':True,'tiledSHA256':sha(M),'gameTestsRun':False});print('Exported derived viewer:',len(blocks),'static instances')
def patch_shell():
 f=V/'assets/main/index.probe41.js';s=f.read_text()
 marker='f.camera=f.cameraViews[new URLSearchParams(location.search).get("view")||"near"]||f.camera,'
 if marker not in s:s=s.replace('this.initialZoom=null!=',marker+'this.initialZoom=null!=')
 s=s.replace('*(new URLSearchParams(location.search).get("view")==="close"?1.5:1)','');f.write_text(s)
 f=V/'index.html';s=f.read_text().replace('S1＋停车','S1南段');old='<a href="?view=overall">总体</a> · <a href="?view=close">近景</a>';new='<a href="?view=overall">总体</a> · <a href="?view=N1">N1住宅</a> · <a href="?view=near">N2＋005近景</a> · <a href="?view=S1">S1南段</a> · <a href="?view=005">005原样板</a> · <a href="?view=details">公共细节</a> · <a href="?view=rest">休憩近景</a>';f.write_text(s.replace(old,new))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['init','export','validate']);p.add_argument('--plan',type=Path);p.add_argument('--approved-plan-sha');a=p.parse_args()
 if a.command=='init':
  if not a.plan:p.error('--plan required; no default pending plan')
  initialize(a.plan,a.approved_plan_sha)
 elif a.command=='export':export()
 else:lib.validate()
