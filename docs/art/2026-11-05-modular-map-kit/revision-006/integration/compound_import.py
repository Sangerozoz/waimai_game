#!/usr/bin/env python3
"""Restricted source125 scene consumer: preflight, explicit negative probes, transactional apply.

This is a static map-input importer, not a game test runner or bulk scene producer.
"""
import sys
sys.dont_write_bytecode=True
import argparse,copy,json,math,os,shutil
from pathlib import Path
import neighborhood_export as e
import geometry_009 as g
PIPE=e.R.parent/'revision-009/pipeline';sys.path.insert(0,str(PIPE))
from compound_contract import validate_candidate,source_accounting,require,SCENE,PARENT_SHA
from batch_prepare import Context

I=e.I;B=I/'compound-pilot';MARKER=I/'compound-pilot-increment.json'
P=e.R.parent/'revision-009/planning/compound-pilot/scene-compound-pilot.json'
REVIEW=e.R.parent/'revision-009/review/compound-pilot-review/review.json'
BASE_SHA='e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7'
TMJ_SHA='5a4ee4e32ca61f88c81d97161469fa558fdfa75d1f8051ffaeef7c03badfee5c'

def reservations():
 return {i for r in e.read(e.R.parent/'revision-009/planning/fit-round-4/usage-contracts.json')['reservations']for i in r['sourceIndices']}

def validate(plan,ctx):
 return validate_candidate(plan,ctx.scene,e.read(ctx.city_path),e.sha(ctx.city_path),reservations())

def bbox(poly):return[min(q[0]for q in poly),min(q[1]for q in poly),max(q[0]for q in poly),max(q[1]for q in poly)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def indexed(rows):return[(id,poly,bbox(poly))for id,poly in rows]
def nearest(poly,idx):
 bb=bbox(poly);best=float('inf');item=None
 for lower,id,q in sorted((boxgap(bb,box),id,q)for id,q,box in idx):
  if lower>best:break
  distance=g.gap(poly,q)
  if distance<best:best,item=distance,id
 return {'gap':best,'id':item}

def geometry(plan,ctx):
 city=e.read(ctx.city_path);context=e.read(e.R/'planning/source-context.json');water=[x['points']for x in context['waterAreas']]
 old=e.read(I/'batch-009-r5/actual-old-shape-evidence.json')+[{'id':b['persistentId'],'polygon':b['footprintPolygonMap']}for b in e.read(I/'batch-009-r5/009r5-derived-plan.json')['buildings']]+[{'id':f['persistentId'],'polygon':f['groundContactPolygonMap']}for f in e.read(I/'market-life/market-layout.json')['newFixtures']]
 require(len(old)==161 and {x['id']for x in old}==set(ctx.objects),'Actual161 contact evidence differs from current published IDs')
 sources=indexed((i,p)for i,p in enumerate(city['buildings'])if i!=125);oldidx=indexed((x['id'],x['polygon'])for x in old);grounds=indexed((id,x['polygonMap'])for id,x in ctx.ground.items());waters=indexed(enumerate(water));lines=indexed(enumerate(line for line in city['waterways']if len(line)>1))
 roads=[dict(r,points=[ctx.nodes[id]for id in r['nodes']])for r in city['roads']];rb=[bbox(r['points'])for r in roads];zone=e.read(e.R.parent.parent/'2026-11-02-county-zoning/selection.json')['regions']['city']['worldPolygonMetresApprox'];market=[x for x in old if x['id'].startswith('market-life-')]
 results=[]
 for item,kind,poly in [(m,'body',m['footprintPolygonMap'])for m in plan['buildings']]+[(s,'ground',s['polygonMap'])for s in plan['groundSurfaces']]:
  id=item.get('persistentId',item.get('id'));bb=bbox(poly);rg={'gap':float('inf'),'id':None};wg={'gap':float('inf'),'id':None}
  for lower,j in sorted((max(0,boxgap(bb,box)-roads[j]['width']/2),j)for j,box in enumerate(rb)):
   if lower>max(0,rg['gap']):break
   distance=g.line_gap(poly,roads[j]['points'])-roads[j]['width']/2
   if distance<rg['gap']:rg={'gap':distance,'id':roads[j]['id']}
  for lower,j,line in sorted((max(0,boxgap(bb,box)-3),j,line)for j,line,box in lines):
   if lower>max(0,wg['gap']):break
   distance=g.line_gap(poly,line)-3
   if distance<wg['gap']:wg={'gap':distance,'id':j}
  proof={'id':id,'kind':kind,'otherSource':nearest(poly,sources),'old161Contact':nearest(poly,oldidx),'old501Ground':nearest(poly,grounds),'waterPolygon':nearest(poly,waters),'waterwayMinus3m':wg,'carriageway':rg,'blue':all(g.inside(q,zone)for q in poly),'marketFiveContacts':[{'id':x['id'],'gap':g.gap(poly,x['polygon'])}for x in market]}
  proof['POIGap'],proof['POINode']=min((0 if g.inside(ctx.nodes[p['node']],poly)else min(g.point_segment(ctx.nodes[p['node']],a,b)for a,b in g.edges(poly)),p['node'])for p in city['pois'])
  require(proof['blue'],'Outside blue: '+id)
  for name,minimum in [('otherSource',2 if kind=='body'else .15),('old161Contact',1 if kind=='body'else .15),('old501Ground',1 if kind=='body'else .15),('waterPolygon',5),('waterwayMinus3m',5),('carriageway',2 if kind=='body'else-1e-7)]:require(proof[name]['gap']>=minimum,'Compound entire scene rejected: '+id+' '+name+' '+str(proof[name]))
  require(proof['POIGap']>0,'Original POI covered')
  proof['sameSceneBodyChecks']=[]
  for module in plan['buildings']:
   mid=module['persistentId'];foot=module['footprintPolygonMap']
   if kind=='body'and mid==id:continue
   if kind=='ground'and item.get('thresholdOf')==mid:
    a,b=module['visualApproach']['centrelineMap'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);direction=[dx/length,dy/length]
    require(module['visualApproach']['initialManualThresholdAllowanceMetres']==.6,'Threshold exception changed')
    beyond=g.clip_half(poly,[-v for v in direction],-sum(a[k]*direction[k]for k in(0,1))-.6)
    require(len(beyond)>=3 and g.gap(beyond,foot)>=.05,'Own threshold penetrates beyond permitted first0.6m')
    proof['sameSceneBodyChecks'].append({'moduleId':mid,'ownThresholdFirstMetres':.6,'beyond0_6mGap':g.gap(beyond,foot),'fullPolygonGap':g.gap(poly,foot)})
   else:
    distance=g.gap(poly,foot);require(distance>=(2 if kind=='body'else .15),'Same-source modules/ground collide; no same-source body exemption')
    proof['sameSceneBodyChecks'].append({'moduleId':mid,'gap':distance})
  results.append(proof)
 paving=[s for s in plan['groundSurfaces']if s['materialId']=='S01-paving'];seen={paving[0]['id']}
 while True:
  more={s['id']for s in paving if any(g.gap(s['polygonMap'],z['polygonMap'])<=1e-7 for z in paving if z['id']in seen)}
  if more<=seen:break
  seen|=more
 require(len(seen)==4,'Four paving faces not connected')
 garden=next(s for s in plan['groundSurfaces']if s['surfaceClass']=='garden');shared=next(s for s in paving if s['surfaceClass']=='shared-court');require(g.gap(garden['polygonMap'],shared['polygonMap'])==0,'Garden does not adjoin shared court')
 for s in paving:
  if s['surfaceClass']in ['door-walk','shared-walk']:require(g.gap(garden['polygonMap'],s['polygonMap'])>.05,'Soil bed covers pedestrian route')
 return {'globalAndSameSceneChecks':results,'pavingConnectedComponents':1,'gardenDoesNotCoverDoorWalks':True,'actualOldContactCount':len(old),'fullOriginalWaterwayCount':len(city['waterways']),'allOriginalRoadsChecked':len(roads),'oldContacts':old}

def preflight(plan=None):
 require(not MARKER.exists(),'Duplicate apply refused: pilot increment already exists')
 require(e.sha(P)==PARENT_SHA,'Approved original candidate SHA changed')
 review=e.read(REVIEW);require(review['verdict']=='safe-for-limited-integration'and review['reviewedCandidateSHA256']==PARENT_SHA,'Independent review target/verdict mismatch')
 require(review['baselineSceneSHA256']==BASE_SHA and review['baselineTiledSHA256']==TMJ_SHA,'Independent review baseline differs')
 require(e.sha(e.V/'assets/scene-layout.json')==BASE_SHA and e.sha(e.M)==TMJ_SHA,'Latest actual baseline advanced; must recheck before applying, never replay a snapshot')
 ctx=Context();candidate=e.read(P)if plan is None else copy.deepcopy(plan);ownership=validate(candidate,ctx)
 require(ownership['baselineCounts']['uniqueSourceCount']==81 and len(ctx.scene['blocks'])==161 and len(ctx.scene['groundSurfaces'])==501,'Actual baseline counts differ')
 require(e.read(P.parent/'import-contract.json')['planSHA256']==PARENT_SHA,'Producer contract SHA differs')
 latest=e.read(P.parent/'latest161-recheck.json');require(latest['frozenPlanSHA256']==PARENT_SHA and latest['completedBaseline']['publishedSceneSHA256']==BASE_SHA,'Latest161 producer recheck target differs')
 normalized=[];native=[];derived=copy.deepcopy(candidate)
 for b in derived['buildings']:
  o=ctx.normalize_object(b,SCENE);require(o['baselineStatus']=='new','Module already present');cal=ctx.cal[b['libraryAssetId']];ppu=cal.get('nativePixelsPerUnit',cal.get('sourceNativePPU'));ap=cal.get('anchorPixel',cal.get('originalAnchorPixel'));pixels=[[198,910],[438,1229],[1055,931],[815,612]]if b['libraryAssetId']=='B01'else cal['groundCornersPixelLeftFrontRightRear']
  q=e.project(b['anchorMap']);foot=[e.unproject([q[k]+16*b['uniformScale']*(p[k]-ap[k])/ppu for k in(0,1)])for p in pixels]
  require(len(foot)==len(b['footprintPolygonMap'])and max(math.dist(x,y)for x,y in zip(foot,b['footprintPolygonMap']))<1e-8,'Actual hand footline differs from approved candidate')
  a=ctx.assets[b['libraryAssetId']];raw=Path(a['runtimeDerivation']['source']);require(raw.is_file(),'Native missing')
  if b['libraryAssetId']=='B01':prov=e.lib.OLD/'integration/provenance-check.json';tool=Path(next(x['source']for x in e.read(prov)if x['id']=='B01'))
  else:prov=raw.parent/'provenance.json';pv=e.read(prov);tool=Path(pv.get('toolSourceAbsolutePath',pv.get('original_tool_output_absolute_path','')))
  require(e.sha(raw)==e.sha(tool)==a['runtimeDerivation']['sourceSHA256'],'Tool/native SHA differ')
  b['sourceNativeSHA256']=e.sha(raw);b['nativeFootlineEvidence']={'nativePixels':pixels,'nativePPU':ppu,'nativeAnchorPixel':ap,'scaleOnce':b['uniformScale'],'uncertaintyPixels':25,'hiddenRearInferred':True,'definition':'B01 retained producer four manual base estimates; not the entire billboard and not surveyed corners'if b['libraryAssetId']=='B01'else'B05 retained calibration visible base controls plus inferred rear','originalCalibrationPath':str(ctx.calibration_path),'footprintMapConverted':foot}
  native.append({'persistentId':b['persistentId'],'assetId':b['libraryAssetId'],'nativePath':str(raw),'toolPath':str(tool),'provenancePath':str(prov),'sourceNativeSHA256':e.sha(raw),'runtimeFile':a['file'],'runtimeSHA256':a['sha256'],'worldSizeUnits':b['worldSizeUnits'],'anchorUV':b['anchorUV'],'nodeScale':1,'entryCheck':o['doorCoordinateCheck'],'footlineEvidence':b['nativeFootlineEvidence']});normalized.append(o)
 e.verify_roads(candidate)
 for r in candidate['roads']:ctx.verify_road(r)
 geom=geometry(candidate,ctx)
 derived['consumerDerivation']={'approvedOriginalPath':str(P.resolve()),'approvedOriginalSHA256':PARENT_SHA,'reviewedCandidateSHA256':review['reviewedCandidateSHA256'],'reviewPath':str(REVIEW.resolve()),'actualBaselineSceneSHA256':BASE_SHA,'actualBaselineTiledSHA256':TMJ_SHA,'actualBaselineCounts':[161,501,81],'rules':['one exact scene/source125/two modules/five surfaces only','resolved world frames, nodeScale1, existing PPU/UV fixed','source count is owner-scene union, no old records migrated','same-scene peer checks retained; own first0.6m threshold only','atomic whole-scene append, no old edit'],'displayedYet':False}
 return ctx,derived,ownership,normalized,native,geom

def write_preflight(result):
 ctx,derived,ownership,normalized,native,geom=result;B.mkdir(exist_ok=True)
 for src,name in [(ctx.scene_path,'pre-compound-scene.json'),(ctx.map_path,'pre-compound-neighborhood.tmj'),(e.V/'assets/asset-manifest.json','pre-compound-asset-manifest.json')]:
  dst=B/name
  if not dst.exists():shutil.copyfile(src,dst)
  require(e.sha(src)==e.sha(dst),'Saved actual baseline differs; never overwrite')
 protected=e.read(I/'market-life/read-only-protection.json')
 for directory in [P.parent,REVIEW.parent]:
  for f in directory.iterdir():
   if f.is_file():protected[str(f.resolve())]=e.sha(f)
 for f in [e.R.parent/'revision-009/scenic-scene-contract.md',PIPE/'schema.json',I/'asset-library.json',I/'asset-calibration.json']:
  protected[str(f.resolve())]=e.sha(f)
 for row in native:
  for key in ['nativePath','toolPath','provenancePath']:protected[str(Path(row[key]).resolve())]=e.sha(row[key])
 for name,data in [('derived-compound-plan.json',derived),('ownership-preflight.json',ownership),('normalized-modules.json',normalized),('native-foot-door-scale-check.json',native),('geometry-preflight.json',geom),('read-only-protection.json',protected)]:e.write(B/name,data)

def negative_probes():
 require(not MARKER.exists(),'Negative probes require the real pre-apply baseline; do not relabel duplicate-apply failures as schema evidence')
 preflight()
 original=e.read(P);ctx=Context();snapshot={str(f):e.sha(f)for f in [e.M,e.V/'assets/scene-layout.json',e.V/'assets/asset-manifest.json']};cases=[]
 def run(name,edit):
  bad=copy.deepcopy(original);edit(bad)
  try:preflight(bad)
  except (ValueError,AssertionError,KeyError)as exc:cases.append({'case':name,'explicitInMemoryNegativeInput':True,'rejected':True,'reason':str(exc),'mainSHAUnchanged':all(e.sha(f)==h for f,h in snapshot.items())})
  else:raise ValueError('Consumer accepted a forbidden negative: '+name)
 run('duplicate-module-persistentId',lambda p:p['buildings'][1].update(persistentId=p['buildings'][0]['persistentId']))
 run('duplicate-ground-id',lambda p:p['groundSurfaces'][1].update(id=p['groundSurfaces'][0]['id']))
 run('missing-module-sceneId',lambda p:p['buildings'][0].pop('sceneId'))
 run('missing-scene',lambda p:p.update(scenes=[]))
 run('scene-omits-existing-module-orphan',lambda p:p['scenes'][0]['moduleIds'].pop())
 run('scene-lists-absent-module',lambda p:p['scenes'][0]['moduleIds'].append('explicit-negative-absent-module'))
 def cross(p):s=copy.deepcopy(p['scenes'][0]);s['sceneId']='explicit-negative-second-scene';p['scenes'].append(s)
 run('cross-scene-source-reuse',cross)
 def bind(p,index):
  s=p['scenes'][0];s['sourceIndices']=[index];s['sourcePolygonsMap']=[e.read(ctx.city_path)['buildings'][index]]
 run('old-array-bound-source-conflict',lambda p:bind(p,260))
 run('old-singular-bound-source-conflict',lambda p:bind(p,630))
 run('reserved-source-conflict',lambda p:bind(p,1731))
 # 1731 is both already used and historically reserved.114 is also bound. Exercise
 # independent reservation gate using the same consumer validator with a frozen
 # temporary baseline whose unrelated bindings are removed only in memory.
 temp=copy.deepcopy(ctx.scene);temp['visualReplacements']=[];bad=copy.deepcopy(original);bind(bad,114)
 try:validate_candidate(bad,temp,e.read(ctx.city_path),e.sha(ctx.city_path),reservations())
 except ValueError as exc:cases.append({'case':'reservation-gate-independent-of-old-binding','explicitInMemoryNegativeInput':True,'rejected':True,'reason':str(exc),'mainSHAUnchanged':all(e.sha(f)==h for f,h in snapshot.items())})
 else:raise ValueError('Reserved source accepted')
 run('unsupported-schema',lambda p:p.update(schemaVersion='explicit-negative-unknown'))
 require(all(x['mainSHAUnchanged']for x in cases),'Negative input mutated main map')
 B.mkdir(exist_ok=True);e.write(B/'consumer-negative-preflight.json',{'consumerEntry':str(Path(__file__).resolve()),'samePreflightUsedByApply':True,'notGameTests':True,'cases':cases,'mainHashesBeforeAndAfter':snapshot,'productionInputsEdited':False})
 return cases

def append_doc(ctx,plan):
 doc=copy.deepcopy(ctx.map);lid=doc['nextlayerid'];oid=doc['nextobjectid'];ts=doc['tilesets'][0];objects=[];grounds=[]
 priority={'shared-court':0,'garden':1,'shared-walk':2,'door-walk':3}
 for surface in sorted(plan['groundSurfaces'],key=lambda s:priority[s['surfaceClass']]):
  pts=[e.project(q)for q in surface['polygonMap']];x,y=pts[0];prop={'surfaceAssetId':surface['materialId'],'sceneId':surface['sceneId'],'owner':surface['owner'],'moduleIdsJSON':json.dumps(surface['moduleIds']),'purpose':surface['purpose'],'surfaceClass':surface['surfaceClass'],'thresholdOf':surface.get('thresholdOf','')}
  grounds.append({'id':oid,'name':surface['id'],'type':'ground-surface','x':x,'y':y,'visible':True,'polygon':[{'x':a-x,'y':b-y}for a,b in pts],'properties':e.properties(prop)});oid+=1
 for b in plan['buildings']:
  a=ctx.assets[b['libraryAssetId']];tile=next(t for t in ts['tiles']if e.props(t)['assetId']==a['id']);x,y=e.project(b['anchorMap']);w,h=[v*16 for v in b['worldSizeUnits']];u,v=b['anchorUV']
  prop={'persistentId':b['persistentId'],'assetId':b['libraryAssetId'],'sceneId':b['sceneId'],'sourceIndicesJSON':json.dumps(b['sourceIndices']),'visualReplacementOfJSON':json.dumps(b['visualReplacementOf']),'sourceNativeSHA256':b['sourceNativeSHA256'],'uniformScaleProvenance':b['uniformScale'],'resolvedNodeScale':1,'nativeFootlineEvidenceJSON':json.dumps(b['nativeFootlineEvidence']),'entryPixelJSON':json.dumps(b['entryPixel'])}
  objects.append({'id':oid,'name':b['persistentId'],'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties(prop)});oid+=1
 objects.sort(key=lambda o:o['y']-(1-ctx.assets[e.props(o)['assetId']]['anchorUV'][1])*o['height'])
 doc['layers'].append({'id':lid,'type':'group','name':SCENE+' — one source, two modules, shared court','offsetx':0,'offsety':0,'visible':True,'layers':[{'id':lid+1,'type':'objectgroup','name':'five scene-owned grounds: base then soil then actual door walks','draworder':'index','objects':grounds},{'id':lid+2,'type':'objectgroup','name':'two independently editable native modules','draworder':'index','objects':objects}]});doc['nextlayerid']=lid+3;doc['nextobjectid']=oid
 require(doc['layers'][:-1]==ctx.map['layers']and doc['tilesets']==ctx.map['tilesets'],'Appending pilot altered existing Tiled data')
 return doc

def atomic_bytes(path,data):
 path=Path(path);tmp=path.with_name(path.name+'.compound-writing');tmp.write_bytes(data);os.replace(tmp,path)

def recover():
 journal=B/'transaction-journal.json'
 if not journal.exists():return
 data=e.read(journal)
 if data['status']in ['committed','rolled-back']:return
 for row in reversed(data['publishTargets']):
  target=Path(row['target'])
  if row['beforeExists']:atomic_bytes(target,Path(row['backup']).read_bytes())
  elif target.exists():target.unlink()
 data['status']='rolled-back';e.write(journal,data)

def apply():
 require(not MARKER.exists(),'Duplicate apply refused: pilot increment already exists')
 journal=B/'transaction-journal.json'
 if journal.exists():require(e.read(journal)['status']in ['rolled-back'],'Unfinished transaction: run recover, never initialize/reset')
 result=preflight();write_preflight(result);ctx,plan,ownership,normalized,native,geom=result
 stage=B/'transaction-stage';require(not stage.exists(),'Existing transaction staging evidence: review/recover rather than overwrite')
 stage.mkdir();doc=append_doc(ctx,plan);e.write(stage/'candidate.tmj',doc)
 inc={'parentPath':str(P.resolve()),'parentOriginalSHA256':PARENT_SHA,'derivedPath':str((B/'derived-compound-plan.json').resolve()),'derivedSHA256':e.sha(B/'derived-compound-plan.json'),'preScenePath':str((B/'pre-compound-scene.json').resolve()),'preSceneSHA256':BASE_SHA,'preTiledSHA256':TMJ_SHA,'actualBaselineCounts':[161,501,81],'sceneId':SCENE,'moduleIds':[m['persistentId']for m in plan['buildings']],'sourceIndices':[125],'groundIds':[s['id']for s in plan['groundSurfaces']],'status':'atomic-scene-appended-pending-real-Cocos','newBusinessPOIs':0,'newNavigationEdges':0}
 # Temporary export of the same tiny runtime shell is transaction staging, never a
 # new project/server. The live viewer and Tiled remain untouched until all checks.
 shutil.copytree(e.V,stage/'viewer');oldM,oldV,oldwrite=e.M,e.V,e.write
 def stagewrite(path,data):
  if Path(path)==I/'export-report.json':return oldwrite(stage/'export-report.json',data)
  return oldwrite(path,data)
 try:
  e.M=stage/'candidate.tmj';e.V=stage/'viewer';e.write=stagewrite;e._compound_pending=inc;e.export()
 finally:
  e.M=oldM;e.V=oldV;e.write=oldwrite;e._compound_pending=None
 target=e.read(stage/'viewer/assets/scene-layout.json');require(target['blocks'][:161]==ctx.scene['blocks']and target['groundSurfaces'][:501]==ctx.scene['groundSurfaces'],'Staged export damaged actual161/501')
 require(len(target['blocks'])==163 and len(target['groundSurfaces'])==506,'Atomic scene is incomplete')
 counts=source_accounting(target);require((counts['uniqueSourceCount'],counts['sourceOwningSceneCount'],counts['sourceBoundModuleCount'])==(82,82,83),'Source union/scene/module accounting incorrect')
 for key,value in ctx.scene['cameraViews'].items():require(target['cameraViews'][key]==value,'Old camera changed in stage')
 require(e.sha(e.M)==TMJ_SHA and e.sha(ctx.scene_path)==BASE_SHA,'Live baseline changed before commit')
 for path,h in e.read(B/'read-only-protection.json').items():require(e.sha(path)==h,'Read-only protected file changed before commit')
 e.write(stage/'increment.json',inc)
 promotions=[(stage/'candidate.tmj',e.M),(stage/'viewer/assets/scene-layout.json',e.V/'assets/scene-layout.json'),(stage/'viewer/assets/asset-manifest.json',e.V/'assets/asset-manifest.json'),(stage/'viewer/index.html',e.V/'index.html'),(stage/'export-report.json',I/'export-report.json'),(stage/'increment.json',MARKER)]
 require(e.sha(stage/'viewer/assets/main/index.probe41.js')==e.sha(e.V/'assets/main/index.probe41.js'),'Pilot must not rewrite renderer')
 backup=B/'transaction-backups';backup.mkdir();entries=[]
 for j,(source,targetpath)in enumerate(promotions):
  exists=targetpath.exists();back=backup/(str(j)+'.before')
  if exists:back.write_bytes(targetpath.read_bytes())
  entries.append({'source':str(source.resolve()),'target':str(targetpath.resolve()),'beforeExists':exists,'backup':str(back.resolve()),'beforeSHA256':e.sha(targetpath)if exists else None,'afterSHA256':e.sha(source)})
 tx={'status':'prepared','scope':SCENE,'publishTargets':entries,'allModulesAndGroundsValidatedBeforeCommit':True};e.write(journal,tx)
 try:
  tx['status']='publishing';e.write(journal,tx)
  for row in entries:atomic_bytes(row['target'],Path(row['source']).read_bytes())
  require(all(e.sha(row['target'])==row['afterSHA256']for row in entries),'Commit byte check failed')
  tx['status']='committed';e.write(journal,tx)
 except BaseException:
  recover();raise
 e.write(B/'staged-export-accounting.json',counts);print('COMMITTED whole scene: +1 source/+1 scene/+2 modules/+5 surfaces; actual163/506/82')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['preflight','negative-probes','apply','recover']);args=parser.parse_args()
 if args.command=='preflight':write_preflight(preflight());print('PREFLIGHT:1 source/1 scene/2 modules/5 surfaces on actual161/501/81')
 elif args.command=='negative-probes':print('CONSUMER NEGATIVES',len(negative_probes()),'rejected; live hashes unchanged')
 elif args.command=='recover':recover();print('Recovery checked')
 else:apply()
