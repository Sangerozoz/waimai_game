from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys,subprocess
D=json.loads(sys.argv[1]); p=Path(D['dir']);p.mkdir(parents=True,exist_ok=True); s=Path(D['toolSource']); f=p/(D['id']+'-'+D['ver']+'.png');shutil.copyfile(s,f)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(f);D.update(tool='image_gen.imagegen',size=list(im.size),mode=im.mode,alphaExtrema=list(im.getchannel('A').getextrema()),bytes=f.stat().st_size,sourceSHA=sha(s),copySHA=sha(f),byteIdentical=s.read_bytes()==f.read_bytes(),references=[{'path':x,'sha256':sha(x)} for x in D['refs']],status='candidate-not-integrated-not-user-accepted',dimensions='PM candidate not source measurement')
(p/'provenance.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
rt=p/(D['id']+('-v2' if D['ver']=='v2' else '')+'-runtime-280.png')
subprocess.run(['python3','docs/art/2026-11-05-modular-map-kit/revision-005/runtime-size-pilot/export_runtime.py','--output-dir',str(p),'--max-edge','280','--single-source',str(f),'--single-target',str(rt)],check=True)
print(str(rt))
