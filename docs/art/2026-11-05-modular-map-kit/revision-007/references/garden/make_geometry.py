from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw
root=Path('/Users/sanger/Documents/ChatGPT/taptap 2'); out=Path(__file__).parent
cp=root/'docs/art/2026-11-05-modular-map-kit/revision-003/road-constraint.json'; c=json.loads(cp.read_text()); ax=c['projection']['axisX']; ay=c['projection']['axisY']; az=c['projection']['axisZ']; u=c['streetTangentMap']; n=[-v for v in c['outwardPerpendicularMap']]
idx=json.loads((root/'docs/art/2026-11-05-modular-map-kit/revision-006/references/approved-25-index.json').read_text()); source=idx['sources'][4]; sp=Path(source['source']); assert hashlib.sha256(sp.read_bytes()).hexdigest()==source['sha256']
box=(470,285,705,435); Image.open(sp).crop(box).save(out/'TR35-v1-garden-style.png')
(out/'style-source.json').write_text(json.dumps(dict(source,styleCropBox=box,unscaled=True,role='local green foliage, soil and timber palette / painted daylight only; not layout authority',identity='P08/P09: 风格参考下原创补充; source garden beds are tiny, no exact individual identity or precise original object bbox claimed',originalObjectBox=None),ensure_ascii=False,indent=2))
for id,L,W,H,scale in [('P08',2.6,1.6,.55,330),('P09',4,2.4,2.1,210)]:
 im=Image.new('RGB',(1536,1536),'white'); d=ImageDraw.Draw(im)
 def p(s,t,z):
  x=s*u[0]+t*n[0]; y=s*u[1]+t*n[1];return (768+scale*(x*ax[0]+y*ay[0]+z*az[0]),850+scale*(x*ax[1]+y*ay[1]+z*az[1]))
 corners=[p(-L/2,-W/2,0),p(L/2,-W/2,0),p(L/2,W/2,0),p(-L/2,W/2,0)]
 d.polygon(corners,fill='#ded6c3',outline='#58666a',width=4)
 if id=='P08':
  top=[p(s,t,.12) for s,t in [(-L/2,-W/2),(L/2,-W/2),(L/2,W/2),(-L/2,W/2)]]
  for j in range(4):d.polygon([corners[j],corners[(j+1)%4],top[(j+1)%4],top[j]],fill='#c3b79e',outline='#5c6664',width=3)
  d.polygon(top,fill='#c7c0ae',outline='#5c6664',width=4)
  for t in [-.48,0,.48]:
   for s in [-.95,-.48,0,.48,.95]:
    pts=[p(s+.18*math.cos(a*math.pi/24),t+.18*math.sin(a*math.pi/24),.35) for a in range(49)]; d.line(pts,fill='#68956e',width=5)
 else:
  for s in [-L/2,-L/6,L/6,L/2]:
   pts=[p(s,-W/2,0),p(s,-W/2,.5)]+[p(s,-W/2*math.cos(a*math.pi/40),.5+1.6*math.sin(a*math.pi/40)) for a in range(41)]+[p(s,W/2,0)]
   d.line(pts,fill='#65818f',width=6)
  for t,z in [(-W/2,.5),(0,H),(W/2,.5)]:d.line([p(-L/2,t,z),p(L/2,t,z)],fill='#65818f',width=5)
  for t in [-.65,.65]:d.line([p(-1.7,t,.1),p(1.7,t,.1)],fill='#78996f',width=16)
 for q in corners:d.ellipse((q[0]-8,q[1]-8,q[0]+8,q[1]+8),fill='#d94d47')
 d.text((60,60),id+' geometry input only. Red dots = ground corners; remove all labels/markers.',fill='#34454b');im.save(out/f'{id}-geometry.png')
 rec={'id':id,'dimensionsCandidate':[L,W,H],'sourceMeasured':False,'u':u,'n':n,'axisX':ax,'axisY':ay,'axisZ':az,'pixelsPerUnit':scale,'origin':[768,850],'groundCornersABCD':corners,'longAxisScreenDeg':-28.486362688849802,'widthAxisScreenDeg':55.40598449120886,'constraintSHA256':hashlib.sha256(cp.read_bytes()).hexdigest(),'doorEnd':'+u upper-right end, P09 only','geometryOnlyNotFinalArt':True}
 (out/f'{id}-geometry.json').write_text(json.dumps(rec,indent=2))
