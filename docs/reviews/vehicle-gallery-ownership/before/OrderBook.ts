import { TRIP_PROFILE, TripProfile, tripTiming, travelDelta } from './TripClock';
import { CityData, MapRoute, Point, Preference } from './MapTypes';
import { RoadRouter, routePosition } from './RoadRouter';
import { advancePickupClock, DeliveryProgress, DeliveryTiming, deliveryProgress, deliveryTiming, legacyDeliveryTiming, PICKUP_STOP_SECONDS } from './DeliveryClock';
import { Damage, Player } from '../domain/GameConfig';
import { CountyReceipt, CountyTerms, countyDamageChance, countySettlement, legacyCountySettlement, estimateCountyIncome, newCountyPlayer } from './CountyRules';
import { COUNTY_VEHICLES, countyExperienceLevel } from './CountyConfig';
import { countyMapId, validateCountySnapshot } from './CountySnapshot';
import { contains } from './CityExtent';
import { FOOD_CATALOG, foodForOffer, selectFoodForOffer } from './FoodCatalog';
import { DispatchArea, dispatchAreaForTrip } from './DispatchAreas';
import { RiderAnchor, anchorAt, anchorExits, routeFromAnchor } from './RiderAnchor';
import { HandoffPhase, HandoffState, advanceHandoff, beginTrip, startPickup, startDelivery } from './ManualHandoff';
import { newOfferSource } from './OrderPresentation';
import { BillingSnapshot, BillingView, DeliveryLedger } from './DeliveryLedger';

export interface DeliveryOffer extends CountyTerms { from:number; to:number; food:string; tag:string; weightKg:number; source?:'direct'|'transfer'; quantity?:number; buyerNote?:string }
export interface OfferPreview {
  offer:DeliveryOffer; available:boolean; pickupMetres:number; deliveryMetres:number; timing:DeliveryTiming; deadlineSeconds:number; estimatedIncomeCents:number;
}
export interface AcceptedDelivery {
  offer:DeliveryOffer; routes:MapRoute[]; selected:number; elapsed:number; ruleVersion?:1|2; pickupWaitElapsed?:number;
  mode:'routes'|'running'|'paused'|'arrived'|'done';
  handoff?:{version:1;phase:HandoffPhase};
  tripProfile?:TripProfile;
  mileage?:{profile:'road-increment-v1';accountedMetres:number};
  damageNoticeShown?:boolean;
  deadlineSeconds:number; damage:Damage|null; playerBefore:Player; receipt:CountyReceipt|null;
}
export interface CountySnapshot {
  version:1|2|3|4|5|6;randomState?:number;riderAnchor?:RiderAnchor|null;mapId:string;player:Player;offers:DeliveryOffer[];currentNode:string;sequence:number;
  recent:number[];lobbyHistory?:number[];billing?:BillingSnapshot;tutorialComplete:boolean;daily:{day:string;used:number};active:AcceptedDelivery|null;
}
function localDay():string{const d=new Date();return `${d.getFullYear()}-${d.getMonth()+1}-${d.getDate()}`;}
const LOBBY_SIZE=10,MAX_TRIP_METRES=10000;

export class OrderBook {
  private readonly router:RoadRouter;
  private readonly cityRouter:RoadRouter;
  private readonly operatingNodes:Set<string>|null;
  private migrating=false;
  private migrationRoll=0;
  private readonly offers:DeliveryOffer[]=[];
  private readonly cache=new Map<string,MapRoute|null>();
  private accepted:AcceptedDelivery|null=null;
  private currentNode:string;
  private riderAnchor:RiderAnchor|null=null;
  private snapshotVersion:3|4|5=5;
  private randomState=1;
  private sequence=1;
  private playerState:Player=newCountyPlayer();
  private tutorialComplete=false;
  private daily:{day:string;used:number};
  private readonly mapId:string;
  private recent:number[]=[];
  private lobbyHistory:number[]=[];
  private readonly ledger:DeliveryLedger;

  constructor(readonly data:CityData,private readonly random:()=>number=Math.random,private readonly today:()=>string=localDay,saved?:CountySnapshot) {
    this.randomState=saved?.randomState??(Math.floor(this.random()*4294967296)>>>0);
    this.router=new RoadRouter(data);
    this.cityRouter=data.playBounds?new RoadRouter({...data,nodes:data.nodes.filter(n=>contains(data.playBounds!,[n.x,n.y]))}):this.router;
    this.operatingNodes=data.operatingPOIs?new Set(data.operatingPOIs.map(i=>data.pois[i].node)):null;
    this.mapId=countyMapId(data);this.daily={day:today(),used:0};
    this.ledger=new DeliveryLedger(saved?.billing,saved?saved.player.completedOrders:0,today(),!!saved);
    const start=data.pois.find(p=>p.kind==='restaurant');
    if(!start)throw new Error('No restaurant in the delivery map');
    this.currentNode=start.node;
    if(saved){
      this.snapshotVersion=5;this.riderAnchor=saved.version>=4?(saved.riderAnchor||null):null;
      this.playerState=saved.player;this.offers=saved.offers;this.currentNode=saved.currentNode;
      this.sequence=saved.sequence;this.recent=saved.recent;this.lobbyHistory=saved.lobbyHistory||[];this.tutorialComplete=saved.tutorialComplete;this.daily=saved.daily;this.accepted=saved.active;
      if(saved.version<3&&this.accepted)this.accepted.ruleVersion=1;
      this.playerState={...this.playerState,level:countyExperienceLevel(this.playerState.experience)};
      if(this.accepted&&this.accepted.mode==='paused')this.accepted.mode='running';
      if(saved.version===1||saved.mapId!==this.mapId){
        // Replacement candidates are deterministic; migration never redraws activity or consumes the caller's RNG.
        this.migrating=true;
        const migrated=this.nearbyOffers(this.offers,this.accepted&&this.accepted.mode!=='done'?this.accepted.offer:null);
        this.offers.splice(0,this.offers.length,...migrated);this.migrating=false;
      }
      return;
    }
    this.offers.push(...this.nearbyOffers([]));
  }
  static restore(data:CityData,serialized:string,random:()=>number=Math.random,today:()=>string=localDay):OrderBook {
    let saved:unknown;try{saved=JSON.parse(serialized);}catch{throw new Error('存档内容无法读取');}
    validateCountySnapshot(data,saved);return new OrderBook(data,random,today,saved);
  }
  serialize():string {
    const snapshot:CountySnapshot={version:6,randomState:this.randomState,...(this.snapshotVersion>=4?{riderAnchor:this.riderAnchor}:{}),mapId:this.mapId,player:this.playerState,offers:this.offers,currentNode:this.currentNode,sequence:this.sequence,recent:this.recent,lobbyHistory:this.lobbyHistory,billing:this.ledger.snapshot(),tutorialComplete:this.tutorialComplete,daily:this.daily,active:this.accepted};
    return JSON.stringify(snapshot);
  }
  get player():Readonly<Player>{return {...this.playerState};}
  get isFirstDelivery():boolean{return !this.tutorialComplete;}
  get refreshesLeft():number{return this.daily.day===this.today()?2-this.daily.used:2;}
  get active():Readonly<AcceptedDelivery>|null{return this.accepted;}
  get riderNode():string{return this.currentNode;}
  get completed():number{return this.playerState.completedOrders;}
  get billing():BillingView{return this.ledger.view(this.today(),this.playerState.cashCents,this.playerState.completedOrders);}
  recordOnlineTime(start:number,end:number):void{this.ledger.recordOnlineTime(start,end);}
  get mode():'idle'|AcceptedDelivery['mode']{return this.accepted?this.accepted.mode:'idle';}
  get tripStage():'pickup'|'collecting'|'delivery'|null {
    if(!this.accepted)return null;
    const phase=this.accepted.handoff?.phase;if(phase)return phase==='picking'?'collecting':phase==='toDropoff'||phase==='arrived'?'delivery':'pickup';
    if(this.accepted.mode==='running'&&this.accepted.pickupWaitElapsed!==undefined&&this.accepted.pickupWaitElapsed<PICKUP_STOP_SECONDS&&this.accepted.elapsed>=this.pickupAt()-1e-9)return 'collecting';
    const route=this.accepted.routes[this.accepted.selected];
    const legacy=this.accepted.ruleVersion===1;
    const pickup=route.segments.slice(0,route.pickupIndex||0).reduce((sum,s)=>sum+(legacy?s.seconds:s.metres),0);
    return (legacy?this.progress.routeElapsedSeconds:this.progress.routeElapsedMetres)<pickup?'pickup':'delivery';
  }
  get pickupWaitRemaining():number{return this.tripStage==='collecting'?PICKUP_STOP_SECONDS-this.accepted!.pickupWaitElapsed!:0;}
  takeDamageNotice():boolean {
    const active=this.accepted;
    if(!active||active.mode!=='running'||!active.damage||active.damage==='none'||active.damageNoticeShown||this.tripStage!=='delivery')return false;
    const route=active.routes[active.selected];
    const pickup=(route.origin?.exit.metres||0)+route.segments.slice(0,route.pickupIndex||0).reduce((sum,s)=>sum+s.metres,0);
    let travelled=this.progress.routeElapsedMetres;
    if(active.ruleVersion===1){
      // Historic animation follows road seconds; segment speeds can differ greatly.
      let remaining=this.progress.routeElapsedSeconds;travelled=0;
      for(const segment of route.segments){
        const used=Math.min(remaining,segment.seconds);travelled+=segment.metres*used/segment.seconds;remaining-=used;
        if(remaining<=0)break;
      }
    }
    if(travelled<(pickup+route.metres)/2)return false;
    active.damageNoticeShown=true;return true;
  }
  private pickupAt():number {
    const active=this.accepted!,route=active.routes[active.selected];
    const metres=(route.origin?.exit.metres||0)+route.segments.slice(0,route.pickupIndex||0).reduce((n,s)=>n+s.metres,0);
    return this.progress.animationSeconds*metres/route.metres;
  }
  get progress():DeliveryProgress {
    if(!this.accepted)return {displaySeconds:0,animationSeconds:0,progress:0,routeElapsedSeconds:0,routeElapsedMetres:0,remainingSeconds:0};
    const active=this.accepted,route=active.routes[active.selected],vehicle=COUNTY_VEHICLES[active.playerBefore.vehicleTier-1];
    if(active.ruleVersion===1){
      const timing=legacyDeliveryTiming(route.seconds,vehicle.speedMultiplier),progress=Math.max(0,Math.min(1,active.elapsed/timing.animationSeconds));
      return {...timing,progress,routeElapsedSeconds:route.seconds*progress,routeElapsedMetres:route.metres*progress,remainingSeconds:timing.displaySeconds*(1-progress)};
    }
    const timing=active.tripProfile?tripTiming(route.metres,vehicle.speedKph,active.tripProfile):deliveryTiming(route.metres,vehicle.speedKph);
    const fraction=timing.animationSeconds===0?1:Math.max(0,Math.min(1,active.elapsed/timing.animationSeconds));
    const progress:DeliveryProgress={...timing,progress:fraction,routeElapsedSeconds:0,routeElapsedMetres:route.metres*fraction,remainingSeconds:active.tripProfile?(timing.displaySeconds-60)*(1-fraction)+60*(1-(active.pickupWaitElapsed||0)/2):timing.displaySeconds*(1-fraction)};
    // Keep routeElapsedSeconds meaningful for callers using the router's road-time parameter.
    return {...progress,routeElapsedSeconds:this.roadSecondsAtDistance(route,progress.routeElapsedMetres)};
  }
  get riderPose():{point:Point;angle:number} {
    if(this.accepted){const r=this.accepted.routes[this.accepted.selected];return routePosition(r,this.progress.routeElapsedSeconds);}
    if(this.riderAnchor)return {point:anchorExits(this.data,this.riderAnchor).point,angle:0};
    const n=this.router.nodes.get(this.currentNode)!;return {point:[n.x,n.y],angle:0};
  }
  list():OfferPreview[] {
    return this.offers.map(offer=>{
      const bounded=this.riderInsideCity()&&this.insideCity(this.data.pois[offer.from].node)&&this.insideCity(this.data.pois[offer.to].node);
      const route=this.deliveryRoute(offer,'fast',bounded),estimatedIncomeCents=estimateCountyIncome(this.playerState,offer.feeCents);
      if(!route)return {offer,available:false,pickupMetres:0,deliveryMetres:0,timing:{displaySeconds:0,animationSeconds:0},deadlineSeconds:0,estimatedIncomeCents};
      const pickupMetres=(route.origin?.exit.metres||0)+route.segments.slice(0,route.pickupIndex||0).reduce((sum,segment)=>sum+segment.metres,0),deliveryMetres=route.metres-pickupMetres,timing=this.timing(route.metres);
      let deadlineSeconds=this.accepted?.offer.id===offer.id?this.accepted.deadlineSeconds:0,available=true;
      if(!deadlineSeconds){try{deadlineSeconds=Math.min(...this.legalRoutes(offer).map(r=>this.timing(r.metres).displaySeconds))+(offer.type==='urgent'?120:300);}catch(_){available=false;}}
      return {offer,available,pickupMetres,deliveryMetres,timing,deadlineSeconds,estimatedIncomeCents};
    });
  }
  accept(id:string):void {
    if(this.accepted)throw new Error('Already carrying an order');
    const offer=this.offers.find(o=>o.id===id);
    if(!offer)throw new Error('Unknown order');
    if(offer.weightKg>COUNTY_VEHICLES[this.playerState.vehicleTier-1].capacityKg)throw new Error('这单超出当前车辆载重');
    const routes=this.legalRoutes(offer);
    const fastest=Math.min(...routes.map(r=>this.timing(r.metres).displaySeconds));
    this.snapshotVersion=5;this.accepted={offer,routes,ruleVersion:2,tripProfile:TRIP_PROFILE,mileage:{profile:'road-increment-v1',accountedMetres:0},handoff:{version:1,phase:'planning'},pickupWaitElapsed:0,selected:0,elapsed:0,mode:'routes',deadlineSeconds:fastest+(offer.type==='urgent'?120:300),damage:null,playerBefore:{...this.playerState},receipt:null};
  }
  private legalRoutes(offer:DeliveryOffer):MapRoute[] {
    const routes:MapRoute[]=[],seen=new Set<string>();
    for(const preference of ['fast','main','smooth'] as Preference[]){
      const route=this.normalRoute(offer,preference);
      if(!route||route.metres>MAX_TRIP_METRES)continue;
      if(this.localDispatch&&this.timing(route.metres).displaySeconds>1800)continue;
      const key=JSON.stringify(route.points);if(seen.has(key))continue;seen.add(key);routes.push(route);
    }
    if(!routes.length)throw new Error('No legal delivery route');
    return routes;
  }
  select(index:number):void {
    if(!this.accepted||this.accepted.mode!=='routes'||!this.accepted.routes[index])return;
    this.accepted.selected=index;
  }
  cancel():void {
    const active=this.accepted;if(!active)return;
    const phase=active.handoff?.phase;
    if(phase&&phase!=='planning'&&phase!=='toPickup'&&phase!=='awaitPickup')throw new Error('取餐开始后不能取消');
    if(!phase&&active.mode!=='routes'){
      const route=active.routes[active.selected],pickup=route.segments.slice(0,route.pickupIndex||0).reduce((sum,segment)=>sum+segment.seconds,0);
      if(active.mode!=='running'||this.progress.routeElapsedSeconds>=pickup)throw new Error('取餐开始后不能取消');
      if(active.elapsed>0){this.riderAnchor=anchorAt(route,this.progress.routeElapsedSeconds);this.currentNode=this.riderAnchor.from;this.snapshotVersion=5;}
    }
    if(phase==='awaitPickup'){this.currentNode=this.data.pois[active.offer.from].node;this.riderAnchor=null;}
    else if(phase==='toPickup'&&active.elapsed>0){this.riderAnchor=anchorAt(active.routes[active.selected],this.progress.routeElapsedSeconds);this.currentNode=this.riderAnchor.from;}
    this.accepted=null;
  }
  /** Post-pickup abandonment is distinct from the original pre-pickup cancel. */
  get canCancelDelivery():boolean {
    const active=this.accepted;if(!active||active.mode!=='running')return false;
    const phase=active.handoff?.phase;
    return phase?phase==='awaitDeliveryStart'||phase==='toDropoff':this.tripStage==='delivery';
  }
  cancelDelivery():void {
    if(!this.canCancelDelivery)throw new Error('当前阶段不能取消配送');
    const active=this.accepted!,anchor=anchorAt(active.routes[active.selected],this.progress.routeElapsedSeconds);
    // Resolve first: malformed routes must not partially clear the activity.
    anchorExits(this.data,anchor);
    this.riderAnchor=anchor;this.currentNode=anchor.from;this.snapshotVersion=5;
    this.accepted=null;
    // Preserve player, ledger, candidate pool, RNG and refresh quota byte-for-byte.
  }
  private handoffState():HandoffState {
    const a=this.accepted!;return {version:1,phase:a.handoff!.phase,elapsed:a.elapsed,serviceElapsed:a.pickupWaitElapsed||0};
  }
  private applyHandoff(next:HandoffState):void {
    const a=this.accepted!;a.handoff={version:1,phase:next.phase};a.elapsed=next.elapsed;a.pickupWaitElapsed=next.serviceElapsed;
  }
  depart():void{
    if(!this.accepted||this.accepted.mode!=='routes')return;
    const chance=this.accepted.routes[this.accepted.selected].risk;
    let damage:Damage='none';if(this.roll()<chance){const severity=this.roll();damage=severity<.7?'minor':severity<.95?'moderate':'severe';}
    this.accepted.damage=damage;this.accepted.mode='running';
    if(this.accepted.handoff)this.applyHandoff(beginTrip(this.handoffState(),this.pickupAt()));
  }
  pickup():void {if(!this.accepted?.handoff)throw new Error('当前订单无需手动取餐');this.applyHandoff(startPickup(this.handoffState()));}
  deliver():void {if(!this.accepted?.handoff)throw new Error('当前订单无需手动送餐');this.applyHandoff(startDelivery(this.handoffState()));}
  // Kept for old view integrations; deliveries no longer support manual pausing.
  togglePause():void {}
  advance(seconds:number,multiplier=1,day=this.today()):boolean {
    const active=this.accepted;
    if(!active||active.mode!=='running'||!Number.isFinite(seconds)||seconds<=0)return false;
    if(active.handoff){
      const next=advanceHandoff(this.handoffState(),active.tripProfile&&active.handoff.phase!=='picking'?travelDelta(seconds,multiplier):seconds,this.pickupAt(),this.progress.animationSeconds),changed=next.phase!==active.handoff.phase;this.applyHandoff(next);
      if(active.mileage){const route=active.routes[active.selected],distance=Math.min(route.metres,route.metres*active.elapsed/this.progress.animationSeconds),delta=Math.max(0,distance-active.mileage.accountedMetres);this.ledger.recordDistance(delta,day);active.mileage.accountedMetres=distance;}
      if(next.phase==='arrived'){active.mode='arrived';this.currentNode=this.data.pois[active.offer.to].node;this.riderAnchor=null;this.settle(active.offer.demand==='door'?true:null,day);}
      return changed;
    }
    if(active.pickupWaitElapsed===undefined)active.elapsed=Math.min(this.progress.animationSeconds,active.elapsed+seconds);
    else{
      const next=advancePickupClock(active.elapsed,active.pickupWaitElapsed,seconds,this.pickupAt(),this.progress.animationSeconds);
      active.elapsed=next.elapsed;active.pickupWaitElapsed=next.pickupWaitElapsed;
    }
    if(this.progress.progress<1)return false;
    active.mode='arrived';this.currentNode=this.data.pois[active.offer.to].node;
    this.riderAnchor=null;this.settle(active.offer.demand==='door'?true:null,day);
    return true;
  }
  settle(doorAnswer:boolean|null=null,day=this.today()):CountyReceipt {
    const active=this.accepted;if(!active)throw new Error('没有待结算订单');
    if(active.mode==='done')return JSON.parse(JSON.stringify(active.receipt));
    if(active.mode!=='arrived')throw new Error('尚未送达，不能结算');
    const result=(active.ruleVersion===1?legacyCountySettlement:countySettlement)(active.playerBefore,active.offer,{displaySeconds:this.progress.displaySeconds,deadlineSeconds:active.deadlineSeconds,damage:active.damage!,doorAnswer});
    const refill=this.nearbyOffers(this.offers.filter(o=>o.id!==active.offer.id));
    this.ledger.recordDelivery(result.receipt,active.mileage?0:active.routes[active.selected].metres,day);
    this.playerState={...result.player,level:countyExperienceLevel(result.player.experience)};active.receipt=result.receipt;active.mode='done';this.tutorialComplete=true;
    this.recent.push(active.offer.to);if(this.recent.length>20)this.recent.shift();
    this.offers.splice(0,this.offers.length,...refill);
    return JSON.parse(JSON.stringify(result.receipt));
  }
  finish():void{if(this.accepted&&this.accepted.mode==='done')this.accepted=null;}
  timing(distanceMetres:number):DeliveryTiming{return tripTiming(distanceMetres,COUNTY_VEHICLES[this.playerState.vehicleTier-1].speedKph);}
  timingForRoute(route:MapRoute):DeliveryTiming {
    if(this.accepted&&this.accepted.ruleVersion===1&&this.accepted.routes.indexOf(route)>=0)return legacyDeliveryTiming(route.seconds,COUNTY_VEHICLES[this.accepted.playerBefore.vehicleTier-1].speedMultiplier);
    if(this.accepted&&this.accepted.routes.indexOf(route)>=0&&!this.accepted.tripProfile)return deliveryTiming(route.metres,COUNTY_VEHICLES[this.accepted.playerBefore.vehicleTier-1].speedKph);
    if(this.accepted?.tripProfile&&this.accepted.routes.indexOf(route)>=0)return tripTiming(route.metres,COUNTY_VEHICLES[this.accepted.playerBefore.vehicleTier-1].speedKph,this.accepted.tripProfile);
    return this.timing(route.metres);
  }
  private roadSecondsAtDistance(route:MapRoute,distance:number):number {
    let remaining=distance,seconds=0;
    if(route.origin){const prefix=route.origin.exit;if(remaining<=prefix.metres)return prefix.metres?prefix.seconds*Math.max(0,remaining)/prefix.metres:0;remaining-=prefix.metres;seconds+=prefix.seconds;}
    for(const segment of route.segments){
      if(remaining<=segment.metres)return seconds+segment.seconds*Math.max(0,remaining)/segment.metres;
      remaining-=segment.metres;seconds+=segment.seconds;
    }
    return route.seconds;
  }
  upgradeVehicle():void {
    if(this.accepted)throw new Error('请先完成当前订单，再升级车辆');
    if(this.playerState.vehicleTier>=2)throw new Error('县城当前站点最高为D+');
    const fee=COUNTY_VEHICLES[1].upgradeFeeCents;
    if(this.playerState.cashCents<fee)throw new Error(`余额不足，还差¥${((fee-this.playerState.cashCents)/100).toFixed(2)}`);
    this.playerState={...this.playerState,cashCents:this.playerState.cashCents-fee,vehicleTier:2};
  }
  refreshFree():void {
    if(this.accepted)throw new Error('请先完成当前订单');
    if(this.daily.day!==this.today())this.daily={day:this.today(),used:0};
    if(this.daily.used>=2)throw new Error('今日免费刷新已用完；广告刷新暂未开放，现有订单仍可接取');
    const history=this.lobbyHistory.concat(this.offers.map(o=>o.to)).slice(-20);
    const refreshed=this.nearbyOffers([],null,history);this.offers.splice(0,this.offers.length,...refreshed);this.lobbyHistory=history;
    this.daily.used++;
  }
  private roll():number{const value=this.migrating?((Math.imul(this.sequence+ ++this.migrationRoll,1664525)+1013904223)>>>0)/4294967296:((this.randomState=(Math.imul(this.randomState,1664525)+1013904223)>>>0)/4294967296);return Number.isFinite(value)?Math.max(0,Math.min(1-Number.EPSILON,value)):.99;}
  private path(from:string,to:string,preference:Preference,bounded=false):MapRoute|null {
    const key=`${bounded?'city':'full'}/${from}/${to}/${preference}`;
    if(!this.cache.has(key)){if(this.cache.size>400)this.cache.clear();this.cache.set(key,(bounded?this.cityRouter:this.router).find(from,to,preference));}
    return this.cache.get(key)!;
  }
  private pickupPath(to:string,preference:Preference,bounded=false):MapRoute|null {
    if(!this.riderAnchor)return this.path(this.currentNode,to,preference,bounded);
    const origin=routeFromAnchor(this.data,this.riderAnchor,to,preference,bounded?this.cityRouter:this.router);if(!origin)return null;
    return {...origin.tail,origin:{anchor:origin.anchor,start:origin.start,exit:origin.exit},metres:origin.metres,seconds:origin.seconds};
  }
  private deliveryRoute(offer:DeliveryOffer,preference:Preference,bounded=false):MapRoute|null {
    const pickup=this.pickupPath(this.data.pois[offer.from].node,preference,bounded);
    const delivery=this.path(this.data.pois[offer.from].node,this.data.pois[offer.to].node,preference,bounded);
    if(!pickup||!delivery)return null;
    const segments=[...pickup.segments,...delivery.segments];
    return {preference,nodes:[...pickup.nodes,...delivery.nodes.slice(1)],points:[...pickup.points,...delivery.points.slice(1)],segments,
      pickupIndex:pickup.nodes.length-1,...(pickup.origin?{origin:pickup.origin}:{}),metres:pickup.metres+delivery.metres,seconds:pickup.seconds+delivery.seconds,
      risk:countyDamageChance(preference,offer.fragility)};
  }
  private riderInsideCity():boolean {return !this.data.playBounds||contains(this.data.playBounds,this.riderPose.point);}
  private riderAtNode(id:string):boolean {return this.riderAnchor?this.riderAnchor.fraction===0&&this.riderAnchor.from===id||this.riderAnchor.fraction===1&&this.riderAnchor.to===id:this.currentNode===id;}
  private insideCity(node:string):boolean {
    const n=this.router.nodes.get(node)!;return !this.data.playBounds||contains(this.data.playBounds,[n.x,n.y]);
  }
  private get localDispatch():boolean{return !!this.data.dispatchBounds&&this.riderInsideCity();}
  private insideOperating(node:string):boolean {
    const n=this.router.nodes.get(node)!;return (!this.operatingNodes||this.operatingNodes.has(node))&&(this.data.dispatchBounds?contains(this.data.dispatchBounds,[n.x,n.y]):this.insideCity(node));
  }
  private normalRoute(offer:DeliveryOffer,preference:Preference):MapRoute|null {
    const inCity=this.riderInsideCity(),from=this.data.pois[offer.from].node,to=this.data.pois[offer.to].node;
    if(inCity&&(!this.insideCity(from)||!this.insideCity(to)))return null;
    return this.deliveryRoute(offer,preference,inCity);
  }
  private nearbyOffers(candidates:DeliveryOffer[],pending:DeliveryOffer|null=null,avoid:number[]=[]):DeliveryOffer[] {
    const next:DeliveryOffer[]=pending?[pending]:[];
    for(const offer of candidates){
      if(next.length>=LOBBY_SIZE)break;
      if(next.some(o=>o.id===offer.id)||offer.weightKg>COUNTY_VEHICLES[this.playerState.vehicleTier-1].capacityKg)continue;
      // Old ordinary outside endpoints migrate to city candidates; pending activity is kept above.
      if(!this.insideOperating(this.data.pois[offer.from].node)||!this.insideOperating(this.data.pois[offer.to].node))continue;
      const route=this.normalRoute(offer,'fast');
      if(!route||route.metres>MAX_TRIP_METRES)continue;
      if(this.localDispatch){
        const seconds=this.timing(route.metres).displaySeconds;
        if(seconds>1800||seconds>1200&&next.filter(o=>this.offerSeconds(o)>1200).length>=2)continue;
        if(this.data.dispatchAreas){
          const area=this.offerArea(offer),count=(kind:DispatchArea)=>next.filter(o=>this.offerArea(o)===kind).length;
          if(area!=='urban'&&next.filter(o=>this.offerArea(o)!=='urban').length>=5)continue;
          if(area==='suburb'&&count(area)>=3||area==='remote'&&count(area)>=2||area==='cross'&&count(area)>=1)continue;
        }
      }
      next.push(offer);
    }
    while(next.length<LOBBY_SIZE)next.push(this.createOffer(next,avoid));
    return next;
  }
  private createOffer(existing:DeliveryOffer[],avoid:number[]):DeliveryOffer {
    if(this.localDispatch)return this.createLocalOffer(existing,avoid);
    const point=(i:number)=>this.router.nodes.get(this.data.pois[i].node)!;
    const inCity=this.riderInsideCity(),used=new Set(existing.map(o=>o.to));
    const merchants=this.data.pois.map((p,i)=>({p,i})).filter(v=>v.p.kind==='restaurant'&&(!inCity||this.insideCity(v.p.node))).map(v=>v.i);
    const customers=this.data.pois.map((p,i)=>({p,i})).filter(v=>v.p.kind!=='restaurant'&&(!inCity||this.insideCity(v.p.node))).map(v=>v.i);
    const rotation=(this.sequence-1)%merchants.length;
    const merchantOrder=merchants.map((i,index)=>({i,cost:existing.filter(o=>o.from===i).length*1000000+(!this.insideCity(this.data.pois[i].node)?100000:0)+(index-rotation+merchants.length)%merchants.length})).sort((a,b)=>a.cost-b.cost).map(v=>v.i);
    const band=(this.sequence-1)%5;
    // Search all legal unique destinations before permitting repetition on small/disconnected fixtures.
    for(const repeat of [false,true])for(const from of merchantOrder){
      const pickup=this.pickupPath(this.data.pois[from].node,'fast',inCity);
      if(!pickup||pickup.metres>=MAX_TRIP_METRES)continue;
      const a=point(from),budget=MAX_TRIP_METRES-pickup.metres,target=Math.min([800,1800,3000,4500,6500][band],budget);
      const ranked=customers.filter(i=>(repeat||!used.has(i))&&this.data.pois[i].node!==this.data.pois[from].node&&Math.hypot(point(i).x-a.x,point(i).y-a.y)<=budget)
        .map(i=>({i,cost:(used.has(i)?1e9:0)+(!this.insideCity(this.data.pois[i].node)?1e8:0)+(avoid.indexOf(i)>=0?1e7:0)+(this.recent.indexOf(i)>=0||this.riderAtNode(this.data.pois[i].node)?1e6:0)+Math.abs(Math.hypot(point(i).x-a.x,point(i).y-a.y)-target)+this.roll()*target*.12})).sort((a,b)=>a.cost-b.cost);
      for(const candidate of ranked){
        const delivery=this.path(this.data.pois[from].node,this.data.pois[candidate.i].node,'fast',inCity);
        if(!delivery||delivery.metres===0||pickup.metres+delivery.metres>MAX_TRIP_METRES)continue;
        const first=this.sequence===1,food=first?FOOD_CATALOG[0]:selectFoodForOffer(this.roll(),this.roll(),existing.map(o=>foodForOffer(o.food).id));
        const type=first?'normal':this.roll()<.2?'urgent':'normal',demand=first?'none':this.roll()<.5?'door':'none';
        const quantity=first?1:1+Math.floor(this.roll()*3),weightKg=food.unitWeightKg*quantity;
        const feeCents=first?2000:1500+Math.floor(this.roll()*1001),fragility=food.fragility;
        return {id:`CC-${this.sequence++}`,from,to:candidate.i,food:`${food.name} · ${quantity}份`,tag:first?'首单推荐':type==='urgent'?'加急':fragility==='fragile'?'怕洒':fragility==='durable'?'耐放':'普通',feeCents,type,fragility,demand,weightKg,quantity,source:newOfferSource(`CC-${this.sequence-1}`),...(demand==='door'?{buyerNote:'放门口，别敲门'}:{})};
      }
    }
    throw new Error('当前位置10km内没有可达的取送路线，请检查地点池');
  }

  private offerSeconds(offer:DeliveryOffer):number {
    const route=this.normalRoute(offer,'fast');return route?this.timing(route.metres).displaySeconds:Infinity;
  }
  private offerArea(offer:DeliveryOffer):DispatchArea{return dispatchAreaForTrip(this.data,offer.from,offer.to,this.riderAnchor?this.riderPose.point:this.currentNode);}
  private createLocalOffer(existing:DeliveryOffer[],avoid:number[]):DeliveryOffer {
    const used=new Set(existing.map(o=>o.to)),point=(i:number)=>this.router.nodes.get(this.data.pois[i].node)!;
    const merchants=this.data.pois.map((p,i)=>({p,i})).filter(v=>v.p.kind==='restaurant'&&this.insideOperating(v.p.node))
      .map(v=>({i:v.i,pickup:this.pickupPath(v.p.node,'fast',true),variation:this.roll()*300})).filter(v=>v.pickup!==null)
      .sort((a,b)=>(a.pickup!.metres+existing.filter(o=>o.from===a.i).length*800+a.variation)-(b.pickup!.metres+existing.filter(o=>o.from===b.i).length*800+b.variation));
    const customers=this.data.pois.map((p,i)=>({p,i})).filter(v=>v.p.kind!=='restaurant'&&this.insideOperating(v.p.node)).map(v=>v.i);
    const long=existing.filter(o=>this.offerSeconds(o)>1200).length<2&&existing.filter(o=>this.offerSeconds(o)<=1200).length>=8;
    const count=(area:DispatchArea)=>existing.filter(o=>this.offerArea(o)===area).length;
    const wanted:DispatchArea=count('urban')<5?'urban':count('suburb')<3?'suburb':this.sequence%20===0&&count('cross')<1?'cross':count('remote')<2?'remote':'urban';
    const areas:DispatchArea[]=this.data.dispatchAreas?(wanted==='urban'?['urban']:[wanted,'urban']):['urban'];
    // Prefer 10–20 minute real-road trips. The last two slots may offer 20–30 minutes.
    for(const area of areas)for(const extended of long?[true,false]:[false])for(const fresh of avoid.length?[true,false]:[false])for(const repeat of [false,true])for(const {i:from,pickup} of merchants){
      const speed=COUNTY_VEHICLES[this.playerState.vehicleTier-1].speedKph/3.6,limit=(extended?1800:1200)*speed;
      if(pickup!.metres>=limit)continue;
      const phase=this.sequence-1+Math.floor((this.sequence-1)/10);
      const a=point(from),target=(extended?1500:[660,780,900,1020,1140][phase%5])*speed;
      const ranked=customers.filter(i=>(repeat||!used.has(i))&&(!fresh||avoid.indexOf(i)<0)&&this.data.pois[i].node!==this.data.pois[from].node&&(!this.data.dispatchAreas||dispatchAreaForTrip(this.data,from,i,this.riderAnchor?this.riderPose.point:this.currentNode)===area)&&Math.hypot(point(i).x-a.x,point(i).y-a.y)<=limit-pickup!.metres)
        .map(i=>({i,cost:(used.has(i)?1e9:0)+(avoid.indexOf(i)>=0?1e7:0)+(this.recent.indexOf(i)>=0||this.riderAtNode(this.data.pois[i].node)?1e6:0)+Math.abs(Math.hypot(point(i).x-a.x,point(i).y-a.y)+pickup!.metres-target)+this.roll()*80})).sort((a,b)=>a.cost-b.cost);
      let best:{i:number;cost:number}|null=null,checked=0;
      for(const candidate of ranked){
        const delivery=this.path(this.data.pois[from].node,this.data.pois[candidate.i].node,'fast',true);
        if(!delivery||delivery.metres===0)continue;
        const metres=pickup!.metres+delivery.metres;
        if(metres>limit||extended&&this.timing(metres).displaySeconds<=1200)continue;
        const seconds=this.timing(metres).displaySeconds;
        const cost=(used.has(candidate.i)?1e9:0)+(avoid.indexOf(candidate.i)>=0?1e7:0)+(this.recent.indexOf(candidate.i)>=0||this.riderAtNode(this.data.pois[candidate.i].node)?1e6:0)+(seconds<600?1e5:0)+Math.abs(metres-target);
        if(!best||cost<best.cost)best={i:candidate.i,cost};
        if(++checked>=12)break;
      }
      if(!best)continue;
      const first=this.sequence===1,food=first?FOOD_CATALOG[0]:selectFoodForOffer(this.roll(),this.roll(),existing.map(o=>foodForOffer(o.food).id));
      const type=first?'normal':this.roll()<.2?'urgent':'normal',demand=first?'none':this.roll()<.5?'door':'none';
      const quantity=first?1:1+Math.floor(this.roll()*3),weightKg=food.unitWeightKg*quantity,fragility=food.fragility;
      const feeCents=first?2000:1500+Math.floor(this.roll()*1001);
      return {id:`CC-${this.sequence++}`,from,to:best.i,food:`${food.name} · ${quantity}份`,tag:first?'首单推荐':type==='urgent'?'加急':fragility==='fragile'?'怕洒':fragility==='durable'?'耐放':'普通',feeCents,type,fragility,demand,weightKg,quantity,source:newOfferSource(`CC-${this.sequence-1}`),...(demand==='door'?{buyerNote:'放门口，别敲门'}:{})};
    }
    throw new Error('当前营业区内没有30分钟内可达的取送路线，请检查地点池');
  }
}
