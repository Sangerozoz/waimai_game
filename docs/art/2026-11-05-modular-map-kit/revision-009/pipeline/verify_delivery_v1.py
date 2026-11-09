#!/usr/bin/env python3
"""Package/static reference and one actual Cocos edit demonstration, no game tests."""
import json,hashlib,math,zipfile,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'delivery-kit/v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for path,h in read(D/'metadata/main-protection.json').items():assert sha(Path(path))==h
lib=read(D/'metadata/catalog.json');assert len(lib['assets'])==34
for a in lib['assets']:
 p=D/a['packageFile'];assert p.is_file()and sha(p)==a['sha256']and max(Image.open(p).size)<=280
# Resolve every TMJ inline/external tile set and every template's relative image.
for p in [D/'user-layout.tmj',D/'asset-palette.tmj',D/'demonstration/demo-layout.tmj',D/'templates/asset-library.tsj']:
 d=read(p)
 for ts0 in d.get('tilesets',[d]if'tiles'in d else[]):
  source=p.parent/ts0['source']if'source'in ts0 else p;ts=read(source)if'source'in ts0 else ts0
  for tile in ts['tiles']:assert(source.parent/tile['image']).is_file(),(str(p),tile['image'])
for p in(D/'templates').glob('*.tx'):
 d=read(p);assert(p.parent/d['tileset']['source']).is_file();assert not any(x['name']in['persistentId','sourceIndices','navigationStopNodeId','visualReplacementOf']for x in d['object']['properties'])
userhash=sha(D/'user-layout.tmj');demohash=sha(D/'demonstration/demo-layout.tmj')
subprocess.run(['python3',str(D/'export_user_preview.py'),'--map',str(D/'demonstration/demo-layout.tmj'),'--output',str(D/'preview-demo'),'--focus-id','009compound-source0125-court-module-02-B01,009compound-source0125-court-module-01-B05,user-object-671'],check=True,capture_output=True)
assert sha(D/'user-layout.tmj')==userhash and sha(D/'demonstration/demo-layout.tmj')==demohash
out=read(D/'preview-demo/assets/scene-layout.json');manifest=read(D/'preview-demo/assets/asset-manifest.json');assets={a['id']:a for a in manifest['assets']};base=read(D/'metadata/base-scene.json');actual=read(D/'demonstration/actual-runtime.json');uis={r['persistentId']:r for r in actual['ui']};nodes={r['persistentId']:r for r in actual['order']if r['persistentId']};mapping={r['persistentId']:r for r in read(D/'preview-demo/user-export-report.json')['instancesMapping']}
assert len(out['blocks'])==164 and len(uis)==164
pid='009compound-source0125-court-module-02-B01';old=next(b for b in base['blocks']if b['persistentId']==pid);oldasset=next(a for a in read(D/'preview/assets/asset-manifest.json')['assets']if a['id']==old['assetId']);a=assets['instance-'+pid];assert all(math.isclose(a['worldSizeUnits'][k],oldasset['worldSizeUnits'][k]*1.15,rel_tol=1e-10)for k in(0,1));assert math.dist(old['anchorMap'],mapping[pid]['anchorMap'])>1
for b in out['blocks']:
 a=assets[b['assetId']];u=uis[b['persistentId']];assert u['nodeScaleX']==u['nodeScaleY']==1;assert all(math.isclose(u['worldFrameUnits'][k],a['worldSizeUnits'][k],rel_tol=1e-10)for k in(0,1))
 assert math.isclose(u['uiWidth'],a['worldSizeUnits'][0]*32,rel_tol=1e-10)
 assert mapping[b['persistentId']]['newBusinessOrNavigationBinding']is False
 q=b['anchorMap'];pr=out['projection'];dx,dy=[q[k]-pr['originMap'][k]for k in(0,1)];xy=[32*(dx*pr['axisX'][k]+dy*pr['axisY'][k])for k in(0,1)];node=nodes[b['persistentId']];assert math.dist([node['x'],node['y']],[xy[0],-xy[1]])<1e-4
assert mapping['user-object-671']['libraryAssetId']=='P03';assert 'visualReplacementOf'not in next(b for b in out['blocks']if b['persistentId']=='user-object-671')
for key in ['roads','rider','projection','visualReplacements']:assert out[key]==base[key]
frame={}
for r in actual['frames']:frame.setdefault(r['file'],set()).add(r['frameIndex'])
assert all(len(s)==1 for s in frame.values());assert actual['textures']['uniqueAssetImages']==30
for directory in [D/'preview',D/'preview-demo']:
 m=read(directory/'assets/asset-manifest.json');refs={a['file']for a in m['assets']};assert refs=={p.name for p in(directory/'assets').glob('*.png')}
 for f in refs:assert(directory/'assets'/f).is_file()and max(Image.open(directory/'assets'/f).size)<=280
result={'libraryPNG':34,'libraryPNGBytes':sum(a['bytes']for a in lib['assets']),'categories':lib['categories'],'templateCount':len(list((D/'templates').glob('*.tx'))),'prototypeCounts':[len(base['blocks']),len(base['groundSurfaces'])],'demoCounts':[len(out['blocks']),len(out['groundSurfaces'])],'movedExistingB01':True,'uniformSizeFactor':1.15,'templateNewVisualId':'user-object-671','allActual164NodeWorldSizesMatch':True,'runtimePNG':30,'runtimePNGBytes':sum(f.stat().st_size for f in(D/'preview-demo/assets').glob('*.png')),'actualTextureStats':actual['textures'],'allFrameFilesShared':True,'userLayoutNotChangedByExport':True,'mainAllProtectedSHAUnchanged':True,'TiledGUIUsed':False,'relativeMapTemplateImageReferencesChecked':True,'gameTestsRun':False,'userAccepted':False}
(D/'demonstration/verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
