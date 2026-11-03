"""Prepare visual-only outer landscape from confirmed bounds and original water geometry."""
import hashlib,json,math,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'delivery-game/assets/resources/map-sample/city.json'
out=ROOT/'delivery-game/county-sample/outer-landscape.json'
raw=source.read_bytes();data=json.loads(raw)
red={'minX':-3187.43,'maxX':136.05,'minY':-1817.63,'maxY':1505.84}
blue={'minX':-2652.59,'maxX':-361.42,'minY':-1282.79,'maxY':867.46}
def overlaps(points,bounds):
 if not points:return False
 xs=[p[0] for p in points];ys=[p[1] for p in points]
 return max(xs)>=bounds['minX'] and min(xs)<=bounds['maxX'] and max(ys)>=bounds['minY'] and min(ys)<=bounds['maxY']
water=[a['points'] for a in data['areas'] if a['kind']=='water' and overlaps(a['points'],red)]
streams=[]
for line in data['waterways']:
 for a,b in zip(line,line[1:]):
  if overlaps([a,b],red):streams.append([a,b])
def segment_distance(x,y,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];length=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/length)) if length else 0
 return math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
def point_in(x,y,points):
 inside=False;j=len(points)-1
 for i,a in enumerate(points):
  b=points[j]
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
  j=i
 return inside
def outside_water(x,y,pad):
 if any(segment_distance(x,y,a,b)<pad+10 for a,b in streams):return False
 for poly in water:
  if not overlaps(poly,{'minX':x-pad,'maxX':x+pad,'minY':y-pad,'maxY':y+pad}):continue
  if point_in(x,y,poly) or any(segment_distance(x,y,a,b)<pad for a,b in zip(poly,poly[1:]+poly[:1])):return False
 return True
size=160;tiles=[]
for ix in range(math.floor(red['minX']/size),math.ceil(red['maxX']/size)):
 for iy in range(math.floor(red['minY']/size),math.ceil(red['maxY']/size)):
  l=max(red['minX'],ix*size);r=min(red['maxX'],(ix+1)*size);b=max(red['minY'],iy*size);t=min(red['maxY'],(iy+1)*size)
  if l>=blue['minX'] and r<=blue['maxX'] and b>=blue['minY'] and t<=blue['maxY']:continue
  rng=random.Random(f'county-outer-v1:{ix}:{iy}');cx=(l+r)/2;cy=(b+t)/2
  zone='north' if cy>=blue['maxY'] else 'east' if cx>=blue['maxX'] else 'west' if cx<=blue['minX'] else 'south'
  trees=[]
  for _ in range(rng.randint(1,3) if zone in ('north','east','west') else rng.randint(0,2)):
   x=rng.uniform(l,r);y=rng.uniform(b,t)
   if blue['minX']<=x<=blue['maxX'] and blue['minY']<=y<=blue['maxY']:continue
   if outside_water(x,y,9):trees.append({'groundAnchor':[round(x,2),round(y,2)],'heightMetres':round(rng.uniform(6,10),1),'crownDiameterMetres':round(rng.uniform(5,8),1)})
  hills=[]
  if zone in ('north','east'):
   x=rng.uniform(l+10,r-10);y=rng.uniform(b+10,t-10);radius=rng.uniform(25,45)
   if outside_water(x,y,radius):hills.append({'center':[round(x,2),round(y,2)],'radiusMetres':round(radius,1),'heightMetres':round(rng.uniform(12,27),1)})
  tiles.append({'key':f'{ix}:{iy}','bounds':{'minX':l,'maxX':r,'minY':b,'maxY':t},'zone':zone,'trees':trees,'hills':hills,'groundPatternSeed':rng.randrange(100000)})
payload={'version':1,'purpose':'visual-only-landscape-no-operating-addresses-or-routes','displayBounds':red,'businessBounds':blue,'coordinateUnit':'ground-metres','source':'delivery-game/assets/resources/map-sample/city.json','sourceSHA256':hashlib.sha256(raw).hexdigest(),'tileSizeMetres':size,'heightNote':'procedural scenery values, not surveyed elevation','waterVisualWidthMetres':12,'tiles':tiles,'sourceWaterPolygons':water,'sourceWaterSegments':streams}
out.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n')
print('景观格',len(tiles),'树',sum(len(t['trees']) for t in tiles),'低山',sum(len(t['hills']) for t in tiles),'水域',len(water),'水道段',len(streams))
