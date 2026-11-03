from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math
R=Path('docs/art/2026-11-03-county-region-atlas/registration');O=R/'diagnostic';src=Path('docs/art/2026-11-03-county-region-atlas/images/REGION-B-v3.png');im=Image.new('RGBA',(1254,1400),'#20202aff');a=Image.open(src).convert('RGBA');im.alpha_composite(a);overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay)
# Only diagnostic markings; no generated art is edited.
red=[(220,509),(330,455),(420,411),(498,373)]
d.line(red,fill=(255,30,40,75),width=52,joint='curve');d.line(red,fill=(255,30,40,240),width=4,joint='curve')
for p in red:d.ellipse((p[0]-6,p[1]-6,p[0]+6,p[1]+6),fill='#ff3344')
old=[(351,390),(448,314),(553,348),(560,453),(518,482),(518,566),(426,551),(358,493)]
d.polygon(old,fill=(50,120,255,45),outline=(60,150,255,255),width=4)
# One compact stepped group is allowed to be redrawn here. Ground footprint, not roof.
new=[(403,531),(529,608),(571,559),(445,486)]
d.polygon(new,fill=(50,150,255,45),outline=(80,180,255,255),width=4)
d.line([(470,425),(483,517)],fill='#66baff',width=5);d.polygon([(483,517),(470,500),(493,498)],fill='#66baff')
# Existing fixed source projection of north street (cyan): must not become a fake road through a roof.
f=json.load(open(R/'registration-B-v2.json'))['fit'];q=math.sqrt(.5);st=math.sin(math.radians(62.5));ori=f['anchorMap'];P=f['nativePixelsPerUnit'];anchor=f['anchorPixel']
def proj(p):x,y=p[0]-ori[0],p[1]-ori[1];return (anchor[0]+P*(x-y)*q,anchor[1]+P*(x+y)*st*q)
cyan=[proj(p) for p in [[-1528.97,107.99],[-1517.43,50.57],[-1511.8168891435118,20]]]
d.line(cyan,fill=(0,245,235,255),width=3)
# Put red line on top of projected line where it is the immediate A/B seam correction.
d.line(red,fill=(255,30,40,255),width=4,joint='curve')
try:font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18);small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
except:font=small=ImageFont.load_default()
def label(p,text,color):
 b=d.textbbox((0,0),text,font=font);d.rectangle([p[0]-4,p[1]-3,p[0]+b[2]+5,p[1]+b[3]+3],fill=(20,20,28,240));d.text(p,text,font=font,fill=color)
label((45,455),'1. JUNCTION (220,509)','#ff8888');label((525,364),'2. SEAM NORTH (498,373)','#ff8888')
label((45,350),'BLUE: redraw/relocate WHOLE group','#88bbff');label((390,620),'GROUND target footprint; roofs must clear red','#88bbff')
label((735,160),'CYAN: unchanged source road projection','#66ffef')
label((25,1230),'DIAGNOSTIC REFERENCE ONLY - NOT GAME ART','#ffffff')
lines=['RED = required shared-road centre from A. 34px asphalt; ~52px including sidewalks.',
'Clear the RED band. Relocate/rebuild blue group as a compact stepped whole on blue ground footprint.',
'Keep ~6m ground setback (~41px) from road centre; no roof may cover the route.',
'Relocate/remove tiny courtyard kiosk if it conflicts; preserve right half and main east junction.',
'CYAN upstream remains unready. Do not bend the source route around buildings or move source map.',
'Native B3 is untouched. All coordinates are on its 1254 x 1254 pixel canvas.']
for i,t in enumerate(lines):d.text((25,1265+i*20),t,font=small,fill='white')
im=Image.alpha_composite(im,overlay);im.convert('RGB').save(O/'B-v3-north-seam-edit-guide.png')
