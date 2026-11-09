import argparse,concurrent.futures,hashlib,json,pathlib,subprocess,urllib.request,urllib.error,time
from PIL import Image
BASE=pathlib.Path(__file__).resolve().parent;catalog=json.loads((BASE/'web-batches.json').read_text());SESSION=catalog['session'];ROOT=BASE.parents[3]
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run(script,name):
 name=catalog.get('runLabel','large')+'-'+name
 command=['bb','browser-automation','run',SESSION,'--script',script,'--timeout','20s','--json'];r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(BASE/(name+'-response.json')).write_bytes(r.stdout);(BASE/(name+'-stderr.log')).write_bytes(r.stderr)
 if r.returncode:raise SystemExit('browser operation failed: '+name)
 data=json.loads(r.stdout);return json.loads(data['text'])
def inspect(index):
 return run("const p=await browser.getPage('main');JSON.stringify(await p.evaluate(()=>({text:document.body.innerText.slice(0,12000),downloads:Array.from(document.querySelectorAll('a')).filter(a=>a.href.includes('/backend/opt/download/')).map(a=>({name:decodeURIComponent(new URL(a.href).pathname.split('/').at(-1)),url:a.href}))})));",f'batch-{index:02}-poll')
ap=argparse.ArgumentParser();ap.add_argument('step',choices=['start','poll','finish','salvage']);ap.add_argument('index',type=int);args=ap.parse_args();rows=catalog['batches'][args.index]
known_rows={r['sourceSHA256'] for r in json.loads((BASE/'web-receipt.json').read_text())['results']};rows=[r for r in rows if r['sha256'] not in known_rows]
if args.step=='start':
 prefix="const p=await browser.getPage('main');"
 if args.index>=0:prefix+="await p.reload({waitUntil:'domcontentloaded',timeout:15000});await new Promise(r=>setTimeout(r,1500));"
 paths=[str((ROOT/r['path']).resolve()) for r in rows]
 assert len(paths)<=20 and all(pathlib.Path(p).is_file() and pathlib.Path(p).stat().st_size<=5_000_000 for p in paths)
 script=prefix+"const input=await p.$('input[type=file]');await input.uploadFile(..."+json.dumps(paths)+");JSON.stringify({submitted:"+str(len(rows))+"});"
 data=run(script,f'batch-{args.index:02}-start');print(json.dumps({'batch':args.index,**data}));raise SystemExit()
data=inspect(args.index);links={r['name']:r['url'] for r in data['downloads']};ready=[r for r in rows if pathlib.Path(r['path']).name in links]
if args.step=='poll':print(json.dumps({'batch':args.index,'ready':len(ready),'expected':len(rows),'hasError':'INVALID' in data['text'] or 'Too many' in data['text'],'summary':data['text'].split('OUR PRODUCTS')[0][-650:]}));raise SystemExit()
if len(ready)!=len(rows) and args.step!='salvage':raise SystemExit('batch not complete; do not reset or bypass a provider limit')
if args.step=='salvage':rows=ready
receipt=json.loads((BASE/'web-receipt.json').read_text());known={r['sourceSHA256'] for r in receipt['results']}
def download(row):
 source=ROOT/row['path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
 url=links[source.name];assert url.startswith('https://tinypng.com/backend/opt/download/')
 target=BASE/('optimized-'+row['sha256']+source.suffix.lower())
 if target.is_file():
  raw=target.read_bytes()
 else:
  for attempt in range(3):
   try:
    with urllib.request.urlopen(url,timeout=45) as response:raw=response.read();assert response.status==200
    break
   except urllib.error.HTTPError:
    raise  # Never retry a provider limit or authentication error through another route.
   except (urllib.error.URLError,TimeoutError):
    if attempt==2:raise
    time.sleep(1+attempt)
  target.write_bytes(raw)
 with Image.open(source) as a,Image.open(target) as z:
  assert a.size==z.size and a.format==z.format
 return {'source':row['path'],'sourceSHA256':row['sha256'],'inputBytes':row['bytes'],'outputBytes':len(raw),'optimizedPath':str(target.relative_to(ROOT)),'outputSHA256':hashlib.sha256(raw).hexdigest(),'downloaded':True,'dimensionsPreserved':True,'formatPreserved':True,'webBatch':args.index,'webRun':catalog.get('runLabel','large'),'downloadURL':url}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(download,[r for r in rows if r['sha256'] not in known]):receipt['results'].append(result);write(BASE/'web-receipt.json',receipt)
all_rows=[r for group in catalog['batches'] for r in group];needed={r['sha256'] for r in all_rows};done={r['sourceSHA256'] for r in receipt['results']}
if needed<=done:receipt['status']='COMPLETE'
write(BASE/'web-receipt.json',receipt);print(json.dumps({'batchFinished':args.index,'completedImages':len(receipt['results']),'inputBytes':sum(r['inputBytes'] for r in receipt['results']),'outputBytes':sum(r['outputBytes'] for r in receipt['results']),'status':receipt['status']}))
