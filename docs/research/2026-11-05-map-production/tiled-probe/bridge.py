#!/usr/bin/env python3
"""Throwaway Tiled JSON ↔ existing HighCameraCity data adapter. Stdlib only."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import uuid
import zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BUILT = ROOT / 'delivery-game/build/map-sample/high-camera-city/assets'
MODULAR = ROOT / 'docs/art/2026-11-03-modular-city-assets'
MAP = HERE / 'probe.tmj'


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def props(obj):
    return {p['name']: p['value'] for p in obj.get('properties', [])}


def property_list(values):
    return [{'name': k, 'type': 'bool' if isinstance(v, bool) else 'float' if isinstance(v, (int,float)) else 'string', 'value': v} for k,v in values.items()]


def project(point, meta):
    p = meta['projection']; dx = point[0]-p['originMap'][0]; dy = point[1]-p['originMap'][1]
    return [meta['editorOrigin'][i] + meta['pixelsPerUnit']*(dx*p['axisX'][i]+dy*p['axisY'][i]) for i in (0,1)]


def unproject(point, meta):
    p=meta['projection']; x,y=[(point[i]-meta['editorOrigin'][i])/meta['pixelsPerUnit'] for i in (0,1)]
    a,b=p['axisX']; c,d=p['axisY']; determinant=a*d-b*c
    return [p['originMap'][0]+(d*x-c*y)/determinant,p['originMap'][1]+(-b*x+a*y)/determinant]


def make_object(object_id, persistent_id, asset, point, scale, meta, gid):
    w,h=[n/asset['nativePixelsPerUnit']*meta['pixelsPerUnit']*scale for n in asset['nativeSize']]
    u,v=asset['anchorUV']; x,y=project(point,meta)
    return {'id':object_id,'name':persistent_id,'type':'sprite','gid':gid,'x':x-u*w,'y':y+(1-v)*h,'width':w,'height':h,'rotation':0,'visible':True,
            'properties':property_list({'persistentId':persistent_id,'assetId':asset['id'],'orientationVariant':'native','scale':scale,'manualLocked':False})}


def object_pose(obj, asset, meta, layer=None):
    if obj.get('rotation',0) or obj['gid'] & 0xf0000000:
        raise ValueError('Plane rotation/mirroring is unsupported: '+obj['name'])
    sx=obj['width']/(asset['nativeSize'][0]/asset['nativePixelsPerUnit']*meta['pixelsPerUnit'])
    sy=obj['height']/(asset['nativeSize'][1]/asset['nativePixelsPerUnit']*meta['pixelsPerUnit'])
    if sx<=0 or not math.isclose(sx,sy,rel_tol=1e-5,abs_tol=1e-6):
        raise ValueError('Use positive uniform scaling: '+obj['name'])
    u,v=asset['anchorUV'];layer=layer or {}
    return unproject([obj['x']+layer.get('offsetx',0)+u*obj['width'],obj['y']+layer.get('offsety',0)-(1-v)*obj['height']],meta),sx


def object_layer(doc):
    return next(l for l in doc['layers'] if l['name']=='Editable objects' and l['type']=='objectgroup')


def append_object(doc, asset, point, meta, persistent_id, gid):
    layer=object_layer(doc)
    if any(props(o).get('persistentId')==persistent_id for o in layer['objects']):
        raise ValueError('Persistent ID already exists')
    obj=make_object(doc['nextobjectid'],persistent_id,asset,point,1,meta,gid)
    obj['x']-=layer.get('offsetx',0);obj['y']-=layer.get('offsety',0)
    layer['objects'].append(obj); doc['nextobjectid']+=1
    return obj


def background(layout, meta, target):
    """Rasterize original world-space road corridors then project; no asset edits."""
    w=h=1792; rows=[bytearray(bytes.fromhex('dedbd0')*w) for _ in range(h)]
    def polygon(points, colour):
        xy=[project(p,meta) for p in points]
        for y in range(max(0,math.floor(min(p[1] for p in xy))),min(h,math.ceil(max(p[1] for p in xy)))):
            hits=[]
            for a,b in zip(xy,xy[1:]+xy[:1]):
                if (a[1]<=y+.5<b[1]) or (b[1]<=y+.5<a[1]):
                    hits.append(a[0]+(y+.5-a[1])/(b[1]-a[1])*(b[0]-a[0]))
            hits.sort()
            for x0,x1 in zip(hits[::2],hits[1::2]):
                start=max(0,math.ceil(x0)); stop=min(w,math.ceil(x1))
                if stop>start: rows[y][start*3:stop*3]=colour*(stop-start)
    # Entire rectangular image is a locked reference. Roads are clipped by canvas;
    # runtime retains the exact source nodes/widths and draws its own materials.
    for extra,colour in [(3.6,bytes.fromhex('c9c3b3')),(0,bytes.fromhex('75797a'))]:
        for road in layout['roads']:
            radius=(road['width']+extra)/2
            for a,b in zip(road['nodes'],road['nodes'][1:]):
                dx=b[0]-a[0];dy=b[1]-a[1]; length=math.hypot(dx,dy)
                if not length: continue
                nx=-dy/length*radius;ny=dx/length*radius
                polygon([[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]],colour)
            for x,y in road['nodes']:
                polygon([[x+radius*math.cos(i*math.pi/16),y+radius*math.sin(i*math.pi/16)] for i in range(32)],colour)
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    target.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\x00'+r for r in rows)))+chunk(b'IEND',b''))


def prepare():
    if MAP.exists():
        raise ValueError('Refusing to overwrite current authoritative probe.tmj')
    layout=read(BUILT/'scene-layout.json'); manifest=read(BUILT/'asset-manifest.json')
    assets=manifest['assets']; provenance=[]; (HERE/'assets').mkdir(exist_ok=True)
    for a in assets:
        source=BUILT/a['file']; shutil.copyfile(source,HERE/'assets'/a['file'])
        provenance.append({'assetId':a['id'],'source':str(source.relative_to(ROOT)),'file':a['file'],'sha256':sha(source)})
    for a in read(MODULAR/'asset-manifest.json')['assets']:
        if a['id'] not in ('T02','P01'): continue
        a=copy.deepcopy(a); a['anchorUV']=a.pop('anchor'); a['nativePixelsPerUnit']=a['nativeSize'][0]/a['displayWidthMeters']; a['kind']='block'
        a['projectionCaveat']='Older modular-city painted camera, reused unchanged as workflow prop; not62.5-camera artwork validation'
        source=MODULAR/a['file']; a['sha256']=sha(source); shutil.copyfile(source,HERE/'assets'/a['file']);assets.append(a)
        provenance.append({'assetId':a['id'],'source':str(source.relative_to(ROOT)),'file':a['file'],'sha256':sha(source)})
    meta={'projection':layout['projection'],'editorOrigin':[896,896],'pixelsPerUnit':16}
    write(HERE/'bridge-meta.json',meta); write(HERE/'base-scene-layout.json',layout); write(HERE/'assets/asset-manifest.json',manifest);write(HERE/'source-integrity.json',provenance)
    editable=[a for a in assets if a['kind']=='block']; tiles=[]
    for i,a in enumerate(editable):
        tiles.append({'id':i,'image':'assets/'+a['file'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':property_list({'assetId':a['id']})})
    tileset={'firstgid':1,'name':'Existing native assets','tilewidth':1254,'tileheight':1536,'tilecount':len(tiles),'columns':0,'objectalignment':'bottomleft','tiles':tiles}
    objects=[]
    for i,a in enumerate(editable):
        point=a.get('anchorMap') or ([-1608,91] if a['id']=='T02' else [-1599,91])
        objects.append(make_object(i+1,'initial-'+a['id'],a,point,1,meta,i+1))
    doc={'type':'map','version':'1.10','tiledversion':'1.11.2','orientation':'orthogonal','renderorder':'right-down','infinite':False,'width':56,'height':56,'tilewidth':32,'tileheight':32,'nextlayerid':3,'nextobjectid':len(objects)+1,'backgroundcolor':'#dedbd0','properties':property_list({'projectionId':meta['projection']['id'],'pixelsPerUnit':16,'note':'Screen-space layout; do not rotate or mirror native sprites'}),'tilesets':[tileset],
         'layers':[{'id':1,'name':'Original roads — locked reference','type':'imagelayer','image':'original-roads.png','offsetx':0,'offsety':0,'opacity':1,'visible':True,'locked':True,'properties':property_list({'manualLocked':True,'sourceRoadsSHA256':hashlib.sha256(json.dumps(layout['roads'],sort_keys=True).encode()).hexdigest()})},
                   {'id':2,'name':'Editable objects','type':'objectgroup','draworder':'topdown','opacity':1,'visible':True,'objects':objects}]}
    background(layout,meta,HERE/'original-roads.png');write(MAP,doc);write(HERE/'initial-map-snapshot.json',doc)
    import_map(MAP,HERE/'runtime')
    print('Prepared',MAP)


def import_map(path, output):
    path=Path(path).resolve(); output=Path(output).resolve()
    if not output.is_relative_to(HERE): raise ValueError('Output must stay inside probe directory')
    original_bytes=path.read_bytes();original_sha=hashlib.sha256(original_bytes).hexdigest()
    snapshot=output/'source-maps'/(original_sha+'.tmj');snapshot.parent.mkdir(parents=True,exist_ok=True)
    if not snapshot.exists():snapshot.write_bytes(original_bytes)
    doc=json.loads(original_bytes);meta=read(HERE/'bridge-meta.json');manifest=read(HERE/'assets/asset-manifest.json');layout=read(HERE/'base-scene-layout.json')
    # Read the edited map only: deleted objects never come back from initial layout.
    # The editor reference covers its whole finite screen canvas. Expand the
    # existing viewer's world-space ground clip to contain all four corners;
    # source roads and camera remain untouched.
    previous_bounds=copy.deepcopy(layout['bounds'])
    canvas_width=doc['width']*doc['tilewidth'];canvas_height=doc['height']*doc['tileheight']
    if doc.get('infinite') or canvas_width<=0 or canvas_height<=0:
        raise ValueError('Expected a positive finite editor canvas')
    canvas_corners=[unproject(point,meta) for point in ([0,0],[canvas_width,0],[canvas_width,canvas_height],[0,canvas_height])]
    layout['bounds']={'minX':min(p[0] for p in canvas_corners),'maxX':max(p[0] for p in canvas_corners),'minY':min(p[1] for p in canvas_corners),'maxY':max(p[1] for p in canvas_corners)}
    by_id={a['id']:a for a in manifest['assets']}; blocks=[]; report=[];seen=set()
    ts=doc['tilesets'][0]
    if 'source' in ts: raise ValueError('Keep embedded image collection tileset')
    tiles={ts['firstgid']+t['id']:props(t)['assetId'] for t in ts['tiles']}
    layer=object_layer(doc)
    for obj in layer['objects']:
        p=props(obj);asset_id=tiles.get(obj['gid'])
        if not asset_id: raise ValueError('Unknown tile / flipped tile')
        if p.get('assetId',asset_id)!=asset_id: raise ValueError('Object assetId must match tile')
        pid=p.get('persistentId')
        # GUI duplicate copies custom IDs. Normalize ONLY that duplicate and persist it.
        if not pid or pid in seen:
            pid='tiled-'+str(obj['id'])+'-'+uuid.uuid4().hex[:8]
        if p.get('orientationVariant','native')!='native': raise ValueError('Only native orientation is supported')
        seen.add(pid);a=by_id[asset_id];point,scale=object_pose(obj,a,meta,layer)
        p.update({'persistentId':pid,'assetId':asset_id,'scale':scale,'orientationVariant':p.get('orientationVariant','native'),'manualLocked':p.get('manualLocked',False)});obj['properties']=property_list(p)
        clone=copy.deepcopy(a);clone['id']='instance-'+pid;clone['nativePixelsPerUnit']=a['nativePixelsPerUnit']/scale;clone['anchorMap']=point;clone['sortMap']=point;manifest['assets'].append(clone)
        blocks.append({'assetId':clone['id'],'anchorMap':point,'sortMap':point,'persistentId':pid,'sourceAssetId':asset_id,'scale':scale,'manualLocked':p['manualLocked'],'orientationVariant':p['orientationVariant']})
        screen=project(point,meta);u,v=a['anchorUV'];back=[obj['x']+layer.get('offsetx',0)+u*obj['width'],obj['y']+layer.get('offsety',0)-(1-v)*obj['height']]
        error=math.dist(screen,back)
        report.append({'persistentId':pid,'tiledObjectId':obj['id'],'assetId':asset_id,'map':point,'scale':scale,'anchorRoundtripEditorPx':error,'manualLocked':p['manualLocked']})
    if not blocks:raise ValueError('Existing viewer requires at least one block object')
    # Always save normalized scale metadata; no object coordinates or deletions changed.
    write(path,doc)
    layout['blocks']=blocks;layout['parcels']=[];layout['status']='isolated-tiled-probe-not-art-acceptance';layout['tiledSourceSHA256']=sha(path)
    target=output/'assets';target.mkdir(parents=True,exist_ok=True)
    for a in manifest['assets']:
        source=HERE/'assets'/a['file']
        if sha(source)!=a['sha256']:raise ValueError('Copied asset SHA mismatch '+a['id'])
        shutil.copyfile(source,target/a['file'])
    write(target/'scene-layout.json',layout);write(target/'asset-manifest.json',manifest)
    write(output/'import-report.json',{'map':str(path.relative_to(HERE)),'previousBounds':previous_bounds,'runtimeBounds':layout['bounds'],'editorCanvasSizePx':[canvas_width,canvas_height],'editorCanvasWorldCorners':canvas_corners,'boundsPolicy':'World-axis-aligned enclosure of inverse-projected finite editor canvas; original road nodes and widths unchanged','sourceMapSnapshot':str(snapshot.relative_to(output)),'sourceMapSHA256':original_sha,'tiledLayerOffsetPx':[layer.get('offsetx',0),layer.get('offsety',0)],'tiledDrawOrder':layer.get('draworder','topdown'),'manualDrawOrderPreserved':False,'runtimeDrawOrder':'Existing viewer sorts by projected anchor depth; Tiled index ordering is not reproduced','mapSHA256':sha(path),'objects':report,'deletedInitialPersistentIds':sorted({props(o)['persistentId'] for o in object_layer(read(HERE/'initial-map-snapshot.json'))['objects']}-seen),'roadsUnchanged':layout['roads']==read(BUILT/'scene-layout.json')['roads'],'maxAnchorRoundtripEditorPx':max(r['anchorRoundtripEditorPx'] for r in report),'runtimeViewer':'Existing HighCameraCity build; assets package only; no GUI/render verification implied'})
    print('Imported',len(blocks),'objects into',target)


def check(path, output):
    import_map(path,output)
    report=read(Path(output)/'import-report.json')
    if not report['roadsUnchanged'] or report['maxAnchorRoundtripEditorPx']>=.5:raise ValueError('Coordinate/road invariant failed')
    print(json.dumps(report,ensure_ascii=False,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('prepare')
    for cmd in ('import','check'):
        p=sub.add_parser(cmd);p.add_argument('--map',type=Path,default=MAP);p.add_argument('--output',type=Path,default=HERE/'runtime')
    p=sub.add_parser('append');p.add_argument('--map',type=Path,default=MAP);p.add_argument('--asset',default='P01');p.add_argument('--x',type=float,required=True);p.add_argument('--y',type=float,required=True);p.add_argument('--id',required=True)
    args=parser.parse_args()
    if args.command=='prepare':prepare()
    elif args.command in ('import','check'):
        (check if args.command=='check' else import_map)(args.map,args.output)
    else:
        doc=read(args.map);meta=read(HERE/'bridge-meta.json');asset=next(a for a in read(HERE/'assets/asset-manifest.json')['assets'] if a['id']==args.asset);ts=doc['tilesets'][0];gid=ts['firstgid']+next(t['id'] for t in ts['tiles'] if props(t)['assetId']==args.asset)
        append_object(doc,asset,[args.x,args.y],meta,args.id,gid);write(args.map,doc);print('Appended',args.id,'without resetting existing objects')

if __name__=='__main__':main()
