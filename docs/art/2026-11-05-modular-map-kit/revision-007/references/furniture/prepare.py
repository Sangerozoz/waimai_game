from pathlib import Path
from PIL import Image,ImageDraw
import json,math,hashlib
D=Path(__file__).resolve().parent;K=D.parents[2];R=K/'revision-007'
c=json.loads((K/'revision-003/road-constraint.json').read_text());u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']];p=c['projection']
src=Path('/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-04-county-twentyfive-region-plan/review-018/TR-32-v1.png');box=[352,754,529,868];Image.open(src).crop(box).save(D/'TR32-courtyard-style.png')
(D/'style-source.json').write_text(json.dumps(dict(imageNumber=11,region='TR-32',version='v1',source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),styleCropBox=box,identity='风格参考下原创补充；box只记录色彩笔触参考，无可辨家具身份'),ensure_ascii=False,indent=2))
def project(q):
 s,t,z=q;x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return (x*p['axisX'][0]+y*p['axisY'][0],x*p['axisX'][1]+y*p['axisY'][1]+z*p['axisZ'][1])
for id in ['P03','P04','P05']:
 lines=[]
 if id=='P03':
  for z,t in [(.45,-.325),(.45,.325),(.9,-.325)]:lines.append([(-1,t,z),(1,t,z)])
  for s in [-.8,.8]:
   for t in [-.25,.25]:lines.append([(s,t,0),(s,t,.45)])
  for s in [-1,1]:lines += [[(s,-.325,.45),(s,-.325,.9)],[(s,-.325,.45),(s,.325,.45)]]
  for z in [.6,.75]:lines.append([(-1,-.325,z),(1,-.325,z)])
 else:
  radius,h=(.5,.75) if id=='P04' else (.21,.45)
  lines.append([(radius*math.cos(i*math.pi/32),radius*math.sin(i*math.pi/32),h) for i in range(65)])
  for s,t in [(-.6,-.6),(-.6,.6),(.6,-.6),(.6,.6)]:lines.append([(s*radius,t*radius,0),(s*radius,t*radius,h)])
 pts=[project(q) for l in lines for q in l];x0=min(x for x,y in pts);x1=max(x for x,y in pts);y0=min(y for x,y in pts);y1=max(y for x,y in pts);sc=min(1100/(x1-x0),1000/(y1-y0))
 im=Image.new('RGBA',(1536,1536));dr=ImageDraw.Draw(im)
 for l in lines:dr.line([(768+(x-(x0+x1)/2)*sc,800+(y-(y0+y1)/2)*sc) for x,y in map(project,l)],fill='#72a3b8',width=9)
 dr.text((60,40),id+' GEOMETRY ONLY; no final art; u -28.486 n +55.406; wall verticals vertical',fill='#72a3b8');im.save(D/(id+'-geometry.png'))
