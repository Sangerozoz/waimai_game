#!/usr/bin/env python3
"""Draw a clearly labelled city-layout proposal, not final generated artwork."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ART = HERE.parents[1]
ZONING = ART / '2026-11-02-county-zoning/selection.json'
REFERENCE = ART / '2026-11-05-modular-map-kit/revision-009/references/layout25/approved-25-assembly-reference.jpg'
FONT = '/System/Library/Fonts/STHeiti Medium.ttc'
BOX = (52, 170, 1052, 1010)
REGIONS = [
    ('C01', '西北河谷与林地', '自然背景为主；蓝内少量低层院落', '#e2ead6'),
    ('C02', '北部居住与校园', '住宅、学校；由疏到密进入城区', '#e9e8d6'),
    ('C03', '东北低密与自然', '低层聚落、公园与外围树林', '#e0ebd9'),
    ('C04', '西部社区与工坊', '生活社区、小工坊、服务院落', '#e8dfcd'),
    ('C05', '繁华商业核心', '市场、街铺、办公与混合住宅', '#f0dfbc'),
    ('C06', '东部文教与公园', '公建、住宅、滨水绿地组合', '#dce8e2'),
    ('C07', '西南郊居与田园', '院落、菜地；渐疏到自然', '#e3e6cd'),
    ('C08', '南部生活与运动', '住宅、邻里中心、运动休闲', '#e8e1d3'),
    ('C09', '东南低密与外围', '低密居住过渡，水系与自然背景', '#e0e9d4'),
]
ROADS = [
    ('东西主干', [(0.18, .55), (.83, .55)]),
    ('南北主干', [(.55, .215), (.55, .817)]),
    ('中部连接环', [(.34,.30),(.67,.30),(.72,.36),(.72,.70),(.67,.75),(.34,.75),(.29,.70),(.29,.36),(.34,.30)]),
    ('东部文教支路', [(.55,.44),(.80,.44)]),
    ('西部社区支路', [(.18,.44),(.40,.44),(.40,.55)]),
    ('南部生活支路', [(.40,.55),(.40,.80),(.72,.80),(.72,.70)]),
]
RIVERS = [
    [(0.24,0),(.21,.12),(.18,.27),(.11,.33),(0,.36)],
    [(.18,.27),(.32,.31),(.45,.27),(.60,.31),(.69,.38),(.74,.50),(.74,.65),(.85,.84),(.90,1)],
]


def font(size):
    return ImageFont.truetype(FONT, size)


def xy(p):
    return (BOX[0] + p[0] * (BOX[2]-BOX[0]), BOX[1] + p[1] * (BOX[3]-BOX[1]))


def main():
    target = HERE/'city-layout-draft-v1.png'
    if target.exists():
        raise SystemExit('Keep existing review version; do not overwrite')
    z = json.loads(ZONING.read_text())['regions']
    red = z['map']['worldBoundsMetresApprox']
    def normalized(key):
        a = z[key]['worldBoundsMetresApprox']
        w, h = red['maxX']-red['minX'], red['maxY']-red['minY']
        return [(a['minX']-red['minX'])/w, (red['maxY']-a['maxY'])/h,
                (a['maxX']-red['minX'])/w, (red['maxY']-a['minY'])/h]
    city, core = normalized('city'), normalized('urban')
    image = Image.new('RGB',(1480,1270),'#f7f5ec')
    draw = ImageDraw.Draw(image)
    draw.text((52,32),'整城总体布局草案  ·  9区预案',font=font(39),fill='#243e48')
    draw.text((52,91),'先审城市结构，再做相邻两区；不是最终美术，也不是已完成整城。',font=font(23),fill='#5a6b6b')
    draw.text((52,134),'平面关系示意｜正式图采用统一斜俯视；此处线位不代表旧路精确配准',font=font(19),fill='#677973')
    entries=[]
    for index,(rid,name,note,color) in enumerate(REGIONS):
        row,col=divmod(index,3)
        bounds=(col/3,row/3,(col+1)/3,(row+1)/3)
        a,b=xy(bounds[:2]),xy(bounds[2:])
        draw.rectangle((*a,*b),fill=color)
        entries.append({'id':rid,'name':name,'role':note,'row':row,'column':col,
                        'normalizedBounds':bounds,'status':'layout-proposal-not-generated-art'})
    # Water references the broad north/west river valley and central branch in the approved assembly.
    for river in RIVERS:
        draw.line([xy(p)for p in river],fill='#a5ccd0',width=28,joint='curve')
        draw.line([xy(p)for p in river],fill='#689fae',width=14,joint='curve')
    for name,points in ROADS:
        q=[xy(p)for p in points]
        draw.line(q,fill='#fff9ed',width=20,joint='curve')
        draw.line(q,fill='#697d83',width=10,joint='curve')
    for n in (1,2):
        x=BOX[0]+(BOX[2]-BOX[0])*n/3
        y=BOX[1]+(BOX[3]-BOX[1])*n/3
        for t in range(BOX[1],BOX[3],18):draw.line((x,t,x,min(t+10,BOX[3])),fill='#a3a58f',width=2)
        for t in range(BOX[0],BOX[2],18):draw.line((t,y,min(t+10,BOX[2]),y),fill='#a3a58f',width=2)
    # Match the old user-defined three-zone relative proportions, not old road geometry.
    for bounds,color,width in [([0,0,1,1],'#c96259',5),(city,'#3680a9',5),(core,'#38946a',5)]:
        a,b=xy(bounds[:2]),xy(bounds[2:]);draw.rectangle((*a,*b),outline=color,width=width)
    for entry in entries:
        row,col=entry['row'],entry['column']
        x=BOX[0]+col*(BOX[2]-BOX[0])/3+14
        y=BOX[1]+row*(BOX[3]-BOX[1])/3+16
        draw.rounded_rectangle((x-5,y-4,x+298,y+84),radius=9,fill='#faf9f0')
        draw.text((x,y),entry['id']+'  '+entry['name'],font=font(24),fill='#29434c')
        note=entry['role']
        # Two short lines remain readable in the full-resolution review image.
        split=note.find('；')
        lines=note.split('；') if split>=0 else [note[:13],note[13:]]
        for i,line in enumerate(lines):draw.text((x,y+36+i*23),line,font=font(18),fill='#53676b')
    # First adjacency exercise, not permission to generate these regions yet.
    for col in (1,2):
        a,b=xy((col/3,1/3)),xy(((col+1)/3,2/3))
        draw.rectangle((a[0]+7,a[1]+7,b[0]-7,b[1]-7),outline='#c18a22',width=5)
    portals=[]
    for pid,y in [('P01',.44),('P02',.55)]:
        p=xy((2/3,y));draw.ellipse((p[0]-10,p[1]-10,p[0]+10,p[1]+10),fill='#ffdb70',outline='#9c7017',width=3)
        draw.text((p[0]+14,p[1]-13),pid,font=font(20),fill='#714d00')
        portals.append({'id':pid,'between':['C05','C06'],'normalizedPoint':[2/3,y],
                        'status':'suggested-portal-not-frozen-pixel-contract'})
    x=1092
    draw.text((x,180),'三层边界',font=font(27),fill='#29434c')
    for i,(color,label,detail)in enumerate([
        ('#c96259','红：地图展示范围','外围自然与零散背景房屋'),
        ('#3680a9','蓝：经营 / 配送范围','取送点与完整路线均在蓝内'),
        ('#38946a','绿：繁华核心','向蓝绿之间自然降低密度')]):
        y=233+i*91;draw.line((x,y+12,x+35,y+12),fill=color,width=5)
        draw.text((x+46,y),label,font=font(21),fill='#29434c')
        draw.text((x,y+35),detail,font=font(18),fill='#607174')
    draw.text((x,533),'先验证 C05 ＋ C06',font=font(25),fill='#926318')
    for i,line in enumerate(['两个整区画面真正接上','P01 / P02 是建议接头','同一Tiled总图、同一坐标','跨区导航不能跳段穿楼']):
        draw.text((x,575+i*32),line,font=font(20),fill='#53676b')
    draw.text((x,743),'原25图总图参考',font=font(23),fill='#29434c')
    with Image.open(REFERENCE)as ref:
        thumb=ref.convert('RGB');thumb.thumbnail((330,305));image.paste(thumb,(x,782))
    draw.text((x,1097),'只借楼群、体量与疏密关系',font=font(18),fill='#607174')
    draw.text((52,1043),'图块编号不是功能硬切：一个区可同时含城区、郊区和自然过渡。',font=font(23),fill='#304e58')
    draw.text((52,1085),'灰线只定主干和连接关系；次街、门口与小路由整区画面确定后再描入导航。',font=font(21),fill='#53676b')
    draw.text((52,1127),'9区为优先评估方案；若目标近景细节不足，再比较16区，不靠插值宣称高清。',font=font(21),fill='#53676b')
    draw.text((52,1169),'旧地图、用户布局与已通过导航小样均不覆盖。此稿尚待用户确认。',font=font(21),fill='#53676b')
    image.save(target)
    (HERE/'layout-draft-v1.json').write_text(json.dumps({
        'status':'planning-proposal-awaiting-user-review','regionCount':len(entries),
        'regions':entries,'relativeCityBounds':city,'relativeUrbanBounds':core,
        'zoningSource':str(ZONING),'zoningMeaningPreserved':True,
        'roadSkeletonProposal':[{'id':name,'normalizedPoints':points}for name,points in ROADS],
        'riverRelationshipsReference':str(REFERENCE),'riverLinesAreProposedNotOldGeometry':RIVERS,
        'firstAdjacentPair':['C05','C06'],'suggestedPortals':portals,
        'finalCameraOrScaleFrozen':False,'artworkGenerated':False,
        'oldSourceOrUserFilesWritten':False,
    },ensure_ascii=False,indent=2)+'\n')
    # A readable close-up of the first two adjacent planning regions.
    crop=image.crop((BOX[0]+(BOX[2]-BOX[0])//3-10,BOX[1]+(BOX[3]-BOX[1])//3-10,
                     BOX[2]+10,BOX[1]+2*(BOX[3]-BOX[1])//3+10))
    crop.save(HERE/'first-adjacent-pair-draft.png')
    print(json.dumps({'overview':str(target),'regionCount':len(entries),
                      'firstPair':['C05','C06'],'nativeArtworkGenerated':False},ensure_ascii=False))


if __name__=='__main__':
    main()
