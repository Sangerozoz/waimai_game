from pathlib import Path
from PIL import Image,ImageDraw
import json,math,hashlib
root=Path('/Users/sanger/Documents/ChatGPT/taptap 2'); out=Path(__file__).parent;cpath=root/'docs/art/2026-11-05-modular-map-kit/revision-003/road-constraint.json';c=json.loads(cpath.read_text());ax=c['projection']['axisX'];ay=c['projection']['axisY'];az=c['projection']['axisZ'];u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']]
s=json.loads((root/'docs/art/2026-11-05-modular-map-kit/revision-006/references/approved-25-index.json').read_text())['sources'][4];sp=Path(s['source']);assert hashlib.sha256(sp.read_bytes()).hexdigest()==s['sha256'];box=[610,410,875,690];Image.open(sp).crop(box).save(out/'TR35-v1-foliage-style.png');(out/'source.json').write_text(json.dumps(dict(s,styleCropBox=box,unscaled=True,objectIdentity='风格参考下原创补充',individualObjectBBox=None,reason='Natural graduated greens and layered broadleaf crowns; no exact tree/shrub identity claimed'),ensure_ascii=False,indent=2))
for id,dims,scale,origin in [('T04',[4.5,4,5.5],205,[768,1140]),('T05',[1.8,1.2,.9],480,[768,980])]:
 im=Image.new('RGB',(1536,1536),'white');d=ImageDraw.Draw(im)
 def p(s,t,z):
  x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return(origin[0]+scale*(x*ax[0]+y*ay[0]+z*az[0]),origin[1]+scale*(x*ax[1]+y*ay[1]+z*az[1]))
 def branch(a,b,w):d.line([p(*a),p(*b)],fill='#776a59',width=w)
 def ell(s,t,z,rx,ry,rz):
  for h in [-.5,0,.5]:
   pts=[p(s+rx*math.sqrt(1-h*h)*math.cos(a*math.pi/36),t+ry*math.sqrt(1-h*h)*math.sin(a*math.pi/36),z+rz*h) for a in range(73)];d.line(pts,fill='#729784',width=4)
  for phi in [0,math.pi/2]:d.line([p(s+rx*math.cos(a*math.pi/36)*math.cos(phi),t+ry*math.cos(a*math.pi/36)*math.sin(phi),z+rz*math.sin(a*math.pi/36)) for a in range(73)],fill='#91ac9c',width=3)
 if id=='T04':
  branch((0,0,0),(.08,0,2),24)
  for a,b in [((.08,0,1.5),(-1.4,-.4,3.2)),((.08,0,1.9),(1.3,.6,3.4)),((.08,0,1.8),(.3,-1.3,3.7)),((.08,0,2),(-.2,.8,4.2))]:branch(a,b,15)
  for e in [(-1.1,-.6,3.45,1.15,1.15,.7),(1,.55,3.65,1.1,1.25,.75),(.15,-.9,4.25,1.3,1.05,.75),(-.15,.45,4.7,1.5,1.25,.8)]:ell(*e)
  for s0,t0 in [(-.55,.1),(.4,.4),(.3,-.45)]:branch((0,0,.35),(s0,t0,0),10)
 else:
  for e in [(-.45,0,.35,.45,.5,.35),(.2,-.12,.5,.5,.48,.4),(.55,.2,.3,.35,.4,.3)]:ell(*e)
  for s0,t0 in [(-.45,0),(.2,-.12),(.55,.2)]:branch((s0,t0,0),(s0,t0,.3),9)
 q=p(0,0,0);d.ellipse((q[0]-8,q[1]-8,q[0]+8,q[1]+8),fill='#cc4e4e');d.text((50,50),id+' structure guide ONLY / red = root origin / wire masses NOT literal final shape',fill='black');im.save(out/f'{id}-geometry.png')
 (out/f'{id}-geometry.json').write_text(json.dumps(dict(id=id,dimensionsCandidate=dims,sourceMeasured=False,u=u,n=n,axisX=ax,axisY=ay,axisZ=az,pixelsPerUnit=scale,origin=origin,rootPixel=q,constraintSHA256=hashlib.sha256(cpath.read_bytes()).hexdigest(),note='organic envelope not camera-axis evidence; input only'),indent=2))
