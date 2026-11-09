#!/usr/bin/env python3
"""Approved007 props ->006 library/TMJ incremental only. Never resets existing map."""
import sys
sys.dont_write_bytecode=True
import math,copy,shutil,ast
from pathlib import Path
import neighborhood_export as e
I,R,lib=e.I,e.R,e.lib;P=R.parent/'revision-007';ids=['P01','P10','P03','P05']
if any(o.get('name','').startswith('N2-life-') for l in e.read(e.M)['layers'] if l['type']=='objectgroup' for o in l['objects']):raise ValueError('Life props already exist; preserve hand edits and use export, never rerun initial placement')
ns={'math':math};tree=ast.parse((R/'planning/build_plan.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['inside','ps','cross','ss','edges','pp','pl']],type_ignores=[]),'pure-readonly-geometry','exec'),ns)
pp,pl,inside=ns['pp'],ns['pl'],ns['inside'];base=e.read(I/'runtime-subset-plan.json');u=[.23417355683909316,-.9721948082958105];n=[.9721948082958105,.23417355683909316];proj=base['projection']
def pr(q):return [q[0]*proj['axisX'][k]+q[1]*proj['axisY'][k]for k in (0,1)]
lu,ln=math.hypot(*pr(u)),math.hypot(*pr(n));catalog={p['id']:p for p in e.read(P/'catalog.json')['props']};before={str(f.resolve()):e.sha(f)for aid in ids for f in (P/f'native/{aid}-001').iterdir()if f.is_file()};before[str((P/'catalog.json').resolve())]=e.sha(P/'catalog.json')
oldreport=I/'export-report-base-street.json'
if not oldreport.exists():e.write(oldreport,e.read(I/'export-report.json'))
libdoc=e.read(I/'asset-library.json');caldoc=e.read(I/'asset-calibration.json');checks=[];newcal=[]
controls={'P01':[[344,833],[512,1067],[906,830],[738,596]],'P10':[[280,930],[437,1081],[964,840],[807,689]],'P03':[[219,1021],[355,1123],[1039,783],[911,697]],'P05':[[368,904],[567,1056],[884,913],[692,845]]}
for aid in ids:
 root=P/f'native/{aid}-001';raw=root/f'{aid}-v1.png';rt=root/f'{aid}-runtime-280.png';prov=e.read(root/'provenance.json');der=e.read(rt.with_suffix('.runtime.json'));source=Path(prov['toolSourceAbsolutePath']);assert e.sha(source)==e.sha(raw)==der['sourceSHA256'];assert e.sha(rt)==der['sha256'];dims=catalog[aid]['dimensions'];co=controls[aid];anchor=[sum(p[k]for p in co)/4 for k in (0,1)]
 if aid=='P05':ppu=math.dist(co[0],co[2])/(dims[0]*lu);method='manual circular leg spread maximum span / candidate projected diameter; not whole PNG base'
 else:
  lens=[math.dist(co[1],co[2]),math.dist(co[0],co[1])];targets=[dims[0]*lu,dims[1]*ln];ppu=sum(a*b for a,b in zip(lens,targets))/sum(v*v for v in targets);method='manual baseplate/leg-foot perimeter, one positive scalar least-squares against catalog candidate frontage/depth'
 x,y,x2,y2=der['cropBox'];world=[(x2-x)/ppu,(y2-y)/ppu];uv=[(anchor[0]-x)/(x2-x),(anchor[1]-y)/(y2-y)];ca={'id':aid,'status':'hand-ground-candidate-not-registration-ready','sourceNativeSize':der['sourceSize'],'sourceNativeSHA256':e.sha(raw),'catalogDimensionsCandidate':dims,'groundContactPixelsManual':co,'hiddenContactInference':aid in ['P01','P10'],'manualPixelUncertainty':20,'nativePixelsPerUnit':ppu,'anchorPixel':anchor,'anchorUV':uv,'worldSizeUnits':world,'cropBox':der['cropBox'],'method':method,'availability':'library-only-await-table-context'if aid=='P05'else'public-courtyard-comparison-candidate'};newcal.append(ca);a={'id':aid,'kind':'prop','file':rt.name,'sha256':e.sha(rt),'nativeSize':der['runtimeSize'],'nativePixelsPerUnit':1,'worldSizeUnits':world,'anchorUV':uv,'runtimeDerivation':der,'projectionId':proj['id'],'availability':ca['availability']};libdoc['assets']=[v for v in libdoc['assets']if v['id']!=aid]+[a];caldoc['assets']=[v for v in caldoc['assets']if v['id']!=aid]+[ca];shutil.copyfile(rt,lib.A/rt.name);checks.append({'id':aid,'nativeSHA256':e.sha(raw),'toolSourceSHA256':e.sha(source),'runtimeSHA256':e.sha(rt),'source':str(source),'runtimeSize':der['runtimeSize']})
e.write(I/'asset-library.json',libdoc);e.write(I/'asset-calibration.json',caldoc);e.write(I/'prop-calibration.json',{'assets':newcal,'sourceChecks':checks,'readOnly007Snapshot':before,'excluded':['P04-all-unapproved'],'P05Placement':'library only, wait for admitted matching table/context'})
# Incremental map changes, all original objects retained verbatim.
doc=e.read(e.M);pre=e.sha(e.M);oldobj={o['name']:copy.deepcopy(o)for l in doc['layers']if l['type']=='objectgroup'for o in l['objects']};obstacles=[x['nativeGroundPolygonMap']for x in e.read(I/'placement-screening.json')['rows']if x.get('decision')=='retained'];obstacles += [x['footprintPolygonMap']for x in e.read(lib.OLD/'planning/mixed-street-layout.json')['buildings']];walks=[s['polygonMap']for s in base['groundSurfaces']if '-walk-'in s['id']];doors=[b['entryMap']for b in base['buildings']]+[b['entryAnchorMap']for b in e.read(lib.OLD/'planning/mixed-street-layout.json')['buildings']];zones=[s['polygonMap']for s in base['groundSurfaces']if s['id']in ['N2-court','N2-03-B02-parcel','N2-04-B04-parcel']];city=e.read(e.read(R/'planning/source-context.json')['source']);nodes={x['id']:[x['x'],x['y']]for x in city['nodes']};roads=[(r['width'],nodes[a],nodes[b])for r in city['roads']for a,b in zip(r['nodes'],r['nodes'][1:])if all(-1700<q[0]<-1550 and 80<q[1]<150 for q in [nodes[a],nodes[b]])];fixtures=[f for f in base['fixtures']if f['persistentId'].startswith('N2-')];park=[s['polygonMap']for s in base['parkingSpaces']];placed=[];records=[]
def rect(center,w,d):return [[center[k]+t*u[k]+z*n[k]for k in (0,1)]for t,z in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
def safecandidate(center,aid):
 dims=catalog[aid]['dimensions'];poly=rect(center,dims[0],dims[1]);gaps={}
 if not any(all(inside(p,z)for p in poly)for z in zones):return None
 gaps['building']=min(pp(poly,q)for q in obstacles);gaps['walk']=min(pp(poly,q)for q in walks);gaps['door']=min(min(ns['ps'](p,a,b)for a,b in ns['edges'](poly))if not inside(p,poly)else 0 for p in doors);gaps['road']=min(pl(poly,a,b)-w/2 for w,a,b in roads);gaps['parking']=min(pp(poly,q)for q in park);gaps['fixture']=min([min(ns['ps'](f['anchorMap'],a,b)for a,b in ns['edges'](poly))-(.9 if f['libraryAssetId'].startswith('T')else.3)for f in fixtures]or[999]);gaps['prop']=min([pp(poly,q)for q in placed]or[999])
 if min(gaps['building'],gaps['walk'],gaps['parking'],gaps['fixture'],gaps['prop'])<.35 or gaps['door']<1.8 or gaps['road']<.4:return None
 return poly,gaps
# Search within existing public parcel/court only, prefer B04 public forecourt.
for aid in ['P03','P01','P10']:
 pid='N2-life-'+aid
 if pid in oldobj:continue
 preferred={'P03':[-1641,108],'P01':[-1642.5,114],'P10':[-1641,102]}[aid];candidates=[]
 for ix in range(40):
  for iy in range(72):
   c=[-1658+ix*.5,94+iy*.5];result=safecandidate(c,aid)
   if result:candidates.append((math.dist(c,preferred),c,*result))
 if not candidates:records.append({'id':aid,'decision':'library-only-no-safe-public-space'});continue
 _,center,poly,gaps=min(candidates,key=lambda q:q[0]);placed.append(poly);a=next(a for a in libdoc['assets']if a['id']==aid);ts=doc['tilesets'][0];tileid=max(t['id']for t in ts['tiles'])+1;ts['tiles'].append({'id':tileid,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':e.properties({'assetId':aid})});ts['tilecount']=len(ts['tiles']);w,h=[q*16 for q in a['worldSizeUnits']];u0,v0=a['anchorUV'];x,y=e.project(center);oid=max(o['id']for l in doc['layers']if l['type']=='objectgroup'for o in l['objects'])+1;obj={'id':oid,'name':pid,'type':'sprite','gid':ts['firstgid']+tileid,'x':x-u0*w,'y':y+(1-v0)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties({'persistentId':pid,'assetId':aid,'context':'public/civic courtyard','manualCalibration':True})};layer=next(l for l in doc['layers']if l['id']==2);layer['objects'].append(obj);records.append({'id':aid,'persistentId':pid,'decision':'placed-candidate','anchorMap':center,'catalogFootprintPolygonMap':poly,'clearanceMetres':gaps,'uniformScale':1})
# Depth insertion preserves all pre-existing relative order; no reset or overwrite of original objects.
by={a['id']:a for a in libdoc['assets']};layer=next(l for l in doc['layers']if l['id']==2);newobjs=[o for o in layer['objects']if o['name']not in oldobj];layer['objects']=[o for o in layer['objects']if o['name']in oldobj]
def depth(o):
 a=by[e.props(o)['assetId']];return o['y']-(1-a['anchorUV'][1])*o['height']
for o in sorted(newobjs,key=depth):
 pos=next((k for k,v in enumerate(layer['objects'])if depth(v)>depth(o)),len(layer['objects']));layer['objects'].insert(pos,o)
for l in doc['layers']:
 if l['type']=='objectgroup':
  for o in l['objects']:
   if o['name']in oldobj:assert o==oldobj[o['name']]
doc['nextobjectid']=max(o['id']for l in doc['layers']if l['type']=='objectgroup'for o in l['objects'])+1;e.write(e.M,doc);e.write(I/'life-props-placement.json',{'mapBeforeSHA256':pre,'mapAfterSHA256':e.sha(e.M),'records':records,'originalObjectsUnchanged':len(oldobj),'basePlanSHAUnchanged':e.sha(I/'runtime-subset-plan.json'),'source007Unchanged':all(e.sha(p)==h for p,h in before.items()),'noNavigationOrBusinessChange':True});e.export();print(records)
