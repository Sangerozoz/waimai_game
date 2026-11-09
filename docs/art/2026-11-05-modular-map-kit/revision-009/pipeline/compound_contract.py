"""Executable ownership checks for the single reviewed source125 compound pilot.

Legacy records are normalized into temporary ownership views only. Nothing here writes
old scene/binding data, changes their schema, or grants bulk compound admission.
"""
import copy

SCENE='009compound-source0125-court'
SCHEMA='scene-compound-static-v1'
PARENT_SHA='a5564388f2efb4afc55c8baa50e0f0607b1d0484ded6c2b05b6cc9abda6edb27'

def require(ok,message):
 if not ok:raise ValueError(message)

def binding_view(record):
 b=record.get('visualReplacementOf',record)
 if 'sourceIndices'in b:indices=b['sourceIndices'];polygons=b.get('sourcePolygonsMap')
 elif 'sourceIndex'in b:indices=[b['sourceIndex']];polygons=[b.get('sourcePolygonMap',b.get('sourcePolygon'))]
 else:raise ValueError('Missing real source index binding')
 require(isinstance(indices,list)and indices and all(type(i)is int and i>=0 for i in indices)and len(indices)==len(set(indices)),'Invalid unique sourceIndices')
 require(isinstance(polygons,list)and len(polygons)==len(indices)and all(isinstance(p,list)and len(p)>=3 for p in polygons),'Missing source polygon binding')
 return copy.deepcopy(indices),copy.deepcopy(polygons),b.get('sourceSHA256',b.get('sourceCitySHA256'))

def source_accounting(layout):
 records=layout.get('visualReplacements',[]);registry={}
 for scene in layout.get('compoundScenes',[]):
  sid=scene['sceneId'];require(sid not in registry,'Duplicate published compound sceneId');registry[sid]=scene
 owners={};groups={};ids=set()
 for r in records:
  pid=r['persistentId'];require(pid not in ids,'Duplicate source-bound module persistentId');ids.add(pid)
  indices,polys,sha=binding_view(r);sid=r.get('sceneId')
  if sid:
   require(sid in registry,'Published compound module has no scene registry')
   scene=registry[sid];require(pid in scene['moduleIds'],'Published compound orphan module')
   require(indices==scene['sourceIndices']and polys==scene['sourcePolygonsMap'],'Published compound source ownership mismatch')
   owner='scene:'+sid
  else:owner='legacy:'+pid
  groups.setdefault(owner,set()).add(pid)
  for i in indices:
   require(i not in owners or owners[i]==owner,'Source reused across published scene owners: '+str(i));owners[i]=owner
 for sid,s in registry.items():require(groups.get('scene:'+sid)==set(s['moduleIds']),'Published scene missing a listed module')
 return {'uniqueSourceCount':len(owners),'sourceIndices':sorted(owners),'sourceOwningSceneCount':len(groups),'sourceBoundModuleCount':len(ids),'ownershipBySource':{str(i):o for i,o in sorted(owners.items())},'scope':'source carriers/scenic owners/modules, never business addresses'}

def validate_candidate(plan,baseline,city,city_sha,reserved_sources):
 require(plan.get('schemaVersion')==SCHEMA,'Unsupported compound schema')
 require(plan.get('projection')==baseline['projection'],'Compound projection changed')
 scenes=plan.get('scenes');modules=plan.get('buildings');grounds=plan.get('groundSurfaces')
 require(isinstance(scenes,list)and scenes,'Missing scene registry')
 require(isinstance(modules,list)and modules,'Missing modules')
 require(isinstance(grounds,list)and grounds,'Missing groundSurfaces')
 old=source_accounting(baseline);oldids={b['persistentId']for b in baseline['blocks']}|{g['id']for g in baseline['groundSurfaces']}
 registry={};sourceowners={};ids=set();modulemap={};groundmap={}
 for s in scenes:
  sid=s.get('sceneId');require(isinstance(sid,str)and sid and sid not in registry,'Duplicate/missing sceneId');registry[sid]=s
  indices,polys,sha=binding_view(s)
  require(sha==city_sha,'Scene source SHA mismatch')
  require(all(i<len(city['buildings'])and city['buildings'][i]==poly for i,poly in zip(indices,polys)),'Scene real source polygon mismatch')
  for i in indices:
   require(i not in sourceowners or sourceowners[i]==sid,'Cross-scene source reuse: '+str(i));sourceowners[i]=sid
   require(i not in old['sourceIndices'],'Source already bound in published baseline: '+str(i))
   require(i not in reserved_sources,'Source reserved by an existing usage contract: '+str(i))
  require(isinstance(s.get('moduleIds'),list)and s['moduleIds']and len(s['moduleIds'])==len(set(s['moduleIds'])),'Scene moduleIds missing/duplicate')
  require(isinstance(s.get('groundSurfaceIds'),list)and len(s['groundSurfaceIds'])==len(set(s['groundSurfaceIds'])),'Scene groundSurfaceIds missing/duplicate')
 for m in modules:
  pid=m.get('persistentId');require(pid and pid not in ids and pid not in oldids,'Duplicate/old persistentId: '+str(pid));ids.add(pid);modulemap[pid]=m
  require(m.get('id')==pid,'Module id/persistentId differ')
  sid=m.get('sceneId');require(sid in registry,'Module missing sceneId or unknown scene')
  s=registry[sid];require(pid in s['moduleIds'],'Orphan module not listed by its scene')
  indices,polys,sha=binding_view(m);require(indices==s['sourceIndices']and polys==s['sourcePolygonsMap']and sha==city_sha,'Module source ownership differs from scene')
  require(m.get('sourceIndices')==indices,'Module direct sourceIndices differ')
  require(m['visualReplacementOf'].get('sourceDataChanged')is False,'Source mutation forbidden')
  require(m.get('nodeScale')==1 and m.get('rotation',0)==0 and not any(m.get(k,False)for k in ['mirror','mirrorPNG','flipX','flipY']),'Only resolved frame/nodeScale1 unrotated unmirrored')
 for g in grounds:
  gid=g.get('id');require(gid and gid not in ids and gid not in oldids,'Duplicate/old ground persistentId: '+str(gid));ids.add(gid);groundmap[gid]=g
  sid=g.get('sceneId');require(sid in registry and g.get('owner')==sid,'Ground missing/incorrect scene owner')
  s=registry[sid];require(gid in s['groundSurfaceIds'],'Orphan ground not listed by scene')
  require(isinstance(g.get('moduleIds'),list)and g['moduleIds']and len(g['moduleIds'])==len(set(g['moduleIds']))and set(g['moduleIds'])<=set(s['moduleIds']),'Ground orphan/duplicate module references')
  if g.get('surfaceClass')=='door-walk':require(g.get('thresholdOf')in g['moduleIds']and len(g['moduleIds'])==1,'Door threshold must name exactly its own module')
  else:require(not g.get('thresholdOf'),'Only own door surface has threshold allowance')
 for sid,s in registry.items():
  require(set(s['moduleIds'])=={id for id,m in modulemap.items()if m['sceneId']==sid},'Scene lists missing module / module omitted')
  require(set(s['groundSurfaceIds'])=={id for id,g in groundmap.items()if g['sceneId']==sid},'Scene lists missing ground / ground omitted')
  require(s.get('originalSemanticStatus')=='unknown'and s.get('newPOIs')==0 and s.get('newNavigationEdges')==0 and not s.get('oldSurfaceEdits'),'Scenic-only source unknown/no old edits required')
 counts={'uniqueSources':len(sourceowners),'scenes':len(scenes),'modules':len(modules),'grounds':len(grounds)}
 require(plan.get('sourceIndices')==sorted(sourceowners),'Root source union mismatch')
 for key,count in [('uniqueSourceCount',counts['uniqueSources']),('sceneCount',counts['scenes']),('moduleCount',counts['modules']),('groundSurfaceCount',counts['grounds'])]:require(plan.get(key)==count,'Declared count mismatch: '+key)
 require(plan.get('renderedNewCount')==0 and plan.get('userAcceptedNewCount')==0,'Input is a candidate, not displayed/accepted evidence')
 require(not plan.get('fixtures')and not plan.get('parkedVehicles')and not plan.get('parkingSpaces'),'Pilot admits no added props/vehicles/parking')
 # Structural checks above remain meaningful, but live production is deliberately
 # restricted to the one exact reviewed scene. No general multi-module producer.
 require(counts=={'uniqueSources':1,'scenes':1,'modules':2,'grounds':5}and set(sourceowners)=={125}and set(registry)=={SCENE},'Outside approved one-source pilot scope')
 require({m['libraryAssetId']:m['uniformScale']for m in modules}=={'B05':.9,'B01':1},'Pilot only B05@0.9 and B01@1')
 return {'candidateCounts':counts,'baselineCounts':old,'newSourceOwnership':sourceowners,'allModulesAndGroundsOwned':True,'oldRecordsRewritten':False}
