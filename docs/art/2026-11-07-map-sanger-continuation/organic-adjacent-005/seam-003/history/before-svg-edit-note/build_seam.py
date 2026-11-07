"""Deterministic map assembly from unchanged native pixels and editable cut geometry."""
import hashlib
import io
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()


def png(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def cuts_for_rows(points, height):
    assert points[0][1] == 0 and points[-1][1] == height
    assert all(a[1] < b[1] for a,b in zip(points,points[1:]))
    assert all(1520 <= x <= 1671 for x,_ in points)
    result = []
    segment = 0
    for row in range(height):
        y = row + .5
        while points[segment+1][1] <= y:
            segment += 1
        (x0,y0),(x1,y1) = points[segment:segment+2]
        x = x0 + (x1-x0)*(y-y0)/(y1-y0)
        # Pixel centres strictly to the left use005; no alpha interpolation.
        result.append(math.ceil(x - .5))
    return result


def write_owned(outputs):
    manifest_path = HERE / 'generated-files.json'
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for relative in outputs:
        path = HERE / relative
        assert path.resolve().is_relative_to(HERE.resolve())
        if path.exists():
            assert relative in old and sha(path) == old[relative]['sha256'], relative
    for relative, raw in outputs.items():
        path = HERE / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    updated = {name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in outputs.items()}
    manifest_path.write_bytes(encoded(dict(sorted({**old, **updated}.items()))))


def main():
    inputs = json.loads((HERE / 'seam-input.json').read_text())
    images = {}
    for source in ['005','004']:
        record = inputs['native'+source]
        path = HERE / record['path']
        assert sha(path) == record['sha256']
        images[source] = Image.open(path).convert('RGB')
        assert list(images[source].size) == record['size']
    width,height = inputs['assemblySize']
    cuts = cuts_for_rows(inputs['cutPolyline'], height)
    pair = Image.new('RGB', (width,height))
    mask = Image.new('L', (1671,height), 0)
    for row,cut in enumerate(cuts):
        pair.paste(images['005'].crop((0,row,cut,row+1)), (0,row))
        pair.paste(images['004'].crop((cut-1520,row,width-1520,row+1)), (cut,row))
        mask.paste(255, (0,row,cut,row+1))
    selected005 = images['005'].convert('RGBA')
    selected005.putalpha(mask)
    record = {'sourceSHA256':{k:inputs['native'+k]['sha256'] for k in images},'size':[width,height],
              'method':inputs['method'],'rowCuts':cuts,'sourcePixelCounts':{'005':sum(cuts),'004':width*height-sum(cuts)},
              'source005MaskAlphaValues':[0,255],'seamRasterization':'source005 when pixel centre x+0.5 < interpolated cut at y+0.5',
              'wholeSeamReady':False,'userCompositeApproved':False,'ordinaryRegionAdmitted':False,'formalGameTestsPerformed':False}
    path = ' '.join(('M' if i == 0 else 'L') + str(x)+' '+str(y) for i,(x,y) in enumerate(inputs['cutPolyline']))
    west = 'M0 0 ' + ' '.join('L'+str(x)+' '+str(y) for x,y in inputs['cutPolyline']) + ' L0 941 Z'
    east = 'M3192 0 ' + ' '.join('L'+str(x)+' '+str(y) for x,y in inputs['cutPolyline']) + ' L3192 941 Z'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="3192" height="941" viewBox="0 0 3192 941">
<title>004/005 editable cut candidate; SVG display may antialias boundaries; PNG uses binary source pixels</title>
<defs><clipPath id="west"><path d="{west}"/></clipPath><clipPath id="east"><path d="{east}"/></clipPath></defs>
<image href="../native.png" width="1671" height="941" clip-path="url(#west)"/>
<image href="../../organic-layout-004/native.png" x="1520" width="1672" height="941" clip-path="url(#east)"/>
<path d="{path}" fill="none" stroke="#df006f" stroke-width="2" style="display:none" id="editable-cut"/>
</svg>'''
    annotated = pair.copy()
    draw = ImageDraw.Draw(annotated)
    draw.line([tuple(point) for point in inputs['cutPolyline']], fill='#ff0088', width=2)
    outputs = {'assembly/pair-native.png':png(pair),'assembly/005-mask.png':png(mask),'assembly/005-selected.png':png(selected005),
               'assembly/record.json':encoded(record),'editable-cut.svg':svg.encode(),
               'inspection/seam-with-cut.png':png(annotated.crop((1380,0,1800,941))),
               'inspection/seam-clean.png':png(pair.crop((1380,0,1800,941)))}
    for name,y0,y1 in [('north',0,235),('middle',280,500),('south',700,941)]:
        outputs['inspection/'+name+'-clean.png'] = png(pair.crop((1380,y0,1800,y1)))
        outputs['inspection/'+name+'-cut.png'] = png(annotated.crop((1380,y0,1800,y1)))
    write_owned(outputs)
    print(json.dumps({'size':[width,height],'sourcePixelCounts':record['sourcePixelCounts'],'nativeSourcesUnchanged':True,'candidateOnly':True}))


if __name__ == '__main__':
    main()
