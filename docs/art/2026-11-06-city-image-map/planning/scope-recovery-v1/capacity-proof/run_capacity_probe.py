#!/usr/bin/env python3
"""One bounded high-return-resolution/8-block capacity proof; not city production."""
import base64
import hashlib
import io
import json
import math
import signal
import sys
import time
from contextlib import ExitStack
from pathlib import Path
from urllib.parse import urlparse
import httpx
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').is_file())
PLAN=HERE.parent/'scope-plan.json'
ART=ROOT/'docs/art'
STYLE=ART/'2026-11-04-county-twentyfive-region-plan/review-009/TR-33-v1.png'
A2=ART/'2026-11-06-city-image-map/compact-pair-v2-density/native/A-v2-api.png'
SIZE=(3824,2144)
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
sys.path.insert(0,'/Users/sanger/.hermes/hermes-agent')
from hermes_cli.config import load_config
from hermes_cli.runtime_provider import resolve_runtime_provider

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):(HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def deadline(signum,frame):raise TimeoutError('Whole proof exceeded480-second bounded deadline; no automatic retry.')

def main():
    HERE.mkdir(parents=True,exist_ok=True)
    if (HERE/'request-started.json').exists() or (HERE/'native.png').exists():
        print(json.dumps({'status':'existing-request-or-native-refusing-duplicate'}),flush=True)
        return
    started=time.time();signal.signal(signal.SIGALRM,deadline);signal.alarm(480)
    protected={str(p):digest(p) for p in [PLAN,STYLE,A2]}
    plan=json.loads(PLAN.read_text())
    blocks=[b for b in plan['blocks'] if 2<=b['column']<=5 and 3<=b['row']<=4]
    assert len(blocks)==8
    points=[v for b in blocks for v in b['polygonDesignMetres']]
    xmin=min(p[0] for p in points)-40;xmax=max(p[0] for p in points)+40
    ymin=min(p[1] for p in points);ymax=max(p[1] for p in points)
    scale=SIZE[0]/(xmax-xmin);vertical=scale*math.sin(math.radians(62.5))
    centre=(ymin+ymax)/2;ymin=centre-SIZE[1]/vertical/2;ymax=centre+SIZE[1]/vertical/2
    def screen(p):return ((p[0]-xmin)*scale,(ymax-p[1])*vertical)
    guide=Image.new('RGB',SIZE,'#d6dfc5');draw=ImageDraw.Draw(guide)
    colors={'residential':'#d8cbb8','commercial-office':'#cdb9a6','civic':'#c6cfce','workshop-service':'#c7bfb6','park-community-open':'#9eaf8a'}
    for b in blocks:
        draw.polygon([screen(v) for v in b['polygonDesignMetres']],fill=colors[b['programme']])
    nodes={n['id']:n['designMetres'] for n in plan['nodes']}
    # Ground-plane affine is an input design, not a claim the output obeys it.
    used_edges=[]
    for e in plan['edges']:
        a,b=nodes[e['from']],nodes[e['to']]
        if max(a[0],b[0])<xmin or min(a[0],b[0])>xmax or max(a[1],b[1])<ymin or min(a[1],b[1])>ymax:continue
        pa,pb=screen(a),screen(b);width=max(1,round(e['proposedAsphaltWidthMetres']*scale))
        draw.line([pa,pb],fill='#ddd7c7',width=width+round(4*scale))
        draw.line([pa,pb],fill='#747a7d',width=width)
        used_edges.append({'edgeId':e['id'],'fromPixel':list(pa),'toPixel':list(pb),'tier':e['tier'],'designAsphaltMetres':e['proposedAsphaltWidthMetres']})
    for b in blocks:
        draw.text(screen(b['centre']),b['id']+' '+b['programme'],font=ImageFont.truetype(FONT,24),fill='#273b36',anchor='mm')
    guide.save(HERE/'structure-guide.png')
    with Image.open(A2) as im:im.crop((1080,40,1500,560)).save(HERE/'approved-density-local.png')
    spec={'status':'input-design-only-not-measured-output-or-new-region','requestedReturnSize':list(SIZE),
          'selectedBlockIds':[b['id'] for b in blocks],'completeInputStreetBlocks':len(blocks),
          'designBoundsMetres':[xmin,ymin,xmax,ymax],'blockCentrelineAreaMetres2':sum(b['centrelineEnclosedAreaMetres2'] for b in blocks),
          'groundPixelAffineDesign':{'xPixelsPerMetre':scale,'yPixelsPerMetre':vertical,'elevationAssumptionDegrees':62.5,'notNativeCalibration':True},
          'blocks':blocks,'roadInputs':used_edges,
          'successGates':['actual returned size recorded without resizing','all8 intended full street blocks visibly present','dense urban mixed masses at useful1:1 detail','continuous road/junction topology consistent with guide','no field/garden shrinkage substituted for city','detail and actual geometry still require independent visual review'],
          'notImplied':['whole city produced','current A/B/C physical coverage known','4-6 images enough','vendor internal generation resolution proven by pixel dimensions alone']}
    save('input-spec.json',spec)
    prompt='''CAPACITY PROOF, not a final city. Produce ONE new integrated Japanese contemporary-city game-map illustration. Native requested3824x2144. The first attached image is a ground-plane street-block design guide, not artwork. It deliberately contains EIGHT complete adjacent urban street blocks in a4-column by2-row group, plus narrow surrounding continuations. Maintain all8 complete blocks and their continuous primary/secondary/local road and junction organisation. Do not silently reduce it to2-4 blocks or a small isolated neighborhood. Input block IDs and colour cells are planning annotations only: remove all labels/debug colours from final art.\n\nImage2 is ORIGINAL approved TR-33, style/material/daylight reference only, not its roads/layout. Image3 is only a small crop of approved A2 dense commercial massing/readable detail, not a full neighbor or a composition to copy. No upscaling/cropping old art as output. No white diorama border, sky, debug lines or UI. Design roads, buildings and grounds together in the accepted fixed high-oblique orthographic-like view with consistent ground and verticals. Do not zoom out and make every house tiny to claim8 blocks. Use the genuinely larger requested raster to show the larger planned region while maintaining detailed readable individual facades and human/vehicle/street proportions.\n\nThe8 core street blocks should be recognisably distinct, fully organised dense urban groups: connected2-3storey street shops,4-6storey mixed residential/office backs, a few taller but modest commercial masses, one compact civic/library or exhibition building, small service courts and purposeful community green. Most street frontages continuous, front/back building layers, narrow useful courtyards/accesses, not scattered villas in large lawns and not eight cloned apartment compounds. Do not repeat another giant market hall as the sole landmark. Keep each block's roads clear and connected, entrances reachable and complete, no road under architecture, no overpass/tunnel. Ground corridors and8 block structure follow image1.\n\nNeutral daytime palette, accepted Japanese youthful contemporary-city anime painterly/thick-painted look, varied plaster/brick/wood/glass/roofs, natural soft shadows, deeper natural foliage. Keep accepted warm window treatment as daylight, not universal glowing night lights. No overall recolour, photoreal product-render look, heavy icon outlines or rooftop trees. Small props belong to uses: benches, shopfront signs without legible text, tables/chairs, bins, flowerboxes, service vans parked out of lanes. No catalogue spread, all-vegetable fields or giant empty grass. Preserve meaningful open courts/parks but not a garden-like suburban substitute for city. All edges are coherent painted ground/roads, complete buildings not chopped at edges. Return exactly one entirely new illustration. This is a real output-resolution AND region-capacity proof, not evidence from a requested parameter alone.'''
    (HERE/'prompt.txt').write_text(prompt)
    refs=[(HERE/'structure-guide.png','8-block design geometry input, not art'),(STYLE,'original accepted25 style, not layout'),(HERE/'approved-density-local.png','approved A2 local density/detail only')]
    assert SIZE[0]%16==0 and SIZE[1]%16==0 and max(SIZE)<3840 and SIZE[0]*SIZE[1]<=8294400
    config=load_config();runtime=resolve_runtime_provider(requested='openai-api',explicit_base_url=config['model']['base_url'],target_model=config['model']['default'])
    if runtime.get('provider')!='openai-api' or not runtime.get('api_key'):raise RuntimeError('Approved OpenAI API route unavailable; no fallback attempted')
    req={'status':'request-about-to-be-sent-not-result','startedUnix':time.time(),'operation':'images.edit','model':'gpt-image-2','requestedSize':f'{SIZE[0]}x{SIZE[1]}','qualityRequested':'high','n':1,'maxRetries':0,'totalWallclockLimitSeconds':480,
         'provider':'openai-api','endpointHost':urlparse(runtime['base_url']).hostname,
         'sizeRationale':'bounded experimental high-resolution request based on OpenAI size-constraint search excerpts; compatible endpoint support still unproven',
         'inputs':[{'path':str(p),'sha256':digest(p),'role':role} for p,role in refs],
         'promptSHA256':digest(HERE/'prompt.txt'),'codeSHA256':digest(Path(__file__)),
         'expectedInputBlocks':8,'scope':'single proof only, not D or mass map production'}
    with (HERE/'request-started.json').open('x') as f:json.dump(req,f,ensure_ascii=False,indent=2)
    print(json.dumps({'status':'request_started','requestedSize':req['requestedSize'],'model':'gpt-image-2','expectedInputBlocks':8,'maxRequests':1}),flush=True)
    client=OpenAI(api_key=runtime['api_key'],base_url=runtime['base_url'],timeout=420.,max_retries=0,default_headers={'OpenAI-Project':''},http_client=httpx.Client(trust_env=True,timeout=420.))
    try:
        with ExitStack() as stack:
            images=[stack.enter_context(p.open('rb')) for p,_ in refs]
            res=client.images.edit(model='gpt-image-2',prompt=prompt,image=images,size=req['requestedSize'],quality='high',n=1)
        if not res.data:raise RuntimeError('No returned image; no substitute created')
        result=res.data[0]
        if result.b64_json:raw=base64.b64decode(result.b64_json,validate=True)
        elif result.url and urlparse(result.url).scheme=='https':
            fetched=httpx.get(result.url,timeout=45,follow_redirects=True);fetched.raise_for_status();raw=fetched.content
        else:raise RuntimeError('No supported actual image payload')
        with Image.open(io.BytesIO(raw)) as im:im.load();actual=list(im.size);mode=im.mode
        with (HERE/'native.png').open('xb') as f:f.write(raw)
        usage=getattr(res,'usage',None)
        usage=usage.model_dump() if usage is not None and hasattr(usage,'model_dump') else None
        record={**req,'status':'actual-image-returned-not-detail-or-capacity-accepted','actualSize':actual,'mode':mode,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                'requestedDimensionHeld':actual==list(SIZE),'qualityReturned':getattr(result,'quality',None),'nativeBytesPreserved':True,'noLocalUpscalingOrWarping':True,
                'vendorInternalNoUpscaleClaim':False,'actualPrompt':prompt,'revisedPrompt':getattr(result,'revised_prompt',None),'usage':usage,
                'elapsedSeconds':time.time()-started,'inputSourcesUnchanged':all(digest(Path(p))==h for p,h in protected.items()),
                'eightBlocksActuallyPresent':None,'localDetailAtAcceptedScalePassed':None,'wholeCityOrImageCountFeasibilityPassed':False}
        save('provenance.json',record)
        print(json.dumps({k:record[k] for k in ['status','actualSize','bytes','sha256','requestedDimensionHeld','elapsedSeconds']}),flush=True)
    except Exception as e:
        text=str(e).replace(runtime.get('api_key') or 'UNMATCHABLE','[REDACTED]')
        err={'status':'failed-no-retry-no-fabricated-result','errorType':type(e).__name__,'httpStatus':getattr(e,'status_code',None),'message':text[:1800],'elapsedSeconds':time.time()-started,'requestedSize':req['requestedSize']}
        save('error.json',err);print(json.dumps(err,ensure_ascii=False),flush=True);raise SystemExit(1)
    finally:client.close();signal.alarm(0)

if __name__=='__main__':
    try:main()
    except SystemExit:raise
    except Exception as e:
        save('preparation-error.json',{'status':'preparation-failed-no-fake-output','errorType':type(e).__name__,'message':str(e)[:1000]})
        print(json.dumps({'status':'preparation_failed','errorType':type(e).__name__}),flush=True);raise SystemExit(1)
