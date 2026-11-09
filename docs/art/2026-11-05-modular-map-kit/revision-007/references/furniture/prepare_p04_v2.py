from pathlib import Path
from PIL import Image,ImageDraw
import json,math
D=Path(__file__).resolve().parent;K=D.parents[2];c=json.loads((K/'revision-003/road-constraint.json').read_text());p=c['projection'];u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']]
def xy(s,t,z):
 x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return (768+800*(x*p['axisX'][0]+y*p['axisY'][0]),1000+800*(x*p['axisX'][1]+y*p['axisY'][1]+z*p['axisZ'][1]))
def circle(r,z):return [xy(r*math.cos(i*math.pi/64),r*math.sin(i*math.pi/64),z) for i in range(128)]
im=Image.new('RGBA',(1536,1536));dr=ImageDraw.Draw(im)
# Correct painter order: base then column then opaque tabletop. No X-ray lines.
dr.polygon(circle(.3,.025),fill='#647783',outline='#355366',width=4)
a=xy(0,0,.025);b=xy(0,0,.715);dr.line([a,b],fill='#536875',width=70)
dr.polygon(circle(.5,.715),fill='#8d999c',outline='#355366',width=4)
dr.polygon(circle(.5,.75),fill='#d9e0e0',outline='#355366',width=4)
dr.text((45,40),'P04-v2 GEOMETRY ONLY; opaque tabletop occludes support; central pedestal/base',fill='#6490a0');im.save(D/'P04-v2-geometry.png')
