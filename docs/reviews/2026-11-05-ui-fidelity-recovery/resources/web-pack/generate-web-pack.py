#!/usr/bin/env python3
"""Offline UI-only derivatives. No engine/build/server/game/save execution.
Requires Pillow 11.3.0. Run --category vehicles, review pilot, then --category all.
Original manifests and image masters are read-only. All generated images/metas are
under ui-v2/web; review images, source/derivative SHA records stay beside this file.
"""
from __future__ import annotations
import argparse
import ast

import hashlib
import json
import math
from pathlib import Path
import re
import uuid
from PIL import Image, ImageDraw, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[5]
RES = ROOT / 'delivery-game/assets/resources'
OUT = RES / 'ui-v2/web'
DOC = Path(__file__).resolve().parent
NAMESPACE = uuid.UUID('db494501-a328-42f7-bd92-df749ca35840')
CATEGORIES = ('vehicles', 'portraits', 'chrome', 'food')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def arithmetic(text):
    def walk(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return walk(node.left) / walk(node.right)
        raise ValueError('not a numeric crop expression: ' + text)
    return walk(ast.parse(text, mode='eval').body)


def round_js(value):
    return math.floor(value + .5)


def native_rect(normalized, size):
    x, y, w, h = normalized
    iw, ih = size
    left, top = round_js(x * iw), round_js(y * ih)
    return [left, top, round_js((x + w) * iw) - left, round_js((y + h) * ih) - top]


def descriptors():
    entries = []
    # Every source/key/status/rectangle remains in its existing manifest.
    # In particular maps.json and map-preview-* never enter the generator.
    for name in ('manifest', 'portraits'):
        manifest = json.loads((RES / f'ui-v2/{name}.json').read_text())
        for key, asset in manifest['assets'].items():
            if name == 'portraits':
                # Largest existing cover viewport is 104x146. Hero square cover
                # within that slot uses 146x146 of the original avatar crop.
                budget = [146, 146] if key == 'hero' else [104, 146]
                category = 'portraits'
            else:
                category = 'chrome'
                budget = chrome_budget(key)
            entries.append(dict(category=category, key=f'{name}/{key}', resource=asset['resource'],
                                rect=asset['rect'], budget=budget, fit='cover' if name == 'portraits' else 'contain',
                                inset=asset.get('inset')))
    text = (ROOT / 'delivery-game/assets/scripts/map-sample/CartoonArt.ts').read_text()

    # Trace the final explicit assignments, not the superseded register defaults.
    crops = {}
    for match in re.finditer(r"crops(?:\['([^']+)'\]|\.([a-zA-Z]+))=\{resource:'([^']+)',rect:\[([^]]+)\]\};", text):
        key = match[1] or match[2]
        crops[key] = (match[3], [arithmetic(x) for x in match[4].split(',')])
    side_keys = ['side-d', 'side-d-plus', 'side-c', 'side-c-plus', 'side-b', 'side-b-plus', 'side-a', 'side-s', 'side-ss', 'side-sss']
    fallback_keys = ['avatar', 'recruit', 'vehicle', 'map', 'bills', 'station', 'coin', 'heart', 'bag', 'close', 'target', 'confirm', 'pause']
    food_match = re.search(r'const foodKeys=(\[[^;]+\]);', text)
    assert food_match is not None
    food_keys = json.loads(food_match[1])
    for key in side_keys + fallback_keys + food_keys:
        resource, normalized = crops[key]
        with Image.open(RES / (resource + '.png')) as source:
            rect = native_rect(normalized, source.size)
        category = 'vehicles' if key in side_keys else 'food' if key in food_keys else 'portraits' if key == 'avatar' else 'chrome'
        # Main vehicle UI slot is 500x350; menu food slot 146 square minus
        # its existing 10px inset is 136px. No enlargement of originals.
        budget = [500, 350] if category == 'vehicles' else [136, 136] if category == 'food' else [146, 146] if key == 'avatar' else [108, 108]
        entries.append(dict(category=category, key='cartoon/' + key, resource=resource, rect=rect, budget=budget,
                            fit='cover' if key == 'avatar' else 'contain', inset=None))
    return entries


def chrome_budget(key):
    if key.startswith('icon-'):
        return [108, 108]  # includes 61px metric glyph / 52*1.18 vehicle glyph
    return {
        'dispatch-disc': [146, 146], 'panel-glass': [684, 494],
        'button-orange': [684, 90], 'button-blue': [684, 90],
        'nav-tile': [150, 116], 'nav-selected': [150, 116],
        'page-paper': [720, 1280], 'hud-shell': [684, 80],
        'portrait-frame': [108, 150], 'level-badge': [126, 35],
        'status-blue': [102, 35], 'status-gray': [102, 35],
        'xp-track': [220, 20], 'xp-fill': [220, 20],
        'checkbox-unchecked': [36, 36], 'checkbox-checked': [36, 36],
        'bill-metric': [330, 112],
    }[key]


def image_meta(path, alpha):
    template = json.loads((RES / 'ui-v2/nav-icons-v1.png.meta').read_text())
    identifier = str(uuid.uuid5(NAMESPACE, path.relative_to(RES).as_posix()))
    template['uuid'] = identifier
    template['files'] = ['.json', path.suffix]
    texture = template['subMetas']['6c48a']
    texture['uuid'] = identifier + '@6c48a'
    texture['displayName'] = path.stem
    texture['userData']['imageUuidOrDatabaseUri'] = identifier
    template['userData']['hasAlpha'] = alpha
    template['userData']['redirect'] = texture['uuid']
    write_json(Path(str(path) + '.meta'), template)
    return identifier


def emit_metadata():
    directory = json.loads((RES / 'ui-v2.meta').read_text())
    directory['uuid'] = str(uuid.uuid5(NAMESPACE, 'ui-v2/web'))
    write_json(RES / 'ui-v2/web.meta', directory)
    meta = json.loads((RES / 'ui-v2/manifest.json.meta').read_text())
    meta['uuid'] = str(uuid.uuid5(NAMESPACE, 'ui-v2/web/pack.json'))
    write_json(OUT / 'pack.json.meta', meta)


def source_record(resource):
    path = RES / (resource + '.png')
    with Image.open(path) as image:
        return dict(path=str(path), size=list(image.size), mode=image.mode,
                    bytes=path.stat().st_size, sha256=sha(path))


def generate(categories):
    entries = [e for e in descriptors() if e['category'] in categories]
    groups = {}
    for entry in entries:
        group = groups.setdefault((entry['resource'], tuple(entry['rect'])), [])
        group.append(entry)
    sources, assets, runtime = {}, [], {}
    for (resource, rect_tuple), aliases in groups.items():
        source = sources.setdefault(resource, source_record(resource))
        x, y, w, h = rect_tuple
        assert 0 <= x and 0 <= y and w > 0 and h > 0
        assert x+w <= source['size'][0] and y+h <= source['size'][1]
        scales = []
        for entry in aliases:
            bw, bh = entry['budget']
            # Cover portraits must retain enough pixels after viewport cropping.
            ratios = [2*bw/w, 2*bh/h]
            scales.append((max if entry['fit'] == 'cover' else min)(ratios))
        scale = min(1, max(scales))
        size = [max(1, math.ceil(w*scale)), max(1, math.ceil(h*scale))]
        # Single-sprite crop avoids any atlas-rectangle reuse after resizing.
        # Integer output rounding is represented by exact per-axis inset scales.
        with Image.open(source['path']) as image:
            crop = image.crop((x, y, x+w, y+h))
            alpha = 'A' in crop.getbands() and crop.getchannel('A').getextrema() != (255, 255)
            crop = crop.convert('RGBA' if alpha else 'RGB')
            result = crop.resize(size, Image.Resampling.LANCZOS)
            suffix = '.png' if alpha else '.jpg'
            token = hashlib.sha256((resource + ':' + ','.join(map(str, rect_tuple))).encode()).hexdigest()[:12]
            path = OUT / (aliases[0]['category'] + '-' + token + suffix)
            path.parent.mkdir(parents=True, exist_ok=True)
            if alpha:
                result.save(path, optimize=True, compress_level=9)
            else:
                # No palette quantization / no chroma subsampling for faces/text.
                result.save(path, quality=92, subsampling=0, optimize=True, progressive=False)
        identifier = image_meta(path, alpha)
        target = 'ui-v2/web/' + path.stem
        scaled_insets = {}
        for entry in aliases:
            if entry['inset']:
                scaled_insets[entry['key']] = {k: v*size[0 if k in ('left', 'right') else 1]/(w if k in ('left', 'right') else h)
                                               for k, v in entry['inset'].items()}
        assets.append(dict(category=aliases[0]['category'], keys=[e['key'] for e in aliases], source=source['path'],
                           sourceResource=resource, sourceRect=list(rect_tuple),
                           budgets=[dict(key=e['key'], logical=e['budget'], fit=e['fit'], dpr=2) for e in aliases],
                           derivative=dict(path=str(path), resource=target, size=size, rect=[0, 0, *size], bytes=path.stat().st_size,
                                           sha256=sha(path), mode='RGBA' if alpha else 'RGB', uuid=identifier),
                           scale=[size[0]/w, size[1]/h], scaledInsets=scaled_insets))
        source_map = runtime.setdefault(resource, dict(size=source['size'], regions={}))
        source_map['regions'][','.join(map(str, rect_tuple))] = dict(resource=target, size=size)
    pack = dict(version=1, sources=runtime)
    write_json(OUT / 'pack.json', pack)
    emit_metadata()
    totals = {}
    for category in categories:
        selected = [a for a in assets if a['category'] == category]
        original_resources = {a['sourceResource'] for a in selected}
        original_bytes = sum(sources[r]['bytes'] for r in original_resources)
        derivative_bytes = sum(a['derivative']['bytes'] for a in selected)
        totals[category] = dict(keys=sum(len(a['keys']) for a in selected), textures=len(selected),
                                originalTextures=len(original_resources), originalBytes=original_bytes,
                                derivativeBytes=derivative_bytes, reductionPercent=100*(1-derivative_bytes/original_bytes))
    original_bytes = sum(v['bytes'] for v in sources.values())
    derivative_bytes = sum(a['derivative']['bytes'] for a in assets)
    report = dict(version=1, pillow=pillow_version, categories=list(categories),
                  constraints=['No map assets/manifests transformed or remapped', 'Original image files/manifests read-only',
                               'UI-only offline image processing; no game, save, tests, typecheck, Creator build or deployment',
                               'Not native HD; derived pixels do not create missing detail'],
                  sources=sources, assets=assets, totals=totals,
                  overall=dict(originalTextures=len(sources), derivativeTextures=len(assets), originalBytes=original_bytes,
                               derivativeBytes=derivative_bytes, mappingBytes=(OUT/'pack.json').stat().st_size,
                               reductionPercent=100*(1-derivative_bytes/original_bytes)))
    write_json(DOC / ('asset-records.json' if len(categories) == 4 else 'pilot-records.json'), report)
    comparisons(assets, 'review' if len(categories) == 4 else 'pilot')
    print(json.dumps(dict(totals=totals, overall=report['overall']), ensure_ascii=False, indent=2))


def comparisons(assets, prefix):
    # Side-by-side original-at-display-size / derivative-at-display-size on the
    # same checkerboard. These are offline contact sheets, not game screenshots.
    sheets = []
    for category in CATEGORIES:
        selected = [a for a in assets if a['category'] == category]
        if not selected:
            continue
        limit = 12 if category != 'portraits' else 31
        for start in range(0, len(selected), limit):
            part = selected[start:start+limit]
            slot_w, slot_h = (500, 350) if category == 'vehicles' else (160, 180)
            cols = 1 if category == 'vehicles' else 3
            cell_w, cell_h = 2*slot_w+32, slot_h+42
            canvas = Image.new('RGB', (cols*cell_w, math.ceil(len(part)/cols)*cell_h), '#EFFAFF')
            draw = ImageDraw.Draw(canvas)
            for i, asset in enumerate(part):
                cx, cy = (i % cols)*cell_w, (i // cols)*cell_h
                title = ','.join(asset['keys'])
                draw.text((cx+8, cy+4), title, fill='#061344')
                for side in (0, 1):
                    ox, oy = cx+8+side*(slot_w+16), cy+28
                    for yy in range(0, slot_h, 12):
                        for xx in range(0, slot_w, 12):
                            draw.rectangle((ox+xx, oy+yy, ox+min(xx+11, slot_w-1), oy+min(yy+11, slot_h-1)),
                                           fill='#D6E1EA' if (xx//12+yy//12)%2 else '#FFFFFF')
                    if side == 0:
                        with Image.open(asset['source']) as source:
                            x, y, w, h = asset['sourceRect']
                            image = source.crop((x, y, x+w, y+h)).convert('RGBA')
                    else:
                        image = Image.open(asset['derivative']['path']).convert('RGBA')
                    display_scale = min(slot_w/image.width, slot_h/image.height)
                    image = image.resize((round_js(image.width*display_scale), round_js(image.height*display_scale)), Image.Resampling.LANCZOS)
                    canvas.paste(image, (ox+(slot_w-image.width)//2, oy+(slot_h-image.height)//2), image)
            path = DOC / f'{prefix}-{category}-{start//limit+1:02}.jpg'
            canvas.save(path, quality=94, subsampling=0)
            sheets.append(path.name)
    links = '\n'.join(f'<h2>{name}</h2><img src="{name}" style="max-width:100%">' for name in sheets)
    (DOC/f'{prefix}.html').write_text('<!doctype html><meta charset="utf-8"><title>Offline UI derivative review</title>'
                                    '<p>Left: original crop. Right: derivative. Offline images only; not game or remote rendering evidence.</p>'+links)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', choices=(*CATEGORIES, 'all'), required=True)
    args = parser.parse_args()
    generate(CATEGORIES if args.category == 'all' else (args.category,))
