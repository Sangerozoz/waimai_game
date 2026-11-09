#!/usr/bin/env python3
"""Existing-image scale/readability board only. No image API/game/server writes."""
from pathlib import Path
import base64,hashlib,html,io,json,math,statistics
from PIL import Image,ImageDraw,ImageFont,ImageChops

HERE=Path(__file__).resolve().parent
PLAN_DIR=HERE.parent
ART_ROOT=PLAN_DIR.parent.parent
A2=ART_ROOT/'compact-pair-v2-density/native/A-v2-api.png'
PROBE_A=PLAN_DIR/'capacity-proof/native.png'
PROBE_B=PLAN_DIR/'capacity-proof/standard-size-control/native.png'
EDGE=ART_ROOT/'compact-pair-v2-density/integration/next-C/identity-and-edge-contract.json'
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
COL={'ink':'#20333b','muted':'#53666d','panel':'#ffffff','line':'#ced9dc','purple':'#943eaf','green':'#19785c','orange':'#bf6427'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n):return ImageFont.truetype(FONT,n)
def dump(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def lines(draw,text,xy,width,size=22,fill=None,spacing=9):
    x,y=xy;f=font(size);line=''
    for c in text:
        if c=='\n' or (line and draw.textlength(line+c,font=f)>width):
            draw.text((x,y),line,font=f,fill=fill or COL['muted']);line='';y+=size+spacing
            if c=='\n':continue
        line+=c
    if line:draw.text((x,y),line,font=f,fill=fill or COL['muted']);y+=size+spacing
    return y

def embed(im):
    out=io.BytesIO();im.save(out,'WEBP',lossless=True,method=5)
    decoded=Image.open(io.BytesIO(out.getvalue())).convert('RGB')
    assert decoded.size==im.size and ImageChops.difference(decoded,im.convert('RGB')).getbbox() is None
    return 'data:image/webp;base64,'+base64.b64encode(out.getvalue()).decode()

def make():
    HERE.mkdir(parents=True,exist_ok=True)
    plan=json.loads((PLAN_DIR/'scope-plan.json').read_text());edge=json.loads(EDGE.read_text())
    source_paths=[A2,PROBE_A,PROBE_B,EDGE,PLAN_DIR/'scope-plan.json',PLAN_DIR/'capacity-proof/experiment-results.json']
    protected={str(p):sha(p) for p in source_paths}
    source=Image.open(A2).convert('RGB');a=Image.open(PROBE_A).convert('RGB');b=Image.open(PROBE_B).convert('RGB')
    assert source.size==(1536,1024) and a.size==(1674,940) and b.size==(1672,941)
    samples=[
      {'id':'shops','title':'沿街店铺组','box':[35,850,655,1018],'note':'屋顶、门窗和入口原生裁片；不将店招文字当功能数据。部分背景被裁，标注主体保留。','groundNote':'门槛/铺地可观察；盆栽与共享墙遮挡，未构建闭合地脚。'},
      {'id':'residential','title':'住宅','box':[72,614,368,904],'note':'保持整栋可见屋顶/立面，不缩楼；植物及前排建筑遮挡的部分不补画。','groundNote':'底部植栽和前排屋顶遮挡，完整地脚未知。'},
      {'id':'commercial','title':'弧面商办组','box':[1160,280,1502,522],'note':'完整可见主体和底商入口的原生裁片；不把影像宽高换算成真实占地。','groundNote':'前场/入口可见，背部及共享侧边不完整；闭合占地未知。'}]
    crops={}
    for s in samples:
        crop=source.crop(s['box']);path=HERE/(s['id']+'-native-1x.png');crop.save(path)
        assert ImageChops.difference(Image.open(path).convert('RGB'),source.crop(s['box'])).getbbox() is None
        crops[s['id']]=crop;s.update({'path':path.name,'cropSize':list(crop.size),'resized':False,'imageBBoxIsGroundFootprint':False,'closedGroundPolygon':None,'sha256':sha(path)})
    # Pixel-colour support only; these masks are not semantic road recognition.
    t=edge['portal']['southwardUnitDirection'];n=[t[1],-t[0]];ns=[]
    for y0 in [970,990]:
        cx=679.5+(y0-1024)*t[0]/t[1];hits=[]
        for d in range(-40,41):
            rgb=source.getpixel((round(cx+n[0]*d),round(y0+n[1]*d)))
            assert isinstance(rgb,tuple)
            if max(rgb)-min(rgb)<22 and 65<sum(rgb)/3<185:hits.append(d)
        lo,hi=min(hits),max(hits);assert (lo,hi)==(-26,26)
        ns.append({'centre':[cx,y0],'tangent':t,'normal':n,'neutralSupportTInterval':[lo,hi],'nominalNormalSpanPixels':hi-lo+1,'manualUncertaintyPixels':2,'endpoints':[[cx+n[0]*(lo-.5),y0+n[1]*(lo-.5)],[cx+n[0]*(hi+.5),y0+n[1]*(hi+.5)]]})
    ew=[]
    for x in [950,1000,1050]:
        hits=[]
        for y in range(510,615):
            rgb=source.getpixel((x,y))
            assert isinstance(rgb,tuple)
            if max(rgb)-min(rgb)<22 and 65<sum(rgb)/3<185:hits.append(y)
        # Pavement/shadow can also be neutral. Keep the visually chosen road
        # component, bridging only the one-pixel lane-paint interruption.
        runs=[]
        for y in hits:
            if not runs or y-runs[-1][-1]>2:runs.append([y])
            else:runs[-1].append(y)
        band=next(run for run in runs if min(run)<=557.5<=max(run))
        lo,hi=min(band),max(band);assert (lo,hi)==(531,584)
        ew.append({'centre':[x,557.5],'tangent':[1,0],'normal':[0,1],'observedAsphaltPixelRows':[lo,hi],'nominalNormalSpanPixels':hi-lo+1,'excludedNeutralPixels':[y for y in hits if y<lo or y>hi],'manualUncertaintyPixels':2,'endpoints':[[x,lo-.5],[x,hi+.5]]})
    road_specs=[('south-road',[620,950,740,1010],ns,'南口：沿道路法向，两处约53px'),('east-west-road',[930,518,1070,600],ew,'东西向：三处约54px')]
    roads=[]
    for name,box,cut,label in road_specs:
        raw=source.crop((box[0],box[1],box[2],box[3]));raw.save(HERE/(name+'-native.png'))
        # Nearest-neighbour enlarged ruler ONLY, never a high-resolution art derivative.
        zoom=raw.resize((raw.width*4,raw.height*4),Image.Resampling.NEAREST);dr=ImageDraw.Draw(zoom)
        for c in cut:
            pts=[((v[0]-box[0])*4,(v[1]-box[1])*4) for v in c['endpoints']]
            dr.line(pts,fill='#ff4e28',width=3)
            for x,y in pts:dr.ellipse((x-4,y-4,x+4,y+4),fill='#ff4e28')
        zoom.save(HERE/(name+'-ruler-4x.png'))
        roads.append({'id':name,'box':box,'label':label,'raw':raw,'zoom':zoom,'cuts':cut})
    block=next(x for x in plan['blocks'] if x['id']=='B-04-04')
    poly=block['polygonDesignMetres'];xmin=min(v[0] for v in poly);ymin=min(v[1] for v in poly)
    overlay=source.copy();ov=ImageDraw.Draw(overlay);projected=[]
    for angle,color in [(62.5,COL['purple']),(45,COL['green'])]:
        q=math.sin(math.radians(angle));pts=[(80+(x-xmin)*6.75,960-(y-ymin)*6.75*q) for x,y in poly]
        ov.line(pts+[pts[0]],fill=color,width=4)
        for x,y in pts:ov.ellipse((x-6,y-6,x+6,y+6),fill=color)
        ov.text((int(pts[-1][0])+12,int(pts[-1][1])+10),f'{angle}° 假设框',font=font(26),fill=color,stroke_width=2,stroke_fill='white')
        projected.append({'elevationAssumptionDegrees':angle,'pixelsPerDesignMetreX':6.75,'pixelsPerDesignMetreY':6.75*q,'pixelCorners':pts,'pixelBoundsSpan':[max(v[0] for v in pts)-min(v[0] for v in pts),max(v[1] for v in pts)-min(v[1] for v in pts)]})
    # Box positions are deliberately NOT presented as native parcel boundaries.
    overlay.save(HERE/'block-ground-frame-on-a2.png')
    comparisons=[]
    for name,im,box,title in [('a2',source,[35,600,655,1020],'认可A2'),('probe-a',a,[180,230,800,650],'自定义尺寸实验'),('probe-b',b,[100,440,720,860],'标准尺寸对照')]:
        crop=im.crop((box[0],box[1],box[2],box[3]));crop.save(HERE/(name+'-observation-620x420.png'));comparisons.append({'id':name,'title':title,'sourceBox':box,'image':crop,'naturalSize':list(crop.size)})
    board=Image.new('RGB',(2240,2260),'#eef3f4');dr=ImageDraw.Draw(board)
    dr.text((24,20),'A2 原生可读标尺 ＋ 代表街坊试排对照',font=font(39),fill=COL['ink'])
    lines(dr,'仅既有素材量读与设计试排，不是新城市美术。原生观察窗不缩放；4×道路图仅像素格量读。米制、投影、净占地与最终图数尚未通过。',(26,80),2180,25)
    for i,s in enumerate(samples):
        x=20+i*740;dr.rounded_rectangle((x,170,x+720,590),radius=10,fill='white');dr.text((x+16,184),s['title']+'｜原生1:1',font=font(27),fill=COL['ink'])
        im=crops[s['id']];board.paste(im,(x+(720-im.width)//2,235))
        lines(dr,s['groundNote'],(x+18,546),680,20)
    for i,r in enumerate(roads):
        x=20+i*1110;dr.rounded_rectangle((x,610,x+1090,1050),radius=10,fill='white');dr.text((x+18,626),r['label'],font=font(27),fill=COL['ink']);board.paste(r['zoom'],(x+18,685))
        tx=x+610;lines(dr,'4×最近邻像素格放大，仅辅助量读；无新增原生细节。\n人工边缘判读误差约±2px。\n灰度记录只作支持，不是自动识路。\n两种路向像素宽相近，不等于地面米数相同。',(tx,690),450,23)
    dr.text((24,1080),'原位地面参照框：仅尺寸对照，不裁楼、不移动A2、不判装箱通过',font=font(30),fill=COL['ink']);board.paste(overlay,(20,1140))
    y=1140
    for paragraph in [f"来源：规划建议地块 {block['id']}，并非A2已有地块。",'试尺：8m次干路 ↔ 约54px，6.75px/m。米数是设计选择，不是旧图标定。','紫框62.5°、绿框45°均为假设，叠在同一原生图上比较。框的位置任意，不是已测道路边界。',f"中心线围合面积约{block['centrelineEnclosedAreaMetres2']:.0f}m²，不等于净可用地块。",'完整楼体图像可跨地面框。不能按影像包围框裁楼，也不能把屋顶范围当占地。','本次没有给闭合地脚、统一相机或容纳栋数PASS；未知部分保留。','素材量读基准：以原生1:1看入口、门窗、层间与街沿。暂不据此更改正式游戏镜头。']:
        y=lines(dr,paragraph,(1580,y),620,25)+28
    dr.text((24,2202),'两次高尺寸均未命中；本板无新Images请求，旧源不改，普通生产仍暂停。',font=font(26),fill=COL['orange'])
    board.save(HERE/'scale-board.png');board.save(HERE/'scale-board-preview.jpg',quality=92,subsampling=0)
    notes={'status':'measurement-and-design-board-not-production-approved','A2Source':str(A2),'A2SHA256':protected[str(A2)],'roadWidthEvidence':{'southNormal':ns,'eastWestNormal':ew,'boundaryScanLegacyPixels':54,'graySupportNotSemantic':True,'cameraOrMetresMeasured':False,'excludedCut':'y1000 min/max-neutral includes isolated curb/shadow pixels; not used as semantic asphalt width'},'samples':samples,'readabilityObservation':{'sourcePixelsPerCSSPixel':1,'physicalDPRNotClaimed':True,'fixedObservationWindowNativePixels':[620,420],'formalClosestGameCameraFrozen':False,'mustDiscern':['entrance/door threshold','facade window separation','street/sidewalk boundary'],'differentObjectsCannotGivePhysicalScaleRatio':True},'representativeDesignBlock':block,'designTrial':{'nominalPixelsPerMetre':6.75,'source':'54px reference /8m proposed new design road','notMeasuredMapMetres':True,'groundProjectionCases':projected,'placementIsDiagnosticOnly':True,'closedBuildingGroundPolygonsAvailable':False,'fitPassed':False},'parentSourceHashes':protected,'newImageRequests':0,'sourceImagesResized':False,'rulerMagnificationOnly':4,'boardPreviewJPEGNotPixelProof':True,'productionReady':False}
    def card(title,im,caption):return '<article><h3>'+html.escape(title)+'</h3><div class="scroll"><img src="'+embed(im)+'" width="'+str(im.width)+'" height="'+str(im.height)+'"></div><p>'+html.escape(caption)+'</p></article>'
    cards=''.join(card(s['title']+'｜原生1:1',crops[s['id']],s['groundNote']) for s in samples)
    rcards=''.join(card(r['label']+'｜4×像素格量读',r['zoom'],'4×最近邻，仅测边缘；并非高原生。约±2px人工误差。') for r in roads)
    ccards=''.join(card(c['title']+'｜620×420原生观察窗',c['image'],'不同对象／不同构图。保持源像素1:1，不据包围框推真实楼体大小。') for c in comparisons)
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A2原生标尺与街坊试排对照</title><style>body{margin:20px;background:#eef3f4;color:#20333b;font:17px/1.65 system-ui}h1{font-size:29px}h2{margin-top:32px}.note{padding:16px;background:#fff4df;border-left:5px solid #bf6427}.grid{display:grid;grid-template-columns:repeat(3,minmax(660px,1fr));gap:16px;overflow:auto}article{background:white;padding:16px;border-radius:8px;min-width:0}h3{font-size:21px}.scroll{height:440px;overflow:auto;background:#e3e9ea}.scroll img{max-width:none;display:block}.wide .scroll{height:780px}p{max-width:1100px}.two{grid-template-columns:repeat(2,minmax(660px,1fr))}code{background:#e1e7e9;padding:2px 5px}a{color:#166e77}</style><h1>A2原生可读标尺 ＋ 代表街坊试排对照</h1><p class="note"><b>这是既有图像量读板，不是新城市图，也不是生产放行。</b>1源像素对应1CSS像素；未声称物理设备DPR，也未锁正式游戏最近镜头。窄屏请在各观察窗内滚动，不通过缩图制造“细节通过”。</p><h2>1．认可A2的三类主体</h2><div class="grid">'''+cards+'''</div><h2>2．两种路向的法向宽度</h2><p>南口两处约53px，东西路三处约54px；人工路缘判读约±2px。既有边界水平扫线54px可作设计参考，但不是同一测量方向。灰度仅支持目视判断，不自动认路。相近像素宽不证明相同米数或相机角。</p><div class="grid two">'''+rcards+'''</div><h2>3．代表地面框与原位楼群对照</h2><p>新建议B-04-04的中心线围合框。8m↔54px是可逆设计试尺；紫62.5°／绿45°为两种投影假设。叠框位置任意，<b>不是A2已有地块，不据此裁楼或判装下</b>。地脚未闭合的建筑保持未知，影像包围框不是地面占地。</p><article class="wide"><div class="scroll"><img src="'''+embed(overlay)+'''" width="1536" height="1024"></div></article><h2>4．已有探针与A2的原生观察窗</h2><p>仅观察入口、门窗、层间与街沿的可辨程度；不同对象不能据裁片宽高计算真实缩小倍率。两次实验实际1674×940和1672×941，均不是所请求4K。</p><div class="grid">'''+ccards+'''</div><h2>仍未通过的部分</h2><p>统一米制映射、可用地块退让／闭合地脚、真实近景展示要求及图区预算仍未定。试算几十张不是开工数量；本板不确认64格、全城覆盖或最终图数。没有新Images请求，D保持暂停。</p><p><a href="scale-board.png">完整诊断板PNG</a> · <a href="measurement-record.json">尺寸／坐标／来源记录</a> · <a href="../capacity-proof/RESULT.md">高尺寸实测结果</a></p></html>'''
    # Split self-contained pages rather than downsampling evidence to fit a
    # single inline preview. Each page retains its native observation pixels.
    frame_start=doc.index('<article class="wide">')
    frame_end=doc.index('</article>',frame_start)+len('</article>')
    frame_fragment=doc[frame_start:frame_end]
    frame_doc='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>原生地面参照框</title><style>body{font:18px/1.7 system-ui;background:#eef3f4;margin:20px;color:#20333b}.scroll{overflow:auto;height:1050px;background:white}.scroll img{max-width:none;display:block}p{max-width:1100px}</style><h1>同一A2原生图上的设计参照框</h1><p>8m↔约54px为可逆试尺。紫62.5°／绿45°只是两种投影假设，框位置任意，不是A2实测地块。中心线围合不等于净可用地块；不能按图像包围框裁楼或判定装下。本图未缩放；不是新增城市美术。</p>'+frame_fragment+'<p><a href="index.html">返回三类主体、道路和近景对照</a> · <a href="measurement-record.json">数据及来源</a></p></html>'
    doc=doc[:frame_start]+'<article><p><a href="frame.html">打开1536×1024原生地面参照框（独立自含页，未缩放）</a>。分页仅减少单页传输体积，不删观察项或降低原生采样。</p></article>'+doc[frame_end:]
    assert len(doc.encode())<5*1024*1024 and len(frame_doc.encode())<5*1024*1024
    (HERE/'index.html').write_text(doc)
    (HERE/'frame.html').write_text(frame_doc)
    assert all(sha(Path(p))==h for p,h in protected.items())
    notes['sourceHashesUnchangedAfterRender']=True;notes['htmlBytes']=len(doc.encode());notes['boardSize']=list(board.size)
    notes['frameHtmlBytes']=len(frame_doc.encode());notes['renderCodeSHA256']=sha(Path(__file__))
    dump('measurement-record.json',notes)
    outputs=[p for p in HERE.iterdir() if p.is_file() and p.name!='delivery-files.json' and p.suffix in {'.png','.jpg','.html','.json'}]
    dump('delivery-files.json',{'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(outputs)],'uniqueFileCount':len(outputs),'manifestExcludedFromOwnInventory':True,'generatedArtifactsNotNewNativeRegions':True})
    print(json.dumps({'status':'board-created-not-production-approved','htmlBytes':len(doc.encode()),'boardSize':list(board.size),'outputArtifacts':len(outputs),'southNormalPixels':[c['nominalNormalSpanPixels'] for c in ns],'eastWestNormalPixels':[c['nominalNormalSpanPixels'] for c in ew],'sourceHashesUnchanged':True,'newImageRequests':0},ensure_ascii=False))
if __name__=='__main__':make()
