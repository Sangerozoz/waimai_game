"""Read-only evidence and HTTP audit; never starts the game or reads user storage."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


receipt = read(HERE / "integration-receipt.json")
expected = {row["path"]: row["afterSHA256"] for row in receipt["approvedChanges"]}
baseline = read(ROOT / receipt["originalProtection"]["path"])
assert sha(ROOT / receipt["originalProtection"]["path"]) == receipt["originalProtection"]["sha256"]
drift = [name for name, row in baseline["files"].items() if sha(ROOT / name) != row["sha256"]]
assert set(drift) == set(expected), drift
for name, digest in expected.items():
    assert sha(ROOT / name) == digest, name
for row in receipt["newFiles"]:
    assert sha(ROOT / row["path"]) == row["sha256"], row["path"]

author_path = ROOT / receipt["authorReceipt"]
assert sha(author_path) == receipt["authorReceiptSHA256"]
author = read(author_path)
for name, digest in author["artifactFiles"].items():
    assert sha(author_path.parent / name) == digest, name
for row in author["sources"]:
    assert sha(ROOT / row["candidate"]) == sha(ROOT / row["productionTarget"])
green = read(author_path.parent / "green-root-fix-receipt.json")
a36_drift = [name for name, digest in green["a36Before"].items() if sha(ROOT / name) != digest]
assert set(a36_drift) == {row["productionTarget"] for row in author["sources"]}
a_dir = ROOT / "docs/balance/2026-11-06-balance-round-01/a"
a_manifest_path = a_dir / "artifact-manifest.json"
assert sha(a_manifest_path) == green["protectedBefore"][str(a_manifest_path.relative_to(ROOT))]
a_manifest = read(a_manifest_path)
for name, digest in a_manifest["files"].items():
    digest = digest if isinstance(digest, str) else digest["sha256"]
    assert sha(a_dir / name) == digest, name

tests = read(HERE / "default-regression-receipt.json")
assert tests["exitCode"] == 0
assert tests["counts"] == {"tests": 113, "pass": 113, "fail": 0, "cancelled": 0, "skipped": 0, "todo": 0}
assert sha(HERE / "default-regression.log") == tests["logSHA256"]
assert re.search(r"^# tests 113$", (HERE / "default-regression.log").read_text(), re.M)
typecheck = read(HERE / "typecheck-receipt.json")
assert typecheck["exitCode"] == 0
assert sha(HERE / "typecheck.log") == typecheck["logSHA256"]
build = read(HERE / "build-receipt.json")
assert build["success"] and build["creatorExitCode"] == 36
assert sha(HERE / build["log"]) == build["logSHA256"]
inputs = read(HERE / "build-inputs-before.json")
for name, row in inputs.items():
    assert sha(ROOT / name) == row["sha256"], name
outputs = read(HERE / "build-output-manifest.json")
for name, row in outputs["files"].items():
    assert sha(Path(outputs["root"]) / name) == row["sha256"], name

deployment = read(HERE / "preview-deployment-receipt.json")
assert set(deployment["ports"]) == {"4182", "4196"}
http_count = 0
for port, row in deployment["ports"].items():
    assert len(row["checks"]) == 15
    for item in row["checks"]:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/{item['path']}", timeout=10) as response:
            assert response.status == 200
            digest = hashlib.sha256(response.read()).hexdigest()
        assert digest == item["sha256"] == outputs["files"][item["path"]]["sha256"]
        http_count += 1

ledger = read(ROOT / "docs/reviews/2026-11-05-game-development/feedback-ledger.json")
assert len(ledger["userIssues"]) == 40 and ledger["summary"]["closedCount"] == 0
assert len(ledger["engineeringFindings"]) == 9
e09 = next(row for row in ledger["engineeringFindings"] if row["id"] == "E09")
assert e09["preventionVerified"] and not e09["closed"] and not e09["existingLockedSaveRescueImplemented"]
assert ledger["integration"]["servedRoot"] == build["outputDirectory"]
for target in re.findall(r"\]\(([^)]+)\)", (HERE / "report.md").read_text()):
    assert (HERE / target).exists(), target

print(json.dumps({
    "capturedAt": datetime.now(timezone.utc).isoformat(),
    "status": "PASS_PREVENTION_INTEGRATION_ONLY",
    "originalProtectionFiles": len(baseline["files"]),
    "approvedChangedFiles": len(drift),
    "otherProtectedUnchanged": len(baseline["files"]) - len(drift),
    "retainedAuthorArtifacts": len(author["artifactFiles"]),
    "historicA36ApprovedSourceChanges": len(a36_drift),
    "historicAArtifactsUnchanged": len(a_manifest["files"]),
    "defaultTests": 113,
    "typecheckExit": 0,
    "creatorExit": 36,
    "buildInputsUnchanged": len(inputs),
    "outputFilesMatched": len(outputs["files"]),
    "httpFilesFreshlyMatched": http_count,
    "formalUserIssuesClosed": 0,
    "existingLockedSaveRescued": False,
    "gameOrUserStorageAccess": False,
}, ensure_ascii=False, indent=2))
