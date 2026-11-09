from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil
b=Path(__file__).resolve().parents[2]; id=sys.argv[1]; o=b/'native'/f'{id}-001'; p=o/'provenance.json'; r=json.loads(p.read_text()); s=Path(r['toolSourceAbsolutePath']); t=o/f'{id}-v1.png'; assert not t.exists(); shutil.copyfile(s,t); im=Image.open(t)
r.update(actualSize=list(im.size),mode=im.mode,alphaExtrema=im.getchannel('A').getextrema() if 'A' in im.getbands() else None,nativeBytes=t.stat().st_size,sourceCopySHA256=hashlib.sha256(t.read_bytes()).hexdigest(),byteIdenticalVerified=s.read_bytes()==t.read_bytes(),submittedReferenceSHA256={x:hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in r['referenced_image_paths']},dimensionMeaning='PM-game-scale-candidate-not-source-measured',sourceStyleRecord=json.loads((b/'references/garden/style-source.json').read_text()))
p.write_text(json.dumps(r,ensure_ascii=False,indent=2));print(r['actualSize'],r['mode'],r['nativeBytes'],r['sourceCopySHA256'])
