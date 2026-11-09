#!/usr/bin/env python3
"""Create a cropped/resized runtime-only map pilot. Raw art/maps stay read-only.
Resource optimization and actual display inspection, not a game test suite.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image, ImageFilter

SCRIPT_DIR = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, default=SCRIPT_DIR)
parser.add_argument('--max-edge', type=int)
parser.add_argument('--single-source', type=Path)
parser.add_argument('--single-target', type=Path)
args = parser.parse_args()
if args.max_edge is not None and not 16 <= args.max_edge <= 4096:
    raise SystemExit('max-edge must be between 16 and 4096')
HERE = args.output_dir.resolve()
KIT = SCRIPT_DIR.parents[1]
SOURCE = KIT/'revision-004/viewer'


def read(p):
    return json.loads(p.read_text())


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main_component_box(image):
    """Find major alpha component; use only for bounds, not to alter source alpha.
    A one-pixel analysis dilation joins fine branches. Small detached alpha specks
    cannot force an otherwise narrow pole to retain a full square runtime canvas.
    """
    mask = image.getchannel('A').point([0]*16+[255]*240).filter(ImageFilter.MaxFilter(3))
    data = mask.tobytes(); w, h = mask.size
    parents = []; areas = []; boxes = []

    def root(k):
        while parents[k] != k:
            parents[k] = parents[parents[k]]; k = parents[k]
        return k

    def merge(a, b):
        a, b = root(a), root(b)
        if a == b:
            return a
        if areas[a] < areas[b]:
            a, b = b, a
        parents[b] = a; areas[a] += areas[b]
        boxes[a] = [min(boxes[a][0], boxes[b][0]), min(boxes[a][1], boxes[b][1]),
                    max(boxes[a][2], boxes[b][2]), max(boxes[a][3], boxes[b][3])]
        return a

    previous = []
    for y in range(h):
        line = data[y*w:(y+1)*w]; runs = []; x = 0
        while x < w:
            while x < w and not line[x]:
                x += 1
            if x == w:
                break
            left = x
            while x < w and line[x]:
                x += 1
            right = x; k = len(parents)
            parents.append(k); areas.append(right-left); boxes.append([left, y, right, y+1])
            runs.append((left, right, k))
        j = 0
        for left, right, k in runs:
            while j < len(previous) and previous[j][1] < left:
                j += 1
            t = j
            while t < len(previous) and previous[t][0] <= right:
                merge(k, previous[t][2]); t += 1
        previous = runs
    if not parents:
        raise ValueError('No visible sprite alpha')
    largest = max((i for i in range(len(parents)) if root(i) == i), key=lambda i: areas[i])
    x0, y0, x1, y1 = boxes[largest]
    pad = 12
    return [max(0, x0-pad), max(0, y0-pad), min(w, x1+pad), min(h, y1+pad)]


def optimize(source, target, cap, trim=True):
    before = sha(source)
    with Image.open(source) as image:
        image = image.convert('RGBA'); original = list(image.size)
        box = main_component_box(image) if trim else [0, 0, image.width, image.height]
        x0, y0, x1, y1 = box
        crop = image.crop((x0, y0, x1, y1)); factor = min(1.0, cap/max(crop.size))
        size = [max(1, round(v*factor)) for v in crop.size]
        # Premultiplied resize prevents hidden RGB in transparent pixels from
        # creating black/white interpolation halos. Native originals unchanged.
        if size != list(crop.size):
            crop = crop.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
        target.parent.mkdir(parents=True, exist_ok=True)
        crop.save(target, optimize=True, compress_level=9)
    if before != sha(source):
        raise ValueError('Raw source changed')
    return {'source': str(source), 'sourceSHA256': before, 'file': target.name,
            'sourceSize': original, 'cropBox': box, 'runtimeSize': size, 'maximumSide': cap,
            'sourceBytes': source.stat().st_size, 'runtimeBytes': target.stat().st_size,
            'sourceDecodedRGBABytesEstimate': original[0]*original[1]*4,
            'runtimeDecodedRGBABytesEstimate': size[0]*size[1]*4,
            'sha256': sha(target), 'rawUnchanged': True,
            'cropMethod': 'largest alpha>=16 analysis component with one-pixel dilation +12px native margin; source alpha inside retained box preserved before resampling' if trim else 'no trim for repeating material'}


def convert_uv(uv, info):
    w, h = info['sourceSize']; x0, y0, x1, y1 = info['cropBox']
    return [(uv[0]*w-x0)/(x1-x0), (uv[1]*h-y0)/(y1-y0)]


def main():
    viewer = HERE/'viewer'
    if viewer.exists():
        raise ValueError('Refusing to overwrite existing runtime pilot')
    layout = read(SOURCE/'assets/scene-layout.json')
    manifest = read(SOURCE/'assets/asset-manifest.json')
    needed = {b['assetId'] for b in layout['blocks']} | {
        layout['rider']['forwardAssetId'], layout['rider']['reverseAssetId'], 'S01-paving', 'S02-asphalt'}
    selected = [copy.deepcopy(a) for a in manifest['assets'] if a['id'] in needed]
    if len(selected) != len(needed):
        raise ValueError('Unresolved runtime asset IDs')
    hashes = {str(SOURCE/'assets'/a['file']): sha(SOURCE/'assets'/a['file']) for a in selected}

    def ignore(directory, names):
        if Path(directory) == SOURCE/'assets':
            return [n for n in names if n.endswith('.png') or n == 'asset-manifest-before.json']
        return []

    shutil.copytree(SOURCE, viewer, ignore=ignore)
    by_file = {}; rows = []
    for asset in selected:
        old_file = asset['file']
        if old_file not in by_file:
            is_building = old_file.startswith('B01')
            cap = args.max_edge or (600 if is_building or asset['kind'] == 'material' else 400)
            target = viewer/'assets'/('rt-'+old_file)
            by_file[old_file] = optimize(SOURCE/'assets'/old_file, target, cap, asset['kind'] != 'material')
            rows.append(by_file[old_file])
        info = by_file[old_file]
        old_size = list(asset['nativeSize']); old_ppu = asset.get('nativePixelsPerUnit')
        asset['sourceNativeSize'] = old_size; asset['sourceNativeSHA256'] = asset['sha256']
        asset['runtimeDerivation'] = copy.deepcopy(info)
        for key in ['anchorUV', 'wheelContactAnchorUV']:
            if key in asset:
                asset[key] = convert_uv(asset[key], info)
        if 'opaqueBoundsUV' in asset:
            box = asset['opaqueBoundsUV']
            asset['opaqueBoundsUV'] = convert_uv(box[:2], info)+convert_uv(box[2:], info)
        if 'groundPolygon' in asset:
            asset['groundPolygon'] = [convert_uv(v, info) for v in asset['groundPolygon']]
        if old_ppu and asset['kind'] == 'block':
            x0, y0, x1, y1 = info['cropBox']
            asset['worldSizeUnits'] = [(x1-x0)/old_ppu, (y1-y0)/old_ppu]
        asset.update(file=info['file'], nativeSize=info['runtimeSize'], sha256=info['sha256'],
                     status='runtime-derived-resolution-pilot-not-a-new-native-original')
    manifest['assets'] = selected
    manifest['status'] = 'runtime-size-budget-pilot-original-camera-and-poses'
    manifest['notes'] = ['Raw native files remain archived unchanged; this manifest contains only active runtime assets.',
                         f'Max edge override={args.max_edge}; otherwise building/material600 and small sprites400; cropped proportions/pivots remapped.',
                         'This is a size-only comparison with revision-004; lamp orientation changes from revision-005 not yet integrated here.']
    write(viewer/'assets/asset-manifest.json', manifest)
    patch_viewer(viewer)
    if any(sha(Path(p)) != value for p, value in hashes.items()):
        raise ValueError('Protected original changed')
    pngs = list((viewer/'assets').glob('*.png'))
    if len(pngs) != len(by_file):
        raise ValueError('Unused raw PNG accidentally included')
    loose_original = list((SOURCE/'assets').glob('*.png'))
    report = {
        'status': 'runtime-export-statistics-not-game-performance-or-visual-acceptance',
        'assetRows': rows, 'activeAssetIds': len(selected), 'uniqueImageFiles': len(rows),
        'previousLoosePNGCount': len(loose_original), 'previousLoosePNGBytes': sum(p.stat().st_size for p in loose_original),
        'activeOriginalPNGBytes': sum(r['sourceBytes'] for r in rows),
        'optimizedPNGBytes': sum(r['runtimeBytes'] for r in rows),
        'uniqueOriginalDecodedRGBABytesEstimate': sum(r['sourceDecodedRGBABytesEstimate'] for r in rows),
        'uniqueOptimizedDecodedRGBABytesEstimate': sum(r['runtimeDecodedRGBABytesEstimate'] for r in rows),
        'sourceSHA256': hashes, 'sourceRoadsAndWorldAnchorsUnchanged': True,
        'gameTestsRun': False, 'limitations': ['RGBA estimates exclude mips, ground canvas, driver allocations, engine and UI.',
          'Final game maximum zoom and device DPR budget not frozen; 400/600 is a comparison candidate, not a universal sharpness guarantee.']}
    write(HERE/'resource-report.json', report)
    # The corrected new lamp is also exported as a separate runtime example.
    near = KIT/'revision-005/native/retry-near-001/L01-road-near-v1.png'
    example_cap = args.max_edge or 400
    example = optimize(near, HERE/f'examples/new-near-lamp-{example_cap}.png', example_cap)
    write(HERE/f'examples/new-near-lamp-{example_cap}.json', example)
    print(json.dumps({k: report[k] for k in ['activeAssetIds', 'uniqueImageFiles', 'previousLoosePNGCount', 'previousLoosePNGBytes',
                     'activeOriginalPNGBytes', 'optimizedPNGBytes', 'uniqueOriginalDecodedRGBABytesEstimate', 'uniqueOptimizedDecodedRGBABytesEstimate']}, ensure_ascii=False))
    print('new lamp example', json.dumps(example, ensure_ascii=False))


def patch_viewer(viewer):
    bundle = viewer/'assets/main/index.probe41.js'
    code = bundle.read_text()
    replacements = [
      ('e.assets=new Map,e.frames=new Map,e.images=new Map,',
       'e.assets=new Map,e.frames=new Map,e.images=new Map,e.imagePromises=new Map,e.frameCache=new WeakMap,e.nativeFramesCreated=0,e.canvasFramesCreated=0,'),
      ('o.loadImage=function()', 'o.loadOriginalImage=function()'),
      ('o.frame=function(t){var e=new s;e.image=new h(t);var r=new c;return r.texture=e,r}',
       'o.loadImage=function(e){var k=e.file+"@"+e.sha256;if(!this.imagePromises.has(k))this.imagePromises.set(k,this.loadOriginalImage(e));return this.imagePromises.get(k)},o.frame=function(t){if(this.frameCache.has(t))return this.frameCache.get(t);var e=new s;e.image=new h(t);var r=new c;r.texture=e;this.frameCache.set(t,r);t.naturalWidth?this.nativeFramesCreated++:this.canvasFramesCreated++;globalThis.__mapTextureStats={uniqueAssetImages:this.imagePromises.size,nativeFramesCreated:this.nativeFramesCreated,canvasFramesCreated:this.canvasFramesCreated};return r}'),
      ('E.nativeSize[0]/E.nativePixelsPerUnit*this.ppm,E.nativeSize[1]/E.nativePixelsPerUnit*this.ppm,E.anchorUV',
       '(E.worldSizeUnits?E.worldSizeUnits[0]:E.nativeSize[0]/E.nativePixelsPerUnit)*this.ppm,(E.worldSizeUnits?E.worldSizeUnits[1]:E.nativeSize[1]/E.nativePixelsPerUnit)*this.ppm,E.anchorUV'),
    ]
    for old, new in replacements:
        if code.count(old) != 1:
            raise ValueError('Unexpected generated runtime implementation: '+old[:65])
        code = code.replace(old, new)
    bundle.write_text(code)


if __name__ == '__main__':
    if args.single_source or args.single_target:
        if not args.single_source or not args.single_target:
            raise SystemExit('Both single-source and single-target are required')
        if args.single_source.resolve() == args.single_target.resolve() or args.single_target.exists():
            raise SystemExit('Refusing to overwrite native/existing image')
        if not args.single_target.resolve().is_relative_to(HERE):
            raise SystemExit('Single target must be inside output-dir')
        info = optimize(args.single_source, args.single_target, args.max_edge or 280)
        write(args.single_target.with_suffix('.runtime.json'), info)
        print(json.dumps(info, ensure_ascii=False))
    else:
        main()
