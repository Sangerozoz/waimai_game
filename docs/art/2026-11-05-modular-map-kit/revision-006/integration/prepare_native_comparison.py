#!/usr/bin/env python3
"""Actual native controls -> one positive-scalar calibration, legal-source small comparison."""
import sys
sys.dont_write_bytecode=True
import copy,math,shutil,json
from pathlib import Path
from PIL import Image
import neighborhood_export as e
import geometry_009 as g
I=e.I;B=I/'native-comparison';N=e.R.parent/'revision-009/art-expansion/native'
if (I/'native-comparison-increment.json').exists():raise ValueError('Comparison already applied; preserve editable map and export only')
B.mkdir(exist_ok=True)
for src,name in [(e.V/'assets/scene-layout.json','pre-comparison-scene.json'),(e.M,'pre-comparison-neighborhood.tmj'),(e.V/'assets/asset-manifest.json','pre-comparison-asset-manifest.json'),(I/'asset-library.json','pre-comparison-library.json'),(I/'asset-calibration.json','pre-comparison-calibration.json')]:
 dst=B/name
 if not dst.exists():shutil.copyfile(src,dst)
 assert e.sha(src)==e.sha(dst),'Existing map/library changed after snapshot; never overwrite'
old=e.read(B/'pre-comparison-scene.json');assert e.sha(B/'pre-comparison-scene.json')=='9f7adf3e269fc320830b3b5b422797faed5014b453a99d199efd0c76d546bf8f'
assert [len(old['blocks']),len(old['groundSurfaces'])]==[143,462]
protected=e.read(I/'batch-009-r4/read-only-protection.json')
# Two editable library containers intentionally receive new entries, all old entries fixed.
for f in [I/'asset-library.json',I/'asset-calibration.json']:protected.pop(str(f.resolve()),None)
for root in [N/'B12-001',N/'B13-001',N/'T05-001']:
 for f in root.iterdir():
  if f.is_file():protected[str(f.resolve())]=e.sha(f)
usagepath=e.R.parent/'revision-009/planning/fit-round-4/usage-contracts.json';usage=e.read(usagepath);usages={s['assetId']:s for s in usage['reservations']}
admission=e.R.parent/'revision-009/art-expansion/review/admission-round4-inputs.json'
for f in [usagepath,admission]:protected[str(f.resolve())]=e.sha(f)
ref=e.read(e.lib.OLD/'planning/mixed-street-layout.json')['referenceFrame'];u=ref['frontageTangent'];normal=ref['positiveRoadNormal'];pr=e.META['projection']
def projdelta(q):return [q[0]*pr['axisX'][k]+q[1]*pr['axisY'][k]for k in(0,1)]
pu,pn=projdelta(u),projdelta(normal);lu,ln=math.hypot(*pu),math.hypot(*pn)
specs={
 'B12':{'dims':[6.4,4.6,3.8],'left':[183,813],'front':[450,1143],'right':[1065,861],'outline':[[183,813],[450,1143],[779,989],[820,1027],[934,976],[915,930],[1065,861],[798,531]],'entry':[841.5,935.5],'step':[877,1001.5],'visibleBaseRisePixels':230},
 'B13':{'dims':[6,5,3.6],'left':[143,804],'front':[440,1197],'right':[1120,943],'outline':[[143,804],[440,1197],[556,1180],[694,1122],[758,1097],[1084,954],[1120,943],[823,550]],'entry':[601.5,1103.5],'step':[625,1151],'visibleBaseRisePixels':330}}
library=e.read(B/'pre-comparison-library.json');calibration=e.read(B/'pre-comparison-calibration.json');newassets=[];newcal=[];checks=[]
for aid in ['B12','B13','T05']:
 root=N/(aid+'-001');raw=root/(aid+'-v1.png');rt=root/(aid+'-runtime-280'+('-clean'if aid=='B13'else'')+'.png');der=e.read(root/(aid+'-runtime-280.runtime.json'));pv=e.read(root/'provenance.json');tool=Path(pv.get('toolSourceAbsolutePath',pv.get('toolSource','')))
 assert tool.is_file(),(aid,'tool source missing')
 assert e.sha(raw)==e.sha(tool)==der['sourceSHA256'];protected[str(tool.resolve())]=e.sha(tool)
 assert list(Image.open(raw).size)==der['sourceSize'];assert list(Image.open(rt).size)==der['runtimeSize']and max(der['runtimeSize'])<=280
 if aid=='B13':
  assert e.sha(rt)=='f97a525034c83998be5782fc21572e60ca937b05629a646db63e459d9892bb7c'
  before=Image.open(root/'B13-runtime-280.png').convert('RGBA');after=Image.open(rt).convert('RGBA');mask=Image.open(root/'B13-runtime-280-clean-deletion-mask.png').convert('L');changed=[]
  for j,(a,z,m)in enumerate(zip(before.getdata(),after.getdata(),mask.getdata())):
   assert (a!=z)==bool(m)
   if a!=z:assert a[3]==1 and z==(0,0,0,0);changed.append(j)
  assert len(changed)==1055
 else:assert e.sha(rt)==der['sha256']
 box=der['cropBox'];w,h=box[2]-box[0],box[3]-box[1]
 if aid in specs:
  s=specs[aid];anchor=[(s['left'][k]+s['right'][k])/2 for k in(0,1)];lengths=[math.dist(s['front'],s['right']),math.dist(s['left'],s['front'])];target=[s['dims'][0]*lu,s['dims'][1]*ln];ppu=sum(a*b for a,b in zip(lengths,target))/sum(t*t for t in target)
  c={'id':aid,'status':'native-controls-reviewed-single-source-small-comparison-only','nativePixelsPerUnit':ppu,'anchorPixel':anchor,'entryPixel':s['entry'],'stepFrontPixel':s['step'],'occupiedGroundOutlinePixel':s['outline'],'manualVisibleControlsPath':str((root/'native-control-points.json').resolve()),'manualVisibleControlsSHA256':e.sha(root/'native-control-points.json'),'visibleControlUncertaintyPixels':3,'additionalOuterBaseEstimateUncertaintyPixels':20,'hiddenRearInferred':True,'hiddenRearPixel':s['outline'][-1],'hiddenRearMeaning':'conservative parallelogram closure from visible left/front/right; not measured corner','candidateDimensionsFrontageDepthHeight':s['dims'],'positiveUniformOnly':True,'scaleMethod':'one positive scalar least squares from full visible body frontage and depth versus candidate game dimensions, no anisotropy or camera correction','actualCandidateBodyFrontageDepth':[lengths[0]/ppu/lu,lengths[1]/ppu/ln],'heightReadbackCandidate':s['visibleBaseRisePixels']/ppu/abs(pr['axisZ'][1]),'heightMeaning':'coarse visible wall rise only; roof excluded, not surveyed height','availability':'one-legal-source-comparison-only','angleResiduals':e.read(root/'native-control-points.json')['visibleStraightBaseEdges']}
 else:
  anchor=[660,930];target=[abs(pu[0])*1.8+abs(pn[0])*1.2,abs(pu[1])*1.8+abs(pn[1])*1.2+abs(pr['axisZ'][1])*.9];ppu=sum(a*b for a,b in zip([w,h],target))/sum(t*t for t in target)
  c={'id':aid,'status':'manual-inferred-root-garden-comparison-only','nativePixelsPerUnit':ppu,'anchorPixel':anchor,'rootOriginMeasured':False,'rootVisibility':'hidden by overlapping leaf clumps; root inferred from basal twig locations, not transparent hole','visibleBasalTwigPixelsApproximate':[[457,989],[862,867]],'rootInferenceUncertaintyPixels':70,'candidateDimensionsFrontageDepthHeight':[1.8,1.2,.9],'conservativeContactEnvelopeFrontageDepth':[2.2,1.6],'positiveUniformOnly':True,'scaleMethod':'one positive scalar least squares of existing full crop width/height against candidate projected crown envelope; foliage is NOT a camera-axis measurement','availability':'one-or-two-low-garden-comparisons-only','risk':'inferred root/rear contacts, yellow-green fringe and repeated leaf texture; not user or precise camera accepted'}
 uv=[(anchor[0]-box[0])/w,(anchor[1]-box[1])/h];world=[w/ppu,h/ppu]
 c.update({'sourceNativeSHA256':e.sha(raw),'sourceNativeSize':der['sourceSize'],'runtimeSize':der['runtimeSize'],'cropBox':box,'anchorUV':uv,'worldSizeUnits':world,'runtimeSHA256':e.sha(rt),'runtimeNativeMappingUnchanged':True})
 runtime=copy.deepcopy(der)
 if aid=='B13':runtime.update({'file':rt.name,'sha256':e.sha(rt),'runtimeBytes':rt.stat().st_size,'originalRuntimeSHA256':der['sha256'],'cleanDerivationPath':str((root/'B13-runtime-280-clean-derivation.json').resolve()),'cleanMapping':'same262x280 canvas/original crop; same calibratedPPU/anchor for pristine and clean; no recrop or resize'})
 newassets.append({'id':aid,'kind':'building'if aid in specs else'plant','file':rt.name,'sha256':e.sha(rt),'nativeSize':der['runtimeSize'],'nativePixelsPerUnit':1,'worldSizeUnits':world,'anchorUV':uv,'projectionId':pr['id'],'runtimeDerivation':runtime,'availability':c['availability']});newcal.append(c)
 checks.append({'id':aid,'nativePath':str(raw.resolve()),'toolPath':str(tool),'nativeSHA256':e.sha(raw),'runtimePath':str(rt.resolve()),'runtimeSHA256':e.sha(rt),'nativeToolSHAEqual':True,'runtimeLongEdge':max(der['runtimeSize']),'PPU':ppu,'anchorPixel':anchor,'anchorUV':uv,'worldSizeUnits':world,'controlPointStatus':'manually estimated / root inferred, no registration-ready claim'})

# Static source/road/water/prior protection, including all fourth-batch and life objects.
citypath=e.R.parents[3]/'delivery-game/assets/resources/map-sample/city.json';city=e.read(citypath);nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};ctx=e.read(e.R/'planning/source-context.json');water=[s['points']for s in ctx['waterAreas']]
oldshapes=e.read(I/'batch-009-r4/actual-old-shape-evidence.json')+[{'id':b['persistentId'],'polygon':b['footprintPolygonMap'],'scope':'fourth-batch resolved native footprint'}for b in e.read(I/'batch-009-r4/009r4-derived-plan.json')['buildings']]
assert len(oldshapes)==143
bluepath=e.R.parent.parent/'2026-11-02-county-zoning/selection.json';blue=e.read(bluepath)['regions']['city']['worldPolygonMetresApprox']
roads=[dict(r,points=[nodes[n]for n in r['nodes']])for r in city['roads']];roadby={r['id']:r for r in roads}
def bbox(poly):return[min(q[0]for q in poly),min(q[1]for q in poly),max(q[0]for q in poly),max(q[1]for q in poly)]
def boxgap(a,b):return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))
def index(rows):return[(id,p,bbox(p))for id,p in rows]
sourceidx=index(enumerate(city['buildings']));oldidx=index((s['id'],s['polygon'])for s in oldshapes);wateridx=index(enumerate(water));groundidx=index((s['id'],s['polygonMap'])for s in old['groundSurfaces']);rb=[bbox(r['points'])for r in roads]
def nearest(poly,idx,exclude=()):
 bb=bbox(poly);best=float('inf');item=None
 for lower,id,q in sorted((boxgap(bb,box),id,q)for id,q,box in idx if id not in exclude):
  if lower>best:break
  d=g.gap(poly,q)
  if d<best:best,item=d,id
 return best,item
def check(poly,own,ground_exempt=()):
 if not all(g.inside(q,blue)for q in poly):raise ValueError('Outside blue')
 sg,si=nearest(poly,sourceidx,own);og,oi=nearest(poly,oldidx);wg,wi=nearest(poly,wateridx);gg,gi=nearest(poly,groundidx,ground_exempt);bb=bbox(poly);rg=float('inf');ri=None
 for lower,j in sorted((max(0,boxgap(bb,bb2)-roads[j]['width']/2),j)for j,bb2 in enumerate(rb)):
  if lower>max(0,rg):break
  d=g.line_gap(poly,roads[j]['points'])-roads[j]['width']/2
  if d<rg:rg,ri=d,roads[j]['id']
 pg,pi=min((0 if g.inside(nodes[poi['node']],poly)else min(g.point_segment(nodes[poi['node']],a,z)for a,z in g.edges(poly)),poi['node'])for poi in city['pois'])
 errors=[]
 for d,id,label in [(sg,si,'other source'),(og,oi,'actual143 ground/contact'),(wg,wi,'water'),(gg,gi,'protected462 ground')]:
  if d<=1e-7:errors.append(label+' '+str(id))
 if rg<0:errors.append('carriageway '+str(ri))
 if pg==0:errors.append('original POI '+pi)
 if errors:raise ValueError('; '.join(errors))
 return {'otherSourceGap':sg,'otherSourceIndex':si,'actual143Gap':og,'oldInstance':oi,'waterGap':wg,'waterIndex':wi,'protectedGroundGap':gg,'protectedGroundId':gi,'roadEdgeGap':rg,'roadId':ri,'POIGap':pg,'POINodeId':pi,'onlyOwnCarrierExempted':own,'groundSupportExemptions':list(ground_exempt),'allVerticesBlue':True}
def pixelmap(pix,anchor,c):
 q=e.project(anchor);return e.unproject([q[k]+16*(pix[k]-c['anchorPixel'][k])/c['nativePixelsPerUnit']for k in(0,1)])
def rect(anchor,fw,dep):return[[anchor[k]+x*u[k]+y*normal[k]for k in(0,1)]for x,y in[(-fw/2,-dep/2),(fw/2,-dep/2),(fw/2,dep/2),(-fw/2,dep/2)]]
def strip(a,z,width):
 dx,dy=z[0]-a[0],z[1]-a[1];l=math.hypot(dx,dy);n=[-dy/l,dx/l]
 return[[q[k]+side*width/2*n[k]for k in(0,1)]for q,side in[(a,1),(z,1),(z,-1),(a,-1)]]
admitted=[];surfaces=[];rejected=[];trials=[]
for aid in ['B12','B13']:
 c=next(x for x in newcal if x['id']==aid);a=next(x for x in newassets if x['id']==aid);use=usages[aid];own=use['sourceIndices'];assert len(own)==1 and city['buildings'][own[0]][:-1]==use['sourcePolygonMap']or city['buildings'][own[0]]==use['sourcePolygonMap']
 assert not set(own)&{i for r in old['visualReplacements']for i in r.get('sourceIndices',[r.get('sourceIndex')])}
 candidate=use['anchorCandidateMap'];r=roadby[use['sourceRoadId']];j=use['sourceNodeRangeInclusive'][0];start,end=r['points'][j:j+2];dx,dy=end[0]-start[0],end[1]-start[1];length=math.hypot(dx,dy);accepted=None
 offsets=[(0,0)]+[(x/2,y/2)for x in range(-6,7)for y in range(-6,7)if x or y];offsets.sort(key=lambda q:math.hypot(*q))
 for off in offsets:
  anchor=[candidate[k]+off[k]for k in(0,1)];foot=[pixelmap(pix,anchor,c)for pix in c['occupiedGroundOutlinePixel']];step=pixelmap(c['stepFrontPixel'],anchor,c);door=pixelmap(c['entryPixel'],anchor,c)
  t=max(0,min(1,sum((step[k]-start[k])*[dx,dy][k]for k in(0,1))/(length*length)));at=[start[k]+t*[dx,dy][k]for k in(0,1)];out=[step[k]-at[k]for k in(0,1)];d=math.hypot(*out);out=[v/d for v in out];shoulder=[at[k]+out[k]*(r['width']/2+1.83)for k in(0,1)];pathstart=[step[k]-out[k]*.03 for k in(0,1)];walk=strip(pathstart,shoulder,1.5)
  try:bodycheck=check(foot,own);walkcheck=check(walk,own)
  except ValueError as exc:
   trials.append({'assetId':aid,'anchorOffset':off,'rejectedReason':str(exc)});continue
  accepted={'id':'009art-src-'+str(own[0]).zfill(4)+'-'+aid,'persistentId':'009art-src-'+str(own[0]).zfill(4)+'-'+aid,'libraryAssetId':aid,'anchorMap':anchor,'worldSizeUnits':a['worldSizeUnits'],'anchorUV':a['anchorUV'],'uniformScale':1,'rotation':0,'footprintPolygonMap':foot,'entryMap':door,'entryPixel':c['entryPixel'],'stepFrontMap':step,'stepFrontPixel':c['stepFrontPixel'],'sourceNativeSHA256':c['sourceNativeSHA256'],'visualReplacementOf':{'sourceArray':'city.buildings','sourceIndices':own,'sourcePolygonsMap':[city['buildings'][i]for i in own],'sourceSHA256':e.sha(citypath),'sourceDataChanged':False},'landUseIntent':use['landUseIntent'],'sceneProgramme':'single-storey ordinary dwelling comparison'if aid=='B12'else'low street shop comparison, no business address','sourceRoadId':r['id'],'visualApproach':{'centrelineMap':[pathstart,shoulder],'width':1.5},'staticCheck':bodycheck,'anchorDerivation':{'contractCandidateAnchorMap':candidate,'appliedWorldTranslation':list(off),'reason':'legal actual native footprint/door route fit; no image rotation/resize/shear'},'status':'one-source-runtime-comparison-not-accepted'}
  walksurface={'id':accepted['id']+'-walk-0','owner':accepted['id'],'materialId':'S01-paving','polygonMap':walk,'staticCheck':walkcheck,'purpose':'finite1.5m visual pedestrian connection from actual outer step to original source road shoulder, no nav edge'}
  base=city['buildings'][own[0]]
  try:basecheck=check(base,own);surfaces.append({'id':accepted['id']+'-source-yard','owner':accepted['id'],'materialId':'G01-lawn'if aid=='B12'else'S01-paving','polygonMap':base,'staticCheck':basecheck,'purpose':'finite original carrier yard, no source geometry change'})
  except ValueError as exc:rejected.append({'surfaceId':accepted['id']+'-source-yard','reason':str(exc),'buildingRetained':True})
  surfaces.append(walksurface);admitted.append(accepted);break
 if not accepted:rejected.append({'assetId':aid,'sourceIndices':own,'reason':'No legal actual native footprint and1.5m outer-step connection within3m of original reservation anchor; see placement-trials.json','fallbackCreated':False})

# One visible middle layer next to the existing tree/bench courtyard; no old ground edit.
c=next(x for x in newcal if x['id']=='T05');a=next(x for x in newassets if x['id']=='T05');anchor=[-1250.5,207.5];contact=rect(anchor,2.2,1.6);owner='009r3-src-0612';support=[s['id']for s in old['groundSurfaces']if s['id'].startswith(owner+'-')and s['materialId']not in['S01-paving','S02-asphalt']]
try:
 proof=check(contact,[612],support);lawn=next(s for s in old['groundSurfaces']if s['id']==owner+'-carrier-court-612')['polygonMap'];assert all(g.inside(q,lawn)for q in contact),'Conservative shrub envelope outside existing residential lawn'
 admitted.append({'id':'009art-612-T05','persistentId':'009art-612-T05','libraryAssetId':'T05','anchorMap':anchor,'worldSizeUnits':a['worldSizeUnits'],'anchorUV':a['anchorUV'],'uniformScale':1,'rotation':0,'groundContactPolygonMap':contact,'sourceNativeSHA256':c['sourceNativeSHA256'],'ownerBuildingId':owner,'sceneProgramme':'one low shrub layer beside existing tree and bench, no duplicated garden furniture','rootOriginMeasured':False,'rootInferenceUncertaintyPixels':70,'staticCheck':proof,'status':'one-low-garden-comparison-not-accepted'})
except (ValueError,AssertionError)as exc:rejected.append({'assetId':'T05','reason':str(exc),'fallbackCreated':False})
out={'status':'prepared-real-native-calibration-and-legal-comparison-not-displayed','baselineCounts':[143,462],'baselineSceneSHA256':e.sha(B/'pre-comparison-scene.json'),'baselineTiledSHA256':e.sha(B/'pre-comparison-neighborhood.tmj'),'usageContractPath':str(usagepath.resolve()),'usageContractSHA256':e.sha(usagepath),'admissionPath':str(admission.resolve()),'admissionSHA256':e.sha(admission),'calibration':newcal,'assets':newassets,'instances':admitted,'newGrounds':surfaces,'rejected':rejected,'sourceDataChanged':False,'newBusinessPOIs':0,'newNavigationEdges':0,'newArtGenerated':False,'scaleRule':'single calibrated canonical size, nodeScale1; no anisotropy/mirror/rotation','groundRule':'new legal connection and limited original source yard only; existing462 unchanged'}
e.write(B/'comparison-plan.json',out);e.write(B/'placement-trials.json',trials);e.write(B/'native-provenance-check.json',checks);e.write(B/'read-only-protection.json',protected)
print('calibrated',[(x['id'],x['nativePixelsPerUnit'],x['worldSizeUnits'])for x in newcal]);print('admitted',[(x['id'],x['anchorMap'])for x in admitted],'newgrounds',len(surfaces),'rejected',rejected)
