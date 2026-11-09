"""Run a short isolated browser script and retain its result and images."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
session = json.loads((HERE / "session.json").read_text())
label = sys.argv[1]
if not re.fullmatch(r"[a-z0-9-]+", label):
    raise ValueError("Invalid evidence label")
script = HERE / (label + ".js")
result_path = HERE / (label + "-result.json")
receipt_path = HERE / (label + "-receipt.json")
if result_path.exists() or receipt_path.exists():
    raise FileExistsError("Do not overwrite a prior browser action")
command = ["bb", "browser-automation", "run", session["session"], "--script-file", str(script),
           "--script-host", session["host"], "--timeout-ms", "30000", "--json"]
started = datetime.now(timezone.utc).isoformat()
run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
result_path.write_text(run.stdout)
if run.stderr:
    (HERE / (label + "-stderr.log")).write_text(run.stderr)
try:
    result = json.loads(run.stdout)
except json.JSONDecodeError:
    result = {"unparsedOutput": run.stdout}
images = {}
for index, image in enumerate(result.get("images", []), 1):
    destination = HERE / (label + f"-{index}.jpg")
    shutil.copyfile(image["path"], destination)
    images[destination.name] = hashlib.sha256(destination.read_bytes()).hexdigest()
receipt = {"startedAt": started, "finishedAt": datetime.now(timezone.utc).isoformat(),
           "session": session["session"], "command": command, "exitCode": run.returncode,
           "scriptSHA256": hashlib.sha256(script.read_bytes()).hexdigest(),
           "resultSHA256": hashlib.sha256(result_path.read_bytes()).hexdigest(), "images": images,
           "realUserBrowserOrSaveAccess": False}
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"receipt": receipt_path.name, "exitCode": run.returncode, "images": images}, ensure_ascii=False))
print(result.get("text", run.stdout)[-14000:])
sys.exit(run.returncode)
