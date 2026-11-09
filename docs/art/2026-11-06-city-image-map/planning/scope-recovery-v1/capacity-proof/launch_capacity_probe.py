#!/usr/bin/env python3
"""Launch the approved single proof with the actual parent runtime, no installs."""
import hashlib
import json
import os
from pathlib import Path
import shlex

HERE=Path(__file__).resolve().parent
runtime=json.loads((HERE/'runtime.json').read_text())
exe=Path(runtime['pythonExecutable'])
script=HERE/'run_capacity_probe.py'
if not exe.is_file() or not script.is_file():
    raise SystemExit('Actual runtime/script unavailable; no substitute interpreter or install attempted.')
env=os.environ.copy()
env['PYTHONDONTWRITEBYTECODE']='1'
env['PYTHONPATH']=os.pathsep.join(runtime['moduleSearchPaths'])
command='PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='+shlex.quote(env['PYTHONPATH'])+' '+shlex.quote(str(exe))+' '+shlex.quote(str(script))
(HERE/'execution-command.json').write_text(json.dumps({'cwd':str(Path.cwd()),'exactCommand':command,'pythonExecutable':str(exe),'scriptSHA256':hashlib.sha256(script.read_bytes()).hexdigest(),'task':'one user-authorized capacity proof, max1Images request, no image/region production loop'},ensure_ascii=False,indent=2)+'\n')
os.execve(str(exe),[str(exe),str(script)],env)
