#!/usr/bin/env python3
"""One useful market forecourt; only four explicitly authorized old surfaces may change."""
import sys
sys.dont_write_bytecode=True
import copy,math,shutil
from pathlib import Path
import neighborhood_export as e
import geometry_009 as g
I=e.I;B=I/'market-life';OWNER='009r4-src-0587'
if (I/'market-life-increment.json').exists():raise ValueError('Market life already exists; preserve hand edits, export only')
B.mkdir(exist_ok=True)
for src,name in [(e.V/'assets/scene-layout.json','pre-market-scene.json'),(e.M,'pre-market-neighborhood.tmj'),(e.V/'assets/asset-manifest.json','pre-market-asset-manifest.json')]:
 dst=B/name
 if not dst.exists():shutil.copyfile(src,dst)
 assert e.sha(src)==e.sha(dst),'Current scene/map differs from frozen art baseline'
old=e.read(B/'pre-market-scene.json');assert e.sha(B/'pre-market-scene.json')=='69ee3cb14645be306500d5db09a46a3eac4b5c75c8154eaacb586a90a23e6cc8'
assert [len(old['blocks']),len(old['groundSurfaces'])]==[156,497]
ref=e.read(e.lib.OLD/'planning/mixed-street-layout.json')['referenceFrame'];u=ref['frontageTangent'];n=ref['positiveRoadNormal'];anchor=next(b['anchorMap']for b in old['blocks']if b['persistentId']==OWNER)
def world(q):return[anchor[k]+q[0]*u[k]+q[1]*n[k]for k in(0,1)]
def polygon(points):return[world(q)for q in points]
original={s['id']:s for s in old['groundSurfaces']};walk=original[OWNER+'-walk-0']['polygonMap'];cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']};lib={a['id']:a for a in e.read(I/'asset-library.json')['assets']}
allowed=[OWNER+'-source-court-587']+[OWNER+'-planted-pocket-'+str(i)for i in range(3)]
designs=[
 ('source-court-587','S01-paving',[[-5.4,2.8],[8.8,3.6],[8.4,5.3],[3,6.9],[1.8,6.9],[1.8,5.8],[-2.2,5.8],[-2.2,3.8],[-5.4,3.4]],'finite entrance apron follows actual curved-market front; replace large mostly hidden carrier paving'),
 ('planted-pocket-0','G02-planting',[[-8,7.5],[-7.7,7.2],[-6.2,7.2],[-6,7.5],[-6,9.4],[-6.3,9.8],[-7.7,9.8],[-8,9.5]],'bounded shade-tree pocket adjoining waiting terrace, no floating rear rectangle'),
 ('planted-pocket-1','G02-planting',[[-5.4,4.2],[-5.1,3.9],[-2.5,3.9],[-2.2,4.2],[-2.2,5.3],[-2.5,5.6],[-5.1,5.6],[-5.4,5.3]],'low shrub planting joins entrance apron, native root is inferred'),
 ('planted-pocket-2','G01-lawn',[[6.8,6.2],[8.2,6.2],[8.8,6.8],[8.5,9.4],[7.8,9.8],[6.8,9.3]],'finite green edge bounds garbage pad; no extra facility/vehicle road')]
changes=[]
for suffix,mat,points,reason in designs:
 id=OWNER+'-'+suffix;before=original[id];after={'id':id,'materialId':mat,'polygonMap':polygon(points)};changes.append({'surfaceId':id,'before':before,'after':after,'changedFields':[k for k in before if before[k]!=after[k]],'reason':reason,'localTNCandidate':points})
grounds=[
 {'id':'market-life-rest-terrace','materialId':'S01-paving','polygonMap':polygon([[-7.6,8.3],[-3.4,8.3],[-3,8.7],[-3,11.6],[-3.4,12],[-7.2,12],[-7.6,11.6]]),'purpose':'finite waiting terrace with one bench and adjoining shade-tree pocket'},
 {'id':'market-life-waste-pad','materialId':'S01-paving','polygonMap':polygon([[3.8,6.1],[6.4,6.1],[6.8,6.5],[6.8,9.1],[4.2,9.1],[3.8,8.7]]),'purpose':'small separate double-bin collection landing, away from main door'}]
def strip(a,z,width):
 dx,dy=z[0]-a[0],z[1]-a[1];length=math.hypot(dx,dy);normal=[-dy/length,dx/length]
 return[[q[k]+side*width/2*normal[k]for k in(0,1)]for q,side in[(a,1),(z,1),(z,-1),(a,-1)]]
# Both short branches terminate at the exact immutable path edge. Their half-plane
# clips guarantee no polygon covers the old 1.5m walk, even though the edges touch.
for name,targetTN,crossN,width,edge,keepAbove in [('rest',[-3.3,9.5],9.5,1.5,walk[:2],True),('waste',[4.2,7.5],7.5,1.2,[walk[3],walk[2]],False)]:
 door=next(b['entryMap']for b in e.read(I/'batch-009-r4/009r4-derived-plan.json')['buildings']if b['id']==OWNER);end=[(walk[1][k]+walk[2][k])/2 for k in(0,1)]
 doorN=sum((door[k]-anchor[k])*n[k]for k in(0,1));endN=sum((end[k]-anchor[k])*n[k]for k in(0,1));t=(crossN-doorN)/(endN-doorN);start=[door[k]+t*(end[k]-door[k])for k in(0,1)]
 raw=strip(start,world(targetTN),width);a,z=edge;slope=(z[1]-a[1])/(z[0]-a[0]);hn=[slope,-1]if keepAbove else[-slope,1];hc=sum(hn[k]*a[k]for k in(0,1));poly=g.clip_half(raw,hn,hc)
 assert len(poly)>=4 and all(sum(hn[k]*q[k]for k in(0,1))<=hc+1e-9 for q in poly)
 assert g.gap(poly,walk)==0
 grounds.append({'id':'market-life-'+name+'-connector','materialId':'S01-paving','polygonMap':poly,'purpose':'short visual pedestrian branch connecting existing immutable1.5m walk to '+name+' landing; no nav edge','candidateWidth':width,'immutableWalkEdgeHalfPlane':{'normal':hn,'constant':hc}})
for s in grounds:s['owner']=OWNER
assert g.gap(grounds[0]['polygonMap'],grounds[2]['polygonMap'])==0 and g.gap(grounds[1]['polygonMap'],grounds[3]['polygonMap'])==0

citypath=e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json';city=e.read(citypath);nodes={x['id']:[x['x'],x['y']]for x in city['nodes']};ctx=e.read(e.R/'planning/source-context.json');water=[s['points']for s in ctx['waterAreas']];blue=e.read(e.R.parent.parent/'2026-11-02-county-zoning/selection.json')['regions']['city']['worldPolygonMetresApprox']
oldshapes=e.read(I/'batch-009-r5/actual-old-shape-evidence.json')+[{'id':b['persistentId'],'polygon':b['footprintPolygonMap'],'scope':'fifth-v2 native footprint'}for b in e.read(I/'batch-009-r5/009r5-derived-plan.json')['buildings']];assert len(oldshapes)==156
def bbox(p):return[min(q[0]for q in p),min(q[1]for q in p),max(q[0]for q in p),max(q[1]for q in p)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def index(rows):return[(id,p,bbox(p))for id,p in rows]
sourceidx=index(enumerate(city['buildings']));oldidx=index((s['id'],s['polygon'])for s in oldshapes);groundidx=index((s['id'],s['polygonMap'])for s in old['groundSurfaces']);wateridx=index(enumerate(water));wlidx=index(enumerate(line for line in city['waterways']if len(line)>1));roads=[dict(r,points=[nodes[id]for id in r['nodes']])for r in city['roads']];rb=[bbox(r['points'])for r in roads]
def nearest(poly,idx,exclude=()):
 bb=bbox(poly);best=float('inf');item=None
 for lower,id,q in sorted((boxgap(bb,box),id,q)for id,q,box in idx if id not in exclude):
  if lower>best:break
  d=g.gap(poly,q)
  if d<best:best,item=d,id
 return best,item
def check(poly,pathedge=False,object=False):
 assert all(g.inside(q,blue)for q in poly),'Outside blue'
 source,sid=nearest(poly,sourceidx,[587]);prior,pid=nearest(poly,oldidx);watergap,wid=nearest(poly,wateridx);excluded=allowed+([OWNER+'-walk-0']if pathedge else[]);ground,gid=nearest(poly,groundidx,excluded);bb=bbox(poly);rg=float('inf');rid=None;wg=float('inf');wlid=None
 for lower,j in sorted((max(0,boxgap(bb,box)-roads[j]['width']/2),j)for j,box in enumerate(rb)):
  if lower>max(0,rg):break
  d=g.line_gap(poly,roads[j]['points'])-roads[j]['width']/2
  if d<rg:rg,rid=d,roads[j]['id']
 for lower,j,line in sorted((max(0,boxgap(bb,box)-3),j,line)for j,line,box in wlidx):
  if lower>max(0,wg):break
  d=g.line_gap(poly,line)-3
  if d<wg:wg,wlid=d,j
 pg,poiid=min((0 if g.inside(nodes[p['node']],poly)else min(g.point_segment(nodes[p['node']],a,z)for a,z in g.edges(poly)),p['node'])for p in city['pois'])
 assert source>.15,('other source',sid,source);assert prior>.1,('old156 ground',pid,prior);assert ground>1e-7,('unapproved old ground',gid,ground);assert watergap>0 and wg>=5;assert rg>=0 and pg>0
 walkgap=g.gap(poly,walk)
 if object:assert walkgap>.35,('main walk object gap',walkgap)
 return {'otherSourceGap':source,'otherSourceIndex':sid,'old156GroundContactGap':prior,'oldInstance':pid,'unapprovedGroundGap':ground,'unapprovedGroundId':gid,'immutableWalkGap':walkgap,'onlyOwnSourceExemption':587,'allowedGroundSupportIds':excluded,'waterPolygonGap':watergap,'waterwayMinus3mGap':wg,'waterwayId':wlid,'carriagewayGap':rg,'roadId':rid,'originalPOIGap':pg,'POINode':poiid,'allVerticesBlue':True}
for change in changes:change['staticCheck']=check(change['after']['polygonMap'],pathedge=change['surfaceId'].endswith('source-court-587'))
for s in grounds:s['staticCheck']=check(s['polygonMap'],pathedge='connector'in s['id'])
fixtures=[];native=[];protected=e.read(I/'batch-009-r5/read-only-protection.json')
specs=[('shade-tree','T02',[-7,8.5],'one natural shade tree next to waiting seat'),('waiting-bench','P03',[-5,10.5],'one waiting bench facing the market forecourt'),('entry-sign','P01',[2.7,4.9],'daytime blank information lightbox near entrance, no invented text'),('waste-bins','P10',[5,7.8],'separate public collection double bin, no business logic'),('low-shrub','T05',[-3.7,4.75],'one additional low clump comparison along entrance planting edge')]
for suffix,aid,tn,purpose in specs:
 a=lib[aid];c=cal[aid];pos=world(tn);raw=Path(a['runtimeDerivation']['source']);raw=raw if raw.is_absolute()else e.R.parents[3]/raw;pvpath=raw.parent/'provenance.json';pv=e.read(pvpath);tool=Path(pv.get('toolSourceAbsolutePath',pv.get('toolSource',pv.get('original_tool_output_absolute_path',''))));assert e.sha(raw)==e.sha(tool)==a['runtimeDerivation']['sourceSHA256'];assert e.sha(I/'assets'/a['file'])==a['sha256']
 for f in [raw,pvpath,tool]:protected[str(f.resolve())]=e.sha(f)
 if aid=='T02':foot=[[pos[0]+dx,pos[1]+dy]for dx,dy in[(-.2,-.2),(.2,-.2),(.2,.2),(-.2,.2)]];method='candidate0.4m root box at existing manually calibrated visible root; not canopy'
 elif aid=='T05':foot=[[pos[k]+x*u[k]+y*n[k]for k in(0,1)]for x,y in[(-1.1,-.8),(1.1,-.8),(1.1,.8),(-1.1,.8)]];method='inferred root, conservative2.2x1.6 candidate envelope; rear roots hidden, uncertainty70px'
 else:
  q=e.project(pos);foot=[e.unproject([q[k]+16*(pix[k]-c['anchorPixel'][k])/c['nativePixelsPerUnit']for k in(0,1)])for pix in c['groundContactPixelsManual']];method='existing actual native baseplate/leg/feet manual contacts and same scalar PPU, uncertainty20px'
 proof=check(foot,object=True)
 for other in fixtures:assert g.gap(foot,other['groundContactPolygonMap'])>.3,('new fixture contact collision',suffix,other['id'])
 supporting=changes[1]['after']['polygonMap']if aid=='T02'else changes[2]['after']['polygonMap']if aid=='T05'else grounds[0]['polygonMap']if aid=='P03'else grounds[1]['polygonMap']if aid=='P10'else changes[0]['after']['polygonMap']
 assert all(g.inside(q,supporting)for q in foot),('unsupported fixture',aid)
 fixtures.append({'id':'market-life-'+suffix,'persistentId':'market-life-'+suffix,'libraryAssetId':aid,'anchorMap':pos,'localTNCandidate':tn,'worldSizeUnits':a['worldSizeUnits'],'anchorUV':a['anchorUV'],'uniformScale':1,'rotation':0,'ownerBuildingId':OWNER,'groundContactPolygonMap':foot,'groundContactMethod':method,'purpose':purpose,'staticCheck':proof,'sourceNativeSHA256':e.sha(raw)})
 native.append({'id':aid,'nativePath':str(raw),'toolPath':str(tool),'nativeToolSHAEqual':True,'sourceNativeSHA256':e.sha(raw),'runtimeFile':a['file'],'runtimeSHA256':a['sha256'],'nativePPU':c.get('nativePixelsPerUnit',c.get('sourceNativePPU')),'anchorPixel':c.get('anchorPixel',c.get('originalAnchorPixel'))})
assert sum(b['sourceAssetId']=='T05'for b in old['blocks'])+sum(f['libraryAssetId']=='T05'for f in fixtures)==2
result={'status':'prepared-market-use-candidate-not-rendered','ownerBuildingId':OWNER,'baselineCounts':[156,497],'baselineSceneSHA256':e.sha(B/'pre-market-scene.json'),'baselineTiledSHA256':e.sha(B/'pre-market-neighborhood.tmj'),'authorizedOldSurfaceIds':allowed,'immutableWalkId':OWNER+'-walk-0','existingGroundChanges':changes,'newGroundSurfaces':grounds,'newFixtures':fixtures,'vehiclesAdded':0,'vehicleSkipReason':'no approved parkingSpace plus car approach; primary pedestrian route never used as car access','noTablesStoolsFencesTankOrVegetablePlots':True,'oldInstancesChanged':False,'newBusinessPOIs':0,'newNavigationEdges':0,'scaleRule':'all existing canonical PPU/frame/anchor unchanged, positive scalar1 only','T05RootMeasured':False,'T05TotalInstanceCount':2}
e.write(B/'market-layout.json',result);e.write(B/'native-contact-provenance.json',native);e.write(B/'read-only-protection.json',protected)
print('Prepared',len(fixtures),'real fixtures,',len(grounds),'new finite paving faces,',len(changes),'authorized old surfaces; layoutSHA',e.sha(B/'market-layout.json'))
