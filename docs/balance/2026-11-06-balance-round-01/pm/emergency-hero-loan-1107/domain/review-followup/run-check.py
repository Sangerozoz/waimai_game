import datetime,hashlib,json,pathlib,re,subprocess,sys,tempfile
root=pathlib.Path.cwd();out=pathlib.Path(__file__).resolve().parent;label=sys.argv[1]
log=out/(label+'.log');receipt=out/(label+'.json')
if log.exists() or receipt.exists():raise SystemExit('Evidence already exists: '+label)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((out/'inputs-before.json').read_text());paths=list(freeze['sourceAndTestSHA256'])
before={p:sha(root/p) for p in paths}
for p,h in freeze['sourceAndTestSHA256'].items():
 if p.endswith('.ts'):assert before[p]==h,p
for p,h in freeze['protectedEvidenceSHA256'].items():assert sha(root/p)==h,p
scratch=set(pathlib.Path(tempfile.gettempdir()).glob('delivery-v2-test-*'))
command=['node','delivery-game/tests/run-v2.cjs',*sys.argv[2:]]
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('xb') as stream:result=subprocess.run(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT)
after={p:sha(root/p) for p in paths};remaining=set(pathlib.Path(tempfile.gettempdir()).glob('delivery-v2-test-*'))-scratch
protectedChanges=[p for p,h in freeze['protectedEvidenceSHA256'].items() if sha(root/p)!=h]
content=log.read_text();counts={k:int(m[-1]) if (m:=re.findall(r'^# '+k+r' (\d+)$',content,re.M)) else None for k in ['tests','pass','fail']}
record=dict(command=command,cwd=str(root),startedAt=started,finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=result.returncode,sourceAndTestSHA256Before=before,sourceAndTestSHA256After=after,inputsStableDuringRun=before==after,fiveProductionSourcesUnchanged=all(after[p]==h for p,h in freeze['sourceAndTestSHA256'].items() if p.endswith('.ts')),protectedEvidenceChanges=protectedChanges,logSHA256=sha(log),newRunnerScratchRemaining=sorted(map(str,remaining)),counts=counts)
with receipt.open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(record,ensure_ascii=False,indent=2));print('\n'.join(content.splitlines()[-35:]))
raise SystemExit(result.returncode)
