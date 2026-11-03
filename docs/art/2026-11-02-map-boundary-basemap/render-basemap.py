"""Export precise, north-up selection sheets from existing offline geometry.

This is an art/planning export, not a game implementation or game test.
PNG pixels map back to source road metres via the adjacent manifest.
"""
from pathlib import Path
from collections import defaultdict, deque
import hashlib
import json
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
SOURCE = PROJECT / 'delivery-game/assets/resources/map-sample/city.json'
DATA = json.loads(SOURCE.read_text())
NODES = {n['id']: (n['x'], n['y']) for n in DATA['nodes']}
FONT_FILE = '/System/Library/Fonts/STHeiti Light.ttc'
FONT_BOLD = '/System/Library/Fonts/STHeiti Medium.ttc'
INK = '#29372f'
MUTED = '#626b63'
OUT = []


def font(size, bold=False):
    path = FONT_BOLD if bold and Path(FONT_BOLD).exists() else FONT_FILE
    return ImageFont.truetype(path, size)


def render(name, title, subtitle, bounds, width, height, grid_step, inset=None):
    image = Image.new('RGB', (width, height), '#fcfbf7')
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = 175, 310, width - 155, height - 255
    min_x, min_y, max_x, max_y = bounds
    scale = min((right-left)/(max_x-min_x), (bottom-top)/(max_y-min_y))
    plot_w, plot_h = (max_x-min_x)*scale, (max_y-min_y)*scale
    x0 = (left+right-plot_w)/2
    y0 = (top+bottom-plot_h)/2
    plot = (round(x0), round(y0), round(x0+plot_w), round(y0+plot_h))
    # All geometry is rendered into a separate data viewport for exact clipping.
    layer = Image.new('RGB', (plot[2]-plot[0], plot[3]-plot[1]), '#f2f0e8')
    geo = ImageDraw.Draw(layer)

    def xy(p):
        return ((p[0]-min_x)*scale, (max_y-p[1])*scale)

    def visible(ps, pad=0):
        return ps and max(p[0] for p in ps)>=min_x-pad and min(p[0] for p in ps)<=max_x+pad and max(p[1] for p in ps)>=min_y-pad and min(p[1] for p in ps)<=max_y+pad

    area_colors = {'residential':'#e9e6dd','commercial':'#eae2d7',
                   'farmland':'#e8eddc','green':'#dce7d3','water':'#bed8d9'}
    area_order = {'residential':0,'commercial':1,'farmland':2,'green':3,'water':4}
    for area in sorted(DATA['areas'], key=lambda a: area_order.get(a['kind'],0)):
        ps = area['points']
        if len(ps)>=3 and visible(ps):
            geo.polygon([xy(p) for p in ps], fill=area_colors.get(area['kind'],'#e9e6dd'))
    for water in DATA['waterways']:
        if len(water)>1 and visible(water, 20):
            geo.line([xy(p) for p in water], fill='#b4d1d3', width=max(5,round(20*scale)), joint='curve')
    for polygon in DATA['buildings']:
        if len(polygon)>=3 and visible(polygon):
            geo.polygon([xy(p) for p in polygon], fill='#babdb6', outline='#a7ada5')

    roads = []
    for road in DATA['roads']:
        ps = [NODES[n] for n in road['nodes'] if n in NODES]
        if len(ps)<2 or not visible(ps,30):
            continue
        major = road['kind'] in ['primary','secondary','tertiary']
        stroke = max(3 if major else 2, round(road['width']*scale))
        roads.append((major, road['width'], ps, stroke, road['id']))
    roads.sort(key=lambda r:(r[0],r[1]))
    for major, _, ps, stroke, _ in roads:
        geo.line([xy(p) for p in ps], fill='#a3a49b', width=stroke+3, joint='curve')
    for major, _, ps, stroke, _ in roads:
        geo.line([xy(p) for p in ps], fill='#fffdf7' if major else '#f9f8f2', width=stroke, joint='curve')

    # Grid over the geometry: these are measured cells, not fictional city blocks.
    xs = list(range(math.ceil(min_x/grid_step)*grid_step, round(max_x), grid_step))
    ys = list(range(math.ceil(min_y/grid_step)*grid_step, round(max_y), grid_step))
    for x in xs:
        if x>min_x: geo.line([xy((x,min_y)),xy((x,max_y))], fill='#c8c9bd',width=1)
    for y in ys:
        if y>min_y: geo.line([xy((min_x,y)),xy((max_x,y))], fill='#c8c9bd',width=1)

    # Original POIs are reference locations; operating catalog is generated later.
    points = []
    for index, poi in enumerate(DATA['pois']):
        p = NODES.get(poi['node'])
        if p and min_x<=p[0]<=max_x and min_y<=p[1]<=max_y:
            points.append((index, poi, p))
            x,y = xy(p)
            radius = 8 if grid_step<=500 else 6
            color = '#d88033' if poi['kind']=='restaurant' else '#596d77'
            geo.ellipse((x-radius-2,y-radius-2,x+radius+2,y+radius+2),fill='#fffdf8')
            geo.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color)
    placed = []
    for index, poi, p in points:
        if index>=8: continue
        x,y = xy(p)
        label = ('起点参考 · ' if index==0 else '')+poi['name']
        f = font(31 if grid_step<=500 else 27, index==0)
        box = geo.textbbox((0,0),label,font=f)
        tw,th = box[2]-box[0]+22,box[3]-box[1]+18
        candidates = [(x+20,y-44),(x+20,y+14),(x-tw-20,y-44),(x-tw-20,y+14),(x+20,y-90),(x+20,y+65)]
        for tx,ty in candidates:
            b = (tx,ty,tx+tw,ty+th)
            if b[0]<6 or b[1]<6 or b[2]>layer.width-6 or b[3]>layer.height-6: continue
            if any(not(b[2]+10<q[0] or b[0]-10>q[2] or b[3]+10<q[1] or b[1]-10>q[3]) for q in placed): continue
            geo.line([(x,y),(max(tx,min(x,tx+tw)),max(ty,min(y,ty+th)))],fill='#767f72',width=2)
            geo.rounded_rectangle(b, radius=6, fill='#fffdf8', outline='#c4c5b9',width=1)
            geo.text((tx+11,ty+7-box[1]),label,font=f,fill=INK)
            placed.append(b)
            break

    if inset:
        a,b,c,d = inset
        corners = [xy((a,d)),xy((c,d)),xy((c,b)),xy((a,b)),xy((a,d))]
        # Reference frame only: explicitly not the user's production boundary.
        geo.line(corners,fill='#bd7339',width=5)
        px,py=xy((a,d))
        label='图2街区放大范围（非制作边界）'
        ff=font(29,True)
        tb=geo.textbbox((0,0),label,font=ff)
        geo.rectangle((px,py-49,px+tb[2]+20,py-2),fill='#fff9ed')
        geo.text((px+10,py-44-tb[1]),label,font=ff,fill='#9c5726')

    image.paste(layer,(plot[0],plot[1]))
    draw.rectangle(plot,outline='#9ca596',width=3)
    # Column/row identifiers remain outside geometry to keep marking space free.
    nx = math.ceil((max_x-min_x)/grid_step)
    ny = math.ceil((max_y-min_y)/grid_step)
    f_grid=font(29,True)
    for i in range(nx):
        gx=plot[0]+(i+.5)*grid_step*scale
        draw.text((gx,plot[1]-42),chr(65+i),font=f_grid,fill=MUTED,anchor='mm')
        draw.text((gx,plot[3]+35),chr(65+i),font=f_grid,fill=MUTED,anchor='mm')
    for i in range(ny):
        gy=plot[1]+(i+.5)*grid_step*scale
        draw.text((plot[0]-42,gy),str(i+1),font=f_grid,fill=MUTED,anchor='mm')
        draw.text((plot[2]+42,gy),str(i+1),font=f_grid,fill=MUTED,anchor='mm')

    draw.text((175,65),title,font=font(70,True),fill=INK)
    draw.text((178,165),subtitle,font=font(32),fill=MUTED)
    draw.text((178,218),f'北向上 · 每格 {grid_step} 米 · 请画闭合圈，圈内制作街区及配送',font=font(31),fill=MUTED)
    # A north arrow inside top-right edge of the plot.
    ax,ay=plot[2]-76,plot[1]+110
    draw.polygon([(ax,ay-60),(ax-25,ay+12),(ax,ay-5),(ax+25,ay+12)],fill='#40523f')
    draw.text((ax,ay+45),'北',font=font(30,True),fill=INK,anchor='mm')
    # Measured scale bar in a quiet bottom corner.
    bar_m=500 if grid_step<=500 else 1000
    bx,by=plot[0]+45,plot[3]-55
    bw=bar_m*scale
    draw.rectangle((bx-18,by-57,bx+bw+30,by+22),fill='#fffdf7')
    draw.rectangle((bx,by-8,bx+bw/2,by+3),fill='#40523f')
    draw.rectangle((bx+bw/2,by-8,bx+bw,by+3),fill='#fffdf7',outline='#40523f',width=2)
    draw.text((bx,by-38),'0',font=font(25),fill=INK)
    draw.text((bx+bw,by-38),f'{bar_m}米',font=font(25),fill=INK,anchor='rt')
    legend_y=height-130
    legend=[('#fffdf7','道路'),('#babdb6','已有建筑'),('#bed8d9','水系'),('#dce7d3','绿地/农地'),('#d88033','原始取餐点参考'),('#596d77','原始送达点参考')]
    cursor=178
    for color,text in legend:
        draw.rectangle((cursor,legend_y,cursor+36,legend_y+26),fill=color,outline='#9fa89b',width=1)
        draw.text((cursor+49,legend_y-4),text,font=font(29),fill=MUTED)
        cursor+=49+draw.textlength(text,font=font(29))+52
    draw.text((178,height-62),'现有数据参考，非行政县界；未圈定制作范围。© OpenStreetMap contributors',font=font(27),fill=MUTED)
    path=ROOT/(name+'.png')
    image.save(path,optimize=True)
    record={
        'id':name,'path':path.name,'width':width,'height':height,
        'source':str(SOURCE.relative_to(PROJECT)),
        'worldBoundsMetres':{'minX':min_x,'minY':min_y,'maxX':max_x,'maxY':max_y},
        'pixelViewport':{'left':plot[0],'top':plot[1],'right':plot[2],'bottom':plot[3]},
        'pixelsPerMetre':scale,
        'pixelToWorld':{
            'x':'minX+(pixelX-left)/pixelsPerMetre',
            'y':'maxY-(pixelY-top)/pixelsPerMetre'},
        'gridMetres':grid_step,'northUp':True,'sourceRoadsDrawn':len(roads),
        'originalPOIsShown':len(points),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'status':'awaiting-user-closed-boundary-selection-not-production-map'}
    OUT.append(record)
    return record


if __name__=='__main__':
    core=(-4500,-1500,-500,1500)
    render('01-county-overview','澄川县 · 路网总览 / 圈选底图',
           '查看现有路网与周边；橙框对应图2街区放大图，不是制作范围',
           (-6000,-6500,6000,6500),3800,4400,1000,inset=core)
    render('02-county-core','澄川县 · 街区放大 / 圈选用',
           '保留真实道路与已有建筑位置；你圈定后，外围再用绿地与山脉收边',
           core,4200,3600,500)
    manifest={
        'date':'2026-11-02','purpose':'用户圈选街区制作与配送边界',
        'sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'rendering':'deterministic data plot using original geometry; not AI-painted geometry',
        'selection':None,'artworkProductionStarted':False,'images':OUT,
        'rules':['圈内制作街区及取送地点，配送路线全程在圈内。',
                 '圈外以绿地/树林/山脉作背景，不产生配送点。',
                 '不规则闭合圈线保留形状，不替换为包围矩形。',
                 '圈定后再核对道路连接及跨边界绕行；本次没有裁剪游戏路网。']}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'path':r['path'],'size':[r['width'],r['height']],'roads':r['sourceRoadsDrawn'],'poi':r['originalPOIsShown']} for r in OUT],ensure_ascii=False))
