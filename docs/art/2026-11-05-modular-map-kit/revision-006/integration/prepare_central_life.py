#!/usr/bin/env python3
"""One complete visual street vignette; selected-ground edits only, no source/old sprite mutation."""
import sys
sys.dont_write_bytecode=True
import copy,math,json
from pathlib import Path
import neighborhood_export as e
import geometry_009 as g
I=e.I;B=I/'central-life';baseline=e.read(B/'pre-life-scene.json');assert len(baseline['blocks'])==94 and len(baseline['groundSurfaces'])==260
if (I/'central-life-increment.json').exists():raise ValueError('Life increment exists; retain manual edits and export only')
assert e.sha(e.V/'assets/scene-layout.json')==e.sha(B/'pre-life-scene.json')
selected=['009r3-src-0593','009r3-src-0610','009r3-src-0612'];owners={id:int(id[-4:])for id in selected};r3=e.read(I/'batch-009-r3/009r3-derived-plan.json');bybuilding={x['id']:x for x in r3['buildings']};oldground={x['id']:x for x in baseline['groundSurfaces']};lib={a['id']:a for a in e.read(I/'asset-library.json')['assets']};cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']};protected=e.read(B/'read-only-protection.json');citypath=e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json';city=e.read(citypath);nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};ctx=e.read(e.R/'planning/source-context.json');water=[s['points']for s in ctx['waterAreas']]
priorplans=[e.read(I/'batch-009/009-derived-plan.json'),e.read(I/'batch-009-r2/009r2-derived-plan.json'),r3];known={}
for plan in priorplans:
 for b in plan['buildings']+plan.get('fixtures',[]):known[b['persistentId']]=b
aliases={a['id']:a for a in e.read(B/'pre-life-asset-manifest.json')['assets']};oldbodies=[]
for b in baseline['blocks']:
 prior=known.get(b['persistentId']);shape=prior.get('footprintPolygonMap',prior.get('actualFootContactPolygonMap',prior.get('rootCandidatePolygonMap')))if prior else None
 if shape:oldbodies.append((b['persistentId'],shape));continue
 a=aliases[b['assetId']];q=e.project(b['anchorMap']);w,h=[v*16 for v in a['worldSizeUnits']];u,v=a['anchorUV'];shape=[e.unproject(p)for p in [[q[0]-u*w,q[1]-v*h],[q[0]+(1-u)*w,q[1]-v*h],[q[0]+(1-u)*w,q[1]+(1-v)*h],[q[0]-u*w,q[1]+(1-v)*h]]];oldbodies.append((b['persistentId'],shape))

def bbox(poly):return[min(p[0]for p in poly),min(p[1]for p in poly),max(p[0]for p in poly),max(p[1]for p in poly)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def index(rows):return[(id,p,bbox(p))for id,p in rows]
source=index(enumerate(city['buildings']));olds=index(oldbodies);waters=index(enumerate(water));roads=[dict(r,points=[nodes[id]for id in r['nodes']])for r in city['roads']];roadboxes=[bbox(r['points'])for r in roads]
def nearest(poly,entries,exclude=()):
 best=float('inf');id=None;bb=bbox(poly)
 for low,key,q in sorted((boxgap(bb,b),key,q)for key,q,b in entries if key not in exclude):
  if low>best:break
  dist=g.gap(poly,q)
  if dist<best:best,id=dist,key
 return best,id

def check(poly,owner,object=False,own_lawn=False):
 src,srcid=nearest(poly,source,[owners[owner]]);old,oldid=nearest(poly,olds,()if object else[owner]);wg,wid=nearest(poly,waters);bb=bbox(poly);rg=float('inf');rid=None
 for low,j in sorted((max(0,boxgap(bb,box)-roads[j]['width']/2),j)for j,box in enumerate(roadboxes)):
  if low>max(0,rg):break
  dist=g.line_gap(poly,roads[j]['points'])-roads[j]['width']/2
  if dist<rg:rg,rid=dist,roads[j]['id']
 assert src>1e-7,('other raw source',srcid,src);assert old>1e-7,('old94 body/contact',oldid,old);assert wg>0;assert rg>=-1e-8,('carriageway',rid,rg)
 # Existing surfaces outside the selected third-batch plots cannot be overlapped or changed.
 unaffected=[s for s in baseline['groundSurfaces']if not any(s['id'].startswith(id+'-')for id in selected)];priorgrounds=min((g.gap(poly,s['polygonMap']),s['id'])for s in unaffected);assert priorgrounds[0]>1e-7,('unselected/frozen ground',priorgrounds)
 walkgaps=[(g.gap(poly,oldground[id+'-walk-0']['polygonMap']),id)for id in selected]
 if object:assert min(d for d,id in walkgaps)>=.35,('protected1.5m walk',walkgaps)
 nodegap=min((0 if g.inside(nodes[p['node']],poly)else min(g.point_segment(nodes[p['node']],a,b)for a,b in g.edges(poly)),p['node'])for p in city['pois']);assert nodegap[0]>0
 return {'nearestOtherSource':srcid,'otherSourceGap':src,'nearestOld94Instance':oldid,'old94FootOrConservativeGap':old,'waterPolygonGap':wg,'waterIndex':wid,'sourceRoadCarriagewayGap':rg,'roadId':rid,'nearestUnselectedOrProtectedGround':priorgrounds[1],'unselectedGroundGap':priorgrounds[0],'protectedWalkGaps':walkgaps,'originalPOINodeGap':nodegap[0],'POINodeId':nodegap[1],'sourceCarrierExemptionOnly':owners[owner]}

# Existing third-batch surfaces:10 color/material changes, no walk or source geometry alteration.
changes=[]
for id in selected:
 for s in baseline['groundSurfaces']:
  if not s['id'].startswith(id+'-')or'-walk-'in s['id']:continue
  after=copy.deepcopy(s)
  if '-carrier-court-'in s['id']:after['materialId']='G10-r3-courtyard'if id.endswith('0610')else'G01-lawn'
  elif '-planted-edge-'in s['id']:after['materialId']='G02-planting'
  if after!=s:changes.append({'surfaceId':s['id'],'before':s,'after':after,'fieldsChanged':['materialId'],'reason':'bounded courtyard lawn replaces unused broad white paving'if'carrier-court'in s['id']else'darker controlled planted border now joined to useful courtyard and real greenery'})

# 593 private irregular lawn follows its real carrier boundary, not a free-floating rectangle.
raw=bybuilding[selected[0]]['visualReplacementOf']['sourcePolygonsMap'][0]
newgrounds=[{'id':'life-central-593-private-lawn','owner':selected[0],'materialId':'G04-suburb-lawn','polygonMap':raw,'purpose':'bounded private garden follows existing source parcel notch; primary door walk retained above it','tiledInsertion':'before-third-grounds'}]
# Small beveled commercial terrace shares a same-material junction with the immutable primary walk.
patio=[[-1249.7,187.45],[-1249.25,187.0],[-1243.65,187.0],[-1243.2,187.45],[-1243.2,190.45],[-1243.65,190.9],[-1249.25,190.9],[-1249.7,190.45]]
newgrounds.append({'id':'life-central-610-rest-terrace','owner':selected[1],'materialId':'S01-paving','polygonMap':patio,'purpose':'finite connected commercial sitting terrace, not whole source white-tile court','tiledInsertion':'after-third-grounds'})
benchpad=[[-1247.2,203.9],[-1246.8,203.5],[-1244.0,203.5],[-1243.6,203.9],[-1243.6,206.5],[-1244.0,206.9],[-1246.8,206.9],[-1247.2,206.5]]
newgrounds.append({'id':'life-central-612-bench-pad','owner':selected[2],'materialId':'S01-paving','polygonMap':benchpad,'purpose':'small quiet bench landing in otherwise green yard','tiledInsertion':'after-third-grounds'})
b=bybuilding[selected[2]];a,z=b['visualApproach']['centrelineMap'];t=(-1248.7-a[0])/(z[0]-a[0]);start=[a[k]+t*(z[k]-a[k])for k in(0,1)];path=[start,[-1247.6,202.8],[-1246.0,204.3]]
def strip(path,width):
 normals=[]
 for a,z in zip(path,path[1:]):dx,dy=z[0]-a[0],z[1]-a[1];l=math.hypot(dx,dy);normals.append([-dy/l,dx/l])
 left=[];right=[]
 for j,q in enumerate(path):
  if j==0:n=normals[0]
  elif j==len(path)-1:n=normals[-1]
  else:
   n=[normals[j-1][k]+normals[j][k]for k in(0,1)];l=math.hypot(*n);n=[v/l for v in n];d=sum(n[k]*normals[j][k]for k in(0,1));n=[v/d for v in n]
  left.append([q[k]+width/2*n[k]for k in(0,1)]);right.append([q[k]-width/2*n[k]for k in(0,1)])
 return left+list(reversed(right))
newgrounds.append({'id':'life-central-612-garden-connector','owner':selected[2],'materialId':'S01-paving','polygonMap':strip(path,1.1),'purpose':'limited quiet garden connector to original1.5m walk; visual ground only, no nav edge','centrelineMap':path,'candidateWidth':1.1,'tiledInsertion':'after-third-grounds'})
for s in newgrounds:s['staticCheck']=check(s['polygonMap'],s['owner'])
assert g.gap(patio,oldground[selected[1]+'-walk-0']['polygonMap'])==0
assert g.gap(newgrounds[-1]['polygonMap'],oldground[selected[2]+'-walk-0']['polygonMap'])==0 and g.gap(newgrounds[-1]['polygonMap'],benchpad)==0

specs=[('593-tree','T02',[-1244.2,178.9],selected[0]),('593-short-fence','P06',[-1248.5,173.5],selected[0]),('610-sign','P01',[-1249.0,188.2],selected[1]),('610-table','P04-v2',[-1245.8,188.9],selected[1]),('610-stool-a','P05',[-1246.7,189.25],selected[1]),('610-stool-b','P05',[-1245.2,188.05],selected[1]),('610-short-fence','P07',[-1244.1,190.7],selected[1]),('612-bench','P03',[-1245.5,205.0],selected[2]),('612-tree','T02',[-1247.5,206.0],selected[2])]
props=[];provenance=[]
for suffix,aid,anchor,owner in specs:
 a=lib[aid];c=cal[aid];assert 'hold'not in a.get('availability','');raw=Path(a['runtimeDerivation']['source']);assert raw.is_absolute();assert e.sha(raw)==a['runtimeDerivation']['sourceSHA256'];assert e.sha(I/'assets'/a['file'])==a['sha256'];protected[str(raw.resolve())]=e.sha(raw)
 pvpath=raw.parent/'provenance.json';pv=e.read(pvpath);tool=Path(pv.get('toolSourceAbsolutePath',pv.get('toolSource',pv.get('original_tool_output_absolute_path',''))))
 if tool.is_file():assert e.sha(tool)==e.sha(raw);protected[str(tool.resolve())]=e.sha(tool)
 else:raise ValueError('Actual tool source path unavailable '+aid)
 protected[str(pvpath.resolve())]=e.sha(pvpath);ppu=c.get('nativePixelsPerUnit',c.get('sourceNativePPU'));ap=c.get('anchorPixel',c.get('originalAnchorPixel'));q=e.project(anchor)
 if aid=='T02':poly=[[anchor[0]+dx,anchor[1]+dy]for dx,dy in[(-.2,-.2),(.2,-.2),(.2,.2),(-.2,.2)]];method='candidate0.4m trunk-root box at accepted native root; not canopy or surveyed foundation'
 else:
  points=c['groundContactPixelsManual'];poly=[e.unproject([q[k]+16*(pix[k]-ap[k])/ppu for k in(0,1)])for pix in points];method='actual prior manually calibrated native foot/post-contact pixels, positive scalar unchanged'
  if len(poly)==2:
   dx,dy=poly[1][0]-poly[0][0],poly[1][1]-poly[0][1];l=math.hypot(dx,dy);nx,ny=-dy/l*.1,dx/l*.1;poly=[[poly[0][0]+nx,poly[0][1]+ny],[poly[1][0]+nx,poly[1][1]+ny],[poly[1][0]-nx,poly[1][1]-ny],[poly[0][0]-nx,poly[0][1]-ny]];method+='; conservative0.2m rail/post footprint thickness, not a stretched standard segment'
 checkrow=check(poly,owner,object=True)
 for other in props:assert g.gap(poly,other['groundContactPolygonMap'])>=.2,('new prop feet overlap/too close',suffix,other['id'])
 supporting=patio if owner==selected[1]else(newgrounds[0]['polygonMap']if owner==selected[0]else bybuilding[owner]['visualReplacementOf']['sourcePolygonsMap'][0])
 assert all(g.inside(v,supporting)for v in poly),('foot outside bounded intended courtyard',suffix)
 row={'id':'life-central-'+suffix,'persistentId':'life-central-'+suffix,'libraryAssetId':aid,'anchorMap':anchor,'worldSizeUnits':a['worldSizeUnits'],'anchorUV':a['anchorUV'],'uniformScale':1,'rotation':0,'owner':owner,'groundContactPolygonMap':poly,'groundContactMethod':method,'staticCheck':checkrow,'sourceNativeSHA256':e.sha(raw),'purpose':('private garden'if owner==selected[0]else'public commercial resting corner'if owner==selected[1]else'quiet residential bench garden')}
 if aid=='P05':row['contextualAdmission']='explicit parent-approved P04-v2 table/stool comparison, same610 terrace; not standalone library gate override';row['tablePersistentId']='life-central-610-table'
 if aid in['P06','P07']:row['boundaryScope']='one unrotated/unmirrored native short segment only; no closure/stretch/seamless kit claim'
 props.append(row);provenance.append({'assetId':aid,'native':str(raw),'toolSource':str(tool),'nativeToolSHAEqual':True,'sourceNativeSHA256':e.sha(raw),'runtimeFile':a['file'],'runtimeSHA256':a['sha256']})
result={'status':'prepared-local-art-increment-not-yet-seen','baselineSceneSHA256':e.sha(B/'pre-life-scene.json'),'baselineTiledSHA256':e.sha(B/'pre-life-neighborhood.tmj'),'baselineCounts':[94,260],'selectedThirdBatchBuildingIds':selected,'existingGroundChanges':changes,'newGroundSurfaces':newgrounds,'newFixtures':props,'parentAuthorizationScope':'selected third96 grounds only, primary1.5m paths and first164 grounds protected; old94 unchanged','groundOrderRules':['593 lawn before third-batch selected borders/walks','610 terrace/612 bench pad+connector after existing selected grounds','all original road geometry last, no source data or navigation change'],'newSpriteOrderRule':'depth inserted between fixed oldR3 editor ranks, old94 relative order and editor rank preserved'}
e.write(B/'life-layout.json',result);e.write(B/'ground-diff-before-after.json',changes);e.write(B/'native-ground-provenance.json',provenance);e.write(B/'read-only-protection.json',protected);print('Prepared',len(props),'real props,',len(newgrounds),'limited grounds,',len(changes),'selected material changes; layoutSHA',e.sha(B/'life-layout.json'))
