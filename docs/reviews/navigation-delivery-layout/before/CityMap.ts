import { EventMouse, EventTouch, Graphics, Label, Mask, Node, UIOpacity, UITransform, Vec3 } from 'cc';
import { routePoints, CityData, MapRoute, Point, Preference } from './MapTypes';
import { box, C, col, item, label, tap } from './SampleUI';
import { clampCamera, compatibilityBounds, contains } from './CityExtent';
import { cssUnits, pageMargin, readable } from './PresentationLayout';
import { foodImage } from './FoodImages';
import { MapVehicle } from './MapVehicle';
export const ROUTE_COLORS:Record<Preference,string>={fast:'#C36A31',main:'#6C8982',smooth:C.green};
const MAP_W=720,MAP_Y=83;
const TILE_SIZE=600;
const DEFAULT_METRES=15,DEFAULT_SCALE=60/DEFAULT_METRES,MIN_SCALE=60/100,MAX_SCALE=60/10;
const NAVIGATION_STYLE={selected:'#168BFF',outline:'#F6FBFF',alternative:'#9EAFBD',selectedCss:7.5,outlineCss:10,alternativeCss:4,cardWidthCss:146,cardHeightCss:52,fontCss:13,gapCss:8};
export interface NavigationStops {pickupName:string;deliveryName:string;food:string;pickup:Point;delivery:Point}
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
 private readonly nodePoints=new Map<string,Point>();
 private stopData:NavigationStops|null=null;
 private stopCards:Node[]=[];
 private stopLines:Graphics|null=null;
 private get cardWidth():number{return cssUnits(NAVIGATION_STYLE.cardWidthCss,this.screenHeight);}
 private get cardHeight():number{return cssUnits(NAVIGATION_STYLE.cardHeightCss,this.screenHeight);}
 setNavigationStops(stops:NavigationStops|null):void{
   for(const card of this.stopCards){card.active=false;card.destroy();}this.stopCards=[];
   if(this.stopLines){this.stopLines.node.destroy();this.stopLines=null;}
   this.stopData=stops;if(!stops)return;
   this.stopLines=item(this.overlay,'StopConnectors').addComponent(Graphics);
   for(const [index,name] of [stops.pickupName,stops.deliveryName].entries()){
     const w=this.cardWidth,h=this.cardHeight,pad=cssUnits(8,this.screenHeight);
     const card=item(this.overlay,index===0?'PickupInfoCard':'DeliveryInfoCard',0,0,w,h);
     box(card,'Shadow',cssUnits(1,this.screenHeight),-cssUnits(2,this.screenHeight),w,h,'#39372F20',pad);
     box(card,'Surface',0,0,w,h,'#FFFCF5',pad,'#D8C8A9');
     card.addComponent(UIOpacity);
     const imageSize=h-2*pad;
     if(index===1){const image=foodImage(card,stops.food,-w/2+pad+imageSize/2,0,imageSize),fallback=image.getComponentInChildren(Label);if(fallback){fallback.fontSize=cssUnits(10,this.screenHeight);fallback.lineHeight=cssUnits(12,this.screenHeight);fallback.enableWrapText=true;fallback.overflow=Label.Overflow.CLAMP;fallback.node.getComponent(UITransform)!.setContentSize(imageSize-8,imageSize-8);}}
     const textWidth=w-2*pad-(index===1?imageSize+pad:0);
     const title=readable(card,name,index===1?(imageSize+pad)/2:0,0,cssUnits(NAVIGATION_STYLE.fontCss,this.screenHeight),C.ink,textWidth,true,'left',h-2*pad);
     title.lineHeight=cssUnits(17,this.screenHeight);
     this.stopCards.push(card);
   }
   this.syncOverlay();
 }
 setLowerClearance(bottom:number):void{this.routeInsets.bottom=Math.max(pageMargin(this.screenHeight),bottom);}
 private cardBounds(){const m=pageMargin(this.screenHeight);return {left:-MAP_W/2+this.safeSides.left+m,right:MAP_W/2-this.safeSides.right-m,top:this.mapHeight/2-this.routeInsets.top,bottom:-this.mapHeight/2+this.routeInsets.bottom};}
 private syncStopCards():void{
   const g=this.stopLines;if(!g)return;g.clear();if(!this.stopData||!this.routes.length){for(const c of this.stopCards)c.getComponent(UIOpacity)!.opacity=0;return;}
   const bounds=this.cardBounds(),w=this.cardWidth,h=this.cardHeight,gap=cssUnits(NAVIGATION_STYLE.gapCss,this.screenHeight),pinTop=44;
   const occupied:Array<{x:number;y:number}>=[];
   for(const [i,point] of [this.stopData.pickup,this.stopData.delivery].entries()){
     const card=this.stopCards[i],p=this.project(point);card.getComponent(UIOpacity)!.opacity=0;
     // Offscreen anchors never acquire a clamped, misleading onscreen card.
     if(p[0]<-MAP_W/2||p[0]>MAP_W/2||p[1]<-this.mapHeight/2||p[1]>this.mapHeight/2||bounds.right-bounds.left<w||bounds.top-bounds.bottom<h)continue;
     const clampX=(x:number)=>Math.max(bounds.left+w/2,Math.min(bounds.right-w/2,x));
     const candidates=[{x:clampX(p[0]),y:p[1]+pinTop+gap+h/2},{x:clampX(p[0]),y:p[1]-gap-h/2},
       {x:clampX(p[0]+w/2+gap+24),y:p[1]+h/2},{x:clampX(p[0]-w/2-gap-24),y:p[1]+h/2}];
     const other=this.project(i===0?this.stopData.delivery:this.stopData.pickup);
     if(Math.abs(other[0]-p[0])<w+gap&&Math.abs(other[1]-p[1])<h+pinTop+gap)
       candidates.unshift({x:clampX((p[0]+other[0])/2+(i===0?-1:1)*(w+gap)/2),y:Math.max(p[1],other[1])+pinTop+gap+h/2});
     // Edge candidates keep the pin separate and retain a short explicit connector.
     candidates.push({x:clampX(p[0]),y:bounds.top-h/2},{x:clampX(p[0]),y:bounds.bottom+h/2});
     const position=candidates.find(c=>c.y-h/2>=bounds.bottom&&c.y+h/2<=bounds.top&&
       occupied.every(o=>Math.abs(c.x-o.x)>=w+gap||Math.abs(c.y-o.y)>=h+gap)&&
       [this.stopData!.pickup,this.stopData!.delivery].every(q=>{const a=this.project(q);return Math.abs(c.x-a[0])>=w/2+24||c.y-h/2>a[1]+pinTop||c.y+h/2<a[1]-8;}));
     if(!position)continue;card.getComponent(UIOpacity)!.opacity=255;card.setPosition(position.x,position.y);occupied.push(position);
     const end:Point=[Math.max(position.x-w/2,Math.min(position.x+w/2,p[0])),Math.max(position.y-h/2,Math.min(position.y+h/2,p[1]+22))];
     this.line(g,[[p[0],p[1]+22],end],cssUnits(1.5,this.screenHeight),'#ACB6BB');
   }
 }
 private routes:MapRoute[]=[];
 private selected=0;
 private routeOverview=false;
 private autoFit=false;
 private planningControlsHidden=false;
 setHeaderClearance(top:number):void{this.routeInsets.top=Math.max(0,top);}
 private routeInsets={top:232,bottom:252,left:90,right:90};
 private scale=DEFAULT_SCALE;
 private offset:Point=[0,0];
 private riderPoint:Point=[0,0];
 private riderAngle=0;
 private touchPoints=new Map<number,Point>();
 private pinchStart:{distance:number;midpoint:Point;scale:number;offset:Point}|null=null;
 private follow=false;
 private locating:{elapsed:number;scale:number;offset:Point}|null=null;
 private detailElapsed=0;
 private readonly detailData=new Map<string,DetailTile>();
 private readonly detailNodes=new Map<string,Node>();
 private majorInk!:Graphics;
 private majorScale=-1;
 private readonly scaleLabel:Label;
 constructor(parent:Node,private readonly data:CityData,private readonly mapHeight=748,onAttribution:()=>void=()=>{},mapY=MAP_Y,footerInset=0,private readonly safeSides:{left:number;right:number;top?:number}={left:0,right:0},private readonly screenHeight=1280){
   const MAP_H=this.mapHeight;this.routeInsets={top:232+(safeSides.top||0),bottom:252,left:90+safeSides.left,right:90+safeSides.right};
   this.viewport=item(parent,'CityViewport',0,mapY,MAP_W,MAP_H);this.viewport.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
   box(this.viewport,'MapGround',0,0,MAP_W,MAP_H,'#E9E5D7',0);
   this.world=item(this.viewport,'RealRoadGeometry');
   for(const n of data.nodes)this.nodePoints.set(n.id,[n.x,n.y]);
   this.drawCity();this.routeInk=item(this.world,'Routes').addComponent(Graphics);
   this.overlay=item(this.viewport,'MapLabels');
   for(const l of data.labels){
     const text=label(this.overlay,l.text,l.x,l.y,l.kind==='district'?25:15,l.kind==='district'?'#697576':'#8C8B80',l.kind==='district'?180:110,l.kind==='district','center');
     if(l.kind==='street')text.node.angle=l.angle||0;
     this.labels.push({n:text.node,x:l.x,y:l.y,kind:l.kind});
   }
   this.startPin=this.pin('取','#D59831');this.endPin=this.pin('送','#F05B70');
   const shadow=item(this.overlay,'VehicleGroundShadow');const sg=shadow.addComponent(Graphics);for(let i=5;i>=1;i--){sg.fillColor=col('#49443508');sg.ellipse(0,0,38+i*2,17+i*2);sg.fill();}
   this.rider=item(this.overlay,'DeliveryRider');this.vehicle=new MapVehicle(this.rider,this.drawRider());
   this.startPin.setSiblingIndex(this.overlay.children.length-1);this.endPin.setSiblingIndex(this.overlay.children.length-1);
   this.scaleLabel=label(this.viewport,`${DEFAULT_METRES} m`,-279+safeSides.left,-MAP_H/2+footerInset+32,12,'#758080',110);
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
   const areaColor:Record<string,string>={water:'#96BDB8',green:'#BAC8A1',farmland:'#D4D2AC',residential:'#E9E5D7',commercial:'#E6D8C1'};
   const areaOrder:Record<string,number>={residential:0,commercial:1,farmland:2,green:3,water:4};
   const areas=this.data.areas.slice().sort((a,b)=>(areaOrder[a.kind]||0)-(areaOrder[b.kind]||0));
   for(const a of areas){g.fillColor=col(areaColor[a.kind]||'#E9E5D7');this.polygon(g,a.points);}
   for(const water of this.data.waterways){this.line(g,water,23,'#D8E4DA');this.line(g,water,17,'#96BDB8');}
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
   const boost=Math.max(1,.18/this.scale);if(this.majorScale===boost)return;this.majorScale=boost;this.majorInk.clear();
   const roads=this.data.roads.filter(r=>r.width>=8).sort((a,b)=>a.width-b.width);
   for(const r of roads)this.line(this.majorInk,r.nodes.map(n=>this.nodePoints.get(n)!),(r.width+2.6)*boost,'#BEB9AD');
   for(const r of roads)this.line(this.majorInk,r.nodes.map(n=>this.nodePoints.get(n)!),r.width*boost,'#E8E4D9');
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
         for(let i=0;i<data.buildings.length;i++){
           const p=data.buildings[i];
           // Warm roof planes, fine ink edges and one consistent afternoon shadow.
           g.fillColor=col('#6C695331');this.polygon(g,p,3,-4);
           g.fillColor=col('#BCB5A1');this.polygon(g,p,1,-1.5);
           g.fillColor=col(['#F4EFDF','#E9DECB','#E5E5D9','#DDCBB8'][i%4]);this.polygon(g,p);
           g.strokeColor=col('#A49D893F');g.lineWidth=.65;g.stroke();
           if(i%3===0){
             const cx=p.reduce((v,a)=>v+a[0],0)/p.length,cy=p.reduce((v,a)=>v+a[1],0)/p.length;
             const roof=p.map(a=>[cx+(a[0]-cx)*.64,cy+(a[1]-cy)*.64] as Point);
             g.fillColor=col('#FFFCF349');this.polygon(g,roof);g.strokeColor=col('#B3AB9340');g.lineWidth=.5;g.stroke();
           }
         }
         const roads=data.roads.slice().sort((a,b)=>a.width-b.width);
         for(const r of roads)this.line(g,r.points,r.width+2.6,r.width>=8?'#BEB9AD':'#CBC5B8');
         for(const r of roads)this.line(g,r.points,r.width,r.width>=8?'#E8E4D9':'#F2EDE1');
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
 setPlanningControlsHidden(hidden:boolean):void{this.planningControlsHidden=hidden;}
 captureView():{scale:number;offset:Point;follow:boolean;overview:boolean;autoFit:boolean}{return {scale:this.scale,offset:[this.offset[0],this.offset[1]],follow:this.follow,overview:this.routeOverview,autoFit:this.autoFit};}
 restoreView(state:{scale:number;offset:Point;follow:boolean;overview:boolean;autoFit:boolean}):void{this.scale=state.scale;this.offset=[state.offset[0],state.offset[1]];this.follow=state.follow;this.routeOverview=state.overview;this.autoFit=state.autoFit;if(state.autoFit)this.focusRoute();else this.sync();}
 get isFollowing():boolean{return this.follow;}
 setRoutes(routes:MapRoute[],selected:number,fit=false):void{this.routes=routes;this.selected=selected;this.follow=false;if(fit&&routes.length)this.focusRoute();else this.sync();}
 setRider(point:Point,angle:number):void{this.riderPoint=point;this.riderAngle=angle;if(this.follow)this.offset=[-point[0]*this.scale,-point[1]*this.scale];this.clampOffset();this.syncOverlay();this.world.setPosition(this.offset[0],this.offset[1]);this.syncDetails();}
 cancelLocate():void{this.locating=null;}
 locateAnimated():void{this.routeOverview=this.scale<MIN_SCALE;this.autoFit=false;this.follow=false;this.locating={elapsed:0,scale:this.scale,offset:[this.offset[0],this.offset[1]]};this.detailElapsed=0;}
 advanceLocate(dt:number):void {
   const a=this.locating;if(!a)return;
   a.elapsed=Math.min(.6,a.elapsed+Math.max(0,dt));const t=a.elapsed/.6,e=t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
   this.scale=a.scale+(DEFAULT_SCALE-a.scale)*e;
   this.offset=[a.offset[0]+(-this.riderPoint[0]*DEFAULT_SCALE-a.offset[0])*e,a.offset[1]+(-this.riderPoint[1]*DEFAULT_SCALE-a.offset[1])*e];
   this.clampOffset();this.world.setScale(this.scale,this.scale,1);this.world.setPosition(this.offset[0],this.offset[1]);this.drawRoutes();this.syncOverlay();this.scaleLabel.string=`${Math.round(60/this.scale)} m`;
   this.detailElapsed+=dt;if(this.detailElapsed>=.1){this.syncDetails();this.detailElapsed=0;}
   if(t===1){this.locating=null;this.follow=true;this.locate(true);}
 }
 locate(resetZoom=false):void{this.routeOverview=false;this.autoFit=false;this.cancelLocate();this.follow=true;this.scale=resetZoom?DEFAULT_SCALE:Math.max(MIN_SCALE,Math.min(MAX_SCALE,this.scale));this.offset=[-this.riderPoint[0]*this.scale,-this.riderPoint[1]*this.scale];this.sync();}
 overview():void{this.routeOverview=false;this.autoFit=false;this.cancelLocate();this.follow=false;this.scale=MIN_SCALE;this.offset=[-this.riderPoint[0]*this.scale,-this.riderPoint[1]*this.scale];this.sync();}
 focusRoute():void{this.cancelLocate();
   if(!this.routes.length)return;this.follow=false;const points:Point[]=[];for(const r of this.routes)points.push(...routePoints(r));if(this.stopData)points.push(this.stopData.pickup,this.stopData.delivery);const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
   const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
   // Automatic planning view may zoom beyond manual 100m. Reserve HUD and lower map controls.
   const bounds=this.cardBounds(),hasCards=!!this.stopData;
   const half=hasCards?this.cardWidth/2:24,above=hasCards?this.cardHeight+44+cssUnits(NAVIGATION_STYLE.gapCss,this.screenHeight):44;
   const left=bounds.left+half,right=Math.max(left+1,bounds.right-half),bottom=bounds.bottom+8,top=Math.max(bottom+1,bounds.top-above);
   this.routeOverview=true;this.autoFit=true;this.scale=Math.min(MAX_SCALE,(right-left)/Math.max(1,maxX-minX),(top-bottom)/Math.max(1,maxY-minY));
   this.offset=[(left+right)/2-(minX+maxX)/2*this.scale,(bottom+top)/2-(minY+maxY)/2*this.scale];this.sync();
 }
 zoom(factor:number,anchor:Point=[0,0],previousAnchor:Point=anchor):void{
   this.routeOverview=false;this.autoFit=false;this.cancelLocate();this.follow=false;const before=this.scale;this.scale=Math.max(MIN_SCALE,Math.min(MAX_SCALE,this.scale*factor));
   this.offset=[anchor[0]-(previousAnchor[0]-this.offset[0])*this.scale/before,anchor[1]-(previousAnchor[1]-this.offset[1])*this.scale/before];this.sync();
 }
 private sync():void{
   this.clampOffset();
   this.world.setScale(this.scale,this.scale,1);this.world.setPosition(this.offset[0],this.offset[1]);this.drawMajorRoads();this.drawRoutes();this.syncOverlay();this.syncDetails();
   this.scaleLabel.string=`${Math.round(60/this.scale)} m`;
 }
 private clampOffset():void{
   if(this.routeOverview)return;
   const base=this.data.playBounds||{minX:-this.data.width/2,maxX:this.data.width/2,minY:-this.data.height/2,maxY:this.data.height/2};
   const points=[this.riderPoint,...this.routes.reduce((all,r)=>all.concat(routePoints(r)),[] as Point[])];
   const bounds=compatibilityBounds(base,points,MAP_W/2/MIN_SCALE,this.mapHeight/2/MIN_SCALE);
   this.offset=clampCamera(bounds,this.offset,this.scale,MAP_W,this.mapHeight);
 }
 private drawRoutes():void{
   this.routeInk.clear();const order=this.routes.map((r,i)=>({r,i})).sort((a,b)=>Number(a.i===this.selected)-Number(b.i===this.selected));
   for(const {r,i} of order){const selected=i===this.selected;if(selected)this.line(this.routeInk,routePoints(r),cssUnits(NAVIGATION_STYLE.outlineCss,this.screenHeight)/this.scale,NAVIGATION_STYLE.outline);this.line(this.routeInk,routePoints(r),cssUnits(selected?NAVIGATION_STYLE.selectedCss:NAVIGATION_STYLE.alternativeCss,this.screenHeight)/this.scale,selected?NAVIGATION_STYLE.selected:NAVIGATION_STYLE.alternative);}
 }
 private project(p:Point):Point{return[p[0]*this.scale+this.offset[0],p[1]*this.scale+this.offset[1]];}
 private syncOverlay():void{
   for(const l of this.labels){const p=this.project([l.x,l.y]);l.n.setPosition(p[0],p[1]);l.n.active=(l.kind==='district'?this.scale<.28:this.scale>=.28)&&Math.abs(p[0])<MAP_W/2+80&&Math.abs(p[1])<this.mapHeight/2+40;}
   this.startPin.active=this.endPin.active=this.routes.length>0;
   if(this.routes.length){const r=this.routes[this.selected];const a=this.project(this.stopData?.pickup||r.points[r.pickupIndex||0]),b=this.project(this.stopData?.delivery||r.points[r.points.length-1]);this.startPin.setPosition(a[0],a[1]);this.endPin.setPosition(b[0],b[1]);}
   this.syncStopCards();
   const p=this.project(this.riderPoint);this.overlay?.getChildByName('VehicleGroundShadow')?.setPosition(p[0]+3,p[1]-8);this.rider.setPosition(p[0],p[1]);this.rider.angle=this.riderAngle;
 }
 private local(event:EventTouch):Point{const p=event.getUILocation();const v=this.viewport.getComponent(UITransform)!.convertToNodeSpaceAR(new Vec3(p.x,p.y));return[v.x,v.y];}
 private touchStart(e:EventTouch):void{
   const id=e.getID();if(id===null)return;this.autoFit=false;this.cancelLocate();this.follow=false;this.touchPoints.set(id,this.local(e));
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
