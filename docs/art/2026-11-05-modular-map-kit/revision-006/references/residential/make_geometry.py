from pathlib import Path
import json
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent
K=D.parents[2]
c=json.loads((K/'revision-003/road-constraint.json').read_text())
u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']];p=c['projection']
def proj(q):
 s,t,z=q;x=s*u[0]+t*n[0];y=s*u[1]+t*n[1]
 return (x*p['axisX'][0]+y*p['axisY'][0],x*p['axisX'][1]+y*p['axisY'][1]+z*p['axisZ'][1])
models={'B06':[(-5.5,-1,-3.5,3.5,6),(-1,1,-2.5,2.5,4),(1,5.5,-3.5,3.5,3.5)],'B07':[(-9,9,-6,-2,10),(-9,-5,-2,6,10),(5,9,-2,6,10)]}
for id,bs in models.items():
 faces=[]
 for a,b,c,d,h in bs:
  g=[(a,c,0),(b,c,0),(b,d,0),(a,d,0)];r=[(s,t,h) for s,t,z in g]
  faces += [(g[0:1]+[g[3],r[3],r[0]],'#a5b7bf'),([g[3],g[2],r[2],r[3]],'#e2e8eb'),(r,'#bccdd3')]
 pts=[proj(v) for f,col in faces for v in f];x0=min(v[0] for v in pts);x1=max(v[0] for v in pts);y0=min(v[1] for v in pts);y1=max(v[1] for v in pts);scale=min(1200/(x1-x0),1150/(y1-y0))
 def xy(v):
  x,y=proj(v);return (768+(x-(x0+x1)/2)*scale,790+(y-(y0+y1)/2)*scale)
 im=Image.new('RGBA',(1536,1536));dr=ImageDraw.Draw(im)
 for f,col in faces:dr.polygon([xy(v) for v in f],fill=col,outline='#416477',width=3)
 dr.text((50,35),id+' GEOMETRY ONLY - NOT ART; vertical walls; frontage -28.486 depth +55.406',fill='#3b677a')
 dr.text((50,60),'PM approximate masses only; B06 left pitched roof to be added per appearance; U courtyard EMPTY',fill='#3b677a')
 im.save(D/(id+'-geometry.png'))
