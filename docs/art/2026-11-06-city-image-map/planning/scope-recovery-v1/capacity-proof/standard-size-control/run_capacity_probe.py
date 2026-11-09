#!/usr/bin/env python3
"""One standard-size control after the custom-size proof missed dimensions."""
import base64,hashlib,io,json,signal,sys,time
from contextlib import ExitStack
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, cast
import httpx
from openai import OpenAI
from PIL import Image
sys.path.insert(0,'/Users/sanger/.hermes/hermes-agent')
from hermes_cli.config import load_config
from hermes_cli.runtime_provider import resolve_runtime_provider
HERE=Path(__file__).resolve().parent
FIRST=HERE.parent

def save(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def expired(sig,frame):raise TimeoutError('Standard-size control480s deadline; no retry')
def main():
 if (HERE/'request-started.json').exists() or (HERE/'native.png').exists():
  print('{"status":"existing-control-refuse-duplicate"}',flush=True);return
 first=json.loads((FIRST/'provenance.json').read_text());assert first['requestedDimensionHeld'] is False
 refs=first['inputs'];assert all(digest(Path(x['path']))==x['sha256'] for x in refs)
 prompt=(FIRST/'prompt.txt').read_text().replace('3824x2144','3840x2160')
 (HERE/'prompt.txt').write_text(prompt)
 cfg=load_config();rt=resolve_runtime_provider(requested='openai-api',explicit_base_url=cfg['model']['base_url'],target_model=cfg['model']['default'])
 assert rt.get('provider')=='openai-api' and rt.get('api_key')
 started=time.time();signal.signal(signal.SIGALRM,expired);signal.alarm(480)
 req={'status':'standard-preset-control-request-started','model':'gpt-image-2','provider':'openai-api','requestedSize':'3840x2160','qualityRequested':'high','n':1,'maxRetries':0,'wallclockLimitSeconds':480,'totalCapabilityExperimentBudget':2,'controlOrdinal':2,'noFurtherImagesRequestsAuthorized':True,'inputs':refs,'inputImagesByteIdenticalToFirstProof':True,'promptSHA256':digest(HERE/'prompt.txt'),'codeSHA256':digest(Path(__file__)),'changedTreatment':'size field and matching prompt dimension only; no model,quality,reference or provider changes','hypothesis':'test whether the compatible service handles the documented standard3840x2160 differently from custom3824x2144; not an assertion either size works','documentationEvidence':'OpenAI images.edit API reference search excerpt explicitly lists maximum3840x2160; complete pages were not fetched successfully','sourceFirstResultSHA256':digest(FIRST/'provenance.json'),'endpointHost':urlparse(rt['base_url']).hostname,'startedUnix':started}
 with (HERE/'request-started.json').open('x') as f:json.dump(req,f,ensure_ascii=False,indent=2)
 print(json.dumps({'status':'standard_size_control_started','requestedSize':'3840x2160','maxRequestsThisControl':1,'totalExperimentBudget':2}),flush=True)
 c=OpenAI(api_key=rt['api_key'],base_url=rt['base_url'],timeout=420,max_retries=0,default_headers={'OpenAI-Project':''},http_client=httpx.Client(trust_env=True,timeout=420))
 try:
  with ExitStack() as stack:
   images=[stack.enter_context(Path(x['path']).open('rb')) for x in refs]
   # Installed SDK literals predate the retrieved API size definition.
   # This is an explicit runtime capability probe, not a support assertion.
   res=c.images.edit(model='gpt-image-2',prompt=prompt,image=images,size=cast(Any,req['requestedSize']),quality='high',n=1)
  if not res.data:raise RuntimeError('No image returned; no substitute')
  result=res.data[0]
  if result.b64_json:raw=base64.b64decode(result.b64_json,validate=True)
  elif result.url and urlparse(result.url).scheme=='https':
   response=httpx.get(result.url,timeout=45,follow_redirects=True);response.raise_for_status();raw=response.content
  else:raise RuntimeError('No supported actual image payload')
  with Image.open(io.BytesIO(raw)) as im:im.load();size=list(im.size);mode=im.mode
  with (HERE/'native.png').open('xb') as f:f.write(raw)
  usage=getattr(res,'usage',None);usage=usage.model_dump() if usage is not None and hasattr(usage,'model_dump') else None
  rec={**req,'status':'standard-size-control-actual-response-not-art-or-production-accepted','actualSize':size,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'requestedDimensionHeld':size==[3840,2160],'mode':mode,'actualPrompt':prompt,'qualityReturned':getattr(result,'quality',None),'usage':usage,'noLocalUpscalingOrWarp':True,'vendorInternalNativeResolutionProven':False,'elapsedSeconds':time.time()-started,'inputImagesStillUnchanged':all(digest(Path(x['path']))==x['sha256'] for x in refs),'wholeCityProductionPassed':False}
  save('provenance.json',rec)
  print(json.dumps({k:rec[k] for k in ['status','actualSize','bytes','sha256','requestedDimensionHeld','elapsedSeconds']}),flush=True)
 except Exception as e:
  safe=str(e).replace(rt.get('api_key') or 'UNMATCHABLE','[REDACTED]');rec={'status':'control-failed-no-retry','errorType':type(e).__name__,'httpStatus':getattr(e,'status_code',None),'message':safe[:1600],'elapsedSeconds':time.time()-started};save('error.json',rec);print(json.dumps(rec),flush=True);raise SystemExit(1)
 finally:c.close();signal.alarm(0)
if __name__=='__main__':main()
