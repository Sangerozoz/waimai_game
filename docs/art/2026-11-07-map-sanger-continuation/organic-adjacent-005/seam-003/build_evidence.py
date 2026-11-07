"""Pair navigation is a bounded sample freshly observed on the candidate, not a city graph."""
import copy
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OLD = HERE.parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    output = module(HERE / 'build_seam.py', 'seam_output')
    helper = module(OLD / 'build_actual_evidence.py', 'original_graph_algorithms')
    graph = json.loads((OLD / 'actual-pair-graph.json').read_text())
    graph['source'] = 'assembly/pair-native.png'
    graph['scope'] = '005 core visible-road subset plus004 main street, observed on this object-cut candidate; not full005/004 inventory'
    graph['assemblyStatus'] = 'whole-object cut candidate; source images unchanged; seam approval separate'
    graph['completeObjectOwnershipResolved'] = False
    graph['wholeSeamRegistrationComplete'] = False
    graph['formalMapAdmission'] = False
    graph['forbiddenInferenceSource'] = '../revision-002/actual-005-graph.json#OC1--EJ'
    graph['forbiddenInferenceIncludedInNavigation'] = False
    graph['sourceTraceBeforeThisIncrement'] = '../actual-pair-graph.json'
    changed = next(edge for edge in graph['edges'] if edge['id'] == 'E-MP--R1')
    graph['previousFirstEastEdge'] = copy.deepcopy(changed)
    changed.update(points=[[1520,501],[1558,495],[1581,488],[1640,463],[1728,454],[1824,455],[1916,460],[1974,453]],
                   sourceRegion='mixed005-004-at-new-cut', surfaceObservation='visible-asphalt-manual-trace',
                   traceRevision='seam003; first east edge re-sampled on new assembly')
    changed['lengthPixels'] = sum(math.dist(a,b) for a,b in zip(changed['points'],changed['points'][1:]))
    graph['statistics'],graph['boundedFaceGeometry'] = helper.analyse(graph)
    graph['routes'] = {'main':helper.route(graph,'W-MW','E-R4'),
                       'alternative':helper.route(graph,'W-MW','E-R4','W-M1--ML')}
    contacts = json.loads((HERE / 'contact-input.json').read_text())
    images = {'005':Image.open(OLD / 'native.png'), '004':Image.open(OLD.parent / 'organic-layout-004/native.png')}
    for contact in contacts['contacts']:
        x,y = contact['pointPair']
        contact.update(point005=[x,y],point004=[x-1520,y],
                       nativeRGB005=list(images['005'].getpixel((x,y))),nativeRGB004=list(images['004'].getpixel((x-1520,y))),
                       visibleAsphaltObservedInBoth=True)
    tiled = helper.tmj(graph,[('004 unchanged native','../../../organic-layout-004/native.png',1672,941,1520,0),
                             ('005 selected native pixels','../assembly/005-selected.png',1671,941,0,0)])
    # Original roof-occluded structure remains explicitly forbidden and hidden.
    prior = json.loads((OLD / 'revision-002/actual-005-graph.json').read_text())
    inferred = next(edge for edge in prior['edges'] if edge['id'] == 'OC1--EJ')
    obj = helper.polyobj(tiled['nextobjectid'],'005-OC1--EJ',inferred['points'],
                         {'navigationAllowed':False,'surfaceObservation':'roof-occluded-inference-not-navigable',
                          'source':'005 revision002 structural inference only'})
    tiled['layers'].append({'id':tiled['nextlayerid'],'name':'occluded-inference-not-navigation','type':'objectgroup',
                            'visible':False,'opacity':1,'draworder':'index','color':'#b67f17','objects':[obj]})
    tiled['nextlayerid'] += 1
    tiled['nextobjectid'] += 1
    seam_input = json.loads((HERE / 'seam-input.json').read_text())
    cut_object = helper.polyobj(tiled['nextobjectid'],'editable-source-cut',seam_input['cutPolyline'],
        {'source005OnLeft':True,'navigationAllowed':False,'derivedImageRebuildRequired':True,'inputFile':'../seam-input.json'})
    tiled['layers'].append({'id':tiled['nextlayerid'],'name':'source-cut-guide-rebuild-mask-after-edit','type':'objectgroup',
                            'visible':False,'opacity':1,'draworder':'index','color':'#ff0088','objects':[cut_object]})
    tiled['nextlayerid'] += 1
    tiled['nextobjectid'] += 1
    tiled['properties'] = helper.props({'unit':'native pixels','metreCalibration':'unestablished','wholeSeamRegistrationComplete':False,
        'fullStreetInventoryComplete':False,'ordinaryRegionAdmitted':False,'formalGameTests':False,'trafficVerified':False,
        'assemblyStatus':'object-cut candidate; separate from native art approval','forbiddenRoofInferenceIncludedInNavigation':False})
    viewer = {'graph':graph,'contacts':contacts,'seam':seam_input,'inferredEdge':inferred}
    outputs = {'actual-pair-graph.json':output.encoded(graph),'contacts.json':output.encoded(contacts),
               'tiled/organic-pair.tmj':output.encoded(tiled),'viewer-data.json':output.encoded(viewer)}
    pair = Image.open(HERE / 'assembly/pair-native.png')
    draw = ImageDraw.Draw(pair)
    for edge in graph['edges']:
        draw.line([tuple(point) for point in edge['points']], fill='#dd3199', width=2)
    for kind,color in [('main','#00a675'),('alternative','#e79812')]:
        draw.line([tuple(point) for point in graph['routes'][kind]['points']],fill=color,width=3)
    outputs['inspection/pair-routes.png'] = output.png(pair)
    template = (HERE / 'viewer-template.html').read_text()
    assert template.count('__SEAM_DATA__') == 1
    outputs['index.html'] = template.replace('__SEAM_DATA__',json.dumps(viewer,ensure_ascii=False)).encode()
    output.write_owned(outputs)
    print(json.dumps({'statistics':graph['statistics'],'routes':{key:value['lengthPixels'] for key,value in graph['routes'].items()},
                      'newImageGeneration':False,'cityInventoryComplete':False}))


if __name__ == '__main__':
    main()
