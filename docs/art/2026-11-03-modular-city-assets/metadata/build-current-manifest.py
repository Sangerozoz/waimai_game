"""Static native-image metadata + isolated street-corner layout. No image edits or engine access."""
import hashlib
import json
import math
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[2]
CITY_PATH = PROJECT / 'delivery-game/assets/resources/map-sample/city.json'
city = json.loads(CITY_PATH.read_text())
node = {n['id']: [n['x'], n['y']] for n in city['nodes']}
records = {x['id']: x for x in json.loads((ROOT/'generation-records.json').read_text())['images']}
projection = {'axisX': [.8660254, .5], 'axisY': [-.8660254, .5], 'vertical': [0, -1], 'pixelsPerMeter': 32}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def inverse(p, a):
    x, y = p[0]-a[0], p[1]-a[1]
    return [y+x/math.sqrt(3), y-x/math.sqrt(3)]
def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def ptseg(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; z=dx*dx+dy*dy
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/z)) if z else 0
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def inside(p, poly):
    hit=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if ptseg(p,a,b)<1e-9: return True
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]: hit=not hit
    return hit
def intersects(a,b,c,d):
    v=[cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)]
    if v[0]*v[1]<0 and v[2]*v[3]<0: return True
    return any(abs(vv)<1e-9 and ptseg(p,q,r)<1e-9 for vv,p,q,r in [(v[0],c,a,b),(v[1],d,a,b),(v[2],a,c,d),(v[3],b,c,d)])
def segpoly(a,b,p):
    if inside(a,p) or inside(b,p): return 0
    ds=[]
    for c,d in zip(p,p[1:]+p[:1]):
        if intersects(a,b,c,d): return 0
        ds.extend([ptseg(a,c,d),ptseg(b,c,d),ptseg(c,a,b),ptseg(d,a,b)])
    return min(ds)
def polydist(p,q):
    if inside(p[0],q) or inside(q[0],p): return 0
    return min(segpoly(a,b,q) for a,b in zip(p,p[1:]+p[:1]))

# Pixels are manual candidates from native originals, not calibrated surveys.
building_inputs = [
    ('B01',[674,1200],[[95,930],[480,698],[620,785],[840,650],[1055,790],[1194,905],[674,1200],[350,1020],[290,1051]],[1,2,3,4],[2,7],[[[350,1020],[674,1200]],[[674,1200],[1194,905]]],[-1571,63]),
    ('B02',[526,1249],[[208,1099],[749,788],[1067,938],[526,1249]],[1],[],[[[208,1099],[526,1249]],[[526,1249],[1067,938]]],[-1578.5,79]),
    ('B03',[746,1234],[[160,998],[503,724],[1089,960],[746,1234]],[1],[],[[[160,998],[746,1234]],[[746,1234],[1089,960]]],[-1564,93]),
]
assets=[]; annotation=[]; placements=[]
def add_asset(id, kind, anchor_pixel, polygon, width, footprint=None, notes=None):
    rec=records[id]; p=ROOT/rec['file']; im=Image.open(p); w,h=im.size
    a={'id':id,'file':rec['file'],'kind':kind,'nativeSize':[w,h],
       'anchor':[round(anchor_pixel[0]/w,8),round(anchor_pixel[1]/h,8)] if anchor_pixel else [],
       'groundPolygon':[[round(x/w,8),round(y/h,8)] for x,y in polygon],
       'footprintMeters':footprint or [],'displayWidthMeters':width,
       'facing':'upright complete native bitmap; no 2D rotation',
       'source':{'tool':rec['tool'],'originalPath':rec['originalPath'],'sha256':sha(p)},
       'notes':notes or []}
    if im.mode=='RGBA':
        al=im.getchannel('A'); hist=al.histogram()
        alpha={'zeroPixels':hist[0],'fullyOpaquePixels':hist[255],'pixelsAtLeast250':sum(hist[250:]),'bounds':al.getbbox(),
               'notes':'Native alpha unchanged; sparse residuals make threshold-1 bounds unsuitable for ground anchors.'}
    else: alpha={'mode':im.mode,'notes':'Opaque repeating material, not a transparent sprite.'}
    assets.append(a); annotation.append({'id':id,'anchorPixel':anchor_pixel,'groundPolygonPixels':polygon,'alpha':alpha})
    return a,annotation[-1]

for id,anchor,poly,hidden,concave,edges,pos in building_inputs:
    a,ann=add_asset(id,'building',anchor,poly,18,notes=[
        'Manual wall-ground anchor, normalized from original top-left; v increases downward. Cocos anchorY must convert to bottom-left as 1-v.',
        'displayWidthMeters is the whole native canvas width. Preserve native aspect ratio; no shear, crop, rotation or nonuniform scaling.',
        'Occluded rear ground corners are estimated. Layout and footprint are candidates, not survey measurements or user acceptance.'])
    ppm=a['nativeSize'][0]/a['displayWidthMeters']; local=[[v/ppm for v in inverse(p,anchor)] for p in poly]
    a['footprintMeters']=[round(max(p[i] for p in local)-min(p[i] for p in local),4) for i in [0,1]]
    ann.update(hiddenEstimatedVertexIndices=hidden,concaveVertexIndices=concave,localGroundFootprintMeters=local)
    vec=[[e[1][0]-e[0][0],e[1][1]-e[0][1]] for e in edges]; slopes=[y/x for x,y in vec]
    elev=math.degrees(math.atan(math.sqrt(-slopes[0]*slopes[1]))); iv=[inverse(v,[0,0]) for v in vec]
    co=sum(x*y for x,y in zip(*iv))/math.prod(math.hypot(*v) for v in iv); angle=math.degrees(math.acos(max(-1,min(1,co))))
    ann['cameraCandidate']={'groundEdgeSamplesPixels':edges,'screenEdgeDegrees':[round(math.degrees(math.atan2(y,x)),3) for x,y in vec],
        'inferredElevationIfRectangularDegrees':round(elev,3),'inverseNominalEdgeAngleDegrees':round(angle,3),
        'status':'approximately-compatible-with-30-degree-camera' if abs(angle-90)<4 else 'small-camera-residual-remains',
        'notes':'Manual edge candidates. A different horizontal facing can explain unequal screen slopes only if nominal inverse edges remain approximately orthogonal.'}
    a['facing']={'B01':'two front faces approximately aligned with nominal map axes; stepped footprint',
                 'B02':'narrow front screen lower-left and long side lower-right; v2 camera closer, residual remains',
                 'B03':'broad front screen lower-left, narrow side lower-right; unequal angles consistent approximately with rotated facing under nominal camera'}[id]
    a['notes'].append('Camera candidate: elevation %.2f degrees if rectangular, nominal inverse edge angle %.2f degrees; not exact calibration.'%(elev,angle))
    placements.append({'id':'building-'+id.lower(),'assetId':id,'map':pos,'scale':1,'layer':10,
                       'groundFootprint':[[round(pos[0]+x,6),round(pos[1]+y,6)] for x,y in local]})

for id,foot,width in [('T02',[593,1065],6.6),('T03',[594,1075],6.8),('P01',[514,1414],3.8)]:
    p=[[foot[0]-25,foot[1]-12],[foot[0],foot[1]-25],[foot[0]+25,foot[1]-12],[foot[0],foot[1]+2]]
    a,ann=add_asset(id,'tree' if id.startswith('T') else 'prop',foot,p,width,[.7,.7],notes=[
        'Anchor manually follows visible trunk/pole ground contact, not canvas bottom or alpha bounding box.',
        'Ground footprint is a small conservative 0.7m root/base extent; canopy may overlap in screen space and needs depth sorting.',
        'Original native PNG and alpha preserved; candidate, no engine/user acceptance.'])
    if id=='P01':
        ann['alpha']['outsideHaloSamples']={str(p):Image.open(ROOT/records[id]['file']).getpixel(p)[3] for p in [(350,500),(350,1000),(700,500),(700,1000),(300,200)]}
        a['notes'].append('Daytime unlit v2 lantern. Apparent exterior RGB halo has zero-alpha at sampled exterior points; use normal sprite alpha, not additive blending.')
for id in ['S01','S02']:
    material,ann=add_asset(id,'material',None,[],4,notes=['Opaque native repeating material; anchor/groundPolygon/footprintMeters intentionally empty. Use on exact source-road or paving geometry.'])
    material['id']=ann['id']='S01-paving' if id=='S01' else 'S02-asphalt'

rider_manifest_path=PROJECT/'docs/art/2026-11-03-county-sample-production/rider-directions/manifest.json'
rm=json.loads(rider_manifest_path.read_text()); rider_source=next(x for x in rm['assets'] if x['file']=='rider-d-ne.png')
rp=Path(rider_source['project_path']); shutil.copyfile(rp,ROOT/'R01-rider.png')
assets.append({'id':'R01','file':'R01-rider.png','kind':'rider','nativeSize':rider_source['actual_size'],
    'anchor':rider_source['groundAnchorNormalized'],'groundPolygon':[],'footprintMeters':[.8,1.9],
    'displayWidthMeters':3.2,'facing':'ne; native existing direction frame, no rotation',
    'source':{'tool':'byte-identical copy of existing image_gen asset','originalPath':str(rp),'sha256':sha(rp)},
    'notes':['Ground anchor copied from existing rider manifest: midpoint of wheel contacts; original top-left normalized UV.',
             'Existing D rider/vehicle identity; no new image generation or pixel edits. Source manifest: '+str(rider_manifest_path),
             'Single native NE pose for the isolated route demo; reverse movement would need another existing frame for precise facing.']})

def base_polygon(pos,r=.35):
    return [[round(pos[0]+r*math.cos(i*math.pi/4),6),round(pos[1]+r*math.sin(i*math.pi/4),6)] for i in range(8)]
tree_points=[[-1592,48],[-1596,64],[-1600,80],[-1580,66],[-1577,82],[-1557,94],[-1567,105]]
lamp_points=[[-1590,44],[-1594,60],[-1598,76],[-1587,86],[-1576,95],[-1553,99]]
for i,pos in enumerate(tree_points): placements.append({'id':'tree-%02d'%(i+1),'assetId':'T02' if i%2==0 else 'T03','map':pos,'scale':1,'layer':10,'groundFootprint':base_polygon(pos)})
for i,pos in enumerate(lamp_points): placements.append({'id':'lamp-%02d'%(i+1),'assetId':'P01','map':pos,'scale':1,'layer':10,'groundFootprint':base_polygon(pos,.3)})

# Full source nodes retained; only the viewport is clipped, never the road data.
road_ids=['149397380-0','149397519-0','1046196059-0']
roads=[{'id':r['id'],'width':r['width'],'nodes':[node[n] for n in r['nodes']],'sourceNodeIds':r['nodes'],'kind':r['kind'],'direction':r['direction']} for r in city['roads'] if r['id'] in road_ids]
segments=[(r['id'],r['width'],node[a],node[b]) for r in city['roads'] for a,b in zip(r['nodes'],r['nodes'][1:])]
analysis=[]
for p in placements:
    gp=p['groundFootprint']; closest=min((segpoly(a,b,gp)-width/2,rid) for rid,width,a,b in segments)
    other=[q['id'] for q in placements if q['id']!=p['id'] and polydist(gp,q['groundFootprint'])<1e-7]
    water=[i for i,w in enumerate(city['areas']) if w.get('kind')=='water' and len(w.get('points',[]))>2 and polydist(gp,w['points'])==0]
    waterways=[i for i,line in enumerate(city['waterways']) if any(segpoly(a,b,gp)==0 for a,b in zip(line,line[1:]))]
    analysis.append({'id':p['id'],'nearestRoadId':closest[1],'carriagewayClearanceMeters':round(closest[0],4),
        'carriagewayOverlap':closest[0]<=0,'otherDisplayFootprintOverlaps':other,'waterAreaOverlapIndices':water,'waterwayCenterlineOverlapIndices':waterways})
manifest={'schemaVersion':1,'status':'current-candidate-not-user-accepted','projection':projection,'assets':assets,
          'notes':['All anchors use native top-left UV (v increases downward); adapt to Cocos bottom-left anchor as needed.',
                   'Only current v2 B02/B03/T02/P01 and T03 are used; rejected front-view T02 and superseded v1 building/lamp files excluded.']}
layout={'schemaVersion':1,'status':'isolated-art-layout-candidate-not-game-tested','origin':{'x':-1580,'y':75},
    'source':{'path':str(CITY_PATH.relative_to(PROJECT)),'sha256':sha(CITY_PATH),'roadIds':road_ids,'buildingReferenceIndices':[143,144,145]},
    'projection':projection,'placements':placements,'roads':roads,
    'bounds':{'minX':-1606,'maxX':-1551,'minY':43,'maxY':108},
    'displayClip':{'minX':-1606,'maxX':-1551,'minY':43,'maxY':108},
    'sourceSampleBounds':{'minX':-1720,'maxX':-1340,'minY':-240,'maxY':200},
    'rider':{'assetId':'R01','map':[-1589.05,64.5],'direction':'ne','roadId':'149397380-0',
        'route':[[-1593.7454,84.0],[-1587.7244,59.0]],'mode':'memory-only-demonstration','notes':'Route candidates lie on one unchanged source centerline segment; no orders, business or save access.'},
    'notes':['55x65m near viewport clips display only; all three selected original roads keep every native source node.',
             'Three independent complete buildings, seven trees, six daytime lamps; road-aligned paving only, no boxed building substitutes.',
             'Source 143/144/145 are parcel references only. Other source buildings are not rendered in this isolated art sample; original city.json remains unchanged.',
             'All static clearance calculations use ALL city road segments and their width/2 as carriageway boundary. No source sidewalk widths provided.',
             'Ground corners/root radii are honest manual candidates; exact hidden rear corners and canopy/roof occlusion need actual composition review.',
             'Sort buildings, trees, lamps, rider by projected ground foot y; preserve intact PNGs and alpha. No game testing or user acceptance claimed.']}
current={'schemaVersion':1,'status':'manual-current-candidate','sourceGenerationRecordsSha256':sha(ROOT/'generation-records.json'),
         'annotations':annotation,'staticGeometryAnalysis':analysis,'segmentsConsidered':len(segments),
         'limitations':['No engine/browser/render/tests/typecheck. Source images and city.json unchanged.',
                        'Waterways have no width in source: only centerline overlap checked. Hidden wall corners remain estimates.']}
for p,d in [(ROOT/'asset-manifest.json',manifest),(ROOT/'sample-layout.json',layout),(ROOT/'metadata/current-annotations.json',current)]:
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'files':{p.name:sha(p) for p in [ROOT/'asset-manifest.json',ROOT/'sample-layout.json',ROOT/'metadata/current-annotations.json',ROOT/'R01-rider.png']},'staticGeometryAnalysis':analysis},ensure_ascii=False,indent=2))
