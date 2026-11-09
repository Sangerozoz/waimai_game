"""Read-only checks of this delivery's frozen evidence and served package."""
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
baseline = read(HERE / "inputs-before.json")["files"]
assert sha(HERE / "inputs-before.json") == receipt["inputBaselineSHA256"]
approved = receipt["approvedSources"]
drift = {name for name, digest in baseline.items() if sha(ROOT / name) != digest}
assert drift == set(approved), sorted(drift)
assert len(drift) == 6
for name, digest in {**approved, **receipt["newTests"]}.items():
    assert sha(ROOT / name) == digest, name

for name, expected in receipt["checks"].items():
    check = read(HERE / name)
    assert check["exitCode"] == 0, name
    assert sha(HERE / check["log"]) == check["logSHA256"], name
    if "counts" in expected:
        assert check["counts"] == expected["counts"], name
        for key, number in expected["counts"].items():
            assert re.search(rf"^# {key} {number}$", (HERE / check["log"]).read_text(), re.M), (name, key)
    assert check["inputDrift"] == [], name
    for path, digest in approved.items():
        assert check["inputSHA256"][path] == digest, (name, path)
    if name == "default-regression-followup-receipt.json":
        for path, digest in receipt["newTests"].items():
            assert check["inputSHA256"][path] == digest, (name, path)

for name, digest in receipt["reviewEvidence"].items():
    assert sha(HERE / name) == digest, name
review = read(HERE / "backend-review-result.json")
assert review["spec"] == review["codeQuality"] == "PASS"
assert review["critical"] == review["important"] == 0
for name, digest in review["sourceSHA256"].items():
    assert sha(ROOT / name) == digest, name

build = read(HERE / "build-receipt.json")
assert build["success"] and build["creatorExitCode"] == 36
assert build["inputDrift"] == []
assert sha(HERE / build["log"]) == build["logSHA256"]
for name, row in read(HERE / "build-inputs-before.json").items():
    assert sha(ROOT / name) == row["sha256"], name
output = read(HERE / "build-output-manifest.json")
for name, row in output["files"].items():
    assert sha(Path(output["root"]) / name) == row["sha256"], name

browser = read(HERE / "browser/receipt.json")
assert browser["status"] == "PASS_ISOLATED_EMERGENCY_LOAN_FLOW"
assert browser["realUserBrowserOrSaveAccess"] is False
assert sha(ROOT / browser["fixturePath"]) == browser["fixtureSHA256"]
for name, digest in browser["artifacts"].items():
    assert sha(HERE / "browser" / name) == digest, name
assert browser["sessionClosed"]
assert browser["originalInputDirectCreatorRestore"].startswith("BLOCKED_")
original = read(ROOT / browser["fixturePath"])["fixtures"]["signedZeroQuota"]
adapted = read(HERE / "browser" / browser["browserInput"])
adapted["route"]["mapKey"] = original["route"]["mapKey"]
assert adapted == original
final_slot = read(HERE / "browser" / "final-isolated-slot.json")
state = final_slot["dispatch"]["economy"]["state"]
assert state["heroEmergencyLoan"]["active"] is False
assert state["riders"][0]["vehicleId"] == "starter-1"
assert len(state["vehicles"]) == 1
assert state["cashCents"] == 10000
assert state["ledger"]["opening"]["balanceCents"] + sum(row["amountCents"] for row in state["ledger"]["entries"]) == state["cashCents"]
assert len({row["id"] for row in state["ledger"]["entries"]}) == len(state["ledger"]["entries"])

old_resources = ROOT / "delivery-game/build/v2-hero-car-reserve-1107/assets/resources"
new_resources = Path(output["root"]) / "assets/resources"
old_files = {str(path.relative_to(old_resources)): sha(path) for path in old_resources.rglob("*") if path.is_file()}
new_files = {str(path.relative_to(new_resources)): sha(path) for path in new_resources.rglob("*") if path.is_file()}
assert old_files == new_files
assert len(old_files) == 524

deployment = read(HERE / "preview-deployment-receipt.json")
assert set(deployment["ports"]) == {"4182", "4196"}
http_count = 0
for port, row in deployment["ports"].items():
    for item in row["checks"]:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/{item['path']}", timeout=10) as response:
            assert response.status == 200
            digest = hashlib.sha256(response.read()).hexdigest()
        assert digest == item["sha256"] == output["files"][item["path"]]["sha256"]
        http_count += 1

ledger = read(ROOT / "docs/reviews/2026-11-05-game-development/feedback-ledger.json")
assert len(ledger["userIssues"]) == 40 and ledger["summary"]["closedCount"] == 0
assert len(ledger["engineeringFindings"]) == 9
e09 = next(row for row in ledger["engineeringFindings"] if row["id"] == "E09")
assert e09["preventionVerified"] and e09["existingLockedSaveRescueImplemented"]
assert e09["recoveryProposal"]["productionImplemented"]
assert ledger["integration"]["servedRoot"] == build["outputDirectory"]

print(json.dumps({
    "capturedAt": datetime.now(timezone.utc).isoformat(),
    "status": "PASS_RESTRICTED_EMERGENCY_LOAN_DELIVERY",
    "inputBaselineFiles": len(baseline),
    "approvedSourceChanges": len(drift),
    "otherBaselineFilesUnchanged": len(baseline) - len(drift),
    "newTests": len(receipt["newTests"]),
    "outputFilesMatched": len(output["files"]),
    "httpFilesFreshlyMatched": http_count,
    "isolatedRecoveryFlow": True,
    "realUserBrowserOrSaveAccess": False,
    "browserInput": "mapKey-only packed transport adaptation",
    "originalSourceFixtureDirectCreatorRestore": "BLOCKED; original bytes and failure retained",
    "packedResourceFilesUnchangedFromPreviousPreview": len(old_files),
    "finalIsolatedCashCents": state["cashCents"],
    "finalIsolatedPermanentCars": len(state["vehicles"]),
    "formalUserIssuesClosed": 0,
    "wholeProductAccepted": False,
}, ensure_ascii=False, indent=2))
