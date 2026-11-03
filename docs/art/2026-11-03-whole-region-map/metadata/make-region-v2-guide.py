"""Fresh code-native geometry guide. Neutral unassigned land is not a park instruction."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
base=json.loads((R/'region-A-structure.json').read_text())
proj=base['projection'];origin=base['originMap'];ppu=proj['nativePixelsPerUnit'];off=proj['originPixel']
def project(p):
    x,y=p[0]-origin[0],p[1]-origin[1];z=p[2] if len(p)>2 else 0
    return [off[i]+ppu*(x*proj['axisX'][i]+y*proj['axisY'][i]+z*proj['axisZ'][i]) for i in range(2)]
im=Image.new('RGBA',(1536,1536),(0,0,0,0));dr=ImageDraw.Draw(im)
ground=[[-1640,20],[-1520,20],[-1520,140],[-1640,140]]
dr.polygon([tuple(project(p)) for p in ground],fill='#dfdad1')
def corridor(part,width,color):
    a,b=part;dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    if length<1e-8:return
    nx,ny=-dy/length*width/2,dx/length*width/2
    poly=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]]
    dr.polygon([tuple(project(p)) for p in poly],fill=color)
for road in base['roads']:
    for part in road['displaySegments']:corridor(part,road['width']+3.6,'#c4bfae')
for road in base['roads']:
    for part in road['displaySegments']:corridor(part,road['width'],'#828887')
for b in sorted(base['buildingReferences'],key=lambda b:sum(project(p)[1] for p in b['footprint'])/len(b['footprint'])):
    foot=b['footprint'];top=[p+[b['heightNominal']] for p in foot];faces=[]
    for j in range(len(foot)):
        k=(j+1)%len(foot);faces.append(([foot[j],foot[k],top[k],top[j]],sum(project(p)[1] for p in [foot[j],foot[k]])))
    for face,_ in sorted(faces,key=lambda f:f[1]):dr.polygon([tuple(project(p)) for p in face],fill='#d0cbbf',outline='#9f9d94')
    dr.polygon([tuple(project(p)) for p in top],fill='#f4f0e7',outline='#989c96',width=2)
path=R/'guides/region-A-structure-v2-neutral.png';im.save(path)
meta={'id':'REGION-A-v2-geometry','sourceStructure':'region-A-structure.json','sourceStructureSHA256':hashlib.sha256((R/'region-A-structure.json').read_bytes()).hexdigest(),'file':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'nativeSize':list(im.size),'projection':proj,'buildingReferences':len(base['buildingReferences']),'roadCount':len(base['roads']),'notes':['Neutral taupe open areas are unassigned urban plots, not green land or a demand for huge paved plazas.','Whole-region painter may complete these plots with varied candidate urban buildings/courtyards while preserving all source roads and boundary controls.','Guide boxes give structural position and camera only; their repeated form is not architectural style.','No existing PNG pixels edited; new guide authored from geometry.']}
(R/'metadata/region-A-v2-guide.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(meta,ensure_ascii=False,indent=2))
