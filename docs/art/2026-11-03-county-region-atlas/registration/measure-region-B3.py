"""Observe B3 edit using unchanged B2 transform so refit cannot hide drift."""
import json,math,hashlib,copy
from pathlib import Path
R=Path('docs/art/2026-11-03-county-region-atlas/registration');art=R.parent/'images/REGION-B-v3.png';reg=json.loads((R/'registration-B-v2.json').read_text());reg['id']='REGION-B-v3';reg['sourceArt'].update(file=str(art),sha256=hashlib.sha256(art.read_bytes()).hexdigest());f=reg['fit'];f['method']='Inherited fixed B2 62.5/45 uniform transform. Reobserved B3 junctions/endpoints; no refit after edit.'
changes={'J1-1623821610':[228,517],'EDGE-W-149396514':[57,622],'SHARED-E-149397548':[293,550],'SHARED-N-149396913':None}
for e in reg['controlPoints']:
 if e['id'] in changes:e['imagePx']=changes[e['id']]
 if e['imagePx'] is None:
  e['errorPixels']=None;e['errorVectorPixels']=None;e['confidence']='unpaired-after-edit';e['observation']='B3 bends drawn road toward upper-left; no unique visible vertex for this map point. Required shared target [498.12,373.16] remains on original building. Closest manually traced road centre is ~85-95px away.'
 else:e['errorPixels']=math.dist(e['projectedPx'],e['imagePx']);e['errorVectorPixels']=[e['projectedPx'][k]-e['imagePx'][k] for k in [0,1]]
f['fitMaxResidualPixels']=max(e['errorPixels'] for e in reg['controlPoints'] if e['usedInFit']);f['allObservedMaxResidualPixels']=max(e['errorPixels'] for e in reg['controlPoints'] if e['errorPixels'] is not None)
reg['additionalDrawnStreet'].update(classification='removed-in-B3-replaced-by-courtyard-paving',routeEligible=False);reg['status']='shared-junction-improved-north-roof-conflict-persists';reg['observedNorthRoadPolylineNative']=[[228,517],[350,411],[417,332],[460,286],[520,249],[620,198],[704,142]]
(R/'registration-B-v3.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
entry=json.loads((R/'region-B-runtime-entry.json').read_text());entry.update(file=art.name,sha256=reg['sourceArt']['sha256']);entry['registration'].update(evidence=str(R/'registration-B-v3.json'),controlPoints=[dict(map=e['sourceMap'],pixel=e['imagePx'],confidence=e['confidence']) for e in reg['controlPoints'] if e['imagePx'] is not None],maxResidualPixels=f['allObservedMaxResidualPixels']);entry['note']='B3 shared junction/west/main-east endpoints improve. Northern shared route still crosses building in source projection: excluded until whole-scene edit. Internal east main-road corridor may be PM-authorized separately.'
(R/'region-B-v3-runtime-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
seam=json.loads((R/'A-B-seam-production.json').read_text());seam['id']='REGION-A__REGION-B-v3-observation';seam['BArt']='REGION-B-v3.png';t=seam['BToANativeDiagnosticTransform'];new={'shared-junction-1623821610':[228,517],'shared-main-east-149397548':[293,550],'shared-southwest-149396514':[57,622],'shared-north-149396913':None}
for e in seam['targets']:
 e['BCurrent']=new[e['id']]
 if e['BCurrent']:
  e['BEditDeltaPixels']=[e['BTargetNativePixel'][k]-e['BCurrent'][k] for k in [0,1]];e['currentWorldMismatchAtANativePixels']=math.dist([t['uniformScale']*e['BCurrent'][k]+t['translation'][k] for k in [0,1]],e['AObserved'])
 else:e['BEditDeltaPixels']=None;e['currentWorldMismatchAtANativePixels']=None;e['roofConflict']=dict(target=[498.1205,373.1637],stillInside='unchanged left/middle frontage building group',nearestObservedRoadDistancePixelsApprox=[85,95])
seam['editGuide']='diagnostic/B-v3-north-seam-edit-guide.png';seam['stitched']=False;seam['ownershipCandidate']['reason']='B3 improves three endpoints, but north shared street remains roof-conflicted; candidate source partition stays unready. Red/blue native guide supplied for direct whole-scene edit.'
(R/'A-B-v3-seam-observation.json').write_text(json.dumps(seam,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'fit':f,'seamTargets':seam['targets']},indent=2))
