#!/usr/bin/env python3
"""Reuse the v1 exporter, isolated to the new reference25 authoring directory."""
import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / 'v1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map', default=str(HERE / 'reference-layout.tmj'))
    parser.add_argument('--output', default=str(HERE / 'preview-reference'))
    parser.add_argument('--focus-id', default='')
    args = parser.parse_args()
    if not args.focus_id:
        args.focus_id = ','.join(json.loads((HERE / 'layout-changes.json').read_text())['focusIDs'])
    source = Path(args.map).resolve()
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location('existing_v1_visual_export', V1 / 'export_user_preview.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('Existing v1 exporter is missing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    setattr(module, 'HERE', HERE)
    if not (HERE / 'preview').exists():
        shutil.copytree(V1 / 'preview', HERE / 'preview',
                        ignore=shutil.ignore_patterns('*.png'))
    module.export(args)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    output = Path(args.output).resolve()
    layout = json.loads((output / 'assets/scene-layout.json').read_text())
    base = json.loads((HERE / 'metadata/base-scene.json').read_text())
    assert layout['roads'] == base['roads'], 'Original road arrays must remain unchanged'
    print(json.dumps({'inputMapUnchanged': True, 'originalRoadsUnchanged': True,
                      'visualOnly': True, 'entry': str(output / 'index.html')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
