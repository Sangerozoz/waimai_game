import json,pathlib,subprocess,time
base=pathlib.Path(__file__).resolve().parent;catalog=json.loads((base/'web-batches.json').read_text());helper=base/'web-batch.py'
def step(action,index):
 r=subprocess.run(['python3',str(helper),action,str(index)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 print(r.stdout.strip(),flush=True)
 if r.returncode:raise SystemExit(r.returncode)
 return json.loads(r.stdout.strip().splitlines()[-1])
for i in range(len(catalog['batches'])):
 done={r['sourceSHA256'] for r in json.loads((base/'web-receipt.json').read_text())['results']}
 if all(r['sha256'] in done for r in catalog['batches'][i]):continue
 step('start',i)
 for attempt in range(60):
  d=step('poll',i)
  if d['hasError']:raise SystemExit('TinyPNG reports an error/limit; stopped without bypassing it')
  if d['ready']==d['expected']:step('finish',i);break
  time.sleep(3)
 else:raise SystemExit('TinyPNG batch timed out; kept previous outputs')
print('ALL_TINYPNG_WEB_BATCHES_COMPLETE',flush=True)
