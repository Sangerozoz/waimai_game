import { CityData, MapRoute, Preference, Point, MapNode, RouteSegment } from './MapTypes';

interface Edge extends RouteSegment { major: boolean }
class Queue {
  private items: Array<{id:string; cost:number}> = [];
  push(id:string,cost:number):void {
    const item={id,cost};this.items.push(item);let i=this.items.length-1;
    while(i>0){const parent=(i-1)>>1;if(this.items[parent].cost<=cost)break;this.items[i]=this.items[parent];i=parent;}
    this.items[i]=item;
  }
  pop():{id:string;cost:number}|undefined {
    if(!this.items.length)return undefined;
    const first=this.items[0],last=this.items.pop()!;
    if(this.items.length){let i=0;while(i*2+1<this.items.length){let child=i*2+1;if(child+1<this.items.length&&this.items[child+1].cost<this.items[child].cost)child++;
      if(this.items[child].cost>=last.cost)break;this.items[i]=this.items[child];i=child;}this.items[i]=last;}
    return first;
  }
}

export class RoadRouter {
  readonly nodes = new Map<string,MapNode>();
  private readonly adjacency = new Map<string,Edge[]>();
  constructor(data: CityData) {
    for(const node of data.nodes){this.nodes.set(node.id,node);this.adjacency.set(node.id,[]);}
    for(const road of data.roads){
      for(let i=1;i<road.nodes.length;i++){
        const a=this.nodes.get(road.nodes[i-1]),b=this.nodes.get(road.nodes[i]);if(!a||!b)continue;
        const metres=Math.hypot(b.x-a.x,b.y-a.y);if(metres<=0||road.speed<=0)continue;
        const common={road:road.id,metres,seconds:metres/road.speed,roughness:road.roughness,major:['primary','secondary','tertiary'].indexOf(road.kind)>=0};
        if(road.direction!==-1)this.adjacency.get(a.id)!.push({...common,from:a.id,to:b.id});
        if(road.direction!==1)this.adjacency.get(b.id)!.push({...common,from:b.id,to:a.id});
      }
    }
  }
  find(start: string, end: string, preference: Preference): MapRoute | null {
    if(!this.nodes.has(start)||!this.nodes.has(end))return null;
    const distances=new Map<string,number>([[start,0]]),previous=new Map<string,Edge>(),queue=new Queue();queue.push(start,0);
    let item;
    while((item=queue.pop())){
      if(item.cost!==distances.get(item.id))continue;
      if(item.id===end)break;
      for(const edge of this.adjacency.get(item.id)||[]){
        const multiplier=preference==='smooth'?1+edge.roughness*9:preference==='main'?(edge.major?1:2.8):1;
        const cost=item.cost+edge.seconds*multiplier;
        if(cost<(distances.get(edge.to)??Infinity)){distances.set(edge.to,cost);previous.set(edge.to,edge);queue.push(edge.to,cost);}
      }
    }
    if(start!==end&&!previous.has(end))return null;
    const segments:RouteSegment[]=[];
    for(let at=end;at!==start;){const edge=previous.get(at)!;segments.push(edge);at=edge.from;}
    segments.reverse();const nodes=[start,...segments.map(s=>s.to)];
    const points=nodes.map(id=>{const n=this.nodes.get(id)!;return [n.x,n.y] as Point;});
    const metres=segments.reduce((v,s)=>v+s.metres,0),seconds=segments.reduce((v,s)=>v+s.seconds,0);
    // Game-only cumulative exposure, not a claim about surveyed road quality.
    const risk=1-Math.exp(-segments.reduce((v,s)=>v+s.metres*s.roughness,0)/2300);
    return {preference,nodes,points,segments,metres,seconds,risk};
  }
}
export function routePosition(route: MapRoute, seconds: number): { point: Point; angle: number } {
  let remaining=Math.max(0,seconds);
  if(route.origin){const a=route.origin.start,b=route.points[0],duration=route.origin.exit.seconds;if(remaining<=duration&&duration>0){const t=remaining/duration;return {point:[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t],angle:Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI};}remaining=Math.max(0,remaining-duration);}
  for(let i=0;i<route.segments.length;i++){
    const segment=route.segments[i],a=route.points[i],b=route.points[i+1];
    if(remaining<=segment.seconds||i===route.segments.length-1){
      const t=Math.min(1,remaining/segment.seconds);
      return {point:[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t],angle:Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI};
    }remaining-=segment.seconds;
  }
  return {point:route.points[0],angle:0};
}
