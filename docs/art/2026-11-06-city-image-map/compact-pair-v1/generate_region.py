#!/usr/bin/env python3
"""One native request per region, sequential and never overwriting prior output."""
import argparse
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
from PIL import Image, ImageDraw

sys.path.insert(0, '/Users/sanger/.hermes/hermes-agent')
from hermes_cli.config import load_config
from hermes_cli.runtime_provider import resolve_runtime_provider

HERE = Path(__file__).resolve().parent
ART = HERE.parent.parent
STYLE = ART / '2026-11-04-county-twentyfive-region-plan/review-009/TR-33-v1.png'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('region', choices=['A', 'B'])
    region = parser.parse_args().region
    out = HERE / 'native' / region
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'native.png').exists() or (out / 'request-started.json').exists():
        raise SystemExit('Existing native/request sentinel: no duplicate request or overwrite.')
    refs = [(HERE / 'references' / f'{region}-structure.png', 'geometry-and-fully-painted-ground-guide'),
            (STYLE, 'original-approved-25-image-art-style-only-not-white-margins-or-source-road-geometry')]
    if region == 'B':
        first = HERE / 'native/A/native.png'
        with Image.open(first) as a:
            if a.size != (1536, 1024):
                raise SystemExit('Actual A dimensions differ; stop rather than resize the native or guess offsets.')
            edge = a.crop((1472, 0, 1536, 1024))
            edge_path = HERE / 'references/A-east-edge.png'
            edge.save(edge_path)
        # The first native did not hold the requested y600 portal: follow the
        # observed y556 road, never warp A or pretend the old contract passed.
        guide = Image.new('RGB', (1536, 1024), '#a3ae8c')
        draw = ImageDraw.Draw(guide)
        for box in [(260, 85, 485, 285), (590, 55, 935, 285),
                    (1075, 90, 1450, 290), (270, 375, 485, 475),
                    (620, 370, 1005, 475), (1100, 390, 1450, 475),
                    (210, 720, 485, 940), (660, 725, 980, 940),
                    (1130, 715, 1440, 935)]:
            draw.rounded_rectangle(box, radius=14, fill='#c1baa6')
        for points in [[(0, 556), (1536, 556)],
                       [(360, 556), (530, 320), (1020, 320), (1130, 556)],
                       [(630, 556), (555, 1024)]]:
            draw.line(points, fill='#d7d0bd', width=92, joint='curve')
            draw.line(points, fill='#737b7d', width=64, joint='curve')
        guide.paste(edge, (0, 0))
        matched = HERE / 'references/B-structure-matched-to-A.png'
        guide.save(matched)
        refs[0] = (matched, 'structure-guide-with-exact-actual-A-64px-shared-strip')
        save(HERE / 'A-observed-portal.json', {
            'requestedY': 600, 'observedCenterYApprox': 556,
            'observedAsphaltRowsColorSupport': [[528, 555], [557, 584]],
            'centerlineBasis': 'Visible road center/dashes in actual A; color rows only supporting diagnostic.',
            'BRequestedAsphaltWidthPixels': 64,
            'ARescaledOrWarped': False, 'newRequestForA': False,
            'AEdgeCrop': [1472, 0, 1536, 1024]})
        refs.append((edge_path, 'only-64px-A-edge-corresponding-exactly-to-B-left-64px-no-full-neighbor-input'))
    instructions = (HERE / f'prompt-{region}.txt').read_text()
    prompt_hash = hashlib.sha256(instructions.encode()).hexdigest()
    config = load_config()
    runtime = resolve_runtime_provider(requested='openai-api',
        explicit_base_url=config['model']['base_url'], target_model=config['model']['default'])
    if runtime.get('provider') != 'openai-api' or not runtime.get('api_key'):
        raise SystemExit('Authorized runtime OpenAI API unavailable; no alternate channel.')
    started = time.time()
    request = {'region': region, 'model': 'gpt-image-2', 'operation': 'images.edit',
               'size': '1536x1024', 'quality': 'high', 'n': 1, 'maxRetries': 0,
               'promptSHA256': prompt_hash,
               'inputs': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                           'role': role} for p, role in refs],
               'multiImageClientCapability': 'OpenAI SDK Images.edit image: Union[FileTypes, SequenceNotStr[FileTypes]]; extract_files image/<array> inspected before requests.',
               'startedUnix': started}
    with (out / 'request-started.json').open('x') as f:
        json.dump(request, f, ensure_ascii=False, indent=2)
    client = OpenAI(api_key=runtime['api_key'], base_url=runtime['base_url'], timeout=240.,
                    max_retries=0, default_headers={'OpenAI-Project': ''},
                    http_client=httpx.Client(trust_env=True, timeout=240.))
    try:
        with ExitStack() as stack:
            images = [stack.enter_context(p.open('rb')) for p, _ in refs]
            response = client.images.edit(model='gpt-image-2', prompt=instructions, image=images,
                                          size='1536x1024', quality='high', n=1)
        if not response.data:
            raise RuntimeError('No image returned; no substitute manufactured.')
        result = response.data[0]
        if result.b64_json:
            raw = base64.b64decode(result.b64_json, validate=True)
        elif result.url and urlparse(result.url).scheme == 'https':
            fetched = httpx.get(result.url, timeout=60, follow_redirects=True)
            fetched.raise_for_status()
            raw = fetched.content
        else:
            raise RuntimeError('No supported image payload.')
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            actual_size, mode = list(image.size), image.mode
        with (out / 'native.png').open('xb') as f:
            f.write(raw)
        usage = getattr(response, 'usage', None)
        usage = usage.model_dump() if usage is not None and hasattr(usage, 'model_dump') else None
        save(out / 'provenance.json', {**request,
            'status': 'real-native-candidate-not-seam-verified-or-user-accepted',
            'agentProvider': 'acp-hermes-agent', 'agentModel': 'openai-api:gpt-6.1-sol',
            'imageProvider': 'openai-api', 'endpointHost': urlparse(runtime['base_url']).hostname,
            'endpointOperation': 'images.edit', 'actualSize': actual_size, 'mode': mode,
            'qualityReturned': getattr(result, 'quality', None), 'usage': usage,
            'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'nativeBytesPreserved': True, 'actualPrompt': instructions,
            'revisedPrompt': getattr(result, 'revised_prompt', None),
            'elapsedSeconds': time.time() - started, 'fullNeighborImageAttached': False})
        print(json.dumps({'region': region, 'status': 'received', 'file': str(out / 'native.png'),
                          'actualSize': actual_size, 'bytes': len(raw),
                          'elapsedSeconds': time.time() - started}, ensure_ascii=False), flush=True)
    except Exception as exc:
        safe = str(exc).replace(runtime['api_key'], '[REDACTED]')
        save(out / 'generation-error.json', {'status': 'failed-no-retry-no-fabricated-image',
             'errorType': type(exc).__name__, 'httpStatus': getattr(exc, 'status_code', None),
             'message': safe[:1800], 'elapsedSeconds': time.time() - started})
        print(json.dumps({'status': 'failed', 'errorType': type(exc).__name__,
                          'httpStatus': getattr(exc, 'status_code', None), 'message': safe[:1000]}), flush=True)
        raise SystemExit(1)
    finally:
        client.close()


if __name__ == '__main__':
    main()
