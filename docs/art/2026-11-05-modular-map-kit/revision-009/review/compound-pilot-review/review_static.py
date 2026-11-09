"""Independent bounded static reviewer: no producer/importer module execution."""
import ast,json,math,hashlib,copy
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=next(p for p in H.parents if (p/'delivery-game/assets/resources/map-sample/city.json').exists());K=ROOT/'docs/art/2026-11-05-modular-map-kit';R=K/'revision-009';I=K/'revision-006/integration';F=R/'planning/compound-pilot';C=ROOT/'delivery-game/assets/resources/map-sample/city.json'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):(H/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
expected='a5564388f2efb4afc55c8baa50e0f0607b1d0484ded6c2b05b6cc9abda6edb27'; target='e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7'
planfile=F/'scene-compound-pilot.json';live=K/'revision-006/viewer/assets/scene-layout.json';ref=R/'pipeline/current-integration-reference.json';assert sha(planfile)==expected;assert read(ref)['currentSceneSHA256']==target and sha(live)==target
# Freeze one already-published exact byte copy, never poll an in-flight viewer.
(H/'published161-scene.json').write_bytes(live.read_bytes()); scene=read(H/'published161-scene.json');p=read(planfile);market=read(I/'market-life/market-layout.json')
paths=[planfile,F/'import-contract.json',F/'static-verification.json',F/'verify_static.py',F/'plan_compound.py',F/'old156-ground-evidence.json',R/'scenic-scene-contract.md',ref,R/'pipeline/applied-market-life.json',live,I/'neighborhood.tmj',C,ROOT/'docs/art/2026-11-02-county-zoning/selection.json',K/'revision-003/road-constraint.json',K/'revision-006/planning/build_plan.py',R/'baselines/visible143/asset-calibration.json',I/'asset-library.json',I/'asset-calibration.json',I/'market-life/market-layout.json',I/'market-life/native-contact-provenance.json',I/'market-life/pre-market-scene.json',I/'batch-009-r5/009r5-derived-plan.json',I/'batch-009-r4/actual-old-shape-evidence.json',I/'batch-009-r4/009r4-derived-plan.json',I/'native-comparison/comparison-plan.json',R/'planning/fit-round-4/usage-contracts.json']
lib={a['id']:a for a in read(I/'asset-library.json')['assets']};cal={a['id']:a for a in read(R/'baselines/visible143/asset-calibration.json')['assets']}
for aid in ['B01','B05']:
 a=lib[aid];paths += [I/'assets'/a['file'],Path(a['runtimeDerivation']['source'])]
before={str(f):sha(f)for f in paths};save('input-sha-before.json',before)
checks=[]
def ck(ok,label,evidence=None):checks.append({'rule':label,'passed':bool(ok),'evidence':evidence})
city=read(C);nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};z=read(ROOT/'docs/art/2026-11-02-county-zoning/selection.json');geo=read(K/'revision-003/road-constraint.json');P=geo['projection'];u=geo['streetTangentMap'];n=[-u[1],u[0]]
ns={'math':math,'z':z,'u':u,'n':n};names={'add','mul','rect','inside','ps','cross','ss','edges','pp','pl','inbounds'};t=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in t.body if isinstance(x,ast.FunctionDef)and x.name in names],type_ignores=[]),'<read-pure-geometry>','exec'),ns);pp=ns['pp'];pl=ns['pl'];inside=ns['inside'];edges=ns['edges'];ps=ns['ps']
def bbox(q):return [min(v[0]for v in q),min(v[1]for v in q),max(v[0]for v in q),max(v[1]for v in q)]
def bgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def pixel(px,anchor,co,s):
 ap=co.get('anchorPixel',co.get('originalAnchorPixel'));ppu=co.get('nativePixelsPerUnit',co.get('sourceNativePPU'));x,y=[(px[k]-ap[k])/ppu*s for k in (0,1)];a,b=P['axisX'],P['axisY'];d=a[0]*b[1]-a[1]*b[0];return [anchor[0]+(x*b[1]-y*b[0])/d,anchor[1]+(a[0]*y-a[1]*x)/d]
def poly_for(m):
 co=cal[m['libraryAssetId']];pts=co.get('occupiedGroundOutlinePixel')or co.get('groundCornersPixelLeftFrontRightRear')or ([[198,910],[438,1229],[1055,931],[815,612]] if m['libraryAssetId']=='B01' else None);assert pts;return [pixel(v,m['anchorMap'],co,m['uniformScale'])for v in pts]
def close(a,b):return len(a)==len(b)and all(math.dist(v,w)<1e-8 for v,w in zip(a,b))
def bindings(s):
 out=set()
 for r in s['visualReplacements']:
  v=r.get('visualReplacementOf',r);out.update(v.get('sourceIndices',r.get('sourceIndices',[])));i=v.get('sourceIndex',r.get('sourceIndex'))
  if i is not None:out.add(i)
 return out
bound=bindings(scene);reserved={i for r in read(R/'planning/fit-round-4/usage-contracts.json')['reservations']for i in r['sourceIndices']}
def ownership_ok(doc,old=bound,res=reserved):
 try:
  scenes=doc['scenes'];mods=doc['buildings'];ss={s['sceneId']:s for s in scenes};mm={m['persistentId']:m for m in mods};assert len(ss)==len(scenes)and len(mm)==len(mods);owners={}
  for s in scenes:
   assert len(s['sourceIndices'])==len(set(s['sourceIndices']));assert len(s['moduleIds'])==len(set(s['moduleIds']));assert set(s['moduleIds'])=={m['persistentId']for m in mods if m['sceneId']==s['sceneId']}
   for i in s['sourceIndices']:assert i not in owners and i not in old|res;owners[i]=s['sceneId']
  for m in mods:assert m['sceneId']in ss and m['sourceIndices'] and set(m['sourceIndices'])<=set(ss[m['sceneId']]['sourceIndices'])
  for s in scenes:assert set(s['sourceIndices'])=={i for m in mods if m['sceneId']==s['sceneId']for i in m['sourceIndices']}
  return True
 except (AssertionError,KeyError):return False
ck(ownership_ok(p),'scene-source-module-bidirectional-ownership');ck(len(bound)==81 and 125 not in bound|reserved,'125-unbound-unreserved',{'boundCount':len(bound),'reserved':sorted(reserved)})
ck([len(p['scenes']),len(p['buildings']),len(p['groundSurfaces']),len(set(p['sourceIndices'])),p['renderedNewCount']]==[1,2,5,1,0],'parsed-counts-1scene2modules5grounds1source0rendered');ck([p['sceneCount'],p['moduleCount'],p['groundSurfaceCount'],p['uniqueSourceCount'],p['userAcceptedNewCount']]==[1,2,5,1,0],'declared-counts');ck(p['projection']==P==scene['projection'],'projection-exact');ck([len(scene['blocks']),len(scene['groundSurfaces'])]==[161,501],'latest-published-counts')
neg=[]
for label,mut in [('duplicate-module-id',lambda q:q['buildings'][1].update(persistentId=q['buildings'][0]['persistentId'])),('missing-scene',lambda q:q['buildings'][1].pop('sceneId')),('orphan-module-membership',lambda q:q['scenes'][0]['moduleIds'].pop()),('cross-scene-source-reuse',lambda q:q['scenes'].append(dict(q['scenes'][0],sceneId='illegal-second-scene',moduleIds=[])))]:
 q=copy.deepcopy(p);mut(q);neg.append({'case':label,'rejected':not ownership_ok(q)})
neg += [{'case':'old-bound-source','rejected':not ownership_ok(p,bound|{125},reserved)},{'case':'reserved-source','rejected':not ownership_ok(p,bound,reserved|{125})}];ck(all(x['rejected']for x in neg),'ownership-negative-cases',neg)
for s in p['scenes']:
 ck(s['sourcePolygonsMap']==[city['buildings'][i]for i in s['sourceIndices']] and s['sourceSHA256']==sha(C),'exact-source-scene-copy');ck(s['originalSemanticStatus']=='unknown'and s['newPOIs']==s['newNavigationEdges']==s['renderedSourceCount']==0 and not s['oldSurfaceEdits'],'unknown-scenic-only-no-old-edit');ck(set(s['groundSurfaceIds'])=={v['id']for v in p['groundSurfaces']if v['sceneId']==s['sceneId']},'surface-membership')
for r in p['roads']:
 src=city['roads'][r['sourceRoadArrayIndex']];ck(src['nodes']==r['sourceNodeIds']and r['nodes']==[nodes[i]for i in src['nodes']]and all(r.get(k)==v for k,v in src.items()if k!='nodes'),'complete-road-every-field-and-order',r['id'])
for m in p['buildings']:
 aid=m['libraryAssetId'];a=lib[aid];co=cal[aid];sc=m['uniformScale'];ck(sc==({'B01':1,'B05':.9}[aid])and m['nodeScale']==1 and m['rotation']==0,'positive-scale-once-'+aid);ck(m['worldSizeUnits']==[v*sc for v in a['worldSizeUnits']]and m['anchorUV']==a['anchorUV'],'canonical-world-frame-'+aid);ck(close(poly_for(m),m['footprintPolygonMap']),'native-pixel-footprint-'+aid)
 ck(math.dist(pixel(m['entryPixel'],m['anchorMap'],co,sc),m['entryMap'])<1e-8 and m['entryPixel']==({'B01':[973,965],'B05':[810,1070]}[aid]),'true-door-pixel-'+aid);v=m['visualReplacementOf'];ck(v['sourcePolygonsMap']==[city['buildings'][i]for i in v['sourceIndices']]and v['sourceSHA256']==sha(C)and not v['sourceDataChanged'],'exact-module-source-'+aid)
 rt=I/'assets'/a['file'];im=Image.open(rt);ck(max(im.size)<=280 and sha(rt)==a['sha256']and sha(a['runtimeDerivation']['source'])==a['runtimeDerivation']['sourceSHA256'],'native-runtime-integrity-'+aid)
 ap=m['visualApproach'];pts=ap['centrelineMap'];ck(math.dist(pts[0],m['entryMap'])<1e-8 and not ap['originalPOIBindingClaimed']and ap['navigationEdgesCreated']==0,'door-not-poi-'+aid);rr=next(r for r in city['roads']if r['id']==ap['roadId']);j=ap['segmentIndex'];edge=ps(pts[-1],nodes[rr['nodes'][j]],nodes[rr['nodes'][j+1]])-rr['width']/2;ck(abs(edge-.03)<1e-8,'road-shoulder-'+aid,edge)
 d=math.dist(*pts);nv=[-(pts[1][1]-pts[0][1])/d,(pts[1][0]-pts[0][0])/d];expectedWalk=[[q[k]+nv[k]*sign*.75 for k in (0,1)]for q,sign in [(pts[0],1),(pts[1],1),(pts[1],-1),(pts[0],-1)]];ck(len(ap['polygonsMap'])==1 and close(expectedWalk,ap['polygonsMap'][0]),'actual-1.5m-walk-polygon-'+aid);cut=[pts[0][k]+.6*(pts[1][k]-pts[0][k])/d for k in (0,1)];normal=[-(pts[1][1]-cut[1])/math.dist(cut,pts[1]),(pts[1][0]-cut[0])/math.dist(cut,pts[1])];tail=[[q[k]+normal[k]*sign*.75 for k in (0,1)]for q,sign in [(cut,1),(pts[1],1),(pts[1],-1),(cut,-1)]];ck(pp(tail,m['footprintPolygonMap'])>=.05,'own-body-after-0.6m-'+aid,pp(tail,m['footprintPolygonMap']))
# Old exact exporter evidence is deliberately conservative where no measured ground controls exist.
old=read(I/'batch-009-r4/actual-old-shape-evidence.json');old +=[{'id':b['persistentId'],'polygon':b['footprintPolygonMap'],'scope':'resolved r4'}for b in read(I/'batch-009-r4/009r4-derived-plan.json')['buildings']];old +=[{'id':b['persistentId'],'polygon':b.get('footprintPolygonMap',b.get('groundContactPolygonMap')),'scope':'native comparison'}for b in read(I/'native-comparison/comparison-plan.json')['instances']];old +=[{'id':b['persistentId'],'polygon':b['footprintPolygonMap'],'scope':'resolved r5'}for b in read(I/'batch-009-r5/009r5-derived-plan.json')['buildings']];old +=[{'id':b['persistentId'],'polygon':b['groundContactPolygonMap'],'scope':b['groundContactMethod']}for b in market['newFixtures']]
ck(len(old)==161 and {b['id']for b in old}=={b['persistentId']for b in scene['blocks']},'old161-contact-id-coverage')
for b in market['newFixtures']:
 actual=next(v for v in scene['blocks']if v['persistentId']==b['persistentId']);ck(actual['groundContactPolygonMap']==b['groundContactPolygonMap']and math.dist(actual['anchorMap'],b['anchorMap'])<1e-8,'market-actual-contact-'+b['libraryAssetId'])
ck(sha(I/'market-life/market-layout.json')==read(R/'pipeline/applied-market-life.json')['marketLayoutSHA256'],'market-published-layout-sha')
# Global broadphase with bbox pruning only when proven lower bound exceeds the current minimum.
def nearest(poly,items,fn=pp):
 bb=bbox(poly);best=9999;bid=None
 for low,id,q,extra in sorted(((max(0,bgap(bb,bbox(q))-extra),str(id),q,extra)for id,q,extra in items),key=lambda x:x[0]):
  if low>max(best,0):break
  dist=fn(poly,q)-extra
  if dist<best:best,bid=dist,id
 return {'gap':best,'id':bid}
sources=[(i,q,0)for i,q in enumerate(city['buildings'])if i!=125];roads=[(r['id']+':'+str(j),[nodes[a],nodes[b]],r['width']/2)for r in city['roads']for j,(a,b)in enumerate(zip(r['nodes'],r['nodes'][1:]))];waters=[('area:'+str(i),a['points'],0)for i,a in enumerate(city['areas'])if a.get('kind')=='water'and len(a.get('points',[]))>=3];wlines=[('line:'+str(i)+':'+str(j),[a,b],3)for i,w in enumerate(city['waterways'])for j,(a,b)in enumerate(zip(w,w[1:]))];grounds=[(s['id'],s['polygonMap'],0)for s in scene['groundSurfaces']];bodies=[(b['id'],b['polygon'],0)for b in old]
geom=[]
for item,isbody in [(b,True)for b in p['buildings']]+[(s,False)for s in p['groundSurfaces']]:
 poly=item['footprintPolygonMap']if isbody else item['polygonMap'];q={'id':item['id'],'kind':'body'if isbody else 'ground','otherSource':nearest(poly,sources),'road':nearest(poly,roads,lambda q,line:pl(q,*line)),'waterArea':nearest(poly,waters),'waterwayMinus3':nearest(poly,wlines,lambda q,line:pl(q,*line)),'oldGround':nearest(poly,grounds),'oldContact':nearest(poly,bodies),'marketContacts':[{'id':b['persistentId'],'gap':pp(poly,b['groundContactPolygonMap'])}for b in market['newFixtures']]};q['poi']=min((0 if inside(nodes[o['node']],poly)else min(ps(nodes[o['node']],a,b)for a,b in edges(poly)),o['node'])for o in city['pois']);q['blue']=all(ns['inbounds'](v,'city')for v in poly);ck(q['otherSource']['gap']>=(2 if isbody else .15)and q['road']['gap']>=(2 if isbody else -.001)and min(q['waterArea']['gap'],q['waterwayMinus3']['gap'])>=5 and min(q['oldGround']['gap'],q['oldContact']['gap'])>=(1 if isbody else .15)and q['poi'][0]>=.15 and q['blue'],'global-latest-external-'+item['id'],q);geom.append(q)
a,b=p['buildings'];bodygap=pp(a['footprintPolygonMap'],b['footprintPolygonMap']);walkgap=min(pp(q,peer['footprintPolygonMap'])for m,peer in [(a,b),(b,a)]for q in m['visualApproach']['polygonsMap']);ck(bodygap>=2 and abs(bodygap-p['scenes'][0]['jointBodyGapMetres'])<1e-8,'peer-body-gap',bodygap);ck(walkgap>=.15 and abs(walkgap-p['scenes'][0]['peerWalkBodyGapMetres'])<1e-8,'peer-walk-gap',walkgap)
for s in p['groundSurfaces']:
 ck(s['owner']==s['sceneId']==p['scenes'][0]['sceneId']and set(s['moduleIds'])<=set(p['scenes'][0]['moduleIds']),'ground-scene-ownership-'+s['id']);ck(all(pp(s['polygonMap'],m['footprintPolygonMap'])>=.15 for m in p['buildings']if m['persistentId']!=s.get('thresholdOf')),'ground-peer-entities-'+s['id'])
paving=[s for s in p['groundSurfaces']if s['materialId']=='S01-paving'];seen={0}
while True:
 nxt=seen|{j for j,b in enumerate(paving)if any(pp(paving[i]['polygonMap'],b['polygonMap'])<1e-7 for i in seen)}
 if nxt==seen:break
 seen=nxt
ck(len(seen)==len(paving),'connected-paving-union');ck(any(pp(s['polygonMap'],q['polygonMap'])<1e-7 for s in p['groundSurfaces']if s['materialId']=='G02-planting'for q in paving),'garden-touches-paving')
# Independent convex clipping: source125 is convex (ignore closing duplicate).
def area(q):return abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in edges(q)))/2 if len(q)>2 else 0
clip=city['buildings'][125][:-1];sign=1 if sum(a[0]*b[1]-a[1]*b[0]for a,b in edges(clip))>0 else -1
fractions=[]
for m in p['buildings']:
 out=m['footprintPolygonMap'][:]
 for a,b in edges(clip):
  inp=out;out=[]
  if not inp:break
  def d(v):return sign*((b[0]-a[0])*(v[1]-a[1])-(b[1]-a[1])*(v[0]-a[0]))
  for v,w in edges(inp):
   dv,dw=d(v),d(w)
   if dv>=0:out.append(v)
   if (dv>=0)!=(dw>=0):out.append([v[k]+dv/(dv-dw)*(w[k]-v[k])for k in (0,1)])
 A=area(m['footprintPolygonMap']);insidearea=area(out);fractions.append({'moduleId':m['persistentId'],'area':A,'insideArea':insidearea,'outsideArea':A-insidearea,'insideFraction':insidearea/A})
for f,decl in zip(fractions,p['scenes'][0]['footprintVsCarrier']):ck(abs(f['insideFraction']-decl['insideFraction'])<1e-8,'carrier-clip-fraction-'+f['moduleId'],f)
after={str(f):sha(f)for f in paths};save('input-sha-after.json',after);changed=[f for f,h in before.items()if after[f]!=h];ck(not changed,'protected-inputs-unchanged',changed)
result={'verdict':'safe-for-limited-integration'if all(c['passed']for c in checks)else 'changes-required','reviewedCandidateSHA256':sha(planfile),'baselineSceneSHA256':sha(H/'published161-scene.json'),'baselineTiledSHA256':before[str(I/'neighborhood.tmj')],'latestPublishedReferenceSHA256':before[str(ref)],'baselineCounts':[161,501,81],'counts':{'sources':1,'scenes':1,'modules':2,'grounds':5,'rendered':0},'checks':checks,'geometry':geom,'bodyGapMetres':bodygap,'peerWalkGapMetres':walkgap,'carrierFractions':fractions,'negativeCases':neg,'producerCheckCountObserved':read(F/'static-verification.json')['passedRuleCount'],'protectedFiles':len(paths),'changedInputs':changed,'independentPureASTGeometryOnly':True,'gameTestsRun':False,'browserRun':False,'noImplementationChanges':True,'producerBaselineStaleButIndependentlyRechecked':True,'scope':'single local integration comparison only, consumer scene contract adaptation and immediate same-SHA baseline recheck required'};save('review.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['checks','geometry']},indent=2));print('FAILED',[c['rule']for c in checks if not c['passed']])
