"""Build source-coordinate seam proof in SVG; native artwork remains untouched."""
from pathlib import Path
import json,math,html
BASE=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
p=json.loads((BASE/'geometry/twentyfive-regions.json').read_text());m=json.loads((BASE/'review-manifest.json').read_text());a=json.loads((BASE/'assembly/placement-manifest.json').read_text());city=json.loads((ROOT/'delivery-game/assets/resources/map-sample/city.json').read_text());q=math.sqrt(.5);s=math.sin(math.radians(62.5))
def proj(pt):return [(pt[0]-pt[1])*q,(pt[0]+pt[1])*q*s]
# Sample includes the complete shared edge and enough plot context, not whole neighboring scenes.
world=[[-2680,150],[-2370,150],[-2370,875],[-2680,875]];ps=[proj(v) for v in world];lo=[min(v[i] for v in ps)-25 for i in [0,1]];span=max(max(v[i] for v in ps)-lo[i]+25 for i in [0,1]);box=[lo[0]-(span-(max(v[0] for v in ps)-lo[0]+25))/2,lo[1]-(span-(max(v[1] for v in ps)-lo[1]+25))/2,span,span]
images=[];defs=[]
for it in m['items']:
 spec=next(z for z in a['regions'] if z['id']==it['regionId']);rect=spec['imageBoundsProjected'];poly=spec['corePolygonProjected'];pts=' '.join(','.join(map(str,v)) for v in poly);defs.append(f'<clipPath id="{spec["id"]}"><polygon points="{pts}"/></clipPath>');images.append(f'<g clip-path="url(#{spec["id"]})"><image href="../../{it["file"]}" x="{rect[0]}" y="{rect[1]}" width="{rect[2]-rect[0]}" height="{rect[3]-rect[1]}"/></g>')
nodes={str(n['id']):[n['x'],n['y']] for n in city['nodes']};water=[];roads=[]
for ar in city['areas']:
 if ar['kind']=='water':water.append('<polygon points="'+' '.join(','.join(map(str,proj(v))) for v in ar['points'])+'" fill="#81b3c8"/>')
for wa in city['waterways']:water.append('<polyline points="'+' '.join(','.join(map(str,proj(v))) for v in wa)+'" fill="none" stroke="#81b3c8" stroke-width="5"/>')
for road in city['roads']:
 pts=' '.join(','.join(map(str,proj(nodes[str(n)]))) for n in road['nodes']);roads.append(f'<polyline points="{pts}" fill="none" stroke="#b7b8b3" stroke-width="{road.get("width",5)+3}" stroke-linejoin="round"/><polyline points="{pts}" fill="none" stroke="#5c6367" stroke-width="{road.get("width",5)}" stroke-linejoin="round"/>')
base=f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="{" ".join(map(str,box))}">';before=base+'<defs>'+''.join(defs)+'</defs><rect x="-10000" y="-10000" width="20000" height="20000" fill="#ddd9d3"/>'+''.join(images)+'</svg>'
linepts=' '.join(','.join(map(str,proj(v))) for v in [[-2522.734,150],[-2522.734,875]])
source=base+'<rect x="-10000" y="-10000" width="20000" height="20000" fill="#e4e6dc"/>'+''.join(water)+''.join(roads)+'</svg>'
for name,svg in [('before',before),('source-structure',source)]:
 (OUT/(name+'.svg')).write_text(svg);(OUT/(name+'.html')).write_text('<!doctype html><style>html,body{margin:0;width:1000px;height:1000px;overflow:hidden;background:#fff}svg{display:block}</style>'+svg)
(OUT/'patch-coordinate.json').write_text(json.dumps({'viewBoxProjected':box,'rasterSize':[1000,1000],'sourceSampleWorldPolygon':world,'semanticSeamX':-2522.734,'registration':'nominal-patch-frame;not-ready'},indent=2)+'\n')
print(json.dumps({'box':box,'sourceRoadCount':len(city['roads']),'purpose':'joint local seam proof;source roads unchanged'}))
