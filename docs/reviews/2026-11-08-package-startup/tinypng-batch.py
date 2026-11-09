#!/usr/bin/env python3
"""Use the official Tinify API on authoring-image copies, never logging secrets."""
import argparse,base64,hashlib,json,pathlib,shlex,urllib.request,urllib.error
from PIL import Image
API='https://api.tinify.com/shrink'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--credential-file',type=pathlib.Path,required=True);ap.add_argument('--inventory',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
 key=None
 for line in args.credential_file.read_text().splitlines():
  name,sep,value=line.partition('=')
  if sep and name.strip()=='TINIFY_API_KEY':
   values=shlex.split(value,comments=True);key=values[0] if len(values)==1 else None
 if not key:raise SystemExit('TINIFY_API_KEY is missing; no images submitted')
 authorization='Basic '+base64.b64encode(('api:'+key).encode()).decode();del key
 args.output.mkdir(parents=True,exist_ok=True);receipt=args.output/'receipt.json';jobs=json.loads(receipt.read_text()) if receipt.exists() else {'provider':'TinyPNG official Tinify API','endpoint':API,'results':[],'failed':[],'compressionCount':None}
 inventory=json.loads(args.inventory.read_text())['files'];existing={r['sourceSHA256']:r for r in jobs['results'] if r.get('downloaded')}
 def request(url,data=None,auth=False):
  headers={'Authorization':authorization} if auth else {}
  req=urllib.request.Request(url,data=data,headers=headers)
  try:
   with urllib.request.urlopen(req,timeout=60) as r:return r.status,dict(r.headers),r.read()
  except urllib.error.HTTPError as e:return e.code,dict(e.headers),e.read()
 # Tinify documents this empty shrink request for key validation. It does not compress an image.
 status,headers,body=request(API,b'',True)
 count=headers.get('Compression-Count') or headers.get('compression-count')
 if status not in (400,415) or count is None:raise SystemExit('TinyPNG credential validation failed: HTTP '+str(status)+'; no images submitted')
 jobs['compressionCount']=int(count);write(receipt,jobs)
 for row in inventory:
  source=pathlib.Path(row['path']);sha=row['sha256'];assert digest(source)==sha,'source image drift'
  if sha in existing and pathlib.Path(existing[sha]['optimizedPath']).is_file() and digest(pathlib.Path(existing[sha]['optimizedPath']))==existing[sha]['outputSHA256']:continue
  if jobs['compressionCount']>=500:
   jobs['status']='BLOCKED_FREE_MONTHLY_LIMIT';write(receipt,jobs);raise SystemExit('TinyPNG free monthly500 boundary reached; stopped before another compression')
  status,headers,body=request(API,source.read_bytes(),True)
  if status!=201:
   jobs['failed'].append({'sourceSHA256':sha,'source':str(source),'httpStatus':status});jobs['status']='BLOCKED_API_ERROR';write(receipt,jobs);raise SystemExit('TinyPNG compression failed: HTTP '+str(status))
  count=headers.get('Compression-Count') or headers.get('compression-count');jobs['compressionCount']=int(count) if count else jobs['compressionCount']+1
  response=json.loads(body);url=response['output']['url'];assert url.startswith('https://api.tinify.com/output/')
  # Persist the successful compression before download, so a network issue is visible.
  job={'source':str(source),'sourceSHA256':sha,'inputBytes':row['bytes'],'responseInput':response['input'],'responseOutput':response['output'],'compressionCount':jobs['compressionCount'],'downloaded':False};jobs['results'].append(job);write(receipt,jobs)
  status,_,raw=request(url)
  if status!=200:jobs['status']='BLOCKED_OUTPUT_DOWNLOAD';write(receipt,jobs);raise SystemExit('TinyPNG output download failed: HTTP '+str(status))
  target=args.output/(sha+source.suffix.lower());target.write_bytes(raw)
  with Image.open(source) as a,Image.open(target) as optimized:
   assert a.size==optimized.size,'TinyPNG changed dimensions unexpectedly';assert a.format==optimized.format,'TinyPNG changed format unexpectedly'
  assert len(raw)==response['output']['size']
  job.update({'optimizedPath':str(target),'outputSHA256':digest(target),'outputBytes':len(raw),'downloaded':True,'dimensionsPreserved':True,'formatPreserved':True,'useOptimized':len(raw)<row['bytes']});existing[sha]=job;write(receipt,jobs)
  print(json.dumps({'completed':len(jobs['results']),'source':str(source),'inputBytes':row['bytes'],'outputBytes':len(raw),'compressionCount':jobs['compressionCount']}),flush=True)
 jobs['status']='COMPLETE';write(receipt,jobs)
if __name__=='__main__':main()
