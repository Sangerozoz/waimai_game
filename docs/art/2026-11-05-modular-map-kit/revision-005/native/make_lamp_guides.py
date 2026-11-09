#!/usr/bin/env python3
"""Geometric lamp orientation references, not final art. No source PNG edits."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
constraint = json.loads((HERE.parents[1]/'revision-003/road-constraint.json').read_text())
p = constraint['projection']; u = constraint['streetTangentMap']; n = [-u[1], u[0]]
ppu = 220.0; origin = [768.0, 1280.0]

def project(a, b, z):
    world = [a*u[i]+b*n[i] for i in (0, 1)]
    return [origin[i]+ppu*(world[0]*p['axisX'][i]+world[1]*p['axisY'][i]+z*p['axisZ'][i]) for i in (0, 1)]

records=[]
for label, sign in [('near', 1), ('far', -1)]:
    im=Image.new('RGBA',(1536,1536),(0,0,0,0)); d=ImageDraw.Draw(im)
    foot=[project(a,b,0.02) for a,b in [(-.16,-.16),(.16,-.16),(.16,.16),(-.16,.16)]]
    d.polygon(foot,fill='#606970',outline='#3e4852',width=3)
    shaft=[project(0,0,z) for z in [.06,7]]
    d.line([tuple(v) for v in shaft],fill='#4d5963',width=17)
    d.line([tuple(project(-.018,0,z)) for z in [.12,6.95]],fill='#77848b',width=4)
    elbow=project(0,sign*1.12,7)
    d.line([tuple(shaft[-1]),tuple(elbow)],fill='#4d5963',width=15)
    corners=[project(a,sign*b,7.02) for a,b in [(-.20,1),(.20,1),(.20,2.15),(-.20,2.15)]]
    underside=[project(a,sign*b,6.89) for a,b in [(-.20,1),(.20,1),(.20,2.15),(-.20,2.15)]]
    d.polygon(underside,fill='#dddacb',outline='#46535d',width=3)
    for j in range(4):
        k=(j+1)%4
        d.polygon([corners[j],corners[k],underside[k],underside[j]],fill='#5e6a75',outline='#46535d',width=2)
    d.polygon(corners,fill='#64717c',outline='#404d59',width=3)
    path=HERE/f'L01-road-{label}-geometry.png'
    if path.exists():raise SystemExit('Refusing to overwrite guide')
    im.save(path)
    records.append({'id':f'L01-road-{label}-v1','guide':path.name,'status':'geometry-proxy-not-native-art','guideSize':list(im.size),
      'candidatePoleHeight':7,'guidePixelsPerUnit':ppu,'guideAnchorPixel':origin,'shaftBasePixel':shaft[0],'shaftTopPixel':shaft[1],
      'headCenterPixel':project(0,sign*1.575,7.02),'armDirectionMap':[sign*v for v in n],
      'sideNormalSign':-sign,'lightOpticalDirection':'downward toward ground/carriageway','headCorners':corners})
(HERE/'lamp-guides.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(records,ensure_ascii=False))
