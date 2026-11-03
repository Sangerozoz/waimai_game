"""Record native sources and uniform frontage registration; never edits image pixels."""
import json, math, hashlib
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
layout=json.loads((R/'scene-layout.json').read_text())
ann=json.loads((R/'metadata/manual-annotations.json').read_text())
axes=layout['projection']; origin=axes['originMap']
def project(p):
    return [sum((p[j]-origin[j])*axes['axis'+['X','Y'][j]][i] for j in range(2)) for i in range(2)]
def unproject(p):
    a,b=axes['axisX'],axes['axisY'];det=a[0]*b[1]-a[1]*b[0]
    return [origin[0]+(p[0]*b[1]-p[1]*b[0])/det, origin[1]+(p[1]*a[0]-p[0]*a[1])/det]
def native(item):
    rec=json.loads((R/'metadata'/item['sourceRecord']).read_text()); p=R/item['file']
    im=Image.open(p)
    assert im.mode=='RGBA' and hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
    alpha=im.getchannel('A'); bb=alpha.point(lambda x:255 if x>8 else 0).getbbox()
    assert alpha.getextrema()[0]==0 and bb
    return rec,im,bb
assets=[];records=[]
for parcel in layout['parcels']:
    aid=parcel['assetId']; item=ann['blocks'][aid];rec,im,bb=native(item)
    points=[]
    for control in item['groundControls']:
        i=int(control['name'].split('-')[-1]);m=parcel['groundPolygon'][i]
        points.append(dict(**control,map=m,projected=project(m)))
    used=[p for p in points if p['name'] in item['fitControlNames']]
    mx=[sum(p['projected'][i] for p in used)/len(used) for i in range(2)]
    mp=[sum(p['pixel'][i] for p in used)/len(used) for i in range(2)]
    numerator=sum((p['projected'][i]-mx[i])*(p['pixel'][i]-mp[i]) for p in used for i in range(2))
    denominator=sum((p['projected'][i]-mx[i])**2 for p in used for i in range(2))
    scale=numerator/denominator
    shift=[mp[i]-scale*mx[i] for i in range(2)]
    ap=project(parcel['anchorMap']);anchor=[ap[i]*scale+shift[i] for i in range(2)]
    for p in points:
        predicted=[p['projected'][i]*scale+shift[i] for i in range(2)]
        p['predictedPixel']=predicted;p['residualPixels']=math.dist(predicted,p['pixel']);p['residualProjectionUnits']=p['residualPixels']/scale
        p['artBoundaryMapCandidate']=unproject([(p['pixel'][i]-shift[i])/scale for i in range(2)])
    a=dict(id=aid,file=item['file'],kind='block',nativeSize=list(im.size),sha256=rec['sha256'],
        anchorUV=[anchor[i]/im.size[i] for i in range(2)],anchorMap=parcel['anchorMap'],sortMap=parcel['anchorMap'],
        nativePixelsPerUnit=scale,projectionId=axes['id'],controlPoints=points,
        registration=dict(method='frontage-two-points-uniform-scale-and-translation-no-rotation',estimatedControlsIncluded=any(not p['visible'] for p in used),maxRearResidualProjectionUnits=max(p['residualProjectionUnits'] for p in points),status='approximate-painted-candidate-not-four-corner-calibration'),
        visibleEntrances=item['visibleEntrances'],observations=item['observations'])
    assets.append(a); parcel['artStatus']='native-candidate-manually-registered-approximate';parcel['artBoundaryMapCandidate']=[p['artBoundaryMapCandidate'] for p in points]
    records.append(dict(id=aid,**rec,prompt=json.loads((R/rec['promptFile']).read_text()),observations=item['observations']))
for aid,item in ann['riders'].items():
    rec,im,bb=native(item);w,h=im.size;anchor=item['wheelContactAnchorPixel']
    a=dict(id=aid,file=item['file'],kind='rider',nativeSize=[w,h],sha256=rec['sha256'],direction=item['direction'],projectionId=axes['id'],
        anchorUV=[anchor[0]/w,anchor[1]/h],wheelContactAnchorUV=[anchor[0]/w,anchor[1]/h],nativePixelsPerUnit=1,
        opaqueBoundsUV=[bb[0]/w,bb[1]/h,bb[2]/w,bb[3]/h],opaqueBoundsThreshold='alpha>8',
        wheelContactPixels=item['wheelContactPixels'],observations=item['observations'])
    assets.append(a);records.append(dict(id=aid,**rec,prompt=json.loads((R/rec['promptFile']).read_text()),observations=item['observations']))
for rec in records:
    rec['referenceSources']=[dict(path=str((R/s).resolve()),sha256=hashlib.sha256((R/s).read_bytes()).hexdigest()) for s in rec['prompt']['references']]
manifest=dict(schemaVersion=1,packageComplete=len(assets)==4,status='native-candidates-not-user-accepted-not-game-tested',projection=axes,assets=assets,
    notes=['All native source bytes and alpha preserved; no image pixel edits, mirroring, plane rotation or nonuniform deformation.',
        'Engine roads use exact common62.5 projection. Painted blocks have local residuals; registration does not prove exact camera/heights or original-business-coordinate changes.'])
(R/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(R/'generation-records.json').write_text(json.dumps(dict(tool='built-in image_gen',records=records),ensure_ascii=False,indent=2)+'\n')
layout['camera']=dict(focusMap=origin,viewWidthUnits=54,screenOffset=[0,0],referenceWidth=720,referenceHeight=1280)
(R/'scene-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([dict(id=a['id'],size=a['nativeSize'],ppu=a['nativePixelsPerUnit'],anchor=a['anchorUV'],registration=a.get('registration')) for a in assets],indent=2))
