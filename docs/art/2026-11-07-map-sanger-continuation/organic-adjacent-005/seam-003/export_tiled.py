"""Read the editable pair in installed Tiled and export map-only evidence."""
import hashlib
import json
import plistlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
EXE = Path('/Applications/Tiled.app/Contents/MacOS/tmxrasterizer')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = HERE / 'verification/tiled-cli-001'
    output.mkdir(parents=True,exist_ok=False)
    cases = [('native',['--hide-object-layers'])]
    for name,layer in [('roads','visible-asphalt-trace'),('main','main-route'),('alternative','alternative-route')]:
        cases.append((name,['--ignore-visibility','--show-layer','004 unchanged native','--show-layer','005 selected native pixels','--show-layer',layer]))
    commands = []
    tiled_sha = sha(HERE/'tiled/organic-pair.tmj')
    for name,flags in cases:
        argv = [str(EXE),'--scale','1','--no-smoothing',*flags,str(HERE/'tiled/organic-pair.tmj'),str(output/(name+'.png'))]
        result = subprocess.run(argv,capture_output=True,text=True,timeout=25)
        commands.append({'case':name,'argv':argv,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        (output/'commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
        assert result.returncode==0,commands[-1]
    source = Image.open(HERE/'assembly/pair-native.png')
    rendered = Image.open(output/'native.png')
    exact = source.size==rendered.size and ImageChops.difference(source.convert('RGB'),rendered.convert('RGB')).getbbox() is None
    alpha = rendered.convert('RGBA').getchannel('A').getextrema()
    assert exact and alpha==(255,255)
    report = {'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'passed',
              'appVersion':plistlib.loads(Path('/Applications/Tiled.app/Contents/Info.plist').read_bytes())['CFBundleShortVersionString'],
              'binarySHA256':sha(EXE),'tiledSHA256':tiled_sha,'commands':len(commands),
              'exports':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'size':list(Image.open(p).size)} for p in sorted(output.glob('*.png'))],
              'nativeRGBPixelExact':exact,'nativeAlphaExtrema':alpha,'GUIWindowValidated':False,'wholeSeamReady':False,'formalGameTestsPerformed':False}
    (output/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':
    main()
