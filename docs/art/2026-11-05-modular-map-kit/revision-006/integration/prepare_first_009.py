#!/usr/bin/env python3
"""Derive the explicitly approved009 seed; no source or existing placement writes."""
import sys
sys.dont_write_bytecode=True
import copy,math
from pathlib import Path
import neighborhood_export as e
import geometry_009 as g
I=e.I;B=I/'batch-009';P=e.R.parent/'revision-009/planning/first-expansion-batch.json';PS='9360a09116a099e6df54fd2848ee49bd3b39ab7c90d0b5273ba0bfb4089cc9e6'
assert e.sha(P)==PS
if (I/'north-009-increment.json').exists():raise ValueError('009 already appended; preserve hand edits, export instead')
plan=e.read(P);derived=copy.deepcopy(plan);scene=e.read(B/'pre-009-scene.json');assert len(scene['blocks'])==57 and len(scene['groundSurfaces'])==115
assert e.sha(B/'pre-009-scene.json')==plan['protectedExisting']['sceneSHA256'];city=e.read(plan['source']['cityPath']);assert e.sha(plan['source']['cityPath'])==plan['source']['citySHA256'];e.verify_roads(plan)
assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']};cal={a['id']:a for a in e.read(I/'asset-calibration.json')['assets']};nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};roads=[dict(r,points=[nodes[n]for n in r['nodes']])for r in city['roads']]
zonefile=e.R.parent.parent/'2026-11-02-county-zoning/selection.json'
zones=e.read(zonefile)['regions'];blue=zones['city']['worldPolygonMetresApprox'];green=zones['urban']['worldPolygonMetresApprox'] if 'urban'in zones else zones['core']['worldPolygonMetresApprox']
readprotect=e.read(B/'read-only-protection.json');readprotect[str(zonefile.resolve())]=e.sha(zonefile)
# Do not bind unrelated concurrent009 planning work. Only the parent-fixed seed is consumed.
readprotect={p:h for p,h in readprotect.items()if '/revision-009/planning/'not in p or p==str(P.resolve())}
checks=[];provenance=[];extra_surfaces=[];fixtures=[];grounds=plan['groundSurfaces'];polys=[b['footprintPolygonMap']for b in plan['buildings']]

def obstacle(poly,owner):
 others=[(g.gap(poly,p),i)for i,p in enumerate(city['buildings'])if i!=owner]
 nearest=min(others)
 roadway=min((g.line_gap(poly,r['points'])-r['width']/2,r['id'])for r in roads)
 water=min(g.line_gap(poly,line)for line in city['waterways'])
 assert all(g.inside(q,blue)for q in poly),'Outside blue'
 assert nearest[0]>.001,('Other source building overlap',nearest)
 assert roadway[0]>-.001,('Road carriageway overlap',roadway)
 assert water>18,('Conservative18m source water centreline guard',water)
 assert not any(g.gap(poly,p)==0 for p in plan['protectedExisting']['regionProtectionPolygonsMap']),'Old57 region overlap'
 return {'nearestOtherSourceBuildingIndex':nearest[1],'nearestOtherSourceBuildingGap':nearest[0],'nearestRoadCarriagewayGap':roadway[0],'nearestRoadId':roadway[1],'waterCentrelineGap':water,'waterGuardCandidateMetres':18,'blueInside':True,'greenInside':all(g.inside(q,green)for q in poly)}

def native_points(aid,anchor,pixels):
 c=cal[aid];ap=c.get('anchorPixel',c.get('originalAnchorPixel'));ppu=c.get('nativePixelsPerUnit',c.get('sourceNativePPU'));pr=e.project(anchor)
 return [e.unproject([pr[k]+(pix[k]-ap[k])*16/ppu for k in (0,1)])for pix in pixels]

for b in derived['buildings']:
 aid=b['libraryAssetId'];a=assets[aid];c=cal[aid];replacement=b['visualReplacementOf'];owner=replacement['sourceIndex'];assert city['buildings'][owner]==replacement['sourcePolygonMap'];assert replacement['sourceSHA256']==plan['source']['citySHA256']
 if aid=='B08':raw=e.R/'native/B08-001/B08-v1.png';pvpath=raw.parent/'provenance.json';pv=e.read(pvpath);tool=Path(pv['toolSourceAbsolutePath'])
 elif aid=='B02':raw=e.R.parent/'revision-005/native/B02-001/B02-v1.png';pvpath=raw.parent/'provenance.json';pv=e.read(pvpath);tool=Path(pv['original_tool_output_absolute_path'])
 else:
  raw=e.R.parent/'revision-003/B01-road-aligned-native-v1.png';pvpath=e.R.parent/'revision-005/integration/provenance-check.json';pv=next(x for x in e.read(pvpath)if x['id']==aid);tool=Path(pv['source'])
 assert e.sha(raw)==e.sha(tool)==a['runtimeDerivation']['sourceSHA256'];assert e.sha(I/'assets'/a['file'])==a['sha256'];assert a['worldSizeUnits']==b['worldSizeUnits'] and a['anchorUV']==b['anchorUV']
 for path in [raw,pvpath,tool]:readprotect[str(path.resolve())]=e.sha(path)
 b['sourceNativeSHA256']=e.sha(raw);b['sourceNativeEvidence']={'nativePath':str(raw.resolve()),'toolSourcePath':str(tool),'provenancePath':str(pvpath.resolve()),'toolAndNativeByteEqual':True,'runtimeSHA256':a['sha256']}
 entry=native_points(aid,b['anchorMap'],[b['entryPixel']])[0];assert math.dist(entry,b['entryMap'])<1e-8
 # Every raw building except THIS building's own carrier remains an obstacle.
 check=obstacle(b['footprintPolygonMap'],owner);check.update({'id':b['id'],'sourceIndex':owner,'sourcePolygonSHA256':__import__('hashlib').sha256(__import__('json').dumps(replacement['sourcePolygonMap'],separators=(',',':')).encode()).hexdigest(),'sourceNativeSHA256':b['sourceNativeSHA256'],'entryPixel':b['entryPixel'],'entryConvertedMap':entry,'entryDifference':math.dist(entry,b['entryMap']),'candidateArea':g.area(b['footprintPolygonMap']),'sourceCarrierArea':g.area(replacement['sourcePolygonMap']),'areaRatio':replacement['candidateToSourceAreaRatio'],'interpretation':'building plus retained contextual land; not equal-footprint reconstruction','businessMapping':b['businessNodeMapping'],'ownSourceExcludedOnly':owner,'noOtherSourceObstacleRemoved':True})
 # Complete each small frontage using a bounded connected paving base beneath already approved strips.
 srcgrounds=[s for s in grounds if s['id'].startswith(b['id']+'-')];floor=g.hull(b['footprintPolygonMap']+[q for s in srcgrounds for q in s['polygonMap']]);fc=obstacle(floor,owner)
 sid=b['id']+'-forecourt-base';extra_surfaces.append({'id':sid,'materialId':'S01-paving','polygonMap':floor,'purpose':'limited connected pedestrian forecourt underneath original garden strips and1.5m approach; no vehicle road or navigation edge','ownerBuildingId':b['id'],'blockId':b['blockId'],'derivation':'convex hull of approved actual footprint and approved16-ground components; checked against all other source obstacles','staticCheck':fc});check['addedForecourtCheck']=fc
 # Existing street-tree scale, root explicitly in a planned planted border, away from the real door.
 garden=next(s for s in srcgrounds if s['id'].endswith('garden-0'));root=[sum(q[k]for q in garden['polygonMap'])/len(garden['polygonMap'])for k in (0,1)];rootpoly=[[root[0]+dx,root[1]+dy]for dx,dy in [(-.4,-.4),(.4,-.4),(.4,.4),(-.4,.4)]]
 if all(g.inside(q,garden['polygonMap'])for q in rootpoly) and min(g.gap(rootpoly,p)for p in polys)>.1 and math.dist(root,b['entryMap'])>3:
  tc=obstacle(rootpoly,owner);fixtures.append({'id':'009-extra-tree-'+str(owner),'persistentId':'009-extra-tree-'+str(owner),'libraryAssetId':'T01','anchorMap':root,'uniformScale':1,'rotation':0,'worldSizeUnits':assets['T01']['worldSizeUnits'],'anchorUV':assets['T01']['anchorUV'],'rootCandidatePolygonMap':rootpoly,'purpose':'street tree rooted in approved garden border, original T01 scale','ownerBuildingId':b['id'],'staticCheck':tc})
 checks.append(check);provenance.append({'id':b['id'],'assetId':aid,**b['sourceNativeEvidence'],'sourceNativeSHA256':b['sourceNativeSHA256']})
# One useful public rest/garbage combination on the market's continuous forecourt.
market=derived['buildings'][0];floor=extra_surfaces[0]['polygonMap'];owner=market['visualReplacementOf']['sourceIndex'];walk=market['doorApproach']['polygonMap'];gardens=[s['polygonMap']for s in grounds if s['id'].startswith(market['id']+'-garden')]
placed=[]
for aid in ['P03','P10']:
 c=cal[aid];candidates=[]
 for xstep in range(math.ceil(min(q[0]for q in floor)*2),math.floor(max(q[0]for q in floor)*2)+1):
  for ystep in range(math.ceil(min(q[1]for q in floor)*2),math.floor(max(q[1]for q in floor)*2)+1):
   root=[xstep/2,ystep/2];poly=native_points(aid,root,c['groundContactPixelsManual'])
   if not all(g.inside(q,floor)for q in poly) or min(g.gap(poly,p)for p in polys)<.75 or g.gap(poly,walk)<.7:continue
   if any(g.gap(poly,p)<.15 for p in gardens) or any(g.gap(poly,p)<.7 for p in placed):continue
   if any(g.gap(poly,f.get('rootCandidatePolygonMap',f.get('actualFootContactPolygonMap')))<1 for f in fixtures):continue
   score=abs(math.dist(root,market['entryMap'])-5)+(.2*math.dist(root,[sum(q[0]for q in floor)/len(floor),sum(q[1]for q in floor)/len(floor)]))
   candidates.append((score,root,poly))
 if candidates:
  _,root,poly=min(candidates);check=obstacle(poly,owner);fixtures.append({'id':'009-extra-market-'+aid,'persistentId':'009-extra-market-'+aid,'libraryAssetId':aid,'anchorMap':root,'uniformScale':1,'rotation':0,'worldSizeUnits':assets[aid]['worldSizeUnits'],'anchorUV':assets[aid]['anchorUV'],'actualFootContactPolygonMap':poly,'purpose':'public market forecourt rest and garbage point with continuous paving, clear door approach','ownerBuildingId':market['id'],'staticCheck':check});placed.append(poly)
# Road-side lamp native arm+n toward eastward carriageway; no PNG rotation.
road=plan['roads'][0]
for j,(segment,fraction)in enumerate([(0,.30),(1,.55)]):
 a,z=road['nodes'][segment:segment+2];dx,dy=z[0]-a[0],z[1]-a[1];length=math.hypot(dx,dy);normal=[dy/length,-dx/length];root=[a[k]+fraction*(z[k]-a[k])-(road['width']/2+1.2)*normal[k]for k in (0,1)];poly=[[root[0]+dx,root[1]+dy]for dx,dy in [(-.15,-.15),(.15,-.15),(.15,.15),(-.15,.15)]]
 if all(g.gap(poly,b['doorApproach']['polygonMap'])>.9 for b in plan['buildings']) and min(g.gap(poly,p)for p in polys)>1:
  check=obstacle(poly,-1);fixtures.append({'id':'009-extra-near-lamp-'+str(j),'persistentId':'009-extra-near-lamp-'+str(j),'libraryAssetId':'L-near','anchorMap':root,'uniformScale':1,'rotation':0,'worldSizeUnits':assets['L-near']['worldSizeUnits'],'anchorUV':assets['L-near']['anchorUV'],'rootCandidatePolygonMap':poly,'purpose':'upright lamp on original road shoulder; native+n arm toward carriageway','staticCheck':check})
# Ground order matters: connected bases first, approved walks/gardens second, original roads last in renderer.
derived['groundSurfaces']=extra_surfaces+derived['groundSurfaces'];derived['fixtures']=fixtures;derived['derivation']={'parentOriginalPath':str(P.resolve()),'parentOriginalSHA256':PS,'pre009SceneSHA256':e.sha(B/'pre-009-scene.json'),'pre009TiledSHA256':e.sha(B/'pre-009-neighborhood.tmj'),'sourceNativeSHAFilledFromActualToolAndNative':True,'extraGroundIds':[s['id']for s in extra_surfaces],'extraInstanceIds':[f['persistentId']for f in fixtures],'rules':['no old objects/ground/camera/rider changes','source carrier mapping retained; no raw source polygons were displayed in current renderer','all native images scale1, no plane rotation/mirror','small pedestrian-use forecourts only, original road full nodes retained','other source buildings/roads/water/old regions kept as obstacles','no newPOI/business/navigation edge']}
e.write(B/'009-derived-plan.json',derived);e.write(B/'geometry-and-door-report.json',checks);e.write(B/'native-provenance-verified.json',provenance);e.write(B/'read-only-protection.json',readprotect)
print('Derived',len(derived['buildings']),'buildings +',len(fixtures),'limited fixtures,',len(derived['groundSurfaces']),'grounds; originalSHA',PS,'derivedSHA',e.sha(B/'009-derived-plan.json'))
