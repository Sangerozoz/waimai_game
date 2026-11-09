#!/usr/bin/env python3
"""Actual exported polygon static readback; not engine tests."""
import ast,json,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;K=O.parent.parent
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=read(O/'first-expansion-batch.json');c=read(p['source']['cityPath']);frozen=sha(O/'first-expansion-batch.json');nodes={n['id']:[n['x'],n['y']] for n in c['nodes']};P=p['projection'];u=[.23417355683909316,-.9721948082958105];n=[-u[1],u[0]]
names={'add','mul','inside','ps','cross','ss','edges','pp','pl'};t=ast.parse((K/'revision-006/planning/build_plan.py').read_text());exec(compile(ast.Module(body=[x for x in t.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),'<geometry>','exec'))
def bbox(q):return [min(x[0] for x in q),min(x[1] for x in q),max(x[0] for x in q),max(x[1] for x in q)]
def close(a,b,r=50):return a[0]-r<b[2] and a[2]+r>b[0] and a[1]-r<b[3] and a[3]+r>b[1]
roads=[(r,a,b) for r in c['roads'] for a,b in zip(r['nodes'],r['nodes'][1:])];results=[]
for b in p['buildings']:
 owner=b['visualReplacementOf']['sourceIndex'];bp=bbox(b['footprintPolygonMap']+b['doorApproach']['polygonMap']);q=[]
 for name,poly in [('body',b['footprintPolygonMap']),('walk',b['doorApproach']['polygonMap'])]:
  road=min(pl(poly,nodes[a],nodes[d])-r['width']/2 for r,a,d in roads if close(bp,bbox([nodes[a],nodes[d]])))
  source=min(pp(poly,ob) for i,ob in enumerate(c['buildings']) if i!=owner and close(bp,bbox(ob)))
  water=min([pp(poly,a['points']) for a in c['areas'] if a.get('kind')=='water' and len(a.get('points',[]))>=3 and close(bp,bbox(a['points']))]+[pl(poly,a,d)-3 for w in c['waterways'] for a,d in zip(w,w[1:]) if close(bp,bbox([a,d]))]+[9999])
  poi=min(0 if inside(nodes[v['node']],poly) else min(ps(nodes[v['node']],a,d) for a,d in edges(poly)) for v in c['pois'] if v.get('node') in nodes)
  protected=min(pp(poly,ob) for ob in p['protectedExisting']['regionProtectionPolygonsMap'])
  assert road>=-.001 and source>=.15 and water>=5 and poi>=6 and protected>=8,(b['id'],name,road,source,water,poi,protected)
  q.append({'polygon':name,'roadEdgeMetres':road,'otherSourceBuildingMetres':source,'waterSafetyMetres':water,'businessEntranceMetres':poi,'protected57RegionMetres':protected})
 results.append({'id':b['id'],'visualReplacementSourceIndex':owner,'checks':q})
for r in p['roads']:
 original=next(x for x in c['roads'] if x['id']==r['id']);assert r['sourceNodeIds']==original['nodes'] and r['nodes']==[nodes[n] for n in original['nodes']]
assert sha(O/'first-expansion-batch.json')==frozen
for f,h in read(O/'protected-inputs.json').items():assert sha(f)==h
(O/'seed-exported-polygon-verification.json').write_text(json.dumps({'seedSHA256':frozen,'allExactRoadNodeSequencesWidthsDirectionsRetained':True,'allProtectedInputsSHAUnchanged':True,'exportedBodyAndWalkPolygons':results,'ownDoorstepLevels':'manual native door/ground rim uncertainty not certified; pipeline admission required'},ensure_ascii=False,indent=2)+'\n')
print('STATIC READBACK',len(results),'buildings; source/road/water/POI/protected clear; seed unchanged')
