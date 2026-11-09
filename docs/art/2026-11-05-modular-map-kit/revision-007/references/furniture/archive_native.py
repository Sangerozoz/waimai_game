from pathlib import Path
import sys,json,hashlib,shutil,subprocess
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[1];K=R.parent
id,src=sys.argv[1:];src=Path(src);out=R/'native'/(id+'-001');out.mkdir(parents=True,exist_ok=True);dst=out/(id+'-v1.png')
assert not dst.exists()
shutil.copyfile(src,dst)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):
 im=Image.open(p);return dict(path=str(p),size=list(im.size),mode=im.mode,bytes=p.stat().st_size,alphaExtrema=list(im.getchannel('A').getextrema()),alphaBBox=im.getchannel('A').getbbox(),sha256=sha(p))
a=json.loads((D/(id+'-tool-args.json')).read_text())
p=dict(tool='image_gen.imagegen',toolSourceAbsolutePath=str(src),toolArguments=a,references=[dict(path=f,sha256=sha(f)) for f in a['referenced_image_paths']],sourceSelection=json.loads((D/'style-source.json').read_text()),native=info(dst),toolSourceSHA256=sha(src),sourceCopySHA256Match=sha(src)==sha(dst),status='native-candidate-not-user-accepted-not-integrated')
assert p['sourceCopySHA256Match']
(out/'provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['python3',str(K/'revision-005/runtime-size-pilot/export_runtime.py'),'--output-dir',str(out),'--max-edge','280','--single-source',str(dst),'--single-target',str(out/(id+'-runtime-280.png'))],check=True)
p['runtime']=info(out/(id+'-runtime-280.png'));(out/'provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(native=p['native'],runtime=p['runtime']),ensure_ascii=False))
