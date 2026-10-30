import { Bounds, contains } from './CityExtent';
import { CityData, MapNode } from './MapTypes';

export type PlaceArea='urban'|'suburb'|'remote';
export type DispatchArea=PlaceArea|'cross';
const points=new WeakMap<CityData,Map<string,MapNode>>();

export function buildDispatchAreas(data:CityData):{zones:Record<string,PlaceArea>;urbanBounds:Bounds} {
  const cells=new Map<string,number>(),key=(x:number,y:number)=>`${Math.floor(x/300)}/${Math.floor(y/300)}`;
  for(const polygon of data.buildings){
    if(!polygon.length)continue;
    const x=polygon.reduce((s,p)=>s+p[0],0)/polygon.length,y=polygon.reduce((s,p)=>s+p[1],0)/polygon.length,k=key(x,y);
    cells.set(k,(cells.get(k)||0)+1);
  }
  const zones:Record<string,PlaceArea>={},dense:MapNode[]=[];
  for(const n of data.nodes){
    const count=cells.get(key(n.x,n.y))||0;zones[n.id]=count>=10?'urban':count>=3?'suburb':'remote';
    if(count>=10&&(!data.dispatchBounds||contains(data.dispatchBounds,[n.x,n.y])))dense.push(n);
  }
  const bounds=data.dispatchBounds||data.playBounds||{minX:0,maxX:data.width,minY:0,maxY:data.height};
  if(!dense.length){for(const n of data.nodes)zones[n.id]='urban';return {zones,urbanBounds:bounds};}
  return {zones,urbanBounds:{minX:Math.min(...dense.map(n=>n.x)),maxX:Math.max(...dense.map(n=>n.x)),minY:Math.min(...dense.map(n=>n.y)),maxY:Math.max(...dense.map(n=>n.y))}};
}

/** Classify the complete pickup/delivery trip, including a rider starting at the opposite side of town. */
export function dispatchAreaForTrip(data:CityData,from:number,to:number,start?:string):DispatchArea {
  if(!data.dispatchAreas||!data.urbanBounds)return 'urban';
  let nodes=points.get(data);if(!nodes){nodes=new Map(data.nodes.map(n=>[n.id,n]));points.set(data,nodes);}
  const a=nodes.get(data.pois[from].node)!,b=nodes.get(data.pois[to].node)!,bounds=data.urbanBounds;
  const alongX=bounds.maxX-bounds.minX>=bounds.maxY-bounds.minY;
  const min=alongX?bounds.minX:bounds.minY,max=alongX?bounds.maxX:bounds.maxY,span=max-min;
  const positions=[a,b,...(start&&nodes.has(start)?[nodes.get(start)!]:[])].map(n=>alongX?n.x:n.y);
  const low=Math.min(...positions),high=Math.max(...positions);
  if(span>0&&high-low>=span*.55&&low<min+span/3&&high>max-span/3)return 'cross';
  const fromArea=data.dispatchAreas[a.id],toArea=data.dispatchAreas[b.id];
  if(fromArea==='remote'||toArea==='remote')return 'remote';
  if(fromArea==='suburb'||toArea==='suburb')return 'suburb';
  return 'urban';
}
