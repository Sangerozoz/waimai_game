"""Source-space rectangular zone arithmetic only. No generated pixels or game state modified."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
planpath=ROOT/'docs/art/2026-11-04-county-twentyfive-region-plan/geometry/twentyfive-regions.json'
d=json.loads(planpath.read_text());z=d['zones']
def intersect(a,b):
 p={'minX':max(a['minX'],b['minX']),'maxX':min(a['maxX'],b['maxX']),'minY':max(a['minY'],b['minY']),'maxY':min(a['maxY'],b['maxY'])}
 return p if p['maxX']>p['minX'] and p['maxY']>p['minY'] else None
def area(b):return max(0,b['maxX']-b['minX'])*max(0,b['maxY']-b['minY']) if b else 0
entries=[]
for r in d['regions']:
 obj={'id':r['id']}
 for scope,key in [('core','coreBoundsMetres'),('render','renderBoundsMetres')]:
  b=r[key];total=area(b);urban=area(intersect(b,z['urban']));blue=area(intersect(b,z['city']));outer=total-blue
  obj[scope]={'bounds':b,'denseUrbanIntersection':intersect(b,z['urban']),'blueCityIntersection':intersect(b,z['city']),'areaFractions':{'denseUrban':urban/total,'suburb':(blue-urban)/total,'outerLandscape':outer/total},'areaSquareMetres':{'denseUrban':urban,'suburb':blue-urban,'outerLandscape':outer}}
 obj['dominantCoreZone']=max(obj['core']['areaFractions'],key=obj['core']['areaFractions'].get);entries.append(obj)
result={'status':'source-zoning-arithmetic;not-generated-image-density-or-alignment-validation','input':{'file':str(planpath.relative_to(ROOT)),'sha256':hashlib.sha256(planpath.read_bytes()).hexdigest()},'sourceUserBounds':'docs/art/2026-11-02-county-zoning/selection.json','meaning':{'denseUrban':'insidegreen;dense vibrant urban, greater business/office/public-service concentration','suburb':'insideblue outsidegreen;less dense/lower-rise/courts/large-ground uses, deliveriesallowed','outerLandscape':'insidered outsideblue;forest/green/hills/sceneryonly, no business plots/pickups/dropoffs/routes'},'ignoredFrame':'brown overview enlargement reference, neverproduction boundary','boundaryAccuracy':'user-authorized approximate source rectangles retained, not resurveyed','regions':entries,'housingShareRule':'about50percent of programmed urban/suburban neighborhood land, not50percentofwholeRedimage; outer sceneryexcluded; no perregion identical quota'}
(OUT/'zone-overlap.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for ident in ['TR-22','TR-23','TR-33','TR-34']:
 r=next(r for r in entries if r['id']==ident);print(ident,'core',r['core']['areaFractions'],'render',r['render']['areaFractions'])
