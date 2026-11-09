#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import math,ast,copy
from pathlib import Path
import neighborhood_export as e
I=e.I;doc=e.read(e.M);base=e.read(I/'runtime-subset-plan.json');assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']};record=e.read(I/'prop-corners-placement.json');ns={'math':math};t=ast.parse((e.R/'planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in t.body if isinstance(x,ast.FunctionDef)and x.name in ['inside','ps','cross','ss','edges','pp','pl']],type_ignores=[]),'pure-geometry','exec'),ns)
u=[.23417355683909316,-.9721948082958105];n=[.9721948082958105,.23417355683909316]
def rect(c,w,d):return [[c[k]+t*u[k]+z*n[k]for k in (0,1)]for t,z in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
obs=[x['nativeGroundPolygonMap']for x in e.read(I/'placement-screening.json')['rows']if x.get('decision')=='retained']+[x['footprintPolygonMap']for x in e.read(e.lib.OLD/'planning/mixed-street-layout.json')['buildings']];walks=[s['polygonMap']for s in base['groundSurfaces']if '-walk-'in s['id']]+[s['polygonMap']for s in record['newGroundSurfaces']];occ=[rect(r['anchorMap'],*{'P03':[2,.65],'P01':[.65,.4],'P10':[1.1,.65]}[r['id']])for r in e.read(I/'life-props-placement.json')['records']];occ +=[r['footprintMap']for r in record['instances']if r.get('decision')=='placed-comparison'and r['assetId']in ['P06','P07']];rest=e.read(I/'life-props-placement.json')['additionalPublicGround']['polygonMap'];placed=[];l=next(l for l in doc['layers']if l['id']==2)
for aid,pid,tv,nv,d in [('P04-v2','N2-rest-table',-1.,.95,1.),('P05','N2-rest-stool-a',-1.9,.95,.42),('P05','N2-rest-stool-b',-.1,.95,.42)]:
 c=[-1641+tv*u[0]+nv*n[0],118+tv*u[1]+nv*n[1]];poly=rect(c,d,d);gaps={'building':min(ns['pp'](poly,q)for q in obs),'walk':min(ns['pp'](poly,q)for q in walks),'otherProp':min(ns['pp'](poly,q)for q in occ+placed)};assert min(gaps.values())>.16,(pid,gaps);assert all(ns['inside'](p,rest)for p in poly);a=assets[aid];o=next((o for o in l['objects']if o['name']==pid),None)
 if o is None:
  ts=doc['tilesets'][0];tile=next((t for t in ts['tiles']if e.props(t)['assetId']==aid),None)
  if tile is None:
   tile={'id':max(t['id']for t in ts['tiles'])+1,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':e.properties({'assetId':aid})};ts['tiles'].append(tile);ts['tilecount']=len(ts['tiles'])
  w,h=[v*16 for v in a['worldSizeUnits']];o={'id':doc['nextobjectid'],'name':pid,'type':'sprite','gid':ts['firstgid']+tile['id'],'width':w,'height':h,'rotation':0,'visible':True,'properties':e.properties({'persistentId':pid,'assetId':aid,'context':'small-table-static-comparison'})};doc['nextobjectid']+=1;l['objects'].append(o)
 x,y=e.project(c);au,av=a['anchorUV'];o.update({'x':x-au*o['width'],'y':y+(1-av)*o['height']});placed.append(poly);record['instances']=[r for r in record['instances']if r['id']!=pid];record['instances'].append({'id':pid,'assetId':aid,'decision':'placed-comparison','anchorMap':c,'footprintMap':poly,'clearance':gaps,'uniformScale':1,'risk':'P04 pedestal perspective remains candidate'if aid=='P04-v2'else'P05 paired with admitted v2 table'});print(pid,c,gaps)
# Only new furnishing group inserted by contact depth; existing39 relative order stays intact.
newids={'N2-rest-table','N2-rest-stool-a','N2-rest-stool-b','N2-rest-short-fence'};new=[o for o in l['objects']if o['name']in newids];l['objects']=[o for o in l['objects']if o['name']not in newids]
def depth(o):return o['y']-(1-assets[e.props(o)['assetId']]['anchorUV'][1])*o['height']
for o in sorted(new,key=depth):l['objects'].insert(next((k for k,p in enumerate(l['objects'])if depth(p)>depth(o)),len(l['objects'])),o)
e.write(e.M,doc);e.write(I/'prop-corners-placement.json',record);e.export()
