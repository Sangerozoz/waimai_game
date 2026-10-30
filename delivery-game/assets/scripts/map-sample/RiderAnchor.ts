import { CityData, MapRoute, Point } from './MapTypes';
import { RoadRouter } from './RoadRouter';

/** A position on one directed road segment, measured from its from-node. */
export interface RiderAnchor { road:string; from:string; to:string; fraction:number }
export interface AnchorExit { node:string; metres:number; seconds:number; reverse:boolean }

/** Derive an exact position from an existing road-time route. */
export function anchorAt(route:MapRoute,roadSeconds:number):RiderAnchor {
 if(!Number.isFinite(roadSeconds)||roadSeconds<0||!route.segments.length)throw new Error('无效的骑手进度');
 let rest=roadSeconds;
 if(route.origin){const o=route.origin;if(rest<=o.exit.seconds&&o.exit.seconds>0){const t=rest/o.exit.seconds;return {...o.anchor,fraction:o.exit.reverse?o.anchor.fraction*(1-t):o.anchor.fraction+(1-o.anchor.fraction)*t};}rest=Math.max(0,rest-o.exit.seconds);}
 for(let i=0;i<route.segments.length;i++){
  const s=route.segments[i];
  if(rest<=s.seconds||i===route.segments.length-1)return {road:s.road,from:s.from,to:s.to,fraction:Math.min(1,rest/s.seconds)};
  rest-=s.seconds;
 }
 throw new Error('无效路线');
}

/** Validate against the real directed road and enumerate legal exits from the point. */
export function anchorExits(data:CityData,anchor:RiderAnchor):{point:Point;exits:AnchorExit[]} {
 if(!anchor||!Number.isFinite(anchor.fraction)||anchor.fraction<0||anchor.fraction>1)throw new Error('无效的骑手位置');
 const road=data.roads.find(r=>r.id===anchor.road),from=data.nodes.find(n=>n.id===anchor.from),to=data.nodes.find(n=>n.id===anchor.to);
 if(!road||!from||!to||road.speed<=0)throw new Error('无效的骑手道路');
 const index=road.nodes.findIndex((id,i)=>i+1<road.nodes.length&&((id===from.id&&road.nodes[i+1]===to.id)||(id===to.id&&road.nodes[i+1]===from.id)));
 if(index<0)throw new Error('骑手道路不相邻');
 const forward=road.nodes[index]===from.id;
 if(forward?road.direction===-1:road.direction===1)throw new Error('骑手原方向不合法');
 const dx=to.x-from.x,dy=to.y-from.y,total=Math.hypot(dx,dy);
 if(total<=0)throw new Error('骑手道路长度无效');
 const point:Point=[from.x+dx*anchor.fraction,from.y+dy*anchor.fraction];
 const exits:AnchorExit[]=[{node:to.id,metres:total*(1-anchor.fraction),seconds:total*(1-anchor.fraction)/road.speed,reverse:false}];
 if(road.direction===0||anchor.fraction===0)exits.push({node:from.id,metres:total*anchor.fraction,seconds:total*anchor.fraction/road.speed,reverse:true});
 return {point,exits};
}

export interface AnchorRoute { anchor:RiderAnchor; start:Point; exit:AnchorExit; tail:MapRoute; metres:number; seconds:number }
/** Route from the actual position via an allowed endpoint and the real road graph. */
export function routeFromAnchor(data:CityData,anchor:RiderAnchor,destination:string,preference:import('./MapTypes').Preference,providedRouter?:RoadRouter):AnchorRoute|null {
 const {point,exits}=anchorExits(data,anchor),router=providedRouter||new RoadRouter(data),roads=new Map(data.roads.map(r=>[r.id,r]));
 const multiplier=(roadId:string,roughness:number)=>{
  const road=roads.get(roadId)!;
  return preference==='smooth'?1+roughness*9:preference==='main'?(road.kind==='primary'||road.kind==='secondary'||road.kind==='tertiary'?1:2.8):1;
 };
 let best:AnchorRoute|null=null,bestCost=Infinity;
 for(const exit of exits){
  const tail=router.find(exit.node,destination,preference);if(!tail)continue;
  const originRoad=roads.get(anchor.road)!,cost=exit.seconds*multiplier(anchor.road,originRoad.roughness)+tail.segments.reduce((sum,s)=>sum+s.seconds*multiplier(s.road,s.roughness),0);
  if(cost<bestCost){bestCost=cost;best={anchor:{...anchor},start:point,exit,tail,metres:exit.metres+tail.metres,seconds:exit.seconds+tail.seconds};}
 }
 return best;
}
