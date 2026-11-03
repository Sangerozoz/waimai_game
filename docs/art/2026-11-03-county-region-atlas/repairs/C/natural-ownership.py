"""Common-map natural ownership candidate. Diagnostic only, source art unchanged."""
exec((__import__('pathlib').Path(__file__).parent/'ownership-diagnostic.py').read_text().split("ab=json.loads")[0])
from PIL import ImageChops
ab=json.loads((B/'registration/A-B-v4-production-handoff.json').read_text())
path=ab['sourceMapSeam'];across=[]
for x,y in zip(path,path[1:]):
 across.append(x)
 if x[1]<=132<=y[1]:
  t=(132-x[1])/(y[1]-x[1]);across.append([x[k]+t*(y[k]-x[k])for k in [0,1]]);break
AB=[list(world(p))for p in across];T=AB[-1]
def cp(p):
 e=entries[2];s=P/e['nativePixelsPerUnit'];a=world(e['anchorMap']);return [a[k]+s*(p[k]-1254*e['anchorUV'][k])for k in [0,1]]
def dp(p):
 e=entries[3];s=P/e['nativePixelsPerUnit'];a=world(e['anchorMap']);return [a[k]+s*(p[k]-1254*e['anchorUV'][k])for k in [0,1]]
AC=[[-100,250],cp([450,-50]),cp([450,160]),cp([480,220]),cp([520,300]),cp([555,339]),cp([827,233]),cp([860,300]),cp([870,350]),cp([860,410]),cp([865,500]),cp([860,650]),cp([940,700]),T]
CD=[T,cp([1020,700]),cp([900,750]),cp([817,784]),cp([767,820]),cp([650,920]),cp([540,1020]),cp([423,1092]),[-100,1300]]
BD=[T,dp([635,90]),dp([700,40]),dp([790,100]),dp([900,220]),dp([1020,360]),dp([1120,450]),dp([1250,550]),[1500,1100]]
planes={
 'REGION-A':[[-100,-100],[1400,-100]]+AB+list(reversed(AC[:-1])),
 'REGION-B':[[1400,-100],[1500,-100],[1500,1100]]+list(reversed(BD[:-1]))+list(reversed(AB[:-1])),
 'REGION-C':AC+CD[1:]+[[-100,1500]],
 'REGION-D':list(reversed(CD))+BD[1:]+[[1500,1500],[-100,1500]]}
def canvasMap(p):
 x=(p[0]-700)/P;y=(p[1]-400)/P/st;return [-1580+q*(x+y),80+q*(y-x)]
def uv(p,e):
 m=canvasMap(p);x,y=m[0]-e['anchorMap'][0],m[1]-e['anchorMap'][1];s=e['nativePixelsPerUnit'];return [e['anchorUV'][0]+s*q*(x-y)/1254,e['anchorUV'][1]+s*q*st*(x+y)/1254]
sourcepolys={};im=Image.new('RGB',(1400,1500),'#33343b');outputs=[];out=O/'ownership-candidate';out.mkdir(exist_ok=True)
for i in [2,3,0,1]:
 e,f=entries[i],arts[i]
 id=e['id'];poly=planes[id]
 if id=='REGION-A':
  v=ab['ownershipPolygonUV'][id]
 elif id=='REGION-B':v=[uv(p,e)for p in planes[id]]
 elif id=='REGION-C':v=[[0,0],[1,0],[1,1],[0,1]]
 else:
  poly=list(reversed(CD))+[[1500,-100],[1500,1500],[-100,1500]]
  v=[uv(p,e)for p in poly]
 for dim,val,le in [(0,0,False),(0,1,True),(1,0,False),(1,1,True)]:v=clip(v,dim,val,le)
 sourcepolys[id]=[inverse(p,e)for p in v];en=dict(e);en['sortOrder']={'REGION-C':-2,'REGION-D':-1,'REGION-A':0,'REGION-B':1}[id];en['ownershipPolygonUV']=v;en['note']=e.get('note','')+' Natural ownership candidate; PM must inspect common diagnostic. No full county claim.'
 (out/(id+'-entry.json')).write_text(json.dumps(en,indent=2)+'\n');outputs.append(en)
 art=Image.open(f);scale=P/e['nativePixelsPerUnit'];nw=round(1254*scale);art=art.resize((nw,nw),Image.Resampling.LANCZOS);anchor=world(e['anchorMap']);xy=(round(anchor[0]-e['anchorUV'][0]*nw),round(anchor[1]-e['anchorUV'][1]*nw));layer=Image.new('RGBA',im.size);layer.paste(art,xy);mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon([world(p)for p in sourcepolys[id]],fill=255);mask=ImageChops.multiply(mask,layer.getchannel('A'));im.paste(layer,mask=mask)
im.save(O/'ABCD-natural-ownership-candidate.jpg');d=ImageDraw.Draw(im)
for line in [AB,AC,BD,CD]:d.line([tuple(p)for p in line],fill='magenta',width=2)
d.text((20,20),'Natural ownership CANDIDATE: diagnostic, not engine screenshot',fill='white');im.save(O/'ABCD-natural-ownership-lines.jpg')
record={'status':'actual-consumable-natural-ownership-candidate-awaiting-PM','sourceMapPolygons':sourcepolys,'constructionGuideSourceMap':{'A-B':[canvasMap(p)for p in AB],'A-C':[canvasMap(p)for p in AC],'B-D':[canvasMap(p)for p in BD],'C-D':[canvasMap(p)for p in CD]},'entries':[str(out/(e['id']+'-entry.json'))for e in outputs],'note':'Actual sourceMapPolygons and per-entry ownershipPolygonUV are authoritative clipping candidates. constructionGuideSourceMap contains helper contours, not all implemented as mutual exclusive seams. C full native underlay sort-2, D natural west contour sort-1, A prior AB mask sort0, B AB edge with D north exterior contour sort1. A/B internal street priority; original alpha holes reveal lower native images, no painted filler. Native alpha plus sortOrder determines one visible pixel owner. Small border drift retained. PM inspect D west roof adjacency to C lower road.'};(O/'natural-ownership-candidate.json').write_text(json.dumps(record,indent=2)+'\n')
print('entries',len(outputs))
