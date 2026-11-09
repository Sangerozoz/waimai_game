"""Read-only inventory/HTTP probe; does not launch the game, build, or touch saves."""
import json,re,glob,hashlib,urllib.request,struct,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
RES=ROOT/'delivery-game/assets/resources'; BUILD=ROOT/'delivery-game/build/v2-preview'
OUT=Path(__file__).parent
config_path=next((BUILD/'assets/resources').glob('config*.json'))
config=json.loads(config_path.read_text()); paths={v[0]:config['types'][v[1]] for v in config['paths'].values()}
logs=(OUT/'request-evidence.txt').read_text()
items=[]
def add(group,key,resource,rect=None):
 src=RES/(resource+'.png');meta=RES/(resource+'.png.meta')
 row={'group':group,'key':key,'resource':resource,'source':str(src),'sourceExists':src.exists(),'textureInBuildConfig':paths.get(resource+'/texture')=='cc.Texture2D'}
 if src.exists():
  data=src.read_bytes();w,h=struct.unpack('>II',data[16:24]);row.update(bytes=len(data),size=[w,h],sha256=hashlib.sha256(data).hexdigest())
  if rect:
   x,y,rw,rh=rect;row.update(rect=rect,rectInBounds=x>=0 and y>=0 and rw>0 and rh>0 and x+rw<=w and y+rh<=h)
  u=json.loads(meta.read_text())['uuid'];native=list((BUILD/'assets/resources/native'/u[:2]).glob(u+'.*.png'))
  row['nativeFiles']=[str(p.relative_to(BUILD)) for p in native]
  row['nativeMatchesSource']=bool(native) and all(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'] for p in native)
  row['observedRequestTimes']=re.findall(r'19:\d\d:\d\d','\n'.join(l for l in logs.splitlines() if u in l))
 items.append(row)
for manifest,group in [('manifest','navigation_and_skin'),('portraits','portraits'),('maps','map_cards')]:
 data=json.loads((RES/'ui-v2'/f'{manifest}.json').read_text())
 for key,asset in data['assets'].items():add(group,key,asset['resource'],asset['rect'])
s=(ROOT/'delivery-game/assets/scripts/map-sample/CartoonArt.ts').read_text()
for key,resource in re.findall(r"crops\['([^']+)'\]=\{resource:'([^']+)'",s):
 if key.startswith('side-'):add('vehicles',key,resource,[0,0,*struct.unpack('>II',(RES/(resource+'.png')).read_bytes()[16:24])])
 if 'food-batch' in resource:
  crop=re.search(r"crops\['"+re.escape(key)+r"'\]=\{resource:'[^']+',rect:\[([^]]+)\]",s).group(1)
  def number(v):
   a,*b=v.split('/');return float(a)/(float(b[0]) if b else 1)
  w,h=struct.unpack('>II',(RES/(resource+'.png')).read_bytes()[16:24]);norm=list(map(number,crop.split(',')))
  add('food',key,resource,[round(norm[0]*w),round(norm[1]*h),round(norm[2]*w),round(norm[3]*h)])
add('portraits','legacy-avatar','map-sample/anime/au01/rider-master-original',[340,0,360,360])
# HTTP GET one existing native per category; content hash records bytes actually read.
probes=[]
for group in ['navigation_and_skin','portraits','map_cards','vehicles','food']:
 row=next((r for r in items if r['group']==group and r.get('nativeFiles')),None)
 if not row:continue
 path=row['nativeFiles'][0];probe={'group':group,'path':path}
 try:
  with urllib.request.urlopen('http://127.0.0.1:4182/'+path,timeout=15) as response:
   data=response.read();probe.update(status=response.status,contentType=response.headers.get('Content-Type'),bytes=len(data),matchesSource=hashlib.sha256(data).hexdigest()==row['sha256'])
 except Exception as e:probe['error']=str(e)
 probes.append(probe)
manifest_probes=[]
for name in ['manifest','portraits','maps']:
 resource='ui-v2/'+name;u=json.loads((RES/(resource+'.json.meta')).read_text())['uuid']
 files=list((BUILD/'assets/resources/import'/u[:2]).glob(u+'.*.json'))
 row={'resource':resource,'jsonInBuildConfig':paths.get(resource)=='cc.JsonAsset','buildFiles':[str(p.relative_to(BUILD)) for p in files]}
 if files:
  try:
   with urllib.request.urlopen('http://127.0.0.1:4182/'+str(files[0].relative_to(BUILD)),timeout=15) as response:
    data=response.read();json.loads(data);row.update(status=response.status,bytes=len(data),matchesBuild=data==files[0].read_bytes())
  except Exception as e:row['error']=str(e)
 manifest_probes.append(row)
# Map observed requests to source identities, without copying broad terminal logs.
known={json.loads(p.read_text())['uuid']:str(p.relative_to(RES))[:-5] for p in RES.rglob('*.png.meta')}
requests=[]
for line in logs.splitlines():
 match=re.search(r'\[(.*?)\] "GET (\S+).*?" (\d+)',line)
 if match:
  stamp,path,status=match.groups();u=re.search(r'/([a-f0-9-]{36})\.',path)
  requests.append({'time':stamp,'path':path,'status':int(status),'source':known.get(u.group(1)) if u else None})
summary={}
for group in sorted(set(r['group'] for r in items)):
 rows=[r for r in items if r['group']==group];unique={r['resource']:r for r in rows}
 summary[group]={'keys':len(rows),'uniqueTextures':len(unique),'uniqueSourceBytes':sum(r.get('bytes',0) for r in unique.values()),'missing':[r['key'] for r in rows if not r['sourceExists'] or not r['textureInBuildConfig'] or not r.get('nativeMatchesSource')],'invalidRectangles':[r['key'] for r in rows if r.get('rectInBounds') is False]}
result={'sourceFixes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'delivery-game/assets/scripts/map-sample'/n for n in ['UIArtResources.ts','UIArtResources.ts.meta','V2ImageSkin.ts','CartoonArt.ts']]},'date':'2026-11-05','scope':'read-only inventory and localhost resource HTTP; no browser/game execution','buildConfig':str(config_path),'summary':summary,'httpProbes':probes,'manifestHttpProbes':manifest_probes,'assets':items,'observedRequests':requests,'limitations':['No authenticated remote browser trace; server 200 does not prove transfer/decode/render completion.','Source fix not built/deployed by this agent.','No tests/typecheck/regression or gameplay actions authorized.']}
(OUT/'asset-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'summary':summary,'httpProbes':probes,'manifestHttpProbes':manifest_probes},ensure_ascii=False,indent=2))
