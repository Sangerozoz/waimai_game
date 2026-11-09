#!/usr/bin/env python3
"""Deliver the one real density candidate with explicit failed protection gates."""
import datetime
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'compact-pair-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    record_path = HERE / 'delivery-record.json'
    if record_path.exists():
        raise SystemExit('Delivery record exists; preserve subsequent user/PM work.')
    preview = HERE / 'preview'
    references = HERE / 'references'
    preview.mkdir(exist_ok=True)
    references.mkdir(exist_ok=True)
    source_a = OLD / 'native/A/native.png'
    source_b = OLD / 'native/B/native.png'
    native = HERE / 'native/A-v2-api.png'
    provenance = read(HERE / 'native/provenance.json')
    review = read(OLD / 'user-review-001.json')
    if sha(native) != provenance['nativeSHA256']:
        raise SystemExit('API native changed; no replacement.')
    shutil.copyfile(source_b, references / 'B-v1-native.png')
    a = Image.open(source_a).convert('RGB')
    b = Image.open(source_b).convert('RGB')
    edited = Image.open(native).convert('RGB')
    if edited.size != (1536, 1024):
        raise SystemExit('Native size mismatch; no interpolation.')
    comparison = Image.new('RGB', (3072, 1024))
    comparison.paste(a, (0, 0))
    comparison.paste(edited, (1536, 0))
    comparison.save(preview / 'A-before-after-api.png')
    small = comparison.copy()
    small.thumbnail((1536, 512))
    small.save(preview / 'A-before-after-overview.jpg', quality=94)
    edited.crop((1180, 0, 1536, 540)).save(preview / 'east-block-1x.png')
    edited.crop((0, 850, 750, 1024)).save(preview / 'frontage-1x.png')
    candidate_pair = Image.new('RGB', (3008, 1024))
    candidate_pair.paste(edited.crop((0, 0, 1504, 1024)), (0, 0))
    candidate_pair.paste(b.crop((32, 0, 1536, 1024)), (1504, 0))
    candidate_pair.save(preview / 'pair-v2-api-candidate-not-approved.png')
    pair_small = candidate_pair.copy()
    pair_small.thumbnail((1504, 512))
    pair_small.save(preview / 'pair-v2-overview-not-approved.jpg', quality=94)
    protected = read(HERE / 'protected-inputs.json')
    changed_sources = [p for p, value in protected.items() if sha(Path(p)) != value]
    new_old_files = [str(p) for p in OLD.rglob('*') if p.is_file() and str(p) not in protected]
    diff = read(HERE / 'analysis/raw-difference.json')
    body = {
        'schemaVersion': 1, 'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'real-density-candidate-produced-protection-composite-blocked-not-integrated',
        'scope': 'A urban-core density only; no new B request, no other region, no changes to old version or game.',
        'parentRequest': '../planning/density-revision-request.md',
        'acceptedOldProperties': review['acceptedByUser'],
        'actualProductionCommands': read(HERE / 'execution-commands.json'),
        'native': {'path': 'native/A-v2-api.png', 'sha256': sha(native), 'bytes': native.stat().st_size,
                   'actualSize': list(edited.size), 'model': provenance['model'],
                   'imageProvider': 'openai-api', 'agentProvider': provenance['agentProvider'],
                   'agentModel': provenance['agentModel'], 'qualityRequested': provenance['quality'],
                   'qualityReturned': provenance['qualityReturned'],
                   'elapsedSeconds': provenance['elapsedSeconds'], 'originalReturnedBytesPreserved': True,
                   'requestCount': 1, 'automaticRetries': 0},
        'inputs': {'A': {'path': str(source_a), 'sha256': sha(source_a)},
                   'guide': {'path': 'inputs/edit-guide.png', 'sha256': sha(HERE / 'inputs/edit-guide.png'),
                             'role': 'PIL allowed-area annotation, not artwork'},
                   'mask': {'path': 'inputs/edit-mask.png', 'sha256': sha(HERE / 'inputs/edit-mask.png'),
                            'alphaConvention': 'transparent editable, opaque protected'},
                   'prompt': {'path': 'prompt.txt', 'sha256': sha(HERE / 'prompt.txt')},
                   'productionCode': {'path': 'generate_density.py', 'sha256': sha(HERE / 'generate_density.py')}},
        'densityVisualObservation': ['Eastern oversized garden replaced by a higher mixed-use rear block and lower connected commercial frontage.',
                                     'Narrow infill added in the northern gap, using the original viewpoint rather than shrinking old buildings.',
                                     'Foreground lawns now contain continuous low shop ranges and small courts; not merely extra trees or signs.'],
        'maskEndpointObservation': {'clientFieldVerifiedBeforeRequest': True,
                                    'actualRequestAcceptedMaskField': True,
                                    'nonMaskPixelsHardPreserved': diff['endpointHardPreservedNonMaskPixels'],
                                    'outsideMaskChangedPixels': diff['outsideMaskChangedPixels'],
                                    'east64ChangedPixels': diff['east64ChangedPixels'],
                                    'exactInternalReasonEstablished': False,
                                    'rawDiffRecord': 'analysis/raw-difference.json'},
        'protectedComposite': {'candidateInspectionOnly': 'analysis/protected-preview-unaccepted.png',
                               'useForDeliveryOrRuntime': False,
                               'failedReason': 'Visual inspection shows the original hard mask cuts the east curved commercial frontage/steps and affects some foreground infill boundaries. A mechanically protected image is not acceptable if it truncates new architecture.',
                               'outlineEvidence': 'analysis/mask-outline-on-api.png',
                               'silhouetteClippingAcceptedAsFix': False,
                               'newMaskOrImageRetryAttempted': False},
        'BReuse': {'source': str(source_b), 'copy': 'references/B-v1-native.png',
                   'sourceSHA256': sha(source_b), 'copySHA256': sha(references / 'B-v1-native.png'),
                   'byteForByte': (source_b.read_bytes() == (references / 'B-v1-native.png').read_bytes()),
                   'newAPIRequest': False, 'cityCentreDensityApproved': False},
        'oldRoads': {'graphSHA256': sha(OLD / 'navigation/graph.json'),
                     'frozenGraphSHA256': review['frozenInputs']['roadGraph_SHA256'],
                     'oldTiledSHA256': sha(OLD / 'tiled/compact-pair.tmj'),
                     'frozenTiledSHA256': review['frozenInputs']['Tiled_SHA256'],
                     'nodes': 11, 'edges': 12, 'offsetB': [1472, 0], 'coreSeamX': 1504,
                     'geometryWrittenOrRedrawn': False,
                     'oldNavigationEvidenceReusedAsNewPass': False},
        'candidatePreview': {'beforeAfter': 'preview/A-before-after-api.png',
                              'beforeAfterHalfSizeOverview': 'preview/A-before-after-overview.jpg',
                              'pairOverview': 'preview/pair-v2-overview-not-approved.jpg',
                              'pairNativePixelComposite': 'preview/pair-v2-api-candidate-not-approved.png',
                              'oneToOneCrops': ['preview/east-block-1x.png', 'preview/frontage-1x.png'],
                              'newTiledOrNavigationPromotion': False,
                              'reason': 'Density is visible, but a road/seam/existing-building pixel-preserving complete-building display candidate has not passed; do not integrate the raw or clipped composite as approved.'},
        'protection': {'protectedFileCount': len(protected), 'changedSources': changed_sources,
                       'newFilesUnderReadonlyOldVersion': new_old_files,
                       'sourcesUnchanged': not changed_sources and not new_old_files,
                       'snapshots': 'protected-inputs.json'},
        'notPerformed': ['B generation', 'second A image request', 'runtime integration or new navigation claim',
                         'repeated native Tiled repaint attempts', 'game tests/typecheck/regression/FPS',
                         'save/order operations', 'commit/push', 'provider/account/global permission changes'],
        'userAcceptedNewDensity': False, 'wholeCityComplete': False,
        'handoff': 'Return bounded write lease. Await review of the real density edit and explicit decision on protection-mask limitations; no further generation.'}
    save(record_path, body)
    print(json.dumps({'status': body['status'], 'nativeSize': list(edited.size), 'nativeSHA256': sha(native),
                      'BByteForByteUnchanged': body['BReuse']['byteForByte'],
                      'sourceProtectionUnchanged': body['protection']['sourcesUnchanged'],
                      'newTiledOrNavigationPromotion': False, 'extraImageRequests': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
