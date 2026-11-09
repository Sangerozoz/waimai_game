#!/usr/bin/env python3
"""Prepare D from actual B/C interfaces; no placeholder pixels become art input."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

HERE = Path(__file__).resolve().parent
CITY = HERE.parent.parent
BASE = CITY / 'compact-three-v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    if (HERE / 'references').exists() or (HERE / 'native.png').exists() or (HERE / 'request-started.json').exists():
        raise SystemExit('Input/request/native already exists; preserve without duplicate generation.')
    known = {'README.md', 'prepare_d.py', 'generate_d.py', 'prompt.txt', 'execution-commands.json'}
    unknown = [p.name for p in HERE.iterdir() if p.name not in known]
    if unknown:
        raise SystemExit('Unexpected content: ' + repr(unknown))
    refs = HERE / 'references'; refs.mkdir()
    protected = {str(p): sha(p) for folder in [BASE, CITY / 'regions/C-001', CITY / 'compact-pair-v2-density', CITY / 'compact-pair-v1'] for p in folder.rglob('*') if p.is_file()}
    for p in [CITY / 'planning/current-scope.json', CITY / 'planning/compact-layout-v1.json',
              CITY.parents[2] / 'delivery-game/assets/resources/map-sample/city.json']:
        protected[str(p)] = sha(p)
    save(HERE / 'protected-inputs.json', protected)
    source = BASE / 'preview/tiled-cli-three.png'
    composite = Image.open(source).convert('RGB')
    north = composite.crop((1472, 960, 3008, 1024))
    west = composite.crop((1472, 960, 1536, 1984))
    if ImageChops.difference(north.crop((0, 0, 64, 64)), west.crop((0, 0, 64, 64))).getbbox() is not None:
        raise ValueError('Shared corner mismatch; do not submit guessed inputs.')
    north.save(refs / 'actual-north-64.png'); west.save(refs / 'actual-west-64.png')
    contract = {'status': 'pre-request-actual-interface-contract-not-generated-art', 'nativeSizeReference': [1536, 1024],
        'DWorldOffset': [1472, 960], 'coreCropBoxLocal': [64, 64, 1536, 1024], 'coreWorldOrigin': [1536, 1024],
        'ownership': 'B/A2 own north y<1024; C complete core owns west x<1536 below y1024. Do not use top-row1504 boundary below.',
        'northBandGlobalBounds': [1472, 960, 3008, 1024], 'westBandGlobalBounds': [1472, 960, 1536, 1984],
        'sourceOfficialRender': str(source), 'sourceOfficialRenderSHA256': sha(source),
        'placeholderIncludedInReferences': False, 'cornerPixelsEqual': True,
        'northActual': {'source': 'B1 native y1023', 'asphaltXInterval': [502, 570], 'centerDLocalX': (502+570)/2,
                        'widthPixels': 570-502+1, 'physicalWorldPortal': [1472+(502+570)/2, 1024],
                        'frozenVectorWorldPortal': [1997, 1024], 'vectorDLocalPortal': [525, 64],
                        'note': 'Frozen vector endpoint525 lies inside asphalt502..570; retain old data, join within visible carriageway.'},
        'westActual': {'source': 'C native x1535', 'asphaltYInterval': [521,563], 'centerDLocalY': (521+563)/2,
                       'widthPixels': 563-521+1, 'physicalWorldPortal': [1536,960+(521+563)/2],
                       'frozenVectorWorldPortal': [1536,1500], 'vectorDLocalPortal': [64,540]},
        'directionsFromActualNarrowBand': {'north': [-10,63], 'west': [63,.5]},
        'sourceUnits': 'native pixels; no metre calibration'}
    save(refs / 'interface-contract.json', contract)
    guide = Image.new('RGB', (1536,1024), '#a2b18e'); draw = ImageDraw.Draw(guide)
    for box,color in [((110,130,370,400),'#c9bba6'),((650,130,970,370),'#c4b69f'),
                      ((1090,125,1400,350),'#bfc4a3'),((130,680,335,920),'#c8bca6'),
                      ((650,680,960,920),'#b1bf95'),((1090,720,1460,970),'#8f9f75')]:
        draw.rounded_rectangle(box,radius=16,fill=color)
    spine=[(546,0),(536,64),(515,190),(490,370),(465,542),(430,800),(410,1024)]
    lateral=[(0,541.5),(64,542),(465,542),(950,555),(1250,605),(1536,620)]
    draw.line(spine,fill='#d5cfbc',width=97,joint='curve');draw.line(spine,fill='#747c7d',width=69,joint='curve')
    draw.line(lateral,fill='#d5cfbc',width=71,joint='curve');draw.line(lateral,fill='#747c7d',width=43,joint='curve')
    guide.paste(north,(0,0));guide.paste(west,(0,0));guide.save(refs/'D-structure.png')
    save(refs/'input-record.json',{'guideRole':'structure-only, not final artwork','guideRoads':[spine,lateral],
         'north':'actual-north-64.png','west':'actual-west-64.png','fullNeighborAttached':False,
         'nativeIndependentDProduced':False,'northAndWestBandsExcludeUnproducedStatusPlate':True})
    print(json.dumps({'prepared':True,'northActualCenter':contract['northActual']['centerDLocalX'],
                      'westActualCenter':contract['westActual']['centerDLocalY'],'requestsMade':0},ensure_ascii=False))


if __name__=='__main__':
    main()
