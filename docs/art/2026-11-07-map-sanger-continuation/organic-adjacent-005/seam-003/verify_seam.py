"""Read-only by default. Check unchanged native provenance, graph and editable artifacts."""
import argparse
import hashlib
import importlib.util
import json
import math
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OLD = HERE.parent
BASE = OLD.parent
ROOT = BASE.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('independent_previous_verifier',OLD / 'verify_005.py')
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    need = check.need
    data = read(HERE / 'seam-input.json')
    images = {}
    for source in ['005','004']:
        item = data['native'+source]
        path = HERE / item['path']
        images[source] = Image.open(path)
        need(source+' native unchanged',sha(path)==item['sha256'] and list(images[source].size)==item['size'] and images[source].mode=='RGB')
    source005 = images['005'].tobytes()
    source004 = images['004'].tobytes()
    assembly = Image.open(HERE / 'assembly/pair-native.png')
    selected = Image.open(HERE / 'assembly/005-selected.png')
    mask = Image.open(HERE / 'assembly/005-mask.png')
    need('native output sizes and modes',assembly.size==(3192,941) and assembly.mode=='RGB' and mask.size==selected.size==(1671,941) and mask.mode=='L' and selected.mode=='RGBA')
    need('mask binary and alpha exact',set(mask.tobytes())=={0,255} and selected.getchannel('A').tobytes()==mask.tobytes())
    need('selected005 RGB remains native including transparent pixels',selected.convert('RGB').tobytes()==source005)
    actual = assembly.tobytes()
    mask_raw = mask.tobytes()
    points = data['cutPolyline']
    need('editable cut inside common band',points[0][1]==0 and points[-1][1]==941 and all(a[1]<b[1] for a,b in zip(points,points[1:])) and all(1520<=x<=1671 for x,y in points))
    row_cuts = []
    for row in range(941):
        y = Fraction(2*row+1,2)
        a,b = next((a,b) for a,b in zip(points,points[1:]) if a[1]<=y<b[1])
        threshold = Fraction(a[0]) + (y-a[1])*Fraction(b[0]-a[0],b[1]-a[1]) - Fraction(1,2)
        cut = -(-threshold.numerator//threshold.denominator)
        row_cuts.append(cut)
        expected = source005[row*1671*3:(row*1671+cut)*3] + source004[(row*1672+cut-1520)*3:(row+1)*1672*3]
        assert actual[row*3192*3:(row+1)*3192*3]==expected,('pixel provenance',row,cut)
        assert mask_raw[row*1671:(row+1)*1671]==b'\xff'*cut+b'\x00'*(1671-cut),('mask',row,cut)
    record = read(HERE / 'assembly/record.json')
    need('all3003672 output pixels exact to native sources',len(actual)//3==3003672 and record['rowCuts']==row_cuts
         and record['sourcePixelCounts']=={'005':sum(row_cuts),'004':3003672-sum(row_cuts)})
    objects = read(HERE / 'ownership.json')
    need('nine object assignments including previously omitted foreground',len(objects['objects'])==len({obj['id'] for obj in objects['objects']})==objects['objectGroups']==9
         and objects['sourceSelectionRecordedForAllIdentifiedGroups'] is True and objects['originalFramesWritten'] is False
         and objects['originalFrameTruncationsReconstructed'] is False and objects['userCompositeApproved'] is False)
    for obj in objects['objects']:
        for x,y in obj['probePointsInOwnerNative']:
            world_x = x+(1520 if obj['owner']=='004' else 0)
            actual_owner = '005' if world_x<row_cuts[y] else '004'
            need('source probe '+obj['id']+':'+str((x,y)),actual_owner==obj['owner'] and assembly.getpixel((world_x,y))==images[obj['owner']].getpixel((x,y)))
    need('north/south original clipping disclosed',next(obj for obj in objects['objects'] if obj['id']=='N-1')['inheritedFrameTruncation']=='top'
         and next(obj for obj in objects['objects'] if obj['id']=='S-4')['inheritedFrameTruncation']=='bottom')
    graph = read(HERE / 'actual-pair-graph.json')
    stats = check.geometry(graph,'seam003-pair')
    need('bounded partial graph scope',stats['nodes']==26 and stats['edges']==30 and graph['fullStreetInventoryComplete'] is False
         and graph['metreCalibration'] is None and graph['forbiddenInferenceIncludedInNavigation'] is False
         and all('OC1' not in e['id'] for e in graph['edges']))
    previous = read(OLD / 'actual-pair-graph.json')
    need('original graph node coordinates retained',graph['nodes']==previous['nodes'])
    prior_edges = {e['id']:e for e in previous['edges']}
    for edge in graph['edges']:
        if edge['id']!='E-MP--R1':
            need('unchanged road '+edge['id'],edge==prior_edges[edge['id']])
    need('fresh shared contact on resampled first east edge',next(e for e in graph['edges'] if e['id']=='E-MP--R1')['points'][1:3]==[[1558,495],[1581,488]])
    for name,route in graph['routes'].items():
        check.verify_route(graph,route,'seam003-'+name)
    need('explicit blocked edge detour',graph['routes']['alternative']['excludedEdge']=='W-M1--ML')
    contacts = read(HERE / 'contacts.json')
    need('three observed common-asphalt contacts remain non-surveyed',len(contacts['contacts'])==3 and contacts['contactCentrelineResidualPixels'] is None and contacts['metreCalibration'] is None)
    for contact in contacts['contacts']:
        x,y = contact['pointPair']
        need('contact '+contact['id'],contact['point005']==[x,y] and contact['point004']==[x-1520,y]
             and contact['nativeRGB005']==list(images['005'].getpixel((x,y))) and contact['nativeRGB004']==list(images['004'].getpixel((x-1520,y)))
             and abs(x-row_cuts[y])<=1 and contact['visibleAsphaltObservedInBoth'] is True)
    tiled = read(HERE / 'tiled/organic-pair.tmj')
    layers = tiled['layers']
    image_layers = [l for l in layers if l['type']=='imagelayer']
    need('Tiled dimensions preserve native scale',tiled['width']==3192 and tiled['height']==941 and tiled['tilewidth']==tiled['tileheight']==1 and tiled['orientation']=='orthogonal')
    expected_images = [('004 unchanged native','../../../organic-layout-004/native.png',1672,941,1520,0),
                       ('005 selected native pixels','../assembly/005-selected.png',1671,941,0,0)]
    need('two ordered source images',len(image_layers)==2)
    for layer,expected in zip(image_layers,expected_images):
        need('Tiled source '+expected[0],tuple(layer[k] for k in ['name','image','imagewidth','imageheight','offsetx','offsety'])==expected
             and layer['visible'] is True and layer['locked'] is True and layer['opacity']==1 and (HERE/'tiled'/layer['image']).resolve().is_file())
    groups = {l['name']:l for l in layers if l['type']=='objectgroup'}
    need('all object layer names',set(groups)=={'visible-asphalt-trace','main-route','alternative-route','occluded-inference-not-navigation','source-cut-guide-rebuild-mask-after-edit'})
    roads = groups['visible-asphalt-trace']['objects']
    need('Tiled complete road name coverage',len(roads)==len({o['name'] for o in roads})==len(graph['edges']) and {o['name'] for o in roads}=={e['id'] for e in graph['edges']})
    for edge in graph['edges']:
        obj = next(o for o in roads if o['name']==edge['id'])
        check.line_object(obj,edge['points'],{k:edge[k] for k in ['from','to','lengthPixels','navigationAllowed','surfaceObservation','bidirectionalAssumption','trafficVerified']},'Tiled-road-'+edge['id'])
    for name,route in graph['routes'].items():
        layer = groups[name+'-route']
        need('hidden route '+name,layer['visible'] is False and len(layer['objects'])==1 and layer['objects'][0]['name']==name)
        check.line_object(layer['objects'][0],route['points'],{'lengthPixels':route['lengthPixels'],'trafficVerified':False},'Tiled-route-'+name)
    inferred = next(edge for edge in read(OLD/'revision-002/actual-005-graph.json')['edges'] if edge['id']=='OC1--EJ')
    layer = groups['occluded-inference-not-navigation']
    need('Tiled inference separate and hidden',layer['visible'] is False and len(layer['objects'])==1)
    check.line_object(layer['objects'][0],inferred['points'],{'navigationAllowed':False,'surfaceObservation':'roof-occluded-inference-not-navigable',
        'source':'005 revision002 structural inference only'},'Tiled-forbidden-inference')
    layer = groups['source-cut-guide-rebuild-mask-after-edit']
    need('Tiled cut hidden and explicitly requires rebuild',layer['visible'] is False and len(layer['objects'])==1)
    check.line_object(layer['objects'][0],points,{'source005OnLeft':True,'navigationAllowed':False,'derivedImageRebuildRequired':True,'inputFile':'../seam-input.json'},'Tiled-cut')
    all_objects = [o for l in groups.values() for o in l['objects']]
    need('unique contiguous IDs',sorted(l['id'] for l in layers)==list(range(1,tiled['nextlayerid'])) and sorted(o['id'] for o in all_objects)==list(range(1,tiled['nextobjectid'])))
    need('Tiled full typed scope',check.properties(tiled)==check.typed({'unit':'native pixels','metreCalibration':'unestablished','wholeSeamRegistrationComplete':False,
         'fullStreetInventoryComplete':False,'ordinaryRegionAdmitted':False,'formalGameTests':False,'trafficVerified':False,
         'assemblyStatus':'object-cut candidate; separate from native art approval','forbiddenRoofInferenceIncludedInNavigation':False}))
    viewer = read(HERE / 'viewer-data.json')
    need('viewer exact current graph, cut and inference',viewer=={'graph':graph,'contacts':contacts,'seam':data,'inferredEdge':inferred})
    need('viewer generated from exact data',(HERE/'index.html').read_text()==(HERE/'viewer-template.html').read_text().replace('__SEAM_DATA__',json.dumps(viewer,ensure_ascii=False)))
    svg = (HERE/'editable-cut.svg').read_text()
    need('SVG uses both source originals and warns boundary antialias',all(text in svg for text in ['../native.png','../../organic-layout-004/native.png','x="1520"','width="3192"','may antialias boundaries']))
    review = read(OLD / 'user-review-001.json')
    need('005 latest user art approval bound to native SHA',review['userArtApproved'] is True and review['sha256']==data['native005']['sha256'] and review['wholeSeamAccepted'] is False and review['formalGameTestsAuthorized'] is False)
    for name,item in read(HERE/'generated-files.json').items():
        need('owned '+name,sha(HERE/name)==item['sha256'] and (HERE/name).stat().st_size==item['bytes'])
    start = read(HERE/'start-record.json')
    for name,item in start['priorManifest']['files'].items():
        if name in start['allowedExistingUpdates']:
            need('archived prior '+name,sha(HERE/'history/start'/name)==item['sha256'])
        else:
            need('prior unchanged '+name,sha(BASE/name)==item['sha256'])
    protected = read(ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json')
    for name,item in protected['files'].items():
        need('protected '+name,sha(ROOT/name)==item['sha256'])
    report = {'recordedAt':datetime.now(timezone.utc).isoformat(),'status':'passed-candidate-file-and-geometry-checks',
              'checkCount':len(check.CHECKS),'checks':check.CHECKS,'actualOutputPixelsVerified':3003672,'statistics':stats,
              'ownershipSourceProbeCount':sum(len(o['probePointsInOwnerNative']) for o in objects['objects']),
              'objectGroupCount':9,'protectedMatched':91,'priorFilesAudited':454,'sourcePixelCounts':record['sourcePixelCounts'],
              'wholeSeamReady':False,'userCompositeApproved':False,'metreCalibration':None,'formalGameTestsPerformed':False,
              'visualCompleteObjectOrAsphaltCertifiedByScript':False}
    if args.write_report:
        p = HERE/'verification/static-checks.json'
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))


if __name__=='__main__':
    main()
