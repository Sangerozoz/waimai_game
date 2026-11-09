#!/usr/bin/env python3
"""Prepare approved map batches as data only. All writes confined to009/pipeline.
No main-map apply command, engine copy, source mutation, or game execution.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import copy
import hashlib
import json
import math
import re
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
KIT = ROOT.parents[1]
BASE = KIT / 'revision-006'
REPO = KIT.parents[2]
STAGING = ROOT / 'staging'
PALETTE = {'G01-lawn':'#9da981','G02-planting':'#82906e','G03-meadow':'#a7ae8d',
           'G04-suburb-lawn':'#9fb986','G05-garden-soil':'#9b8261','G06-b07-garden':'#a3bc8a'}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def writable(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Output must remain inside009/pipeline')
    return path


def write(path, value):
    path = writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def finite_pair(value):
    if not isinstance(value, list) or len(value) != 2 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in value):
        raise ValueError('Expected finite coordinate pair')
    return value


def same_points(a, b, tolerance=1e-8):
    return len(a) == len(b) and all(math.dist(finite_pair(x), finite_pair(y)) <= tolerance for x,y in zip(a,b))


def project(point, projection):
    dx,dy = [point[k]-projection['originMap'][k] for k in (0,1)]
    return [dx*projection['axisX'][k]+dy*projection['axisY'][k] for k in (0,1)]


def unproject(point, projection):
    a,b = projection['axisX']; c,d = projection['axisY']; determinant=a*d-b*c
    return [projection['originMap'][0]+(d*point[0]-c*point[1])/determinant,
            projection['originMap'][1]+(-b*point[0]+a*point[1])/determinant]


def bbox(points):
    return [min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]


def intersects(a,b):
    return not (a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1])


def point_in_polygon(point, polygon):
    result=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>point[1]) != (b[1]>point[1]) and point[0] < (b[0]-a[0])*(point[1]-a[1])/(b[1]-a[1])+a[0]:
            result=not result
    return result


def materials(surface):
    material=surface.get('materialId',surface.get('material'))
    if material in ('S01-paving','S02-asphalt'):
        return {'kind':'existing-image','assetId':material}
    if material in PALETTE:
        return {'kind':'controlled-color','color':PALETTE[material]}
    if material in ('neutral-grass','neutral-soil'):
        color=surface.get('color')
        if not isinstance(color,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',color):
            raise ValueError('Controlled ground requires explicit color; no invented texture/default')
        return {'kind':'controlled-color','color':color.lower()}
    raise ValueError('Unknown ground material: '+str(material))


def props(values):
    return [{'name':k,'type':'bool' if isinstance(v,bool) else 'float' if isinstance(v,(int,float)) else 'string','value':v}
            for k,v in values.items()]


class Context:
    def __init__(self):
        self.scene_path=BASE/'viewer/assets/scene-layout.json'
        self.map_path=BASE/'integration/neighborhood.tmj'
        self.library_path=BASE/'integration/asset-library.json'
        self.calibration_path=BASE/'integration/asset-calibration.json'
        self.scene=read(self.scene_path)
        self.map=read(self.map_path)
        self.library=read(self.library_path)
        self.assets={a['id']:a for a in self.library['assets']}
        self.cal={a['id']:a for a in read(self.calibration_path)['assets']}
        self.projection=self.scene['projection']
        self.city_path=REPO/'delivery-game/assets/resources/map-sample/city.json'
        city=read(self.city_path)
        self.source_buildings=city['buildings']
        self.nodes={n['id']:[n['x'],n['y']] for n in city['nodes']}
        self.roads={r['id']:r for r in city['roads']}
        self.objects={b['persistentId']:b for b in self.scene['blocks']}
        self.ground={g['id']:g for g in self.scene['groundSurfaces']}
        self.scene_assets={a['id']:a for a in read(BASE/'viewer/assets/asset-manifest.json')['assets']}
        self.source_hashes={str(p.resolve()):sha(p) for p in [self.scene_path,self.map_path,self.library_path,
                            self.calibration_path,self.city_path,BASE/'viewer/assets/main/index.probe41.js']}
        self.image_cache={}
        for road in self.scene['roads']:
            self.verify_road(road)

    def protect(self,path):
        path=Path(path).resolve(); current=sha(path)
        if str(path) in self.source_hashes and self.source_hashes[str(path)]!=current:
            raise ValueError('Source changed during prepare: '+str(path))
        self.source_hashes[str(path)]=current

    def verify_road(self,road):
        source=self.roads.get(road['id'])
        if source is None:
            raise ValueError('Road ID not in original city')
        expected=[self.nodes[n] for n in source['nodes']]
        if road['nodes'] != expected or road['width'] != source['width'] or road['direction'] != source['direction']:
            raise ValueError('Road nodes/order/width/direction differ from source city: '+road['id'])
        if road.get('sourceNodeIds',source['nodes']) != source['nodes']:
            raise ValueError('Source node IDs changed')
        return copy.deepcopy(road)

    def image(self,aid):
        a=self.assets[aid]; file=BASE/'integration/assets'/a['file']
        if file.resolve().parent != (BASE/'integration/assets').resolve():
            raise ValueError('Unsafe asset filename')
        if sha(file)!=a['sha256']:
            raise ValueError('Runtime image SHA mismatch')
        with Image.open(file) as image:
            if max(image.size)>280 or list(image.size)!=a['nativeSize']:
                raise ValueError('Runtime image exceeds280 or dimensions mismatch')
        self.protect(file)
        return file

    def normalize_object(self,obj,district_id):
        pid=obj.get('persistentId',obj.get('id')); aid=obj.get('libraryAssetId',obj.get('assetId'))
        if not pid or not aid or aid not in self.assets:
            raise ValueError('Missing stable persistentId or unavailable library asset; no white-box fallback')
        a=self.assets[aid]; calibration=self.cal.get(aid)
        status=a.get('availability','')
        if 'hold' in status or status.startswith('library-only'):
            raise ValueError('Asset admission forbids new placement: '+aid+' '+status)
        if not calibration:
            raise ValueError('Actual calibration required, no defaultPPU: '+aid)
        ppu=calibration.get('nativePixelsPerUnit',calibration.get('sourceNativePPU'))
        if not isinstance(ppu,(int,float)) or ppu<=0:
            raise ValueError('Missing positive original-native PPU; runtime nativePixelsPerUnit=1 is not calibration')
        for key in ('rotation','rotationPNG'):
            if obj.get(key,0)!=0:
                raise ValueError('Plane rotation forbidden')
        for key in ('mirrorPNG','mirror','flipX','flipY'):
            if obj.get(key,False):
                raise ValueError('Mirror/flip forbidden')
        scale=obj.get('uniformScale',1)
        if not isinstance(scale,(int,float)) or not math.isfinite(scale) or scale<=0:
            raise ValueError('Only positive uniform scale')
        for key in ('scaleX','scaleY'):
            if key in obj and obj[key]!=scale:
                raise ValueError('Nonuniform or conflicting scale component forbidden')
        for key in ('offsetx','offsety','rotationDegrees'):
            if obj.get(key,0)!=0:
                raise ValueError('Unsupported local transform; supply final anchorMap explicitly: '+key)
        world=[v*scale for v in a['worldSizeUnits']]
        if 'worldSizeUnits' in obj and not same_points([obj['worldSizeUnits']],[world]):
            raise ValueError('Nonuniform scale or world-size mismatch')
        if 'anchorUV' in obj and not same_points([obj['anchorUV']],[a['anchorUV']]):
            raise ValueError('Crop anchor mismatch')
        if aid in ('B01','T01') and not math.isclose(scale,1,abs_tol=1e-10):
            raise ValueError('Accepted B01/T01 scale fixed')
        anchor=finite_pair(obj['anchorMap']); self.image(aid)
        result={'persistentId':pid,'libraryAssetId':aid,'districtId':district_id,'anchorMap':anchor,
                'sortMap':finite_pair(obj.get('sortMap',anchor)),'worldSizeUnits':world,'anchorUV':a['anchorUV'],
                'originalNativePPU':ppu,'uniformScale':scale,'scaleSource':'actual-library-calibration',
                'sourceObject':copy.deepcopy(obj),'file':a['file'],'sha256':a['sha256']}
        if 'visualReplacementOf' in obj:
            binding=obj['visualReplacementOf']
            if 'sourceIndices' in binding:
                indices=binding['sourceIndices'];polygons=binding.get('sourcePolygonsMap')
                if not isinstance(indices,list) or not indices or len(set(indices))!=len(indices):raise ValueError('Invalid nonempty sourceIndices binding')
                if not isinstance(polygons,list) or len(polygons)!=len(indices):raise ValueError('sourceIndices/sourcePolygonsMap cardinality mismatch')
            elif 'sourceIndex' in binding:
                indices=[binding['sourceIndex']];polygons=[binding['sourcePolygonMap']]
            else:raise ValueError('Explicit real source index binding required; no invented ID')
            if any(not isinstance(index,int) or index<0 or index>=len(self.source_buildings) for index in indices):raise ValueError('Source index outside city.buildings')
            if any(self.source_buildings[index]!=polygon for index,polygon in zip(indices,polygons)):raise ValueError('Actual source polygon binding mismatch')
            if binding.get('sourceSHA256',binding.get('sourceCitySHA256'))!=sha(self.city_path):raise ValueError('Source binding citySHA mismatch')
            if binding.get('sourceDataChanged',False) is not False:raise ValueError('Source data mutation forbidden')
            result['sourceIndices']=copy.deepcopy(indices);result['sourcePolygonsMap']=copy.deepcopy(polygons)
            result['sourceBindingOriginal']=copy.deepcopy(binding)
        if a['kind']=='building' or aid.startswith('B'):
            if 'entryPixel' not in obj or 'entryMap' not in obj:
                raise ValueError('Building needs explicit actual entryPixel and entryMap')
            pixel=finite_pair(obj['entryPixel']); origin=calibration.get('anchorPixel',calibration.get('originalAnchorPixel'))
            if not origin:
                raise ValueError('Original pixel anchor missing')
            q=project(anchor,self.projection)
            door=unproject([q[k]+(pixel[k]-origin[k])/ppu*scale for k in (0,1)],self.projection)
            if math.dist(door,finite_pair(obj['entryMap']))>1e-7:
                raise ValueError('Actual native door coordinate does not match map entry')
            if aid=='B07' and pixel!=calibration['entryPixel']:
                raise ValueError('B07 must use corrected door11; no transparent fake door')
            derivation=a['runtimeDerivation']; source=Path(derivation['source'])
            if not source.is_absolute():source=REPO/source
            self.protect(source)
            if sha(source)!=derivation['sourceSHA256']:
                raise ValueError('Native calibration sourceSHA changed')
            with Image.open(source) as image:
                px,py=[round(v) for v in pixel]
                if not(0<=px<image.width and 0<=py<image.height) or image.convert('RGBA').getpixel((px,py))[3]==0:
                    raise ValueError('Door pixel outside native or fully transparent; not a valid visible threshold')
            result['doorCoordinateCheck']={'entryPixel':pixel,'convertedMap':door,'declaredMap':obj['entryMap'],
                'differenceUnits':math.dist(door,obj['entryMap']),'scope':'coordinate/alpha only; semantic door/manual footprint not automatically certified'}
        if a['kind']=='parked-vehicle':
            result['requiresParkingSpaceId']=obj.get('parkingSpaceId')
            if not obj.get('candidateBodyPolygonMap'):
                raise ValueError('Parked vehicle needs explicit candidate body polygon; wheel midpoint is not body centre')
        q=project(anchor,self.projection);w,h=world;au,av=a['anchorUV']
        screen=[[q[0]-au*w,q[1]-av*h],[q[0]+(1-au)*w,q[1]-av*h],
                [q[0]+(1-au)*w,q[1]+(1-av)*h],[q[0]-au*w,q[1]+(1-av)*h]]
        result['conservativeVisibilityBoundsMap']=bbox([unproject(p,self.projection) for p in screen])
        result['tiledObject']={'name':pid,'type':'sprite','x':896+(q[0]-au*w)*16,
            'y':896+(q[1]+(1-av)*h)*16,'width':w*16,'height':h*16,'rotation':0,
            'visible':obj.get('visible',True),'properties':props({'persistentId':pid,'assetId':aid})}
        if pid in self.objects:
            old=self.objects[pid]; olda=self.scene_assets[old['assetId']]
            if old['sourceAssetId']!=aid or math.dist(old['anchorMap'],anchor)>1e-8 or not same_points([olda['worldSizeUnits']],[world]) or olda['anchorUV']!=a['anchorUV']:
                raise ValueError('Existing persistentId has changed placement/asset/scale; refusing overwrite')
            result['baselineStatus']='already-present-identical'
        else:result['baselineStatus']='new'
        return result


def all_tiles(bounds,size):
    for tx in range(math.floor(bounds[0]/size),math.floor(bounds[2]/size)+1):
        for ty in range(math.floor(bounds[1]/size),math.floor(bounds[3]/size)+1):
            yield f't{size}:{tx}:{ty}',[tx*size,ty*size,(tx+1)*size,(ty+1)*size]


def tile_index(objects,surfaces,roads,projection,asset_keys,size=64):
    tiles={}
    def entry(tile,bounds):
        return tiles.setdefault(tile,{'id':tile,'clipBoundsMap':bounds,'objectIds':[],'surfaceIds':[],
                                    'sourceRoadIds':[],'assetKeys':[]})
    for o in objects:
        for tid,b in all_tiles(o['conservativeVisibilityBoundsMap'],size):
            t=entry(tid,b);t['objectIds'].append(o['persistentId']);t['assetKeys'].append(o['file']+'#'+o['sha256'])
    for s in surfaces:
        for tid,b in all_tiles(bbox(s['sourceSurface']['polygonMap']),size):
            t=entry(tid,b);t['surfaceIds'].append(s['id'])
            if s['material']['kind']=='existing-image':t['assetKeys'].append(asset_keys[s['material']['assetId']])
    for t in tiles.values():
        b=t['clipBoundsMap']
        for r in roads:
            margin=r['width']/2+1.8
            if any(intersects([min(a[0],z[0])-margin,min(a[1],z[1])-margin,max(a[0],z[0])+margin,max(a[1],z[1])+margin],b)
                   for a,z in zip(r['nodes'],r['nodes'][1:])):t['sourceRoadIds'].append(r['id'])
        if t['sourceRoadIds']:t['assetKeys'].append(asset_keys['S02-asphalt'])
        t['assetKeys']=sorted(set(t['assetKeys']));t['clipping']='canvas clip only; original polygons/road nodes remain intact'
    return {'schemaVersion':1,'tileSizeMapUnits':size,'projection':projection,'tiles':sorted(tiles.values(),key=lambda t:t['id']),
            'role':'conservative reference index; sprites/ground IDs may span tiles, not duplicate image payloads',
            'fullRoadGeometryStoredOnce':'converted-plan.json/sourceRoads','sourceGraphEdgesAdded':0}


def prepare(args):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',args.batch_id):raise ValueError('Invalid stable batchId')
    if args.index<0:raise ValueError('batchIndex must be nonnegative')
    out=writable(STAGING/args.batch_id)
    if out.exists():raise ValueError('Batch already staged; refusing duplicate import or reset: '+args.batch_id)
    staged_objects=set();staged_surfaces=set()
    for previous in STAGING.glob('*/prepare-report.json'):
        if read(previous)['batchIndex']==args.index:
            raise ValueError('batchIndex already staged; no implicit replacement: '+str(args.index))
        previous_delta=read(previous.parent/'difference.json')
        staged_objects.update(previous_delta['newObjects']);staged_surfaces.update(previous_delta['newSurfaces'])
    plan_path=Path(args.plan).resolve()
    if sha(plan_path)!=args.parent_sha:raise ValueError('Fixed parent-approved source SHA does not match')
    ctx=Context();ctx.protect(plan_path);ctx.protect(__file__);source=read(plan_path)
    if source.get('schemaVersion')=='scene-compound-static-v1':
        raise ValueError('Compound pilot requires the limited compound_import.py preflight/apply entry; legacy batch preparation cannot flatten scene ownership')
    if source['projection']!=ctx.projection:raise ValueError('Projection differs from fixed57-instance baseline')
    if args.demonstration_existing and not(len(ctx.scene['blocks'])==57 and len(ctx.scene['groundSurfaces'])==115):
        raise ValueError('Demonstration requires the supplied57/115 baseline')
    for p in [ROOT/'schema.json',ROOT/'budget-policy.json']:
        if p.exists():ctx.protect(p)
    districts=source.get('districts') or [source]
    objects=[];surfaces=[];roadmap={};rejected=[];ids=set();surfaceids=set();district_index=[];slots={}
    for j,district in enumerate(districts):
        did=district.get('districtId',district.get('id',f'{args.batch_id}-district-{j:02}'))
        meta={k:copy.deepcopy(district.get(k,source.get(k))) for k in ['zoning','zone','landuse','landUse','site','selectedSite','batchMetadata']}
        district_index.append({'districtId':did,'inputIndex':j,'metadata':meta,'objectIds':[],'surfaceIds':[]})
        for s in district.get('parkingSpaces',[]):
            if s['id'] in slots and slots[s['id']]!=s:raise ValueError('Conflicting parking ID')
            slots[s['id']]=s
        for road in district.get('roads',source.get('roads',[])):
            road=ctx.verify_road(road)
            if road['id'] in roadmap and roadmap[road['id']]!=road:raise ValueError('Conflicting duplicate source road')
            roadmap[road['id']]=road
        items=district.get('buildings',[])+district.get('fixtures',[])+district.get('parkedVehicles',[])
        for item in items:
            pid=item.get('persistentId',item.get('id'))
            if pid in ids:raise ValueError('Duplicate persistentId within batch, no silent renaming: '+str(pid))
            ids.add(pid)
            try:
                if pid in staged_objects:raise ValueError('PersistentId already reserved by another staged batch')
                obj=ctx.normalize_object(item,did)
                if obj.get('requiresParkingSpaceId'):
                    slot=slots.get(obj['requiresParkingSpaceId'])
                    if not slot or not all(point_in_polygon(p,slot['polygonMap']) for p in item['candidateBodyPolygonMap']):
                        raise ValueError('Vehicle body does not fit original planned parking slot')
                if obj['baselineStatus']=='already-present-identical' and not args.demonstration_existing:
                    raise ValueError('PersistentId already imported in baseline; replay forbidden without explicit demonstration mode')
                objects.append(obj);district_index[-1]['objectIds'].append(pid)
            except (ValueError,KeyError,TypeError) as exc:
                rejected.append({'persistentId':pid,'libraryAssetId':item.get('libraryAssetId',item.get('assetId')),'reason':str(exc),'fallbackCreated':False})
        rejectedids={r['persistentId'] for r in rejected if r['persistentId']}
        for surface in district.get('groundSurfaces',[]):
            sid=surface['id']
            if sid in staged_surfaces:raise ValueError('Ground ID already reserved by another staged batch: '+sid)
            if sid in surfaceids:raise ValueError('Duplicate ground ID inside batch: '+sid)
            surfaceids.add(sid);owner=surface.get('ownerBuildingId',surface.get('containsBuildingId',surface.get('buildingId')))
            if owner in rejectedids or any(sid.startswith(p+'-') for p in rejectedids):
                rejected.append({'surfaceId':sid,'reason':'exclusive ground for rejected object','fallbackCreated':False});continue
            polygon=surface['polygonMap']
            if len(polygon)<3:raise ValueError('Invalid surface polygon')
            for p in polygon:finite_pair(p)
            mat=materials(surface);status='new'
            if sid in ctx.ground:
                old=ctx.ground[sid]
                if not same_points(old['polygonMap'],polygon) or materials(old)!=mat:
                    raise ValueError('Existing ground ID changed; refusing overwrite: '+sid)
                status='already-present-identical'
                if not args.demonstration_existing:raise ValueError('Ground already imported; explicit demonstration required')
            surfaces.append({'id':sid,'districtId':did,'material':mat,'sourceSurface':copy.deepcopy(surface),'baselineStatus':status})
            district_index[-1]['surfaceIds'].append(sid)
    oldroads={r['id']:r for r in ctx.scene['roads']};road_duplicates=[];newroads=[]
    for r in roadmap.values():
        if r['id'] in oldroads:
            o=oldroads[r['id']]
            if r['nodes']!=o['nodes'] or r['width']!=o['width'] or r['direction']!=o['direction']:raise ValueError('Existing road fields changed')
            road_duplicates.append(r['id'])
        else:newroads.append(r)
    newobjects=[o for o in objects if o['baselineStatus']=='new'];newsurfaces=[s for s in surfaces if s['baselineStatus']=='new']
    if args.demonstration_existing and (newobjects or newsurfaces or newroads):raise ValueError('Demonstration-existing cannot smuggle new geometry into staging')
    if not args.demonstration_existing and objects and not newobjects and not newsurfaces and not newroads:
        raise ValueError('No new geometry; duplicate batch import refused')
    if args.demonstration_existing and rejected:raise ValueError('Existing-data demo has rejected source objects; fix adapter rather than silently omitting evidence')
    # Complete baseline data is copied for review, not an engine or full-city analysis snapshot.
    merged=copy.deepcopy(ctx.scene);baseline_hash=digest(ctx.scene);nextorder=max(b['editorRenderOrder'] for b in merged['blocks'])+1
    asset_additions=[]
    for k,o in enumerate(newobjects):
        row={'assetId':'instance-'+o['persistentId'],'sourceAssetId':o['libraryAssetId'],'persistentId':o['persistentId'],'anchorMap':o['anchorMap'],'sortMap':o['sortMap'],'editorRenderOrder':nextorder+k}
        if not o['sourceObject'].get('visible',True):row['visible']=False
        merged['blocks'].append(row)
        asset=copy.deepcopy(ctx.assets[o['libraryAssetId']]);asset['id']=row['assetId']
        asset['worldSizeUnits']=o['worldSizeUnits'];asset_additions.append(asset)
    for s in newsurfaces:
        row=copy.deepcopy(s['sourceSurface']);row['materialId']=row.get('materialId',row.get('material'));merged['groundSurfaces'].append(row)
    merged['roads']+=newroads
    if args.demonstration_existing and merged!=ctx.scene:raise ValueError('Demonstration changed baseline')
    # CAS assets shared across staged batches. No PNG is copied once per sprite.
    refs=[];aids={o['libraryAssetId'] for o in objects}|{'S01-paving','S02-asphalt'}
    for aid in sorted(aids):
        a=ctx.assets[aid];file=ctx.image(aid);cas=writable(STAGING/'shared-assets'/(a['sha256']+'.png'))
        if cas.exists():
            if sha(cas)!=a['sha256']:raise ValueError('CAS payload corrupted')
        else:
            cas.parent.mkdir(parents=True,exist_ok=True)
            with cas.open('xb') as handle:handle.write(file.read_bytes())
        refs.append({'libraryAssetId':aid,'originalFile':a['file'],'sha256':a['sha256'],'relativeSharedPNG':'../shared-assets/'+cas.name,
                     'runtimeSize':a['nativeSize'],'bytes':file.stat().st_size,'imageFrameSharingKey':a['file']+'#'+a['sha256'],
                     'decodedRGBABytesEstimate':a['nativeSize'][0]*a['nativeSize'][1]*4})
    roads=list(roadmap.values());tiles=tile_index(objects,surfaces,roads,ctx.projection,{r['libraryAssetId']:r['imageFrameSharingKey'] for r in refs})
    normalized={'schemaVersion':1,'batchId':args.batch_id,'batchIndex':args.index,'projection':ctx.projection,'objects':objects,
                'groundSurfaces':surfaces,'sourceRoads':roads,'parkingSpaces':list(slots.values()),'districtIndex':district_index}
    for key in ['sourceMappings','sourceIndices','uniqueSourceCount','visualModuleCount','districtOrganization','originalTopology']:
        if key in source:normalized[key]=copy.deepcopy(source[key])
    if 'sourceIndices' in source:
        actual={index for obj in objects for index in obj.get('sourceIndices',[])}
        if not rejected and actual!=set(source['sourceIndices']):raise ValueError('Root/source-object sourceIndices sets differ')
    delta={'schemaVersion':1,'batchId':args.batch_id,'batchIndex':args.index,'baseSceneSHA256':sha(ctx.scene_path),
           'baseTiledSHA256':sha(ctx.map_path),'parentOriginalPath':str(plan_path),'parentApprovedOriginalSHA256':args.parent_sha,
           'mode':'demonstration-existing-only' if args.demonstration_existing else 'prepared-awaiting-parent-integration',
           'applyAllowed':False,'sourceGraphEdgesAdded':0,'newObjects':[o['persistentId'] for o in newobjects],
           'newSurfaces':[s['id'] for s in newsurfaces],'newRoadIds':[r['id'] for r in newroads],
           'alreadyPresentObjects':[o['persistentId'] for o in objects if o['baselineStatus']!='new'],
           'alreadyPresentSurfaces':[s['id'] for s in surfaces if s['baselineStatus']!='new'],'alreadyReferencedRoadIds':road_duplicates,
           'rejected':rejected,'immutableBaselineFields':['all existing blocks','all existing ground polygons','camera','cameraViews','rider','projection','origin'],
           'integrationGate':'future parent approval plus matching baseline SHA and no duplicate batchId required; this tool cannot apply to006'}
    # Real editable append group includes only accepted NEW objects. Demonstration delta is intentionally empty.
    tiledefs=[];gidmap={}
    for k,aid in enumerate(sorted({o['libraryAssetId'] for o in newobjects})):
        a=ctx.assets[aid];gidmap[aid]=k+1;tiledefs.append({'id':k,'image':'../shared-assets/'+a['sha256']+'.png','imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':props({'assetId':aid})})
    tiledobjects=[]
    for k,o in enumerate(newobjects):
        row=copy.deepcopy(o['tiledObject']);row.update({'id':k+1,'gid':gidmap[o['libraryAssetId']]});tiledobjects.append(row)
    groundobjects=[]
    for k,s in enumerate(newsurfaces,len(tiledobjects)+1):
        points=[project(p,ctx.projection) for p in s['sourceSurface']['polygonMap']];x,y=points[0]
        groundobjects.append({'id':k,'name':s['id'],'type':'ground-surface','x':896+x*16,'y':896+y*16,
            'polygon':[{'x':(p[0]-x)*16,'y':(p[1]-y)*16} for p in points],'properties':props({'sourceSurfaceId':s['id'],'materialJSON':json.dumps(s['material'])})})
    tiled={'type':'map','version':'1.10','tiledversion':'1.11.2','orientation':'orthogonal','renderorder':'right-down',
           'infinite':True,'width':0,'height':0,'tilewidth':32,'tileheight':32,'nextobjectid':len(tiledobjects)+len(groundobjects)+1,'nextlayerid':4,
           'tilesets':[{'firstgid':1,'name':'batch-calibrated-assets','tilewidth':280,'tileheight':280,'columns':0,'tilecount':len(tiledefs),'objectalignment':'bottomleft','tiles':tiledefs}] if tiledefs else [],
           'layers':[{'id':1,'name':args.batch_id+' append-only','type':'group','offsetx':0,'offsety':0,'layers':[
             {'id':2,'type':'objectgroup','name':'new ground only','draworder':'index','objects':groundobjects},
             {'id':3,'type':'objectgroup','name':'new sprites only','draworder':'index','objects':tiledobjects}]}]}
    out.mkdir(parents=True)
    write(out/'converted-plan.json',normalized);write(out/'difference.json',delta);write(out/'asset-references.json',refs)
    write(out/'asset-manifest-additions.json',asset_additions)
    write(out/'coordinate-report.json',{'projection':ctx.projection,
        'baselineRoadsVerified':len(ctx.scene['roads']),'baselineRoadNodesVerified':sum(len(r['nodes']) for r in ctx.scene['roads']),
        'inputRoads':[{'id':r['id'],'fullNodeCount':len(r['nodes']),'nodesOrderWidthDirectionUnchanged':True} for r in roads],
        'doors':[{'persistentId':o['persistentId'],**o['doorCoordinateCheck']} for o in objects if 'doorCoordinateCheck' in o],
        'baselineGroupsSnapshot':[{'id':g['id'],'name':g.get('name'),'offsetx':g.get('offsetx',0),'offsety':g.get('offsety',0)} for g in ctx.map['layers']],
        'existingTiledByteCopyPreservesAllNestedGroupsOffsetsVisibilityAndOrder':True,
        'newTiledContract':'final anchorMap in map units; append group starts at zero offset; sourceObject retains metadata; later hand-edited TMJ export uses existing006 exporter',
        'footprints':'actual source polygons retained in converted sourceObject; no inferred white-box footprint',
        'geometricScope':'static coordinate and native alpha checks only, no navigation or new visual acceptance'})
    write(out/'tile-index.json',tiles);write(out/'increment.tmj',tiled);write(out/'merged-scene-data.json',merged)
    shutil.copyfile(ctx.scene_path,out/'baseline-scene.json');shutil.copyfile(ctx.map_path,out/'baseline-editable-map.tmj')
    write(out/'source-protection-before.json',ctx.source_hashes)
    changed=[p for p,h in ctx.source_hashes.items() if sha(p)!=h]
    if changed:raise ValueError('Read-only sources changed during prepare: '+str(changed))
    report={'batchId':args.batch_id,'batchIndex':args.index,'inputObjects':len(objects),'inputGroundSurfaces':len(surfaces),'fullSourceRoadRecords':len(roads),
            'newObjects':len(newobjects),'newGroundSurfaces':len(newsurfaces),'newRoadReferences':len(newroads),
            'alreadyPresentObjects':len(delta['alreadyPresentObjects']),'alreadyPresentGroundSurfaces':len(delta['alreadyPresentSurfaces']),
            'rejections':len(rejected),'uniqueAssetReferences':len(refs),'uniqueReferencedPNGBytes':sum(r['bytes'] for r in refs),
            'candidateActiveTiles':len(tiles['tiles']),'baselineObjects':len(ctx.scene['blocks']),'baselineGroundSurfaces':len(ctx.scene['groundSurfaces']),
            'baselineSemanticSHA256':baseline_hash,'mergedBaselineFieldsPreserved':True,'parentApprovedOriginalSHA256':args.parent_sha,
            'convertedPlanSHA256':sha(out/'converted-plan.json'),'differenceSHA256':sha(out/'difference.json'),
            'protectedSources':len(ctx.source_hashes),'allSourceSHAUnchanged':True,'applyAllowed':False,'newMapRendered':False,
            'engineCopied':False,'gameTestsRun':False,'status':delta['mode']}
    write(out/'prepare-report.json',report);write(out/'package-manifest.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps(report,ensure_ascii=False))


def cache_window(args):
    package=writable(Path(args.package));tiles=read(package if package.is_file() else package/'tile-index.json');bounds=args.bounds
    if len(bounds)!=4 or any(not math.isfinite(v) for v in bounds) or bounds[0]>=bounds[2] or bounds[1]>=bounds[3]:raise ValueError('Invalid map viewport bounds')
    visible=[t for t in tiles['tiles'] if intersects(t['clipBoundsMap'],bounds)]
    policy=read(ROOT/'budget-policy.json');limit=policy['maxResidentTiles'];previous=read(writable(args.previous)) if args.previous else {'residentTileIds':[]}
    if len(visible)>limit:
        write(args.output,{'status':'blocked-visible-window-exceeds-resident-tile-cap','visibleTileIds':[t['id'] for t in visible],
                          'requiredVisibleTiles':len(visible),'limit':limit,'applyAllowed':False,'rendererChanged':False})
        print('Cache window blocked: no silent visible-tile omission');return
    centre=[(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2]
    candidates=[t for t in tiles['tiles'] if t not in visible]
    candidates.sort(key=lambda t:math.dist([(t['clipBoundsMap'][0]+t['clipBoundsMap'][2])/2,(t['clipBoundsMap'][1]+t['clipBoundsMap'][3])/2],centre))
    resident=visible+candidates[:min(policy['maxPrefetchTiles'],limit-len(visible))]
    proj=tiles['projection'];extent=tiles['tileSizeMapUnits']+2*policy['clipHaloMapUnits'];projected=[extent*(abs(proj['axisX'][k])+abs(proj['axisY'][k])) for k in (0,1)]
    density=min(policy['nominalGroundPixelsPerProjectedUnit'],policy['maxCanvasEdge']/max(projected));pixelbudget=policy['maxResidentGroundPixels']
    while True:
        size=[math.ceil(v*density) for v in projected];pixels=size[0]*size[1]*len(resident)
        if pixels<=pixelbudget:break
        density*=math.sqrt(pixelbudget/pixels)*.99999
    ids=[t['id'] for t in resident];out={'status':'data-cache-window-plan-not-rendered','residentTileIds':ids,'visibleTileIds':[t['id'] for t in visible],
         'prefetchTileIds':[t['id'] for t in resident if t not in visible],'evictTileIds':[t for t in previous['residentTileIds'] if t not in ids],
         'loadTileIds':[t for t in ids if t not in previous['residentTileIds']],'tileCanvasCandidateSize':size,'groundPixelsPerProjectedUnit':density,
         'residentGroundPixels':pixels,'groundGPUBytesRGBA8Estimate':pixels*4,'retainedCanvasCPUBytesEstimate':pixels*4,
         'assetKeysToAcquire':sorted({k for t in resident for k in t['assetKeys']}),'worldScaleChanged':False,
         'applyAllowed':False,'rendererChanged':False,'originalCameraRiderAndSceneUntouched':True,'measuredFPSOrMemory':False,
         'evictionContract':'future existing006 renderer must detach nodes then destroy unreferenced ground SpriteFrame/Texture2D; shared PNG frames use reference counts, no per-instance Texture'}
    write(args.output,out);print(json.dumps(out,ensure_ascii=False))


def build_index(args):
    combined={};projection=None;size=None;packages=[];batchids=set();indices=set();newids=set()
    for path in args.packages:
        package=writable(path);delta=read(package/'difference.json');index=read(package/'tile-index.json')
        if delta['batchId'] in batchids or delta['batchIndex'] in indices:raise ValueError('Duplicate batchId/index in tile registry')
        if newids.intersection(delta['newObjects']):raise ValueError('Duplicate new persistentId across packages')
        batchids.add(delta['batchId']);indices.add(delta['batchIndex']);newids.update(delta['newObjects'])
        if projection is not None and (projection!=index['projection'] or size!=index['tileSizeMapUnits']):raise ValueError('Tile projection/size mismatch')
        projection=index['projection'];size=index['tileSizeMapUnits']
        packages.append({'batchId':delta['batchId'],'batchIndex':delta['batchIndex'],'packagePath':str(package),
            'parentApprovedOriginalSHA256':delta['parentApprovedOriginalSHA256'],'differenceSHA256':sha(package/'difference.json'),
            'baseSceneSHA256':delta['baseSceneSHA256'],'mode':delta['mode']})
        for tile in index['tiles']:
            out=combined.setdefault(tile['id'],{'id':tile['id'],'clipBoundsMap':tile['clipBoundsMap'],
                'objectIds':[],'surfaceIds':[],'sourceRoadIds':[],'assetKeys':[],'batchIds':[]})
            if out['clipBoundsMap']!=tile['clipBoundsMap']:raise ValueError('Conflicting stable tile bounds')
            for key in ['objectIds','surfaceIds','sourceRoadIds','assetKeys']:out[key]=sorted(set(out[key]+tile[key]))
            out['batchIds'].append(delta['batchId'])
    result={'schemaVersion':1,'projection':projection,'tileSizeMapUnits':size,'packages':packages,
        'tiles':sorted(combined.values(),key=lambda t:t['id']),'applyAllowed':False,'newRenderedMap':False,
        'scope':'staged batch reference union only; existing006 world remains protected; shared payloads in staging/shared-assets'}
    write(args.output,result);print(json.dumps({'registryTiles':len(combined),'batches':len(packages),'applyAllowed':False}))


def audit(args):
    package=writable(args.package);manifest=read(package/'package-manifest.json')
    for name,value in manifest.items():
        if sha(package/name)!=value:raise ValueError('Staged file changed: '+name)
    report=read(package/'prepare-report.json');sources=read(package/'source-protection-before.json')
    if any(sha(p)!=h for p,h in sources.items()):raise ValueError('Protected source changed after staging')
    refs=read(package/'asset-references.json')
    for r in refs:
        png=writable(package/r['relativeSharedPNG'])
        if sha(png)!=r['sha256']:raise ValueError('CAS image changed')
    delta=read(package/'difference.json')
    if delta['mode']=='demonstration-existing-only':
        if read(package/'merged-scene-data.json')!=read(package/'baseline-scene.json'):raise ValueError('Demo changed old scene fields')
        if delta['newObjects'] or delta['newSurfaces'] or delta['newRoadIds']:raise ValueError('Demo contains new geometry')
    print(json.dumps({'package':str(package),'audit':'passed-static-data-integrity','newRenderedMap':False,
                      'baselineObjects':report['baselineObjects'],'baselineGroundSurfaces':report['baselineGroundSurfaces'],'newObjects':report['newObjects']},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--batch-id',required=True);p.add_argument('--index',type=int,required=True);p.add_argument('--plan',required=True);p.add_argument('--parent-sha',required=True);p.add_argument('--demonstration-existing',action='store_true');p.set_defaults(run=prepare)
    p=sub.add_parser('cache-window');p.add_argument('--package',required=True);p.add_argument('--bounds',type=float,nargs=4,required=True);p.add_argument('--previous');p.add_argument('--output',required=True);p.set_defaults(run=cache_window)
    p=sub.add_parser('audit');p.add_argument('--package',required=True);p.set_defaults(run=audit)
    p=sub.add_parser('build-index');p.add_argument('--packages',nargs='+',required=True);p.add_argument('--output',required=True);p.set_defaults(run=build_index)
    args=parser.parse_args()
    try:args.run(args)
    except (ValueError,KeyError,TypeError,FileNotFoundError) as exc:
        print('REFUSED: '+str(exc),file=sys.stderr);raise SystemExit(2)
