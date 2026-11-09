#!/usr/bin/env python3
"""Exactly one authorized A density edit, with a real SDK mask field."""
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

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'compact-pair-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    output = HERE / 'native'
    output.mkdir(exist_ok=True)
    marker = output / 'request-started.json'
    native = output / 'A-v2-api.png'
    if marker.exists() or native.exists():
        raise SystemExit('A-v2 request/output exists; inspect it, never generate twice.')
    inputs = [(OLD / 'native/A/native.png', 'accepted-A-mother-for-density-edit-only'),
              (HERE / 'inputs/edit-guide.png', 'allowed-area-annotation-not-art-or-new-palette')]
    mask = HERE / 'inputs/edit-mask.png'
    with Image.open(mask) as m:
        if m.mode != 'RGBA' or m.size != (1536, 1024):
            raise SystemExit('Invalid mask; no API request made.')
    protected = json.loads((HERE / 'protected-inputs.json').read_text())
    if any(sha(Path(p)) != value for p, value in protected.items()):
        raise SystemExit('Readonly source changed; do not restore or generate against unknown input.')
    prompt = (HERE / 'prompt.txt').read_text()
    config = load_config()
    runtime = resolve_runtime_provider(requested='openai-api',
        explicit_base_url=config['model']['base_url'], target_model=config['model']['default'])
    if runtime.get('provider') != 'openai-api' or not runtime.get('api_key'):
        raise SystemExit('Authorized API runtime unavailable; no alternate provider.')
    request = {'operation': 'images.edit', 'model': 'gpt-image-2', 'region': 'A-v2-density',
               'size': '1536x1024', 'quality': 'high', 'n': 1, 'maxRetries': 0,
               'inputs': [{'path': str(p), 'sha256': sha(p), 'role': role} for p, role in inputs],
               'mask': {'path': str(mask), 'sha256': sha(mask),
                        'semantics': 'alpha0 editable, alpha255 protected; applies to first input A'},
               'promptPath': str(HERE / 'prompt.txt'), 'promptSHA256': sha(HERE / 'prompt.txt'),
               'codeSHA256': sha(Path(__file__)),
               'sdkMaskCapability': 'Images.edit mask: FileTypes; extract_files paths includes mask, previously inspected.',
               'endpointHardPreservationBeforeRequest': 'unverified; measured on this single real result, no extra probe',
               'executionCommands': 'execution-commands.json', 'agentProvider': 'acp-hermes-agent',
               'agentModel': 'openai-api:gpt-6.1-sol', 'reasoningEffortRequested': 'high'}
    started = time.time()
    with marker.open('x') as file:
        json.dump({**request, 'startedUnix': started}, file, ensure_ascii=False, indent=2)
    client = OpenAI(api_key=runtime['api_key'], base_url=runtime['base_url'], timeout=240.,
                    max_retries=0, default_headers={'OpenAI-Project': ''},
                    http_client=httpx.Client(trust_env=True, timeout=240.))
    try:
        with ExitStack() as stack:
            handles = [stack.enter_context(path.open('rb')) for path, _ in inputs]
            mask_file = stack.enter_context(mask.open('rb'))
            response = client.images.edit(model='gpt-image-2', image=handles, mask=mask_file,
                                          prompt=prompt, size='1536x1024', quality='high', n=1)
        if not response.data:
            raise RuntimeError('No image returned; no fabricated replacement.')
        first = response.data[0]
        if first.b64_json:
            data = base64.b64decode(first.b64_json, validate=True)
        elif first.url and urlparse(first.url).scheme == 'https':
            fetched = httpx.get(first.url, timeout=60, follow_redirects=True)
            fetched.raise_for_status()
            data = fetched.content
        else:
            raise RuntimeError('No supported image payload.')
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            actual_size, mode = list(im.size), im.mode
        with native.open('xb') as file:
            file.write(data)
        usage = getattr(response, 'usage', None)
        record = {**request, 'status': 'real-native-edit-returned-not-density-or-geometry-accepted',
                  'endpointHost': urlparse(runtime['base_url']).hostname,
                  'actualSize': actual_size, 'mode': mode,
                  'qualityReturned': getattr(first, 'quality', None),
                  'nativeSHA256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                  'nativeBytesPreserved': True, 'actualPrompt': prompt,
                  'revisedPrompt': getattr(first, 'revised_prompt', None),
                  'usage': usage.model_dump() if usage is not None and hasattr(usage, 'model_dump') else None,
                  'elapsedSeconds': time.time() - started, 'BRequestMade': False}
        save(output / 'provenance.json', record)
        print(json.dumps({'status': 'received', 'native': str(native), 'actualSize': actual_size,
                          'bytes': len(data), 'elapsedSeconds': time.time() - started}, ensure_ascii=False), flush=True)
    except Exception as exc:
        safe = str(exc).replace(runtime['api_key'], '[REDACTED]')
        save(output / 'generation-error.json', {'status': 'failed-no-retry-no-substitute',
             'errorType': type(exc).__name__, 'httpStatus': getattr(exc, 'status_code', None),
             'message': safe[:1800], 'elapsedSeconds': time.time() - started})
        print(json.dumps({'status': 'failed', 'errorType': type(exc).__name__,
                          'httpStatus': getattr(exc, 'status_code', None), 'message': safe[:1000]}), flush=True)
        raise SystemExit(1)
    finally:
        client.close()


if __name__ == '__main__':
    main()
