from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).resolve().parent;K=D.parents[3];c=json.loads((K/'revision-003/road-constraint.json').read_text());p=c['projection'];u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']]
src=Path('/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-04-county-twentyfive-region-plan/review-018/TR-32-v1.png');Image.open(src).crop((395,365,594,562)).save(D/'TR32-style.png')
(D/'style-source.json').write_text(json.dumps(dict(source=str(src),imageNumber=11,region='TR-32',version='v1',sha256=hashlib.sha256(src.read_bytes()).hexdigest(),styleBox=[395,365,594,562],identity='风格参考下原创补充；非源物件复刻，box仅局部画法/材质'),ensure_ascii=False,indent=2))
def proj(q):
 s,t,z=q;x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return [x*p['axisX'][i]+y*p['axisY'][i]+z*p['axisZ'][i] for i in [0,1]]
for id,w,dep,h in [('B12',6.4,4.6,2.7),('B13',6,5,3.3)]:
 a,b=-w/2,w/2;c0,d=-dep/2,dep/2;g=[(a,c0,0),(b,c0,0),(b,d,0),(a,d,0)];r=[(s,t,h) for s,t,z in g];faces=[([g[0],g[3],r[3],r[0]],'#a7b7bd'),([g[3],g[2],r[2],r[3]],'#dce5e7')]
 if id=='B12':
  ra=(a-.2,0,3.8);rb=(b+.2,0,3.8);e=[(a-.2,c0-.2,h),(b+.2,c0-.2,h),(b+.2,d+.2,h),(a-.2,d+.2,h)];faces += [([e[0],e[3],ra],'#b3c2c6'),([e[0],e[1],rb,ra],'#8299a5'),([ra,rb,e[2],e[3]],'#9bb0b9')]
 else:faces += [(r,'#9bb0b9')]
 pts=[proj(v) for f,col in faces for v in f];x0=min(x for x,y in pts);x1=max(x for x,y in pts);y0=min(y for x,y in pts);y1=max(y for x,y in pts);scale=min(1200/(x1-x0),1100/(y1-y0))
 def xy(v):
  x,y=proj(v);return (768+(x-(x0+x1)/2)*scale,790+(y-(y0+y1)/2)*scale)
 im=Image.new('RGBA',(1536,1536));dr=ImageDraw.Draw(im)
 for f,col in faces:dr.polygon([xy(v) for v in f],fill=col,outline='#446476',width=3)
 # actual front door recess guide, not a transparent hole
 s=.9 if id=='B12' else -1.6
 door=[(s-.45,d,.12),(s+.45,d,.12),(s+.45,d,2.2),(s-.45,d,2.2)];dr.polygon([xy(v) for v in door],fill='#526c79',outline='#355266',width=3)
 dr.text((50,40),id+' GEOMETRY ONLY; ONE storey; front door on near face; u -28.486 n +55.406',fill='#56818f');im.save(D/(id+'-geometry.png'))
