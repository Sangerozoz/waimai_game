from PIL import Image,ImageDraw
import math
from pathlib import Path
p=Path(__file__).resolve().parent
for angle in [0,90,180,270]:
 im=Image.new('RGB',(1254,1254),'white');d=ImageDraw.Draw(im);a=math.sin(math.radians(62.5));h=math.cos(math.radians(62.5));scale=44
 def pt(x,y,z):return (627+(x-y)/math.sqrt(2)*scale,735+(x+y)/math.sqrt(2)*a*scale-z*h*scale)
 def rot(x,y):
  t=math.radians(angle);return (x*math.cos(t)-y*math.sin(t),x*math.sin(t)+y*math.cos(t))
 def box(x0,y0,x1,y1,z0,z1):
  xy=[rot(x,y) for x,y in [(x0,y0),(x0,y1),(x1,y0),(x1,y1)]];x0=min(q[0] for q in xy);x1=max(q[0] for q in xy);y0=min(q[1] for q in xy);y1=max(q[1] for q in xy)
  polys=[([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],'#dedbd0'), ([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],'#bbbcb7'), ([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],'#a9b1be')]
  for pts,col in polys:d.polygon([pt(*q) for q in pts],fill=col,outline='#334455',width=3)
 box(-8,-5.5,8,5.5,0,8);box(-6.5,-4,-3.5,-1,8,10);box(3.5,-4,5,-2.5,8,8.7);box(5.5,-4,7,-2.5,8,8.7)
 im.save(p/f'B01-F{angle:02d}-guide.png')
