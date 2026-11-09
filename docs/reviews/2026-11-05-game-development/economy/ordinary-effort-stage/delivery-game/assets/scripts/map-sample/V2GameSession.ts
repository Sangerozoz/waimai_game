import { V2DispatchSession } from '../domain/V2DispatchSession';
import { quantizeOrdinaryDeliveryMetres, vehicleEffects } from '../domain/V2EconomySession';
import { V2TripRules, V2SupplyKind, V2AutoSupplyInput } from '../domain/V2TripRules';
import { V2_SUPPLY_CATALOG } from '../domain/V2SupplyCatalog';
import { CityData, Preference } from './MapTypes';
import { V2RouteOrder, V2RouteSession } from './V2RouteSession';

/** One durable candidate contains route, signed quotes, hero stamina/actions and outcomes. */
export class V2GameSession {
 route:V2RouteSession;
 dispatch:V2DispatchSession;
 private trip=new V2TripRules();
 constructor(private readonly city:CityData,nowSeconds=0){this.route=new V2RouteSession(city);this.dispatch=new V2DispatchSession({verifyArrival:(order,token)=>this.route.verifyArrival(order,token)},nowSeconds);}
 serialize():string{return JSON.stringify({format:'county-v2-game',version:4,route:this.route.snapshot(),dispatch:this.dispatch.snapshot(),tripState:this.trip.state});}
 snapshot(){return this.dispatch.snapshot();}
 get tripState(){return this.trip.state;}
 get routeSnapshot(){return {...this.route.snapshot(),position:this.route.position};}
 get routeMotion(){return this.route.motion;}
 private get equippedVehicle(){const s=this.dispatch.economyState;return s.vehicles.find(v=>v.id===s.riders[0].vehicleId);}
 private get effects(){const v=this.equippedVehicle;if(!v)throw new Error('主角未配车');return vehicleEffects(v);}
 normalCandidates(count=8){if(!this.equippedVehicle)return [];return this.route.candidates(this.effects.capacityKg,this.dispatch.snapshot().orders.map(o=>o.id),count,this.dispatch.economyState.heroCompletedOrders<15?1000:Infinity);}
 specialCandidate(id:string){if(!this.equippedVehicle)return null;return this.route.specialCandidate(id,this.effects.capacityKg,this.dispatch.snapshot().orders.map(o=>o.id),this.dispatch.economyState.heroCompletedOrders<15?1000:Infinity);}
 acceptBatch(orders:V2RouteOrder[]){
  if(this.trip.state.action)throw new Error('补给动作进行中');
  const candidate=V2RouteSession.restore(this.city,this.route.serialize());candidate.plan(orders);
  const fastest=orders.map(o=>this.route.fastest(o.pickupNode,o.dropoffNode));
  const ordinaryPricingById:Record<string,{deliveryMetres:number}>=Object.create(null);
  orders.forEach((order,i)=>{if(order.kind==='ordinary')ordinaryPricingById[order.id]={deliveryMetres:fastest[i].heldMetres};});
  const safe=this.dispatch.economyState.heroCompletedOrders<15;
  if(safe&&(fastest.some(route=>route.metres>1000)||candidate.choices().every(c=>c.metres>1000*orders.length||c.metres/1000*[2,2,3,3,4][this.dispatch.economyState.selectedMapId-1]+candidate.serviceBudget.stamina>this.trip.state.stamina)))throw new Error('起步阶段请选择真实短途订单');
  const trip=V2TripRules.restore(this.trip.state);trip.begin(this.dispatch.economyState.selectedMapId,candidate.progress.tripId,orders.map((o,i)=>({id:o.id,...fastest[i],fastestGameSeconds:fastest[i].gameSeconds,safe})));
  const quotes=this.dispatch.acceptBatch(orders,ordinaryPricingById);this.route=candidate;this.trip=trip;return quotes;
 }
 routeChoices(){if(this.route.progress.phase!=='planned')return [];const t=this.trip.state,safe=t.orders.every(o=>o.safe),budget=this.route.serviceBudget;return this.route.choices().filter(c=>!safe||c.metres<=1000*t.orders.length&&c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina<=t.stamina).map(c=>({...c,seconds:(c.seconds-budget.seconds)*this.trip.roadTimeFactor/this.effects.speedRelativeToStarter+budget.seconds,weather:t.weather,stamina:c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina,gameSeconds:t.gameSeconds,orders:t.orders.map(o=>({id:o.id,deadlineGameSeconds:o.deadlineGameSeconds}))}));}
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
  const before=this.dispatch.snapshot();const tick=this.dispatch.tick(sequence,nowSeconds,foreground,paused,{deferAuto:true,deferFleet:true});
  const wallStart=before.frame.nowSeconds,frameEnd=Math.max(wallStart,nowSeconds);
  const pendingAd=(before.rewards as {tickets:{status:string}[]}).tickets.some(t=>t.status==='pending');
  const active=sequence>before.frame.sequence&&foreground&&!paused&&before.frame.foreground&&!before.frame.paused&&!before.clockNeedsRebase&&!pendingAd;
  // Automation expiry never silently drives the remaining interval manually.
  let seconds=before.control==='auto'?tick.autoRunSeconds:active?Math.max(0,nowSeconds-before.frame.nowSeconds):0;
  const allowance=seconds;let used=0;const finish=()=>{this.dispatch.advanceFleetTo(frameEnd);used=Math.min(allowance,Math.max(0,used));if(before.control==='auto'&&used>0)this.dispatch.consumeAutomaticProgress(used);return {...tick,autoRunSeconds:before.control==='auto'?used:0,control:this.dispatch.snapshot().control};};
  if(seconds<=0)return finish();
  const automatic=before.control==='auto';
  // Spend this interval across action and batch boundaries. A stop consumes no tail time.
  while(seconds>0){
   const iterationStart=seconds;
   const afterSupply=this.trip.advanceSupply(seconds);used+=seconds-afterSupply;seconds=afterSupply;
   if(seconds<=0)break;
   // Settle only work available at this action instant, never borrow frame-end NPC income.
   const actionAt=wallStart+used;this.dispatch.advanceFleetTo(actionAt);
   if(automatic&&!this.equippedVehicle)break;
   if(automatic&&this.trip.state.blocked&&!(this.route.progress.phase==='service'&&this.route.progress.serviceCharged)){
    const choice=this.trip.chooseAutoSupply(this.highestSupplyMap,this.dispatch.economyState.cashCents);
    if(!choice)break;
    this.dispatch.withLedgerTime(actionAt,()=>this.trip.startSupply(choice.kind,this.dispatch.snapshot().batchIds.length>0,c=>this.dispatch.chargeSupply(c,{supplyId:choice.kind,quantity:1}),true,choice.source,this.highestSupplyMap));
    // startSupply always creates a positive-duration action. Consume it next iteration.
    continue;
   }
   let phase=this.route.progress.phase;
   if(automatic&&['idle','finished'].includes(phase)&&this.dispatch.snapshot().batchIds.length===0){
    let capacity=this.effects.capacityKg;const selected:V2RouteOrder[]=[];
    for(const offer of this.normalCandidates(8))if(offer.weightKg<=capacity){selected.push(offer);capacity-=offer.weightKg;}
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
  const s=JSON.parse(raw);if(!s||s.format!=='county-v2-game'||![1,2,3,4].includes(s.version))throw new Error('V2组合路线存档不兼容，需显式迁移');
  // Old combinations cannot borrow the new grouping/ready acceptance gate.
  if(s.route?.version!==(s.version===4?2:1))throw new Error('组合与路线状态版本不一致');
  const result=new V2GameSession(city);
  // All original combination checks run on the original structure, before Route
  // normalizes any legacy stop. Dispatch.restore is pure and does not invoke its port.
  result.dispatch=V2DispatchSession.restore(JSON.stringify(s.dispatch),{verifyArrival:(order,token)=>result.route.verifyArrival(order,token)},options);
  const r=s.route,d=result.dispatch.snapshot();result.route.assertDispatch(d,r);
  if(s.version===1){if(d.batchIds.length||!['idle','finished'].includes(r.phase))throw new Error('旧V2在途存档缺少体力行程，需显式迁移');}
  else {
   if(!s.tripState||(s.version===2&&s.tripState.version!==1)||(s.version>=3&&s.tripState.version!==2))throw new Error('组合与补给状态版本不一致');
   result.trip=V2TripRules.restore(s.tripState);const t=result.trip.state;
   // Match the old v1 omitted-latch inference without modifying its source bytes.
   const charged=s.version<4&&r.serviceCharged===undefined?r.phase==='service'&&r.serviceSeconds>0:r.serviceCharged;
   // Restoration must enforce the same action exclusivity as supply() and auto supply.
   if(t.action&&r.phase==='service'&&charged)throw new Error('取送服务与补给动作不能同时进行');
   const pickup=r.phase==='service'&&r.stops[r.cursor]?.kind==='pickup'?r.stops[r.cursor]:null;
   if(r.phase!=='idle'&&(t.orders.length!==r.orders.length||!t.orders.every(o=>r.orders.some((ro:V2RouteOrder)=>ro.id===o.id)&&o.delivered===r.arrivals.some((a:{id:string})=>a.id===o.id)&&o.picked===(r.picked.includes(o.id)&&!(pickup&&(s.version===4?pickup.orderIds.includes(o.id):pickup.orderId===o.id)&&!charged)))))throw new Error('行程与路线不一致');
   if(t.action?.kind==='rest'&&d.batchIds.length>0&&t.action.restore!==20)throw new Error('在途订单不能使用无单休息');
   if(t.action&&t.action.kind!=='rest'&&!result.supplyOptions().some(item=>item.id===t.action!.kind&&item.unlocked))throw new Error('补给开放状态不一致');
   if(t.orders.some(o=>o.delivered&&!d.orders.some(x=>x.id===o.id&&x.status==='completed')))throw new Error('补给或结算状态不一致');
   for(const order of t.orders){const quote=d.orders.find(stored=>stored.id===order.id)?.quote;if(quote&&'ordinaryPricing' in quote&&quantizeOrdinaryDeliveryMetres(order.heldMetres)!==quote.ordinaryPricing!.deliveryMetres)throw new Error('行程与普通计价路程不一致');}
  }
  // restoreLegacy first runs the complete original v1 route gate (including full
  // router-derived legs equality), then adds singleton membership without replanning.
  result.route=V2RouteSession.restore(city,JSON.stringify(s.route));
  if(s.version===1)result.route.cancel();
  return result;
 }
}
