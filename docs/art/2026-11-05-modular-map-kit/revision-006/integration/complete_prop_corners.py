#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import math,ast,copy,shutil
from pathlib import Path
import neighborhood_export as e
I,R,lib=e.I,e.R,e.lib;P=R.parent/'revision-007';admission=P/'review/prop-admission.json';AD='be089e48d0d5852f78bd21e9d7fdc958d812282bbca9639c912df47f784699bb';assert e.sha(admission)==AD
if (I/'prop-corners-placement.json').exists():raise ValueError('Already applied; preserve manual Tiled edits and export only')
ns={'math':math};t=ast.parse((R/'planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in t.body if isinstance(x,ast.FunctionDef)and x.name in ['inside','ps','cross','ss','edges','pp','pl']],type_ignores=[]),'pure-geometry','exec'),ns);pp,pl,inside=ns['pp'],ns['pl'],ns['inside']
u=[.23417355683909316,-.9721948082958105];n=[.9721948082958105,.23417355683909316];az=.4617486132350339
base=e.read(I/'runtime-subset-plan.json');ctx=e.read(R/'planning/source-context.json');city=e.read(ctx['source']);nodes={x['id']:[x['x'],x['y']]for x in city['nodes']};dims={x['id']:x['dimensions']for x in e.read(P/'catalog.json')['props']};libdoc=e.read(I/'asset-library.json');caldoc=e.read(I/'asset-calibration.json');before={str(admission.resolve()):AD};checks=[]
lu=math.hypot(*[u[0]*base['projection']['axisX'][k]+u[1]*base['projection']['axisY'][k]for k in (0,1)]);ln=math.hypot(*[n[0]*base['projection']['axisX'][k]+n[1]*base['projection']['axisY'][k]for k in (0,1)])
controls={'P02':[[310,1045],[460,1170],[786,1170],[925,1045]],'P04-v2':[[423,1030],[625,1178],[834,1030],[625,893]],'P06':[[270,955],[1260,510]],'P07':[[400,595],[840,1085]],'P08':[[208,692],[444,1033],[1067,682],[819,345]]}
for aid,folder,stem in [('P02','P02-001','P02'),('P04-v2','P04-002','P04-v2'),('P06','P06-001','P06'),('P07','P07-001','P07'),('P08','P08-001','P08')]:
 root=P/'native'/folder;raw=root/(stem+'.png'if aid=='P04-v2'else stem+'-v1.png');rt=root/(stem+'-runtime-280.png');prov=e.read(root/'provenance.json');src=Path(prov.get('toolSourceAbsolutePath',prov.get('toolSource')));der=e.read(rt.with_suffix('.runtime.json'));assert e.sha(src)==e.sha(raw)==der['sourceSHA256'];assert e.sha(rt)==der['sha256'];ad=next(x for x in e.read(admission)['items']if x['id']==('P04'if aid=='P04-v2'else aid));assert ad['nativeSHA256']==e.sha(raw);co=controls[aid];anchor=[sum(q[k]for q in co)/len(co)for k in (0,1)];d=dims['P04'if aid=='P04-v2'else aid]
 if aid=='P04-v2':
  anchor=[625,1034];ppu=(740+468*(d[2]*az))/(1+(d[2]*az)**2);method='manual tabletop diameter740px and top-centre/base vertical offset468px; single scalar fit diameter1 and height0.75; pedestal perspective remains approximate'
 elif aid in ['P06','P07']:
  rise=350 if aid=='P06' else 395;ppu=rise/(d[2]*az);method='manual upright endpoint post rise / catalog1m height / projectionZ; ground span separately reported, not stretched to force catalog2.5m length'
 elif aid=='P08':
  lens=[math.dist(co[1],co[2]),math.dist(co[0],co[1])];tg=[d[0]*lu,d[1]*ln];ppu=sum(a*b for a,b in zip(lens,tg))/sum(a*a for a in tg);method='manual four timber ground rim corners, single scalar fit2.6x1.6 candidate bed; alpha frame not used as footprint'
 else:ppu=615/1.2;method='manual four visible/inferred leg contacts, candidate1.2m maximum round foot spread; not a surveyed tank'
 x,y,x2,y2=der['cropBox'];world=[(x2-x)/ppu,(y2-y)/ppu];uv=[(anchor[0]-x)/(x2-x),(anchor[1]-y)/(y2-y)];ca={'id':aid,'nativePixelsPerUnit':ppu,'sourceNativeSHA256':e.sha(raw),'sourceNativeSize':der['sourceSize'],'groundContactPixelsManual':co,'anchorPixel':anchor,'anchorUV':uv,'worldSizeUnits':world,'cropBox':der['cropBox'],'catalogDimensionsCandidate':d,'method':method,'status':'manual-candidate-no-registration-or-user-acceptance','availability':'library-only-no-workshop-context'if aid=='P02'else'limited-context-comparison'}
 if aid in ['P06','P07']:ca['candidateGroundSpanFromHeightScale']=math.dist(*co)/ppu/(lu if aid=='P06'else ln);ca['risk']='native two directions have different picket counts and inferred length; independent short sections only, no seamless standard kit'
 if aid=='P04-v2':ca['risk']='central column longer / base flatter than exact target; grain on circular top is not alignment criterion'
 if aid=='P08':ca['risk']='fine soil detail and colour fringe need actual-scale scene review'
 libdoc['assets'].append({'id':aid,'kind':'prop','file':rt.name,'sha256':e.sha(rt),'nativeSize':der['runtimeSize'],'nativePixelsPerUnit':1,'anchorUV':uv,'worldSizeUnits':world,'runtimeDerivation':der,'availability':ca['availability'],'projectionId':base['projection']['id']});caldoc['assets'].append(ca);shutil.copyfile(rt,lib.A/rt.name);checks.append({'id':aid,'nativeSHA256':e.sha(raw),'toolSHA256':e.sha(src),'runtimeSHA256':e.sha(rt)})
 for f in root.iterdir():
  if f.is_file():before[str(f.resolve())]=e.sha(f)
e.write(I/'asset-library.json',libdoc);e.write(I/'asset-calibration.json',caldoc);e.write(I/'prop-corners-calibration.json',{'parentAdmissionSHA256':AD,'sourceChecks':checks,'readOnlySnapshot':before,'assets':[a for a in caldoc['assets']if a['id']in controls],'excluded':['P04-v1-permanent','P09-not-current-core-placement','B10-v1/v2']})
# No reset: retain every current object, only append.
doc=e.read(e.M);original={o['name']:copy.deepcopy(o)for l in doc['layers']if l['type']=='objectgroup'for o in l['objects']};assets={a['id']:a for a in libdoc['assets']};cal={a['id']:a for a in caldoc['assets']};records=[];surfaces=[];added=[]
obs=[x['nativeGroundPolygonMap']for x in e.read(I/'placement-screening.json')['rows']if x.get('decision')=='retained']+[x['footprintPolygonMap']for x in e.read(lib.OLD/'planning/mixed-street-layout.json')['buildings']];src=[q for q in ctx['sourceBuildings']if q and min(p[0]for p in q)<-1600 and max(p[0]for p in q)>-1700 and min(p[1]for p in q)<230 and max(p[1]for p in q)>80];roads=[(r['width'],nodes[a],nodes[b])for r in city['roads']for a,b in zip(r['nodes'],r['nodes'][1:])if all(-1720<q[0]<-1590 and 70<q[1]<240 for q in [nodes[a],nodes[b]])];walks=[s['polygonMap']for s in base['groundSurfaces']if '-walk-'in s['id']];waters=[q['points'] if isinstance(q,dict) else q for q in ctx['waterAreas']];waterlines=[(a,b)for q in ctx['waterways']if isinstance(q,list)for a,b in zip(q,q[1:])if isinstance(a,list)];business=[nodes[x['node']]for x in ctx['pois']if x.get('node')in nodes];door=[b['entryMap']for b in base['buildings']];fixtures=[(f['anchorMap'],.9 if f['libraryAssetId'].startswith('T')else.3)for f in base['fixtures']];parking=[s['polygonMap']for s in base['parkingSpaces']]
def rect(c,w,d):return [[c[k]+a*u[k]+b*n[k]for k in (0,1)]for a,b in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
def pointgap(p,q):return 0 if inside(p,q)else min(ns['ps'](p,a,b)for a,b in ns['edges'](q))
def gaps(poly,include_walk=True):
 out={'building':min(pp(poly,q)for q in obs),'sourceBuilding':min(pp(poly,q)for q in src),'road':min(pl(poly,a,b)-w/2 for w,a,b in roads),'door':min(pointgap(p,poly)for p in door),'business':min([pointgap(p,poly)for p in business]or[999]),'fixture':min([pointgap(p,poly)-rad for p,rad in fixtures]or[999]),'parking':min([pp(poly,q)for q in parking]or[999]),'waterArea':min([pp(poly,q)for q in waters]or[999]),'waterLine':min([pl(poly,a,b)-3 for a,b in waterlines]or[999])}
 if include_walk:out['walk']=min(pp(poly,q)for q in walks)
 return out
# Existing props are obstacles for new furniture, with actual base/usable furniture envelope.
occupied=[]
for row in e.read(I/'life-props-placement.json')['records']:
 aid=row['id'];d=dims[aid];occupied.append(rect(row['anchorMap'],d[0],d[1]))
def safe(poly,walk=True):
 gs=gaps(poly,walk);ok=all(v>.2 for k,v in gs.items()if k not in ['door','business'])and gs['door']>1.5 and gs['business']>6
 return ok,gs

def add_surface(pid,poly,mat):
 oid=doc['nextobjectid'];doc['nextobjectid']+=1;q=[e.project(p)for p in poly];x,y=q[0];obj={'id':oid,'name':pid,'type':'ground-surface','x':x,'y':y,'polygon':[{'x':a-x,'y':b-y}for a,b in q],'properties':e.properties({'surfaceAssetId':mat})};next(l for l in doc['layers']if l['id']==1)['objects'].append(obj);surfaces.append({'id':pid,'polygonMap':poly,'materialId':mat})
def add_prop(aid,pid,anchor,poly):
 ok,gs=safe(poly)
 if not ok or any(pp(poly,q)<.16 for q in occupied):records.append({'id':pid,'assetId':aid,'decision':'not-placed-clearance','gaps':gs});return False
 a=assets[aid];ts=doc['tilesets'][0];tile=next((t for t in ts['tiles']if e.props(t)['assetId']==aid),None)
 if tile is None:
  tid=max(t['id']for t in ts['tiles'])+1;tile={'id':tid,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':e.properties({'assetId':aid})};ts['tiles'].append(tile);ts['tilecount']=len(ts['tiles'])
 x,y=e.project(anchor);w,h=[v*16 for v in a['worldSizeUnits']];au,av=a['anchorUV'];o={'id':doc['nextobjectid'],'name':pid,'type':'sprite','gid':ts['firstgid']+tile['id'],'x':x-au*w,'y':y+(1-av)*h,'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties({'assetId':aid,'persistentId':pid,'contextualComparison':True})};doc['nextobjectid']+=1;added.append(o);occupied.append(poly);records.append({'id':pid,'assetId':aid,'decision':'placed-comparison','anchorMap':anchor,'footprintMap':poly,'gaps':gs,'uniformScale':1});return True
# Connect public rest paving to existing1.5m path. Do not modify that path or call this a road.
rest=e.read(I/'life-props-placement.json')['additionalPublicGround']['polygonMap'];parent=e.read(R/'planning/next-neighborhood-plan-access-v2.json');walk=next(w for w in parent['pedestrianConnections']if w['buildingId']=='N2-04-B04');candidates=[]
for j in range(len(rest)):
 a,b=rest[j],rest[(j+1)%len(rest)]
 for frac in [.2,.4,.6,.8]:
  start=[a[k]+frac*(b[k]-a[k])for k in (0,1)]
  for a2,b2 in zip(walk['centrelineMap'],walk['centrelineMap'][1:]):
   for t in [.2,.4,.6,.8]:
    end=[a2[k]+t*(b2[k]-a2[k])for k in (0,1)];dx,dy=end[0]-start[0],end[1]-start[1];length=math.hypot(dx,dy);nx,ny=-dy/length*.6,dx/length*.6;poly=[[start[0]+nx,start[1]+ny],[end[0]+nx,end[1]+ny],[end[0]-nx,end[1]-ny],[start[0]-nx,start[1]-ny]];ok,gs=safe(poly,False)
    if ok and all(pp(poly,q)>.25 for q in occupied):candidates.append((length,start,end,poly,gs))
if candidates:
 length,start,end,poly,gs=min(candidates,key=lambda x:x[0]);add_surface('N2-public-rest-connector',poly,'S01-paving');connection={'status':'connected-finite-paving','width':1.2,'length':length,'startMap':start,'endMap':end,'gaps':gs,'approvedWalkUnchanged':True,'navigationEdgesAdded':0}
else:connection={'status':'unresolved-no-safe-connector','approvedWalkUnchanged':True}
# One small table with two independently placed stools within the existing rest pad.
for aid,pid,c,d in [('P04-v2','N2-rest-table',[-1641.0,119.1],[1.,1.]),('P05','N2-rest-stool-a',[-1641.8,119.2],[.42,.42]),('P05','N2-rest-stool-b',[-1640.2,119.0],[.42,.42])]:
 poly=rect(c,*d)
 if all(inside(p,rest)for p in poly):add_prop(aid,pid,c,poly)
 else:records.append({'id':pid,'assetId':aid,'decision':'not-placed-outside-rest-pad'})
# Independent short fence, based on1m post height; do not force2.5m length or close repeat kit.
c=[-1643.1,119.0];span=cal['P06']['candidateGroundSpanFromHeightScale'];add_prop('P06','N2-rest-short-fence',c,rect(c,span,.16))
# One garden bed in residential N1 court. Search finite approved court only, not commercial frontage.
court=next(s['polygonMap']for s in base['groundSurfaces']if s['id']=='N1-court');found=None
for ix in range(18):
 for iy in range(25):
  c=[-1648+ix*.35,171+iy*.35];poly=rect(c,2.6,1.6);ok,gs=safe(poly)
  if ok and all(inside(p,court)for p in poly)and all(pp(poly,q)>.2 for q in occupied):found=(c,poly);break
 if found:break
if found:
 c,poly=found;add_prop('P08','N1-community-garden-bed',c,poly);c2=[c[k]+1.1*n[k]for k in (0,1)];span=cal['P07']['candidateGroundSpanFromHeightScale'];add_prop('P07','N1-garden-independent-fence',c2,rect(c2,.16,span))
else:records.append({'id':'P08','decision':'library-only-no-safe-residential-court-slot'})
# No reset: insert added sprites by depth while preserving every existing object's bytes and relative order.
l=next(l for l in doc['layers']if l['id']==2)
def depth(o):return o['y']-(1-assets[e.props(o)['assetId']]['anchorUV'][1])*o['height']
for o in sorted(added,key=depth):l['objects'].insert(next((k for k,p in enumerate(l['objects'])if depth(p)>depth(o)),len(l['objects'])),o)
for l in doc['layers']:
 if l['type']=='objectgroup':
  for o in l['objects']:
   if o['name']in original:assert o==original[o['name']]
e.write(e.M,doc);e.write(I/'prop-corners-placement.json',{'parentAdmissionSHA256':AD,'connection':connection,'instances':records,'newGroundSurfaces':surfaces,'existingObjectsUnchanged':len(original),'P02':'library-only-no-workshop-context','P09':'not-admitted-to-current-streets','P04v1':'permanent-excluded','007SourceSHAUnchanged':all(e.sha(p)==h for p,h in before.items())});e.export();print('connection',connection);print('props',[(x['id'],x['decision'])for x in records])
