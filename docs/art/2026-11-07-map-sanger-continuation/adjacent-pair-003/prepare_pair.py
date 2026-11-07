"""Build new design guides and record authorization; never edit source artwork."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = HERE.parent
PLAN = ROOT / 'docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/scope-plan.json'
RECEIPT = ROOT / 'docs/team/handoffs/2026-11-07-map-codex-sanger/new-thread-receipt.json'
SNAPSHOT = RECEIPT.with_name('map-protected-snapshot.json')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_new(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    with p.open('x') as f:
        f.write(raw)


def main():
    assert ROOT == Path('/Users/sanger/Documents/ChatGPT/taptap 2')
    manifest = json.loads((BASE / 'artifact-manifest.json').read_text())
    for n, ref in manifest['files'].items():
        assert sha(BASE / n) == ref['sha256'], f'Owned file changed: {n}'
    assert sha(RECEIPT) == manifest['externalReceipt']['sha256']
    protected = json.loads(SNAPSHOT.read_text())
    for n, ref in protected['files'].items():
        assert sha(ROOT / n) == ref['sha256'], f'Protected source changed: {n}'
    now = datetime.now(timezone.utc).isoformat()
    authorization = {
        'recordedAt': now, 'thread': 'thr_fs5qphhxgc', 'directUserQuote': '允许',
        'approvedProposal': '突破原4～6张PM预算；先验证相邻两区，再按真实清晰度、完整街坊与接缝确定总图数',
        'increasedImageCountRouteAllowed': True,
        'boundedAdjacentPairAllowed': True, 'ordinaryBatchQueueStarted': False,
        'illustrative20to24FrozenOrApprovedAsExactCount': False,
        'targetAreaRatioUnchanged': 0.25,
        'noScaleCameraOrBuildingSizeReductionAuthorized': True,
        'formalGameTestsAllowed': False, 'newBackendOrCredentialsAllowed': False,
        'protectedFilesMatchedBefore': len(protected['files']),
        'previousOwnedArtifactsMatchedBefore': len(manifest['files']),
        'priorManifestSHA256': sha(BASE / 'artifact-manifest.json'),
    }
    write_new(HERE / 'authorization.json', authorization)
    for n in ('current-map-state.json', 'artifact-manifest.json', 'REPORT.md'):
        p = HERE / 'before-authorization' / n
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as f:
            f.write((BASE / n).read_bytes())
    with (HERE / 'before-authorization/new-thread-receipt.json').open('xb') as f:
        f.write(RECEIPT.read_bytes())
    choice = {
        'status': 'user-approved-increased-count-route-bounded-adjacent-pair-first',
        'directUserQuote': '允许', 'authorizationRecord': 'adjacent-pair-003/authorization.json',
        'original4to6IsPMPlanningBudgetNotUserHardCount': True,
        'illustrative20to24IsNotFrozenProductionCount': True,
        'actualFinalImageCount': None,
        'scopeAndClarityGatesStillRequired': True,
    }
    state = json.loads((BASE / 'current-map-state.json').read_text())
    state.update(recordedAt=now, status='adjacent-pair-authorized-preparing-new-structured-guides', imageBudgetChoice=choice,
                 nextAction='Sequentially generate W and E bounded samples, inspect native detail and full blocks, measure shared-road interfaces, then trace and verify independent pair. Do not freeze a whole-city count yet.')
    state['blockingEvidence'] = [s for s in state['blockingEvidence'] if '4-6 image budget' not in s]
    state['blockingEvidence'].append('Increased-count route now allowed; final count depends on actual adjacent-pair readability and seam evidence.')
    (BASE / 'current-map-state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    receipt = json.loads(RECEIPT.read_text())
    receipt['imageBudgetChoice'] = choice
    receipt['currentStage']['stage'] = state['status']
    receipt['nextConcreteAction'] = state['nextAction']
    receipt['authorization']['boundedAdjacentPairIncreasedCountRoute'] = True
    receipt['lastUpdatedAt'] = now
    receipt['newCurrentEntrances'].append('docs/art/2026-11-07-map-sanger-continuation/adjacent-pair-003/PLAN.md')
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')

    plan = json.loads(PLAN.read_text())
    nodes = {n['id']: n for n in plan['nodes']}
    scale = 3.125
    sy = scale * math.sin(math.radians(62.5))
    size = (1672, 941)
    origins = {'W': (380.0, 980.0), 'E': (794.72, 980.0)}
    pair = {'status': 'design-proposal-not-output-calibration', 'sourcePlan': str(PLAN.relative_to(ROOT)),
            'sourcePlanSHA256': sha(PLAN), 'targetAreaRatioUnchanged': 0.25,
            'projectedGroundScaleHypothesisPixelsPerDesignMetre': [scale, sy],
            'elevationHypothesisDegrees': 62.5, 'designCanvasSize': list(size),
            'requestedNativeSize': list(size), 'explicitToolSizeParameter': False,
            'designOnlyEImageTranslationToW': [1296.0, 0.0],
            'translationNotAssumedToBeActualOutput': True,
            'sharedRoadCorridor': 'v-4', 'sharedJunctions': ['j-4-3', 'j-4-4', 'j-4-5'],
            'blockOwnership': 'W owns columns1-3; E owns columns4-6; shared-road cut only after actual art inspection',
            'metreCalibrationEstablished': False, 'finalCountFrozen': False, 'regions': {}}
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
    except OSError:
        font = ImageFont.load_default()
    palette = {'residential': '#d7cdbb', 'commercial-office': '#cbb6a3', 'park-community-open': '#91a87d'}
    for key, (ox, oy) in origins.items():
        columns = range(1, 4) if key == 'W' else range(4, 7)
        def project(p):
            return ((p[0] - ox) * scale, (oy - p[1]) * sy)
        selected = [b for b in plan['blocks'] if b['row'] in (3, 4) and b['column'] in columns]
        node_ids = {f'j-{c}-{r}' for c in range(min(columns), max(columns) + 2) for r in range(3, 6)}
        edges = [e for e in plan['edges'] if e['from'] in node_ids and e['to'] in node_ids]
        image = Image.new('RGB', size, '#cbd2bc')
        draw = ImageDraw.Draw(image)
        for b in selected:
            polygon = [project(p) for p in b['polygonDesignMetres']]
            draw.polygon(polygon, fill=palette[b['programme']])
        for e in edges:
            a, b = [project(nodes[e[k]]['designMetres']) for k in ('from', 'to')]
            # Width is the ground-plan design width; rendered art must be inspected independently.
            width = max(1, round(e['proposedAsphaltWidthMetres'] * scale))
            draw.line([a, b], fill='#ddd5c6', width=width + 12)
            draw.line([a, b], fill='#73787a', width=width)
            # Extend perimeter roads to the image edge, keeping edge fragments outside the block ledger.
            for point, other in ((a, b), (b, a)):
                if abs(point[0] - other[0]) > abs(point[1] - other[1]) and (point[0] == min(a[0], b[0]) or point[0] == max(a[0], b[0])):
                    target = (-100, point[1]) if point[0] < 500 else (1800, point[1])
                    if (point == a and e['from'].split('-')[1] == str(min(columns))) or (point == b and e['to'].split('-')[1] == str(max(columns) + 1)):
                        draw.line([point, target], fill='#ddd5c6', width=width + 12)
                        draw.line([point, target], fill='#73787a', width=width)
                elif e['corridorId'].startswith('v-'):
                    nid = e['from'] if point == a else e['to']
                    row = int(nid.split('-')[2])
                    if row in (3, 5):
                        target = (point[0] + (point[0] - other[0]) * 2, 1100 if row == 3 else -100)
                        draw.line([point, target], fill='#ddd5c6', width=width + 12)
                        draw.line([point, target], fill='#73787a', width=width)
        for b in selected:
            x, y = project(b['centre'])
            text = b['id'] + '\n' + b['programme'] + '\n' + b['densityIntent']
            draw.multiline_text((x, y), text, font=font, fill='#384642', anchor='mm', align='center', spacing=4)
        out = HERE / key
        out.mkdir(exist_ok=True)
        with (out / 'structure-guide.png').open('xb') as f:
            image.save(f, format='PNG')
        all_points = [p for b in selected for p in b['polygonDesignMetres']]
        pair['regions'][key] = {
            'originDesignMetres': [ox, oy], 'frameDesignBoundsHypothesis': [ox, oy - size[1] / sy, ox + size[0] / scale, oy],
            'completeBlockDesignBounds': [min(p[0] for p in all_points), min(p[1] for p in all_points), max(p[0] for p in all_points), max(p[1] for p in all_points)],
            'blocks': selected, 'nodes': [{**nodes[nid], 'guidePixels': project(nodes[nid]['designMetres'])} for nid in sorted(node_ids)],
            'edges': edges, 'guideSHA256': sha(out / 'structure-guide.png'),
            'groundSpanExcludesRoofHeightsAndDoesNotProveArtworkScale': True,
        }
    write_new(HERE / 'pair-plan.json', pair)
    refs = [PLAN, SNAPSHOT, ROOT / 'docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png',
            ROOT / 'docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/capacity-proof/approved-density-local.png']
    write_new(HERE / 'input-fingerprints.json', {str(p.relative_to(ROOT)): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in refs})
    print(json.dumps({'status': pair['status'], 'authorizationRecorded': True, 'guides': ['W/structure-guide.png','E/structure-guide.png'], 'completePlannedBlocks': 12, 'protectedMatched': len(protected['files'])}))


if __name__ == '__main__':
    main()
