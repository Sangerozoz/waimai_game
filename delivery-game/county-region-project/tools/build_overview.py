"""Deterministic runtime-only overview from real region RGBA sources; never edits source art."""
from pathlib import Path
import hashlib,json,math
from PIL import Image,ImageDraw,ImageChops

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def build_overview(atlas,output,max_size=2048):
 if not 64<=max_size<=4096:raise ValueError('Overview max dimension must be 64..4096')
 if atlas['projection']['elevationDeg']!=62.5 or atlas['projection']['azimuthDeg']!=45:raise ValueError('Unsupported fixed projection')
 origin=atlas['projection']['originMap']
 def project(p):
  x,y=p[0]-origin[0],p[1]-origin[1]
  return ((x-y)*.7071067812,(x+y)*.6272113751)
 ordered=sorted(atlas['regions'],key=lambda r:(r['sortOrder'],r['id']))
 bounds=[]
 for r in ordered:
  x,y=project(r['anchorMap']);w,h=[v/r['nativePixelsPerUnit'] for v in r['nativeSize']]
  bounds.append((x-r['anchorUV'][0]*w,y-r['anchorUV'][1]*h,x+(1-r['anchorUV'][0])*w,y+(1-r['anchorUV'][1])*h))
 left,top=min(b[0] for b in bounds),min(b[1] for b in bounds)
 right,bottom=max(b[2] for b in bounds),max(b[3] for b in bounds)
 # Leave one transparent pixel on each edge; a single uniform scale for both axes.
 ppm=min((max_size-2)/(right-left),(max_size-2)/(bottom-top),min(r['nativePixelsPerUnit'] for r in ordered))
 left-=1/ppm;top-=1/ppm
 width=min(max_size,math.ceil((right-left)*ppm)+1);height=min(max_size,math.ceil((bottom-top)*ppm)+1)
 result=Image.new('RGBA',(width,height),(0,0,0,0));sources=[]
 for r,b in zip(ordered,bounds):
  path=output/r['file']
  if digest(path)!=r['sha256']:raise ValueError('Source SHA mismatch '+r['id'])
  with Image.open(path) as raw:
   if list(raw.size)!=r['nativeSize']:raise ValueError('Native size mismatch '+r['id'])
   im=raw.convert('RGBA')
  ownership=r.get('ownershipPolygonUV')
  if ownership:
   mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).polygon([(p[0]*im.width,p[1]*im.height) for p in ownership],fill=255)
   im.putalpha(ImageChops.multiply(im.getchannel('A'),mask))
  # Output-pixel -> native-pixel inverse affine: identical scale on X/Y, no rotation/warp.
  scale=r['nativePixelsPerUnit']/ppm
  affine=(scale,0,(left-b[0])*r['nativePixelsPerUnit'],0,scale,(top-b[1])*r['nativePixelsPerUnit'])
  layer=im.transform(result.size,Image.Transform.AFFINE,affine,Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
  result.alpha_composite(layer)
  sources.append({'id':r['id'],'file':r['file'],'sha256':r['sha256'],'anchorMap':r['anchorMap'],'anchorUV':r['anchorUV'],'nativePixelsPerUnit':r['nativePixelsPerUnit'],'sortOrder':r['sortOrder'],'ownershipPolygonUV':ownership,'projectedImageBounds':list(b)})
 folder=output/'derived';folder.mkdir(exist_ok=True)
 image=folder/'overview.png';result.save(image)
 spec={'file':'derived/overview.png','sha256':digest(image),'nativeSize':[width,height],'pixelsPerUnit':ppm,'projectedTopLeft':[left,top],'sourceRegionIds':[r['id'] for r in ordered],'maxTextureSize':max_size,'evidenceFile':'derived/overview-record.json'}
 record={'schemaVersion':1,'purpose':'runtime-derived-display-only; never navigation/registration','generator':'tools/build_overview.py','generatorSHA256':digest(Path(__file__)),'pillowVersion':Image.__version__,'projection':atlas['projection'],'overview':spec,'sources':sources,'composition':'ascending sortOrder then id; native alpha intersect ownership; uniform affine to shared projected canvas; transparent unmade space','limitations':['overview raster/resampling edges may differ by subpixel from native browser clipping','no art correction or new geometry','no runtime/browser/game verification']}
 (folder/'overview-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 return spec
