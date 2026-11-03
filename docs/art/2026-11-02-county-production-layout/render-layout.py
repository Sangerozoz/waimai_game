"""Render new measured planning diagrams from data; never edit approved art."""
from pathlib import Path
import importlib.util
import json
import hashlib
import math
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('layout_analysis',ROOT/'analyze-layout.py')
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
L=json.loads((ROOT/'layout-data.json').read_text())
R=json.loads((ROOT/'sample-route-reference.json').read_text())
INK='#29382f';MUTED='#697269';RED='#cd5147';BLUE='#417eaa';GREEN='#438455';AMBER='#c1842c'
FONT='/System/Library/Fonts/STHeiti Light.ttc'
BOLD='/System/Library/Fonts/STHeiti Medium.ttc'
OUTPUT=[]
def font(size,bold=False):return ImageFont.truetype(BOLD if bold and Path(BOLD).exists() else FONT,size)

def polyclip(points,b):
    p=list(points)
    for axis,bound,sign in [(0,b['minX'],1),(0,b['maxX'],-1),(1,b['minY'],1),(1,b['maxY'],-1)]:
        result=[]
        if not p:break
        for a,c in zip(p[-1:]+p[:-1],p):
            ia=(a[axis]-bound)*sign>=0;ic=(c[axis]-bound)*sign>=0
            if ia!=ic:
                t=(bound-a[axis])/(c[axis]-a[axis]);result.append((a[0]+(c[0]-a[0])*t,a[1]+(c[1]-a[1])*t))
            if ic:result.append(c)
        p=result
    return p

class Sheet:
    def __init__(self,name,title,subtitle,bounds):
        self.name=name;self.bounds=bounds;self.im=Image.new('RGB',(4400,4050),'#fcfbf7');self.d=ImageDraw.Draw(self.im)
        self.scale=min(3100/(bounds['maxX']-bounds['minX']),3040/(bounds['maxY']-bounds['minY']))
        self.left=170+(3100-(bounds['maxX']-bounds['minX'])*self.scale)/2
        self.top=350+(3040-(bounds['maxY']-bounds['minY'])*self.scale)/2
        self.right=self.left+(bounds['maxX']-bounds['minX'])*self.scale
        self.bottom=self.top+(bounds['maxY']-bounds['minY'])*self.scale
        self.d.text((170,64),title,font=font(78,True),fill=INK)
        self.d.text((174,180),subtitle,font=font(35),fill=MUTED)
        self.d.text((174,244),'用户红 / 蓝 / 绿边界不变 · 棕色旧索引框不参与 · 当前为制作规划图',font=font(32),fill=MUTED)
        self.panel_y=385
    def xy(self,p):return(self.left+(p[0]-self.bounds['minX'])*self.scale,self.top+(self.bounds['maxY']-p[1])*self.scale)
    def rect(self,b,color,width=3,fill=None,dash=False):
        l,t=self.xy((b['minX'],b['maxY']));r,v=self.xy((b['maxX'],b['minY']))
        if fill:ImageDraw.Draw(self.im,'RGBA').rectangle((l,t,r,v),fill=fill)
        if dash:
            for a,c in [((l,t),(r,t)),((r,t),(r,v)),((r,v),(l,v)),((l,v),(l,t))]:self.dashed(a,c,color,width)
        else:self.d.rectangle((l,t,r,v),outline=color,width=width)
    def dashed(self,a,b,color,width=3):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        if length==0:return
        for start in range(0,math.ceil(length),27):
            end=min(start+15,length);self.d.line((a[0]+dx*start/length,a[1]+dy*start/length,a[0]+dx*end/length,a[1]+dy*end/length),fill=color,width=width)
    def line(self,ps,color,width=3):
        for a,b in zip(ps,ps[1:]):
            c=G.clip(a,b,self.bounds)
            if c:self.d.line([self.xy(c[0]),self.xy(c[1])],fill=color,width=width,joint='curve')
    def base(self,connectivity=False):
        self.d.rectangle((self.left,self.top,self.right,self.bottom),fill='#e7ecd9')
        self.rect(G.BOUNDS['city'],BLUE,fill=(246,242,232,255)) if self.name=='01-production-layout' else None
        colors={'water':'#c0d7d6','green':'#dfe8d4','farmland':'#e7ebd9','commercial':'#eae3d8','residential':'#eeebe3'}
        for area in sorted(G.DATA['areas'],key=lambda a:a['kind']=='water'):
            points=polyclip(area['points'],self.bounds)
            if len(points)>=3:self.d.polygon([self.xy(p) for p in points],fill=colors.get(area['kind'],'#eeebe3'))
        # Landscape is a proposal: no outside-city streets/buildings in this draft.
        if self.name=='01-production-layout':
            city=G.BOUNDS['city'];outer=G.BOUNDS['map']
            bands=[{'minX':outer['minX'],'maxX':outer['maxX'],'minY':city['maxY'],'maxY':outer['maxY']},
                   {'minX':outer['minX'],'maxX':outer['maxX'],'minY':outer['minY'],'maxY':city['minY']},
                   {'minX':outer['minX'],'maxX':city['minX'],'minY':city['minY'],'maxY':city['maxY']},
                   {'minX':city['maxX'],'maxX':outer['maxX'],'minY':city['minY'],'maxY':city['maxY']}]
            for b in bands:self.rect(b,'#e2e9d5',1,fill=(220,231,205,220))
            # Stylized ridges mark proposed landscape use, not measured elevations.
            for cx,cy,size in [(-2050,1210,210),(-1610,1300,260),(-1080,1170,220),(-430,1290,210),(-65,100,130)]:
                ps=[(cx-size,cy-size*.34),(cx,cy+size*.60),(cx+size,cy-size*.34)]
                self.line(ps,'#9ba989',4)
            for x in range(-2500,-500,150):
                for y in [-1590]:
                    p=self.xy((x,y));self.d.ellipse((p[0]-8,p[1]-8,p[0]+8,p[1]+8),fill='#abbc96')
        for area in G.DATA['areas']:
            if area['kind']!='water':continue
            points=polyclip(area['points'],self.bounds)
            if len(points)>=3:self.d.polygon([self.xy(p) for p in points],fill='#c0d7d6')
        for ps in G.DATA['waterways']:
            self.line(ps,'#b4d0d0',max(5,round(18*self.scale)))
        for p in G.DATA['buildings']:
            if not p or not all(G.inside(v,G.BOUNDS['city']) for v in p):continue
            points=polyclip(p,self.bounds)
            if len(points)>=3:self.d.polygon([self.xy(v) for v in points],fill='#bbbcb0',outline='#a7ab9e')
        segments=L['roadSegmentsClippedForDrawingOnly'];connected=set(L['mainConnectedNodes'])
        segments=sorted(segments,key=lambda s:s['width'])
        for s in segments:
            active=s['from'] in connected and s['to'] in connected
            self.line([s['a'],s['b']],'#7c8c81' if connectivity and active else '#b69790' if connectivity else '#979d90',max(3,round(s['width']*self.scale)+3))
        for s in segments:
            self.line([s['a'],s['b']],'#fffdf6',max(1,round(s['width']*self.scale)))
        step=500 if self.name!='03-first-sample' else 100
        for x in range(math.ceil(self.bounds['minX']/step)*step,math.ceil(self.bounds['maxX']),step):
            self.line([(x,self.bounds['minY']),(x,self.bounds['maxY'])],'#d8d8cc',1)
        for y in range(math.ceil(self.bounds['minY']/step)*step,math.ceil(self.bounds['maxY']),step):
            self.line([(self.bounds['minX'],y),(self.bounds['maxX'],y)],'#d8d8cc',1)
        self.d.rectangle((self.left,self.top,self.right,self.bottom),outline='#a4ab9b',width=2)
    def zones(self):
        for key,color in [('map',RED),('city',BLUE),('urban',GREEN)]:
            if self.name=='02-road-boundary' and key=='map':continue
            if self.name!='03-first-sample':self.rect(G.BOUNDS[key],color,7)
    def point(self,p,color,r=10):
        x,y=self.xy(p);self.d.ellipse((x-r-3,y-r-3,x+r+3,y+r+3),fill='#fffdf7');self.d.ellipse((x-r,y-r,x+r,y+r),fill=color)
    def label(self,p,text,color=INK,offset=(18,-48),size=33):
        x,y=self.xy(p);f=font(size,True);bb=self.d.textbbox((0,0),text,font=f);w=bb[2]-bb[0]+24;h=bb[3]-bb[1]+20
        tx,ty=x+offset[0],y+offset[1]
        tx=max(self.left+8,min(tx,self.right-w-8));ty=max(self.top+8,min(ty,self.bottom-h-8))
        self.d.line((x,y,tx+min(w,max(0,x-tx)),ty+h/2),fill=color,width=2)
        self.d.rounded_rectangle((tx,ty,tx+w,ty+h),radius=7,fill='#fffdf8',outline='#b8bcad',width=1)
        self.d.text((tx+12,ty+9-bb[1]),text,font=f,fill=color)
    def panel(self,title,lines,color=INK):
        x=3440;y=self.panel_y
        self.d.rectangle((x,y,x+70,y+7),fill=color)
        self.d.text((x,y+25),title,font=font(43,True),fill=color)
        y+=101
        for text in lines:
            self.d.text((x,y),text,font=font(32),fill=MUTED);y+=53
        self.panel_y=y+67
    def finish(self,caption):
        bx,by=self.left+30,self.bottom+72;metres=100 if self.name=='03-first-sample' else 500;w=metres*self.scale
        self.d.rectangle((bx-15,by-65,bx+w+60,by+15),fill='#fffdf7')
        self.d.rectangle((bx,by-6,bx+w/2,by+5),fill='#40543f');self.d.rectangle((bx+w/2,by-6,bx+w,by+5),fill='#fffdf7',outline='#40543f',width=2)
        self.d.text((bx,by-43),'0',font=font(27),fill=INK);self.d.text((bx+w,by-43),f'{metres}米',font=font(27),fill=INK,anchor='rt')
        nx,ny=self.right-68,self.top-85 if self.name=='02-road-boundary' else self.top+74;self.d.polygon([(nx,ny-45),(nx-22,ny+20),(nx,ny+3),(nx+22,ny+20)],fill='#40543f');self.d.text((nx,ny+55),'北',font=font(28,True),fill=INK,anchor='mm')
        self.d.text((175,3545),caption,font=font(34),fill=INK)
        self.d.text((175,3620),'原始道路 / 地块 / 水系共用地面坐标；图中功能分片、密度与样板范围为本轮布局建议。',font=font(31),fill=MUTED)
        self.d.text((175,3680),'静态制作规划，非成品画面或游戏运行结果；不改用户三层边界、不创建新经营规则。',font=font(31),fill=MUTED)
        self.d.text((175,3890),'2026-11-02 · 《送外卖》县城地图制作布局稿 · © OpenStreetMap contributors',font=font(29),fill=MUTED)
        p=ROOT/(self.name+'.png');self.im.save(p,optimize=True)
        OUTPUT.append({'path':p.name,'width':self.im.width,'height':self.im.height,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'worldBounds':self.bounds,'pixelsPerMetre':self.scale,'worldPixelOrigin':{'left':self.left,'top':self.top},'status':'layout-proposal-awaiting-user-review'})

def main():
    s=Sheet('01-production-layout','县城制作布局稿 · 三层分区与首块样板','先确定街区安排与制作顺序，沿用已认可画风；此图展示空间关系。',G.BOUNDS['map']);s.base();s.zones()
    for p,t,c,o in [((-1510,480),'U1 社区与水岸',GREEN,(-280,-75)),((-1150,230),'U2 沿街商住',GREEN,(-210,-90)),((-1500,-650),'U3 南部生活街区',GREEN,(-250,-40)),((-2220,80),'S1 西郊低密院落',BLUE,(-180,-45)),((-650,50),'S2 东郊居住与小店',BLUE,(-160,-45)),((-1570,765),'S3 北郊过渡',BLUE,(-210,-45)),((-1580,-1130),'S4 南郊住区',BLUE,(-150,-40)),((-1300,1260),'L1 山林背景带','#61764d',(-220,-25)),((-1150,-1570),'L2 草地与水岸','#61764d',(-190,-25)),((-2920,300),'L3 河谷绿地','#61764d',(-130,-45))]:s.label(p,t,c,o,31)
    s.rect(G.SAMPLE,AMBER,8,fill=(235,180,80,48));s.label((-1720,200),'A 首批精修样板',AMBER,(-245,-64),32);s.point(G.POINTS['1623821046'],AMBER,12)
    s.panel('边界与经营范围',['红框：整张地图，约3.3×3.3km','蓝框：建设与配送，约2.3×2.2km','绿框：繁华城区，约1.0×1.6km','棕色旧框已忽略。'],RED)
    s.panel('城区 / 绿框内',['主街商铺＋住宅与办公混合。','以3–6层为主，节点少量稍高楼。','沿街相对连续，保留河渠与绿地。','屋顶无树，色彩沿认可首页。'],GREEN)
    s.panel('郊区 / 蓝绿之间',['以1–3层住宅、小店与院落为主。','建筑间距更大，绿地更连续。','临主路适当集中，支路保持疏朗。','与城区渐变，不沿绿框切成硬墙。'],BLUE)
    s.panel('外围 / 红蓝之间',['北与东侧山林，南侧草地水岸。','西侧沿原河谷形成生态背景。','不设经营点、不作为配送通道。','山体为布景建议，不是测绘高程。'],'#61764d')
    s.panel('首块建议：榕树街食堂附近',['精修380×440m，范围全部在绿框内。','含起点、晴川广场与现有连接道路。','先完成完整镜头，再补周边接续。','外侧街区暂不随本轮开工。'],AMBER)
    s.finish('制作安排：先做 A 样板 → 扩展绿框城区 → 衔接四侧郊区 → 完成外围景观。')

    s=Sheet('02-road-boundary','道路与边缘收口 · 蓝框内经营','沿原始道路数据盘点，保持单行方向；不以外围背景区补通内部道路。',G.BOUNDS['city']);s.base(True);s.zones()
    for g in L['boundaryGroups']:
        if g['priority']!='main-road':continue
        s.point(g['point'],AMBER,11)
        off={'N':(-35,25),'E':(-100,-35),'S':(-35,-65),'W':(28,-35)}[g['side']]
        if g['id']=='B61':off=(30,-65)
        s.label(g['point'],g['id'],AMBER,off,31)
    for poi in L['rawPOIs'][:8]:
        s.point(poi['point'],GREEN if poi['mutuallyReachableFromStart'] else '#a3645c',9)
        if poi['name'] in ['榕树街食堂','青禾社区','云岸公寓']:s.label(poi['point'],poi['name'],INK,(18,-50),29)
    s.rect(G.SAMPLE,AMBER,6)
    for p,text in [((-2600,-160),'D1 西侧不连通支段'),((-2590,-790),'D2 西南边缘支段'),((-1880,-275),'D3 城中零散支段')]:s.label(p,text,'#9a655e',(30,-32),29)
    n=L['summary']
    s.panel('圈内道路的基础情况',[f'盘点到 {n["blueSourceGraphNodes"]} 个原始道路节点。',f'其中 {n["startMutuallyReachableNodes"]} 个可从起点往返。',f'原始地点目录 {n["rawPOIsInsideBlue"]} 处在蓝框内，均可往返。','统计不是已完成游戏验证。'],GREEN)
    s.panel('边界优先看这13组主路',[f'全部边界交点聚为 {n["boundaryCrossingGroups"]} 组。','图中仅标主路组，完整表另附CSV。','优先检查 B26 / B34 东侧主路、','B53 南侧主路及 B75 / B79 西侧路。','不是要求增加79个设施或关卡。'],AMBER)
    s.panel('主路怎样结束',['可行驶段收在最近合法转向位置。','取送入口向完整街区内部安排。','景观区不留下暗示可驶入的长路。','不擅自扩蓝框，也不强画连接线。'],BLUE)
    s.panel('零散支段怎样处理',['可见几何相交不等于路网连通。','不连通/不能回返支段先排除取送。','如确需使用，再提出具体连接方案。','不能把它们悄悄当作已修复。'],'#9a655e')
    s.panel('经营点目录注意',['这里仅盘点原始地点参考目录。','运行时动态地址仍需按蓝框筛选，','并绑定可往返的合法入口节点。','14处不代表游戏地址数量上限。'],INK)
    s.finish('图例：绿灰路缘＝起点可往返路段；淡红路缘＝未纳入该分量；橙点＝主路边界交点组。')

    s=Sheet('03-first-sample','首块样板布局 · 榕树街食堂与晴川广场','原道路和入口位置固定；橙框精修、周边接续；镜头占位只用于安排画面。',G.CONTEXT);s.base()
    s.rect(G.SAMPLE,AMBER,9,fill=(236,188,91,30));s.rect(G.VIEW,'#536b7d',4,dash=True)
    route=R['outbound']['points'];s.line(route,'#fffdf7',20);s.line(route,'#d68b2c',10)
    a=G.POINTS['1623821046'];b=G.POINTS['9657208284'];s.point(a,'#d28327',16);s.point(b,'#4d6874',16)
    s.label(a,'P 榕树街食堂 / 原取餐入口','#a36520',(30,28),33);s.label(b,'D 晴川广场 / 原送达入口','#415b66',(35,-72),33)
    s.label((-1710,180),'A 精修边界',AMBER,(25,22),32);s.label((-1620,-200),'约180×220m镜头占位','#536b7d',(18,30),30)
    s.panel('首批精修范围',['380×440m，约0.167平方公里。','保留已有建筑占地与道路、水系。','上下文留白用于相邻街区接续，','不等于整幅图都在首批精修内。'],AMBER)
    s.panel('样板要解决的画面问题',['路面、人行道、店面、屋顶统一。','建筑立面与车辆使用同一视角。','一个完整镜头内道路与骑手清楚。','植被不挡路，不在屋顶补树。'],GREEN)
    s.panel('样板要覆盖的道路关系',[f'现有入口间原始道路参考约 {R["outbound"]["metres"]:.0f}m。','路线严格沿已有节点与道路。','两处入口都在精修范围内。','这是静态选址参考，不是新订单。'],BLUE)
    s.panel('首批素材：少量模块成套',['道路 / 人行道 / 路缘 / 河岸。','沿街店屋、转角商住、普通住宅。','树木、灌木、路灯等少量配景。','配套同视角车辆与明确地面锚点。'],INK)
    s.panel('现有素材先复用',['沥青、人行道、草地与水面已存。','屋顶材质与顶视树冠已有库存。','需对照新视角判断可用部位，','不能把顶视树冠直接当侧立面。'],MUTED)
    s.finish('图例：实线橙框＝精修样板；虚线＝初始镜头占位；橙线＝取送入口间原始路网参考。')
    (ROOT/'image-manifest.json').write_text(json.dumps({'date':'2026-11-02','kind':'new-data-derived-planning-diagrams','images':OUTPUT},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'path':i['path'],'size':[i['width'],i['height']]} for i in OUTPUT],ensure_ascii=False))

if __name__=='__main__':main()
