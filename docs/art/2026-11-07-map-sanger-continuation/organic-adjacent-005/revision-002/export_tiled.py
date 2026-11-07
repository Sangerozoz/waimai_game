"""Export this revision with installed Tiled CLI, without opening GUI or game."""
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='tiled-cli-001')
    args = parser.parse_args()
    assert args.out.startswith('tiled-cli-') and '/' not in args.out
    output = HERE / 'verification' / args.out
    output.mkdir(parents=True, exist_ok=False)
    commands = []
    cases = [('native', ['--hide-object-layers'])]
    for name, layer in [('roads', 'visible-asphalt-trace'), ('main', 'main-route'), ('alternative', 'alternative-route')]:
        cases.append((name, ['--ignore-visibility', '--show-layer', '005 unchanged native', '--show-layer', layer]))
    for name, flags in cases:
        argv = [str(EXE), '--scale', '1', '--no-smoothing', *flags, str(HERE / 'tiled/native005.tmj'), str(output / (name + '.png'))]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=25)
        commands.append({'case': name, 'argv': argv, 'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        (output / 'commands.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2) + '\n')
        assert result.returncode == 0, commands[-1]
    source = Image.open(HERE.parent / 'native.png')
    native = Image.open(output / 'native.png')
    exact = source.size == native.size and ImageChops.difference(source.convert('RGB'), native.convert('RGB')).getbbox() is None
    alpha = native.convert('RGBA').getchannel('A').getextrema()
    assert exact and alpha == (255, 255)
    exports = [{'file': path.name, 'bytes': path.stat().st_size, 'sha256': sha(path), 'size': list(Image.open(path).size)} for path in sorted(output.glob('*.png'))]
    report = {'recordedAt': datetime.now(timezone.utc).isoformat(), 'status': 'passed', 'appVersion': plistlib.loads(Path('/Applications/Tiled.app/Contents/Info.plist').read_bytes())['CFBundleShortVersionString'],
              'binarySHA256': sha(EXE), 'commands': len(commands), 'exports': exports, 'nativeRGBPixelExact': exact, 'nativeAlphaExtrema': alpha,
              'GUIWindowValidated': False, 'wholeSeamRegistrationComplete': False, 'formalGameTestsPerformed': False}
    (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
