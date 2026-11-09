from pathlib import Path
import math,json,hashlib
from PIL import Image,ImageDraw
root=Path('/Users/sanger/Documents/ChatGPT/taptap 2'); out=Path(__file__).parent
cp=root/'docs/art/2026-11-05-modular-map-kit/revision-003/road-constraint.json'; c=json.loads(cp.read_text()); ax=c['projection']['axisX']; ay=c['projection']['axisY']; az=c['projection']['axisZ']; u=c['streetTangentMap']; n=[-v for v in c['outwardPerpendicularMap']]
for id,L,W,H in [('V01',4.2,1.8,1.5),('V02',4.9,2,2.4)]:
 im=Image.new('RGB',(1536,1536),'white'); d=ImageDraw.Draw(im); scale=215
 def p(s,t,z):
  x=s*u[0]+t*n[0]; y=s*u[1]+t*n[1]
  return (768+scale*(x*ax[0]+y*ay[0]+z*az[0]),870+scale*(x*ax[1]+y*ay[1]+z*az[1]))
 def box(s0,s1,t0,t1,z0,z1,color):
  lo=[p(s0,t0,z0),p(s1,t0,z0),p(s1,t1,z0),p(s0,t1,z0)]; hi=[p(s0,t0,z1),p(s1,t0,z1),p(s1,t1,z1),p(s0,t1,z1)]
  for face,fill in [(lo,'#eff1f2'),([lo[0],lo[1],hi[1],hi[0]],'#aab5bd'),([lo[1],lo[2],hi[2],hi[1]],'#b6bec4'),([lo[2],lo[3],hi[3],hi[2]],color),(hi,'#e0e6e9')]: d.polygon(face,fill=fill,outline='#344754',width=4)
  return hi
 wb=L*.62; contacts=[]
 for s in [-wb/2,wb/2]:
  for t in [-W*.46,W*.46]:
   q=p(s,t,0); contacts.append(q)
   pts=[p(s+.31*math.cos(a*math.pi/36),t,.31+.31*math.sin(a*math.pi/36)) for a in range(73)]
   d.line(pts,fill='#586570',width=14)
 if id=='V01':
  box(-L/2,L/2,-W/2,W/2,.32,.77,'#b5c8d1'); box(-1.25,.70,-W*.44,W*.44,.77,H,'#9eb8c9')
 else:
  box(-L/2,L/2,-W*.35,W*.35,.32,.62,'#a5aeb4'); box(-L/2,.78,-W/2,W/2,.62,H,'#c8d2d7'); box(.82,L/2,-W/2,W/2,.5,1.8,'#a7bdca')
 for q in contacts: d.ellipse((q[0]-10,q[1]-10,q[0]+10,q[1]+10),fill='#e13434')
 rear=p(-L/2,0,0); front=p(L/2,0,0); d.line([rear,front],fill='#00a987',width=5); d.text((80,80),f'{id} geometry ONLY / red = four wheel ground contacts / nose UPPER RIGHT',fill='black')
 im.save(out/f'{id}-v2-geometry.png')
 rec={'id':id,'candidateDimensions':[L,W,H],'dimensionStatus':'planning candidates only, not source-measured or user hard limits','constraint':str(cp),'constraintSHA256':hashlib.sha256(cp.read_bytes()).hexdigest(),'u':u,'n':n,'axisX':ax,'axisY':ay,'axisZ':az,'scale':scale,'origin':[768,870],'wheelContactsPixels':contacts,'targetAnglesScreenDeg':c['groundEdgeAnglesScreenDeg'],'role':'geometry input only, never delivery art'}
 (out/f'{id}-v2-geometry.json').write_text(json.dumps(rec,indent=2))
style=root/'docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png'
Image.open(style).crop((620,290,1080,620)).save(out/'v2-map-brushwork-crop.png')
(out/'v2-style-reference.json').write_text(json.dumps({'mapSource':str(style),'mapSHA256':hashlib.sha256(style.read_bytes()).hexdigest(),'box':[620,290,1080,620],'cropTreatment':'unscaled crop, no color edits','role':'brushwork simplified planes daylight only, no building/car identity or scene layout','riderReference':'revision-005/runtime-280/viewer/assets/rt-HC-R-NE-v1.png','riderRole':'paint simplified surfaces and light only; no motorcycle/person identity'},indent=2))
