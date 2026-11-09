from pathlib import Path
from PIL import Image,ImageDraw
import json,math,hashlib
R=Path.cwd(); K=R/'docs/art/2026-11-05-modular-map-kit'; O=K/'revision-007/references/industry'
d=json.loads((K/'revision-003/road-constraint.json').read_text()); pr=d['projection']; u=d['streetTangentMap']; n=d['outwardPerpendicularMap']
def xyz(a,b,z):
 x=u[0]*a+n[0]*b;y=u[1]*a+n[1]*b
 return (pr['axisX'][0]*x+pr['axisY'][0]*y,pr['axisX'][1]*x+pr['axisY'][1]*y+pr['axisZ'][1]*z)
for id,L,W,H in [('B10',13,9,6),('P02',1.2,1.2,1.6),('P06',2.5,.16,1),('P07',.16,2.5,1)]:
 shapes=[]
 def box(a,b,c,e,z,h):
  v=[(a,c,z),(b,c,z),(b,e,z),(a,e,z)];t=[(x,y,h) for x,y,_ in v]
  shapes.extend([v,t,[v[0],v[3],t[3],t[0]],[v[3],v[2],t[2],t[3]]])
 if id=='B10':
  box(-L/2,L/2,-W/2,W/2,0,4)
  for i in range(4):
   a=-L/2+i*L/4;b=a+L/4
   shapes.append([(a,-W/2,4),(a,W/2,4),(b-.15,W/2,6),(b-.15,-W/2,6)])
 elif id=='P02':
  for z in [.15,1.55]: shapes.append([(.6*math.cos(i*math.pi/24),.6*math.sin(i*math.pi/24),z) for i in range(48)])
  for a in [-.4,.4]: box(a-.06,a+.06,-.3,.3,0,.25)
  for a in [-.6,.6]: shapes.append([(a,0,.15),(a,0,1.55)])
 else:
  alongU=id=='P06'
  def bx(a,b,z,h):
   if alongU: box(a,b,-.08,.08,z,h)
   else: box(-.08,.08,a,b,z,h)
  for a in [-1.17,1.17]: bx(a-.08,a+.08,0,1)
  for z in [.32,.7]: bx(-1.17,1.17,z,z+.1)
  for a in [-.8,-.4,0,.4,.8]: bx(a-.055,a+.055,.12,.93)
 pts=[xyz(*v) for s in shapes for v in s]; x0=min(x for x,y in pts);x1=max(x for x,y in pts);y0=min(y for x,y in pts);y1=max(y for x,y in pts);sc=min(1100/(x1-x0),1050/(y1-y0))
 def px(v):
  x,y=xyz(*v);return (768+(x-(x0+x1)/2)*sc,768+(y-(y0+y1)/2)*sc)
 im=Image.new('RGBA',(1536,1536));dr=ImageDraw.Draw(im)
 for s in shapes:
  q=[px(v) for v in s]
  if len(q)>2: dr.polygon(q,fill=(150,164,170,210))
  dr.line(q+q[:1],fill=(25,70,90,255),width=4)
 dr.text((40,40),id+' GEOMETRY ONLY - u -28.486 / n +55.406; vertical z',fill='white')
 im.save(O/(id+'-geometry.png'))
src=R/'docs/art/2026-11-04-county-twentyfive-region-plan/review-007/TR-22-v1.png'
Image.open(src).crop((487,181,599,267)).save(O/'style-local.png')
(O/'source.json').write_text(json.dumps({'source':str(src),'imageNumber':1,'region':'TR-22','version':'v1','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'styleCropBox':[487,181,599,267],'propsIdentity':'风格参考下原创补充，无原小物bbox','dimensions':'PM candidates not surveyed','B10Review':'Actual straight base short edge approx (85,910)-(465,1180) =35.4deg; control (100,930)-(443,1170)=35deg is consistent, not irregular chord. Wall approx 460px. Pose correction justified.'},ensure_ascii=False,indent=2))
