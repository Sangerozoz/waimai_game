from pathlib import Path
from PIL import Image,ImageDraw
import json,math
out=Path(__file__).parent;root=out.parents[6]
cpath=Path('/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-003/road-constraint.json');c=json.loads(cpath.read_text());ax=c['projection']['axisX'];ay=c['projection']['axisY'];az=c['projection']['axisZ'];u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']]
for id,scale,origin in [('T05',470,[768,1000]),('T04',215,[768,1160])]:
 im=Image.new('RGBA',(1536,1536));d=ImageDraw.Draw(im);faces=[]
 def point(s,t,z):
  x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return (origin[0]+scale*(x*ax[0]+y*ay[0]+z*az[0]),origin[1]+scale*(x*ax[1]+y*ay[1]+z*az[1]))
 def depth(v):
  s,t,z=v;x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return -.326506*(x+y)+.887011*z
 def line(a,b,w):d.line([point(*a),point(*b)],fill='#70604a',width=w)
 if id=='T05':
  masses=[(-.45,0,.34,.45,.5,.34),(.15,-.1,.48,.55,.5,.42),(.55,.18,.28,.35,.4,.28)]
  for s,t in [(-.45,0),(.15,-.1),(.55,.18)]:line((s,t,0),(s,t,.3),9)
 else:
  masses=[(-1.1,-.6,3.45,1.15,1.15,.7),(1,.55,3.65,1.1,1.25,.75),(.15,-.9,4.25,1.3,1.05,.75),(-.15,.45,4.7,1.5,1.25,.8)]
  line((0,0,0),(.08,0,2),26)
  for a,b in [((.08,0,1.5),(-1.4,-.4,3.2)),((.08,0,1.9),(1.3,.6,3.4)),((.08,0,1.8),(.3,-1.3,3.7)),((.08,0,2),(-.2,.8,4.2))]:line(a,b,18)
  for s,t in [(-.55,.1),(.4,.4),(.3,-.45)]:line((0,0,.35),(s,t,0),10)
 for s,t,z,rx,ry,rz in masses:
  def v(a,b):return(s+rx*math.cos(a)*math.cos(b),t+ry*math.sin(a)*math.cos(b),z+rz*math.sin(b))
  for i in range(32):
   for j in range(16):
    a=i*2*math.pi/32;b=-math.pi/2+j*math.pi/16;vs=[v(a,b),v(a+2*math.pi/32,b),v(a+2*math.pi/32,b+math.pi/16),v(a,b+math.pi/16)];mid=[sum(q[k] for q in vs)/4 for k in range(3)];light=.75+.17*math.sin(b)+.08*math.cos(a+1);color=tuple(int(ch*light) for ch in [92,132,89])+(255,);faces.append((depth(mid),vs,color))
 for _,vs,color in sorted(faces,key=lambda x:x[0]):d.polygon([point(*q) for q in vs],fill=color)
 im.save(out/f'{id}-solid-v2-guide.png');(out/f'{id}-solid-v2-guide.json').write_text(json.dumps({'id':id,'role':'opaque 3D ellipsoid structure input only, never finished art','projection':c['projection'],'u':u,'n':n,'scale':scale,'origin':origin,'rootWorld':[0,0,0],'rootPixelProjection':origin,'rootVisibility':'may be occluded; projected origin is inferred, not asserted visible','depthSorting':'view dot (-.326506,-.326506,.887011); opaque faces back to front','noLabelsOrMarkers':True,'masses':masses},indent=2))
