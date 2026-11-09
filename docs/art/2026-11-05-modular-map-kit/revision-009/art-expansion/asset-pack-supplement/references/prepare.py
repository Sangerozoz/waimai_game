from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
base=Path('/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit');out=base/'revision-009/art-expansion/asset-pack-supplement/references'
c=json.loads((base/'revision-003/road-constraint.json').read_text());p=c['projection'];u=c['streetTangentMap'];n=[-v for v in c['outwardPerpendicularMap']]
def raw(s,t,z):
 x=s*u[0]+t*n[0];y=s*u[1]+t*n[1];return [x*p['axisX'][i]+y*p['axisY'][i]+z*p['axisZ'][i] for i in range(2)]
models={'P11':[(-.8,.8,-.275,.275,.08,.48),(-.7,-.55,-.23,.23,0,.08),(.55,.7,-.23,.23,0,.08),(-.7,.7,-.22,.22,.48,.75)],'P12':[(-2,2,-.75,.75,2.45,2.6),(-1.85,-1.75,-.6,-.5,0,2.45),(1.75,1.85,-.6,-.5,0,2.45),(-1.85,-1.75,.5,.6,0,2.45),(1.75,1.85,.5,.6,0,2.45),(-1.75,1.75,-.59,-.54,.2,2.3),(-1.84,-1.79,-.5,.5,.2,2.3)]}
for id,boxes in models.items():
 pts=[raw(s,t,z) for a,b,d,e,f,g in boxes for s in [a,b] for t in [d,e] for z in [f,g]];lo=[min(v[i] for v in pts) for i in range(2)];hi=[max(v[i] for v in pts) for i in range(2)];scale=min(720/(hi[i]-lo[i]) for i in range(2));offset=[512-(hi[i]+lo[i])/2*scale for i in range(2)]
 def project(s,t,z):return tuple(raw(s,t,z)[i]*scale+offset[i] for i in range(2))
 im=Image.new('RGB',(1024,1024),'white');dr=ImageDraw.Draw(im)
 # painter ordering: wind panels and legs before opaque roof
 order=boxes if id=='P11' else boxes[1:]+boxes[:1]
 for a,b,d,e,f,g in order:
  v=[project(a,d,f),project(b,d,f),project(b,e,f),project(a,e,f),project(a,d,g),project(b,d,g),project(b,e,g),project(a,e,g)]
  for inds,fill in [([0,3,7,4],'#b8c4ca'),([3,2,6,7],'#d6e1e7'),([4,5,6,7],'#9eafb9')]:dr.polygon([v[i] for i in inds],fill=fill,outline='#54626a',width=2)
 dr.text((40,35),id+' GEOMETRY ONLY; not final art',fill='black');im.save(out/(id+'-geometry.png'))
 (out/(id+'-geometry.json')).write_text(json.dumps(dict(candidateOnly=True,boxes=boxes,projection=c['projection'],u=u,n=n,scale=scale,offset=offset,groundCenter=project(0,0,0)),indent=2))
src=base.parent/'2026-11-04-county-twentyfive-region-plan/review-009/TR-33-v1.png';box=[380,188,685,391];Image.open(src).crop(box).save(out/'TR33-style-context.png')
(out/'source.json').write_text(json.dumps(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),imageNumber=3,region='TR-33',version='v1',styleContextBox=box,identity='参考画风下原创补充；不是物件身份框，未编造物件bbox',role='paint/daylight material only, never composition/camera'),ensure_ascii=False,indent=2))
