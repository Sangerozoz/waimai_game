"""Use installed official Tiled only for this isolated map proof."""
import hashlib
import json
import plistlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
EXE=Path('/Applications/Tiled.app/Contents/MacOS/tmxrasterizer')
OUT=HERE/'verification/tiled-cli-v2'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    commands=[]
    cases=[('W-native','W-native.tmj',['--hide-object-layers']),
           ('E-native','E-native.tmj',['--hide-object-layers']),
           ('pair-native','adjacent-pair.tmj',['--hide-object-layers']),
           ('pair-roads','adjacent-pair.tmj',['--ignore-visibility','--show-layer','W-owned-native-core','--show-layer','E-owned-native-core','--show-layer','traced-roads']),
           ('pair-main','adjacent-pair.tmj',['--ignore-visibility','--show-layer','W-owned-native-core','--show-layer','E-owned-native-core','--show-layer','main-route']),
           ('pair-alternative','adjacent-pair.tmj',['--ignore-visibility','--show-layer','W-owned-native-core','--show-layer','E-owned-native-core','--show-layer','alternative-route'])]
    for name,source,flags in cases:
        argv=[str(EXE),'--scale','1','--no-smoothing',*flags,str(HERE/'tiled'/source),str(OUT/(name+'.png'))]
        r=subprocess.run(argv,capture_output=True,text=True,timeout=25)
        commands.append({'case':name,'argv':argv,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        (OUT/'commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
        if r.returncode:raise RuntimeError(commands[-1])
    comparisons=[]
    for name,src in [('W-native',HERE/'W/native.png'),('E-native',HERE/'E/native.png'),('pair-native',HERE/'assembly/pair-native-pixels.png')]:
        original=Image.open(src).convert('RGB');rendered=Image.open(OUT/(name+'.png'))
        exact=rendered.size==original.size and ImageChops.difference(rendered.convert('RGB'),original).getbbox()is None
        alpha=rendered.convert('RGBA').getchannel('A').getextrema()
        comparisons.append({'case':name,'actualSize':list(rendered.size),'sourceSHA256':sha(src),'RGBPixelExact':exact,'alphaExtrema':alpha})
        assert exact and alpha==(255,255),comparisons[-1]
    exports=[]
    for p in sorted(OUT.glob('*.png')):
        im=Image.open(p);exports.append({'file':p.name,'size':list(im.size),'mode':im.mode,'bytes':p.stat().st_size,'sha256':sha(p)})
    report={'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','appVersion':plistlib.loads(Path('/Applications/Tiled.app/Contents/Info.plist').read_bytes())['CFBundleShortVersionString'],
            'binary':str(EXE),'binarySHA256':sha(EXE),'commands':len(commands),'exports':exports,'comparisons':comparisons,
            'officialCLIReadExportVerified':True,'GUIWindowValidated':False,'formalGameTestsPerformed':False}
    (OUT/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
