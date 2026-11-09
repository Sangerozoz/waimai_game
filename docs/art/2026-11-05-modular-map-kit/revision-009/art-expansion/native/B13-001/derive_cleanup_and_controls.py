from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
R=Path(__file__).resolve().parents[1];D=R/'B13-001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=[p for id in ['B12','B13'] for p in (R/(id+'-001')).iterdir() if p.name in [id+'-v1.png',id+'-runtime-280.png',id+'-runtime-280.runtime.json','provenance.json','REPORT.md']];hashes={str(p):sha(p) for p in protected}
cs=json.loads((D/'B13-runtime-component-pixels.json').read_text());deleted=[1,2]+list(range(4,34))
im=Image.open(D/'B13-runtime-280.png');clean=im.copy();mask=Image.new('L',im.size);count=0
for c in cs:
 if c['id'] not in deleted:continue
 assert c['alphaMax']==1
 for q in c['pixels']:
  q=tuple(q);clean.putpixel(q,(0,0,0,0));mask.putpixel(q,255);count+=1
clean.save(D/'B13-runtime-280-clean.png');mask.save(D/'B13-runtime-280-clean-deletion-mask.png')
changed=[(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))!=clean.getpixel((x,y))]
assert len(changed)==count
assert all(im.getpixel((x,y))==clean.getpixel((x,y)) for y in range(im.height) for x in range(im.width) if not mask.getpixel((x,y)))
canvas=Image.new('RGB',(im.width*2,im.height),'#506070');canvas.paste(im,(0,0),im);canvas.paste(clean,(im.width,0),clean);canvas.resize((im.width*6,im.height*3)).save(D/'B13-runtime-280-clean-before-after.png')
rep=dict(status='runtime-derived-cleanup-not-native-not-new-family',originalSHA256=sha(D/'B13-runtime-280.png'),cleanSHA256=sha(D/'B13-runtime-280-clean.png'),canvasBefore=list(im.size),canvasAfter=list(clean.size),changedPixelCount=count,retainedPixelsRGBAExactlyUnchanged=True,mainComponent3Untouched=True,removedComponentIds=deleted,removedComponents=[{k:v for k,v in c.items() if k!='pixels'} for c in cs if c['id'] in deleted],decision='逐项看标注图：仅上方外部完全游离alpha1碎屑，无屋顶/檐/门阶/灯/把手形态。非keep-largest，非颜色阈值。其余独立组件保守保留，主连通体包括边缘碎屑不动。',mapping='No crop/resize/translation; original cropBox, anchorUV if any, PPU and world size unchanged; use original runtime metadata unchanged.',protectedSHA256=hashes)
(D/'B13-runtime-280-clean-derivation.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n')
configs={'B12':{'W1':([450,1143],'可见左前墙脚转角'),'W2':([749,1001],'同一临街墙脚直边，止于门廊柱基前'),'W3':([183,813],'可见左侧墙脚后端'),'T1':([804,954],'实门底门槛左端'),'T2':([879,917],'实门底门槛右端'),'S1':([820,1027],'最外层台阶左前突出点'),'S2':([934,976],'最外层台阶右前突出点'),'R1':([151,566],'左后屋檐端，非墙脚'),'R2':([802,194],'后屋面高点，非墙脚')},'B13':{'W1':([758,1097],'门阶右侧连续临街墙脚直边起点'),'W2':([1084,954],'同一灰墙脚直边右端，排除外角木柱突出部'),'W3':([143,804],'左侧连续墙脚后端'),'W4':([440,1197],'左前墙脚转角'),'T1':([548,1125],'实门底门槛左端'),'T2':([655,1082],'实门底门槛右端'),'S1':([556,1180],'突出门阶左前点'),'S2':([694,1122],'突出门阶右前点'),'R1':([126,464],'后侧女儿墙端，非墙脚'),'R2':([781,126],'远屋顶角，非墙脚')}}
for id,points in configs.items():
 d=R/(id+'-001');p=json.loads((d/'provenance.json').read_text());rt=json.loads((d/(id+'-runtime-280.runtime.json')).read_text());box=rt['cropBox'];rw,rh=rt['runtimeSize'];edges=[('frontage','W1','W2',-28.486362688849802),('depth','W3','W1' if id=='B12' else 'W4',55.40598449120886)];es=[]
 for kind,a,b,target in edges:
  q=points[a][0];v=points[b][0];ang=math.degrees(math.atan2(v[1]-q[1],v[0]-q[0]));es.append(dict(kind=kind,fromId=a,toId=b,deltaPixels=[v[0]-q[0],v[1]-q[1]],screenAngleDegrees=ang,targetDegrees=target,residualDegrees=ang-target,lengthPixels=math.dist(q,v),note='实际可见同一墙脚直边两端人工点读；数学计算精确不等于点位精确，端点约±3px'))
 rec=dict(id=id,coordinateSystem='native PNG pixels x right/y down; manual readings approximately +/-3 pixels',nativeSourceSHA256=sha(d/(id+'-v1.png')),points=[dict(id=k,nativeXY=q,meaning=label,runtimeXY=[(q[0]-box[0])*rw/(box[2]-box[0]),(q[1]-box[1])*rh/(box[3]-box[1])]) for k,(q,label) in points.items()],visibleStraightBaseEdges=es,hiddenCorner='远后墙脚被建筑实体遮住；不提供假实测点或据此恢复精密四角。',separation='W墙脚/T实门槛/S突出阶/R屋顶分开；透明处不是门。',status='diagnostic-only-not-calibrated-not-admitted',mappingUnchanged=True)
 (d/'native-control-points.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
 out=Image.open(d/(id+'-control-inspection.png')).convert('RGB');dr=ImageDraw.Draw(out);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
 for e in es:dr.line([points[e['fromId']][0],points[e['toId']][0]],fill='#00ffff',width=3)
 for k,(q,label) in points.items():
  x,y=q;col={'W':'#00ffff','T':'#ffff00','S':'#ff80ff','R':'#ff8000'}[k[0]];dr.ellipse((x-6,y-6,x+6,y+6),fill=col);dr.text((x+8,y-24),k,fill=col,font=font)
 out.save(d/'native-control-points-annotated.png');print(id,[(e['kind'],round(e['screenAngleDegrees'],6),round(e['residualDegrees'],6)) for e in es])
assert all(sha(Path(p))==h for p,h in hashes.items())
print('removed',count,'pixels; originals unchanged; clean SHA',rep['cleanSHA256'])
