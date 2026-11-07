"""One Tiled native-background export; no GUI or game."""
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
    output = HERE / 'verification/tiled-native-001'
    output.mkdir(parents=True, exist_ok=False)
    tiled = HERE / 'tiled/native006.tmj'
    argv = [str(EXE), '--scale', '1', '--no-smoothing', '--hide-object-layers', str(tiled), str(output / 'native.png')]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=25)
    command = {'argv': argv, 'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    (output / 'command.json').write_text(json.dumps(command, ensure_ascii=False, indent=2) + '\n')
    assert result.returncode == 0, command
    original = Image.open(HERE / 'native.png')
    rendered = Image.open(output / 'native.png')
    exact = original.size == rendered.size and ImageChops.difference(original.convert('RGB'), rendered.convert('RGB')).getbbox() is None
    alpha = rendered.convert('RGBA').getchannel('A').getextrema()
    assert exact and alpha == (255,255)
    report = {'recordedAt': datetime.now(timezone.utc).isoformat(), 'status': 'passed',
              'appVersion': plistlib.loads(Path('/Applications/Tiled.app/Contents/Info.plist').read_bytes())['CFBundleShortVersionString'],
              'tiledSHA256': sha(tiled), 'binarySHA256': sha(EXE), 'commands': 1, 'exports': 1,
              'exportSHA256': sha(output / 'native.png'), 'size': list(rendered.size),
              'nativeRGBPixelExact': exact, 'alphaExtrema': alpha, 'GUIWindowValidated': False,
              'actualNavigationReady': False, 'formalGameTestsPerformed': False}
    (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
