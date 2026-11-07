"""Export005 evidence with installed official Tiled; never launches the game."""
import hashlib
import argparse
import json
import plistlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
EXE=Path('/Applications/Tiled.app/Contents/MacOS/tmxrasterizer')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='tiled-cli-v1');args=parser.parse_args()
    assert '/'not in args.out and args.out.startswith('tiled-cli-')
    OUT=HERE/'verification'/args.out
    OUT.mkdir(parents=True,exist_ok=False)
    commands=[]
    cases=[('005-native','native005.tmj',['--hide-object-layers']),
           ('004-native','native004-partial.tmj',['--hide-object-layers']),
           ('pair-native','organic-pair.tmj',['--hide-object-layers']),
           ('pair-roads','organic-pair.tmj',['--ignore-visibility','--show-layer','005-native','--show-layer','004-native','--show-layer','visible-asphalt-trace']),
           ('pair-main','organic-pair.tmj',['--ignore-visibility','--show-layer','005-native','--show-layer','004-native','--show-layer','main-route']),
           ('pair-alternative','organic-pair.tmj',['--ignore-visibility','--show-layer','005-native','--show-layer','004-native','--show-layer','alternative-route'])]
    for name,source,flags in cases:
        argv=[str(EXE),'--scale','1','--no-smoothing',*flags,str(HERE/'tiled'/source),str(OUT/(name+'.png'))]
        r=subprocess.run(argv,capture_output=True,text=True,timeout=25)
        commands.append({'case':name,'argv':argv,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        (OUT/'commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
        if r.returncode:raise RuntimeError(commands[-1])
    comparisons=[]
    for name,src in [('005-native',HERE/'native.png'),('004-native',HERE.parent/'organic-layout-004/native.png'),('pair-native',HERE/'assembly/pair-diagnostic.png')]:
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
            'officialCLIReadExportVerified':True,'GUIWindowValidated':False,'wholeSeamReady':False,'formalGameTestsPerformed':False}
    (OUT/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'appVersion':report['appVersion'],'commands':len(commands),'exports':len(exports),'exactBackgrounds':len(comparisons)},ensure_ascii=False))


if __name__=='__main__':main()
