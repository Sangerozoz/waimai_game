"""Run a PM check once, retaining full output, exit status and input identity."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
name, *command = sys.argv[1:]
if command and command[0] == "--":
    command.pop(0)
if not re.fullmatch(r"[a-z0-9-]+", name) or not command:
    raise ValueError("Expected a receipt name followed by a command")
log = HERE / (name + ".log")
receipt = HERE / (name + "-receipt.json")
if log.exists() or receipt.exists():
    raise FileExistsError("Prior check evidence is immutable; select a new name")
paths = set(json.loads((HERE / "inputs-before.json").read_text())["files"])
paths.update([
    "delivery-game/tests/product-regression-1106/emergency-hero-loan.test.cjs",
    "delivery-game/tests/product-regression-1106/emergency-loan-runtime.test.cjs",
    "delivery-game/tests/emergency-loan-ui.test.cjs",
])


def fingerprints():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(paths)}


before = fingerprints()
started = datetime.now(timezone.utc).isoformat()
with log.open("w") as output:
    run = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
after = fingerprints()
text = log.read_text()
counts = {key: int(value) for key, value in re.findall(r"^# (tests|pass|fail|cancelled|skipped|todo) (\d+)$", text, re.M)}
drift = [name for name in before if after[name] != before[name]]
data = {
    "startedAt": started,
    "finishedAt": datetime.now(timezone.utc).isoformat(),
    "command": command,
    "cwd": str(ROOT),
    "exitCode": run.returncode,
    "counts": counts,
    "log": log.name,
    "logSHA256": hashlib.sha256(log.read_bytes()).hexdigest(),
    "inputCount": len(before),
    "inputSHA256": before,
    "inputDrift": drift,
    "realUserBrowserOrSaveAccess": False,
}
receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: value for key, value in data.items() if key != "inputSHA256"}, ensure_ascii=False, indent=2))
print(text[-1200:])
sys.exit(run.returncode if run.returncode else int(bool(drift)))
