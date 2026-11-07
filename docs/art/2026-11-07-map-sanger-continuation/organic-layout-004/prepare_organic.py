"""Create a new pixel-space road guide; never modify artwork or legacy geometry."""
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[3]
SIZE = (1672, 941)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(raw if isinstance(raw, bytes) else raw.encode())


def new_json(path, data):
    new(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


NODES = {
    'A': (105, 175), 'B': (510, 115), 'C': (1015, 95), 'D': (1500, 160),
    'S': (1505, 345), 'E': (1450, 740), 'F': (1090, 850), 'G': (510, 810),
    'H': (100, 720), 'P': (120, 560), 'Q': (555, 520), 'T': (800, 405),
    'R': (970, 380), 'U': (1075, 360), 'M': (625, 650), 'V': (1165, 665),
}

# Each road segment meets another only at an explicit shared endpoint.
SPECS = [
    ('A', 'B', (260, 140), (390, 105), 'collector'),
    ('B', 'C', (700, 130), (880, 105), 'collector'),
    ('C', 'D', (1190, 65), (1350, 95), 'collector'),
    ('D', 'S', (1535, 215), (1530, 280), 'collector'),
    ('S', 'E', (1500, 500), (1480, 620), 'collector'),
    ('E', 'F', (1360, 780), (1210, 830), 'collector'),
    ('F', 'G', (900, 875), (690, 850), 'collector'),
    ('G', 'H', (350, 790), (225, 760), 'local'),
    ('H', 'P', (75, 660), (95, 600), 'local'),
    ('P', 'A', (135, 420), (95, 300), 'local'),
    ('P', 'Q', (270, 550), (410, 565), 'primary'),
    ('Q', 'T', (650, 475), (730, 420), 'primary'),
    ('T', 'R', (850, 395), (920, 395), 'primary'),
    ('R', 'U', (1010, 370), (1045, 366), 'primary'),
    ('U', 'S', (1230, 330), (1360, 330), 'primary'),
    ('B', 'Q', (475, 245), (515, 390), 'collector'),
    ('C', 'R', (1050, 210), (1020, 295), 'local'),
    ('C', 'T', (960, 195), (880, 330), 'local'),
    ('Q', 'M', (600, 565), (625, 600), 'local'),
    ('M', 'G', (630, 720), (560, 790), 'local'),
    ('U', 'V', (1090, 480), (1140, 575), 'collector'),
    ('V', 'F', (1190, 725), (1140, 790), 'collector'),
    ('M', 'V', (800, 610), (980, 610), 'local'),
]

BLOCKS = [
    ('O-01', 'compact mixed housing', 'A B Q P', '#d6dcd5'),
    ('O-02', 'dense housing and street shops', 'B C T Q', '#ced7dc'),
    ('O-03', 'small wedge neighbourhood park', 'C R T', '#abc5a4'),
    ('O-04', 'offices and mixed commercial frontage', 'C D S U R', '#dccfbf'),
    ('O-05', 'low and mid-rise housing', 'P Q M G H', '#d2dbcb'),
    ('O-06', 'compact community service and retail', 'Q T R U V M', '#d9ccb9'),
    ('O-07', 'housing with varied inner courts', 'M V F G', '#cdd6d7'),
    ('O-08', 'riverside residential transition', 'U S E F V', '#c4d4c6'),
]


def cubic(a, c1, c2, b, count=48):
    return [[round((1-t)**3*a[k] + 3*(1-t)**2*t*c1[k] + 3*(1-t)*t*t*c2[k] + t**3*b[k], 5)
             for k in range(2)] for t in [i/count for i in range(count+1)]]


def area(poly):
    return sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(poly, poly[1:]+poly[:1]))/2


def path_points(cycle, roads):
    result = []
    for a, b in zip(cycle, cycle[1:]+cycle[:1]):
        direct = next((e for e in roads if e['from'] == a and e['to'] == b), None)
        reverse = next((e for e in roads if e['from'] == b and e['to'] == a), None)
        assert bool(direct) != bool(reverse), (a, b)
        pts = direct['points'] if direct else list(reversed(reverse['points']))
        result += pts[:-1]
    return result


def main():
    assert ROOT == Path('/Users/sanger/Documents/ChatGPT/taptap 2')
    prior = json.loads((BASE/'artifact-manifest.json').read_text())
    for n, r in prior['files'].items():
        assert sha(BASE/n) == r['sha256'], f'Changed prior artifact: {n}'
    receipt = ROOT/prior['externalReceipt']['path']
    assert sha(receipt) == prior['externalReceipt']['sha256']
    snapshot = ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json'
    protected = json.loads(snapshot.read_text())
    for n, r in protected['files'].items():
        assert sha(ROOT/n) == r['sha256'], f'Changed protected source: {n}'
    now = datetime.now(timezone.utc).isoformat()
    for n in ('current-map-state.json', 'artifact-manifest.json', 'REPORT.md', 'sampling-budget.json', 'index.html'):
        new(HERE/'history/before-structure-correction'/n, (BASE/n).read_bytes())
    new(HERE/'history/before-structure-correction/new-thread-receipt.json', receipt.read_bytes())
    new_json(HERE/'authorization.json', {
        'recordedAt': now, 'thread': 'thr_fs5qphhxgc',
        'directUserQuote': '好的，不可以太规整。我们实际的地图，包括前面生成的 25 张图，整个城市的面貌、道路都是曲折的、多变的，要更加真实。',
        'correction': 'road hierarchy, terrain and unequal blocks before image partitioning',
        'existingContinueImageWorkAuthorizationRetained': True,
        'previousPairTechnicalEvidencePreserved': True,
        'previousPairGridNotApprovedForCityProduction': True,
        'targetAreaRatioUnchanged': 0.25, 'formalGameTestsAllowed': False,
        'previousArtifactsMatched': len(prior['files']), 'protectedFilesMatched': len(protected['files']),
    })
    roads = []
    widths = {'primary': 38, 'collector': 28, 'local': 20}
    for a, b, c1, c2, kind in SPECS:
        roads.append({'id': f'{a}-{b}', 'from': a, 'to': b, 'kind': kind,
                      'widthGuidePixels': widths[kind],
                      'points': cubic(NODES[a], c1, c2, NODES[b]),
                      'controlPoints': [list(NODES[a]), list(c1), list(c2), list(NODES[b])]})
    blocks = []
    use = Counter()
    for ident, function, cycle_string, color in BLOCKS:
        cycle = cycle_string.split()
        polygon = path_points(cycle, roads)
        for a, b in zip(cycle, cycle[1:]+cycle[:1]):
            use['-'.join(sorted([a, b]))] += 1
        blocks.append({'id': ident, 'use': function, 'nodeCycle': cycle,
                       'polygon': polygon, 'designEnclosedPixels2': abs(area(polygon)), 'color': color})
    assert len(roads)-len(NODES)+1 == len(blocks) == 8
    assert set(use.values()) == {1, 2}
    data = {'status': 'pixel-design-guide-only-not-output-tracing-or-metres', 'recordedAt': now,
            'canvas': list(SIZE), 'targetAreaRatioUnchanged': 0.25,
            'coordinateUnit': 'design-image-pixel', 'metreCalibration': None,
            'nodes': [{'id': k, 'point': list(v)} for k, v in NODES.items()],
            'roads': roads, 'blocks': blocks,
            'roadHierarchyWidths': widths,
            'boundedFaceCount': 8,
            'smallParkCount': 1,
            'allCityStreetBlockCountOrImageCountFrozen': False}
    new_json(HERE/'structure-guide.json', data)

    scale = 3
    im = Image.new('RGB', (SIZE[0]*scale, SIZE[1]*scale), '#d8ded0')
    draw = ImageDraw.Draw(im)
    points = lambda ps: [(round(x*scale), round(y*scale)) for x, y in ps]
    water = cubic((1652,-30), (1680,300), (1595,720), (1430,990), 120)
    draw.line(points(water), fill='#8fb9c4', width=42*scale, joint='curve')
    for b in blocks:
        draw.polygon(points(b['polygon']), fill=b['color'])
    extensions = [([[-40,575], [40,565], list(NODES['P'])], 'primary'),
                  ([[510,-30], [505,50], list(NODES['B'])], 'collector'),
                  ([list(NODES['D']), [1490,60], [1470,-30]], 'collector'),
                  ([list(NODES['F']), [1040,910], [1030,980]], 'collector'),
                  ([list(NODES['H']), [35,750], [-40,790]], 'local')]
    for road in roads + [{'points': ps, 'kind': k} for ps, k in extensions]:
        ps = points(road['points']); w = widths[road['kind']]
        draw.line(ps, fill='#bec2bf', width=(w+12)*scale, joint='curve')
        draw.line(ps, fill='#687074', width=w*scale, joint='curve')
        r = (w+12)*scale/2
        for x, y in (ps[0], ps[-1]):
            draw.ellipse((x-r,y-r,x+r,y+r), fill='#bec2bf')
        r = w*scale/2
        for x, y in (ps[0], ps[-1]):
            draw.ellipse((x-r,y-r,x+r,y+r), fill='#687074')
    # Repaint shared junction disks at their largest adjoining road width.
    for ident, pos in NODES.items():
        w = max(widths[e['kind']] for e in roads if ident in (e['from'],e['to']))
        x, y = pos[0]*scale, pos[1]*scale
        r = w*scale/2
        draw.ellipse((x-r,y-r,x+r,y+r),fill='#687074')
    im = im.resize(SIZE, Image.Resampling.LANCZOS)
    im.save(HERE/'structure-guide.png')
    labeled = im.copy(); ld = ImageDraw.Draw(labeled)
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 23)
    # Interior labels are guidance only and must not appear in generated art.
    label_points = [(290,300),(720,265),(946,260),(1270,220),(310,655),(870,530),(840,750),(1310,530)]
    for b, pt in zip(blocks,label_points):
        ld.text(pt, b['id'], fill='#263238',font=font,anchor='mm')
    labeled.save(HERE/'structure-guide-labeled.png')
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE[0]} {SIZE[1]}">',
           '<rect width="100%" height="100%" fill="#d8ded0"/>']
    svg.append('<polyline points="'+ ' '.join(f'{x},{y}' for x,y in water)+'" fill="none" stroke="#8fb9c4" stroke-width="42"/>')
    for b in blocks:
        svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in b['polygon'])+f'" fill="{b["color"]}"/>')
    for e in roads:
        ps=' '.join(f'{x},{y}' for x,y in e['points']); w=e['widthGuidePixels']
        svg += [f'<polyline points="{ps}" fill="none" stroke="#bec2bf" stroke-width="{w+12}" stroke-linecap="round"/>',
                f'<polyline points="{ps}" fill="none" stroke="#687074" stroke-width="{w}" stroke-linecap="round"/>']
    new(HERE/'structure-guide.svg','\n'.join(svg+['</svg>']))
    inputs = [
        (HERE/'structure-guide.png', 'new structure guide; pixel design, not measured road tracing'),
        (ROOT/'docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png', 'user style, material, building and road proportions'),
        (ROOT/'docs/art/2026-11-04-county-twentyfive-region-plan/review-007/TR-22-v1.png', 'legacy city organization, varied blocks and terrain relation only; no white diorama framing'),
        (ROOT/'docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/capacity-proof/approved-density-local.png', 'approved dense street fronts and back rows only; do not copy illuminated windows'),
    ]
    new_json(HERE/'input-fingerprints.json', [{'path':str(p.relative_to(ROOT)), 'role':role,
                'sha256':sha(p),'bytes':p.stat().st_size} for p,role in inputs])
    print(json.dumps({'directory':str(HERE), 'nodes':len(NODES),'roads':len(roads),'designBlocks':len(blocks),
                      'designBlockAreasPx2':[round(b['designEnclosedPixels2'],2) for b in blocks],
                      'protectedMatched':len(protected['files']),'priorMatched':len(prior['files'])}))


if __name__ == '__main__':
    main()
