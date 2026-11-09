#!/usr/bin/env python3
"""One real image edit/generation on the existing authorized OpenAI API route."""
import base64
import hashlib
import io
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, '/Users/sanger/.hermes/hermes-agent')
from hermes_cli.config import load_config
from hermes_cli.runtime_provider import resolve_runtime_provider
import httpx
from openai import OpenAI
from PIL import Image

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / '2026-11-04-county-twentyfive-region-plan/review-009/TR-33-v1.png'


def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    if (HERE / 'native-city-block.png').exists():
        raise SystemExit('Native output already exists; refusing duplicate generation')
    prompt = (HERE / 'prompt.txt').read_text()
    started = time.time()
    # Exclusive sentinel also protects repeated user delivery/interruption recovery.
    with (HERE / 'request-started.json').open('x') as f:
        json.dump({'startedUnix': started, 'operation': 'one-real-openai-api-image-edit',
                   'model': 'gpt-image-2', 'requestedSize': '1536x1024'}, f)
    config = load_config()
    runtime = resolve_runtime_provider(requested='openai-api',
        explicit_base_url=config['model']['base_url'], target_model=config['model']['default'])
    if runtime.get('provider') != 'openai-api' or not runtime.get('api_key'):
        raise RuntimeError('Authorized OpenAI API route unavailable; no alternate provider attempted')
    client = OpenAI(api_key=runtime['api_key'], base_url=runtime['base_url'],
                    timeout=240.0, max_retries=0,
                    default_headers={'OpenAI-Project': ''},
                    http_client=httpx.Client(trust_env=True, timeout=240.0))
    try:
        with REFERENCE.open('rb') as image:
            response = client.images.edit(model='gpt-image-2', prompt=prompt, image=image,
                                          size='1536x1024', quality='high', n=1)
        if not response.data:
            raise RuntimeError('API returned no image data')
        first = response.data[0]
        if first.b64_json:
            native_bytes = base64.b64decode(first.b64_json, validate=True)
        elif first.url:
            if urlparse(first.url).scheme != 'https':
                raise RuntimeError('Refusing non-HTTPS image URL')
            with httpx.Client(timeout=60, follow_redirects=True) as downloader:
                fetched = downloader.get(first.url)
                fetched.raise_for_status()
                native_bytes = fetched.content
        else:
            raise RuntimeError('Image payload missing; no output fabricated')
        with Image.open(io.BytesIO(native_bytes)) as im:
            im.load()
            dimensions, mode = list(im.size), im.mode
        output = HERE / 'native-city-block.png'
        output.write_bytes(native_bytes)
        usage = getattr(response, 'usage', None)
        usage = usage.model_dump() if usage is not None and hasattr(usage, 'model_dump') else None
        record = {'status': 'real-native-image-received-not-user-accepted',
                  'agentProvider': 'Hermes/OpenAI API', 'imageProvider': 'openai-api',
                  'endpointHost': urlparse(runtime['base_url']).hostname,
                  'endpointOperation': 'images.edit', 'modelRequested': 'gpt-image-2',
                  'sizeRequested': '1536x1024', 'qualityRequested': 'high',
                  'qualityReturned': getattr(first, 'quality', None), 'nativeSize': dimensions,
                  'mode': mode, 'bytes': len(native_bytes),
                  'nativeSHA256': hashlib.sha256(native_bytes).hexdigest(),
                  'reference': str(REFERENCE),
                  'referenceSHA256': hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
                  'referenceRole': 'style-only-not-source-geometry',
                  'actualPrompt': prompt, 'revisedPrompt': getattr(first, 'revised_prompt', None),
                  'usage': usage, 'elapsedSeconds': time.time() - started,
                  'nativeBytesPreserved': True, 'noOriginalMapOrRoadEdits': True,
                  'automaticRoadExtractionImplemented': False}
        write_json('provenance.json', record)
        print(json.dumps({'status': 'generated', 'file': str(output),
                          'actualSize': dimensions, 'bytes': len(native_bytes)}, ensure_ascii=False), flush=True)
    except Exception as exc:
        safe = str(exc).replace(runtime.get('api_key') or 'UNMATCHABLE_SECRET', '[REDACTED]')
        write_json('generation-error.json', {'status': 'failed-no-image-substitute',
                   'errorType': type(exc).__name__, 'httpStatus': getattr(exc, 'status_code', None),
                   'message': safe[:2000], 'elapsedSeconds': time.time() - started})
        print(json.dumps({'status': 'failed', 'errorType': type(exc).__name__,
                          'httpStatus': getattr(exc, 'status_code', None), 'message': safe[:1200]}, ensure_ascii=False), flush=True)
        raise SystemExit(1)
    finally:
        client.close()


if __name__ == '__main__':
    main()
