#!/usr/bin/env python3
"""Exactly one D native request on the established authorized Images route."""
import base64
from contextlib import ExitStack
import hashlib
import io
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
import httpx
from openai import OpenAI
from PIL import Image
sys.path.insert(0, '/Users/sanger/.hermes/hermes-agent')
from hermes_cli.config import load_config
from hermes_cli.runtime_provider import resolve_runtime_provider

HERE=Path(__file__).resolve().parent
CITY=HERE.parent.parent
ART=CITY.parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,data):
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def main():
    if (HERE/'request-started.json').exists() or (HERE/'native.png').exists():
        raise SystemExit('D request/native exists; no repeated generation.')
    refs=[(HERE/'references/D-structure.png','D structure with actual north/west strips, not final art'),
          (ART/'2026-11-04-county-twentyfive-region-plan/review-009/TR-33-v1.png','original25 painting/style only, not road layout'),
          (HERE/'references/actual-north-64.png','real northern64px only, no placeholder'),
          (HERE/'references/actual-west-64.png','real western64px only, no placeholder')]
    prompt=(HERE/'prompt.txt').read_text()
    config=load_config()
    runtime=resolve_runtime_provider(requested='openai-api',explicit_base_url=config['model']['base_url'],target_model=config['model']['default'])
    if runtime.get('provider')!='openai-api' or not runtime.get('api_key'):
        raise SystemExit('Authorized API unavailable; no alternate channel.')
    request={'region':'D-001','operation':'images.edit','model':'gpt-image-2','sizeRequested':'1536x1024',
             'qualityRequested':'high','n':1,'maxRetries':0,'agentProvider':'acp-hermes-agent','agentModel':'openai-api:gpt-6.1-sol',
             'inputs':[{'path':str(p),'sha256':sha(p),'role':role} for p,role in refs],
             'promptPath':str(HERE/'prompt.txt'),'promptSHA256':sha(HERE/'prompt.txt'),'codeSHA256':sha(Path(__file__)),
             'executionCommands':'execution-commands.json','fullNeighborAttached':False,'AOrBOrCRegenerated':False}
    started=time.time()
    with (HERE/'request-started.json').open('x') as f:
        json.dump({**request,'startedUnix':started},f,ensure_ascii=False,indent=2)
    client=OpenAI(api_key=runtime['api_key'],base_url=runtime['base_url'],timeout=240.,max_retries=0,
                  default_headers={'OpenAI-Project':''},http_client=httpx.Client(trust_env=True,timeout=240.))
    try:
        with ExitStack() as stack:
            images=[stack.enter_context(p.open('rb')) for p,_ in refs]
            response=client.images.edit(model='gpt-image-2',image=images,prompt=prompt,size='1536x1024',quality='high',n=1)
        if not response.data:
            raise RuntimeError('No native returned; no substitute.')
        first=response.data[0]
        if first.b64_json:
            data=base64.b64decode(first.b64_json,validate=True)
        elif first.url and urlparse(first.url).scheme=='https':
            fetched=httpx.get(first.url,timeout=60,follow_redirects=True);fetched.raise_for_status();data=fetched.content
        else:
            raise RuntimeError('No supported image payload.')
        with Image.open(io.BytesIO(data)) as image:
            image.load();size,mode=list(image.size),image.mode
        with (HERE/'native.png').open('xb') as f:
            f.write(data)
        usage=getattr(response,'usage',None)
        save(HERE/'provenance.json',{**request,'status':'real-D-native-received-not-yet-integrated-or-user-accepted',
             'imageProvider':'openai-api','endpointHost':urlparse(runtime['base_url']).hostname,
             'actualSize':size,'mode':mode,'qualityReturned':getattr(first,'quality',None),
             'nativeSHA256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'nativeBytesPreserved':True,
             'elapsedSeconds':time.time()-started,'actualPrompt':prompt,'revisedPrompt':getattr(first,'revised_prompt',None),
             'usage':usage.model_dump() if usage is not None and hasattr(usage,'model_dump') else None})
        print(json.dumps({'status':'received','native':str(HERE/'native.png'),'actualSize':size,'bytes':len(data),
                          'nativeSHA256':hashlib.sha256(data).hexdigest()},ensure_ascii=False),flush=True)
    except Exception as exc:
        safe=str(exc).replace(runtime['api_key'],'[REDACTED]')
        save(HERE/'generation-error.json',{'status':'failed-no-retry-no-substitute','errorType':type(exc).__name__,
             'httpStatus':getattr(exc,'status_code',None),'message':safe[:1800],'elapsedSeconds':time.time()-started})
        print(json.dumps({'status':'failed','errorType':type(exc).__name__,'message':safe[:1000]}),flush=True)
        raise SystemExit(1)
    finally:
        client.close()


if __name__=='__main__':
    main()
