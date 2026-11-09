import pathlib,json,hashlib
from PIL import Image
p=pathlib.Path(__file__).parent
rects=json.loads((p/'rects.json').read_text()); m={'assets':{}}; rec=[]
for g,rr in rects.items():
 v=2 if int(g)<3 else 1
 f=p/f'atlas-{int(g):02}-v{v}.png'; im=Image.open(f); sha=hashlib.sha256(f.read_bytes()).hexdigest()
 for i,rect in enumerate(rr):
  m['assets'][f'npc-{(int(g)-1)*6+i+1}']=dict(file=str(f),rect=rect,status='candidate',sha256=sha,nativeWidth=im.width,nativeHeight=im.height)
 rec.append(dict(file=str(f),source='built-in image_gen',prompt=f'prompt-{int(g):02}-v2.txt',reference='docs/art/2026-11-02-approved-ui-reference/01-riders-v4.png',sha256=sha,nativeSize=list(im.size),mode=im.mode,alpha='A' in im.getbands(),visualInspection=True,issues=['面部风格及三分之四视角趋同，未用户验收','发顶与格上沿余量较紧','单格比例约0.64，运行需等比填充或留边']))
(p/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(p/'generation-records.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
r=json.loads((p/'roster.json').read_text())
for a in r['characters']:
 if a['id'] in m['assets']: a.update(resource=m['assets'][a['id']]['file'],rect=m['assets'][a['id']]['rect'])
(p/'roster.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print('candidate IDs',len(m['assets']))
