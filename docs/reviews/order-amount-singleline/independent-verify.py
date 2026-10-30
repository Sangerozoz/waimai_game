import json,pathlib,hashlib
p=pathlib.Path('docs/reviews/order-amount-singleline');d=json.loads((p/'independent-after.log').read_text().split('### Result\n')[1].split('\n###')[0]);(p/'independent-after.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));assert len(d)==35
for r in d:
 assert not r.get('error')
 for a in r['amounts']:
  assert len(a['lines'])==1,(r,a)
  assert a['measured']<=a['width']+.5,(r,a)
  assert a['bounds']['right']-a['bounds']['left']<=a['parentWidth']+.5
  for b in a['siblings']:
   x,y=a['bounds'],b['bounds']; overlap=min(x['right'],y['right'])-max(x['left'],y['left'])>1 and min(x['top'],y['top'])-max(x['bottom'],y['bottom'])>1
   assert not overlap,(r['mode'],a['text'],b['text'])
 if r['receipt']:
  assert all(abs(l['bounds']['center']-r['card']['center'])<.1 and l['align']==1 for l in r['receipt'])
 if r['mode']=='effects':
  assert any('晚到影响' in x['text'] for x in r['receipt']),r
  assert any('餐损影响' in x['text'] for x in r['receipt']),r
 assert r['storage']==[{'method':'setItem','key':'storage'}]
print('PASS 35 real-engine state/viewport cases; one-line + measured fit + sibling bounds + receipt centers + both impact rows + intercepted storage probe')
root=pathlib.Path.cwd();site=root/'output/playwright/order-layout-independent/after';prod=root/'delivery-game/build/map-sample';diff=[]
for f in prod.rglob('*'):
 if not f.is_file():continue
 b=(site/f.relative_to(prod)).read_bytes()
 if f.name=='index.html':b=b.replace(b'<script src="fixture.js"></script>\n',b'')
 if b!=f.read_bytes():diff.append(str(f))
assert not diff,diff
paths=list((root/'delivery-game/assets/scripts/map-sample').glob('*.ts'))+list(site.rglob('*'))+list(p.glob('independent-*'))
(p/'independent-final-sha.json').write_text(json.dumps({str(f.relative_to(root) if f.is_absolute() else f):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths if f.is_file() and f.name!='independent-final-sha.json'},indent=2));print('PASS isolated after build matches frozen production build bytes (only fixture index injection excluded)')
