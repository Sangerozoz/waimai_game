"""Material-production diagnostics only. Never alter native art or game data."""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path('docs/art/2026-11-03-county-region-atlas')
OUT = BASE / 'repairs/north-A'
A = json.loads((BASE/'registration/region-A-AB-v4-runtime-entry.json').read_text())
N = json.loads((BASE/'production/R-+00--01/registration/region-entry.json').read_text())
if len(sys.argv)>1:
    N['file']=sys.argv[1]
ART_A = Path('docs/art/2026-11-03-whole-region-map/REGION-A-v3.png')
Q = math.sqrt(.5)
S = math.sin(math.radians(62.5))
def axis(p):
    x, y = p[0]-A['anchorMap'][0], p[1]-A['anchorMap'][1]
    return [(x-y)*Q, (x+y)*S*Q]
def on_a(p):
    return [A['anchorUV'][k]*A['nativeSize'][k] + A['nativePixelsPerUnit']*axis(p)[k] for k in (0,1)]
ratio = A['nativePixelsPerUnit']/N['nativePixelsPerUnit']
origin = on_a(N['anchorMap'])
offset = [origin[k] - N['anchorUV'][k]*N['nativeSize'][k]*ratio for k in (0,1)]
shift = [60, 530]
canvas = Image.new('RGBA', (2100,1900), '#202027')
a = Image.open(ART_A).convert('RGBA')
n = Image.open(N['file']).convert('RGBA')
n = n.resize(tuple(round(v*ratio) for v in n.size), Image.Resampling.LANCZOS)
for order in ('N-over-A','A-over-N'):
    out = canvas.copy()
    for name, im, xy in ([('A',a,shift),('N',n,[round(offset[k]+shift[k]) for k in (0,1)])] if order=='N-over-A' else [('N',n,[round(offset[k]+shift[k]) for k in (0,1)]),('A',a,shift)]):
        out.alpha_composite(im, xy)
    d=ImageDraw.Draw(out)
    seam=[on_a([x,28]) for x in (-1640,-1520)]
    d.line([tuple(p[k]+shift[k] for k in (0,1)) for p in seam], fill='#ff55dd',width=3)
    for x,y in ((-1640,23.61957376557106),(-1577.55159925616,20)):
        p=on_a([x,y]);p=[p[k]+shift[k] for k in (0,1)]
        d.ellipse([p[0]-8,p[1]-8,p[0]+8,p[1]+8],outline='#00ffff',width=3)
    d.text((20,20),f'{order}: SHARED WORLD MATERIAL DIAGNOSTIC / NOT GAME / MAGENTA: NOMINAL y=28 ONLY',fill='white')
    suffix='-v2' if len(sys.argv)>1 else ''
    out.convert('RGB').save(OUT/(order+suffix+'.jpg'))
(OUT/'transform.json').write_text(json.dumps(dict(uniformScale=ratio,translationInANative=offset,diagnosticOnly=True,nativeArtEdited=False,nominalSeamIsNotApproved=True),indent=2)+'\n')
