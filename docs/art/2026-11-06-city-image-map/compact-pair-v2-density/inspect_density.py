#!/usr/bin/env python3
"""Inspect the single raw edit and prepare labelled, unaccepted protection checks."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageDraw

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'compact-pair-v1'


def main():
    directory = HERE / 'analysis'
    if directory.exists():
        raise SystemExit('Analysis already exists; preserve any subsequent edits.')
    directory.mkdir()
    base = Image.open(OLD / 'native/A/native.png').convert('RGB')
    raw = Image.open(HERE / 'native/A-v2-api.png').convert('RGB')
    if raw.size != base.size:
        raise SystemExit('Native size mismatch; do not resize.')
    eligible = Image.open(HERE / 'inputs/edit-eligible.png').convert('L')
    diff = ImageChops.difference(base, raw)
    changed = diff.split()[0]
    for channel in diff.split()[1:]:
        changed = ImageChops.lighter(changed, channel)
    exact_changed = changed.point(lambda x: 255 if x else 0)
    protected_changed = ImageChops.multiply(exact_changed, ImageChops.invert(eligible))
    delta = {'outsideMaskChangedPixels': protected_changed.histogram()[255],
             'east64ChangedPixels': exact_changed.crop((1472, 0, 1536, 1024)).histogram()[255],
             'totalChangedPixels': exact_changed.histogram()[255],
             'endpointHardPreservedNonMaskPixels': protected_changed.histogram()[255] == 0,
             'rawSHA256': hashlib.sha256((HERE / 'native/A-v2-api.png').read_bytes()).hexdigest(),
             'candidateProtectionCompositeNotYetApproved': True}
    (directory / 'raw-difference.json').write_text(json.dumps(delta, ensure_ascii=False, indent=2) + '\n')
    protected_changed.save(directory / 'outside-mask-diff.png')
    candidate = Image.composite(raw, base, eligible)
    candidate.save(directory / 'protected-preview-unaccepted.png')
    edges = ImageChops.subtract(eligible.filter(ImageFilter.MaxFilter(3)), eligible.filter(ImageFilter.MinFilter(3)))
    outline = Image.new('RGB', raw.size, '#00e8ff')
    marked = Image.composite(outline, raw, edges)
    draw = ImageDraw.Draw(marked)
    draw.line([(1472, 0), (1472, 1023)], fill='#ff3b35', width=2)
    marked.save(directory / 'mask-outline-on-api.png')
    comparison = Image.new('RGB', (3072, 1024))
    comparison.paste(base, (0, 0))
    comparison.paste(raw, (1536, 0))
    comparison.save(directory / 'A-before-after-api.png')
    print(json.dumps(delta, ensure_ascii=False))


if __name__ == '__main__':
    main()
