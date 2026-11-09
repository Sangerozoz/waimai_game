#!/usr/bin/env python3
"""Create an isolated, finite Tiled inspection view; never edit delivered layouts."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'reference25'
OUT = HERE / 'tiled-review'
KIT = HERE.parent


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    if OUT.exists():
        raise SystemExit('Preserve existing review and possible user edits: directory already exists')
    source_file = SOURCE / 'reference-layout.tmj'
    original_sha = hashlib.sha256(source_file.read_bytes()).hexdigest()
    doc = read(source_file)
    scene = read(SOURCE / 'preview-reference/assets/scene-layout.json')
    focus = set(read(SOURCE / 'layout-changes.json')['focusIDs'])
    sprites = next(l for l in doc['layers'] if any('gid' in o for o in l.get('objects', [])))
    selected = [o for o in sprites['objects'] if o['name'] in focus]
    assert selected, 'No focus objects'
    # Object coordinates are already the same projected pixels used by the exporter.
    left = min(o['x'] for o in selected) - 180
    right = max(o['x'] + o['width'] for o in selected) + 420
    top = min(o['y'] - o['height'] for o in selected) - 180
    bottom = max(o['y'] for o in selected) + 240
    width = math.ceil((right - left) / 32) * 32
    height = math.ceil((bottom - top) / 32) * 32
    projection = scene['projection']

    def project(p):
        dx = p[0] - projection['originMap'][0]
        dy = p[1] - projection['originMap'][1]
        return (896 + 16 * (dx * projection['axisX'][0] + dy * projection['axisY'][0]) - left,
                896 + 16 * (dx * projection['axisX'][1] + dy * projection['axisY'][1]) - top)

    # Editor-only geometric ground reference. Not new artwork or runtime resources.
    ground = Image.new('RGB', (width, height), '#deddd0')
    draw = ImageDraw.Draw(ground)
    for surface in scene['groundSurfaces']:
        points = [project(p) for p in surface['polygonMap']]
        xs, ys = zip(*points)
        if max(xs) < 0 or min(xs) > width or max(ys) < 0 or min(ys) > height:
            continue
        material = surface['materialId'].lower()
        color = '#a7b38a' if any(s in material for s in ('meadow', 'grass', 'garden', 'green')) else '#ebdfcc'
        draw.polygon(points, fill=color)

    def capsule(a, b, radius):
        angle = math.atan2(b[1] - a[1], b[0] - a[0])
        world = []
        for center, start in [(b, angle - math.pi / 2), (a, angle + math.pi / 2)]:
            for i in range(17):
                t = start + math.pi * i / 16
                world.append([center[0] + radius * math.cos(t), center[1] + radius * math.sin(t)])
        return [project(p) for p in world]

    # Paint all shoulders first, then all asphalt; a later shoulder must not
    # cut a gap across the preceding segment's asphalt at a shared node.
    for asphalt in (False, True):
        for road in scene['roads']:
            for a, b in zip(road['nodes'], road['nodes'][1:]):
                points = capsule(a, b, road['width'] / 2 + (0 if asphalt else 1.2))
                xs, ys = zip(*points)
                if max(xs) < 0 or min(xs) > width or max(ys) < 0 or min(ys) > height:
                    continue
                draw.polygon(points, fill='#71808c' if asphalt else '#eadfcb')

    OUT.mkdir()
    ground.save(OUT / 'editor-ground.png')
    image_objects = []
    for old in sprites['objects']:
        if old.get('x', 0) + old.get('width', 0) < left or old.get('x', 0) > left + width:
            continue
        if old.get('y', 0) < top or old.get('y', 0) - old.get('height', 0) > top + height:
            continue
        obj = copy.deepcopy(old)
        obj['x'] -= left
        obj['y'] -= top
        # Pure visual review copy: no business, navigation, or source-binding edits.
        image_objects.append(obj)
    tilesets = copy.deepcopy(doc['tilesets'])
    for ts in tilesets:
        for tile in ts['tiles']:
            image = (SOURCE / tile['image']).resolve()
            assert image.is_file(), image
            tile['image'] = os.path.relpath(image, OUT)
    result = {k: copy.deepcopy(v) for k, v in doc.items() if k != 'layers'}
    result.update({'width': width // 32, 'height': height // 32, 'infinite': False,
                   'backgroundcolor': '#deddd0', 'tilesets': tilesets,
                   'nextlayerid': 4,
                   'layers': [
                       {'id': 1, 'type': 'imagelayer', 'name': '原路与地面参照（锁定；未改路）',
                        'image': 'editor-ground.png', 'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'locked': True},
                       {'id': 2, 'type': 'objectgroup', 'name': '房屋树木道具（选择对象后直接拖动）',
                        'draworder': 'topdown', 'x': 0, 'y': 0, 'opacity': 1, 'visible': True,
                        'objects': image_objects},
                       {'id': 3, 'type': 'objectgroup', 'name': '手工路线标注（视觉草稿，不改导航）',
                        'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'objects': []}]})
    save(OUT / '街角_直接编辑.tmj', result)
    # Independent whole-image tracing option; deliberately not a game-map replacement.
    assembly = KIT / 'revision-009/references/layout25/approved-25-assembly-reference.jpg'
    if assembly.is_file():
        with Image.open(assembly) as im:
            iw, ih = im.size
        alternative = {k: copy.deepcopy(v) for k, v in result.items() if k != 'layers'}
        alternative.update({'width': math.ceil(iw / 32), 'height': math.ceil(ih / 32), 'tilesets': [],
                            'layers': [
                                {'id': 1, 'type': 'imagelayer', 'name': '25图名义拼接参考（锁定；非高清母版）',
                                 'image': os.path.relpath(assembly, OUT), 'x': 0, 'y': 0,
                                 'opacity': 1, 'visible': True, 'locked': True},
                                {'id': 2, 'type': 'objectgroup', 'name': '手工路线（用插入多边线工具）',
                                 'x': 0, 'y': 0, 'opacity': 1, 'visible': True, 'objects': []}]})
        save(OUT / '25图总图_手工描线比较稿.tmj', alternative)
    assert hashlib.sha256(source_file.read_bytes()).hexdigest() == original_sha
    save(OUT / 'creation-record.json', {'originalMapSHA256': original_sha,
         'originalMapUnchanged': True, 'objects': len(image_objects), 'canvas': [width, height],
         'sourceRoadsNotEdited': True, 'editorGroundIsGeneratedGeometryNotNativeArt': True,
         'alignmentIssueNotCorrectedByThisView': True, 'newBusinessOrNavigationBindings': 0})
    print(json.dumps({'folder': str(OUT), 'editableObjects': len(image_objects),
                      'canvas': [width, height], 'originalUnchanged': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
