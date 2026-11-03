import { Graphics, Node } from 'cc';
import { HomeMapArt } from './HomeMapArt';
import { Point } from './MapTypes';
import { col, item } from './SampleUI';
const BLOCK=96;
/** Restrained, world-anchored illustrative marks; not mapped road facilities. */
export class HomeMapDetailInk {
 readonly node:Node;
 private blocks=new Map<string,Node>();
 constructor(parent:Node,private art:HomeMapArt){this.node=item(parent,'StreetDetailInk');}
 sync(left:number,bottom:number,right:number,top:number,scale:number):void{
  const wanted=new Set<string>();
  if(scale>=1.5)for(let x=Math.floor((left-15)/BLOCK);x<=Math.floor((right+15)/BLOCK);x++)for(let y=Math.floor((bottom-15)/BLOCK);y<=Math.floor((top+15)/BLOCK);y++){
   const key=x+'/'+y;wanted.add(key);if(this.blocks.has(key))continue;
   const l=x*BLOCK,b=y*BLOCK,r=l+BLOCK,t=b+BLOCK,roads=this.art.roadSegments(l,b,r,t),areas=this.art.areaGeometry(l,b,r,t);
   const n=item(this.node,'Details-'+key),g=n.addComponent(Graphics);this.blocks.set(key,n);
   for(const road of roads){
    if(road.bridge||road.width<8)continue;const dx=road.b[0]-road.a[0],dy=road.b[1]-road.a[1],len=Math.hypot(dx,dy);if(len<36)continue;
    const ux=dx/len,uy=dy/len;
    for(let d=12;d<len-12;d+=12){
     const p:Point=[road.a[0]+ux*d,road.a[1]+uy*d];if(p[0]<l||p[0]>=r||p[1]<b||p[1]>=t||!this.art.detailSafe(p,5))continue;
     // Skip intersections and nearby non-connected road segments.
     if(roads.some(o=>o!==road&&Math.min(Math.hypot(p[0]-o.a[0],p[1]-o.a[1]),Math.hypot(p[0]-o.b[0],p[1]-o.b[1]))<12))continue;
     g.strokeColor=col('#F5E6BCAA');g.lineWidth=.35;g.moveTo(p[0]-ux*2,p[1]-uy*2);g.lineTo(p[0]+ux*2,p[1]+uy*2);g.stroke();
    }
   }
   // Only use exact shared endpoints of three or more non-bridge wide-road segments.
   const joints=new Map<string,typeof roads>();
   for(const road of roads)if(!road.bridge&&road.width>=8)for(const p of [road.a,road.b]){
    const key=p[0]+','+p[1],group=joints.get(key);if(group)group.push(road);else joints.set(key,[road]);
   }
   for(const connected of joints.values()){
    if(connected.length<3)continue;const base=connected[0];
    const joint=[base.a,base.b].find(p=>connected.every(v=>(v.a[0]===p[0]&&v.a[1]===p[1])||(v.b[0]===p[0]&&v.b[1]===p[1])));if(!joint)continue;
    if(joint[0]<l||joint[0]>=r||joint[1]<b||joint[1]>=t||!this.art.detailSafe(joint,18))continue;
    const end=base.a===joint?base.b:base.a,dx=end[0]-joint[0],dy=end[1]-joint[1],length=Math.hypot(dx,dy);if(length<30)continue;
    const ux=dx/length,uy=dy/length,nx=-uy,ny=ux;
    const transverse=connected.some(v=>{const q=v.a[0]===joint[0]&&v.a[1]===joint[1]?v.b:v.a,dx=q[0]-joint[0],dy=q[1]-joint[1],len=Math.hypot(dx,dy);return len>20&&Math.abs((dx*ux+dy*uy)/len)<.4;});
    if(!transverse)continue;
    const cx=joint[0]+ux*9,cy=joint[1]+uy*9;g.strokeColor=col('#F8F1DAD0');g.lineWidth=.7;
    for(let k=-2;k<=2;k++){const px=cx+nx*k*1.1,py=cy+ny*k*1.1;g.moveTo(px-ux*1.4,py-uy*1.4);g.lineTo(px+ux*1.4,py+uy*1.4);g.stroke();}
   }
   for(const poly of areas.buildings){
    const cx=(poly.minX+poly.minX2)/2,cy=(poly.minY+poly.minY2)/2;if(cx<l||cx>=r||cy<b||cy>=t)continue;
    const pts=poly.p;g.strokeColor=col('#FFF8E468');g.lineWidth=.35;g.moveTo(pts[0][0],pts[0][1]);for(const p of pts.slice(1))g.lineTo(p[0],p[1]);g.close();g.stroke();
    if(Math.abs(Math.floor(cx*13)+Math.floor(cy*7))%4!==0)continue;
    const corners:Point[]=[[cx-1,cy-1],[cx+1,cy-1],[cx+1,cy+1],[cx-1,cy+1]];
    if(!corners.every(p=>this.art.insideRoof(p,poly,1)))continue;
    g.fillColor=col('#514A3A55');g.rect(cx-.8,cy-1.2,2,2);g.fill();g.fillColor=col('#DDD8C8');g.rect(cx-1,cy-1,2,2);g.fill();
   }
  }
  for(const [key,node] of this.blocks)if(!wanted.has(key)){node.destroy();this.blocks.delete(key);}
 }
}
