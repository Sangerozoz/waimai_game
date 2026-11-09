import json,hashlib,shutil,sys
from pathlib import Path
from PIL import Image
d=Path(__file__).parent
v=json.loads(sys.argv[1]); src=Path(v['source']); dst=d/v['file']; shutil.copy2(src,dst)
im=Image.open(dst); a=im.getchannel('A') if 'A' in im.getbands() else Image.new('L',im.size,255)
bbox=a.point(lambda x:255 if x>16 else 0).getbbox()
meta=dict(width=im.width,height=im.height,mode=im.mode,alphaExtrema=list(a.getextrema()),alphaGt16BBox=list(bbox),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),status='candidate')
entry=dict(id=v['id'],file=v['file'],rect=v['rect'],inset=v['inset'],**meta,rectUnits='native pixels, top-left origin x/y/w/h',insetUnits='native pixels relative to rect',notes=v.get('notes','Native unchanged; provisional slice; exterior low-alpha noise possible. No 98% certification.'))
if 'sprites' in v: entry['sprites']=v['sprites']
p=d/'manifest.json'; m=json.load(open(p)); m['assets'].append(entry); p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
p=d/'generation-records.json'; r=json.load(open(p)); ref=Path(v['reference']); r.append(dict(id=v['id'],tool='builtin image_gen',prompt=v['prompt'],originalOutput=str(src),projectFile=v['file'],references=[dict(path='../2026-11-02-approved-ui-reference/'+ref.name,sha256=hashlib.sha256(ref.read_bytes()).hexdigest())],**meta)); p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(entry))

