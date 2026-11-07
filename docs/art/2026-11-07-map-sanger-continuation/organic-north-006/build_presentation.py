"""Present the returned006 native and archived design without admitting a road graph."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def properties(values):
    return [{'name': key, 'type': 'bool' if isinstance(value, bool) else 'string', 'value': value}
            for key, value in values.items()]


def main():
    result = json.loads((HERE / 'result.json').read_text())
    assert sha(HERE / 'native.png') == result['sha256']
    guide = json.loads((HERE / 'structure-guide.json').read_text())
    objects = []
    for index, road in enumerate(guide['roads'], 1):
        x, y = road['points'][0]
        objects.append({'id': index, 'name': road['id'], 'type': 'design-only-pixel-polyline',
                        'x': x, 'y': y, 'width': 0, 'height': 0, 'rotation': 0, 'visible': True,
                        'polyline': [{'x': px-x, 'y': py-y} for px, py in road['points']],
                        'properties': properties({'designOnly': True, 'navigationAllowed': False, 'kind': road['kind']})})
    tiled = {'type': 'map', 'version': '1.10', 'tiledversion': '1.12.2', 'orientation': 'orthogonal',
             'renderorder': 'right-down', 'infinite': False, 'width': result['actualSize'][0],
             'height': result['actualSize'][1], 'tilewidth': 1, 'tileheight': 1, 'tilesets': [],
             'nextlayerid': 3, 'nextobjectid': len(objects)+1,
             'properties': properties({'unit': 'native pixels', 'nativeArtworkSHA256': result['sha256'],
                 'actualRoadTraceCompleted': False, 'navigationReady': False, 'wholeSeamReady': False,
                 'metreCalibration': 'unestablished', 'userArtApproved': False, 'ordinaryRegionAdmitted': False,
                 'formalGameTestsPerformed': False}),
             'layers': [
                 {'id': 1, 'name': '006 native unchanged', 'type': 'imagelayer', 'image': '../native.png',
                  'imagewidth': result['actualSize'][0], 'imageheight': result['actualSize'][1],
                  'offsetx': 0, 'offsety': 0, 'visible': True, 'locked': True, 'opacity': 1},
                 {'id': 2, 'name': 'archived-design-hidden-not-navigation', 'type': 'objectgroup',
                  'draworder': 'index', 'visible': False, 'opacity': 1, 'color': '#a28d65', 'objects': objects},
             ]}
    viewer = {'native': result, 'sharedComparison': json.loads((HERE / 'inspection/shared-band-comparison.json').read_text())}
    template = (HERE / 'viewer-template.html').read_text()
    assert template.count('__006_DATA__') == 1
    outputs = {'tiled/native006.tmj': encoded(tiled), 'viewer-data.json': encoded(viewer),
               'index.html': template.replace('__006_DATA__', json.dumps(viewer, ensure_ascii=False)).encode()}
    manifest_path = HERE / 'generated-files.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name in outputs:
        path = HERE / name
        if path.exists():
            assert name in previous and sha(path) == previous[name]['sha256'], name
    for name, raw in outputs.items():
        path = HERE / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    manifest_path.write_bytes(encoded({name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                                       for name, raw in sorted(outputs.items())}))
    print(json.dumps({'nativeSize': result['actualSize'], 'designObjectsHidden': len(objects),
                      'newActualRoadGraph': False, 'userArtApproved': False, 'nativeArtworkModified': False}))


if __name__ == '__main__':
    main()
