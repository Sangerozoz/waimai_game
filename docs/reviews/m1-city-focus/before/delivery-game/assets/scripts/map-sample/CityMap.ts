import { EventMouse, EventTouch, Graphics, Label, Mask, Node, UITransform, Vec3 } from 'cc';
import { CityData, MapRoute, Point, Preference } from './MapTypes';
import { box, C, col, item, label, tap } from './SampleUI';
import { clampCamera, compatibilityBounds, contains } from './CityExtent';
import { MapVehicle } from './MapVehicle';
export const ROUTE_COLORS:Record<Preference,string>={fast:'#BE7620',main:'#E88338',smooth:C.green};
const MAP_W=720,MAP_Y=83;
const TILE_SIZE=600;
const DEFAULT_SCALE=60/30,MIN_SCALE=60/100,MAX_SCALE=60/10;
interface DetailTile { buildings:Point[][]; roads:Array<{points:Point[];width:number}> }
export class CityMap {
 static fitViewportHeight(data:CityData,requestedHeight:number):number {
   const bounds=data.playBounds;
   return bounds?Math.min(requestedHeight,(bounds.maxY-bounds.minY)*MIN_SCALE):requestedHeight;
 }
 readonly viewport:Node;
 private readonly world:Node;
 private readonly routeInk:Graphics;
 private readonly overlay:Node;
 private readonly startPin:Node;
 private readonly endPin:Node;
 private readonly rider:Node;
 private readonly vehicle:MapVehicle;
 private readonly labels:Array<{n:Node,x:number,y:number,kind:string}>=[];
 private readonly poiDots:Array<{n:Node,x:number,y:number}>=[];
 private readonly nodePoints=new Map<string,Point>();
 private routes:MapRoute[]=[];
 private selected=0;
 private scale=DEFAULT_SCALE;
 private offset:Point=[0,0];
 private riderPoint:Point=[0,0];
 private riderAngle=0;
 private touchPoints=new Map<number,Point>();
 private pinchStart:{distance:number;midpoint:Point;scale:number;offset:Point}|null=null;
 private follow=false;
 private readonly detailData=new Map<string,DetailTile>();
 private readonly detailNodes=new Map<string,Node>();
 private majorInk!:Graphics;
 private majorScale=-1;
 private readonly scaleLabel:Label;
 constructor(parent:Node,private readonly data:CityData,private readonly mapHeight=748,onAttribution:()=>void=()=>{},mapY=MAP_Y,footerInset=0,safeSides:{left:number;right:number}={left:0,right:0}){
   const MAP_H=this.mapHeight;
   this.viewport=item(parent,'CityViewport',0,mapY,MAP_W,MAP_H);this.viewport.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
   box(this.viewport,'MapGround',0,0,MAP_W,MAP_H,'#EAF5DD',0);
   this.world=item(this.viewport,'RealRoadGeometry');
   for(const n of data.nodes)this.nodePoints.set(n.id,[n.x,n.y]);
   this.drawCity();this.routeInk=item(this.world,'Routes').addComponent(Graphics);
   this.overlay=item(this.viewport,'MapLabels');
   for(const l of data.labels){
     const text=label(this.overlay,l.text,l.x,l.y,l.kind==='district'?25:15,l.kind==='district'?'#697576':'#8C8B80',l.kind==='district'?180:110,l.kind==='district','center');
     if(l.kind==='street')text.node.angle=l.angle||0;
     this.labels.push({n:text.node,x:l.x,y:l.y,kind:l.kind});
   }
   for(const index of data.operatingPOIs||data.pois.map((_p,i)=>i)){const p=data.pois[index],xy=this.nodePoints.get(p.node)!;const pin=item(this.overlay,'Place-'+p.name);const g=pin.addComponent(Graphics);g.fillColor=col('#FFFFFF');g.circle(0,0,10);g.fill();g.strokeColor=col('#C1C7C7');g.lineWidth=1;g.circle(0,0,10);g.stroke();g.fillColor=col(p.kind==='restaurant'?'#D4A254':'#8398AA');g.circle(0,0,4);g.fill();this.poiDots.push({n:pin,x:xy[0],y:xy[1]});}
   this.startPin=this.pin('取','#D59831');this.endPin=this.pin('送','#F05B70');
   const shadow=item(this.overlay,'VehicleGroundShadow');const sg=shadow.addComponent(Graphics);for(let i=5;i>=1;i--){sg.fillColor=col('#30465A08');sg.ellipse(0,0,38+i*2,17+i*2);sg.fill();}
   this.rider=item(this.overlay,'DeliveryRider');this.vehicle=new MapVehicle(this.rider,this.drawRider());
   this.scaleLabel=label(this.viewport,'30 m',-279+safeSides.left,-MAP_H/2+footerInset+32,12,'#758080',110);
   const scaleLine=item(this.viewport,'MapScale',-297+safeSides.left,-MAP_H/2+footerInset+20).addComponent(Graphics);scaleLine.strokeColor=col('#758080');scaleLine.lineWidth=2;scaleLine.moveTo(-30,4);scaleLine.lineTo(-30,0);scaleLine.lineTo(30,0);scaleLine.lineTo(30,4);scaleLine.stroke();
   const attributionWidth=Math.max(1,410-safeSides.left-safeSides.right);
   const attribution=item(this.viewport,'MapAttribution',339-safeSides.right-attributionWidth/2,-MAP_H/2+footerInset+19,attributionWidth,26);
   label(attribution,'© OpenStreetMap contributors',0,0,16,'#596970',attributionWidth,false,'right');
   tap(attribution,onAttribution);
   this.viewport.on(Node.EventType.TOUCH_START,this.touchStart,this);
   this.viewport.on(Node.EventType.TOUCH_MOVE,this.touchMove,this);
   this.viewport.on(Node.EventType.TOUCH_END,this.touchEnd,this);
   this.viewport.on(Node.EventType.TOUCH_CANCEL,this.touchEnd,this);
   this.viewport.on(Node.EventType.MOUSE_WHEEL,(e:EventMouse)=>this.zoom(e.getScrollY()>0?1.15:1/1.15));
   this.sync();
 }
 private polygon(g:Graphics,ps:Point[],dx=0,dy=0):void{if(ps.length<3)return;g.moveTo(ps[0][0]+dx,ps[0][1]+dy);for(const p of ps.slice(1))g.lineTo(p[0]+dx,p[1]+dy);g.close();g.fill();}
 private line(g:Graphics,ps:Point[],width:number,color:string):void{if(ps.length<2)return;g.strokeColor=col(color);g.lineWidth=width;g.lineJoin=Graphics.LineJoin.ROUND;g.lineCap=Graphics.LineCap.ROUND;g.moveTo(ps[0][0],ps[0][1]);for(const p of ps.slice(1))g.lineTo(p[0],p[1]);g.stroke();}
 private drawCity():void{
   const g=item(this.world,'MapBase').addComponent(Graphics);
   const areaColor:Record<string,string>={water:'#85D8EF',green:'#BFE8B0',farmland:'#DBEAB5',residential:'#EAF5DD',commercial:'#FFECC1'};
   const areaOrder:Record<string,number>={residential:0,commercial:1,farmland:2,green:3,water:4};
   const areas=this.data.areas.slice().sort((a,b)=>(areaOrder[a.kind]||0)-(areaOrder[b.kind]||0));
   for(const a of areas){g.fillColor=col(areaColor[a.kind]||'#EAF5DD');this.polygon(g,a.points);}
   for(const water of this.data.waterways){this.line(g,water,23,'#C6F4F5');this.line(g,water,17,'#85D8EF');}
   const tile=(x:number,y:number):DetailTile=>{
     const key=`${Math.floor(x/TILE_SIZE)}/${Math.floor(y/TILE_SIZE)}`;
     if(!this.detailData.has(key))this.detailData.set(key,{buildings:[],roads:[]});return this.detailData.get(key)!;
   };
   for(const p of this.data.buildings){const x=p.reduce((sum,n)=>sum+n[0],0)/p.length,y=p.reduce((sum,n)=>sum+n[1],0)/p.length;tile(x,y).buildings.push(p);}
   for(const r of this.data.roads)for(let i=1;i<r.nodes.length;i++){
     const a=this.nodePoints.get(r.nodes[i-1])!,b=this.nodePoints.get(r.nodes[i])!;
     tile((a[0]+b[0])/2,(a[1]+b[1])/2).roads.push({points:[a,b],width:r.width});
   }
   this.majorInk=item(this.world,'MajorRoads').addComponent(Graphics);this.drawMajorRoads();
 }
 private drawMajorRoads():void{
   if(this.majorScale===this.scale)return;this.majorScale=this.scale;this.majorInk.clear();
   const boost=Math.max(1,.18/this.scale),roads=this.data.roads.filter(r=>r.width>=8).sort((a,b)=>a.width-b.width);
   for(const r of roads)this.line(this.majorInk,r.nodes.map(n=>this.nodePoints.get(n)!),(r.width+2.6)*boost,'#E7C67B');
   for(const r of roads)this.line(this.majorInk,r.nodes.map(n=>this.nodePoints.get(n)!),r.width*boost,'#FFF0BA');
 }
 private syncDetails():void{
   const visible=new Set<string>();
   if(this.scale>=.28){
     const left=(-MAP_W/2-this.offset[0])/this.scale-200,right=(MAP_W/2-this.offset[0])/this.scale+200;
     const bottom=(-this.mapHeight/2-this.offset[1])/this.scale-200,top=(this.mapHeight/2-this.offset[1])/this.scale+200;
     for(let x=Math.floor(left/TILE_SIZE);x<=Math.floor(right/TILE_SIZE);x++)for(let y=Math.floor(bottom/TILE_SIZE);y<=Math.floor(top/TILE_SIZE);y++){
       const key=`${x}/${y}`,data=this.detailData.get(key);if(!data)continue;visible.add(key);
       let node=this.detailNodes.get(key);
       if(!node){
         node=item(this.world,'Detail-'+key);const g=node.addComponent(Graphics);
         for(let i=0;i<data.buildings.length;i++){const p=data.buildings[i];g.fillColor=col('#B7C9A7');this.polygon(g,p,1.2,-1.5);g.fillColor=col(['#FFCFA9','#B8DFF1','#FFE6AA','#D6D0F4'][i%4]);this.polygon(g,p);}
         const roads=data.roads.slice().sort((a,b)=>a.width-b.width);
         for(const r of roads)this.line(g,r.points,r.width+2.6,r.width>=8?'#E7C67B':'#D7CBA8');
         for(const r of roads)this.line(g,r.points,r.width,r.width>=8?'#FFF0BA':'#FFF9DC');
         node.setSiblingIndex(this.routeInk.node.getSiblingIndex());this.detailNodes.set(key,node);
       }
       node.active=true;
     }
   }
   for(const [key,node] of Array.from(this.detailNodes.entries())){
     if(visible.has(key))continue;node.active=false;
     if(this.detailNodes.size>80){node.destroy();this.detailNodes.delete(key);}
   }
 }
 private pin(text:string,color:string):Node{
   const n=item(this.overlay,'Pin-'+text),g=n.addComponent(Graphics);g.fillColor=col('#FFFFFF');g.circle(0,21,23);g.fill();g.fillColor=col(color);g.circle(0,21,19);g.fill();g.moveTo(-10,9);g.lineTo(0,-4);g.lineTo(10,9);g.close();g.fill();label(n,text,0,22,21,'#FFFFFF',38,true,'center');return n;
 }
 private drawRider():Graphics{
   const g=this.rider.addComponent(Graphics);g.fillColor=col('#FFFFFF');g.circle(0,0,24);g.fill();g.fillColor=col('#FFF1BC');g.circle(0,0,20);g.fill();
   g.fillColor=col('#463E2D');g.roundRect(-14,-14,25,6,3);g.fill();g.roundRect(-14,8,25,6,3);g.fill();
   g.fillColor=col('#E6AB14');g.roundRect(-13,-10,28,20,6);g.fill();g.fillColor=col('#4A4232');g.roundRect(-17,-9,16,18,3);g.fill();g.fillColor=col('#FFFFFF');g.circle(9,0,7);g.fill();g.fillColor=col('#65552D');g.circle(12,0,4);g.fill();
   return g;
 }
 setVehicle(tier:number):void{this.vehicle.setTier(tier);}
 get isFollowing():boolean{return this.follow;}
 setRoutes(routes:MapRoute[],selected:number,fit=false):void{this.routes=routes;this.selected=selected;if(routes.length)this.riderPoint=routes[selected].points[0];this.riderAngle=0;this.follow=false;if(fit&&routes.length)this.focusRoute();else this.sync();}
 setRider(point:Point,angle:number):void{this.riderPoint=point;this.riderAngle=angle;if(this.follow)this.offset=[-point[0]*this.scale,-point[1]*this.scale];this.clampOffset();this.syncOverlay();this.world.setPosition(this.offset[0],this.offset[1]);this.syncDetails();}
 locate(resetZoom=false):void{this.follow=true;this.scale=resetZoom?DEFAULT_SCALE:Math.max(MIN_SCALE,Math.min(MAX_SCALE,this.scale));this.offset=[-this.riderPoint[0]*this.scale,-this.riderPoint[1]*this.scale];this.sync();}
 overview():void{this.follow=false;this.scale=MIN_SCALE;this.offset=[-this.riderPoint[0]*this.scale,-this.riderPoint[1]*this.scale];this.sync();}
 focusRoute():void{
   if(!this.routes.length)return;this.follow=false;const points:Point[]=[];for(const r of this.routes)points.push(...r.points);const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
   const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
   this.scale=Math.max(MIN_SCALE,Math.min(MAX_SCALE,(MAP_W-165)/(maxX-minX+90),(this.mapHeight-180)/(maxY-minY+90)));this.offset=[-this.riderPoint[0]*this.scale,-this.riderPoint[1]*this.scale];this.sync();
 }
 zoom(factor:number,anchor:Point=[0,0],previousAnchor:Point=anchor):void{
   this.follow=false;const before=this.scale;this.scale=Math.max(MIN_SCALE,Math.min(MAX_SCALE,this.scale*factor));
   this.offset=[anchor[0]-(previousAnchor[0]-this.offset[0])*this.scale/before,anchor[1]-(previousAnchor[1]-this.offset[1])*this.scale/before];this.sync();
 }
 private sync():void{
   this.clampOffset();
   this.world.setScale(this.scale,this.scale,1);this.world.setPosition(this.offset[0],this.offset[1]);this.drawMajorRoads();this.drawRoutes();this.syncOverlay();this.syncDetails();
   this.scaleLabel.string=`${Math.round(60/this.scale)} m`;
 }
 private clampOffset():void{
   const base=this.data.playBounds||{minX:-this.data.width/2,maxX:this.data.width/2,minY:-this.data.height/2,maxY:this.data.height/2};
   const points=[this.riderPoint,...this.routes.reduce((all,r)=>all.concat(r.points),[] as Point[])];
   const bounds=compatibilityBounds(base,points,MAP_W/2/MIN_SCALE,this.mapHeight/2/MIN_SCALE);
   this.offset=clampCamera(bounds,this.offset,this.scale,MAP_W,this.mapHeight);
 }
 private drawRoutes():void{
   this.routeInk.clear();const order=this.routes.map((r,i)=>({r,i})).sort((a,b)=>Number(a.i===this.selected)-Number(b.i===this.selected));
   for(const {r,i} of order){this.line(this.routeInk,r.points,(i===this.selected?13:7)/this.scale,'#FFFFFF');this.line(this.routeInk,r.points,(i===this.selected?8:4)/this.scale,i===this.selected?ROUTE_COLORS[r.preference]:'#ACB4C6');}
 }
 private project(p:Point):Point{return[p[0]*this.scale+this.offset[0],p[1]*this.scale+this.offset[1]];}
 private syncOverlay():void{
   for(const l of this.labels){const p=this.project([l.x,l.y]);l.n.setPosition(p[0],p[1]);l.n.active=(l.kind==='district'?this.scale<.28:this.scale>=.28)&&Math.abs(p[0])<MAP_W/2+80&&Math.abs(p[1])<this.mapHeight/2+40;}
   for(const d of this.poiDots){const p=this.project([d.x,d.y]);d.n.setPosition(p[0],p[1]);d.n.active=(!this.data.dispatchBounds||contains(this.data.dispatchBounds,[d.x,d.y]))&&this.scale>=.2&&Math.abs(p[0])<MAP_W/2+20&&Math.abs(p[1])<this.mapHeight/2+20;}
   this.startPin.active=this.endPin.active=this.routes.length>0;
   if(this.routes.length){const r=this.routes[this.selected];const a=this.project(r.points[r.pickupIndex||0]),b=this.project(r.points[r.points.length-1]);this.startPin.setPosition(a[0],a[1]);this.endPin.setPosition(b[0],b[1]);}
   const p=this.project(this.riderPoint);this.overlay?.getChildByName('VehicleGroundShadow')?.setPosition(p[0]+3,p[1]-8);this.rider.setPosition(p[0],p[1]);this.rider.angle=this.riderAngle;
 }
 private local(event:EventTouch):Point{const p=event.getUILocation();const v=this.viewport.getComponent(UITransform)!.convertToNodeSpaceAR(new Vec3(p.x,p.y));return[v.x,v.y];}
 private touchStart(e:EventTouch):void{
   const id=e.getID();if(id===null)return;this.follow=false;this.touchPoints.set(id,this.local(e));
   if(this.touchPoints.size===2){const [a,b]=Array.from(this.touchPoints.values());this.pinchStart={distance:Math.hypot(a[0]-b[0],a[1]-b[1]),midpoint:[(a[0]+b[0])/2,(a[1]+b[1])/2],scale:this.scale,offset:[...this.offset]};}
 }
 private touchMove(e:EventTouch):void{
   const id=e.getID();if(id===null)return;const old=this.touchPoints.get(id);if(!old)return;const now=this.local(e);
   // Creator's loose spread transform assumes arrays; Map iterators need Array.from.
   const other=Array.from(this.touchPoints.entries()).find(([otherId])=>otherId!==id);
   if(other&&this.pinchStart){const p=other[1],start=this.pinchStart,after=Math.hypot(now[0]-p[0],now[1]-p[1]);
     if(start.distance>8){this.scale=start.scale;this.offset=[...start.offset];this.zoom(after/start.distance,[(now[0]+p[0])/2,(now[1]+p[1])/2],start.midpoint);}}
   else{this.offset[0]+=now[0]-old[0];this.offset[1]+=now[1]-old[1];this.sync();}this.touchPoints.set(id,now);
 }
 private touchEnd(e:EventTouch):void{const id=e.getID();if(id!==null)this.touchPoints.delete(id);this.pinchStart=null;}
}
