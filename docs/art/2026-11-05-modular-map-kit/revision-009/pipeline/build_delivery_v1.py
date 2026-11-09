#!/usr/bin/env python3
import json,hashlib,shutil,html,zipfile,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'revision-006';OUT=ROOT/'delivery-kit/v1'
def read(p):return json.loads(p.read_text())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if OUT.exists()and '--resume-incomplete'not in sys.argv:raise SystemExit('v1 exists: refuse overwrite of user layout/delivery')
OUT.mkdir(parents=True,exist_ok=True);lib=read(BASE/'integration/asset-library.json');cal={x['id']:x for x in read(BASE/'integration/asset-calibration.json')['assets']};scene=read(BASE/'viewer/assets/scene-layout.json');doc=read(BASE/'integration/neighborhood.tmj');assert len(scene['blocks'])==163 and len(scene['groundSurfaces'])==506
protect={str(p):sha(p)for p in [BASE/'integration/neighborhood.tmj',BASE/'viewer/assets/scene-layout.json',BASE/'integration/asset-library.json',BASE/'integration/asset-calibration.json']}
write(OUT/'metadata/main-protection.json',protect);write(OUT/'metadata/base-scene.json',scene)
names={'B01':'三层街楼','B02':'退台办公楼','B03':'窄高楼','B04':'低层公共展馆','B05':'坡顶住宅','B06':'错落住宅','B07':'U形院楼','B08':'连拱顶市场','B09':'扇壳公共楼','B10':'锯齿厂房','B11':'坡顶作坊','B12':'单层住宅候选','B13':'单层街铺候选','T01':'树池街树','T02':'自然阔叶树','T03':'针叶树候选','T05':'低灌木簇','L-near':'近侧向内灯','L-far':'远侧向内灯','P01':'空白灯箱','P02':'油箱','P03':'长椅','P04-v2':'圆桌中央柱版','P05':'圆凳','P06':'短围栏方向一','P07':'短围栏方向二','P08':'菜畦','P10':'双垃圾桶','V01-v2':'两厢车静态候选','V02-v2':'箱形货车静态候选','HC-R-NE':'D骑手方向一','HC-R-SW':'D骑手方向二','S01-paving':'铺装小纹理','S02-asphalt':'沥青小纹理'}
rows=[];categories={};candidates={'B09','B10','B11','T03'}
for a in lib['assets']:
 a=dict(a)
 if 'worldSizeUnits'not in a:a.update({'worldSizeUnits':[2,2*a['nativeSize'][1]/a['nativeSize'][0]],'anchorUV':a.get('wheelContactAnchorUV',[.5,.5]),'defaultSizeNote':'visual palette candidate only, not a newly measured native PPU'})
 id=a['id'];category='建筑'if id.startswith('B')else'植物'if id.startswith('T')else'灯具'if id.startswith('L-')else'小物'if id.startswith('P')else'地材'if a['kind']=='material'else'车辆与骑手'
 status='候选｜本体或视角有争议，默认不入雏形'if id in candidates else'可手调｜待画面确认'if id in {'B12','B13','T05','V01-v2','V02-v2','P04-v2','P06','P07'}else'主用｜局部已显示或可供摆放，未全局精校'
 target=OUT/'assets'/category/a['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/'integration/assets'/a['file'],target);size=list(Image.open(target).size);assert max(size)<=280 and sha(target)==a['sha256']
 deriv=a.get('runtimeDerivation',{});row=dict(a);row.update({'nameZh':names.get(id,id),'categoryZh':category,'deliveryStatus':status,'packageFile':str(target.relative_to(OUT)),'bytes':target.stat().st_size,'calibration':cal.get(id),'canonicalReadonly':True,'instanceVisualEditing':'position/positive uniform size/add/delete allowed; no business/navigation copies','variantRelation':'B13 clean is same native family and original crop mapping'if id=='B13'else'v2 corrected variant'if id in {'V01-v2','V02-v2','P04-v2'}else None,'sourceNativeSHA256':deriv.get('sourceSHA256')});rows.append(row);categories[category]=categories.get(category,0)+1
write(OUT/'metadata/catalog.json',{'assets':rows,'categories':categories,'uniquePNG':len(rows),'PNGBytes':sum(r['bytes']for r in rows),'sourceNativeFilesIncluded':False,'layoutQuality':'editable rough prototype, not final acceptance'})
# Preserve current map object IDs/layers; only image paths become package relative.
by={a['id']:a for a in rows}
for ts in doc['tilesets']:
 for t in ts['tiles']:
  aid=next(p['value']for p in t['properties']if p['name']=='assetId');t['image']=by[aid]['packageFile']
# Include missing materials and rider directions in the drag-in library as well.
ts=doc['tilesets'][0];present={next(p['value']for p in t['properties']if p['name']=='assetId')for t in ts['tiles']}
for a in rows:
 if a['id']not in present:
  ts['tiles'].append({'id':max(t['id']for t in ts['tiles'])+1,'image':a['packageFile'],'imagewidth':a['nativeSize'][0],'imageheight':a['nativeSize'][1],'properties':[{'name':'assetId','type':'string','value':a['id']}]})
ts['tilecount']=len(ts['tiles']);
if not(OUT/'user-layout.tmj').exists():write(OUT/'user-layout.tmj',doc)
# Tiled object templates include a single external tile set and visual-only properties.
tileby={next(p['value']for p in t['properties']if p['name']=='assetId'):t for t in ts['tiles']}
ext=OUT/'templates/asset-library.tsj';external=dict(ts);external.pop('firstgid',None);external['tiles']=[dict(t,image='../'+t['image'])for t in ts['tiles']];write(ext,external)
for a in rows:
 w,h=a['worldSizeUnits'];template={'type':'template','tileset':{'firstgid':1,'source':'asset-library.tsj'},'object':{'id':1,'name':a['id']+' 装饰','type':'sprite','gid':1+tileby[a['id']]['id'],'width':w*16,'height':h*16,'rotation':0,'visible':True,'properties':[{'name':'assetId','type':'string','value':a['id']},{'name':'visualOnly','type':'bool','value':True}]}}
 write(OUT/'templates'/(a['id']+'.tx'),template)
# Small editable object palette: copy/paste its tile objects into user-layout.
palette=json.loads(json.dumps(doc));palette['layers']=[{'id':1,'name':'分类素材拖入/复制；均为装饰，无经营导航绑定','type':'objectgroup','draworder':'index','objects':[]}]
for j,a in enumerate(rows):
 w,h=a['worldSizeUnits'];palette['layers'][0]['objects'].append({'id':j+1,'name':a['id']+' '+a['nameZh'],'type':'sprite','gid':ts['firstgid']+tileby[a['id']]['id'],'x':(j%6)*440,'y':(j//6+1)*500,'width':w*16,'height':h*16,'visible':True,'properties':[{'name':'assetId','type':'string','value':a['id']},{'name':'visualOnly','type':'bool','value':True}]})
palette['nextobjectid']=len(rows)+1;palette['nextlayerid']=2;write(OUT/'asset-palette.tmj',palette)
# Existing Cocos shell only: base preview has the actual163 layout; no new engine.
shutil.copytree(BASE/'viewer',OUT/'preview');shutil.copyfile(BASE/'viewer/assets/scene-layout.json',OUT/'preview/assets/scene-layout.json')
# Export script stored separately, copied by final packaging step.
cards=[]
for a in rows:cards.append('<article><img src="'+html.escape(a['packageFile'])+'"><b>'+html.escape(a['id']+' '+a['nameZh'])+'</b><p>'+html.escape(a['deliveryStatus'])+'</p><small>'+str(a['nativeSize'])+' / '+str(a['bytes'])+' B</small></article>')
(OUT/'catalog.html').write_text('<!doctype html><meta charset="utf-8"><title>地图资产包 v1</title><style>body{font-family:system-ui;background:#eeeadd;color:#28302b;margin:24px}section{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}article{background:#fff;padding:12px;border-radius:8px}img{width:100%;height:200px;object-fit:contain}b{display:block}p{font-size:14px}</style><h1>地图资产包 v1</h1><p>34张分类运行图，≤280。默认尺寸仅起点；用户可移动、等比缩放、新放/删除装饰。候选本体问题与布局未精校分开，不设1/2实例限制。</p><p><a href="preview/?view=compound-market">163物件可编辑初稿预览</a> · <a href="user-layout.tmj">用户Tiled源</a> · <a href="asset-palette.tmj">素材对象盘</a> · <a href="README.md">3步使用</a></p><section>'+''.join(cards)+'</section>')
print('Built delivery',len(rows),'PNG',sum(r['bytes']for r in rows),categories)
