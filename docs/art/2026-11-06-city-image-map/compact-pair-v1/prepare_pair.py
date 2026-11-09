#!/usr/bin/env python3
"""Prepare structure-only inputs; never produces or modifies native artwork."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ART = HERE.parent.parent
ROOT = ART.parents[1]


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def main():
    if (HERE / 'shared-edge-contract.json').exists():
        raise SystemExit('Prepared inputs already exist; preserve them.')
    protected = [ART / '2026-11-06-city-image-map/planning/current-scope.json',
                 ART / '2026-11-06-city-image-map/planning/layout-draft-v1.json',
                 ART / '2026-11-06-road-tracing-pilot/native-city-block.png',
                 ART / '2026-11-06-road-tracing-pilot/画路试验.tmj',
                 ART / '2026-11-06-road-tracing-pilot/画路试验_助手描线.tmj',
                 ART / '2026-11-05-modular-map-kit/delivery-kit/v1/user-layout.tmj',
                 ART / '2026-11-05-modular-map-kit/delivery-kit/reference25/reference-layout.tmj',
                 ART / '2026-11-05-modular-map-kit/revision-006/viewer/assets/scene-layout.json',
                 ART / '2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj',
                 ROOT / 'delivery-game/assets/resources/map-sample/city.json']
    save(HERE / 'protected-inputs.json', {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected})
    contract = {'status': 'pre-generation-pixel-contract-not-yet-observed-art',
                'requestedNativeSize': [1536, 1024], 'referenceActualPilotSize': [1536, 1024],
                'coordinateSpace': 'native-image-pixels-not-metres',
                'regions': [{'id': 'A', 'role': 'commercial-life-core', 'offset': [0, 0], 'coreLocal': [0, 0, 1504, 1024]},
                            {'id': 'B', 'role': 'residential-education', 'offset': [1472, 0], 'coreLocal': [32, 0, 1536, 1024]}],
                'overlapPixels': 64, 'sharedGlobalBand': [1472, 0, 1536, 1024],
                'coreBoundaryGlobalX': 1504,
                'portal': {'id': 'AB-main', 'centerY': 600, 'directionAtSeam': [1, 0],
                           'asphaltWidthPixels': 56, 'sidewalkWidthEachPixels': 14,
                           'AEdge': [1536, 600], 'BEdge': [0, 600]},
                'noBuildingsInSharedBand': True, 'edgeGroundFullyPainted': True,
                'whiteDisplayMarginsForbidden': True, 'nativeWarpOrRescaleAllowed': False,
                'mergeRule': 'A owns x<1504, B owns x>=1504. Route endpoints must be confirmed on actual art before merging.'}
    save(HERE / 'shared-edge-contract.json', contract)
    plan = {'status': 'compact-four-region-candidate-not-final-grid', 'areaIntentVersusOld25': .25,
            'physicalAreaMeasured': False, 'metreCalibration': None,
            'preferredImageBudget': [4, 6], 'planningCeiling': 6, 'currentRequestedBatch': ['A', 'B'],
            'nominalFourImageRasterWith64Overlap': [3008, 1984],
            'regions': [{'id': 'A', 'function': 'market, local shops, mixed homes, one office'},
                        {'id': 'B', 'function': 'varied housing, small school/library, neighborhood green'},
                        {'id': 'C', 'function': 'small workshop/service, residential courtyard, transition to gardens'},
                        {'id': 'D', 'function': 'sparse low homes, vegetables/orchard, natural edge'}],
            'optionalSplitOnlyIfClarityNeeds': 'Up to six without expanding coverage; no automatic further generation.',
            'contentReduction': 'Merge repeated C01-C09 functions; fewer street blocks and repeated facilities, not all old content shrunk.',
            'localReadingTarget': {'nativeDisplayScale': 1, 'optionalDiagnosticZoom': 2,
                                   'mainRoadRequestedWidthPixels': 56, 'buildingFootprintsApproxPixels': [100, 270]},
            'styleAuthority': ['approved25 assembly relationships', 'original TR-33 accepted artwork'],
            'userAcceptedArt': False}
    save(HERE.parent / 'planning/compact-layout-v1.json', plan)
    image = Image.new('RGB', (1100, 760), '#e7e7d7')
    d = ImageDraw.Draw(image)
    colors = ['#c9b394', '#afc4ac', '#c0b7a1', '#9eaf86']
    for index, (label, x, y) in enumerate([('A  MARKET / MIXED HOMES', 40, 70), ('B  HOMES / EDUCATION', 560, 70), ('C  WORKSHOP / COURTYARDS', 40, 400), ('D  SUBURB / NATURE', 560, 400)]):
        d.rounded_rectangle((x, y, x + 500, y + 305), radius=15, fill=colors[index], outline='#68766a', width=3)
        d.text((x + 16, y + 15), label, fill='#25372e')
    d.line([(65, 250), (1040, 250)], fill='#737d7d', width=20)
    d.line([(410, 120), (410, 675)], fill='#737d7d', width=16)
    d.line([(410, 560), (955, 560)], fill='#737d7d', width=14)
    d.text((35, 22), 'STRUCTURE ONLY - 1/4 AREA INTENT - 4 TO 6 IMAGE BUDGET, NOT A LOCKED GRID', fill='#25372e')
    image.save(HERE.parent / 'planning/compact-layout-v1.png')
    for region in ['A', 'B']:
        im = Image.new('RGB', (1536, 1024), '#9aa785')
        dr = ImageDraw.Draw(im)
        # Every pixel has ground; no display white, sky, or cutout-island convention.
        dr.rectangle((0, 0, 1535, 1023), fill='#a3ae8c')
        if region == 'A':
            zones = [(60, 55, 360, 245, '#c6bda9'), (420, 45, 715, 195, '#b4bd9d'),
                     (760, 55, 1150, 210, '#c6bda9'), (90, 350, 335, 505, '#c5b9a4'),
                     (500, 315, 1000, 510, '#c7bca6'), (60, 740, 310, 945, '#b3bba0'),
                     (420, 730, 680, 930, '#c5b6a2'), (800, 730, 1120, 945, '#b3bba0'),
                     (1190, 755, 1320, 925, '#b4bd9d')]
            roads = [[(0, 600), (1536, 600)], [(120, 600), (210, 300), (900, 250), (1150, 600)],
                     [(740, 600), (700, 1024)]]
        else:
            zones = [(260, 85, 485, 285, '#c6bda9'), (590, 55, 935, 300, '#b4bd9d'),
                     (1075, 90, 1450, 310, '#c6bda9'), (270, 380, 485, 505, '#c5b9a4'),
                     (620, 365, 1005, 505, '#b4bd9d'), (1100, 410, 1450, 520, '#b4bd9d'),
                     (210, 750, 485, 940, '#c5b6a2'), (660, 745, 980, 940, '#b3bba0'),
                     (1130, 735, 1440, 935, '#9eaf86')]
            roads = [[(0, 600), (1536, 600)], [(360, 600), (530, 340), (1020, 340), (1130, 600)],
                     [(630, 600), (555, 1024)]]
        for x0, y0, x1, y1, color in zones:
            dr.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=color)
        for points in roads:
            dr.line(points, fill='#d7d0bd', width=84, joint='curve')
            dr.line(points, fill='#737b7d', width=56, joint='curve')
        p = HERE / 'references' / f'{region}-structure.png'
        p.parent.mkdir(parents=True, exist_ok=True)
        im.save(p)
    print(json.dumps({'prepared': True, 'nativeRequestsMade': 0, 'contract': str(HERE / 'shared-edge-contract.json')}))


if __name__ == '__main__':
    main()
