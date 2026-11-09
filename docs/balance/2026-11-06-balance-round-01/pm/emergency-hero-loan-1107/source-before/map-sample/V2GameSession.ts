import { V2DispatchSession } from '../domain/V2DispatchSession';
import { quantizeOrdinaryDeliveryMetres,contractTerms } from '../domain/V2EconomySession';
import { V2_SLOT_PROFILE_ID } from '../domain/V2EconomyProfiles';
import { parseV2Load,slotCandidateRequestCount,fitsV2Capacity } from '../domain/V2LoadRules';
import type { V2Capacity } from '../domain/V2LoadRules';
import { V2TripRules, V2SupplyKind, V2AutoSupplyInput, V2FoodRiskContract, parseV2FoodRisk } from '../domain/V2TripRules';
import { V2_SUPPLY_CATALOG } from '../domain/V2SupplyCatalog';
import { CityData, Preference } from './MapTypes';
import { V2RouteOrder, V2RouteSession } from './V2RouteSession';
import { foodForV2Order } from './FoodCatalog';

export type V2FoodOffer=V2RouteOrder&{food:V2FoodRiskContract};
function validateCanonicalFood(orderId:string,raw:unknown):void {
 const food=parseV2FoodRisk(raw),canonical=foodForV2Order(orderId);
 if(food.version!==canonical.version||food.foodId!==canonical.foodId||food.fragility!==canonical.fragility)throw new Error('订单与配送食品身份不一致');
}

/** One durable candidate contains route, signed quotes, hero stamina/actions and outcomes. */
export class V2GameSession {
 route:V2RouteSession;
 dispatch:V2DispatchSession;
 private trip=new V2TripRules();
 constructor(private readonly city:CityData,nowSeconds=0){this.route=new V2RouteSession(city);this.route.enableSlots();this.dispatch=new V2DispatchSession({verifyArrival:(order,token)=>this.route.verifyArrival(order,token)},nowSeconds,'slots-v1');}
 serialize():string{const tripState=this.trip.state,route=this.route.snapshot();return JSON.stringify({format:'county-v2-game',version:6,profileId:V2_SLOT_PROFILE_ID,routeLoadProfile:route.version===3?'slots-v1':'kg-v1',route,dispatch:this.dispatch.snapshot(),tripState});}
 snapshot(){return this.dispatch.snapshot();}
 get tripState(){return this.trip.state;}
 get routeSnapshot(){return {...this.route.snapshot(),position:this.route.position};}
 get routeMotion(){return this.route.motion;}
 get nextBatchEffects(){const effects=this.dispatch.nextBatchEffects;if(!effects)throw new Error('主角未配车');return effects;}
 get deliveryEffects():{profileId:string;speedRelativeToStarter:number;incomeFactor:number;capacity:V2Capacity} {
  const effects=this.dispatch.deliveryEffects;if(!effects)throw new Error('主角未配车');return effects;
 }
 private get effects(){return this.deliveryEffects;}
 normalCandidates(count=8):V2FoodOffer[]{if(!this.dispatch.hasEquippedVehicle)return [];if(!Number.isSafeInteger(count)||count<1||count>50)throw new Error('候选读取数量无效');const capacity=this.nextBatchEffects.capacitySlots;return this.route.slotCandidates(capacity,this.dispatch.snapshot().orders.map(o=>o.id),slotCandidateRequestCount(capacity),this.dispatch.economyState.heroCompletedOrders<15?1000:Infinity).map(order=>({...order,food:foodForV2Order(order.id)}));}
 specialCandidate(id:string):V2FoodOffer|null {if(!this.dispatch.hasEquippedVehicle)return null;const order=this.route.slotSpecialCandidate(id,this.nextBatchEffects.capacitySlots,this.dispatch.snapshot().orders.map(o=>o.id),this.dispatch.economyState.heroCompletedOrders<15?1000:Infinity);return order?{...order,food:foodForV2Order(order.id)}:null;}
 acceptBatch(orders:V2RouteOrder[]){
  if(this.trip.state.action)throw new Error('补给动作进行中');
  const routeOrders=orders.map(o=>this.route.canonicalSlotOrder(o));
  const usedIds=new Set(this.dispatch.snapshot().orders.map(o=>o.id));if(routeOrders.some(o=>usedIds.has(o.id))||!fitsV2Capacity(routeOrders.map(o=>parseV2Load(o.load)),this.nextBatchEffects.capacity))throw new Error('订单已签约或超过整数容量');
  const candidate=V2RouteSession.restore(this.city,this.route.serialize());candidate.planSlots(routeOrders);
  const fastest=routeOrders.map(o=>this.route.fastest(o.pickupNode,o.dropoffNode));
  const ordinaryPricingById:Record<string,{deliveryMetres:number}>=Object.create(null);
  routeOrders.forEach((order,i)=>{if(order.kind==='ordinary')ordinaryPricingById[order.id]={deliveryMetres:fastest[i].heldMetres};});
  const safe=this.dispatch.economyState.heroCompletedOrders<15;
  if(safe&&(fastest.some(route=>route.metres>1000)||candidate.choices().every(c=>c.metres>1000*orders.length||c.metres/1000*[2,2,3,3,4][this.dispatch.economyState.selectedMapId-1]+candidate.serviceBudget.stamina>this.trip.state.stamina)))throw new Error('起步阶段请选择真实短途订单');
  const foodById:Record<string,V2FoodRiskContract>=Object.create(null);
  routeOrders.forEach((order,i)=>{
   const input=orders[i] as V2RouteOrder&{food?:unknown};
   if('food' in input){if(!Object.prototype.hasOwnProperty.call(input,'food'))throw new Error('配送食品身份必须显式提供');validateCanonicalFood(order.id,input.food);}
   foodById[order.id]=foodForV2Order(order.id);
  });
  const trip=V2TripRules.restore(this.trip.state);trip.begin(this.dispatch.economyState.selectedMapId,candidate.progress.tripId,routeOrders.map((o,i)=>({id:o.id,...fastest[i],fastestGameSeconds:fastest[i].gameSeconds,safe})),foodById);
  if(trip.state.version!==3)throw new Error('新配送批次缺少食品规则');
  const quotes=this.dispatch.acceptSlotBatch(routeOrders,ordinaryPricingById);this.route=candidate;this.trip=trip;return quotes;
 }
 /** Planned continuous travel/service only: no manual waits, supplies, future events or stamina stops. */
 routeChoices(){
  if(this.route.progress.phase!=='planned')return [];
  const t=this.trip.state,safe=t.orders.every(o=>o.safe),budget=this.route.serviceBudget;
  return this.route.choices().filter(c=>!safe||c.metres<=1000*t.orders.length&&c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina<=t.stamina).map(c=>{
   const arrivals=new Map(c.arrivals.map(a=>[a.id,a]));
   if(c.arrivals.length!==t.orders.length||arrivals.size!==t.orders.length||!t.orders.every(o=>arrivals.has(o.id)))throw new Error('路线与订单预计到达不一致');
   const roadTimeFactor=this.trip.roadTimeFactor,speed=this.effects.speedRelativeToStarter;
   const orders=t.orders.map(o=>{
    const arrival=arrivals.get(o.id)!;
    const etaRealSeconds=arrival.roadSeconds*roadTimeFactor/(40*speed)+arrival.serviceSeconds;
    const etaGameSeconds=arrival.roadSeconds*roadTimeFactor+arrival.serviceSeconds*30;
    return {id:o.id,deadlineGameSeconds:o.deadlineGameSeconds,etaRealSeconds,etaGameSeconds,lateGameSeconds:o.safe?0:Math.max(0,t.gameSeconds+etaGameSeconds-o.deadlineGameSeconds)};
   });
   return {...c,seconds:(c.seconds-budget.seconds)*roadTimeFactor/speed+budget.seconds,weather:t.weather,stamina:c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina,gameSeconds:t.gameSeconds,orders};
  });
 }
 beginTrip(preference:Preference='fast'){if(this.trip.state.action||!this.routeChoices().some(c=>c.aliases.includes(preference)))throw new Error('路线或当前动作不可出发');this.route.beginTrip(this.dispatch.snapshot(),preference);this.trip.choose(preference);}
 pickup(){if(this.trip.state.action)throw new Error('补给动作进行中');this.route.pickup();}
 continueTrip():void {if(this.trip.state.action)throw new Error('补给动作进行中');this.route.continueTrip();}
 private get highestSupplyMap(){return Math.max(...this.dispatch.economyState.ownedMapIds);}
 supplyOptions(){return V2_SUPPLY_CATALOG.map(item=>({...item,unlocked:item.unlockMapId<=this.highestSupplyMap,quantity:this.trip.state.inventory[item.id],actualRestore:Math.min(item.restore,100-this.trip.state.stamina)}));}
 supply(kind:V2SupplyKind,source:'purchase'|'inventory'='purchase'){
  const route=this.route.progress;if(route.phase==='service'&&route.serviceCharged)throw new Error('取送服务中不能重复开启动作');
  const nowSeconds=this.dispatch.snapshot().frame.nowSeconds;this.dispatch.advanceFleetTo(nowSeconds);
  this.dispatch.withLedgerTime(nowSeconds,()=>this.trip.startSupply(kind,this.dispatch.snapshot().batchIds.length>0,c=>this.dispatch.chargeSupply(c,{supplyId:kind,quantity:1}),false,source,this.highestSupplyMap));
 }
 configureAutoSupply(policy:V2AutoSupplyInput){this.trip.configureAutoSupply(policy);}
 claimSupplyReward(grantId:string,rewardId:string){return this.trip.claimSupplyReward(grantId,rewardId);}
 cancelDelivery(id:string){this.dispatch.cancelDelivery(id);this.route.cancel();this.trip.cancel();}
 completeDelivery(id:string,token:string,nowSeconds=this.dispatch.snapshot().frame.nowSeconds){
  const existing=this.dispatch.snapshot().orders.find(o=>o.id===id);if(existing?.status==='completed')return this.dispatch.completeDelivery(id,token,nowSeconds);
  const receipt=this.dispatch.completeDelivery(id,token,nowSeconds,this.trip.outcome(id));this.trip.delivered(id,receipt.ratingDelta||0);return receipt;
 }
 tick(sequence:number,nowSeconds:number,foreground:boolean,paused:boolean){
  const before=this.dispatch.tickContext;const tick=this.dispatch.tick(sequence,nowSeconds,foreground,paused,{deferAuto:true,deferFleet:true});
  const wallStart=before.nowSeconds,frameEnd=Math.max(wallStart,nowSeconds);
  const pendingAd=before.pendingAd;
  const active=sequence>before.sequence&&foreground&&!paused&&before.foreground&&!before.paused&&!before.clockNeedsRebase&&!pendingAd;
  // Automation expiry never silently drives the remaining interval manually.
  let seconds=before.control==='auto'?tick.autoRunSeconds:active?Math.max(0,nowSeconds-before.nowSeconds):0;
  const allowance=seconds;let used=0;const finish=()=>{this.dispatch.advanceFleetTo(frameEnd);used=Math.min(allowance,Math.max(0,used));if(before.control==='auto'&&used>0)this.dispatch.consumeAutomaticProgress(used);return {...tick,autoRunSeconds:before.control==='auto'?used:0,control:this.dispatch.controlMode};};
  if(seconds<=0)return finish();
  const automatic=before.control==='auto';
  // Spend this interval across action and batch boundaries. A stop consumes no tail time.
  while(seconds>0){
   const iterationStart=seconds;
   const afterSupply=this.trip.advanceSupply(seconds,this.route.progress.phase!=='planned');used+=seconds-afterSupply;seconds=afterSupply;
   if(seconds<=0)break;
   // Settle only work available at this action instant, never borrow frame-end NPC income.
   const actionAt=wallStart+used;this.dispatch.advanceFleetTo(actionAt);
   if(automatic&&!this.dispatch.hasEquippedVehicle)break;
   if(automatic&&this.trip.state.blocked&&!(this.route.progress.phase==='service'&&this.route.progress.serviceCharged)){
    const choice=this.trip.chooseAutoSupply(this.highestSupplyMap,this.dispatch.economyState.cashCents);
    if(!choice)break;
    this.dispatch.withLedgerTime(actionAt,()=>this.trip.startSupply(choice.kind,this.dispatch.snapshot().batchIds.length>0,c=>this.dispatch.chargeSupply(c,{supplyId:choice.kind,quantity:1}),true,choice.source,this.highestSupplyMap));
    // startSupply always creates a positive-duration action. Consume it next iteration.
    continue;
   }
   let phase=this.route.progress.phase;
   if(automatic&&['idle','finished'].includes(phase)&&this.dispatch.snapshot().batchIds.length===0){
    let capacity=this.nextBatchEffects.capacitySlots;const selected:V2RouteOrder[]=[];
    for(const offer of this.normalCandidates(8)){const load=parseV2Load(offer.load);if(load.version!=='slots-v1')throw new Error('自动配送缺少格子条款');if(load.occupiedSlots<=capacity){selected.push(offer);capacity-=load.occupiedSlots;}}
    // A combination may be long even when its individual offers are short.
    while(selected.length){try{this.acceptBatch(selected);break;}catch(error){if(this.dispatch.snapshot().batchIds.length)throw error;selected.pop();}}
    if(!selected.length)break;
    phase=this.route.progress.phase;
   }
   // Existing ordinary batches may have been planned before automatic control was granted.
   if(automatic&&phase==='planned'){
    const choice=this.routeChoices()[0];if(!choice)break;
    this.beginTrip(choice.preference);phase=this.route.progress.phase;
   }
   if(automatic&&phase==='ready'){this.continueTrip();phase=this.route.progress.phase;}
   if(!['travelling','pickup','service'].includes(phase))break;
   const offset=used;
   const advanced=this.route.advance(seconds,automatic,this.effects.speedRelativeToStarter,{roadTimeFactor:this.trip.roadTimeFactor,travel:(m,g)=>this.trip.travel(m,g),service:(id,kind)=>this.trip.service(id,kind),pickupGroup:ids=>this.trip.pickupGroup(ids),serviceTime:s=>this.trip.serviceTime(s),arrival:(id,token,elapsedSeconds)=>this.completeDelivery(id,token,wallStart+offset+elapsedSeconds)});
   used+=advanced;seconds=Math.max(0,seconds-advanced);
   if(!automatic||seconds>=iterationStart)break;
  }
  return finish();
 }
 static restore(city:CityData,raw:string,options:{preserveClock?:boolean}={}):V2GameSession {
  const s=JSON.parse(raw);if(!s||s.format!=='county-v2-game'||[1,2,3,4,5,6].indexOf(s.version)<0)throw new Error('V2组合路线存档不兼容，需显式迁移');
  // Old combinations cannot borrow the new grouping/ready acceptance gate.
  if(s.version===6){
   if(!Object.prototype.propertyIsEnumerable.call(s,'profileId')||s.profileId!==V2_SLOT_PROFILE_ID||!Object.prototype.propertyIsEnumerable.call(s,'routeLoadProfile')||!['kg-v1','slots-v1'].includes(s.routeLoadProfile)||s.route?.version!==(s.routeLoadProfile==='slots-v1'?3:2)||s.dispatch?.version!==2)throw new Error('组合与容量状态版本不一致');
  }else if(s.route?.version!==(s.version>=4?2:1)||s.dispatch?.version!==1)throw new Error('组合与路线状态版本不一致');
  const result=new V2GameSession(city);
  // All original combination checks run on the original structure, before Route
  // normalizes any legacy stop. Dispatch.restore is pure and does not invoke its port.
  result.dispatch=V2DispatchSession.restore(JSON.stringify(s.dispatch),{verifyArrival:(order,token)=>result.route.verifyArrival(order,token)},options);
  const r=s.route,d=result.dispatch.snapshot();result.route.assertDispatch(d,r);
  if(s.version===1){if(d.batchIds.length||!['idle','finished'].includes(r.phase))throw new Error('旧V2在途存档缺少体力行程，需显式迁移');}
  else {
   if(!s.tripState||(s.version===2&&s.tripState.version!==1)||(s.version>=3&&s.version<=4&&s.tripState.version!==2)||(s.version===5&&s.tripState.version!==3)||(s.version===6&&![2,3].includes(s.tripState.version))||(s.version===6&&s.routeLoadProfile==='slots-v1'&&r.orders.length>0&&s.tripState.version!==3))throw new Error('组合与补给状态版本不一致');
   result.trip=V2TripRules.restore(s.tripState);const t=result.trip.state;
   if(s.version===6&&t.version!==3&&t.orders.some((o:{id:string})=>{const q=d.orders.find(stored=>stored.id===o.id)?.quote;return q&&contractTerms(q).version==='slots-v1';}))throw new Error('格子合同不能降级食品规则');
   // Match the old v1 omitted-latch inference without modifying its source bytes.
   const charged=s.version<4&&r.serviceCharged===undefined?r.phase==='service'&&r.serviceSeconds>0:r.serviceCharged;
   // Restoration must enforce the same action exclusivity as supply() and auto supply.
   if(t.action&&r.phase==='service'&&charged)throw new Error('取送服务与补给动作不能同时进行');
   const pickup=r.phase==='service'&&r.stops[r.cursor]?.kind==='pickup'?r.stops[r.cursor]:null;
   if(r.phase!=='idle'&&(t.orders.length!==r.orders.length||!t.orders.every(o=>r.orders.some((ro:V2RouteOrder)=>ro.id===o.id)&&o.delivered===r.arrivals.some((a:{id:string})=>a.id===o.id)&&o.picked===(r.picked.includes(o.id)&&!(pickup&&(s.version>=4?pickup.orderIds.includes(o.id):pickup.orderId===o.id)&&!charged)))))throw new Error('行程与路线不一致');
   if(t.action?.kind==='rest'&&d.batchIds.length>0&&t.action.restore!==20)throw new Error('在途订单不能使用无单休息');
   if(t.action&&t.action.kind!=='rest'&&!result.supplyOptions().some(item=>item.id===t.action!.kind&&item.unlocked))throw new Error('补给开放状态不一致');
   if(t.orders.some(o=>o.delivered&&!d.orders.some(x=>x.id===o.id&&x.status==='completed')))throw new Error('补给或结算状态不一致');
   for(const order of t.orders){const quote=d.orders.find(stored=>stored.id===order.id)?.quote;if(quote&&'ordinaryPricing' in quote&&quantizeOrdinaryDeliveryMetres(order.heldMetres)!==quote.ordinaryPricing!.deliveryMetres)throw new Error('行程与普通计价路程不一致');}
  }
  // restoreLegacy first runs the complete original v1 route gate (including full
  // router-derived legs equality), then adds singleton membership without replanning.
  result.route=V2RouteSession.restore(city,JSON.stringify(s.route));
  if(s.version===1)result.route.cancel();
  if(s.version===5||s.version===6&&result.trip.state.version===3)for(const order of result.trip.state.orders)validateCanonicalFood(order.id,order.food);
  // The original dispatch/fleet/economy, trip, geometry and combination gates ran first.
  if(s.version<6)result.dispatch.enableSlots();
  return result;
 }
}
