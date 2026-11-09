#!/usr/bin/env python3
"""Prepare C geometry and narrow references, not final artwork."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
CITY = HERE.parent.parent
BASE = CITY / 'compact-pair-v2-density/integration'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if (HERE / 'references').exists() or (HERE / 'native.png').exists() or (HERE / 'request-started.json').exists():
        raise SystemExit('Prepared input/request/output exists; preserve and inspect, never repeat.')
    known = {'README.md', 'prepare_c.py', 'generate_c.py', 'prompt.txt', 'execution-commands.json'}
    unknown = [p.name for p in HERE.iterdir() if p.name not in known]
    if unknown:
        raise SystemExit('Unknown contents: ' + repr(unknown))
    refs = HERE / 'references'
    refs.mkdir()
    protected = {}
    for directory in [CITY / 'compact-pair-v1', CITY / 'compact-pair-v2-density', CITY / 'planning']:
        protected.update({str(p): sha(p) for p in directory.rglob('*') if p.is_file()})
    (HERE / 'protected-inputs.json').write_text(json.dumps(protected, ensure_ascii=False, indent=2) + '\n')
    contract = json.loads((BASE / 'next-C/identity-and-edge-contract.json').read_text())
    (refs / 'contract-source.json').write_text(json.dumps(contract, ensure_ascii=False, indent=2) + '\n')
    band_source = BASE / 'next-C/actual-north-edge-64.png'
    shutil.copyfile(band_source, refs / 'actual-north-edge-64.png')
    a_source = CITY / 'compact-pair-v2-density/native/A-v2-api.png'
    with Image.open(a_source) as a:
        a.crop((780, 0, 1500, 520)).save(refs / 'A2-density-local.png')
    image = Image.new('RGB', (1536, 1024), '#a1ad8c')
    draw = ImageDraw.Draw(image)
    for box, color in [((30, 145, 205, 395), '#bfb4a1'), ((300, 120, 550, 220), '#c9bba7'),
                       ((310, 320, 565, 440), '#bdbaa6'), ((795, 120, 1120, 400), '#b6b2a3'),
                       ((1190, 140, 1470, 410), '#c7b9a2'), ((40, 660, 430, 910), '#c5b8a6'),
                       ((760, 665, 1010, 930), '#b8bba1'), ((1200, 660, 1480, 950), '#adbb94')]:
        draw.rounded_rectangle(box, radius=12, fill=color)
    roads = [[(686, 0), (679.5, 64), (663, 240), (636, 530), (565, 1024)],
             [(0, 530), (1536, 530)], [(180, 530), (280, 270), (663, 240)],
             [(1050, 530), (1120, 745), (1150, 850)]]
    for points in roads:
        draw.line(points, fill='#d4cebd', width=82, joint='curve')
        draw.line(points, fill='#737b7c', width=54, joint='curve')
    with Image.open(refs / 'actual-north-edge-64.png') as band:
        if band.size != (1536, 64):
            raise ValueError('Unexpected actual band size.')
        image.paste(band.convert('RGB'), (0, 0))
    image.save(refs / 'C-structure.png')
    record = {'sourceRegionContract': str(BASE / 'next-C/identity-and-edge-contract.json'),
              'bandSource': str(band_source), 'bandSourceSHA256': sha(band_source),
              'bandCopySHA256': sha(refs / 'actual-north-edge-64.png'),
              'A2DensitySource': str(a_source), 'A2DensitySourceSHA256': sha(a_source),
              'A2DensityCropBox': [780, 0, 1500, 520],
              'guide': 'C-structure.png', 'guideRole': 'PIL structure only; replace all zones with coherent native artwork',
              'guideRoads': roads, 'requestedSize': [1536, 1024], 'offset': [0, 960],
              'coreStartLocalY': 64, 'doNotAddNewBuildingsAcrossCoreLine': True,
              'fullNeighborImageAttached': False, 'existingNorthStripPixelsInGuide': True}
    (refs / 'input-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'prepared': True, 'requestsMade': 0, 'guide': str(refs / 'C-structure.png')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
