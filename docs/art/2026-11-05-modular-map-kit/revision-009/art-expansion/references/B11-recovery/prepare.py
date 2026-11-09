from pathlib import Path
from PIL import Image,ImageDraw
import json,math,hashlib
K=Path.cwd()/'docs/art/2026-11-05-modular-map-kit';O=K/'revision-009/art-expansion/references/B11-recovery';src=K/'revision-006/native/B11-001/B11-v1.png';im=Image.open(src);dr=ImageDraw.Draw(im)
lines=[('D1',[560,1093],[647,1148],'same service-room left wall plinth; depth'),('U1',[900,1080],[1040,1014],'same service-room long wall plinth; frontage'),('D2',[317,900],[540,1040],'second roller sill; cross-check only NOT wall foot')]
res=[]
for id,a,b,desc in lines:
 ang=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]));dr.line([tuple(a),tuple(b)],fill='cyan',width=3)
 for i,q in enumerate([a,b]):dr.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),fill='red');dr.text((q[0]+5,q[1]-15),id+str(i+1),fill='yellow')
 res.append(dict(id=id,a=a,b=b,angleDeg=ang,meaning=desc,manualEndpointUncertaintyPx=3))
for id,q in [('roller1',[220,859]),('roller2',[430,970]),('person',[810,1087])]:dr.text(q,id,fill='red')
im.save(O/'v1-controls.png');(O/'diagnosis.json').write_text(json.dumps({'source':str(src),'sourceSHA':hashlib.sha256(src.read_bytes()).hexdigest(),'lines':res,'doorsManualSillCentres':{'roller1':[220,859],'roller2':[430,970],'person':[810,1087]},'excluded':'step lip, eaves, shadow, cross-wing chord, hidden rear corners','conclusion':'old envelope invalid as axis, but real straight depth still about32deg; authorize single native v2. No PPU derived from partial edges.'},ensure_ascii=False,indent=2))
p=json.loads((K/'revision-003/road-constraint.json').read_text());u=p['streetTangentMap'];n=p['outwardPerpendicularMap'];pr=p['projection']
def proj(v):
 s,t,z=v;x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return(pr['axisX'][0]*x+pr['axisY'][0]*y,pr['axisX'][1]*x+pr['axisY'][1]*y+pr['axisZ'][1]*z)
faces=[]
for s0,s1,t0,t1,h,rise in [(-5,5,-3.5,-.5,3.5,1.5),(-4.6,4.6,-.5,1.8,2.5,1.2),(-4,4,1.8,3.5,1.9,.8)]:
 a=(s0,t0,0);b=(s1,t0,0);c=(s1,t1,0);d=(s0,t1,0);aa=(s0,t0,h);bb=(s1,t0,h);cc=(s1,t1,h);dd=(s0,t1,h);rl=(s0,(t0+t1)/2,h+rise);rr=(s1,(t0+t1)/2,h+rise)
 faces.extend([([a,d,dd,rl,aa],(174,190,195)),([d,c,cc,dd],(210,220,224)),([aa,bb,rr,rl],(130,151,162)),([rl,rr,cc,dd],(151,174,185))])
pts=[proj(v) for f,col in faces for v in f];x0=min(x for x,y in pts);x1=max(x for x,y in pts);y0=min(y for x,y in pts);y1=max(y for x,y in pts);scale=min(1200/(x1-x0),1100/(y1-y0))
def px(v):
 x,y=proj(v);return(768+(x-(x0+x1)/2)*scale,768+(y-(y0+y1)/2)*scale)
g=Image.new('RGBA',(1536,1536));d=ImageDraw.Draw(g)
for f,col in faces:
 q=[px(v) for v in f];d.polygon(q,fill=col);d.line(q+q[:1],fill=(35,65,80),width=3)
d.text((60,50),'B11 geometry ONLY - actual u/n/Z - 10x7x5 candidate',fill='white');g.save(O/'B11-geometry.png')
print(res)
