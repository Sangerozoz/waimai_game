import { riderHireQuote, riderEffects, riderUpgradeQuote, cheapestUnhiredRider, vehicleCumulativeUpgradeCost } from './V2RiderEconomy';
import { V2Ledger, V2LedgerContext, V2LedgerCategory, V2LedgerDetail, V2LedgerQuery, V2SupplyChargeDetail, createLedger, appendLedger, validateLedger, validateLedgerContext, summarizeLedger } from './V2Ledger';
import { V2DeliveryOutcome, V2FinalSettlement, settleTripIncome } from './V2TripRules';
import { V2_CONFIG as C, V2_CONFIG_ID } from './V2EconomyConfig';
import { getExperienceLevel, getPlayerIncomeMultiplier } from './GameConfig';

export interface V2Vehicle { id:string; modelId:number|'starter'|'legacy'; level:number; legacyTier?:number; legacySpeedKph?:number; legacyCapacityKg?:number; legacyIncomeFactor?:number }
export interface V2Rider { id:string; level:number; vehicleId:string|null }
export interface V2OrdinaryPricing { version:'ordinary-effort-v1'; deliveryMetres:number }
export type V2OrdinaryPricingById=Readonly<Record<string,Readonly<{deliveryMetres:number}>>>;
export const V2_ORDINARY_PRICING=Object.freeze({version:'ordinary-effort-v1' as const,protectedBasisPoints:10000,baseBasisPoints:9000,deliveryMetresCap:2000,basisPointsPerDeliveryMetre:1,extraKgBasisPoints:500,extraKgCap:2});
export interface V2DeliveryQuote { id:string; configId:string; incomeCents:number; heroOrderOrdinal:number; kind:'ordinary'|'special'; mapId:number; vehicleId:string; weightKg?:number; vehicleLevel?:number; incomeFactor?:number; xpMultiplier?:number; heroCompletedAtAcceptance?:number; specialCoins?:number; ordinaryPricing?:V2OrdinaryPricing }
export interface V2DeliveryReceipt extends Partial<V2FinalSettlement> { id:string; incomeCents:number; heroOrderOrdinal:number }
export interface V2FleetQuote { id:string; riderId:string; vehicleId:string; vehicleLevel:number; riderLevel:number; mapId:number; weightKg:number; incomeCents:number; capacityKg:number; speedRelativeToStarter:number; baseIncomeFactor:number; fixedServiceReduction:number }
export interface V2HeroCompletionEvent { id:string; teamCompletedAfter:number }
export interface V2EconomyState {
 ledger:V2Ledger; ledgerContext?:V2LedgerContext|null;
 cashCents:number; heroCompletedOrders:number; heroExperience:number; hireCount:number; nextVehicleId:number;
 riders:V2Rider[]; vehicles:V2Vehicle[]; ownedMapIds:number[]; selectedMapId:number;
 npcCompletedOrders:number; heroCompletionEvents:V2HeroCompletionEvent[]; fleetQuotes:V2FleetQuote[]; activeQuotes:V2DeliveryQuote[];
 settledOrderIds:string[]; activeQuote:V2DeliveryQuote|null; lastReceipt:V2DeliveryReceipt|null;
}
export interface V2EconomySnapshot { format:'county-v2-economy'; version:1; configId:string; state:V2EconomyState; legacyCheckpoint?:string; [key:string]:unknown }
const clone=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
function check(condition:unknown,message='存档校验失败'):asserts condition {if(!condition)throw new Error(message);}
function int(value:unknown,min=0,max=Number.MAX_SAFE_INTEGER):value is number{return typeof value==='number'&&Number.isSafeInteger(value)&&value>=min&&value<=max;}
function object(value:unknown):value is Record<string,unknown>{return !!value&&typeof value==='object'&&!Array.isArray(value);}
function identity(value:unknown):value is string{return typeof value==='string'&&value.length>0&&value.length<=200;}
/** Canonical metres for the versioned price only; never alter route or trip distance. */
export function quantizeOrdinaryDeliveryMetres(raw:unknown):number {
 check(typeof raw==='number'&&Number.isFinite(raw)&&raw>=0,'普通单路程无效');
 const metres=Math.max(1,Math.round(raw));check(int(metres,1),'普通单路程超出安全范围');return metres;
}
function pricingRecord(value:unknown):value is Record<string,unknown> {return object(value)&&(Object.getPrototypeOf(value)===null||Object.getPrototypeOf(value)===Object.prototype);}
/** A supplied context is complete, own-keyed and detached; omission alone selects the old API. */
export function normalizeOrdinaryPricingById(orders:readonly {id:string;kind:'ordinary'|'special';weightKg:number}[],byId?:V2OrdinaryPricingById):V2OrdinaryPricingById|undefined {
 if(byId===undefined)return undefined;
 check(pricingRecord(byId)&&orders.every(o=>!!o&&identity(o.id)&&(o.kind==='ordinary'||o.kind==='special')),'普通计价上下文无效');
 const ordinary=orders.filter(o=>o.kind==='ordinary'),keys=Reflect.ownKeys(byId);
 check(keys.length===ordinary.length&&keys.every(key=>typeof key==='string'&&ordinary.some(o=>o.id===key)),'普通计价ID不匹配');
 const result:Record<string,Readonly<{deliveryMetres:number}>>=Object.create(null);
 for(const order of ordinary){
  check(int(order.weightKg,1)&&Object.prototype.hasOwnProperty.call(byId,order.id),'普通计价缺少订单或重量无效');
  const input=byId[order.id];check(pricingRecord(input)&&Reflect.ownKeys(input).length===1&&Object.prototype.hasOwnProperty.call(input,'deliveryMetres'),'普通计价路程结构无效');
  result[order.id]={deliveryMetres:quantizeOrdinaryDeliveryMetres(input.deliveryMetres)};
 }
 return result;
}
/** Uses the unrounded base; protected batches multiply by exactly one before the sole round. */
export function ordinaryEffortIncomeCents(mapId:number,incomeFactor:number,xpMultiplier:number,acceptedCount:number,weightKg:number,deliveryMetres:number):number {
 check(int(mapId,1,C.maps.length)&&Number.isFinite(incomeFactor)&&incomeFactor>0&&Number.isFinite(xpMultiplier)&&xpMultiplier>=1&&xpMultiplier<=1.6&&int(acceptedCount)&&int(weightKg,1)&&int(deliveryMetres,1),'普通计价输入无效');
 const rule=V2_ORDINARY_PRICING,n=acceptedCount<C.intro.safeOrders?rule.protectedBasisPoints:rule.baseBasisPoints+rule.basisPointsPerDeliveryMetre*Math.min(deliveryMetres,rule.deliveryMetresCap)+rule.extraKgBasisPoints*Math.min(weightKg-1,rule.extraKgCap);
 const cents=Math.round(C.maps[mapId-1].ordinaryBaseFee*100*incomeFactor*xpMultiplier*(n/rule.protectedBasisPoints));check(int(cents),'普通报价超出安全范围');return cents;
}
/** New metadata is checked on active AND historical quotes; absent legacy quotes are untouched. */
export function validateOrdinaryPricingQuote(quote:V2DeliveryQuote,state:Readonly<V2EconomyState>):void {
 if(!('ordinaryPricing' in quote))return;
 check(Object.prototype.hasOwnProperty.call(quote,'ordinaryPricing')&&quote.kind==='ordinary','专送或继承字段不能附普通计价');
 const pricing=quote.ordinaryPricing;
 check(pricingRecord(pricing)&&Reflect.ownKeys(pricing).length===2&&Object.prototype.hasOwnProperty.call(pricing,'version')&&Object.prototype.hasOwnProperty.call(pricing,'deliveryMetres')&&pricing.version===V2_ORDINARY_PRICING.version&&int(pricing.deliveryMetres,1),'普通计价版本或结构无效');
 check(identity(quote.id)&&quote.configId===V2_CONFIG_ID&&int(quote.mapId,1,C.maps.length)&&identity(quote.vehicleId)&&int(quote.incomeCents)&&int(quote.heroOrderOrdinal,1)&&int(quote.weightKg,1)&&int(quote.vehicleLevel,1,30)&&int(quote.heroCompletedAtAcceptance)&&quote.heroCompletedAtAcceptance<=state.heroCompletedOrders&&quote.heroOrderOrdinal>quote.heroCompletedAtAcceptance,'普通锁定合同无效');
 const vehicle=state.vehicles.find(v=>v.id===quote.vehicleId),acceptedCount=quote.heroCompletedAtAcceptance!;
 check(vehicle&&quote.incomeFactor===vehicleEffects({...vehicle,level:quote.vehicleLevel!}).incomeFactor,'普通锁定车辆收益无效');
 check(quote.xpMultiplier===(acceptedCount<C.intro.safeOrders?1:getPlayerIncomeMultiplier(acceptedCount*10<50?1:getExperienceLevel(acceptedCount*10+50))),'普通锁定经验收益无效');
 check(quote.incomeCents===ordinaryEffortIncomeCents(quote.mapId,quote.incomeFactor!,quote.xpMultiplier!,acceptedCount,quote.weightKg!,pricing.deliveryMetres),'普通锁定报价校验失败');
}
export function vehicleEffects(vehicle:V2Vehicle):{speedRelativeToStarter:number;capacityKg:number;incomeFactor:number} {
 check(vehicle.modelId!=='legacy','旧车辆配置不受支持，请重新开始');
 const base=vehicle.modelId==='starter'?C.starterVehicle:C.vehicles[vehicle.modelId-1];
 const progress=Math.pow((vehicle.level-1)/29,.65);
 return {speedRelativeToStarter:base.speedRelativeToStarter*(1+.2*progress),capacityKg:base.capacityKg*(1+.25*progress),incomeFactor:base.incomeFactor*(1+.2*progress)};
}
/** Shared quote for UI and the debit command, including free starter upgrades. */
export function vehicleUpgradeQuote(vehicle:V2Vehicle) {
 if(vehicle.level>=30)return null;
 check(vehicle.modelId!=='legacy','旧车辆配置不受支持，请重新开始');
 const basis=typeof vehicle.modelId==='number'?C.vehicles[vehicle.modelId-1].price:C.starterVehicle.upgradeCostBasis;
 const cumulative=(level:number)=>typeof vehicle.modelId==='number'?C.upgradeLevels[level-1].vehicleCumulativeCosts[vehicle.modelId-1]:vehicleCumulativeUpgradeCost(basis,level);
 return {costCents:(cumulative(vehicle.level+1)-cumulative(vehicle.level))*100,current:vehicleEffects(vehicle),next:vehicleEffects({...vehicle,level:vehicle.level+1}),nextLevel:vehicle.level+1};
}
export function validateV2EconomySnapshot(value:unknown):asserts value is V2EconomySnapshot {
 check(object(value)&&value.format==='county-v2-economy'&&value.version===1&&value.configId===V2_CONFIG_ID,'存档版本或经济配置版本不受支持');
 check(object(value.state));const s=value.state;
 for(const key of ['cashCents','heroCompletedOrders','heroExperience','hireCount','nextVehicleId'])check(int(s[key]));
 check(int(s.hireCount,0,30)&&int(s.nextVehicleId,1)&&s.heroExperience===(s.heroCompletedOrders as number)*10);
 check(Array.isArray(s.riders)&&s.riders.length===s.hireCount+1&&Array.isArray(s.vehicles)&&s.vehicles.length>0);
 const vehicleIds=new Set<string>(),assigned=new Set<string>(),riderIds=new Set<string>();let maxId=0;
 for(const v of s.vehicles){
  check(object(v)&&identity(v.id)&&!vehicleIds.has(v.id)&&int(v.level,1,30));vehicleIds.add(v.id);
  check(v.modelId==='starter'||int(v.modelId,1,10));

  if(/^v2-vehicle-[1-9]\d*$/.test(v.id))maxId=Math.max(maxId,Number(v.id.slice(11)));
 }
 check(Number.isSafeInteger(maxId)&&s.nextVehicleId>maxId);
 for(const r of s.riders){check(object(r)&&identity(r.id)&&!riderIds.has(r.id)&&int(r.level,1,30));riderIds.add(r.id);
  check(r.id==='hero'||/^npc-([1-9]|[12]\d|30)$/.test(r.id));
  check(r.vehicleId===null||typeof r.vehicleId==='string'&&vehicleIds.has(r.vehicleId)&&!assigned.has(r.vehicleId));if(r.vehicleId!==null)assigned.add(r.vehicleId as string);
 }
 check(riderIds.has('hero')&&s.riders[0].id==='hero');
 check(Array.isArray(s.ownedMapIds)&&s.ownedMapIds.includes(1)&&s.ownedMapIds.every(id=>int(id,1,5))&&new Set(s.ownedMapIds).size===s.ownedMapIds.length&&s.ownedMapIds.includes(s.selectedMapId));
 check(Array.isArray(s.settledOrderIds)&&s.settledOrderIds.every(identity)&&new Set(s.settledOrderIds).size===s.settledOrderIds.length);
 check(int(s.npcCompletedOrders)&&Array.isArray(s.heroCompletionEvents)&&Array.isArray(s.fleetQuotes)&&Array.isArray(s.activeQuotes));
 check(s.heroCompletionEvents.length<=Number(s.heroCompletedOrders)&&int(Number(s.heroCompletedOrders)+Number(s.npcCompletedOrders)));
 const typedState=s as unknown as V2EconomyState;
 let previous=0;const eventIds=new Set<string>();
 for(const ev of typedState.heroCompletionEvents){check(object(ev)&&identity(ev.id)&&!eventIds.has(ev.id)&&s.settledOrderIds.includes(ev.id)&&int(ev.teamCompletedAfter,1)&&ev.teamCompletedAfter>previous&&ev.teamCompletedAfter<=Number(s.heroCompletedOrders)+Number(s.npcCompletedOrders));eventIds.add(ev.id);previous=ev.teamCompletedAfter;}
 const openIds=new Set<string>();
 for(const q of typedState.activeQuotes){check(object(q)&&identity(q.id)&&!openIds.has(q.id)&&!s.settledOrderIds.includes(q.id)&&q.configId===V2_CONFIG_ID&&int(q.mapId,1,5)&&vehicleIds.has(q.vehicleId)&&int(q.incomeCents)&&int(q.heroOrderOrdinal,1));openIds.add(q.id);
  check(q.kind==='ordinary'||q.kind==='special');
  {check(typeof q.incomeFactor==='number'&&Number.isFinite(q.incomeFactor)&&q.incomeFactor>0&&typeof q.xpMultiplier==='number'&&Number.isFinite(q.xpMultiplier)&&q.xpMultiplier>=1&&q.xpMultiplier<=1.6&&int(q.vehicleLevel,1,30)&&typeof q.weightKg==='number'&&Number.isFinite(q.weightKg)&&q.weightKg>0);
   const lockedVehicle=typedState.vehicles.find(v=>v.id===q.vehicleId)!;check(q.incomeFactor===vehicleEffects({...lockedVehicle,level:q.vehicleLevel!}).incomeFactor&&int(q.heroCompletedAtAcceptance)&&q.heroCompletedAtAcceptance<=typedState.heroCompletedOrders);
   const acceptedCount=q.heroCompletedAtAcceptance!;check(q.xpMultiplier===(acceptedCount<C.intro.safeOrders?1:getPlayerIncomeMultiplier(acceptedCount*10<50?1:getExperienceLevel(acceptedCount*10+50))));
   if('ordinaryPricing' in q)validateOrdinaryPricingQuote(q,typedState);
   else check(q.kind==='special'?int(q.specialCoins,100,150)&&q.incomeCents===q.specialCoins*100:q.incomeCents===Math.round(C.maps[q.mapId-1].ordinaryBaseFee*100*q.incomeFactor*q.xpMultiplier),'锁定报价校验失败');
  }
 }
 check(typedState.activeQuotes.length===0||typedState.activeQuotes.every(q=>q.vehicleId===typedState.riders[0].vehicleId&&q.mapId===typedState.selectedMapId));
 check(JSON.stringify(s.activeQuote)===JSON.stringify(s.activeQuotes[0]||null));
 for(const q of typedState.fleetQuotes){check(object(q)&&identity(q.id)&&!openIds.has(q.id)&&!s.settledOrderIds.includes(q.id)&&riderIds.has(q.riderId)&&q.riderId!=='hero'&&vehicleIds.has(q.vehicleId)&&int(q.riderLevel,1,30)&&int(q.vehicleLevel,1,30)&&int(q.mapId,1,5)&&int(q.weightKg,1)&&int(q.incomeCents));openIds.add(q.id);
  const v=(s as unknown as V2EconomyState).vehicles.find(v=>v.id===q.vehicleId)!;const effects=vehicleEffects({...v,level:q.vehicleLevel}),rider=riderEffects(q.riderId,q.riderLevel);
  check(q.capacityKg===effects.capacityKg&&q.speedRelativeToStarter===effects.speedRelativeToStarter&&q.weightKg<=q.capacityKg&&q.baseIncomeFactor===rider.baseIncomeFactor&&q.fixedServiceReduction===rider.fixedServiceReduction&&q.incomeCents===Math.round(C.maps[q.mapId-1].ordinaryBaseFee*100*effects.incomeFactor*rider.incomeFactor),'NPC锁定报价校验失败');
 }
 if(s.lastReceipt!==null){const r=s.lastReceipt;check(object(r)&&identity(r.id)&&int(r.incomeCents)&&int(r.heroOrderOrdinal,1)&&s.settledOrderIds.includes(r.id));if(r.baseIncomeCents!==undefined){const calculated=settleTripIncome(r.baseIncomeCents as number,{lateGameSeconds:r.lateGameSeconds as number,damage:r.damage as V2DeliveryOutcome['damage']});check(r.incomeCents===calculated.incomeCents&&r.lateRetain===calculated.lateRetain&&r.damageRetain===calculated.damageRetain&&r.ratingDelta===calculated.ratingDelta);}}
 validateLedger(s.ledger,typedState.cashCents);if(s.ledgerContext!==undefined)validateLedgerContext(s.ledgerContext);
 check(value.legacyCheckpoint===undefined&&value.legacyOriginalCheckpoint===undefined,'旧存档迁移不受支持，请重新开始');

}

function ordinaryIncomeCents(s:V2EconomyState,vehicle:V2Vehicle):number {
 const xpMultiplier=s.heroCompletedOrders<C.intro.safeOrders?1:getPlayerIncomeMultiplier(s.heroExperience<50?1:getExperienceLevel(s.heroExperience+50));
 return Math.round(C.maps[s.selectedMapId-1].ordinaryBaseFee*100*vehicleEffects(vehicle).incomeFactor*xpMultiplier);
}

/** Pure economic commands. No storage, clocks, random rewards, map rendering or route mutation. */
export class V2EconomySession {
 private snapshot:V2EconomySnapshot;
 constructor(){this.snapshot={format:'county-v2-economy',version:1,configId:V2_CONFIG_ID,state:{ledger:createLedger(C.startCoins*100,'initial'),cashCents:C.startCoins*100,heroCompletedOrders:0,heroExperience:0,hireCount:0,nextVehicleId:1,riders:[{id:'hero',level:1,vehicleId:'starter-1'}],vehicles:[{id:'starter-1',modelId:'starter',level:1}],ownedMapIds:[1],selectedMapId:1,npcCompletedOrders:0,heroCompletionEvents:[],fleetQuotes:[],activeQuotes:[],settledOrderIds:[],activeQuote:null,lastReceipt:null}};}
 static restore(serialized:string):V2EconomySession {const raw:unknown=JSON.parse(serialized);validateV2EconomySnapshot(raw);const session=new V2EconomySession();session.snapshot=clone(raw);return session;}
 /** Atomically restores a validated draft; performs no storage write. */
 replaceFrom(serialized:string):void {const restored=V2EconomySession.restore(serialized);this.snapshot=restored.snapshot;}
 get state():Readonly<V2EconomyState>{return clone(this.snapshot.state);}
 /** Scalar event progress only; avoids cloning the wallet to check pending replenishment. */
 get heroCompletionEventCount():number {return this.snapshot.state.heroCompletionEvents.length;}
 serialize():string{return JSON.stringify(this.snapshot);}
 setLedgerContext(context:V2LedgerContext|null):void {validateLedgerContext(context);this.snapshot.state.ledgerContext=clone(context);}
 ledgerSummary(query:V2LedgerQuery){const s=this.snapshot.state,report=summarizeLedger(s.ledger,query);return {...report,reconciliation:{...report.reconciliation,currentCashCents:s.cashCents,balanced:report.reconciliation.expectedCashCents===s.cashCents}};}
 private record(s:V2EconomyState,category:V2LedgerCategory,amountCents:number,detail:V2LedgerDetail={},id?:string):void {appendLedger(s.ledger,{id,category,amountCents,detail},s.ledgerContext||null);}
 get nextHirePriceCents():number|null{return cheapestUnhiredRider(this.snapshot.state.riders)?.priceCents??null;}
 private idle():void {check(!this.snapshot.state.activeQuote,'配送中请先完成订单');}
 /** Historical module compile surface only; current snapshots reject legacy checkpoints. */
 get hasPendingLegacyTrip():boolean {return false;}
 private transact(cost:number,change:(draft:V2EconomyState)=>void,category?:V2LedgerCategory,detail:V2LedgerDetail={}):void {
  this.idle();check(int(cost),'金额超出安全范围');check(this.snapshot.state.cashCents>=cost,'余额不足');const next=clone(this.snapshot);next.state.cashCents-=cost;change(next.state);if(cost>0){check(category,'账目类别缺失');this.record(next.state,category,-cost,detail);}validateV2EconomySnapshot(next);this.snapshot=next;
 }
 buyVehicle(modelId:number):string {check(int(modelId,1,10),'车型无效');const id=`v2-vehicle-${this.snapshot.state.nextVehicleId}`;
  this.transact(C.vehicles[modelId-1].price*100,s=>{s.vehicles.push({id,modelId,level:1});s.nextVehicleId++;},'vehicle_purchase',{vehicleId:id,modelId});return id;
 }
 hireRider(id:string):void {check(/^npc-([1-9]|[12]\d|30)$/.test(id),'人物无效');check(!this.snapshot.state.riders.some(r=>r.id===id),'人物已招募');const price=riderHireQuote(id).priceCents;this.transact(price,s=>{s.riders.push({id,level:1,vehicleId:null});s.hireCount++;},'rider_hire',{riderId:id});}
 assignVehicle(riderId:string,vehicleId:string|null):void {
  const s=this.snapshot.state;check(s.riders.some(r=>r.id===riderId),'人物未招募');check(vehicleId===null||s.vehicles.some(v=>v.id===vehicleId),'车辆不存在');
  check(vehicleId===null||!s.fleetQuotes.some(q=>q.vehicleId===vehicleId&&q.riderId!==riderId),'车辆仍执行旧批次');
  check(vehicleId===null||!s.riders.some(r=>r.id!==riderId&&r.vehicleId===vehicleId),'车辆已被其他人物占用');
  this.transact(0,s=>{s.riders.find(r=>r.id===riderId)!.vehicleId=vehicleId;});
 }
 buyMap(id:number):void {check(int(id,1,5),'地图无效');check(!this.snapshot.state.ownedMapIds.includes(id),'地图已拥有');this.transact(C.maps[id-1].price*100,s=>{s.ownedMapIds.push(id);},'map_purchase',{mapId:id});}
 selectMap(id:number):void {check(this.snapshot.state.ownedMapIds.includes(id),'地图未购买');this.transact(0,s=>{s.selectedMapId=id;});}
 upgradeVehicle(id:string):void {
  const vehicle=this.snapshot.state.vehicles.find(v=>v.id===id);check(vehicle,'车辆不存在');check(vehicle.level<30,'车辆已满级');
  const cost=vehicleUpgradeQuote(vehicle)!.costCents;
  this.transact(cost,s=>{s.vehicles.find(v=>v.id===id)!.level++;},'vehicle_upgrade',{vehicleId:id,level:vehicle.level+1});
 }
 upgradeRider(id:string):void {const rider=this.snapshot.state.riders.find(r=>r.id===id);check(rider,'人物未招募');check(rider.level<30,'人物已满级');check(id!=='hero','主角通过配送获得经验等级');
  this.transact(riderUpgradeQuote(id,rider.level)!.costCents,s=>{s.riders.find(r=>r.id===id)!.level++;},'rider_upgrade',{riderId:id,level:rider.level+1});
 }
 /** Creates immutable contracts; routing/arrival must still be confirmed by the caller. */
 acceptOrdinary(id:string):V2DeliveryQuote {return this.acceptBatch([{id,kind:'ordinary',weightKg:1}])[0];}
 acceptBatch(orders:{id:string;kind:'ordinary'|'special';weightKg:number;specialCoins?:number}[],ordinaryPricingById?:V2OrdinaryPricingById):V2DeliveryQuote[] {
  this.idle();check(Array.isArray(orders)&&orders.length>0,'空订单批次');const s=this.snapshot.state,vehicle=s.vehicles.find(v=>v.id===s.riders[0].vehicleId);check(vehicle,'主角尚未配车');
  const pricingById=normalizeOrdinaryPricingById(orders,ordinaryPricingById);
  const ids=new Set<string>();let weight=0;const effects=vehicleEffects(vehicle),xpMultiplier=s.heroCompletedOrders<C.intro.safeOrders?1:getPlayerIncomeMultiplier(s.heroExperience<50?1:getExperienceLevel(s.heroExperience+50));
  const quotes=orders.map((o,i)=>{check(identity(o.id)&&!ids.has(o.id)&&!s.settledOrderIds.includes(o.id)&&!s.fleetQuotes.some(q=>q.id===o.id),'订单编号无效或重复');ids.add(o.id);check(typeof o.weightKg==='number'&&Number.isFinite(o.weightKg)&&o.weightKg>0,'订单重量无效');weight+=o.weightKg;
   check(o.kind==='ordinary'||o.kind==='special','订单类型无效');if(o.kind==='special')check(orders.length===1&&int(o.specialCoins,100,150),'专送必须独占且报价100–150');
   const pricing:V2OrdinaryPricing|undefined=o.kind==='ordinary'&&pricingById!==undefined?{version:V2_ORDINARY_PRICING.version,deliveryMetres:pricingById[o.id].deliveryMetres}:undefined;
   const q:V2DeliveryQuote={id:o.id,configId:V2_CONFIG_ID,incomeCents:o.kind==='special'?o.specialCoins!*100:pricing?ordinaryEffortIncomeCents(s.selectedMapId,effects.incomeFactor,xpMultiplier,s.heroCompletedOrders,o.weightKg,pricing.deliveryMetres):ordinaryIncomeCents(s,vehicle),heroOrderOrdinal:s.heroCompletedOrders+i+1,kind:o.kind,mapId:s.selectedMapId,vehicleId:vehicle.id,weightKg:o.weightKg,vehicleLevel:vehicle.level,incomeFactor:effects.incomeFactor,xpMultiplier,heroCompletedAtAcceptance:s.heroCompletedOrders};if(o.kind==='special')q.specialCoins=o.specialCoins;if(pricing)q.ordinaryPricing=pricing;return q;
  });check(weight<=effects.capacityKg,'订单超载');const next=clone(this.snapshot);next.state.activeQuotes=quotes;next.state.activeQuote=quotes[0];validateV2EconomySnapshot(next);this.snapshot=next;return clone(quotes);
 }
 cancelDelivery(id:string):void {const next=clone(this.snapshot);check(next.state.activeQuotes.some(q=>q.id===id),'当前配送订单不匹配');next.state.activeQuotes=next.state.activeQuotes.filter(q=>q.id!==id);next.state.activeQuote=next.state.activeQuotes[0]||null;validateV2EconomySnapshot(next);this.snapshot=next;}
 chargeSupply(costCents:number,detail:V2SupplyChargeDetail={}):void {
  check(int(costCents)&&[0,100,300,400,700,900,1500].includes(costCents),'补给费用无效');
  check(detail.supplyId===undefined||identity(detail.supplyId),'补给类型无效');check(detail.quantity===undefined||int(detail.quantity,1),'补给数量无效');check(detail.transactionId===undefined||identity(detail.transactionId),'补给交易编号无效');
  const id=detail.transactionId?`supply:${detail.transactionId}`:undefined;
  const previous=id?this.snapshot.state.ledger.entries.find(e=>e.id===id):undefined;
  if(previous){check(previous.category==='supply_purchase'&&previous.amountCents===-costCents&&previous.detail.supplyId===detail.supplyId&&previous.detail.quantity===detail.quantity&&previous.detail.transactionId===detail.transactionId,'补给重试冲突');return;}
  check(this.snapshot.state.cashCents>=costCents,'余额不足');if(costCents===0)return;
  const next=clone(this.snapshot);next.state.cashCents-=costCents;this.record(next.state,'supply_purchase',-costCents,detail,id);validateV2EconomySnapshot(next);this.snapshot=next;
 }
 completeDelivery(orderId:string,outcome:V2DeliveryOutcome={lateGameSeconds:0,damage:'none'}):V2DeliveryReceipt {
  const s=this.snapshot.state;check(identity(orderId),'订单编号无效');if(s.lastReceipt?.id===orderId)return clone(s.lastReceipt);
  check(!s.settledOrderIds.includes(orderId),'订单已结算');const q=s.activeQuotes.find(q=>q.id===orderId);check(q,'当前配送订单不匹配或已经结算');
  const next=clone(this.snapshot),n=next.state;const final=settleTripIncome(q.incomeCents,outcome);const receipt={id:q.id,...final,heroOrderOrdinal:n.heroCompletedOrders+1};n.cashCents+=final.incomeCents;this.record(n,q.kind==='special'?'hero_special':'hero_ordinary',final.incomeCents,{orderId:q.id,vehicleId:q.vehicleId,mapId:q.mapId},`order:${q.id}`);n.heroCompletedOrders++;n.heroExperience+=10;n.settledOrderIds.push(q.id);n.activeQuotes=n.activeQuotes.filter(v=>v.id!==q.id);n.activeQuote=n.activeQuotes[0]||null;n.lastReceipt=receipt;n.heroCompletionEvents.push({id:q.id,teamCompletedAfter:n.heroCompletedOrders+n.npcCompletedOrders});validateV2EconomySnapshot(next);this.snapshot=next;return clone(receipt);
 }
 /** No caller-supplied amount: only current assets and legal integer weights establish NPC credit. */
 registerFleetOrders(riderId:string,ids:string[],weights:number[]):V2FleetQuote[] {
  const s=this.snapshot.state,r=s.riders.find(r=>r.id===riderId&&r.id!=='hero'),v=s.vehicles.find(v=>v.id===r?.vehicleId);check(r&&v,'NPC未配车');
  check(!s.fleetQuotes.some(q=>q.riderId===riderId||q.vehicleId===v.id),'NPC或车辆仍有旧批次');check(ids.length>0&&ids.length===weights.length&&new Set(ids).size===ids.length,'NPC批次无效');const effects=vehicleEffects(v),rider=riderEffects(riderId,r.level);
  check(weights.every(w=>int(w,1))&&weights.reduce((a,b)=>a+b,0)<=effects.capacityKg,'NPC订单超载');
  for(const id of ids)check(identity(id)&&!s.settledOrderIds.includes(id)&&!s.activeQuotes.some(q=>q.id===id)&&!s.fleetQuotes.some(q=>q.id===id),'订单编号无效或重复');
  const quotes=ids.map((id,i)=>({id,riderId,vehicleId:v.id,vehicleLevel:v.level,riderLevel:r.level,mapId:s.selectedMapId,weightKg:weights[i],baseIncomeFactor:rider.baseIncomeFactor,fixedServiceReduction:rider.fixedServiceReduction,incomeCents:Math.round(C.maps[s.selectedMapId-1].ordinaryBaseFee*100*effects.incomeFactor*rider.incomeFactor),capacityKg:effects.capacityKg,speedRelativeToStarter:effects.speedRelativeToStarter}));
  const next=clone(this.snapshot);next.state.fleetQuotes.push(...quotes);validateV2EconomySnapshot(next);this.snapshot=next;return clone(quotes);
 }
 settleFleetOrder(id:string):number {
  const s=this.snapshot.state;if(s.settledOrderIds.includes(id))return 0;const q=s.fleetQuotes.find(q=>q.id===id);check(q,'NPC订单未签约');
  const next=clone(this.snapshot);next.state.cashCents+=q.incomeCents;this.record(next.state,'npc_delivery',q.incomeCents,{orderId:id,riderId:q.riderId,vehicleId:q.vehicleId,mapId:q.mapId},`order:${id}`);next.state.npcCompletedOrders++;next.state.settledOrderIds.push(id);next.state.fleetQuotes=next.state.fleetQuotes.filter(q=>q.id!==id);validateV2EconomySnapshot(next);this.snapshot=next;return q.incomeCents;
 }
}
