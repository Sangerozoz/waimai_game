"""Assemble five native regions; diagnostic copies never become runtime art."""
import copy, datetime, hashlib, json, math, shutil
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

B = Path(__file__).resolve().parent
O = B/'runtime-package-abcdn'
O.mkdir(exist_ok=False)
atlas = json.loads((B/'runtime-package-abn/region-atlas.json').read_text())
candidate = B/'repairs/C/ownership-candidate'
entries = []
source_files = {}
for old in atlas['regions']:
    e = copy.deepcopy(old)
    if e['id']=='REGION-B':
        e=json.loads((candidate/'REGION-B-entry.json').read_text())
    entries.append(e)
for key in ['C','D']:
    entries.append(json.loads((candidate/f'REGION-{key}-entry.json').read_text()))
sources = {
    'REGION-A': B/'runtime-package-abn/REGION-A-v3.png',
    'REGION-B': B/'images/REGION-B-v4.png',
    'R-+00--01': B/'repairs/north-A/R-+00--01-v2.png',
    'REGION-C': B/'repairs/C/REGION-C-v3.png',
    'REGION-D': B/'repairs/D/REGION-D-v4.png',
}
for e in entries:
    p=sources[e['id']]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']
    e['file']=p.name
    if e['id']=='R-+00--01':e['sortOrder']=-3
    e['registration']['status']='ready'
    e['note']='PM approves native display and measured internal source-road corridors under tile-level user tolerance. Outer junctions and all-county routes are not implied.'
    shutil.copyfile(p,O/p.name)
    source_files[e['id']]=str(p.relative_to(B))
atlas['regions']=entries
roads={r['id']:r for r in atlas['roads']}
for key in ['C','D']:
    s=json.loads((B/f'planning/structures/REGION-{key}-structure.json').read_text())
    for r in s['roads']:
        if r['id'] in roads:assert roads[r['id']]['nodes']==r['nodes']
        else:roads[r['id']]=r
atlas['roads']=list(roads.values())
atlas['camera'].update(focusMap=[-1535,80],viewWidthUnits=450)
atlas['note']='Five unique native regions, PM-approved actual display and observed interior corridors; local street-edge differences accepted. County incomplete; no runtime or stage-test claim.'
for frame in atlas['rider']['frames']:shutil.copyfile(B/'runtime-package-abn'/frame['file'],O/frame['file'])
(O/'region-atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')

# One shared-world material diagnostic, with the exact runtime sorting/masks.
P=4; Q=math.sqrt(.5); S=math.sin(math.radians(62.5)); shift=[730,700]
def world(p):
    x,y=p[0]+1580,p[1]-80
    return [shift[0]+P*Q*(x-y),shift[1]+P*Q*S*(x+y)]
out=Image.new('RGBA',(1800,2000),'#30313aff')
for e in sorted(entries,key=lambda r:(r.get('sortOrder',0),r['id'])):
    art=Image.open(O/e['file']).convert('RGBA')
    if e.get('ownershipPolygonUV'):
        mask=Image.new('L',art.size)
        ImageDraw.Draw(mask).polygon([(p[0]*art.width,p[1]*art.height) for p in e['ownershipPolygonUV']],fill=255)
        art.putalpha(ImageChops.multiply(art.getchannel('A'),mask))
    scale=P/e['nativePixelsPerUnit']
    size=[round(v*scale) for v in art.size]
    art=art.resize(size,Image.Resampling.LANCZOS)
    a=world(e['anchorMap'])
    out.alpha_composite(art,tuple(round(a[k]-e['anchorUV'][k]*size[k]) for k in [0,1]))
ImageDraw.Draw(out).text((20,20),'A/B/C/D/N native material ownership diagnostic - NOT GAME - local seams accepted',fill='white')
out.convert('RGB').save(O/'five-region-material-diagnostic.jpg')
record=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),pm='thr_7w55f3h66f',approvedDisplayAndInternalCoverage=[r['id'] for r in entries],nativeSources=source_files,sourceAtlasSha256=hashlib.sha256((O/'region-atlas.json').read_bytes()).hexdigest(),nativeFiles=[dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in O.glob('*.png')],sourceCitySha256=atlas['source']['sha256'],toleranceEvidence='user-tolerance-20261103.md',sourceArtPixelEdits=False,runtimeViewed=False,gameTestsRun=False,countyComplete=False,remaining=['B-N corner requires the next actual tile','C-D lower-left road-edge double outline retained','D north/service outer endpoints not trusted','all county remains incomplete'])
(O/'package-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(regions=record['approvedDisplayAndInternalCoverage'],roads=len(roads),atlasSHA256=record['sourceAtlasSha256'])))
