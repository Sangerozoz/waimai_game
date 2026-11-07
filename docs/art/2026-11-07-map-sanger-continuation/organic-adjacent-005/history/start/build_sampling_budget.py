#!/usr/bin/env python3
"""Recompute a conditional map sampling budget. Reads existing evidence only."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
BASE = ROOT / 'docs/art/2026-11-06-city-image-map'
PLAN = BASE / 'planning/scope-recovery-v1/scope-plan.json'
CONSUMER = BASE / 'planning/scope-recovery-v1/consumer-scale-source-contract.json'
EXPERIMENTS = BASE / 'planning/scope-recovery-v1/capacity-proof/experiment-results.json'
SNAPSHOT = ROOT / 'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def scenario(width, height, css_width, samples, elevation, usable=0.9):
    # All metres/projection/sampling here are design hypotheses, not A/B/C calibration.
    ppu = css_width / 120 * samples
    projected_width = width * ppu
    projected_height = height * ppu * math.sin(math.radians(elevation))
    blue = json.loads(PLAN.read_text())['blueDesignBounds']
    blue_area = (blue[2] - blue[0]) * (blue[3] - blue[1])
    outer_area = width * height - blue_area
    variants = []
    native_sizes = [(1536, 1024, 'existing-ABC'), (1674, 940, 'previous-high-request-1'),
                    (1672, 941, 'previous-high-request-2'), (3840, 2160, 'hypothetical-unverified')]
    for tw, th, source in native_sizes:
        core_pixels = tw * th * usable ** 2
        area_equivalents = projected_width * projected_height / core_pixels
        cols = math.ceil(projected_width / (tw * usable))
        rows = math.ceil(projected_height / (th * usable))
        # Separate LOD sensitivity: half linear sampling outdoors, not an adopted design.
        mixed_pixels = (blue_area + outer_area * 0.5 ** 2) * ppu ** 2 * math.sin(math.radians(elevation))
        variants.append({
            'nativeSize': [tw, th], 'source': source,
            'previouslyObservedReturnSize': source != 'hypothetical-unverified',
            'detailAndWholeCityCapacityAccepted': False,
            'areaEquivalentsBeforeRounding': area_equivalents,
            'roundedAreaOnlyEstimate': math.ceil(area_equivalents),
            'illustrativeAxisAlignedGrid': [cols, rows], 'illustrativeGridCount': cols * rows,
            'outerHalfLinearSamplingAreaOnlyEstimate': math.ceil(mixed_pixels / core_pixels),
        })
    return {'cssWidthAssumption': css_width, 'sourcePixelsPerCSSPixelAssumption': samples,
            'elevationHypothesisDegrees': elevation, 'closestFullViewWidthMetresFromSource': 120,
            'designPixelsPerMetre': ppu, 'projectedFullTargetRaster': [projected_width, projected_height],
            'projectedGroundPixels': projected_width * projected_height, 'variants': variants}


def main():
    plan = json.loads(PLAN.read_text())
    consumer = json.loads(CONSUMER.read_text())
    assert consumer['worldViewWidthInCurrentlyLabelledMetres']['manualMax'] == 120
    width, height = plan['targetDesignSizeMetres']
    protected = json.loads(SNAPSHOT.read_text())
    mismatches = [name for name, ref in protected['files'].items()
                  if not (ROOT / name).is_file() or sha(ROOT / name) != ref['sha256']
                  or (ROOT / name).stat().st_size != ref['bytes']]
    assert not mismatches, mismatches
    rows = [scenario(width, height, css, samples, angle)
            for css in (320, 375, 430) for samples in (1, 1.5, 2) for angle in (45, 62.5)]
    baseline = next(r for r in rows if r['cssWidthAssumption'] == 375
                    and r['sourcePixelsPerCSSPixelAssumption'] == 1
                    and r['elevationHypothesisDegrees'] == 62.5)
    sources = [PLAN, CONSUMER, EXPERIMENTS, SNAPSHOT,
               BASE / 'planning/scope-recovery-v1/capacity-direction-addendum.json',
               BASE / 'planning/scope-recovery-v1/scale-board-v1/measurement-record.json',
               HERE / 'builtin-capacity-001/request-record.json',
               HERE / 'builtin-capacity-001/result.json',
               HERE / 'builtin-capacity-002/request-record.json',
               HERE / 'builtin-capacity-002/result.json',
               HERE / 'adjacent-pair-003/authorization.json',
               HERE / 'adjacent-pair-003/W/request-record.json',
               HERE / 'adjacent-pair-003/W/result.json',
               HERE / 'adjacent-pair-003/E/request-record.json',
               HERE / 'adjacent-pair-003/E/result.json',
               HERE / 'adjacent-pair-003/assembly-record.json',
               HERE / 'adjacent-pair-003/actual-pair-graph.json',
               HERE / 'organic-layout-004/authorization.json',
               HERE / 'organic-layout-004/request-record.json',
               HERE / 'organic-layout-004/input-fingerprints.json',
               HERE / 'organic-layout-004/result.json']
    data = {
        'status': 'conditional-budget-not-production-release',
        'recordedAt': datetime.now(timezone.utc).isoformat(),
        'authorThread': 'thr_fs5qphhxgc',
        'targetDesignMetres': [width, height], 'targetDesignAreaKm2': width * height / 1e6,
        'targetAreaRatioToLegacy25': 0.25,
        'existingABCMetreCalibration': None, 'existingTargetAreaCoverage': None,
        'fullViewWidthInExistingSource': consumer['worldViewWidthInCurrentlyLabelledMetres'],
        'perAxisUsableCoreFractionAssumption': 0.9,
        'perAxisMarginIsNotMeasuredSeamAllowance': True,
        'baseline': baseline, 'scenarios': rows,
        'newImageToolAttempt': json.loads((HERE / 'organic-layout-004/result.json').read_text()),
        'imageToolAttempts': [json.loads((HERE / name).read_text()) for name in
            ('builtin-capacity-001/result.json','builtin-capacity-002/result.json',
             'adjacent-pair-003/W/result.json','adjacent-pair-003/E/result.json',
             'organic-layout-004/result.json')],
        'imageRequestsSinceHandoff':5,'successfulImagesSinceHandoff':4,
        'latestArtworkCandidate':'organic-layout-004/index.html',
        'organicLayoutCorrection':{'source':'organic-layout-004/authorization.json',
            'nativeSize':[1672,941],'userArtApproved':False,'ordinaryRegionAdmitted':False,
            'actualRoadTraceCompleted':False,'metreCalibration':None,
            'roadLayoutFollowsTerrainAndUnequalBlocks':True,
            'regularRectanglePackingIsNotCityRoadLayout':True},
        'increasedCountRouteAuthorization':json.loads((HERE/'adjacent-pair-003/authorization.json').read_text()),
        'latestIndependentRoadEvidence': 'adjacent-pair-003/index.html',
        'previousEightBlockEvidence':'road-evidence-002/index.html',
        'adjacentPairEvidence':{'nativeSizes':[[1672,941],[1672,941]],'completeBlocks':12,
            'assemblySize':[3248,937],'structuralEdgesIncludingInference':35,'permittedNavigationEdges':34,
            'occludedInferenceEdgeIds':['W-h-0-2'],'metreCalibration':None,'finalImageCount':None,
            'source':'adjacent-pair-003/assembly-record.json','userArtApproved':False},
        'sourceSHA256': {str(p.relative_to(ROOT)): sha(p) for p in sources},
        'protectedFilesChecked': len(protected['files']), 'protectedFilesMatched': len(protected['files']),
        'limits': [
            'CSS widths, sampling, elevation, axis alignment and 90% usable cores are hypotheses.',
            '120m closest full view is source reading, not a new-map camera or user-device approval.',
            'DPR is not measured; sourcePixelsPerCSSPixel is a chosen texture-sampling hypothesis.',
            'Uniform ground raster ignores roof overhang, complete-block packing, seam failures and content quality.',
            'Area-equivalent and regular-grid counts are distinct conditional estimates, not procurement or production counts.',
            'Outdoor half sampling is sensitivity only, not user approval to reduce any art or displayed detail.',
            '4K is unavailable/unverified here; the first built-in request failed HTTP502, the second returned1672x941.',
            'Two additional native1672x941 images now provide a measured adjacent pair; this does not calibrate metres or freeze the illustrative20–24 count.',
            'The pair has one roof-occluded structural inference explicitly excluded from both navigation routes.',
            'The new organic-road image is an artwork candidate only; its design geometry is not actual road tracing. W/E grid composition is not a city production template.',
            'Rectangular raster packing is only a capacity example; organic streets and corridor-based image partitions must be planned separately.',
            'Existing ABC pixels are not assigned arbitrary metres or a fake coverage fraction.',
            'A2 native 53/54px asphalt evidence does not establish a real-world road width or map ground scale.',
        ],
        'ordinaryRegionsAdded': 0, 'DResumed': False, 'productionReady': False,
        'formalGameTestsPerformed': False, 'gameSourceWrites': False,
    }
    write_json(HERE / 'sampling-budget.json', data)
    template = (HERE / 'budget-template.html').read_text()
    (HERE / 'index.html').write_text(template.replace('__BUDGET_DATA__', json.dumps(data, ensure_ascii=False)))
    print(json.dumps({'status': data['status'], 'scenarios': len(rows),
                      'baselineProjectedRaster': baseline['projectedFullTargetRaster'],
                      'baseline': baseline['variants'], 'protectedMatched': len(protected['files']),
                      'htmlBytes': (HERE / 'index.html').stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
