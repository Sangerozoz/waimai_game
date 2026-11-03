import { Graphics } from 'cc';
import { CityData, Point } from './MapTypes';
import { col } from './SampleUI';

export interface HousePlacement {id:string;point:Point;variant:number}
export interface NeighborhoodPlacement {trees:TreePlacement[];houses:HousePlacement[]}
export interface TreePlacement {id:string;point:Point;warm:boolean;diameter:number}
export interface Segment {a:Point;b:Point;width:number;key:string;bridge?:boolean}
export interface Polygon {p:Point[];minX:number;minX2:number;minY:number;minY2:number}
/** Spatial index of immutable source geometry. Decorations are visual only. */
export class HomeMapArt {
 private readonly cell=200;
 private readonly roads=new Map<string,Segment[]>();
 private readonly buildings=new Map<string,Polygon[]>();
 private readonly water=new Map<string,Polygon[]>();
 private readonly grass=new Map<string,Polygon[]>();
 private readonly streams=new Map<string,Segment[]>();
 private readonly pois=new Map<string,Point[]>();
 constructor(data:CityData){
  const nodes=new Map(data.nodes.map(n=>[n.id,[n.x,n.y] as Point]));
  const addSegment=(map:Map<string,Segment[]>,a:Point,b:Point,width:number,key:string,bridge=false)=>{
   const segment={a,b,width,key,bridge};this.index(map,Math.min(a[0],b[0])-40,Math.min(a[1],b[1])-40,Math.max(a[0],b[0])+40,Math.max(a[1],b[1])+40,segment);
  };
  for(const road of data.roads)for(let i=1;i<road.nodes.length;i++){
   const a=nodes.get(road.nodes[i-1]),b=nodes.get(road.nodes[i]);if(a&&b)addSegment(this.roads,a,b,road.width,road.id+'/'+i,road.bridge);
  }
  const addPolygon=(map:Map<string,Polygon[]>,p:Point[])=>{
   if(p.length<3)return;const xs=p.map(q=>q[0]),ys=p.map(q=>q[1]);
   const poly={p,minX:Math.min(...xs),minX2:Math.max(...xs),minY:Math.min(...ys),minY2:Math.max(...ys)};
   this.index(map,poly.minX-25,poly.minY-25,poly.minX2+25,poly.minY2+25,poly);
  };
  for(const p of data.buildings)addPolygon(this.buildings,p);
  for(const a of data.areas){if(a.kind==='water')addPolygon(this.water,a.points);else if(a.kind==='green'||a.kind==='farmland')addPolygon(this.grass,a.points);}
  data.waterways.forEach((p,j)=>{for(let i=1;i<p.length;i++)addSegment(this.streams,p[i-1],p[i],18,'water/'+j+'/'+i);});
  for(const poi of data.pois){const p=nodes.get(poi.node);if(p)this.index(this.pois,p[0]-40,p[1]-40,p[0]+40,p[1]+40,p);}
 }
 private index<T>(map:Map<string,T[]>,l:number,b:number,r:number,t:number,value:T):void{
  for(let x=Math.floor(l/this.cell);x<=Math.floor(r/this.cell);x++)for(let y=Math.floor(b/this.cell);y<=Math.floor(t/this.cell);y++){
   const key=x+'/'+y,items=map.get(key);if(items)items.push(value);else map.set(key,[value]);
  }
 }
 private near<T>(map:Map<string,T[]>,p:Point):T[]{return map.get(Math.floor(p[0]/this.cell)+'/'+Math.floor(p[1]/this.cell))||[];}
 private distance(p:Point,a:Point,b:Point):number{
  const dx=b[0]-a[0],dy=b[1]-a[1],len=dx*dx+dy*dy,t=len?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/len)):0;
  return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy);
 }
 private polygonNear(p:Point,poly:Polygon,buffer:number):boolean{
  if(p[0]<poly.minX-buffer||p[0]>poly.minX2+buffer||p[1]<poly.minY-buffer||p[1]>poly.minY2+buffer)return false;
  let inside=false;const pts=poly.p;
  for(let i=0,j=pts.length-1;i<pts.length;j=i++){
   const a=pts[i],b=pts[j];if(this.distance(p,a,b)<buffer)return true;
   if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;
  }return inside;
 }
 private safe(p:Point,r:number):boolean{
  return !this.near(this.roads,p).some(s=>this.distance(p,s.a,s.b)<s.width/2+r+4)
   &&!this.near(this.buildings,p).some(b=>this.polygonNear(p,b,r+3))
   &&!this.near(this.water,p).some(b=>this.polygonNear(p,b,r+4))
   &&!this.near(this.streams,p).some(s=>this.distance(p,s.a,s.b)<s.width/2+r+4)
   &&!this.near(this.pois,p).some(q=>Math.hypot(p[0]-q[0],p[1]-q[1])<r+18);
 }
 private hash(text:string):number{let h=2166136261;for(let i=0;i<text.length;i++)h=Math.imul(h^text.charCodeAt(i),16777619);return h>>>0;}
 /** Return immutable segments intersecting a world rectangle, de-duplicated by source id. */
 roadSegments(l:number,b:number,r:number,t:number):Segment[]{
  const found=new Map<string,Segment>();
  for(let x=Math.floor(l/this.cell);x<=Math.floor(r/this.cell);x++)for(let y=Math.floor(b/this.cell);y<=Math.floor(t/this.cell);y++)
   for(const s of this.roads.get(x+'/'+y)||[])found.set(s.key,s);
  return Array.from(found.values());
 }
 areaGeometry(l:number,b:number,r:number,t:number):{grass:Polygon[];water:Polygon[];buildings:Polygon[];streams:Segment[]}{
  const gather=<T>(map:Map<string,T[]>):T[]=>{
   const found=new Set<T>();for(let x=Math.floor(l/this.cell);x<=Math.floor(r/this.cell);x++)for(let y=Math.floor(b/this.cell);y<=Math.floor(t/this.cell);y++)for(const v of map.get(x+'/'+y)||[])found.add(v);
   return Array.from(found);
  };
  return {grass:gather(this.grass),water:gather(this.water),buildings:gather(this.buildings),streams:gather(this.streams)};
 }
 detailSafe(p:Point,r:number):boolean {
  return !this.near(this.water,p).some(v=>this.polygonNear(p,v,r))&&!this.near(this.streams,p).some(v=>this.distance(p,v.a,v.b)<v.width/2+r)&&!this.near(this.pois,p).some(q=>Math.hypot(p[0]-q[0],p[1]-q[1])<r+16);
 }
 insideRoof(p:Point,poly:Polygon,margin:number):boolean {
  if(!this.polygonNear(p,poly,0))return false;
  for(let i=0;i<poly.p.length;i++)if(this.distance(p,poly.p[i],poly.p[(i+1)%poly.p.length])<margin)return false;
  return true;
 }
 /** Distribute fixed candidates by 100m cells, independent of input road order. */
 drawTile(g:Graphics,tileX:number,tileY:number,size:number):NeighborhoodPlacement{
  type Candidate={id:string;point:Point;seed:number;house:boolean;nx:number;ny:number};
  const trees:TreePlacement[]=[],houses:HousePlacement[]=[],items=new Map<string,Segment>(),cells=new Map<string,Candidate[]>();
  for(let x=Math.floor((tileX*size-140)/this.cell);x<=Math.floor(((tileX+1)*size+140)/this.cell);x++)for(let y=Math.floor((tileY*size-140)/this.cell);y<=Math.floor(((tileY+1)*size+140)/this.cell);y++)
   for(const road of this.roads.get(x+'/'+y)||[])items.set(road.key,road);
  const add=(candidate:Candidate)=>{
   const p=candidate.point;if(p[0]<tileX*size-110||p[0]>=(tileX+1)*size+110||p[1]<tileY*size-110||p[1]>=(tileY+1)*size+110)return;
   const key=Math.floor(p[0]/100)+'/'+Math.floor(p[1]/100),list=cells.get(key);if(list)list.push(candidate);else cells.set(key,[candidate]);
  };
  for(const road of items.values()){
   const dx=road.b[0]-road.a[0],dy=road.b[1]-road.a[1],length=Math.hypot(dx,dy);if(length<12)continue;
   const count=Math.max(1,Math.floor(length/26)),nx=-dy/length,ny=dx/length;
   for(let i=0;i<count;i++)for(const side of [-1,1]){
    const id=road.key+'/'+i+'/'+side,seed=this.hash(id),t=(i+.5)/count,baseX=road.a[0]+dx*t,baseY=road.a[1]+dy*t;
    if(seed%3!==0){const dist=road.width/2+8+(seed%7);add({id,seed,point:[baseX+nx*side*dist,baseY+ny*side*dist],house:false,nx:nx*side,ny:ny*side});}
    if(seed%4===0){const dist=road.width/2+23+(seed%8);add({id:id+'/house',seed:this.hash(id+'/house'),point:[baseX+nx*side*dist,baseY+ny*side*dist],house:true,nx:nx*side,ny:ny*side});}
   }
  }
  const ranked:Array<Candidate>=[];
  for(const key of Array.from(cells.keys()).sort()){
   const candidates=cells.get(key)!;candidates.sort((a,b)=>Number(b.house)-Number(a.house)||a.seed-b.seed||a.id.localeCompare(b.id));
   let treeCount=0,houseCount=0;
   for(const c of candidates){
    if(c.house?houseCount>=1:treeCount>=6)continue;
    if(!this.safe(c.point,c.house?15:6))continue;
    if(c.house)houseCount++;else treeCount++;ranked.push(c);
   }
  }
  const priority=(a:Candidate,b:Candidate)=>Number(b.house)-Number(a.house)||a.seed-b.seed||a.id.localeCompare(b.id);
  for(const c of ranked){
    const radius=c.house?15:6,p=c.point;
    if(Math.floor(p[0]/size)!==tileX||Math.floor(p[1]/size)!==tileY)continue;
    // A candidate loses to any higher-priority overlapping eligible candidate, independent of tile load order.
    if(ranked.some(other=>other!==c&&priority(other,c)<0&&Math.hypot(p[0]-other.point[0],p[1]-other.point[1])<radius+(other.house?15:6)))continue;
    if(c.house){
     houses.push({id:c.id,point:p,variant:c.seed%3});
     // Courtyard border and approach remain inside the protected radius.
     g.fillColor=col('#C7B69A');g.roundRect(p[0]-10,p[1]-8,20,16,1);g.fill();
     g.strokeColor=col('#8D7E68');g.lineWidth=.45;g.roundRect(p[0]-10,p[1]-8,20,16,1);g.stroke();
     g.strokeColor=col('#E3D1B2');g.lineWidth=1.6;g.moveTo(p[0]-c.nx*5,p[1]-c.ny*5);g.lineTo(p[0]-c.nx*9,p[1]-c.ny*7);g.stroke();
     g.fillColor=col('#768D50');g.circle(p[0]+7,p[1]+5,1.6);g.fill();
     g.fillColor=col('#DED1B7');g.roundRect(p[0]-6,p[1]-4,12,8,1);g.fill();
    }else{
     trees.push({id:c.id,point:p,warm:c.seed%13===0,diameter:(c.seed%13===0?5:6)*(.9+(c.seed%5)*.04)});
     g.fillColor=col('#514F3044');g.ellipse(p[0]+1.8,p[1]-1.8,5,3.8);g.fill();
     g.fillColor=col(c.seed%2?'#718D49':'#A4A557');g.circle(p[0],p[1],3.8);g.fill();
     g.fillColor=col('#D2C47777');g.circle(p[0]-1.1,p[1]+1.3,2);g.fill();
    }
  }
  return {trees,houses};
 }
}
