#!/usr/bin/env python3
import hashlib,json,os,shlex
from pathlib import Path
HERE=Path(__file__).resolve().parent
runtime=json.loads((HERE.parent/'runtime.json').read_text())
exe=Path(runtime['pythonExecutable']);script=HERE/'run_capacity_probe.py'
if not exe.is_file() or not script.is_file():raise SystemExit('Verified runtime/script unavailable; no replacement or install')
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=os.pathsep.join(runtime['moduleSearchPaths'])
command='PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='+shlex.quote(env['PYTHONPATH'])+' '+shlex.quote(str(exe))+' '+shlex.quote(str(script))
(HERE/'execution-command.json').write_text(json.dumps({'cwd':str(Path.cwd()),'exactCommand':command,'scriptSHA256':hashlib.sha256(script.read_bytes()).hexdigest(),'scope':'one explicitly bounded standard-size control; no further request/retry or D production'},ensure_ascii=False,indent=2)+'\n')
os.execve(str(exe),[str(exe),str(script)],env)
