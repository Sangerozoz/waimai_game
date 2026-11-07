"""Read-only candidate audit; --write-report records this bounded verification."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = BASE.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    result = read(HERE/'result.json')
    native = Image.open(HERE/'native.png')
    assert native.size == (1672,941) and native.mode == 'RGB'
    assert result['actualSize'] == [1672,941] and result['bytes'] == (HERE/'native.png').stat().st_size == 3934287
    assert sha(HERE/'native.png') == result['sha256'] == '8c159c4dfdbe34b1bb62e7aac7bad4c097a153e99c34d40bb6f3845c30210fa3'
    assert (HERE/'native.png').read_bytes() == Path(result['toolDefaultOutputPath']).read_bytes()
    assert not result['actualRoadTraceCompleted'] and not result['userArtApproved'] and not result['ordinaryRegionAdmitted']
    assert result['actualCompleteBlockCount'] is None and result['metreCalibration'] is None
    request = read(HERE/'request-record.json')
    assert request['status'] == 'completed-one-native-return' and request['tool'] == 'image_gen.imagegen' and request['mode'] == 'built-in'
    assert request['arguments']['prompt'] == (HERE/'prompt.txt').read_text() and sha(HERE/'prompt.txt') == request['promptSHA256']
    refs = read(HERE/'input-fingerprints.json')
    assert request['inputRoles'] == refs and request['arguments']['referenced_image_paths'] == [str(ROOT/item['path']) for item in refs]
    for item in refs:
        path = ROOT/item['path']
        assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'] and list(Image.open(path).size) == item['size']
    parent = BASE/'organic-adjacent-005/seam-003/assembly/pair-native.png'
    reference = Image.open(HERE/'references/approved-pair-north.png')
    assert ImageChops.difference(reference,Image.open(parent).crop((1520,0,3192,240))).getbbox() is None
    assert ImageChops.difference(reference,Image.open(HERE/'structure-input.png').crop((0,701,1672,941))).getbbox() is None
    new_band = native.crop((0,701,1672,941))
    assert ImageChops.difference(new_band,Image.open(HERE/'inspection/006-shared-band.png')).getbbox() is None
    assert ImageChops.difference(reference,Image.open(HERE/'inspection/approved-shared-band.png')).getbbox() is None
    aa,bb = new_band.tobytes(),reference.tobytes()
    exact = sum(aa[i:i+3] == bb[i:i+3] for i in range(0,len(aa),3))
    error = sum(abs(a-b) for a,b in zip(aa,bb))/len(aa)
    comparison = read(HERE/'inspection/shared-band-comparison.json')
    assert comparison['comparisonPixels'] == 401280 and comparison['pixelsExactlyEqual'] == exact == 25
    assert abs(comparison['meanAbsoluteRGBError']-error) < 1e-12 and not comparison['wholeSeamReady'] and not comparison['actualRoadHandoffsVerified']
    observations = read(HERE/'observations.json')
    assert observations['actualCompleteBlockCount'] is None and not observations['actualRoadTraceCompleted']
    assert observations['designDeviations'][0]['designRoad'] == 'J3--L3' and not observations['designDeviations'][0]['navigationAllowed']
    assert observations['sharedBand']['straightCutAtY701MayCutVisibleBuildings'] and not observations['sharedBand']['completeObjectSourceSelectionPerformed']
    parent_review = read(BASE/'organic-adjacent-005/seam-003/user-review-001.json')
    assert parent_review['userCompositeApproved'] and parent_review['sha256'] == sha(parent) and not parent_review['formalGameTestsAuthorized']
    tiled = read(HERE/'tiled/native006.tmj')
    assert (tiled['width'],tiled['height'],tiled['tilewidth'],tiled['tileheight']) == (1672,941,1,1)
    assert tiled['orientation'] == 'orthogonal' and not tiled['tilesets'] and len(tiled['layers']) == 2
    image,design = tiled['layers']
    assert image['type'] == 'imagelayer' and image['image'] == '../native.png' and image['visible'] and image['locked'] and image['opacity'] == 1
    assert (image['imagewidth'],image['imageheight'],image['offsetx'],image['offsety']) == (1672,941,0,0)
    assert (HERE/'tiled'/image['image']).resolve() == (HERE/'native.png').resolve()
    assert design['type'] == 'objectgroup' and design['visible'] is False and design['name'] == 'archived-design-hidden-not-navigation'
    guide = read(HERE/'structure-guide.json')
    objects = design['objects']
    assert len(objects) == len(guide['roads']) == len({obj['name'] for obj in objects}) == 25
    assert {obj['name'] for obj in objects} == {road['id'] for road in guide['roads']}
    for road in guide['roads']:
        obj = next(obj for obj in objects if obj['name'] == road['id'])
        assert obj['rotation'] == 0 and obj['width'] == obj['height'] == 0 and len(obj['polyline']) == len(road['points'])
        assert [[obj['x']+point['x'],obj['y']+point['y']] for point in obj['polyline']] == road['points']
        assert obj['properties'] == [{'name':'designOnly','type':'bool','value':True},
            {'name':'navigationAllowed','type':'bool','value':False},{'name':'kind','type':'string','value':road['kind']}]
    assert sorted(obj['id'] for obj in objects) == list(range(1,tiled['nextobjectid']))
    assert sorted(layer['id'] for layer in tiled['layers']) == list(range(1,tiled['nextlayerid']))
    props = tiled['properties']
    assert len(props) == len({prop['name'] for prop in props})
    assert all((prop['type']=='bool' and type(prop['value']) is bool) or (prop['type']=='string' and type(prop['value']) is str) for prop in props)
    values = {prop['name']:prop['value'] for prop in props}
    assert values == {'unit':'native pixels','nativeArtworkSHA256':result['sha256'],'actualRoadTraceCompleted':False,
        'navigationReady':False,'wholeSeamReady':False,'metreCalibration':'unestablished','userArtApproved':False,
        'ordinaryRegionAdmitted':False,'formalGameTestsPerformed':False}
    data = read(HERE/'viewer-data.json')
    assert data == {'native':result,'sharedComparison':comparison}
    assert (HERE/'index.html').read_text() == (HERE/'viewer-template.html').read_text().replace('__006_DATA__',json.dumps(data,ensure_ascii=False))
    for name,item in read(HERE/'generated-files.json').items():
        assert sha(HERE/name) == item['sha256'] and (HERE/name).stat().st_size == item['bytes'],name
    cli = read(HERE/'verification/tiled-native-001/result.json')
    assert cli['tiledSHA256'] == sha(HERE/'tiled/native006.tmj') and cli['nativeRGBPixelExact'] and cli['alphaExtrema'] == [255,255]
    exported = Image.open(HERE/'verification/tiled-native-001/native.png')
    assert exported.size == native.size and ImageChops.difference(native,exported.convert('RGB')).getbbox() is None
    browser = read(HERE/'verification/browser-checks.json')
    assert browser['checkCount'] == 7 and all(check['passed'] for check in browser['checks'])
    for item in browser['captures']:
        assert sha(HERE/'verification'/item['file']) == item['sha256']
    assert read(HERE/'verification/browser-close.json')['state'] == 'closed'
    start = read(HERE/'start-record.json')
    for name,item in start['priorManifest']['files'].items():
        path = HERE/'history/start'/name if name in start['allowedExistingUpdates'] else BASE/name
        assert sha(path) == item['sha256'],name
    assert sha(HERE/'history/start/new-thread-receipt.json') == start['priorManifest']['externalReceipt']['sha256']
    protected = read(ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json')
    for name,item in protected['files'].items():
        assert sha(ROOT/name) == item['sha256'],name
    report = {'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'passed-single-native-artifact-and-display-audit',
        'nativeSize':[1672,941],'nativeSHA256':result['sha256'],'bytes':result['bytes'],'toolOutputCopiedExactly':True,
        'inputFingerprintsMatched':len(refs),'priorArtifactCount':len(start['priorManifest']['files']),'protectedFilesMatched':len(protected['files']),
        'hiddenNonNavigableDesignObjectsVerified':25,'actualRoadGraphCreated':False,'sharedPixelsCompared':401280,
        'sharedPixelsExactlyEqual':exact,'meanAbsoluteRGBError':error,'TiledNativeExports':1,'TiledNativeRGBPixelExact':True,
        'browserDisplayChecks':7,'browserCaptures':3,'browserSessionClosed':True,'userArtApproved':False,'wholeSeamReady':False,
        'ordinaryRegionAdmitted':False,'formalGameTestsPerformed':False,'visualArtAndNavigationCertifiedByScript':False}
    if args.write_report:
        (HERE/'verification/integrity-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    main()
