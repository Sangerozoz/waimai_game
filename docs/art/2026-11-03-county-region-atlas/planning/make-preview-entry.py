"""Nominal art placement for assembly-first production; NOT measured registration."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('structure');p.add_argument('image');p.add_argument('output')
a=p.parse_args();s=json.loads(Path(a.structure).read_text());im=Image.open(a.image)
gw,gh=s['guide']['nativeSize'];w,h=im.size
if abs(w/gw-h/gh)>1e-6:raise ValueError('Native aspect ratio differs from guide; manual placement required, do not distort image')
e=dict(id=s['id'],file=str(Path(a.image)),sha256=hashlib.sha256(Path(a.image).read_bytes()).hexdigest(),nativeSize=[w,h],anchorMap=s['originMap'],anchorUV=[s['projection']['originPixel'][0]/gw,s['projection']['originPixel'][1]/gh],nativePixelsPerUnit=s['projection']['nativePixelsPerUnit']*w/gw,sortOrder=-100,ownershipPolygonUV=None,registration=dict(status='preview-only',evidence=str(Path(a.structure)),controlPoints=[],maxResidualPixels=None,routeCoverageMapPolygon=None,method='nominal guide framing only; no observed correspondences or measured registration'),note='Assembly-first display only. No rider/route authorization; alignment and obvious blocking repairs deferred to the full-map pass.')
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
if out.exists():raise ValueError('Preserve prior entry: output already exists')
out.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(id=e['id'],file=e['file'],status='preview-only',measured=False)))
