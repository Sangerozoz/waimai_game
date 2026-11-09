#!/usr/bin/env python3
"""Audit saved B evidence offline; never run or mutate the game/browser/services."""

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
B = OUT.parent
TESTING = B.parent


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def ensure(condition, message):
    if not condition:
        raise AssertionError(message)


def tagged(record):
    values = {}
    for line in record['response'].get('text', '').splitlines():
        label, separator, payload = line.partition(' ')
        if separator and label in ('TOUCH_METHODS', 'TOUCH_HANDLE'):
            # Historical util.inspect output uses JS single quotes, not JSON.
            values[label] = {'format': 'JavaScript debug text', 'raw': payload}
            continue
        if separator and payload.lstrip().startswith(('{', '[')):
            values[label] = json.loads(payload)
    return values


def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length2 = dx * dx + dy * dy
    t = max(0, min(1, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length2)) if length2 else 0
    return math.hypot(point[0] - start[0] - t * dx, point[1] - start[1] - t * dy)


def tap_totals(path):
    content = path.read_text()
    result = {}
    for name in ('tests', 'pass', 'fail', 'skipped'):
        matches = re.findall(r'^# ' + name + r' (\d+)$', content, re.MULTILINE)
        ensure(len(matches) == 1, f'Ambiguous TAP total: {path.name}/{name}')
        result[name] = int(matches[0])
    return result


def main():
    protected_path = ROOT / 'docs/team/handoffs/2026-11-07-codex-migration/protected-artifacts.json'
    protected = read(protected_path)
    protected_checks = []
    for name, expected in protected['files'].items():
        path = ROOT / name
        ensure(path.is_file(), f'Missing protected input: {name}')
        actual = digest(path)
        ensure(actual == expected['sha256'], f'Protected input changed: {name}')
        protected_checks.append({'path': name, 'sha256': actual})

    original_files = {relative(path): digest(path) for path in sorted(B.iterdir()) if path.is_file()}
    manifest_path = OUT / 'original-evidence-manifest.json'
    if manifest_path.exists():
        ensure(original_files == read(manifest_path)['files'], 'Original B files changed since supplement baseline')

    records, values, paths, captures = {}, {}, {}, []
    for path in sorted(B.glob('[0-9][0-9]-*.json')):
        number = int(path.name[:2])
        record = read(path)
        ensure(record['terminalExitCode'] == 0 and record['response']['exitCode'] == 0, f'Record command failed: {path.name}')
        records[number], values[number], paths[number] = record, tagged(record), path
        for capture in record['captures']:
            screenshot = Path(capture['path'])
            expected = capture['copy']['output'].split()[0]
            ensure(capture['copy']['exit_code'] == 0, f'Capture copy failed: {screenshot.name}')
            ensure(digest(screenshot) == expected, f'Capture digest mismatch: {screenshot.name}')
            captures.append({'record': relative(path), 'path': relative(screenshot), 'sha256': expected,
                             'recordedSize': [capture['width'], capture['height']]})
    ensure(sorted(records) == list(range(1, 42)), 'Expected exactly B01..B41')
    for number in range(20, 42):
        for value in values[number].values():
            if isinstance(value, dict):
                for field in ('errors', 'console', 'errorRecords', 'consoleRecords', 'networkFailures'):
                    ensure(not value.get(field), f'Observed diagnostic in B{number}/{field}')

    source_path = ROOT / 'delivery-game/assets/scripts/map-sample/V2GameUI.ts'
    source = source_path.read_bytes()
    fixed = b'loadSummary(Array.from(batchLoads.values()),capacity)'
    previous = b'loadSummary([...batchLoads.values()],capacity)'
    ensure(source.count(fixed) == 1, 'Expected one fixed argument')
    inverse = hashlib.sha256(source.replace(fixed, previous)).hexdigest()
    ensure(inverse == 'cea071606d173007ca8ce8acde05c74748e3243d2c4091390aedcdfcef550ed9', 'Unexpected inverse source')
    ensure(digest(source_path) == 'dd0054b6f15f1bca07c886217a8197796138a951223fb8bde935a23717bbe3c2', 'Unexpected current source')

    identity = read(B / 'fixed-package-identity.json')
    build_root = Path(identity['buildRoot'])
    build_files = []
    for entry in identity['criticalIdentity'] + identity['scripts']:
        path = build_root / entry['path']
        actual = digest(path)
        ensure(entry['matches'] and actual == entry['diskSHA256'] == entry['httpSHA256'], f'Build identity mismatch: {entry["path"]}')
        build_files.append({'path': relative(path), 'sha256': actual})
    ensure(len(identity['scripts']) == identity['observedJavaScriptCount'] == 12, 'Expected 12 observed JavaScript inputs')
    main_url = identity['actualMainURL']
    ensure(values[20]['EXECUTED_IDENTITY']['mainRequests'][0]['name'] == main_url, 'B20 main mismatch')
    ensure(values[35]['ENTRY_IDENTITY']['mainRequests'][0]['name'] == main_url, 'B35 main mismatch')
    final = values[41]['FINAL_DIAGNOSTICS']
    ensure(main_url in [entry['name'] for entry in final['scripts']], 'B41 main mismatch')

    state = {number: value['STATE'] for number, value in values.items() if 'STATE' in value}
    ensure(state[19]['route'] == state[21]['route'] and state[19]['trip'] == state[21]['trip'], 'Original planned trip changed across package fix')
    ensure(state[21]['batchIds'] == ['v2-road-268'] and state[21]['cashCents'] == 10000, 'Original planned balance/order mismatch')
    ensure('本批签约 2/2格 · 速度 ×1.00 · 车辆收益 +0%' in state[22]['labels'], 'Missing real planned capacity display')
    ensure(values[23]['VIEWPORT'] == {'width': 315, 'height': 851, 'dpr': 2, 'canvas': [630, 1702]}, 'B23 viewport mismatch')
    for number in (22, 23, 24):
        ensure(state[number]['route']['phase'] == 'planned' and state[number]['trip']['gameSeconds'] == 0, 'Planned observation advanced route')

    expected_phases = {25: 'travelling', 26: 'pickup', 27: 'service', 28: 'ready', 29: 'ready', 30: 'travelling', 31: 'finished'}
    for number, phase in expected_phases.items():
        ensure(state[number]['route']['phase'] == phase, f'B{number} phase mismatch')
    ensure(state[26]['trip']['orders'][0]['picked'] is False, 'Pickup happened before manual action')
    ensure(state[27]['trip']['orders'][0]['picked'] is True, 'Manual pickup did not mark order')
    ensure(state[28]['route']['position'] == state[29]['route']['position'], 'Ready position moved')
    ensure(state[28]['trip']['gameSeconds'] == state[29]['trip']['gameSeconds'], 'Ready clock advanced')
    ready_hold = state[29]['at'] - state[28]['at']
    ensure(ready_hold == 122982, 'Unexpected observed ready hold')
    ensure(state[31]['cashCents'] == 12000 and state[31]['heroCompletedOrders'] == 1 and state[31]['batchIds'] == [], 'Delivery completion mismatch')
    ensure(state[31]['trip']['orders'][0]['delivered'] is True, 'Delivery not complete')

    samples = values[31]['MOTION_SAMPLES']
    legs = values[25]['REAL_ROUTE_LEGS']
    phases = []
    for sample in samples:
        phase = [sample['phase'], sample['cursor']]
        if not phases or phases[-1] != phase:
            phases.append(phase)
    moving = [sample for sample in samples if sample['phase'] == 'travelling']
    pairs = [(left, right) for left, right in zip(samples, samples[1:])
             if left['phase'] == right['phase'] == 'travelling' and left['cursor'] == right['cursor']]
    segments = [(start, end) for leg in legs for start, end in zip(leg['points'], leg['points'][1:])]
    motion = {
        'sampleCount': len(samples), 'travellingSampleCount': len(moving), 'phaseSequence': phases,
        'maxObservedMovingStepMetres': max(math.dist(left['position'], right['position']) for left, right in pairs),
        'maxMovingSampleGapMs': max(right['at'] - left['at'] for left, right in pairs),
        'maxSampleDistanceFromActualRoutePolylineMetres': max(min(point_segment_distance(sample['position'], start, end) for start, end in segments) for sample in samples),
        'allSamplesFollow': all(sample['follow'] for sample in samples),
        'maxViewOffsetCenteringResidualDesignUnits': max(math.hypot(sample['offset'][0] + sample['scale'] * sample['position'][0], sample['offset'][1] + sample['scale'] * sample['position'][1]) for sample in samples),
        'actorNodeActiveSampleCount': sum(sample['actor']['active'] for sample in samples),
        'readyObservedHoldMs': ready_hold, 'readyPositionUnchanged': True, 'readyGameSecondsUnchanged': True,
    }
    recorded_motion = read(B / 'motion-analysis.json')
    for key, actual in motion.items():
        expected = recorded_motion[key]
        ensure(math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9) if isinstance(actual, (int, float)) else actual == expected, f'Motion analysis mismatch: {key}')
    motion['scope'] = 'Saved 100ms public projection samples and offline route arithmetic; not every GPU frame or physical-device FPS. VehicleTopView probe inactive in all samples; screen marker separately visible in saved captures.'

    performance = values[32]['ACTIVE_PERFORMANCE']
    intervals = performance['rawFrameIntervalsMs']
    ensure(len(intervals) == performance['frameIntervalCount'] == 404, 'Active interval count mismatch')
    ensure(math.isclose(sum(intervals) / len(intervals), performance['meanMs'], abs_tol=1e-9), 'Active interval mean mismatch')
    ensure(max(intervals) == performance['maxMs'], 'Active interval maximum mismatch')
    ensure(sum(value > 50 for value in intervals) == performance['over50Ms'] == 0, 'Active >50ms count mismatch')
    for key, percentile in (('p50Ms', 0.5), ('p95Ms', 0.95), ('p99Ms', 0.99)):
        ensure(sorted(intervals)[min(len(intervals)-1, int(len(intervals)*percentile))] == performance[key], f'Active percentile mismatch: {key}')

    ensure(state[33]['view']['follow'] is False and state[34]['view']['follow'] is True, 'Pan/locate follow mismatch')
    reload_fields = ('route', 'trip', 'cashCents', 'heroCompletedOrders', 'npcCompletedOrders', 'vehicles', 'riders', 'batchIds', 'view')
    for field in reload_fields:
        ensure(state[34][field] == state[36][field], f'Nonzero reload mismatch: {field}')
    ensure(state[36]['cashCents'] == 12000 and state[36]['heroCompletedOrders'] == 1, 'Nonzero reload balance mismatch')
    ensure(state[37]['supplyOpen'] and state[37]['cashCents'] == 12000, 'Supply menu mismatch')
    ensure(state[38]['cashCents'] == state[39]['cashCents'] == 11900, 'Water debit mismatch')
    ensure(state[38]['trip']['action']['kind'] == 'water' and state[38]['trip']['action']['source'] == 'purchase' and state[38]['trip']['action']['costCents'] == 100, 'Water purchase action mismatch')
    ensure(state[39]['trip']['action'] is None and state[39]['trip']['stamina'] == 100 and state[39]['trip']['supplySpentCents'] == 100, 'Water completion mismatch')
    ledger = values[40]['LEDGER']
    ensure([(entry['category'], entry['amountCents']) for entry in ledger['entries']] == [('hero_ordinary', 2000), ('supply_purchase', -100)], 'Ledger entries mismatch')
    ensure(10000 + sum(entry['amountCents'] for entry in ledger['entries']) == state[40]['cashCents'] == final['cashCents'] == 11900, 'Final ledger reconciliation mismatch')
    ensure(final['route']['phase'] == 'finished' and final['heroCompletedOrders'] == 1 and final['batchIds'] == [], 'Final state mismatch')

    closure = read(B / 'browser-close-receipt.json')
    closed = json.loads(closure['close']['output'])
    closed_readback = json.loads(closure['readback']['output'])
    ensure(closure['close']['exit_code'] == closure['readback']['exit_code'] == 0, 'Browser close command failed')
    ensure(closed['id'] == identity['sameSession'] == closure['sessionId'] == closed_readback[0]['id'], 'Browser lineage mismatch')
    ensure(closed['state'] == closed_readback[0]['state'] == 'closed', 'Browser not closed')
    ensure((B / 'report.md').read_bytes() == (B / 'red-checkpoint-report.md').read_bytes(), 'Historical RED reports diverged')
    ensure((B / 'test-results.json').read_bytes() == (B / 'red-checkpoint-test-results.json').read_bytes(), 'Historical RED JSON diverged')

    regression = {}
    for name, expected in (('batch-load-red.log', {'tests': 4, 'pass': 1, 'fail': 3, 'skipped': 0}),
                           ('batch-load-green.log', {'tests': 4, 'pass': 4, 'fail': 0, 'skipped': 0}),
                           ('a/v2-suite-final-complete.log', {'tests': 95, 'pass': 95, 'fail': 0, 'skipped': 0})):
        path = TESTING / name
        actual = tap_totals(path)
        ensure(actual == expected, f'Existing TAP log mismatch: {name}')
        regression[name] = {'path': relative(path), 'sha256': digest(path), 'recordedTotals': actual, 'rerunDuringSupplement': False}

    summaries = []
    for number in range(20, 42):
        value = state.get(number)
        summary = {'number': number, 'path': relative(paths[number]), 'sha256': digest(paths[number]),
                   'recordedAt': records[number]['recordedAt'], 'tags': list(values[number])}
        if value:
            summary['state'] = {key: value[key] for key in ('page', 'route', 'view', 'cashCents', 'heroCompletedOrders', 'batchIds', 'lastError')}
            summary['trip'] = {key: value['trip'][key] for key in ('gameSeconds', 'stamina', 'supplySpentCents', 'action')}
        summaries.append(summary)

    audit = {
        'task': 'CODEX-B-EXISTING-EVIDENCE-AUDIT-1107', 'result': 'PASS',
        'verifiedAt': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'scope': 'Offline integrity/arithmetic/record consistency audit only; no new browser or gameplay test, no service/source/price/save mutation.',
        'protectedArtifactCount': len(protected_checks), 'protectedMismatches': [],
        'originalBFileCount': len(original_files), 'originalBManifest': relative(manifest_path),
        'recordCount': len(records), 'postFixRecordCount': 22,
        'nonJsonDebugTextPreserved': [{'record': relative(paths[number]), 'tag': key, **value}
                                     for number in (4, 5) for key, value in values[number].items()
                                     if key in ('TOUCH_METHODS', 'TOUCH_HANDLE')],
        'screenshotCount': len(captures), 'postFixScreenshotCount': sum(int(Path(entry['record']).name[:2]) >= 20 for entry in captures),
        'captureSHA256Checks': captures,
        'source': {'path': relative(source_path), 'sha256': digest(source_path), 'fixedArgumentCount': 1, 'inverseSingleArgumentSHA256': inverse},
        'buildFiles': list({entry['path']: entry for entry in build_files}.values()),
        'motionRecomputed': motion,
        'activePerformanceRecomputed': {key: performance[key] for key in ('frameIntervalCount', 'meanMs', 'p50Ms', 'p95Ms', 'p99Ms', 'maxMs', 'over50Ms', 'phaseSampleIntervalMs', 'phaseBoundaryPrecision', 'longTasks', 'actionMarks', 'scope')},
        'normalNonzeroReload': {'sameFields': list(reload_fields), 'before': relative(paths[34]), 'reload': relative(paths[35]), 'after': relative(paths[36]), 'splashScreenshotOnlyAtB35': True, 'cashCents': 12000, 'heroCompletedOrders': 1},
        'ledger': ledger, 'final': final, 'closedBrowser': closed,
        'existingRegressionLogs': regression, 'postFixRecords': summaries,
    }
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps({'scope': 'Existing top-level B records/captures/reports, frozen before supplement; never overwrite originals.', 'files': original_files}, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'evidence-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'result': 'PASS', 'protectedArtifacts': len(protected_checks), 'unchangedOriginalBFiles': len(original_files),
                      'postFixRecords': 22, 'verifiedCaptureSHA256': len(captures), 'postFixCaptures': audit['postFixScreenshotCount'],
                      'observedBuildScripts': len(identity['scripts']), 'motionSamples': len(samples), 'activeRAFIntervals': len(intervals),
                      'readyHoldMs': ready_hold, 'finalCashCents': final['cashCents'], 'heroCompletedOrders': final['heroCompletedOrders'],
                      'browserState': closed['state'], 'audit': relative(OUT / 'evidence-audit.json')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
