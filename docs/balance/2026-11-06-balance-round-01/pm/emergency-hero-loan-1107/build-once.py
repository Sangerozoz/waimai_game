"""Build the frozen candidate once and retain failed attempts without overwriting."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
tag = sys.argv[1]
if not re.fullmatch(r"[a-z0-9-]+", tag):
    raise ValueError("Invalid build attempt name")
log = HERE / (tag + ".log")
attempt_receipt = HERE / (tag + "-receipt.json")
if log.exists() or attempt_receipt.exists():
    raise FileExistsError("Build attempts cannot overwrite prior evidence")
frozen = json.loads((HERE / "backend-review-request.json").read_text())["sourceSHA256"]
frozen.update(json.loads((HERE / "ui/review-followup-request.json").read_text())["files"])
for name, digest in frozen.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
for name in ["default-regression", "ui-regression", "typecheck"]:
    check = json.loads((HERE / (name + "-receipt.json")).read_text())
    assert check["exitCode"] == 0 and not check["inputDrift"], name
    for name, digest in frozen.items():
        assert check["inputSHA256"][name] == digest, name
keys = json.loads((HERE.parent / "softlock-prevention-1107/build-inputs-before.json").read_text())


def fingerprints():
    return {name: {"sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest(),
                   "bytes": (ROOT / name).stat().st_size} for name in keys}


before = fingerprints()
inputs_path = HERE / "build-inputs-before.json"
if inputs_path.exists():
    assert json.loads(inputs_path.read_text()) == before
else:
    inputs_path.write_text(json.dumps(before, ensure_ascii=False, indent=2) + "\n")
output_root = ROOT / "delivery-game/build/v2-emergency-hero-loan-1107"
command = ["/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator",
           "--project", str(ROOT / "delivery-game"), "--build", "configPath=" + str(HERE / "build-config.json")]
started = datetime.now(timezone.utc).isoformat()
with log.open("w") as output:
    run = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
drift = [name for name, row in fingerprints().items() if row != before[name]]
files = {str(p.relative_to(output_root)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
         for p in output_root.rglob("*") if p.is_file()} if output_root.exists() else {}
text = log.read_text(errors="replace")
finished = [line for line in text.splitlines() if "build Task (v2-emergency-hero-loan-1107) Finished" in line]
success = run.returncode == 36 and bool(finished) and "index.html" in files and not drift
data = {"command": command, "startedAt": started, "finishedAt": datetime.now(timezone.utc).isoformat(),
        "creatorExitCode": run.returncode, "success": success, "successEvidence": finished,
        "buildInputCount": len(before), "inputDrift": drift,
        "outputDirectory": str(output_root.relative_to(ROOT)), "outputFiles": len(files),
        "outputJavaScriptFiles": sum(name.endswith(".js") for name in files),
        "log": log.name, "logSHA256": hashlib.sha256(log.read_bytes()).hexdigest(),
        "realUserBrowserOrSaveAccess": False}
attempt_receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
if success:
    (HERE / "build-receipt.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    (HERE / "build-output-manifest.json").write_text(json.dumps({"capturedAt": data["finishedAt"], "root": str(output_root), "files": files}, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(data, ensure_ascii=False, indent=2))
print(text[-2500:])
sys.exit(0 if success else 1)
