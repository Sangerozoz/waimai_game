"""Diagnostic only: uniformly placed native art and common-map clipping proposal."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;B=O.parent.parent;q=math.sqrt(.5);st=math.sin(math.radians(62.5));P=4
entries=[json.loads((B/f).read_text())for f in ['registration/region-A-AB-v4-runtime-entry.json','registration/region-B-v4-runtime-entry.json','repairs/C/region-entry.json','repairs/D/region-D-runtime-entry.json']]
arts=[B.parent/'2026-11-03-whole-region-map/REGION-A-v3.png',B/'images/REGION-B-v4.png',O/'REGION-C-v3.png',B/'repairs/D/REGION-D-v4.png']
def world(p):
 x,y=p[0]+1580,p[1]-80;return (700+P*q*(x-y),400+P*q*st*(x+y))
def inverse(uv,e):
 x=(uv[0]*1254-e['anchorUV'][0]*1254)/e['nativePixelsPerUnit'];y=(uv[1]*1254-e['anchorUV'][1]*1254)/e['nativePixelsPerUnit']/st
 return [e['anchorMap'][0]+q*(x+y),e['anchorMap'][1]+q*(y-x)]
def clip(poly,dim,val,le):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=(a[dim]<=val)if le else(a[dim]>=val);ib=(b[dim]<=val)if le else(b[dim]>=val)
  if ia:out.append(a)
  if ia!=ib:
   t=(val-a[dim])/(b[dim]-a[dim]);out.append([a[k]+t*(b[k]-a[k])for k in [0,1]])
 return out
ab=json.loads((B/'registration/A-B-v4-production-handoff.json').read_text());polys={}
for e in entries:
 id=e['id'];native=[inverse(uv,e)for uv in [[0,0],[1,0],[1,1],[0,1]]]
 if id in ab['sourceMapPolygons']:poly=clip(ab['sourceMapPolygons'][id],1,132,True)
 else:poly=clip(clip(native,1,132,False),0,-1535.3,id=='REGION-C')
 polys[id]=poly
im=Image.new('RGB',(1400,1500),'#33343b')
for e,f in zip(entries,arts):
 art=Image.open(f);scale=P/e['nativePixelsPerUnit'];nw=round(1254*scale);art=art.resize((nw,nw),Image.Resampling.LANCZOS);anchor=world(e['anchorMap']);xy=(round(anchor[0]-e['anchorUV'][0]*nw),round(anchor[1]-e['anchorUV'][1]*nw))
 layer=Image.new('RGBA',im.size);layer.paste(art,xy);mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon([world(p)for p in polys[e['id']]],fill=255);alpha=layer.getchannel('A');import PIL.ImageChops
 mask=PIL.ImageChops.multiply(mask,alpha);im.paste(layer,mask=mask)
d=ImageDraw.Draw(im);d.text((20,20),'ABCD common-map ownership DRAFT: diagnostic, NOT runtime screenshot',fill='white')
for id,poly in polys.items():d.line([world(p)for p in poly+[poly[0]]],fill='magenta',width=2)
im.save(O/'ABCD-ownership-DRAFT.jpg')
(O/'ownership-DRAFT.json').write_text(json.dumps({'status':'draft-needs-visual-check','sourceMapPolygons':polys,'note':'AB existing contour retained above y132; A/C and B/D split y132; C/D x=-1535.3. This may cut buildings and is not approved.'},indent=2)+'\n')
