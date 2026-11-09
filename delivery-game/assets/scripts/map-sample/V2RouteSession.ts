import { V2DispatchOrder, V2DispatchSnapshot } from '../domain/V2DispatchSession';
import { CityData, MapRoute, Point, Preference, RouteSegment } from './MapTypes';
import { RoadRouter, routePosition } from './RoadRouter';
import { contains } from './CityExtent';
import { parseV2Load,slotLoadForOrderId,sameV2Load } from '../domain/V2LoadRules';

export interface V2RouteOrder extends V2DispatchOrder { pickupNode:string; dropoffNode:string; pickupName:string; dropoffName:string;sourceOfferId?:string }
interface Stop { orderId:string; orderIds:string[]; kind:'pickup'|'dropoff'; node:string }
interface Anchor { node:string; edge:RouteSegment|null; elapsed:number }
export interface V2RouteSnapshot {
 format:'county-v2-route';version:2|3;timeProfile:'road40-service2-1-grouped-v2';stopPolicy:'legacy-sequential'|'grouped';mapKey:string;nextId:number;tripId:number;loadProfile?:'slots-v1';sourceNextId?:number;
 anchor:Anchor;orders:V2RouteOrder[];stops:Stop[];legs:MapRoute[];preference:Preference;
 cursor:number;legSeconds:number;serviceSeconds:number;phase:'idle'|'planned'|'travelling'|'pickup'|'service'|'ready'|'finished';
 serviceCharged:boolean;picked:string[];arrivals:{id:string;token:string}[];origin:Anchor;
}
export type V2RouteProgress=Readonly<Pick<V2RouteSnapshot,'tripId'|'phase'|'cursor'|'serviceCharged'|'serviceSeconds'>>;
export type V2RouteMotion=V2RouteProgress&{readonly position:Point};
type LegacyStop=Omit<Stop,'orderIds'>;
type LegacyRouteSnapshot=Omit<V2RouteSnapshot,'version'|'timeProfile'|'stopPolicy'|'stops'|'phase'|'serviceCharged'>&{
 version:1;timeProfile:'road40-service2-1-v1';stops:LegacyStop[];phase:Exclude<V2RouteSnapshot['phase'],'ready'>;serviceCharged?:boolean;
};
const copy=<T>(x:T):T=>JSON.parse(JSON.stringify(x));
function check(x:unknown):asserts x {if(!x)throw new Error('V2路线或存档无效');}
function nonnegative(x:number):boolean{return Number.isFinite(x)&&x>=0;}

interface PreparedMap {router:RoadRouter;places:CityData['pois'];roadEdges:RouteSegment[];key:string;expectedLegs:Map<string,string>}
const EXPECTED_LEGS_LIMIT=16,EXPECTED_LEGS_MAX_CHARS=262144;
const preparedMaps=new WeakMap<CityData,PreparedMap>();
/** Non-security geometry fingerprint; callers treat loaded CityData as immutable. */
function geometryKey(value:string):string {let a=0x811c9dc5,b=0x9e3779b9;for(let i=0;i<value.length;i++){const c=value.charCodeAt(i);a=Math.imul(a^c,0x01000193);b=Math.imul(b^c,0x85ebca6b);}return 'fnv2:'+value.length+':'+(a>>>0).toString(16)+':'+(b>>>0).toString(16);}
function prepare(city:CityData):PreparedMap {
 const cached=preparedMaps.get(city);if(cached)return cached;
 const bounds=city.dispatchBounds||city.playBounds;
 const nodes=city.nodes.filter(n=>!bounds||contains(bounds,[n.x,n.y]));const allowed=new Set(nodes.map(n=>n.id));
 // Split original consecutive runs: removing outside nodes must never create shortcut edges.
 const roads:CityData['roads']=[];
 for(const road of city.roads){let run:string[]=[];let part=0;const flush=()=>{if(run.length>1)roads.push({...road,id:road.id+':v2:'+part++,nodes:run});run=[];};for(const id of road.nodes){if(allowed.has(id))run.push(id);else flush();}flush();}
 const router=new RoadRouter({...city,nodes,roads}),roadEdges:RouteSegment[]=[];
 for(const road of roads)for(let i=1;i<road.nodes.length;i++){const a=router.nodes.get(road.nodes[i-1])!,b=router.nodes.get(road.nodes[i])!,metres=Math.hypot(b.x-a.x,b.y-a.y);if(metres<=0||road.speed<=0)continue;const edge={road:road.id,metres,seconds:metres/road.speed,roughness:road.roughness};if(road.direction!==-1)roadEdges.push({...edge,from:a.id,to:b.id});if(road.direction!==1)roadEdges.push({...edge,from:b.id,to:a.id});}
 const places=city.pois.filter((p,i)=>allowed.has(p.node)&&(!city.operatingPOIs||city.operatingPOIs.includes(i)));check(places.length>1);
 const result={router,places,roadEdges,key:geometryKey(JSON.stringify([nodes,roads,places])),expectedLegs:new Map<string,string>()};preparedMaps.set(city,result);return result;
}

/** Actual directed road geometry, no reward or wall-clock authority. */
export class V2RouteSession {
 private readonly router:RoadRouter;
 private readonly roadEdges:RouteSegment[];
 private readonly places:CityData['pois'];
 private readonly expectedLegs:Map<string,string>;
 private state:V2RouteSnapshot;
 constructor(private readonly city:CityData){
  const prepared=prepare(city);this.router=prepared.router;this.places=prepared.places;this.roadEdges=prepared.roadEdges;this.expectedLegs=prepared.expectedLegs;
  const node=this.places[0].node,anchor={node,edge:null,elapsed:0},mapKey=prepared.key;
  this.state={format:'county-v2-route',version:2,timeProfile:'road40-service2-1-grouped-v2',stopPolicy:'grouped',mapKey,nextId:1,tripId:0,anchor,origin:copy(anchor),orders:[],stops:[],legs:[],preference:'fast',cursor:0,legSeconds:0,serviceSeconds:0,serviceCharged:false,phase:'idle',picked:[],arrivals:[]};
 }
 snapshot():V2RouteSnapshot{return copy(this.state);}
 /** Detached scalar reads never clone route geometry or calculate position. */
 get progress():V2RouteProgress {const s=this.state;return {tripId:s.tripId,phase:s.phase,cursor:s.cursor,serviceCharged:s.serviceCharged,serviceSeconds:s.serviceSeconds};}
 /** position can alias a zero-segment leg; detach its coordinate pair as well. */
 get motion():V2RouteMotion {const position=this.position;return {...this.progress,position:[position[0],position[1]]};}
 serialize():string{return JSON.stringify(this.state);}
 get position():Point {const s=this.state;if(['travelling','pickup','service'].includes(s.phase)&&s.legs[s.cursor])return routePosition(s.legs[s.cursor],s.legSeconds).point;if(s.anchor.edge){const e=s.anchor.edge,a=this.router.nodes.get(e.from)!,b=this.router.nodes.get(e.to)!,t=s.anchor.elapsed/e.seconds;return [a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t];}const n=this.router.nodes.get(s.anchor.node)!;return [n.x,n.y];}
 private path(anchor:Anchor,end:string,preference:Preference):MapRoute|null {
  const route=this.router.find(anchor.edge?anchor.edge.to:anchor.node,end,preference);if(!route)return null;
  if(!anchor.edge)return route;
  const first=this.router.nodes.get(anchor.edge.from)!;
  return {...route,nodes:[first.id,...route.nodes],points:[[first.x,first.y] as Point,...route.points],segments:[copy(anchor.edge),...route.segments],metres:route.metres+anchor.edge.metres,seconds:route.seconds+anchor.edge.seconds};
 }
 private legal(order:V2RouteOrder,version:2|3=2):boolean {
  if(!(order&&typeof order.id==='string'&&order.id.length>0&&order.id.length<=200&&(order.kind==='ordinary'||order.kind==='special')&&this.places.some(p=>p.node===order.pickupNode)&&this.places.some(p=>p.node===order.dropoffNode)&&order.pickupNode!==order.dropoffNode&&typeof order.pickupName==='string'&&typeof order.dropoffName==='string'))return false;
  if(version===2)return !('load' in order)&&typeof order.weightKg==='number'&&Number.isSafeInteger(order.weightKg)&&order.weightKg>0;
  if('weightKg' in order||!Object.prototype.propertyIsEnumerable.call(order,'load')||typeof order.sourceOfferId!=='string')return false;
  const match=/^v2-road-([1-9]\d*)$/.exec(order.sourceOfferId);if(!match)return false;const ordinal=Number(match[1]);if(!Number.isSafeInteger(ordinal)||order.kind==='ordinary'&&order.id!==order.sourceOfferId)return false;
  const a=this.places[ordinal%this.places.length],b=this.places[(ordinal+1)%this.places.length];
  if(order.pickupNode!==a.node||order.pickupName!==a.name||order.dropoffNode!==b.node||order.dropoffName!==b.name)return false;
  try{const load=parseV2Load(order.load);return load.version==='slots-v1'&&sameV2Load(load,slotLoadForOrderId(order.id));}catch{return false;}
 }
 canonicalSlotOrder(raw:V2RouteOrder):V2RouteOrder {
  check(this.legal(raw,3));const ordinal=Number(raw.sourceOfferId!.slice(8));check(ordinal>=this.state.nextId&&ordinal-this.state.nextId<this.places.length*2);
  return {id:raw.id,kind:raw.kind,sourceOfferId:raw.sourceOfferId!,pickupNode:raw.pickupNode,dropoffNode:raw.dropoffNode,pickupName:raw.pickupName,dropoffName:raw.dropoffName,load:slotLoadForOrderId(raw.id)};
 }
 enableSlots():void {check(this.state.phase==='idle'&&this.state.orders.length===0);this.state={...this.state,version:3,loadProfile:'slots-v1',sourceNextId:this.state.nextId};}
 /** Require an operating pair that is also unambiguous in the authoritative source.
  * Unknown/ambiguous names remain legal singleton offers, never a grouping key.
  */
 private merchantKey(order:V2RouteOrder):string|null {
  const matches=(p:CityData['pois'][number])=>p.node===order.pickupNode&&p.name===order.pickupName;
  return order.pickupName.length>0&&this.places.some(matches)&&this.city.pois.filter(matches).length===1?JSON.stringify([order.pickupNode,order.pickupName]):null;
 }
 private singletonStop(order:V2RouteOrder,kind:Stop['kind']):Stop {return {orderId:order.id,orderIds:[order.id],kind,node:kind==='pickup'?order.pickupNode:order.dropoffNode};}
 private plannedStops(orders:V2RouteOrder[],policy:V2RouteSnapshot['stopPolicy']):Stop[] {
  if(policy==='legacy-sequential')return orders.flatMap(o=>[this.singletonStop(o,'pickup'),this.singletonStop(o,'dropoff')]);
  const groups:V2RouteOrder[][]=[],known=new Map<string,V2RouteOrder[]>();
  for(const order of orders){const key=this.merchantKey(order),group=key===null?undefined:known.get(key);if(group)group.push(order);else {const next=[order];groups.push(next);if(key!==null)known.set(key,next);}}
  return groups.flatMap(group=>[{orderId:group[0].id,orderIds:group.map(o=>o.id),kind:'pickup' as const,node:group[0].pickupNode},...group.map(o=>this.singletonStop(o,'dropoff'))]);
 }
 get serviceBudget():{seconds:number;stamina:number} {const pickupStops=this.state.stops.filter(s=>s.kind==='pickup').length,dropoffStops=this.state.stops.filter(s=>s.kind==='dropoff').length;return {seconds:pickupStops*2+dropoffStops,stamina:pickupStops+dropoffStops};}
 candidates(capacityKg:number,usedIds:string[],count=8,maxMetres=Infinity):V2RouteOrder[]{
  check(nonnegative(capacityKg)&&Number.isSafeInteger(count)&&count>0&&count<=50);const result:V2RouteOrder[]=[];const weights=[1,2,3].filter(w=>w<=capacityKg);if(!weights.length)return [];
  // Bounded deterministic scan, stable IDs until accepted; disconnected POIs are skipped.
  for(let k=0;k<this.places.length*2&&result.length<count;k++){
   const a=this.places[(this.state.nextId+k)%this.places.length],b=this.places[(this.state.nextId+k+1)%this.places.length];const id='v2-road-'+(this.state.nextId+k);
   if(a.node===b.node||usedIds.includes(id)||!this.path(this.state.anchor,a.node,'fast')||!this.router.find(a.node,b.node,'fast')||!this.router.find(b.node,this.state.anchor.edge?.to||this.state.anchor.node,'fast'))continue;
   if(this.fastest(a.node,b.node).metres>maxMetres)continue;
   result.push({id,kind:'ordinary',weightKg:weights[k%weights.length],pickupNode:a.node,dropoffNode:b.node,pickupName:a.name,dropoffName:b.name});
  }return result;
 }
 slotCandidates(capacitySlots:number,usedIds:string[],count:number,maxMetres=Infinity):V2RouteOrder[]{
  check(Number.isSafeInteger(capacitySlots)&&capacitySlots>0&&Number.isSafeInteger(count)&&count>0&&count<=50);const result:V2RouteOrder[]=[];
  for(let k=0;k<this.places.length*2&&result.length<count;k++){
   const a=this.places[(this.state.nextId+k)%this.places.length],b=this.places[(this.state.nextId+k+1)%this.places.length],id='v2-road-'+(this.state.nextId+k);
   if(!Number.isSafeInteger(this.state.nextId+k)||a.node===b.node||usedIds.includes(id)||!this.path(this.state.anchor,a.node,'fast')||!this.router.find(a.node,b.node,'fast')||!this.router.find(b.node,this.state.anchor.edge?.to||this.state.anchor.node,'fast'))continue;
   if(this.fastest(a.node,b.node).metres>maxMetres)continue;
   const load=slotLoadForOrderId(id);if(load.occupiedSlots>capacitySlots)continue;
   result.push({id,kind:'ordinary',sourceOfferId:id,load,pickupNode:a.node,dropoffNode:b.node,pickupName:a.name,dropoffName:b.name});
  }return result;
 }
 slotSpecialCandidate(id:string,capacitySlots:number,usedIds:string[],maxMetres=Infinity):V2RouteOrder|null {
  const candidate=this.slotCandidates(capacitySlots,usedIds,1,maxMetres)[0];if(!candidate)return null;
  const load=slotLoadForOrderId(id);return load.occupiedSlots<=capacitySlots?{...candidate,id,kind:'special',load}:null;
 }
 fastest(pickup:string,dropoff:string):{metres:number;gameSeconds:number;heldMetres:number} {const a=this.path(this.state.anchor,pickup,'fast'),b=this.router.find(pickup,dropoff,'fast');check(a&&b);return {metres:a.metres+b.metres-(this.state.anchor.edge?this.state.anchor.edge.metres*this.state.anchor.elapsed/this.state.anchor.edge.seconds:0),gameSeconds:a.seconds+b.seconds-this.state.anchor.elapsed+90,heldMetres:b.metres};}
 specialCandidate(id:string,capacityKg:number,usedIds:string[],maxMetres=Infinity):V2RouteOrder|null {const candidate=this.candidates(capacityKg,usedIds,1,maxMetres)[0];return candidate?{...candidate,id,kind:'special',weightKg:1}:null;}
 plan(orders:V2RouteOrder[]):void {
  this.planOrders(orders,false);
 }
 planSlots(orders:V2RouteOrder[]):void {this.planOrders(orders,true);}
 private planOrders(orders:V2RouteOrder[],slots:boolean):void {
  check(['idle','finished'].includes(this.state.phase)&&Array.isArray(orders)&&orders.length>0&&orders.every(o=>this.legal(o,slots?3:2))&&new Set(orders.map(o=>o.id)).size===orders.length);
  if(slots)orders.forEach(o=>this.canonicalSlotOrder(o));else check(this.state.version===2);
  check(Number.isSafeInteger(this.state.nextId+orders.length+8));
  const stops=this.plannedStops(orders,'grouped');
  let anchor=copy(this.state.anchor);for(const stop of stops){check(this.path(anchor,stop.node,'fast'));anchor={node:stop.node,edge:null,elapsed:0};}
  this.state={...this.state,...(slots?{version:3 as const,loadProfile:'slots-v1' as const,sourceNextId:this.state.nextId}:{}),stopPolicy:'grouped',orders:copy(orders),stops,legs:[],origin:copy(this.state.anchor),cursor:0,legSeconds:0,serviceSeconds:0,serviceCharged:false,phase:'planned',picked:[],arrivals:[],tripId:this.state.tripId+1,nextId:this.state.nextId+orders.length+8};
 }
 private makeLegs(preference:Preference,origin=this.state.origin,stops:readonly {node:string}[]=this.state.stops):MapRoute[]{let anchor=copy(origin);return stops.map(stop=>{const route=this.path(anchor,stop.node,preference);check(route);anchor={node:stop.node,edge:null,elapsed:0};return route;});}
 /** Cache only router-derived immutable strings, never legs supplied by a checkpoint.
  * Namespace is the exact PreparedMap/router instance, not the checkpoint's weak mapKey.
  * CityData has the existing immutable-loaded-map contract (see prepare/geometryKey).
  */
 private expectedLegsJSON(preference:Preference,origin=this.state.origin,stops:readonly {node:string}[]=this.state.stops):string {
  const key=JSON.stringify([origin,stops,preference]);
  const cached=this.expectedLegs.get(key);
  if(cached!==undefined){this.expectedLegs.delete(key);this.expectedLegs.set(key,cached);return cached;}
  const expected=JSON.stringify(this.makeLegs(preference,origin,stops));
  // Oversize plans still receive full validation, without retaining an unbounded cache entry.
  if(key.length+expected.length<=EXPECTED_LEGS_MAX_CHARS){
   this.expectedLegs.set(key,expected);
   if(this.expectedLegs.size>EXPECTED_LEGS_LIMIT)this.expectedLegs.delete(this.expectedLegs.keys().next().value!);
  }
  return expected;
 }
 choices():{preference:Preference;aliases:Preference[];metres:number;seconds:number;arrivals:{id:string;roadSeconds:number;serviceSeconds:number}[]}[]{
  check(this.state.phase==='planned');const choices:{preference:Preference;aliases:Preference[];metres:number;seconds:number;arrivals:{id:string;roadSeconds:number;serviceSeconds:number}[];key:string}[]=[];
  for(const p of ['fast','main','smooth'] as Preference[]){
   const legs=this.makeLegs(p),key=JSON.stringify(legs.map(l=>l.segments.map(s=>[s.from,s.to,s.road]))),same=choices.find(c=>c.key===key);
   if(same){same.aliases.push(p);continue;}
   let roadSeconds=0,serviceSeconds=0;const arrivals:{id:string;roadSeconds:number;serviceSeconds:number}[]=[];
   for(let i=0;i<legs.length;i++){
    const stop=this.state.stops[i];roadSeconds+=legs[i].seconds-(i===0?this.state.origin.elapsed:0);serviceSeconds+=stop.kind==='pickup'?2:1;
    if(stop.kind==='dropoff')arrivals.push({id:stop.orderId,roadSeconds,serviceSeconds});
   }
   const ids=new Set(arrivals.map(a=>a.id));check(arrivals.length===this.state.orders.length&&ids.size===arrivals.length&&this.state.orders.every(o=>ids.has(o.id)));
   choices.push({preference:p,aliases:[p],metres:legs.reduce((n,l)=>n+l.metres,0)-(this.state.origin.edge?this.state.origin.edge.metres*this.state.origin.elapsed/this.state.origin.edge.seconds:0),seconds:(legs.reduce((n,l)=>n+l.seconds,0)-this.state.origin.elapsed)/40+this.serviceBudget.seconds,arrivals,key});
  }return choices.map(({key,...rest})=>rest);
 }
 beginTrip(dispatch:V2DispatchSnapshot,preference:Preference='fast'):void {
  check(this.state.phase==='planned'&&['fast','main','smooth'].includes(preference));this.assertDispatch(dispatch);
  this.state.legs=this.makeLegs(preference);this.state.preference=preference;this.state.phase='travelling';this.state.legSeconds=this.state.origin.elapsed;
 }
 pickup():void {check(this.state.phase==='pickup');const stop=this.state.stops[this.state.cursor];check(stop.kind==='pickup');this.state.picked.push(...stop.orderIds);this.state.phase='service';this.state.serviceSeconds=0;this.state.serviceCharged=false;}
 continueTrip():void {check(this.state.phase==='ready');this.state.phase='travelling';}
 advance(seconds:number,automaticPickup:boolean,speed=1,hooks?:{roadTimeFactor:number;travel:(metres:number,gameSeconds:number)=>number;service:(id:string,kind:'pickup'|'dropoff')=>boolean;pickupGroup?:(ids:string[])=>boolean;serviceTime:(seconds:number)=>void;arrival?:(id:string,token:string,elapsedSeconds:number)=>void}):number {
  check(nonnegative(seconds)&&nonnegative(speed)&&speed>0);let remaining=seconds;const s=this.state;
  for(let guard=0;guard<s.stops.length*4+4;guard++){
   // No automatic click or service charge may run on an exhausted allowance.
   if(remaining<=0)return seconds-remaining;
   if(s.phase==='pickup'){if(!automaticPickup)return seconds-remaining;this.pickup();}
   if(s.phase==='travelling'){
    const roadRate=40*speed/(hooks?.roadTimeFactor||1),leg=s.legs[s.cursor];
    let cursor=s.legSeconds;
    for(const edge of leg.segments){
     if(cursor>=edge.seconds){cursor-=edge.seconds;continue;}
     const roadSeconds=Math.min(edge.seconds-cursor,remaining*roadRate),metres=edge.metres*roadSeconds/edge.seconds;
     const fraction=hooks?hooks.travel(metres,roadSeconds*(hooks.roadTimeFactor||1)):1;
     s.legSeconds+=roadSeconds*fraction;remaining-=roadSeconds*fraction/roadRate;
     if(fraction<1||remaining<=0&&s.legSeconds<leg.seconds-1e-8)return seconds-remaining;
     cursor=0;
    }
    s.legSeconds=leg.seconds;s.anchor={node:s.stops[s.cursor].node,edge:null,elapsed:0};s.phase=s.stops[s.cursor].kind==='pickup'?'pickup':'service';s.serviceSeconds=0;s.serviceCharged=false;continue;
   }
   if(s.phase==='service'){
    const stop=s.stops[s.cursor];if(!s.serviceCharged){
     if(stop.kind==='pickup'&&stop.orderIds.length>1){const pickupGroup=hooks?.pickupGroup;check(pickupGroup);if(!pickupGroup([...stop.orderIds]))return seconds-remaining;}
     else if(hooks&&!hooks.service(stop.orderId,stop.kind))return seconds-remaining;
     s.serviceCharged=true;
    }
    const duration=stop.kind==='pickup'?2:1,used=Math.min(remaining,duration-s.serviceSeconds);s.serviceSeconds+=used;remaining-=used;hooks?.serviceTime(used);if(s.serviceSeconds<duration)return seconds-remaining;
    // Elapsed real seconds include actual travel fractions and this completed service.
    if(stop.kind==='dropoff'){check(s.picked.includes(stop.orderId));const token='arrival:'+s.tripId+':'+s.cursor+':'+stop.orderId;s.arrivals.push({id:stop.orderId,token});hooks?.arrival?.(stop.orderId,token,seconds-remaining);}
    s.cursor++;s.legSeconds=0;s.serviceSeconds=0;s.serviceCharged=false;if(s.cursor===s.stops.length){s.phase='finished';return seconds-remaining;}
    if(stop.kind==='pickup'){s.phase='ready';return seconds-remaining;}
    s.phase='travelling';continue;
   }return seconds-remaining;
  }
  return seconds-remaining;
 }
 private sameOrderLoad(a:Readonly<V2DispatchOrder>,b:Readonly<V2DispatchOrder>):boolean {return a.load&&b.load?!('weightKg' in a)&&!('weightKg' in b)&&sameV2Load(parseV2Load(a.load),parseV2Load(b.load)):!('load' in a)&&!('load' in b)&&a.weightKg===b.weightKg;}
 verifyArrival(order:Readonly<V2DispatchOrder>,token:string):boolean{return this.state.arrivals.some(a=>a.id===order.id&&a.token===token)&&this.state.orders.some(o=>o.id===order.id&&o.kind===order.kind&&this.sameOrderLoad(o,order));}
 cancel():void {
  const s=this.state;if(s.phase==='travelling'){const leg=s.legs[s.cursor];let elapsed=s.legSeconds;let anchor:Anchor={node:s.stops[s.cursor].node,edge:null,elapsed:0};for(const edge of leg.segments){if(elapsed<edge.seconds){anchor={node:edge.from,edge:copy(edge),elapsed};break;}elapsed-=edge.seconds;}s.anchor=anchor;}
  s.serviceCharged=false;s.phase='idle';s.orders=[];s.stops=[];s.legs=[];s.cursor=0;s.legSeconds=0;s.serviceSeconds=0;s.picked=[];s.arrivals=[];s.origin=copy(s.anchor);if(s.version===3)s.sourceNextId=s.nextId;
 }
 /** The snapshot argument lets Game check the original combination before upgrade. */
 assertDispatch(dispatch:V2DispatchSnapshot,route:Pick<V2RouteSnapshot,'orders'|'arrivals'>=this.state):void {
  const pending=dispatch.orders.filter(o=>o.status==='pending');
  check(pending.every(o=>route.orders.some(r=>r.id===o.id&&r.kind===o.kind&&this.sameOrderLoad(r,o))));
  check(route.orders.every(o=>dispatch.orders.some(d=>d.id===o.id&&d.kind===o.kind&&this.sameOrderLoad(d,o)&&d.status!=='cancelled')));
  check(dispatch.orders.filter(o=>o.status==='completed'&&route.orders.some(r=>r.id===o.id)).every(o=>route.arrivals.some(a=>a.id===o.id)));
 }
 /** Keep the entire v1 acceptance gate before adding any v2 fields.
  * In-flight legacy plans retain their original stop order and arrival-token indices.
  */
 private static restoreLegacy(city:CityData,s:LegacyRouteSnapshot):V2RouteSession {
  const route=new V2RouteSession(city);check(s&&s.format==='county-v2-route'&&s.version===1&&s.timeProfile==='road40-service2-1-v1'&&s.mapKey===route.state.mapKey);
  check(Number.isSafeInteger(s.nextId)&&s.nextId>0&&Number.isSafeInteger(s.tripId)&&s.tripId>=0&&Array.isArray(s.orders)&&s.orders.every(o=>route.legal(o))&&new Set(s.orders.map(o=>o.id)).size===s.orders.length);
  const validateAnchor=(a:Anchor)=>{check(a&&route.router.nodes.has(a.node)&&nonnegative(a.elapsed));if(a.edge){check(route.roadEdges.some(e=>e.from===a.edge!.from&&e.to===a.edge!.to&&e.road===a.edge!.road&&e.metres===a.edge!.metres&&e.seconds===a.edge!.seconds&&e.roughness===a.edge!.roughness)&&a.node===a.edge.from&&a.elapsed<a.edge.seconds);}else check(a.elapsed===0);};validateAnchor(s.anchor);validateAnchor(s.origin);
  check(['idle','planned','travelling','pickup','service','finished'].includes(s.phase)&&['fast','main','smooth'].includes(s.preference)&&Number.isSafeInteger(s.cursor)&&s.cursor>=0&&nonnegative(s.legSeconds)&&nonnegative(s.serviceSeconds)&&s.serviceSeconds<2);
  check(JSON.stringify(s.stops)===JSON.stringify(s.orders.flatMap(o=>[{orderId:o.id,kind:'pickup',node:o.pickupNode},{orderId:o.id,kind:'dropoff',node:o.dropoffNode}])));
  check(s.serviceCharged===undefined||typeof s.serviceCharged==='boolean');check(!s.serviceCharged||s.phase==='service');check(s.phase!=='service'||s.serviceSeconds===0||s.serviceCharged!==false);if(s.serviceCharged===undefined)s.serviceCharged=s.phase==='service'&&s.serviceSeconds>0;check(s.cursor<=s.stops.length);
  if(s.phase==='idle'||s.phase==='planned'){check(s.legs.length===0&&s.cursor===0&&s.legSeconds===0&&s.serviceSeconds===0);if(s.phase==='idle')check(s.orders.length===0);}
  else {check(s.orders.length>0&&JSON.stringify(s.legs)===route.expectedLegsJSON(s.preference,s.origin,s.stops));check(s.phase==='finished'?s.cursor===s.stops.length:s.cursor<s.stops.length);if(s.cursor<s.legs.length)check(s.legSeconds<=s.legs[s.cursor].seconds);if(s.phase==='pickup')check(s.stops[s.cursor].kind==='pickup');if(s.phase==='pickup'||s.phase==='service'){check(s.legSeconds===s.legs[s.cursor].seconds&&s.anchor.node===s.stops[s.cursor].node&&s.anchor.edge===null);check(s.serviceSeconds<(s.stops[s.cursor].kind==='pickup'?2:1));}if(s.phase==='travelling')check(s.serviceSeconds===0);if(s.phase==='finished')check(s.legSeconds===0&&s.serviceSeconds===0);}
  const completed=s.stops.slice(0,s.cursor);const expectedPicked=completed.filter(t=>t.kind==='pickup').map(t=>t.orderId);if(s.phase==='service'&&s.stops[s.cursor]?.kind==='pickup')expectedPicked.push(s.stops[s.cursor].orderId);
  check(JSON.stringify(s.picked)===JSON.stringify(expectedPicked));check(JSON.stringify(s.arrivals)===JSON.stringify(completed.filter(t=>t.kind==='dropoff').map(t=>({id:t.orderId,token:'arrival:'+s.tripId+':'+s.stops.indexOf(t)+':'+t.orderId}))));
  route.state={...copy(s),version:2,timeProfile:'road40-service2-1-grouped-v2',stopPolicy:'legacy-sequential',stops:s.stops.map(stop=>({orderId:stop.orderId,orderIds:[stop.orderId],kind:stop.kind,node:stop.node})),serviceCharged:s.serviceCharged!};
  return route;
 }
 static restore(city:CityData,raw:string):V2RouteSession {
  const parsed=JSON.parse(raw);if(parsed?.version===1)return V2RouteSession.restoreLegacy(city,parsed);
  const route=new V2RouteSession(city),s:V2RouteSnapshot=parsed;
  check(s&&s.format==='county-v2-route'&&(s.version===2||s.version===3)&&s.timeProfile==='road40-service2-1-grouped-v2'&&s.mapKey===route.state.mapKey&&['legacy-sequential','grouped'].includes(s.stopPolicy));
  if(s.version===3)check(Object.prototype.propertyIsEnumerable.call(s,'loadProfile')&&s.loadProfile==='slots-v1'&&Object.prototype.propertyIsEnumerable.call(s,'sourceNextId')&&typeof s.sourceNextId==='number'&&Number.isSafeInteger(s.sourceNextId)&&s.sourceNextId>0&&s.stopPolicy==='grouped');
  else check(!('loadProfile' in s)&&!('sourceNextId' in s));
  check(Number.isSafeInteger(s.nextId)&&s.nextId>0&&Number.isSafeInteger(s.tripId)&&s.tripId>=0&&Array.isArray(s.orders)&&s.orders.every(o=>route.legal(o,s.version))&&new Set(s.orders.map(o=>o.id)).size===s.orders.length);
  if(s.version===3){check(s.phase==='idle'?s.sourceNextId===s.nextId:s.nextId===s.sourceNextId!+s.orders.length+8);check(s.orders.every(o=>{const ordinal=Number(o.sourceOfferId!.slice(8));return ordinal>=s.sourceNextId!&&ordinal-s.sourceNextId!<route.places.length*2;}));}
  const validateAnchor=(a:Anchor)=>{check(a&&route.router.nodes.has(a.node)&&nonnegative(a.elapsed));if(a.edge){check(route.roadEdges.some(e=>e.from===a.edge!.from&&e.to===a.edge!.to&&e.road===a.edge!.road&&e.metres===a.edge!.metres&&e.seconds===a.edge!.seconds&&e.roughness===a.edge!.roughness)&&a.node===a.edge.from&&a.elapsed<a.edge.seconds);}else check(a.elapsed===0);};validateAnchor(s.anchor);validateAnchor(s.origin);
  check(['idle','planned','travelling','pickup','service','ready','finished'].includes(s.phase)&&['fast','main','smooth'].includes(s.preference)&&Number.isSafeInteger(s.cursor)&&s.cursor>=0&&nonnegative(s.legSeconds)&&nonnegative(s.serviceSeconds)&&s.serviceSeconds<2);
  check(Array.isArray(s.stops)&&Array.isArray(s.legs)&&Array.isArray(s.picked)&&Array.isArray(s.arrivals));
  // Canonical policy comparison proves exact membership, pickup-before-dropoff,
  // singleton dropoffs, stable ordering and authoritative identity of every group.
  const expectedStops=route.plannedStops(s.orders,s.stopPolicy);
  check(s.stops.length===expectedStops.length&&s.stops.every((stop,i)=>{const expected=expectedStops[i];return !!stop&&stop.orderId===expected.orderId&&stop.kind===expected.kind&&stop.node===expected.node&&JSON.stringify(stop.orderIds)===JSON.stringify(expected.orderIds);}));
  check(s.cursor<=s.stops.length&&typeof s.serviceCharged==='boolean'&&(!s.serviceCharged||s.phase==='service')&&(s.phase!=='service'||s.serviceSeconds===0||s.serviceCharged));
  const atNode=(node:string)=>s.anchor.node===node&&s.anchor.edge===null&&s.anchor.elapsed===0;
  if(s.phase==='idle'||s.phase==='planned'){
   check(s.legs.length===0&&s.cursor===0&&s.legSeconds===0&&s.serviceSeconds===0&&JSON.stringify(s.anchor)===JSON.stringify(s.origin));
   if(s.phase==='idle')check(s.orders.length===0);else {check(s.orders.length>0);route.makeLegs('fast',s.origin,s.stops);}
  }else {
   // Always serialize the complete input legs, even on a cache hit.
   check(s.orders.length>0&&s.tripId>0&&JSON.stringify(s.legs)===route.expectedLegsJSON(s.preference,s.origin,s.stops));
   check(s.phase==='finished'?s.cursor===s.stops.length:s.cursor<s.stops.length);
   if(s.phase==='finished')check(s.legSeconds===0&&s.serviceSeconds===0&&atNode(s.stops[s.cursor-1].node));
   else if(s.phase==='ready')check(s.cursor>0&&s.stops[s.cursor-1].kind==='pickup'&&atNode(s.stops[s.cursor-1].node)&&s.legSeconds===0&&s.serviceSeconds===0&&!s.serviceCharged);
   else {
    check(s.legSeconds<=s.legs[s.cursor].seconds);
    if(s.phase==='travelling'){
     check(s.serviceSeconds===0);
     check(s.cursor===0?JSON.stringify(s.anchor)===JSON.stringify(s.origin)&&s.legSeconds>=s.origin.elapsed:atNode(s.stops[s.cursor-1].node));
    }else {
     check(s.legSeconds===s.legs[s.cursor].seconds&&atNode(s.stops[s.cursor].node)&&s.serviceSeconds<(s.stops[s.cursor].kind==='pickup'?2:1));
     if(s.phase==='pickup')check(s.stops[s.cursor].kind==='pickup'&&s.serviceSeconds===0);
    }
   }
  }
  const completed=s.stops.slice(0,s.cursor),expectedPicked=completed.filter(t=>t.kind==='pickup').flatMap(t=>t.orderIds);
  if(s.phase==='service'&&s.stops[s.cursor]?.kind==='pickup')expectedPicked.push(...s.stops[s.cursor].orderIds);
  check(JSON.stringify(s.picked)===JSON.stringify(expectedPicked));
  check(JSON.stringify(s.arrivals)===JSON.stringify(completed.flatMap((stop,index)=>stop.kind==='dropoff'?[{id:stop.orderId,token:'arrival:'+s.tripId+':'+index+':'+stop.orderId}]:[])));
  route.state=copy(s);
  return route;
 }
}
