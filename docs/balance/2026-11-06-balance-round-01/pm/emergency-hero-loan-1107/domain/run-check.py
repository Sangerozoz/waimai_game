"""Capture each authorized narrow runner invocation without replacing earlier evidence."""
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

root = pathlib.Path.cwd()
out = pathlib.Path(__file__).resolve().parent
label = sys.argv[1]
command = ['node', 'delivery-game/tests/run-v2.cjs', *sys.argv[2:]]
log = out / (label + '.log')
receipt = out / (label + '.json')
if log.exists() or receipt.exists():
    raise SystemExit('Evidence already exists: ' + label)
sources = [
    'delivery-game/assets/scripts/domain/V2EconomySession.ts',
    'delivery-game/assets/scripts/domain/V2FleetSession.ts',
    'delivery-game/assets/scripts/domain/V2DispatchSession.ts',
    'delivery-game/assets/scripts/map-sample/V2GameSession.ts',
    'delivery-game/assets/scripts/map-sample/V2RuntimeController.ts',
    'delivery-game/tests/product-regression-1106/emergency-hero-loan.test.cjs',
]
hashes = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sources}
scratch_before = set(pathlib.Path(tempfile.gettempdir()).glob('delivery-v2-test-*'))
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('xb') as stream:
    result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, cwd=root)
scratch_remaining = set(pathlib.Path(tempfile.gettempdir()).glob('delivery-v2-test-*')) - scratch_before
record = dict(command=command, cwd=str(root), startedAt=started,
              finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              exitCode=result.returncode, sourceSHA256=hashes,
              logSHA256=hashlib.sha256(log.read_bytes()).hexdigest(),
              newRunnerScratchRemaining=sorted(map(str, scratch_remaining)))
receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(label=label, exitCode=result.returncode, log=str(log),
                      newRunnerScratchRemaining=record['newRunnerScratchRemaining'])))
print('\n'.join(log.read_text().splitlines()[-35:]))
raise SystemExit(result.returncode)
