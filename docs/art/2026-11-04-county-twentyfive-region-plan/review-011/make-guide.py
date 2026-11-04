"""Draw source geometry only. Never edits generated artwork or source map."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'docs/art/2026-11-04-county-twentyfive-region-plan/geometry/twentyfive-regions.json').read_text())
city=json.loads((ROOT/'delivery-game/assets/resources/map-sample/city.json').read_text())
r=next(r for r in plan['regions'] if r['id']=='TR-34'); b=r['renderBoundsMetres']; q=math.sqrt(.5); sine=math.sin(math.radians(62.5))
poly=r['renderPolygonMetres']
def proj(p):return ((p[0]-p[1])*q,(p[0]+p[1])*q*sine)
pts=[proj(p) for p in poly];lo=[min(p[i] for p in pts) for i in [0,1]];hi=[max(p[i] for p in pts) for i in [0,1]]
scale=min(1888/(hi[i]-lo[i]) for i in [0,1]);off=[(2048-(hi[i]-lo[i])*scale)/2 for i in [0,1]]
def xy(p):
 u,v=proj(p);return ((u-lo[0])*scale+off[0],(v-lo[1])*scale+off[1])
im=Image.new('RGBA',(2048,2048),(255,255,255,0));dr=ImageDraw.Draw(im);dr.polygon([xy(p) for p in poly],fill='#e7e6e1')
# Neutral source-space urban/suburb segmentation: not final art colors.
blue=plan['zones']['city'];green=plan['zones']['urban']
def intersection(a,b):
 z={'minX':max(a['minX'],b['minX']),'maxX':min(a['maxX'],b['maxX']),'minY':max(a['minY'],b['minY']),'maxY':min(a['maxY'],b['maxY'])}
 return z if z['maxX']>z['minX'] and z['maxY']>z['minY'] else None
def corners(z):return [[z['minX'],z['minY']],[z['maxX'],z['minY']],[z['maxX'],z['maxY']],[z['minX'],z['maxY']]]
citypart=intersection(b,blue);urbanpart=intersection(b,green)
if citypart:dr.polygon([xy(v) for v in corners(citypart)],fill='#eeefeb')
if urbanpart:dr.polygon([xy(v) for v in corners(urbanpart)],fill='#d9dddf')
for i in r['renderSourceIds']['areaIndices']:
 a=city['areas'][i]
 if a['kind']=='water':dr.polygon([xy(p) for p in a['points']],fill='#aac0cb')
for i in r['renderSourceIds']['waterwayIndices']:
 dr.line([xy(p) for p in city['waterways'][i]],fill='#aac0cb',width=max(2,round(5*scale)))
for i in r['renderSourceIds']['exactFootprintIntersectingBuildingIndices']:
 p=city['buildings'][i];dr.polygon([xy(v) for v in p],fill='#b6b7b7',outline='#86898a')
nodes={n['id']:[n['x'],n['y']] for n in city['nodes']};ids=set(r['renderSourceIds']['roadIds'])
for road in city['roads']:
 if road['id'] not in ids:continue
 ps=[xy(nodes[n]) for n in road['nodes']];w=max(1,round(road.get('width',5)*scale*sine));dr.line(ps,fill='#91979a',width=w+max(1,round(2*scale)),joint='curve');dr.line(ps,fill='#666d72',width=w,joint='curve')
# Green boundary is a semantic guide only: do not render this line/text in final art.
if b['minX']<green['maxX']<b['maxX']:
 dr.line([xy([green['maxX'],b['minY']]),xy([green['maxX'],b['maxY']])],fill='#05934b',width=7)
fontpath=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
font=ImageFont.truetype(str(fontpath),32) if fontpath.exists() else ImageFont.load_default()
if urbanpart:
 z=urbanpart;pos=xy([(z['minX']+z['maxX'])/2,(z['minY']+z['maxY'])/2]);dr.text(pos,'DENSE URBAN',font=font,fill='#124b30',stroke_width=5,stroke_fill='white',anchor='mm')
if citypart:
 loX=max(green['maxX'],b['minX']);pos=xy([(loX+b['maxX'])/2,(b['minY']+b['maxY'])/2]);dr.text(pos,'LOW-DENSITY SUBURB',font=font,fill='#304450',stroke_width=5,stroke_fill='white',anchor='mm')
mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon([xy(p) for p in poly],fill=255);im.putalpha(mask);im.save(OUT/'TR-34-zoned-source-geometry.png')
record={'regionId':'TR-34','role':'source geometry only, not artwork','size':[2048,2048],'renderBoundsMetres':b,'pixelsPerProjectedMetre':scale,'projectedMin':lo,'canvasOffset':off,'sourceBuildingCount':r['renderSourceIds']['buildingCounts']['exactFootprintIntersecting'],'sourceRoadCount':len(ids),'geometryMeasuredAgainstGeneratedImage':False,'urbanSourceBounds':green,'blueSourceBounds':blue,'guideOnlyBoundaryX':green['maxX'],'diagramLabelsAndColorsNotFinalArt':True}
(OUT/'guide-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record))
