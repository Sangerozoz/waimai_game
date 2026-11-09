#!/usr/bin/env python3
"""Prepare an explicit density-only edit mask; never changes accepted artwork."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'compact-pair-v1'
ART = HERE.parent.parent
ROOT = ART.parents[1]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (HERE / 'inputs/edit-mask.png').exists():
        raise SystemExit('Mask already exists: preserve prepared inputs without resetting.')
    known = {'README.md', 'prepare_density.py', 'generate_density.py', 'prompt.txt', 'execution-commands.json'}
    unknown = [p.name for p in HERE.iterdir() if p.name not in known]
    if unknown:
        raise SystemExit('Unexpected existing content: ' + repr(unknown))
    source = OLD / 'native/A/native.png'
    review = json.loads((OLD / 'user-review-001.json').read_text())
    if sha(source) != review['frozenInputs']['A_native_SHA256']:
        raise SystemExit('Accepted A source differs from review; do not restore or guess.')
    protected = {str(p): sha(p) for p in OLD.rglob('*') if p.is_file()}
    for p in [ROOT / 'AGENTS.md', ART / '2026-11-06-city-image-map/planning/current-scope.json',
              ART / '2026-11-06-city-image-map/planning/density-revision-request.md',
              ROOT / 'delivery-game/assets/resources/map-sample/city.json']:
        protected[str(p)] = sha(p)
    save(HERE / 'protected-inputs.json', protected)
    image = Image.open(source).convert('RGB')
    if image.size != (1536, 1024):
        raise SystemExit('Unexpected source size; no resampling allowed.')
    # White in this analysis plane means eligible. API mask alpha zero edits.
    eligible = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(eligible)
    zones = [
        {'id': 'east-urban-block', 'box': [1226, 12, 1460, 478], 'role': 'replace large eastern garden with tightly grouped commercial/mixed housing; higher rear and lower frontage'},
        {'id': 'north-infill', 'box': [635, 10, 783, 181], 'role': 'one narrow complete mixed-use infill in the gap between existing northern buildings'},
        {'id': 'south-central-infill', 'box': [780, 640, 904, 1012], 'role': 'compact street-facing infill where a complete building fits, not blocking the retained shelter'},
        {'id': 'south-west-shopfronts', 'box': [12, 895, 660, 1012], 'role': 'low continuous courtyard-facing commercial infill, original-size doors, not miniature houses'},
        {'id': 'south-east-shopfronts', 'box': [804, 889, 1460, 1012], 'role': 'low varied connected frontage replacing vacant foreground garden, preserve breathing gaps'},
        {'id': 'far-east-infill', 'box': [1374, 637, 1460, 1012], 'role': 'only if complete urban infill fits at native scale; otherwise leave the narrow pocket'}]
    for zone in zones:
        draw.rectangle(zone['box'], fill=255)
    buildings = [
        [32, 8, 270, 205], [273, 39, 399, 194], [407, 8, 637, 198], [781, 5, 1194, 203],
        [15, 218, 144, 371], [252, 259, 411, 416], [201, 349, 371, 516],
        [402, 225, 850, 522], [864, 315, 1058, 522], [1049, 181, 1242, 461],
        [75, 619, 364, 908], [389, 619, 677, 914],
        [897, 620, 1136, 897], [1138, 685, 1386, 899], [738, 784, 883, 894]]
    for box in buildings:
        draw.rectangle(box, fill=0)
    # Protect all old road surfaces, junctions, crosswalks and adjacent sidewalks.
    graph = json.loads((OLD / 'navigation/graph.json').read_text())
    road_protection = Image.new('L', image.size, 0)
    road_draw = ImageDraw.Draw(road_protection)
    for edge in graph['edges']:
        if not edge['name'].startswith('A-'):
            continue
        points = [tuple(p) for p in edge['points']]
        road_draw.line(points, fill=255, width=140, joint='curve')
        for x, y in points:
            road_draw.ellipse((x - 70, y - 70, x + 70, y + 70), fill=255)
    eligible = ImageChops.subtract(eligible, road_protection)
    draw = ImageDraw.Draw(eligible)
    draw.rectangle((1472, 0, 1535, 1023), fill=0)
    draw.rectangle((0, 0, 1535, 7), fill=0)
    draw.rectangle((0, 1017, 1535, 1023), fill=0)
    (HERE / 'inputs').mkdir(exist_ok=True)
    eligible.save(HERE / 'inputs/edit-eligible.png')
    road_protection.save(HERE / 'inputs/road-sidewalk-protection.png')
    mask = Image.new('RGBA', image.size, (0, 0, 0, 255))
    mask.putalpha(ImageChops.invert(eligible))
    mask.save(HERE / 'inputs/edit-mask.png')
    # Input2 is only a visually marked allowed-area map, never generated artwork.
    overlay = image.convert('RGBA')
    tint = Image.new('RGBA', image.size, (55, 140, 235, 0))
    tint.putalpha(eligible.point(lambda v: 85 if v else 0))
    guide = Image.alpha_composite(overlay, tint).convert('RGB')
    labels = ImageDraw.Draw(guide)
    for zone in zones:
        x, y = zone['box'][:2]
        labels.text((x + 3, y + 5), zone['id'], fill='#08264b', stroke_width=1, stroke_fill='#e8f4ff')
    guide.save(HERE / 'inputs/edit-guide.png')
    save(HERE / 'inputs/edit-zones.json', {
        'sourceA': str(source), 'sourceASHA256': sha(source),
        'maskSemantics': 'RGBA alpha0 = editable; alpha255 = protected. Blue in guide is annotation only.',
        'canvasSize': [1536, 1024], 'zones': zones, 'protectedBuildingBoxes': buildings,
        'roadProtectionWidthPixels': 140, 'east64PixelBandProtected': True,
        'acceptedDimensionsFrozen': review['acceptedByUser'],
        'editablePixels': eligible.histogram()[255],
        'smallResidualPocketsMayRemainUnbuilt': True,
        'noProgrammaticBuildingArt': True})
    print(json.dumps({'prepared': True, 'editablePixels': eligible.histogram()[255],
                      'mask': str(HERE / 'inputs/edit-mask.png'), 'nativeRequestsMade': 0}))


if __name__ == '__main__':
    main()
