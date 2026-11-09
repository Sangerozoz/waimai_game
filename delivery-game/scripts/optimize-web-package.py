#!/usr/bin/env python3
"""Create a versioned runtime copy without changing authoring assets or saves."""
import argparse
import gzip
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

PROJECT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode()


def version(data):
    return hashlib.sha256(data).hexdigest()[:12]


def compact_uuid(value):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    value = value.replace('-', '')
    result = value[:2]
    for index in range(2, 32, 3):
        number = int(value[index:index + 3], 16)
        result += alphabet[number >> 6] + alphabet[number & 63]
    return result


def rename_content(path, raw):
    parts = path.name.split('.')
    assert len(parts) == 3, path
    replacement = path.with_name(parts[0] + '.' + version(raw) + '.' + parts[2])
    replacement.write_bytes(raw)
    if replacement != path:
        path.unlink()
    return replacement


def optimize(source, output, inventory=None, image_receipt=None, transport_only=False):
    source, output = source.resolve(), output.resolve()
    if output.exists() or output == source or source in output.parents:
        raise ValueError('output must be a new directory outside the input build')
    before = {str(p.relative_to(source)): sha(p) for p in source.rglob('*') if p.is_file()}
    if 'index.html' not in before:
        raise ValueError('source is not a built web package')
    jobs = {}
    images = []
    image_provider = None
    native_images = {str(p.relative_to(source)) for p in source.glob('assets/resources/native/*/*')
                     if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.avif', '.jxl')}
    mapped_images = set()
    if not transport_only:
        if inventory is None or image_receipt is None:
            raise ValueError('TinyPNG inventory and completed receipt required')
        provider = json.loads(image_receipt.read_text())
        image_provider = provider.get('provider')
        if provider.get('status') != 'COMPLETE' or image_provider != 'TinyPNG official public website':
            raise ValueError('actual completed TinyPNG receipt required')
        images = json.loads(inventory.read_text())['files']
        jobs = {job['sourceSHA256']: job for job in provider['results'] if job.get('downloaded')}
        if not all(row['sha256'] in jobs for row in images):
            raise ValueError('TinyPNG outputs do not cover every image input')
        for row in images:
            original = PROJECT / row['path']
            uuid = json.loads(original.with_suffix(original.suffix + '.meta').read_text())['uuid']
            native, = source.glob('assets/resources/native/*/' + uuid + '.*' + original.suffix.lower())
            relative = str(native.relative_to(source))
            if relative in mapped_images:
                raise ValueError('image inventory repeats a native asset')
            mapped_images.add(relative)
        if not mapped_images or mapped_images != native_images:
            raise ValueError('image inventory must cover the complete native image set')
    stage = output.with_name(output.name + '.part')
    if stage.exists():
        raise ValueError('previous unfinished stage exists; inspect before retrying')
    stage.mkdir(parents=True)
    changed_images = []
    try:
        for relative in before:
            src, dest = source / relative, stage / relative
            if src.is_symlink():
                raise ValueError('source build must not contain symlinks')
            if src.suffix == '.gz':
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
        resource_root = stage / 'assets/resources'
        config_path, = resource_root.glob('config.*.json')
        config = json.loads(config_path.read_text())
        native_versions = config['versions']['native']
        for row in images:
            original = PROJECT / row['path']
            if sha(original) != row['sha256']:
                raise ValueError('source image changed after inventory: ' + row['path'])
            job = jobs[row['sha256']]
            optimized = Path(job['optimizedPath'])
            if sha(optimized) != job['outputSHA256']:
                raise ValueError('TinyPNG output fingerprint differs')
            uuid = json.loads(original.with_suffix(original.suffix + '.meta').read_text())['uuid']
            native, = resource_root.glob('native/*/' + uuid + '.*' + original.suffix.lower())
            if sha(native) != row['sha256']:
                raise ValueError('native image differs from authoring input: ' + row['path'])
            with Image.open(optimized) as b:
                b.verify()
            with Image.open(native) as a, Image.open(optimized) as b:
                a.load()
                b.load()
                if a.size != b.size or a.format != b.format:
                    raise ValueError('image dimensions/format must be preserved for crop coordinates')
            if optimized.stat().st_size >= native.stat().st_size:
                continue
            old_name = str(native.relative_to(stage))
            raw = optimized.read_bytes()
            new_native = rename_content(native, raw)
            index = config['uuids'].index(compact_uuid(uuid))
            position = native_versions[::2].index(index) * 2 + 1
            native_versions[position] = version(raw)
            changed_images.append({'source': row['path'], 'before': old_name, 'after': str(new_native.relative_to(stage)),
                                   'beforeBytes': row['bytes'], 'afterBytes': len(raw), 'sha256': sha(new_native)})
        settings_path, = (stage / 'src').glob('settings.*.json')
        settings = json.loads(settings_path.read_text())
        if changed_images:
            new_config = rename_content(config_path, encoded_json(config))
            new_bundle_version = new_config.name.split('.')[1]
            old_bundle_version = settings['assets']['bundleVers']['resources']
            index = resource_root / ('index.' + old_bundle_version + '.js')
            index.rename(index.with_name('index.' + new_bundle_version + '.js'))
            settings['assets']['bundleVers']['resources'] = new_bundle_version
        # A fixed logo delay is not a loading requirement. Other engine settings stay intact.
        settings['splashScreen']['totalTime'] = 0
        new_settings = rename_content(settings_path, encoded_json(settings))
        application, = stage.glob('application.*.js')
        raw = application.read_text()
        old_settings = str(settings_path.relative_to(stage))
        if raw.count(old_settings) != 1:
            raise ValueError('unexpected settings reference count')
        new_application = rename_content(application, raw.replace(old_settings, str(new_settings.relative_to(stage))).encode())
        entry, = stage.glob('index.*.js')
        raw = entry.read_text()
        if raw.count(application.name) != 1:
            raise ValueError('unexpected application reference count')
        new_entry = rename_content(entry, raw.replace(application.name, new_application.name).encode())
        html = stage / 'index.html'
        raw = html.read_text()
        if raw.count(entry.name) != 1:
            raise ValueError('unexpected entry reference count')
        html.write_text(raw.replace(entry.name, new_entry.name))
        sidecars = []
        for path in list(stage.rglob('*')):
            if not path.is_file() or path.suffix not in ('.html', '.css', '.js', '.json', '.wasm'):
                continue
            raw = path.read_bytes()
            if len(raw) <= 1024:
                continue
            encoded = gzip.compress(raw, compresslevel=9, mtime=0)
            path.with_name(path.name + '.gz').write_bytes(encoded)
            sidecars.append({'path': str(path.relative_to(stage)), 'rawBytes': len(raw), 'gzipBytes': len(encoded)})
        if any(sha(source / relative) != expected for relative, expected in before.items()):
            raise ValueError('input build changed while packaging')
        receipt = {'source': str(source), 'mode': 'transport-only; TinyPNG images pending' if transport_only else 'TinyPNG plus transport',
                   'imageProvider': image_provider,
                   'allImageInputsCovered': bool(mapped_images) and mapped_images == native_images,
                   'expectedNativeImages': len(native_images), 'mappedNativeImages': len(mapped_images),
                   'imagesCompressed': len(changed_images),
                   'changedImages': changed_images, 'textSidecars': sidecars, 'fixedSplashTimeMs': 0,
                   'businessJavaScriptAndCityUnchanged': True, 'inputFilesUnchanged': len(before)}
        (stage / 'package-receipt.json').write_bytes(encoded_json(receipt))
        (stage / 'package-receipt.json.gz').write_bytes(gzip.compress(encoded_json(receipt), compresslevel=9, mtime=0))
        stage.rename(output)
        return receipt
    except Exception:
        shutil.rmtree(stage)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--inventory', type=Path)
    parser.add_argument('--image-receipt', type=Path)
    parser.add_argument('--transport-only', action='store_true', help='Explicit partial mode; never claims image compression')
    options = parser.parse_args()
    result = optimize(options.source, options.output, options.inventory, options.image_receipt, options.transport_only)
    print(json.dumps({key: result[key] for key in ('mode', 'imageProvider', 'imagesCompressed', 'inputFilesUnchanged')}))


if __name__ == '__main__':
    main()
