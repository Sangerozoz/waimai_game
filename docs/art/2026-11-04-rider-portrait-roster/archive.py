import pathlib,json,hashlib,sys
from PIL import Image
p=pathlib.Path(__file__).parent
g=int(sys.argv[1]); f=p/f'atlas-{g:02}-v1.png'
im=Image.open(f); print(f, im.size, im.mode)
rects=[[27,28,381,585],[437,28,381,585],[846,28,381,585],[27,643,381,585],[437,643,381,585],[846,643,381,585]]
m=json.loads((p/'manifest.json').read_text()) if (p/'manifest.json').exists() else {'assets':{}}
sha=hashlib.sha256(f.read_bytes()).hexdigest()
for i,rect in enumerate(rects):
 m['assets'][f'npc-{(g-1)*6+i+1}']=dict(file=str(f),rect=rect,status='candidate',sha256=sha,nativeWidth=im.width,nativeHeight=im.height)
(p/'manifest.json').write_text(json.dumps(m,indent=2))
