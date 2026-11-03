"""Prepare native PM data for the isolated viewer; no source art is modified."""
from pathlib import Path
import json, hashlib, shutil, sys
source=Path(sys.argv[1]).resolve()
project=Path(__file__).resolve().parents[1]
manifest=json.loads((source/'asset-manifest.json').read_text())
layout=json.loads((source/'scene-layout.json').read_text())
if manifest.get('packageComplete') is not True:raise ValueError('PM native package is incomplete')
assets=manifest['assets']
# Reuse byte-identical native paving/asphalt from the original frozen asset package.
legacy=project.parents[1]/'docs/art/2026-11-03-modular-city-assets'
legacy_manifest=json.loads((legacy/'asset-manifest.json').read_text())
material_sources={}
for old in legacy_manifest['assets']:
 if old['id'] not in ('S01-paving','S02-asphalt'):continue
 material=dict(old)
 material['sha256']=old['source']['sha256']
 material['kind']='material'
 material_sources[material['id']]=legacy/old['file']
 assets[:]=[a for a in assets if a['id']!=material['id']]
 assets.append(material)
parcels=layout['parcels']
origin=layout['projection']['originMap']
layout['origin']={'x':origin[0],'y':origin[1]}
layout.setdefault('camera',{'focusMap':origin,'viewWidthUnits':52,'screenOffset':[0,0]})
lookup={a['id']:a for a in assets}
layout['blocks']=[]
for p in parcels:
 a=lookup[p['assetId']]
 a['kind']='block'
 a.setdefault('anchorMap',p['anchorMap'])
 if not a.get('sortMap'):raise ValueError('PM must provide front ground sortMap '+a['id'])
 layout['blocks'].append({'assetId':a['id'],'anchorMap':a['anchorMap'],'sortMap':a['sortMap']})
frames={a.get('direction','').lower():a for a in assets if a.get('kind')=='rider' or a.get('wheelContactAnchorUV')}
for a in frames.values():a['kind']='rider'
layout['rider']['forwardAssetId']=frames['ne']['id']
layout['rider']['reverseAssetId']=frames['sw']['id']
layout['rider'].setdefault('map',[-1589.05,64.5])
output=project/'runtime-data';output.mkdir(exist_ok=True)
for a in assets:
 rel=Path(a['file'])
 if rel.is_absolute() or '..' in rel.parts:raise ValueError('Non-local asset path')
 src=material_sources.get(a['id'],source/rel)
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 if digest!=a['sha256']:raise ValueError('Source SHA mismatch '+a['id'])
 dst=output/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for name,data in [('asset-manifest.json',manifest),('scene-layout.json',layout)]:
 (output/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
record={'source':str(source),'status':'native package prepared, no runtime visual check','files':{str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file() and p.name!='integration-record.json'}}
(output/'integration-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output':str(output),'blocks':len(layout['blocks']),'directionIds':list(frames),'manifestSHA256':record['files']['asset-manifest.json'],'layoutSHA256':record['files']['scene-layout.json']},ensure_ascii=False))
