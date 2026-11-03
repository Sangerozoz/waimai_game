"""Assemble real finished art only; preserve five trusted regions and preview others."""
import argparse, copy, datetime, hashlib, json, shutil
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('output');p.add_argument('--ids',nargs='+',required=True)
args=p.parse_args()
B=Path(__file__).resolve().parent;O=B/args.output
O.mkdir(exist_ok=False)
atlas=json.loads((B/'runtime-package-abcdn/region-atlas.json').read_text())
ids={r['id'] for r in atlas['regions']};roads={r['id']:r for r in atlas['roads']}
for file in (B/'runtime-package-abcdn').glob('*.png'):shutil.copyfile(file,O/file.name)
rows=[]
for index,id in enumerate(args.ids):
    if id in ids:continue
    folder=B/'production'/id
    entry=folder/'placement-preview.json'
    if not entry.exists():entry=folder/'registration/region-entry.json'
    if id=='R--01-+00':entry=B/'repairs/R--01-+00/registration/region-entry.json'
    r=json.loads(entry.read_text());raw=Path(r['file'])
    candidates=[raw,folder/'art'/raw.name]
    if id=='R--01-+00':candidates=[B/'repairs/R--01-+00/art/R--01-+00-v3.png']
    source=next((p for p in candidates if p.exists()),None)
    if source is None:raise ValueError('Missing native art '+id)
    if hashlib.sha256(source.read_bytes()).hexdigest()!=r['sha256']:raise ValueError('SHA mismatch '+id)
    r['file']=source.name;r['sortOrder']=-100-index;r['registration']['status']='preview-only'
    r['note']='Assembly-first display only. Existing measured observations, if present, retained. No rider/route authorization; obvious seam/coverage defects deferred to the full-map repair pass.'
    shutil.copyfile(source,O/source.name);atlas['regions'].append(r);ids.add(id)
    rows.append(dict(id=id,sourceEntry=str(entry.relative_to(B)),sourceImage=str(source),sha256=r['sha256'],status='preview-only'))
    s=json.loads((folder/'input/structures'/f'{id}-structure.json').read_text())
    for road in s['roads']:
        if road['id'] in roads:
            if roads[road['id']]['nodes']!=road['nodes']:raise ValueError('Original road nodes differ '+road['id'])
        else:roads[road['id']]=road
atlas['roads']=list(roads.values());atlas['camera'].update(focusMap=[-1550,70],viewWidthUnits=750)
atlas['note']='Assembly-first real native county progress: five trusted internal corridors retained, added regions preview-only. County incomplete; final local repair pass pending.'
(O/'region-atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
record=dict(pm='thr_7w55f3h66f',createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),basePackage='runtime-package-abcdn',newDisplayOnlyRegions=rows,regionCount=len(ids),readyInternalRegionCount=5,sourceAtlasSha256=hashlib.sha256((O/'region-atlas.json').read_bytes()).hexdigest(),sourceCitySha256=atlas['source']['sha256'],nativeFiles=[dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(O.glob('*.png'))],decision='assembly-first-decision-20261103.md',countyComplete=False,runtimeViewed=False,testsRun=False)
(O/'package-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(regions=len(ids),roads=len(roads),sha256=record['sourceAtlasSha256'])))
