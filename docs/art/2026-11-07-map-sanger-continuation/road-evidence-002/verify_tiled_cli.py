#!/usr/bin/env python3
"""Render these isolated TMJs through the installed official Tiled CLI."""
import hashlib
import json
import plistlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
EXE = Path('/Applications/Tiled.app/Contents/MacOS/tmxrasterizer')
OUT = HERE/'verification/tiled-cli-v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    commands = []
    version = subprocess.run([str(EXE), '--version'], capture_output=True, text=True, timeout=20)
    commands.append({'argv': [str(EXE), '--version'], 'exitCode': version.returncode,
                     'stdout': version.stdout, 'stderr': version.stderr})
    cases = [
        ('actual-background', 'actual-eight.tmj', ['--hide-object-layers']),
        ('actual-road-overlay', 'actual-eight.tmj', []),
        ('actual-alternative-route', 'actual-eight.tmj', ['--ignore-visibility', '--show-layer', 'native-art', '--show-layer', 'geometric-alternative-route']),
        ('planning-background', 'whole-city-planning.tmj', ['--hide-object-layers']),
        ('planning-road-overlay', 'whole-city-planning.tmj', []),
    ]
    for name, source, flags in cases:
        argv = [str(EXE), '--scale', '1', '--no-smoothing', *flags,
                str(HERE/'tiled'/source), str(OUT/(name+'.png'))]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        commands.append({'case': name, 'argv': argv, 'exitCode': result.returncode,
                         'stdout': result.stdout, 'stderr': result.stderr})
    (OUT/'commands.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2)+'\n')
    assert all(r['exitCode'] == 0 for r in commands), commands
    comparisons = []
    for name, source in [
        ('actual-background', HERE.parent/'builtin-capacity-002/native.png'),
        ('planning-background', HERE/'tiled/plan-schematic.png'),
    ]:
        with Image.open(OUT/(name+'.png')) as rendered, Image.open(source) as original:
            same_size = rendered.size == original.size
            difference = ImageChops.difference(rendered.convert('RGB'), original.convert('RGB')) if same_size else None
            exact = same_size and difference.getbbox() is None
            comparisons.append({'case': name, 'renderedSize': list(rendered.size), 'sourceSize': list(original.size),
                                'RGBPixelForPixelExact': exact, 'sourceSHA256': sha(source)})
            assert exact, comparisons[-1]
    exports = []
    for p in sorted(OUT.glob('*.png')):
        with Image.open(p) as im:
            exports.append({'file': p.name, 'size': list(im.size), 'mode': im.mode, 'bytes': p.stat().st_size, 'sha256': sha(p)})
    app_version = plistlib.loads(Path('/Applications/Tiled.app/Contents/Info.plist').read_bytes())['CFBundleShortVersionString']
    report = {'recordedAt': datetime.now(timezone.utc).isoformat(), 'status': 'passed', 'appVersion': app_version,
              'binary': str(EXE), 'binarySHA256': sha(EXE), 'versionOutput': version.stdout.strip(),
              'commandCount': len(commands), 'exports': exports, 'comparisons': comparisons,
              'readExportThroughOfficialCLI': True, 'nativeGUIValidated': False,
              'formalGameTestsPerformed': False}
    (OUT/'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
