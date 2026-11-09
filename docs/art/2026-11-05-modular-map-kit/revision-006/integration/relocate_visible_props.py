#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import math,ast,copy
from pathlib import Path
import neighborhood_export as e
I=e.I;ns={'math':math};tree=ast.parse((e.R/'planning/build_plan.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['inside','ps','cross','ss','edges','pp','pl']],type_ignores=[]),'pure-geometry','exec'),ns)
u=[.23417355683909316,-.9721948082958105];n=[.9721948082958105,.23417355683909316]
def rect(c,w,d):return [[c[k]+t*u[k]+z*n[k]for k in (0,1)]for t,z in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
doc=e.read(e.M);assets={a['id']:a for a in e.read(I/'asset-library.json')['assets']};cal={a['id']:a for a in e.read(I/'prop-calibration.json')['assets']};base=e.read(I/'runtime-subset-plan.json');public=rect([-1641,118],4.8,3.8);ground=next(l for l in doc['layers']if l['id']==1);pid='N2-public-rest-paving';q=[e.project(p)for p in public];x,y=q[0]
if not any(o['name']==pid for o in ground['objects']):ground['objects'].append({'id':doc['nextobjectid'],'name':pid,'type':'ground-surface','x':x,'y':y,'polygon':[{'x':a-x,'y':b-y}for a,b in q],'properties':e.properties({'surfaceAssetId':'S01-paving','purpose':'small public rest forecourt; no new road/navigation/POI'})});doc['nextobjectid']+=1
records=e.read(I/'life-props-placement.json');obs=[x['nativeGroundPolygonMap']for x in e.read(I/'placement-screening.json')['rows']if x.get('decision')=='retained']+[x['footprintPolygonMap']for x in e.read(e.lib.OLD/'planning/mixed-street-layout.json')['buildings']];ctx=e.read(e.R/'planning/source-context.json');src=[q for q in ctx['sourceBuildings']if q and min(p[0]for p in q)<-1600 and max(p[0]for p in q)>-1700 and min(p[1]for p in q)<150 and max(p[1]for p in q)>80];walks=[s['polygonMap']for s in base['groundSurfaces']if '-walk-'in s['id']];city=e.read(ctx['source']);nodes={n['id']:[n['x'],n['y']]for n in city['nodes']};roads=[(r['width'],nodes[a],nodes[b])for r in city['roads']for a,b in zip(r['nodes'],r['nodes'][1:])if all(-1700<q[0]<-1600 and 80<q[1]<150 for q in [nodes[a],nodes[b]])]
for aid,anchor in [('P03',[-1641.5,118.0]),('P10',[-1640.0,116.7])]:
 c=cal[aid];a=assets[aid];px=e.project(anchor);poly=[e.unproject([px[k]+(p[k]-c['anchorPixel'][k])/c['nativePixelsPerUnit']*16 for k in (0,1)])for p in c['groundContactPixelsManual']];gaps={'nativeBuilding':min(ns['pp'](poly,q)for q in obs),'sourceBuilding':min(ns['pp'](poly,q)for q in src),'walk':min(ns['pp'](poly,q)for q in walks),'road':min(ns['pl'](poly,a,b)-w/2 for w,a,b in roads)};assert all(v>.35 for v in gaps.values()),gaps;assert all(ns['inside'](p,public)for p in poly)
 o=next(o for l in doc['layers']if l['type']=='objectgroup'for o in l['objects']if o['name']=='N2-life-'+aid);o['x']=px[0]-a['anchorUV'][0]*o['width'];o['y']=px[1]+(1-a['anchorUV'][1])*o['height'];row=next(x for x in records['records']if x['id']==aid);row.update({'previousAnchorMap':row['anchorMap'],'anchorMap':anchor,'actualManualGroundPolygonMap':poly,'finalClearanceMetres':gaps,'relocationReason':'first Cocos screenshot showed correct rear-side occlusion; move prop only into clear visible public rest forecourt, no building move'});print(aid,gaps)
# Sort only newly added props into immutable base order.
l=next(l for l in doc['layers']if l['id']==2);life=[o for o in l['objects']if o['name'].startswith('N2-life-')];l['objects']=[o for o in l['objects']if not o['name'].startswith('N2-life-')]
def depth(o):return o['y']-(1-assets[e.props(o)['assetId']]['anchorUV'][1])*o['height']
for o in sorted(life,key=depth):l['objects'].insert(next((k for k,p in enumerate(l['objects'])if depth(p)>depth(o)),len(l['objects'])),o)
records['additionalPublicGround']={'id':pid,'polygonMap':public,'role':'controlled existing paving material, no original road/plan mutation','areaUnits2':4.8*3.8};e.write(I/'life-props-placement.json',records);e.write(e.M,doc);e.export()
