from pathlib import Path
from PIL import Image
import hashlib,json,shutil,subprocess
BASE=Path("/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/")
def save(id,source,prompt,refs):
 out=BASE/'native'/(id+'-001');out.mkdir(parents=True,exist_ok=True);src=Path(source);dst=out/(id+'-v1.png')
 assert not dst.exists();shutil.copyfile(src,dst)
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 with Image.open(dst) as im:meta=dict(size=list(im.size),mode=im.mode,alphaExtrema=list(im.getchannel('A').getextrema()))
 p=dict(status='native-candidate-not-accepted-not-integrated',tool='image_gen.imagegen',toolSourceAbsolutePath=str(src),actualPrompt=prompt,references=[dict(path=r,sha256=sha(Path(r))) for r in refs],styleSource=json.loads((BASE/'references/public/source.json').read_text()),geometry=json.loads((BASE/'references/public'/(id+'-geometry.json')).read_text()),native=meta,bytes=dst.stat().st_size,sourceSHA256=sha(src),sourceCopySHA256=sha(dst),byteIdentical=sha(src)==sha(dst),nativeCalls=1)
 (out/'provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
 subprocess.run(['python3',str(BASE.parent/'revision-005/runtime-size-pilot/export_runtime.py'),'--output-dir',str(out),'--max-edge','280','--single-source',str(dst),'--single-target',str(out/(id+'-runtime-280.png'))],check=True)
 print(id,meta)
if __name__=='__main__':
 save('P01','/Users/sanger/.codex/generated_images/01a1ac1c-02e8-76f0-b1d9-82f4dab00260/exec-00a3e8f6-c960-4af0-902d-91550f9313e1.png',"Create exactly ONE native transparent game prop P01: small freestanding unlit lightbox sign, simple matte charcoal metal pedestal and base plate, rectangular blank off-white frosted panel inside thin metal frame. No writing, no logo, no illumination, not a streetlight. Image 1 is hard geometry/camera/footprint reference ONLY, do not copy its proxy shading or labels; image 2 is local painted style/material reference ONLY, do not copy buildings/streets. Original supplemental prop under the approved TR33 painting style, not extracted source identity. Orthographic high oblique camera: frontage u edges -28.486362689 screen degrees, depth n +55.405984491 degrees, vertical edges screen vertical; preserve exact guide chirality. Candidate world envelope 0.65u x0.4n x1.45z metres, not surveyed. Paint as daytime Japanese urban anime thick-painted background sprite: simplified deliberate brush shading, restrained edge definition, soft upper-left daylight, muted material tones. Not photoreal product photography, not glossy reflective metal, not flat vector icon or heavy cartoon outlines. Complete base and body visible with generous margin. True transparent RGBA outside object, no ground plane, no broad baked shadow, no people/cars/trees/sky, no studio backdrop, no vignette, no text or guide marks. One object only.",["/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/references/public/P01-geometry.png","/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/references/public/TR33-style-context.png"])

