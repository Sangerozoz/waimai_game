from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
base=Path('/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit');out=base/'revision-007/references/public'
c=json.loads((base/'revision-003/road-constraint.json').read_text());p=c['projection'];u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']]
def raw(s,t,z):
 x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return [x*p['axisX'][i]+y*p['axisY'][i]+z*p['axisZ'][i] for i in range(2)]
models={'P01':[(-.325,.325,-.2,.2,0,.10),(-.12,.12,-.09,.09,.1,.38),(-.30,.30,-.10,.10,.38,1.45)],'P10':[(-.55,-.025,-.325,.325,0,.88),(.025,.55,-.325,.325,0,.88),(-.55,-.025,-.325,.325,.88,1),(.025,.55,-.325,.325,.88,1)]}
for id,boxes in models.items():
 pts=[raw(s,t,z) for a,b,d,e,f,g in boxes for s in [a,b] for t in [d,e] for z in [f,g]]
 lo=[min(v[i] for v in pts) for i in range(2)];hi=[max(v[i] for v in pts) for i in range(2)];scale=min(720/(hi[i]-lo[i]) for i in range(2));offset=[512-(hi[i]+lo[i])/2*scale for i in range(2)]
 def project(s,t,z):return tuple(raw(s,t,z)[i]*scale+offset[i] for i in range(2))
 im=Image.new('RGB',(1024,1024),'white');dr=ImageDraw.Draw(im)
 for a,b,d,e,f,g in boxes:
  v=[project(a,d,f),project(b,d,f),project(b,e,f),project(a,e,f),project(a,d,g),project(b,d,g),project(b,e,g),project(a,e,g)]
  for inds,fill in [([0,3,7,4],'#b8c4ca'),([3,2,6,7],'#d6e1e7'),([4,5,6,7],'#9eafb9')]:dr.polygon([v[i] for i in inds],fill=fill,outline='#54626a',width=3)
 dr.text((40,35),id+' GEOMETRY ONLY - no labels in final art',fill='black');im.save(out/(id+'-geometry.png'))
 (out/(id+'-geometry.json')).write_text(json.dumps(dict(candidateOnly=True,boxes=boxes,projection=c['projection'],u=u,n=n,scale=scale,offset=offset,groundCenter=project(0,0,0),footprintCorners=[project(-(.325 if id=='P01' else .55),-.2 if id=='P01' else -.325,0),project(.325 if id=='P01' else .55,-.2 if id=='P01' else -.325,0),project(.325 if id=='P01' else .55,.2 if id=='P01' else .325,0),project(-(.325 if id=='P01' else .55),.2 if id=='P01' else .325,0)]),indent=2))
src=base.parent/'2026-11-04-county-twentyfive-region-plan/review-009/TR-33-v1.png';box=[380,188,685,391];Image.open(src).crop(box).save(out/'TR33-style-context.png')
(out/'source.json').write_text(json.dumps(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),imageNumber=3,region='TR-33',version='v1',styleContextBox=box,identity='风格参考下原创补充；源小物不清晰，不声称框内存在灯箱或双桶，不编造物件bbox。',role='local painted material/daylight reference only; not composition/camera/identity'),ensure_ascii=False,indent=2))
