import pathlib,json,hashlib
from PIL import Image
p=pathlib.Path(__file__).parent
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
m=json.loads((p/'manifest.json').read_text()); r=json.loads((p/'roster.json').read_text()); rec=json.loads((p/'generation-records.json').read_text())
f=p/'hero-v1.png';im=Image.open(f)
m['assets']['hero']=dict(file=str(f),rect=[0,0,im.width,im.height],status='candidate',sha256=sha(f),nativeWidth=im.width,nativeHeight=im.height)
r['characters'][0].update(resource=str(f),rect=m['assets']['hero']['rect'])
rec.append(dict(file=str(f),source='built-in image_gen',prompt='prompt-hero-v1.txt',references=['docs/art/user-deliveries/2026-10-30-au01/rider-master-original.png','docs/art/2026-11-02-approved-ui-reference/01-riders-v4.png'],sha256=sha(f),nativeSize=list(im.size),mode=im.mode,alpha='A' in im.getbands(),visualInspection=True,issues=['棕发橙衣棕眼身份保留；近景重绘五官与原稿存在细节差别，未用户验收']))
origins=['exec-b2ccb031-a075-4d78-9d08-b4e0492657d9.png','exec-39e7c2aa-aa5d-45e5-a680-0e010436c02c.png','exec-0fcad2be-ceef-4283-803a-be15aac391d3.png','exec-cf0c7d76-693f-4e06-ac1f-b20c1c63e952.png','exec-3b6a869c-e712-4810-9de2-f65124184dc0.png','exec-7a9ac136-60ea-41d1-95df-6f34b390b0a8.png']
for a,o in zip(rec,origins):
 a['originalGeneratedFile']='/Users/sanger/.codex/generated_images/01a1a6e8-0187-7240-8647-4d64ca3c9009/'+o
 a['promptText']=(p/a['prompt']).read_text()
 refs=a.get('references',[a.get('reference')]); a['referenceSHA256']={f:sha(f) for f in refs}
 if 'atlas' in a['file']: a['rects']= [v['rect'] for v in m['assets'].values() if v['file']==a['file']]
for n in [1,2]:
 f=p/f'atlas-{n:02}-v1.png';im=Image.open(f)
 rec.append(dict(file=str(f),source='built-in image_gen',prompt=f'prompt-{n:02}.txt',promptText=(p/f'prompt-{n:02}.txt').read_text(),sha256=sha(f),nativeSize=list(im.size),mode=im.mode,alpha=False,status='rejected',issues=['高领外套和背带重复；被v2替代，不得接入']))
rec[4]['issues'].append('npc-29眉疤实际偏额头；npc-30眼镜形状偏圆，非精确文字复刻')
for filename,obj in [('manifest.json',m),('roster.json',r),('generation-records.json',rec)]: (p/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
expected={'hero'}|{f'npc-{i}' for i in range(1,31)}
assert set(m['assets'])==expected
for k,a in m['assets'].items():
 im=Image.open(a['file']); x,y,w,h=a['rect']
 assert 0<=x<x+w<=im.width and 0<=y<y+h<=im.height
 assert w>=280 and sha(a['file'])==a['sha256']
for i in range(1,31): assert m['assets'][f'npc-{i}']['rect']!=m['assets'].get(f'npc-{i+1}',{}).get('rect') or m['assets'][f'npc-{i}']['file']!=m['assets'].get(f'npc-{i+1}',{}).get('file')
result=dict(coveredIDs=sorted(expected),count=31,allFilesExist=True,allSHA256Match=True,allRectsInBounds=True,minNPCWidth=min(a['rect'][2] for k,a in m['assets'].items() if k!='hero'),candidateOnly=True,notGameTest=True,notUserAcceptance=True)
(p/'delivery-integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
