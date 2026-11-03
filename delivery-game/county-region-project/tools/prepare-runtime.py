"""Copy a PM atlas and native bytes into the isolated runtime package."""
from pathlib import Path
import argparse,hashlib,json,shutil
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source')
parser.add_argument('--static-rider-map',nargs=2,type=float,metavar=('X','Y'))
parser.add_argument('--static-rider-direction',default='ne')
args=parser.parse_args()
source=Path(args.source).resolve()
project=Path(__file__).resolve().parents[1]
atlas=json.loads((source/'region-atlas.json').read_text())
if atlas.get('schemaVersion')!=1:raise ValueError('Unsupported atlas')
overrides={}
if args.static_rider_map:
 if not atlas.get('rider',{}).get('frames'):raise ValueError('Static rider needs native frames')
 atlas['rider']['initialMap']=args.static_rider_map
 atlas['rider']['initialDirection']=args.static_rider_direction
 overrides={'staticRider':{'map':args.static_rider_map,'direction':args.static_rider_direction,'status':'requested; runtime blue/coverage/source-road gates still apply'}}
output=project/'runtime-data';output.mkdir(exist_ok=True)
specs=atlas['regions']+atlas.get('rider',{}).get('frames',[])
records={}
for spec in specs:
 rel=Path(spec['file'])
 if rel.is_absolute() or '..' in rel.parts:raise ValueError('Local relative paths required')
 src=(source/rel).resolve()
 if not src.is_relative_to(source):raise ValueError('Source escapes package')
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 if digest!=spec['sha256']:raise ValueError('SHA mismatch '+str(src))
 dst=output/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if src!=dst:shutil.copy2(src,dst)
 records[str(rel)]=digest
# Publish manifest only after all native files are available.
(output/'region-atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
records['region-atlas.json']=hashlib.sha256((output/'region-atlas.json').read_bytes()).hexdigest()
(output/'integration-record.json').write_text(json.dumps({'source':str(source),'sourceAtlasSHA256':hashlib.sha256((source/'region-atlas.json').read_bytes()).hexdigest(),'runtimeOverrides':overrides,'status':'native bytes prepared; no runtime check','files':records},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'regions':len(atlas['regions']),'registration':[{'id':r['id'],'status':r['registration']['status']} for r in atlas['regions']],'files':records},ensure_ascii=False))
