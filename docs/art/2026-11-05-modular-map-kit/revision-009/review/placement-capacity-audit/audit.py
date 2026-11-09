"""Read-only counts and bounded static witnesses; never imports/runs a planner module."""
import ast,json,math,hashlib,copy
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists())
K=ROOT/'docs/art/2026-11-05-modular-map-kit'; R=K/'revision-009'; F=R/'planning/fit-round-5'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,data):(HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
files=set()
for folder in [R/'baselines/visible143',F,R/'planning/fit-round-3',R/'planning/fit-round-4',K/'revision-006/integration/batch-009-r4',K/'revision-006/integration/batch-009-r5']:
 files.update(p for p in folder.rglob('*') if p.is_file())
files.update((K/'revision-006/integration').glob('*.py'))
files.update([ROOT/'delivery-game/assets/resources/map-sample/city.json',ROOT/'docs/art/2026-11-02-county-zoning/selection.json',K/'revision-003/road-constraint.json',K/'revision-006/planning/build_plan.py',K/'revision-008/calibration/footprint-review.json',R/'source-entry-semantics.md'])
seed=read(R/'planning/first-expansion-batch.json');files.add(Path(seed['source']['approvedCountyLayoutPath']))
before={str(p):sha(p) for p in files};save('input-sha-before.json',before)
d=read(F/'local-fit-progress.json');rows=d['rows'];final=set(read(F/'joint-fit-summary.json')['final']['sourceIndices'])
first=Counter();allcats=Counter();attempt=Counter();by=[]
for r in rows:
 rules=r.get('rejectedByRule',{});cats=list(dict.fromkeys(k.split(':',1)[-1] for k in rules));initial=cats[0] if cats else r.get('stage','none-recorded');first[initial]+=1
 for cat in set(cats):allcats[cat]+=1
 attempt.update({})
 for k,v in rules.items():attempt[k.split(':',1)[-1]]+=v
 by.append({'sourceIndex':r['sourceIndex'],'sourceId':f"city.buildings[{r['sourceIndex']}]",'firstRecordedRejection':initial,'allRecordedRejectionCategories':cats,'feasibleTypes':r.get('feasibleTypes',[]),'finalAdmitted':r['sourceIndex'] in final,'stage':r.get('stage','tested'),'rawRuleCounts':rules})
summary={'sources':len(rows),'intentUnknownSources':sum(r.get('stage')=='intent-unknown' for r in rows),'testedSources':sum('actualAssetScaleAttempts'in r for r in rows),'sourcesWithFeasibleTypes':sum(bool(r.get('feasibleTypes')) for r in rows),'sourcesWithoutFeasibleTypesAfterTesting':sum('actualAssetScaleAttempts'in r and not r.get('feasibleTypes') for r in rows),'finalSourcesFromThese45':len(final&{r['sourceIndex']for r in rows}),'firstRecordedRejectionSourceCounts':dict(first),'anyRecordedRejectionSourceCountsNonexclusive':dict(allcats),'ruleCounterEventsNonexclusive':dict(attempt),'assetAnchorScaleAttempts':sum(sum(r.get('actualAssetScaleAttempts',{}).values()) for r in rows),'approachAttempts':sum(sum(r.get('actualApproachAttempts',{}).values()) for r in rows),'rows':by,'countMeaning':'first is first inserted counter key, including failures before later success; not terminal cause. All is recorded observed categories, not exhaustive counterfactual causes; approach-external hides subcauses.'}
poolids={x['sourceIndex'] for x in d['newFitOptions'][:d['existingPoolOptions']]}; feasible={r['sourceIndex'] for r in rows if r.get('feasibleTypes')}
summary['existingPoolUniqueSources']=sorted(poolids);summary['trialFeasibleSourceIndices']=sorted(feasible);summary['newFeasibleSourcesBeyondOldPool']=sorted(feasible-poolids);summary['trialSourcesOutsideOldPool']=len({r['sourceIndex']for r in rows}-poolids)
summary['unsuccessfulSourcesFirstRecordedCounts']=dict(Counter(r['firstRecordedRejection'] for r in by if not r['feasibleTypes']))
summary['unsuccessfulSourcesAnyCategoryCountsNonexclusive']=dict(Counter(cat for r in by if not r['feasibleTypes'] for cat in set(r['allRecordedRejectionCategories'])))
for item in by:item['landUseIntent']=next(r for r in rows if r['sourceIndex']==item['sourceIndex']).get('sourceLandUseIntent')
save('classification.json',summary)
# Only pure function AST definitions extracted; never import planner module, execute top-level setup, or execute its search loop.
g={'math':math}
fnnames={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds','zone'}
t=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in fnnames],type_ignores=[]),'<review-pure-geometry>','exec'),g)
g['c']=read(ROOT/'delivery-game/assets/resources/map-sample/city.json');g['z']=read(ROOT/'docs/art/2026-11-02-county-zoning/selection.json');geo=read(K/'revision-003/road-constraint.json');g.update(P=geo['projection'],u=geo['streetTangentMap']);g['n']=[-g['u'][1],g['u'][0]]
B=R/'baselines/visible143';scene=read(B/'scene-layout.json');g['cal']={x['id']:x for x in read(B/'asset-calibration.json')['assets']};g['b07']=next(x for x in read(K/'revision-008/calibration/footprint-review.json')['assets'] if x['id']=='B07')
t=ast.parse((F/'plan_fifth.py').read_text());names={'bbox','boxgap','centre','pixelmap','footprint','strip','foot','audit','good'};exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<review-fifth-pure-functions>','exec'),g)
c=g['c'];nodes={x['id']:[x['x'],x['y']]for x in c['nodes']};bbox=g['bbox'];pp=g['pp'];pl=g['pl'];add=g['add'];mul=g['mul'];u=g['u'];n=g['n'];centre=g['centre'];footprint=g['footprint'];strip=g['strip'];foot=g['foot'];pixelmap=g['pixelmap'];good=g['good'];audit=g['audit']
g['bs']=[(i,p,bbox(p)) for i,p in enumerate(c['buildings'])];g['segments']=[(r,j,nodes[a],nodes[b],bbox([nodes[a],nodes[b]]))for r in c['roads']for j,(a,b)in enumerate(zip(r['nodes'],r['nodes'][1:]))];g['ww']=[a['points']for a in c['areas']if a.get('kind')=='water'and len(a.get('points',[]))>=3];g['wl']=[(a,b)for w in c['waterways']for a,b in zip(w,w[1:])]
assets={x['id']:x for x in read(B/'asset-library.json')['assets']};manifest={x['id']:x for x in read(B/'asset-manifest.json')['assets']};bodies=[]
for b in scene['blocks']:
 aid=b['sourceAssetId'];a=manifest.get(b['assetId']);canonical=assets.get(aid);s=a['worldSizeUnits'][0]/canonical['worldSizeUnits'][0] if a and canonical and a.get('worldSizeUnits') and canonical.get('worldSizeUnits') else 1
 p=footprint(aid,b['anchorMap'],s) if aid in ['B01','B02','B03','B04','B05','B06','B07','B08'] else g['rect'](b['anchorMap'],1.4 if aid.startswith('T') else 1,1.4 if aid.startswith('T') else 1)
 bodies.append({'id':b['persistentId'],'polygonMap':p,'assetId':aid})
grounds=scene['groundSurfaces'];g['obs']=[(s['polygonMap'],bbox(s['polygonMap']))for s in grounds+bodies]
def witness(poly,idx,phase,aid,scale,anchor,route=None):
 q=audit(poly,[idx]);body=phase=='body';limits={'otherSourceMetres':2 if body else .15,'roadEdgeMetres':2 if body else -.001,'waterSafetyMetres':5,'visible143GroundBodyMetres':1 if body else .15,'otherNewBodyMetres':2 if body else .15};failed=[k for k,v in limits.items()if q[k]<v]
 nearestsource=min(((pp(poly,p),i,p)for i,p,bb in g['bs']if i!=idx),key=lambda x:x[0]);ng=min(((pp(poly,s['polygonMap']),s)for s in grounds),key=lambda x:x[0]);nb=min(((pp(poly,s['polygonMap']),s)for s in bodies),key=lambda x:x[0]);nr=min(((pl(poly,a,b)-r['width']/2,r['id'],j,a,b,r['width'])for r,j,a,b,bb in g['segments']),key=lambda x:x[0])
 return {'sourceIndex':idx,'sourcePolygonMap':c['buildings'][idx],'phase':phase,'assetId':aid,'scale':scale,'anchorMap':anchor,'candidatePolygonMap':poly,'route':route,'clearance':q,'failed':failed,'nearestOtherSource':{'index':nearestsource[1],'distance':nearestsource[0],'polygonMap':nearestsource[2]},'nearestOldGround':{'distance':ng[0],'surface':ng[1]},'nearestOldBody':{'distance':nb[0],'body':nb[1]},'nearestRoad':nr}
examples=[]
# Four bounded geometric cases plus one metadata-only case, max five distinct sources.
for idx in [1766,1765,1740,1423]:
 C=centre(c['buildings'][idx]);picked=[];rr=[(r,j,a,b)for r,j,a,b,bb in g['segments']if g['boxgap'](bbox(c['buildings'][idx]),bb)<65]
 for du,dn in [(0,0),(-3,0),(3,0),(0,-3),(0,3)]:
  anchor=add(add(C,mul(u,du)),mul(n,dn));poly=footprint('B05',anchor,.9);q=audit(poly,[idx])
  if idx==1766 and not picked:picked.append(witness(poly,idx,'body','B05',.9,anchor))
  if idx==1740 and q['visible143GroundBodyMetres']<1:picked.append(witness(poly,idx,'body','B05',.9,anchor));break
  if not good(q,True):continue
  start=pixelmap([810,1070],anchor,g['cal']['B05'],.9)
  for r,j,a,b in sorted(rr,key=lambda v:math.dist(start,foot(start,v[2],v[3])[0]))[:3]:
   stop,_=foot(start,a,b);D=math.dist(stop,start)
   if D<=r['width']/2+2 or D>45:continue
   end=add(stop,mul([(stop[k]-start[k])/D for k in (0,1)],-(r['width']/2+.03)));p=strip(start,end);aq=audit(p,[idx])
   if not good(aq) and idx in [1765,1423]:picked.append(witness(p,idx,'approach','B05',.9,anchor,{'roadId':r['id'],'segment':j,'kind':'direct','centreline':[start,end]}));break
  if picked:break
 examples.append({'sourceIndex':idx,'witnesses':picked})
examples.append({'sourceIndex':586,'sourcePolygonMap':c['buildings'][586],'record':next(r for r in rows if r['sourceIndex']==586),'meaning':'metadata membership gate only; no geometry attempted'})
save('examples.json',examples)
# Minimal semantic-distance counterexample: grass and solid same polygon return identical distance; actual witnesses above establish real use.
rect=g['rect'];p=rect([0,0],4,4);q=rect([3,0],4,4);save('minimal-distance-example.json',{'candidate':p,'ordinaryPavingOrGrass':q,'samePolygonIfSolid':q,'distanceToBoth':pp(p,q),'groundGateWouldReject':pp(p,q)<.15,'meaning':'pp has no surface-purpose semantics; collision value alone cannot certify entity blocking. No gates changed.'})
after={str(p):sha(p) for p in files};changed=[p for p in before if before[p]!=after[p]];save('input-sha-after.json',after);save('protection.json',{'protectedFiles':len(files),'changed':changed,'unchanged':not changed,'noPlannerModuleExecuted':True,'pureFunctionASTOnly':True,'gameTestsRun':False});assert not changed
print(json.dumps({k:v for k,v in summary.items()if k!='rows'},indent=2));print('EXAMPLES',[(e['sourceIndex'],[(w['failed'],w['nearestOldGround']['surface'].get('id'))for w in e.get('witnesses',[])])for e in examples])
