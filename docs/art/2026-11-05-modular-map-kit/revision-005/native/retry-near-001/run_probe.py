#!/usr/bin/env python3
"""Run one native-tool attempt with a hard deadline and real PTY."""
import argparse
import errno
import json
import os
from pathlib import Path
import pty
import select
import signal
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
parser.add_argument('--geometry', default='L01-road-near-geometry.png')
parser.add_argument('--asset', default='L01-road-near-v1.png')
parser.add_argument('--appearance', type=Path)
parser.add_argument('--style', type=Path)
args = parser.parse_args()
HERE = args.output_dir.resolve()
ROOT = Path('/Users/sanger/Documents/ChatGPT/taptap 2')
KIT = ROOT/'docs/art/2026-11-05-modular-map-kit'
geometry = Path(args.geometry)
if not geometry.is_absolute():
    geometry = KIT/'revision-005/native'/geometry
appearance = args.appearance or KIT/'pilot/L01-v1.png'
command = ['codex', 'exec', '--sandbox', 'workspace-write', '--enable', 'image_generation',
           '--disable', 'unbounded_connection_retries', '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort="medium"',
           '--image', str(geometry), '--image', str(appearance)]
if args.style:
    command.extend(['--image', str(args.style)])
command.extend(['--output-last-message', str(HERE/'result.txt'), '-'])
log_path = HERE/'execution.log'
if log_path.exists():
    raise SystemExit('Refusing to rerun the same probe or overwrite its evidence')
master, slave = pty.openpty()
start = time.monotonic()
process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=slave, stderr=slave, cwd=ROOT, start_new_session=True)
os.close(slave)
assert process.stdin is not None
process.stdin.write((HERE/'request.txt').read_bytes())
process.stdin.close()
timed_out = False
with log_path.open('wb') as log:
    while True:
        if time.monotonic()-start > 240:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            break
        readable, _, _ = select.select([master], [], [], .5)
        if readable:
            try:
                data = os.read(master, 65536)
            except OSError as error:
                if error.errno == errno.EIO:
                    break
                raise
            if not data:
                break
            log.write(data); log.flush()
        elif process.poll() is not None:
            break
os.close(master)
if process.poll() is None:
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
report = {'exitCode': process.returncode, 'hardDeadlineSeconds': 240, 'deadlineReached': timed_out,
          'elapsedSeconds': round(time.monotonic()-start, 2), 'nativePNGExists': (HERE/args.asset).exists(),
          'log': str(log_path)}
(HERE/'probe-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False))
# Return only bounded diagnostics, not the repeated project context/prompt dump.
lines = log_path.read_text(errors='replace').splitlines()
print('\n'.join(lines[-35:]))
