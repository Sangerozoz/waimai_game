import pathlib,subprocess,sys,json,time,hashlib
b=pathlib.Path(__file__).resolve().parent
session=json.loads((b/'session-open-observed.json').read_text())['id']
for name in sys.argv[1:]:
 p=b/name
 cmd=['bb','browser-automation','run',session,'--script-file',str(p),'--script-host','host_tr578kqahd','--timeout','60s','--json']
 t=time.monotonic();r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 stem=name.removesuffix('.js');(b/(stem+'-result.json')).write_bytes(r.stdout);(b/(stem+'-stderr.log')).write_bytes(r.stderr)
 receipt={'command':cmd,'exitCode':r.returncode,'elapsedSeconds':time.monotonic()-t,'scriptSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'resultSHA256':hashlib.sha256(r.stdout).hexdigest(),'stderrSHA256':hashlib.sha256(r.stderr).hexdigest()}
 (b/(stem+'-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'script':name,**receipt}),flush=True)
 if r.returncode:print(r.stderr.decode()[-1500:]);raise SystemExit(r.returncode)
