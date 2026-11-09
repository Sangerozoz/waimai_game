import { riderHireQuote, riderEffects, riderUpgradeQuote, cheapestUnhiredRider, vehicleCumulativeUpgradeCost } from './V2RiderEconomy';
import { V2Ledger, V2LedgerContext, V2LedgerCategory, V2LedgerDetail, V2LedgerQuery, V2SupplyChargeDetail, createLedger, appendLedger, validateLedger, validateLedgerContext, summarizeLedger } from './V2Ledger';
import { V2DeliveryOutcome, V2FinalSettlement, settleTripIncome } from './V2TripRules';
import { V2_CONFIG as C, V2_CONFIG_ID } from './V2EconomyConfig';
import { getExperienceLevel, getPlayerIncomeMultiplier } from './GameConfig';
import { V2_SLOT_PROFILE_ID,V2_SLOT_PRICE_POLICY,V2_SLOT_EFFECT_POLICY,V2_SLOT_START_CENTS,slotVehicleEffects,slotVehicleUpgradeQuote,slotRiderEffects,slotRiderUpgradeQuote,slotVehiclePurchaseQuote,slotRiderHireQuote,slotMapBaseIncomeCents,slotMapPurchaseQuote,slotNextHirePriceCents,parseV2ContractTerms,sameV2ContractTerms } from './V2EconomyProfiles';
import type { V2ContractTerms,V2SlotContractTerms,V2SlotVehicleEffects,V2SlotRiderEffects } from './V2EconomyProfiles';
import { slotLoadForOrderId,fitsV2Capacity } from './V2LoadRules';
import type { V2Capacity } from './V2LoadRules';


export interface V2Vehicle { id:string; modelId:number|'starter'|'legacy'; level:number; legacyTier?:number; legacySpeedKph?:number; legacyCapacityKg?:number; legacyIncomeFactor?:number }
export interface V2Rider { id:string; level:number; vehicleId:string|null }
export interface V2DeliveryEffects { profileId:string;speedRelativeToStarter:number;incomeFactor:number;capacity:V2Capacity }
export interface V2OrdinaryPricing { version:'ordinary-effort-v1'|'distance-effort-slots-v1'; deliveryMetres:number }
export const V2_HERO_EMERGENCY_POLICY='hero-emergency-base-v1';
export interface V2HeroEmergencyLoan { policyId:typeof V2_HERO_EMERGENCY_POLICY;sequence:number;active:boolean }
export interface V2EmergencyVehicleRef {kind:'emergency';loanSequence:number;policyId:typeof V2_HERO_EMERGENCY_POLICY}
export type V2OrdinaryPricingById=Readonly<Record<string,Readonly<{deliveryMetres:number}>>>;
export const V2_ORDINARY_PRICING=Object.freeze({version:'ordinary-effort-v1' as const,protectedBasisPoints:10000,baseBasisPoints:9000,deliveryMetresCap:2000,basisPointsPerDeliveryMetre:1,extraKgBasisPoints:500,extraKgCap:2});
export interface V2DeliveryQuote { id:string; configId:string; incomeCents:number; heroOrderOrdinal:number; kind:'ordinary'|'special'; mapId:number; vehicleId?:string;vehicleRef?:V2EmergencyVehicleRef; weightKg?:number; vehicleLevel?:number; incomeFactor?:number; xpMultiplier?:number; heroCompletedAtAcceptance?:number; specialCoins?:number; ordinaryPricing?:V2OrdinaryPricing;terms?:V2ContractTerms }
export interface V2DeliveryReceipt extends Partial<V2FinalSettlement> { id:string; incomeCents:number; heroOrderOrdinal:number }
export interface V2FleetQuote { id:string; riderId:string; vehicleId:string; vehicleLevel:number; riderLevel:number; mapId:number; weightKg?:number; incomeCents:number; capacityKg?:number; speedRelativeToStarter:number; baseIncomeFactor:number; fixedServiceReduction:number;terms?:V2ContractTerms }
export interface V2HeroCompletionEvent { id:string; teamCompletedAfter:number }
export interface V2EconomyState {
 ledger:V2Ledger; ledgerContext?:V2LedgerContext|null;
 cashCents:number; heroCompletedOrders:number; heroExperience:number; hireCount:number; nextVehicleId:number;
 riders:V2Rider[]; vehicles:V2Vehicle[]; ownedMapIds:number[]; selectedMapId:number;
 npcCompletedOrders:number; heroCompletionEvents:V2HeroCompletionEvent[]; fleetQuotes:V2FleetQuote[]; activeQuotes:V2DeliveryQuote[];
 settledOrderIds:string[]; activeQuote:V2DeliveryQuote|null; lastReceipt:V2DeliveryReceipt|null;
 heroEmergencyLoan?:V2HeroEmergencyLoan;
}
export interface V2EconomySnapshot { format:'county-v2-economy'; version:1|2|3; configId:string; state:V2EconomyState; legacyCheckpoint?:string; [key:string]:unknown }
const clone=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
function check(condition:unknown,message='存档校验失败'):asserts condition {if(!condition)throw new Error(message);}
function int(value:unknown,min=0,max=Number.MAX_SAFE_INTEGER):value is number{return typeof value==='number'&&Number.isSafeInteger(value)&&value>=min&&value<=max;}
function object(value:unknown):value is Record<string,unknown>{return !!value&&typeof value==='object'&&!Array.isArray(value);}
function identity(value:unknown):value is string{return typeof value==='string'&&value.length>0&&value.length<=200;}
function hasRecoverableHeroVehicle(state:Readonly<V2EconomyState>):boolean {
 return state.vehicles.some(vehicle=>!state.riders.some(rider=>rider.id!=='hero'&&rider.vehicleId===vehicle.id)&&!state.fleetQuotes.some(quote=>quote.vehicleId===vehicle.id));
}
/** Ownership stays real; reclaiming may additionally detach an NPC's future assignment. */
function reclaimableHeroVehicleIds(state:Readonly<V2EconomyState>):string[] {return state.vehicles.filter(v=>!state.fleetQuotes.some(q=>q.vehicleId===v.id)).map(v=>v.id);}
const emergencyVehicle=()=>({modelId:'starter' as const,level:1});
function validateEmergencyRef(quote:V2DeliveryQuote,state:Readonly<V2EconomyState>):void {
 const ref=quote.vehicleRef,loan=state.heroEmergencyLoan;
 check(object(ref)&&Reflect.ownKeys(ref).length===3&&['kind','loanSequence','policyId'].every(k=>Object.prototype.propertyIsEnumerable.call(ref,k))&&ref.kind==='emergency'&&ref.policyId===V2_HERO_EMERGENCY_POLICY&&int(ref.loanSequence,1)&&loan&&ref.loanSequence<=loan.sequence&&!('vehicleId' in quote),'应急合同车辆来源无效');
}
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
function validateLegacyOrdinaryPricingQuote(quote:V2DeliveryQuote,state:Readonly<V2EconomyState>):void {
 check(!('vehicleRef' in quote),'旧公斤合同不能使用借车来源');
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
export function validateLegacyV2EconomySnapshot(value:unknown):asserts value is V2EconomySnapshot {
 check(object(value)&&value.format==='county-v2-economy'&&value.version===1&&value.configId===V2_CONFIG_ID,'存档版本或经济配置版本不受支持');
 check(object(value.state));const s=value.state;
 check(!('heroEmergencyLoan' in s),'旧经济容器不能包含借车记录');
 for(const key of ['cashCents','heroCompletedOrders','heroExperience','hireCount','nextVehicleId'])check(int(s[key]));
 check(int(s.hireCount,0,30)&&int(s.nextVehicleId,1)&&s.heroExperience===(s.heroCompletedOrders as number)*10);
 check(Array.isArray(s.riders)&&s.riders.length===s.hireCount+1&&Array.isArray(s.vehicles)&&s.vehicles.length>0);
 const vehicleIds=new Set<string>(),assigned=new Set<string>(),riderIds=new Set<string>();let maxId=0;
 for(const v of s.vehicles){
  check(object(v)&&!('vehicleRef' in v)&&identity(v.id)&&!vehicleIds.has(v.id)&&int(v.level,1,30));vehicleIds.add(v.id);
  check(v.modelId==='starter'||int(v.modelId,1,10));

  if(/^v2-vehicle-[1-9]\d*$/.test(v.id))maxId=Math.max(maxId,Number(v.id.slice(11)));
 }
 check(Number.isSafeInteger(maxId)&&s.nextVehicleId>maxId);
 for(const r of s.riders){check(object(r)&&identity(r.id)&&!riderIds.has(r.id)&&int(r.level,1,30));riderIds.add(r.id);
  check(r.id==='hero'||/^npc-([1-9]|[12]\d|30)$/.test(r.id));
  check(r.vehicleId===null||typeof r.vehicleId==='string'&&vehicleIds.has(r.vehicleId)&&!assigned.has(r.vehicleId));if(r.vehicleId!==null)assigned.add(r.vehicleId as string);
 }
 check(riderIds.has('hero')&&s.riders[0].id==='hero');
 check(int(s.selectedMapId,1,5));
 check(Array.isArray(s.ownedMapIds)&&s.ownedMapIds.includes(1)&&s.ownedMapIds.every(id=>int(id,1,5))&&new Set(s.ownedMapIds).size===s.ownedMapIds.length&&s.ownedMapIds.includes(s.selectedMapId));
 check(Array.isArray(s.settledOrderIds)&&s.settledOrderIds.every(identity)&&new Set(s.settledOrderIds).size===s.settledOrderIds.length);
 check(int(s.npcCompletedOrders)&&Array.isArray(s.heroCompletionEvents)&&Array.isArray(s.fleetQuotes)&&Array.isArray(s.activeQuotes));
 check(s.heroCompletionEvents.length<=Number(s.heroCompletedOrders)&&int(Number(s.heroCompletedOrders)+Number(s.npcCompletedOrders)));
 const typedState=s as unknown as Omit<V2EconomyState,'fleetQuotes'>&{fleetQuotes:(V2FleetQuote&{weightKg:number;capacityKg:number})[]};
 let previous=0;const eventIds=new Set<string>();
 for(const ev of typedState.heroCompletionEvents){check(object(ev)&&identity(ev.id)&&!eventIds.has(ev.id)&&s.settledOrderIds.includes(ev.id)&&int(ev.teamCompletedAfter,1)&&ev.teamCompletedAfter>previous&&ev.teamCompletedAfter<=Number(s.heroCompletedOrders)+Number(s.npcCompletedOrders));eventIds.add(ev.id);previous=ev.teamCompletedAfter;}
 const openIds=new Set<string>();
 for(const q of typedState.activeQuotes){check(object(q)&&!('vehicleRef' in q)&&identity(q.id)&&!openIds.has(q.id)&&!s.settledOrderIds.includes(q.id)&&q.configId===V2_CONFIG_ID&&int(q.mapId,1,5)&&identity(q.vehicleId)&&vehicleIds.has(q.vehicleId)&&int(q.incomeCents)&&int(q.heroOrderOrdinal,1));openIds.add(q.id);
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
 for(const q of typedState.fleetQuotes){check(object(q)&&!('vehicleRef' in q)&&identity(q.id)&&!openIds.has(q.id)&&!s.settledOrderIds.includes(q.id)&&riderIds.has(q.riderId)&&q.riderId!=='hero'&&vehicleIds.has(q.vehicleId)&&int(q.riderLevel,1,30)&&int(q.vehicleLevel,1,30)&&int(q.mapId,1,5)&&int(q.weightKg,1)&&int(q.incomeCents));openIds.add(q.id);
  const v=(s as unknown as V2EconomyState).vehicles.find(v=>v.id===q.vehicleId)!;const effects=vehicleEffects({...v,level:q.vehicleLevel}),rider=riderEffects(q.riderId,q.riderLevel);
  check(q.capacityKg===effects.capacityKg&&q.speedRelativeToStarter===effects.speedRelativeToStarter&&q.weightKg<=q.capacityKg&&q.baseIncomeFactor===rider.baseIncomeFactor&&q.fixedServiceReduction===rider.fixedServiceReduction&&q.incomeCents===Math.round(C.maps[q.mapId-1].ordinaryBaseFee*100*effects.incomeFactor*rider.incomeFactor),'NPC锁定报价校验失败');
 }
 if(s.lastReceipt!==null){const r=s.lastReceipt;check(object(r)&&identity(r.id)&&int(r.incomeCents)&&int(r.heroOrderOrdinal,1)&&s.settledOrderIds.includes(r.id));if(r.baseIncomeCents!==undefined){const calculated=settleTripIncome(r.baseIncomeCents as number,{lateGameSeconds:r.lateGameSeconds as number,damage:r.damage as V2DeliveryOutcome['damage']});check(r.incomeCents===calculated.incomeCents&&r.lateRetain===calculated.lateRetain&&r.damageRetain===calculated.damageRetain&&r.ratingDelta===calculated.ratingDelta);}}
 validateLedger(s.ledger,typedState.cashCents);if(s.ledgerContext!==undefined)validateLedgerContext(s.ledgerContext);
 check(value.legacyCheckpoint===undefined&&value.legacyOriginalCheckpoint===undefined,'旧存档迁移不受支持，请重新开始');

}

/** New units have their own tariff. In particular, there is no extraKg input. */
export function slotOrdinaryIncomeCents(mapId:number,incomeFactor:number,xpMultiplier:number,acceptedCount:number,deliveryMetres:number):number {
 check(int(mapId,1,5)&&Number.isFinite(incomeFactor)&&incomeFactor>0&&Number.isFinite(xpMultiplier)&&xpMultiplier>=1&&xpMultiplier<=1.6&&int(acceptedCount)&&int(deliveryMetres,1),'格子普通报价输入无效');
 const rule=V2_ORDINARY_PRICING,n=acceptedCount<C.intro.safeOrders?rule.protectedBasisPoints:rule.baseBasisPoints+Math.min(deliveryMetres,rule.deliveryMetresCap)*rule.basisPointsPerDeliveryMetre;
 const cents=Math.round(slotMapBaseIncomeCents(mapId)*incomeFactor*xpMultiplier*(n/rule.protectedBasisPoints));check(int(cents));return cents;
}
export function legacyQuotePayload<T extends {terms?:V2ContractTerms}>(quote:T):Omit<T,'terms'> {
 const {terms,...payload}=quote;return payload;
}
/** Call only after the original containing payload has passed its complete validator. */
export function wrapLegacyQuote<T extends {terms?:V2ContractTerms}>(quote:T):T {
 check(!('terms' in quote),'旧合同不能附新条款');return {...quote,terms:{version:'kg-v1',profileId:V2_CONFIG_ID}};
}
export function contractTerms(quote:{terms?:V2ContractTerms}):V2ContractTerms {
 check(Object.prototype.propertyIsEnumerable.call(quote,'terms'),'新容器缺少合同单位');return parseV2ContractTerms(quote.terms);
}
function heroSlotTerms(id:string,kind:'ordinary'|'special',vehicle:Pick<V2Vehicle,'modelId'|'level'>,riderLevel:number):V2SlotContractTerms {
 const effects=slotVehicleEffects(vehicle);return {version:'slots-v1',profileId:V2_SLOT_PROFILE_ID,pricePolicyId:kind==='ordinary'?V2_SLOT_PRICE_POLICY:'slots-special-v1',effectPolicyId:V2_SLOT_EFFECT_POLICY,
 load:slotLoadForOrderId(id),capacity:effects.capacity,vehicleLevel:vehicle.level,riderLevel,speedRelativeToStarter:effects.speedRelativeToStarter,incomeFactor:effects.incomeFactor,riderIncomeFactor:1,fixedServiceReduction:0};
}
function fleetSlotTerms(id:string,vehicle:V2Vehicle,rider:V2Rider):V2SlotContractTerms {
 const effects=slotVehicleEffects(vehicle),training=slotRiderEffects(rider.id,rider.level);
 return {version:'slots-v1',profileId:V2_SLOT_PROFILE_ID,pricePolicyId:'slots-fleet-v1',effectPolicyId:V2_SLOT_EFFECT_POLICY,load:slotLoadForOrderId(id),capacity:effects.capacity,vehicleLevel:vehicle.level,riderLevel:rider.level,
 speedRelativeToStarter:effects.speedRelativeToStarter,incomeFactor:effects.incomeFactor,riderIncomeFactor:training.incomeFactor,fixedServiceReduction:training.fixedServiceReduction};
}
export function validateSlotDeliveryQuote(q:V2DeliveryQuote,state:Readonly<V2EconomyState>):void {
 check(object(q)&&identity(q.id)&&q.configId===V2_SLOT_PROFILE_ID&&!('weightKg' in q)&&int(q.mapId,1,5)&&int(q.incomeCents)&&int(q.heroOrderOrdinal,1)&&int(q.vehicleLevel,1,30)&&int(q.heroCompletedAtAcceptance)&&q.heroCompletedAtAcceptance<=state.heroCompletedOrders&&q.heroOrderOrdinal>q.heroCompletedAtAcceptance,'格子合同身份无效');
 check(q.kind==='ordinary'||q.kind==='special');
 if('vehicleRef' in q)validateEmergencyRef(q,state);else check(identity(q.vehicleId),'实车合同缺少车辆身份');
 const v='vehicleRef' in q?emergencyVehicle():state.vehicles.find(v=>v.id===q.vehicleId);check(v&&q.vehicleLevel<=v.level);
 const terms=contractTerms(q);check(terms.version==='slots-v1'&&sameV2ContractTerms(terms,heroSlotTerms(q.id,q.kind,{...v,level:q.vehicleLevel},state.riders[0].level)));
 const accepted=q.heroCompletedAtAcceptance,expectedXp=accepted<C.intro.safeOrders?1:getPlayerIncomeMultiplier(accepted*10<50?1:getExperienceLevel(accepted*10+50));
 check(q.incomeFactor===terms.incomeFactor&&q.xpMultiplier===expectedXp);
 if(q.kind==='special'){check(!('ordinaryPricing' in q)&&int(q.specialCoins,100,150)&&q.incomeCents===q.specialCoins*100);return;}
 check(Object.prototype.propertyIsEnumerable.call(q,'ordinaryPricing'),'格子普通合同缺少可信距离');const p=q.ordinaryPricing;
 check(pricingRecord(p)&&Reflect.ownKeys(p).length===2&&Object.prototype.propertyIsEnumerable.call(p,'version')&&Object.prototype.propertyIsEnumerable.call(p,'deliveryMetres')&&p.version===V2_SLOT_PRICE_POLICY&&int(p.deliveryMetres,1));
 check(q.incomeCents===slotOrdinaryIncomeCents(q.mapId,terms.incomeFactor,expectedXp,accepted,p.deliveryMetres),'格子合同金额不匹配');
}
export function validateSlotFleetQuote(q:V2FleetQuote,state:Readonly<V2EconomyState>):void {
 check(object(q)&&identity(q.id)&&!('vehicleRef' in q)&&!('weightKg' in q)&&!('capacityKg' in q)&&int(q.mapId,1,5)&&int(q.incomeCents)&&int(q.vehicleLevel,1,30)&&int(q.riderLevel,1,30));
 const v=state.vehicles.find(v=>v.id===q.vehicleId),r=state.riders.find(r=>r.id===q.riderId&&r.id!=='hero');check(v&&r&&q.vehicleLevel<=v.level&&q.riderLevel<=r.level);
 const effects=slotVehicleEffects({...v,level:q.vehicleLevel}),training=slotRiderEffects(r.id,q.riderLevel),terms=contractTerms(q);
 check(terms.version==='slots-v1'&&sameV2ContractTerms(terms,fleetSlotTerms(q.id,{...v,level:q.vehicleLevel},{...r,level:q.riderLevel})));
 check(q.speedRelativeToStarter===effects.speedRelativeToStarter&&q.baseIncomeFactor===training.baseIncomeFactor&&q.fixedServiceReduction===training.fixedServiceReduction&&q.incomeCents===Math.round(slotMapBaseIncomeCents(q.mapId)*effects.incomeFactor*training.incomeFactor));
}
export function validateOrdinaryPricingQuote(q:V2DeliveryQuote,state:Readonly<V2EconomyState>):void {
 if('terms' in q){const terms=contractTerms(q);if(terms.version==='slots-v1'){validateSlotDeliveryQuote(q,state);return;}validateLegacyOrdinaryPricingQuote(legacyQuotePayload(q),state);return;}
 validateLegacyOrdinaryPricingQuote(q,state);
}
/** Common invariants reuse the complete legacy validator; only new quotes use the new evaluator. */
export function validateV2EconomySnapshot(value:unknown):asserts value is V2EconomySnapshot {
 check(object(value)&&object(value.state));const s=value.state as unknown as V2EconomyState;
 check(Array.isArray(s.activeQuotes)&&Array.isArray(s.fleetQuotes));
 if(value.version!==3)check(!('heroEmergencyLoan' in s)&&[...s.activeQuotes,...s.fleetQuotes].every(q=>object(q)&&!('vehicleRef' in q)),'旧容器不能包含借车来源');
 if(value.version===1){
  check([...s.activeQuotes,...s.fleetQuotes].every(q=>object(q)&&!('terms' in q)&&!('load' in q)&&!('occupiedSlots' in q)));
  validateLegacyV2EconomySnapshot(value);return;
 }
 check(value.format==='county-v2-economy'&&(value.version===2||value.version===3)&&value.configId===V2_SLOT_PROFILE_ID,'经济配置版本不受支持');
 if(value.version===3){const loan=s.heroEmergencyLoan;check(object(loan)&&Reflect.ownKeys(loan).length===3&&['policyId','sequence','active'].every(k=>Object.prototype.propertyIsEnumerable.call(loan,k))&&loan.policyId===V2_HERO_EMERGENCY_POLICY&&int(loan.sequence,1)&&typeof loan.active==='boolean','借车记录无效');check(!loan.active||Array.isArray(s.riders)&&s.riders[0]?.vehicleId===null,'借车期间不能装备实车');}
 const activeLegacy:V2DeliveryQuote[]=[],fleetLegacy:V2FleetQuote[]=[],ids=new Set<string>();
 for(const q of [...s.activeQuotes,...s.fleetQuotes]){check(object(q)&&identity(q.id)&&!ids.has(q.id)&&Array.isArray(s.settledOrderIds)&&!s.settledOrderIds.includes(q.id));ids.add(q.id);contractTerms(q);}
 for(const q of s.activeQuotes){if(contractTerms(q).version==='slots-v1')validateSlotDeliveryQuote(q,s);else {check(!('load' in q)&&!('occupiedSlots' in q));activeLegacy.push(legacyQuotePayload(q));}}
 for(const q of s.fleetQuotes){if(contractTerms(q).version==='slots-v1')validateSlotFleetQuote(q,s);else {check(!('load' in q)&&!('occupiedSlots' in q));fleetLegacy.push(legacyQuotePayload(q));}}
 check(JSON.stringify(s.activeQuote)===JSON.stringify(s.activeQuotes[0]||null));
 const {heroEmergencyLoan,...realState}=s;
 const projection={...value,version:1,configId:V2_CONFIG_ID,state:{...realState,activeQuotes:activeLegacy,activeQuote:activeLegacy[0]||null,fleetQuotes:fleetLegacy}};
 validateLegacyV2EconomySnapshot(projection);
 check(s.activeQuotes.every(q=>q.mapId===s.selectedMapId&&('vehicleRef' in q?heroEmergencyLoan?.active&&q.vehicleRef?.loanSequence===heroEmergencyLoan.sequence:!heroEmergencyLoan?.active&&q.vehicleId===s.riders[0].vehicleId)),'主角活动合同车辆来源不一致');
 if(s.activeQuotes.length){check(!s.activeQuotes.some(q=>q.kind==='special')||s.activeQuotes.length===1);const terms=s.activeQuotes.map(contractTerms);check(terms.every(t=>t.version===terms[0].version));
  check(s.activeQuotes.every(q=>JSON.stringify(q.vehicleRef)===JSON.stringify(s.activeQuotes[0].vehicleRef)&&q.vehicleId===s.activeQuotes[0].vehicleId),'批次车辆来源混合');
  if(terms[0].version==='slots-v1')check(fitsV2Capacity(terms.map(t=>(t as V2SlotContractTerms).load),terms[0].capacity));
 }
}
function slotPricingById(orders:readonly {id:string;kind:'ordinary'|'special'}[],byId:V2OrdinaryPricingById):V2OrdinaryPricingById {
 check(pricingRecord(byId)&&orders.every(o=>object(o)&&identity(o.id)&&(o.kind==='ordinary'||o.kind==='special')));const ordinary=orders.filter(o=>o.kind==='ordinary'),keys=Reflect.ownKeys(byId);
 check(keys.length===ordinary.length&&keys.every(key=>typeof key==='string'&&ordinary.some(o=>o.id===key)));
 const result:Record<string,{deliveryMetres:number}>=Object.create(null);
 for(const o of ordinary){check(Object.prototype.hasOwnProperty.call(byId,o.id));const p=byId[o.id];check(pricingRecord(p)&&Reflect.ownKeys(p).length===1&&Object.prototype.hasOwnProperty.call(p,'deliveryMetres'));result[o.id]={deliveryMetres:quantizeOrdinaryDeliveryMetres(p.deliveryMetres)};}
 return result;
}
function ordinaryIncomeCents(s:V2EconomyState,vehicle:V2Vehicle):number {
 const xpMultiplier=s.heroCompletedOrders<C.intro.safeOrders?1:getPlayerIncomeMultiplier(s.heroExperience<50?1:getExperienceLevel(s.heroExperience+50));
 return Math.round(C.maps[s.selectedMapId-1].ordinaryBaseFee*100*vehicleEffects(vehicle).incomeFactor*xpMultiplier);
}

/** Pure economic commands. No storage, clocks, random rewards, map rendering or route mutation. */
export class V2EconomySession {
 private snapshot:V2EconomySnapshot;
 constructor(loadProfile:'kg-v1'|'slots-v1'='kg-v1'){check(loadProfile==='kg-v1'||loadProfile==='slots-v1');const cash=loadProfile==='slots-v1'?V2_SLOT_START_CENTS:C.startCoins*100;this.snapshot={format:'county-v2-economy',version:loadProfile==='slots-v1'?2:1,configId:loadProfile==='slots-v1'?V2_SLOT_PROFILE_ID:V2_CONFIG_ID,state:{ledger:createLedger(cash,'initial'),cashCents:cash,heroCompletedOrders:0,heroExperience:0,hireCount:0,nextVehicleId:1,riders:[{id:'hero',level:1,vehicleId:'starter-1'}],vehicles:[{id:'starter-1',modelId:'starter',level:1}],ownedMapIds:[1],selectedMapId:1,npcCompletedOrders:0,heroCompletionEvents:[],fleetQuotes:[],activeQuotes:[],settledOrderIds:[],activeQuote:null,lastReceipt:null}};}
 static restore(serialized:string):V2EconomySession {const raw:unknown=JSON.parse(serialized);validateV2EconomySnapshot(raw);const session=new V2EconomySession();session.snapshot=raw;return session;}
 /** Complete validation of private authority; no serialization, publication or callback. */
 assertValid():void {validateV2EconomySnapshot(this.snapshot);}
 /** Atomically restores a validated draft; performs no storage write. */
 replaceFrom(serialized:string):void {const restored=V2EconomySession.restore(serialized);this.snapshot=restored.snapshot;}
 get state():Readonly<V2EconomyState>{return clone(this.snapshot.state);}
 get usesSlots():boolean{return this.snapshot.configId===V2_SLOT_PROFILE_ID;}
 get schemaVersion():V2EconomySnapshot['version'] {return this.snapshot.version;}
 /** Read validated private authority, never a full snapshot; all returned objects are detached. */
 get hasEquippedVehicle():boolean {return this.snapshot.state.riders[0].vehicleId!==null||this.snapshot.state.heroEmergencyLoan?.active===true;}
 /** Owned car that the hero can equip, excluding NPC assignments and unpaid old contracts. */
 get hasRecoverableHeroVehicle():boolean {return hasRecoverableHeroVehicle(this.snapshot.state);}
 get reclaimableHeroVehicleIds():readonly string[] {return reclaimableHeroVehicleIds(this.snapshot.state);}
 get minimumVehiclePurchaseCents():number {return Math.min(...C.vehicles.map(v=>slotVehiclePurchaseQuote(v.id).costCents));}
 get nextBatchEffects():V2SlotVehicleEffects|null {
  const s=this.snapshot.state,v=s.heroEmergencyLoan?.active?emergencyVehicle():s.vehicles.find(v=>v.id===s.riders[0].vehicleId);return v?slotVehicleEffects(v):null;
 }
 deliveryEffectProjection(quoteId:string|null):V2DeliveryEffects|null {
  const s=this.snapshot.state;
  const quote=quoteId===null?null:s.activeQuotes.find(q=>q.id===quoteId);check(quoteId===null||quote,'当前配送效果合同不一致');
  const terms=quote?.terms;
  if(terms?.version==='slots-v1')return {profileId:terms.profileId,speedRelativeToStarter:terms.speedRelativeToStarter,incomeFactor:terms.incomeFactor,capacity:{version:'slots-v1',capacitySlots:terms.capacity.capacitySlots}};
  const v=s.vehicles.find(v=>v.id===s.riders[0].vehicleId);
  if(quote){check(v,'旧主角合同车辆丢失');const legacy=vehicleEffects(v);return {profileId:V2_CONFIG_ID,speedRelativeToStarter:legacy.speedRelativeToStarter,incomeFactor:legacy.incomeFactor,capacity:{version:'kg-v1',capacityKg:legacy.capacityKg}};}
  const current=this.nextBatchEffects;return current?{profileId:V2_SLOT_PROFILE_ID,speedRelativeToStarter:current.speedRelativeToStarter,incomeFactor:current.incomeFactor,capacity:current.capacity}:null;
 }
 vehicleEffectProjection(vehicleId:string):V2SlotVehicleEffects|null {
  const v=this.snapshot.state.vehicles.find(v=>v.id===vehicleId);return v?slotVehicleEffects(v):null;
 }
 riderEffectProjection(riderId:string):V2SlotRiderEffects|null {
  const r=this.snapshot.state.riders.find(r=>r.id===riderId&&r.id!=='hero');return r?slotRiderEffects(r.id,r.level):null;
 }
 /** Promotion follows full legacy validation; no cash, levels, prices or ledger entries are manufactured. */
 enableSlots():void {
  if(this.usesSlots)return;validateV2EconomySnapshot(this.snapshot);const next=clone(this.snapshot);
  next.state.activeQuotes=next.state.activeQuotes.map(wrapLegacyQuote);next.state.activeQuote=next.state.activeQuotes[0]||null;
  next.state.fleetQuotes=next.state.fleetQuotes.map(wrapLegacyQuote);next.version=2;next.configId=V2_SLOT_PROFILE_ID;
  validateV2EconomySnapshot(next);this.snapshot=next;
 }
 /** Local economic transition. Fleet owns the zero-quota aggregate check. */
 beginHeroEmergencyLoan(expectedSequence:number):number {
  const s=this.snapshot.state,sequence=s.heroEmergencyLoan?.sequence??0;this.idle();
  check(int(expectedSequence)&&expectedSequence===sequence&&!s.heroEmergencyLoan?.active,'借车请求重复或序号已过期');
  check(s.riders[0].vehicleId===null&&s.vehicles.length>0&&reclaimableHeroVehicleIds(s).length===0,'请先取回可用实车');
  check(s.cashCents<this.minimumVehiclePurchaseCents,'余额足够购车，请正常购车');check(int(sequence+1,1),'借车序号超出范围');
  this.enableSlots();const next=clone(this.snapshot);next.version=3;next.state.heroEmergencyLoan={policyId:V2_HERO_EMERGENCY_POLICY,sequence:sequence+1,active:true};
  validateV2EconomySnapshot(next);this.snapshot=next;return sequence+1;
 }
 finishHeroEmergencyLoan(loanSequence:number,vehicleId:string):void {
  const s=this.snapshot.state,loan=s.heroEmergencyLoan;this.idle();
  check(loan?.active&&int(loanSequence,1)&&loanSequence===loan.sequence,'归还请求重复或借车序号已过期');
  check(identity(vehicleId)&&reclaimableHeroVehicleIds(s).includes(vehicleId),'实车不存在或仍有未付旧合同');
  this.transact(0,d=>{for(const rider of d.riders)if(rider.id!=='hero'&&rider.vehicleId===vehicleId)rider.vehicleId=null;d.riders[0].vehicleId=vehicleId;d.heroEmergencyLoan!.active=false;});
 }
 vehicleUpgradePrice(id:string){const v=this.snapshot.state.vehicles.find(v=>v.id===id);check(v,'车辆不存在');return v.level===30?null:this.usesSlots?slotVehicleUpgradeQuote(v):vehicleUpgradeQuote(v);}
 riderUpgradePrice(id:string){const r=this.snapshot.state.riders.find(r=>r.id===id);check(r&&r.id!=='hero','人物无效');return r.level===30?null:this.usesSlots?slotRiderUpgradeQuote(id,r.level):riderUpgradeQuote(id,r.level);}
 /** Scalar event progress only; avoids cloning the wallet to check pending replenishment. */
 get heroCompletionEventCount():number {return this.snapshot.state.heroCompletionEvents.length;}
 serialize():string{return JSON.stringify(this.snapshot);}
 setLedgerContext(context:V2LedgerContext|null):void {validateLedgerContext(context);this.snapshot.state.ledgerContext=clone(context);}
 ledgerSummary(query:V2LedgerQuery){const s=this.snapshot.state,report=summarizeLedger(s.ledger,query);return {...report,reconciliation:{...report.reconciliation,currentCashCents:s.cashCents,balanced:report.reconciliation.expectedCashCents===s.cashCents}};}
 private record(s:V2EconomyState,category:V2LedgerCategory,amountCents:number,detail:V2LedgerDetail={},id?:string):void {appendLedger(s.ledger,{id,category,amountCents,detail},s.ledgerContext||null);}
 get nextHirePriceCents():number|null{return this.usesSlots?slotNextHirePriceCents(this.snapshot.state.riders):cheapestUnhiredRider(this.snapshot.state.riders)?.priceCents??null;}
 private idle():void {check(!this.snapshot.state.activeQuote,'配送中请先完成订单');}
 /** Historical module compile surface only; current snapshots reject legacy checkpoints. */
 get hasPendingLegacyTrip():boolean {return false;}
 private transact(cost:number,change:(draft:V2EconomyState)=>void,category?:V2LedgerCategory,detail:V2LedgerDetail={},allowDuringHero=false):void {
  if(!allowDuringHero)this.idle();check(int(cost),'金额超出安全范围');check(this.snapshot.state.cashCents>=cost,'余额不足');const next=clone(this.snapshot);next.state.cashCents-=cost;change(next.state);if(cost>0){check(category,'账目类别缺失');this.record(next.state,category,-cost,detail);}validateV2EconomySnapshot(next);this.snapshot=next;
 }
 buyVehicle(modelId:number):string {check(int(modelId,1,10),'车型无效');const id=`v2-vehicle-${this.snapshot.state.nextVehicleId}`;
  this.transact(this.usesSlots?slotVehiclePurchaseQuote(modelId).costCents:C.vehicles[modelId-1].price*100,s=>{s.vehicles.push({id,modelId,level:1});s.nextVehicleId++;},'vehicle_purchase',{vehicleId:id,modelId},this.usesSlots);return id;
 }
 hireRider(id:string):void {check(/^npc-([1-9]|[12]\d|30)$/.test(id),'人物无效');check(!this.snapshot.state.riders.some(r=>r.id===id),'人物已招募');const price=this.usesSlots?slotRiderHireQuote(id).costCents:riderHireQuote(id).priceCents;this.transact(price,s=>{s.riders.push({id,level:1,vehicleId:null});s.hireCount++;},'rider_hire',{riderId:id},this.usesSlots);}
 assignVehicle(riderId:string,vehicleId:string|null):void {
  const s=this.snapshot.state;check(s.riders.some(r=>r.id===riderId),'人物未招募');check(vehicleId===null||s.vehicles.some(v=>v.id===vehicleId),'车辆不存在');
  check(riderId!=='hero'||!s.heroEmergencyLoan?.active,'请使用取回实车并归还应急车');
  check(vehicleId===null||!s.fleetQuotes.some(q=>q.vehicleId===vehicleId&&q.riderId!==riderId),'车辆仍执行旧批次');
  check(vehicleId===null||!s.riders.some(r=>r.id!==riderId&&r.vehicleId===vehicleId),'车辆已被其他人物占用');
  this.transact(0,s=>{s.riders.find(r=>r.id===riderId)!.vehicleId=vehicleId;if(riderId!=='hero'&&vehicleId!==null)check(hasRecoverableHeroVehicle(s),'请为主角保留一辆可用车辆');},undefined,{},this.usesSlots&&riderId!=='hero');
 }
 buyMap(id:number):void {check(int(id,1,5),'地图无效');check(!this.snapshot.state.ownedMapIds.includes(id),'地图已拥有');this.transact(this.usesSlots?slotMapPurchaseQuote(id).costCents:C.maps[id-1].price*100,s=>{s.ownedMapIds.push(id);},'map_purchase',{mapId:id});}
 selectMap(id:number):void {check(this.snapshot.state.ownedMapIds.includes(id),'地图未购买');this.transact(0,s=>{s.selectedMapId=id;});}
 upgradeVehicle(id:string):void {
  const vehicle=this.snapshot.state.vehicles.find(v=>v.id===id);check(vehicle,'车辆不存在');check(vehicle.level<30,'车辆已满级');
  const cost=this.vehicleUpgradePrice(id)!.costCents;
  check(!this.snapshot.state.activeQuotes.some(q=>q.vehicleId===id),'主角配送中不能升级当前车辆');
  this.transact(cost,s=>{s.vehicles.find(v=>v.id===id)!.level++;},'vehicle_upgrade',{vehicleId:id,level:vehicle.level+1},this.usesSlots);
 }
 upgradeRider(id:string):void {const rider=this.snapshot.state.riders.find(r=>r.id===id);check(rider,'人物未招募');check(rider.level<30,'人物已满级');check(id!=='hero','主角通过配送获得经验等级');
  this.transact(this.riderUpgradePrice(id)!.costCents,s=>{s.riders.find(r=>r.id===id)!.level++;},'rider_upgrade',{riderId:id,level:rider.level+1},this.usesSlots);
 }
 /** Creates immutable contracts; routing/arrival must still be confirmed by the caller. */
 acceptOrdinary(id:string):V2DeliveryQuote {return this.acceptBatch([{id,kind:'ordinary',weightKg:1}])[0];}
 acceptBatch(orders:{id:string;kind:'ordinary'|'special';weightKg:number;specialCoins?:number}[],ordinaryPricingById?:V2OrdinaryPricingById):V2DeliveryQuote[] {
  check(!this.usesSlots,'新批次必须显式使用整数容量合同');
  this.idle();check(Array.isArray(orders)&&orders.length>0,'空订单批次');const s=this.snapshot.state,vehicle=s.vehicles.find(v=>v.id===s.riders[0].vehicleId);check(vehicle,'主角尚未配车');
  const pricingById=normalizeOrdinaryPricingById(orders,ordinaryPricingById);
  const ids=new Set<string>();let weight=0;const effects=vehicleEffects(vehicle),xpMultiplier=s.heroCompletedOrders<C.intro.safeOrders?1:getPlayerIncomeMultiplier(s.heroExperience<50?1:getExperienceLevel(s.heroExperience+50));
  const quotes=orders.map((o,i)=>{check(identity(o.id)&&!ids.has(o.id)&&!s.settledOrderIds.includes(o.id)&&!s.fleetQuotes.some(q=>q.id===o.id),'订单编号无效或重复');ids.add(o.id);check(typeof o.weightKg==='number'&&Number.isFinite(o.weightKg)&&o.weightKg>0,'订单重量无效');weight+=o.weightKg;
   check(o.kind==='ordinary'||o.kind==='special','订单类型无效');if(o.kind==='special')check(orders.length===1&&int(o.specialCoins,100,150),'专送必须独占且报价100–150');
   const pricing:V2OrdinaryPricing|undefined=o.kind==='ordinary'&&pricingById!==undefined?{version:V2_ORDINARY_PRICING.version,deliveryMetres:pricingById[o.id].deliveryMetres}:undefined;
   const q:V2DeliveryQuote={id:o.id,configId:V2_CONFIG_ID,incomeCents:o.kind==='special'?o.specialCoins!*100:pricing?ordinaryEffortIncomeCents(s.selectedMapId,effects.incomeFactor,xpMultiplier,s.heroCompletedOrders,o.weightKg,pricing.deliveryMetres):ordinaryIncomeCents(s,vehicle),heroOrderOrdinal:s.heroCompletedOrders+i+1,kind:o.kind,mapId:s.selectedMapId,vehicleId:vehicle.id,weightKg:o.weightKg,vehicleLevel:vehicle.level,incomeFactor:effects.incomeFactor,xpMultiplier,heroCompletedAtAcceptance:s.heroCompletedOrders};if(o.kind==='special')q.specialCoins=o.specialCoins;if(pricing)q.ordinaryPricing=pricing;return q;
  });check(weight<=effects.capacityKg,'订单超载');const next=clone(this.snapshot);next.state.activeQuotes=quotes;next.state.activeQuote=quotes[0];validateV2EconomySnapshot(next);this.snapshot=next;return clone(quotes);
 }
 acceptSlotBatch(orders:readonly {id:string;kind:'ordinary'|'special';specialCoins?:number}[],byId:V2OrdinaryPricingById):V2DeliveryQuote[] {
  this.idle();check(this.usesSlots&&Array.isArray(orders)&&orders.length>0,'新格子批次无效');const s=this.snapshot.state,loan=s.heroEmergencyLoan,owned=s.vehicles.find(v=>v.id===s.riders[0].vehicleId),v=loan?.active?emergencyVehicle():owned;check(v,'主角尚未配车');
  check(!loan?.active||reclaimableHeroVehicleIds(s).length===0,'请先取回实车并归还应急车');
  const pricing=slotPricingById(orders,byId),effects=slotVehicleEffects(v),seen=new Set<string>();
  const xp=s.heroCompletedOrders<C.intro.safeOrders?1:getPlayerIncomeMultiplier(s.heroExperience<50?1:getExperienceLevel(s.heroExperience+50));
  const quotes=orders.map((o,i):V2DeliveryQuote=>{
   check(identity(o.id)&&!seen.has(o.id)&&!s.settledOrderIds.includes(o.id)&&!s.fleetQuotes.some(q=>q.id===o.id));seen.add(o.id);
   check(o.kind==='ordinary'||o.kind==='special');if(o.kind==='special')check(orders.length===1&&int(o.specialCoins,100,150));
   const source:Pick<V2DeliveryQuote,'vehicleRef'|'vehicleId'>=loan?.active?{vehicleRef:{kind:'emergency',loanSequence:loan.sequence,policyId:V2_HERO_EMERGENCY_POLICY}}:{vehicleId:owned!.id};
   const q:V2DeliveryQuote={id:o.id,configId:V2_SLOT_PROFILE_ID,kind:o.kind,mapId:s.selectedMapId,...source,vehicleLevel:v.level,incomeFactor:effects.incomeFactor,xpMultiplier:xp,heroCompletedAtAcceptance:s.heroCompletedOrders,heroOrderOrdinal:s.heroCompletedOrders+i+1,
   incomeCents:o.kind==='special'?o.specialCoins!*100:slotOrdinaryIncomeCents(s.selectedMapId,effects.incomeFactor,xp,s.heroCompletedOrders,pricing[o.id].deliveryMetres),terms:heroSlotTerms(o.id,o.kind,v,s.riders[0].level)};
   if(o.kind==='special')q.specialCoins=o.specialCoins;else q.ordinaryPricing={version:V2_SLOT_PRICE_POLICY,deliveryMetres:pricing[o.id].deliveryMetres};return q;
  });check(fitsV2Capacity(quotes.map(q=>(q.terms as V2SlotContractTerms).load),effects.capacity),'订单超载');
  const next=clone(this.snapshot);next.state.activeQuotes=quotes;next.state.activeQuote=quotes[0];validateV2EconomySnapshot(next);this.snapshot=next;return clone(quotes);
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
  check(!this.usesSlots,'新NPC批次必须使用整数容量合同');
  const s=this.snapshot.state,r=s.riders.find(r=>r.id===riderId&&r.id!=='hero'),v=s.vehicles.find(v=>v.id===r?.vehicleId);check(r&&v,'NPC未配车');
  check(!s.fleetQuotes.some(q=>q.riderId===riderId||q.vehicleId===v.id),'NPC或车辆仍有旧批次');check(ids.length>0&&ids.length===weights.length&&new Set(ids).size===ids.length,'NPC批次无效');const effects=vehicleEffects(v),rider=riderEffects(riderId,r.level);
  check(this.hasRecoverableHeroVehicle,'请为主角保留一辆可用车辆');
  check(weights.every(w=>int(w,1))&&weights.reduce((a,b)=>a+b,0)<=effects.capacityKg,'NPC订单超载');
  for(const id of ids)check(identity(id)&&!s.settledOrderIds.includes(id)&&!s.activeQuotes.some(q=>q.id===id)&&!s.fleetQuotes.some(q=>q.id===id),'订单编号无效或重复');
  const quotes=ids.map((id,i)=>({id,riderId,vehicleId:v.id,vehicleLevel:v.level,riderLevel:r.level,mapId:s.selectedMapId,weightKg:weights[i],baseIncomeFactor:rider.baseIncomeFactor,fixedServiceReduction:rider.fixedServiceReduction,incomeCents:Math.round(C.maps[s.selectedMapId-1].ordinaryBaseFee*100*effects.incomeFactor*rider.incomeFactor),capacityKg:effects.capacityKg,speedRelativeToStarter:effects.speedRelativeToStarter}));
  const next=clone(this.snapshot);next.state.fleetQuotes.push(...quotes);validateV2EconomySnapshot(next);this.snapshot=next;return clone(quotes);
 }
 registerSlotFleetOrders(riderId:string,ids:readonly string[]):V2FleetQuote[] {
  check(this.usesSlots);const s=this.snapshot.state,r=s.riders.find(r=>r.id===riderId&&r.id!=='hero'),v=s.vehicles.find(v=>v.id===r?.vehicleId);check(r&&v,'NPC未配车');
  check(!s.fleetQuotes.some(q=>q.riderId===riderId||q.vehicleId===v.id),'NPC或车辆仍有旧批次');check(ids.length>0&&new Set(ids).size===ids.length);
  check(this.hasRecoverableHeroVehicle,'请为主角保留一辆可用车辆');
  const effects=slotVehicleEffects(v),training=slotRiderEffects(riderId,r.level);
  check(fitsV2Capacity(ids.map(slotLoadForOrderId),effects.capacity),'NPC订单超载');
  for(const id of ids)check(identity(id)&&!s.settledOrderIds.includes(id)&&!s.activeQuotes.some(q=>q.id===id)&&!s.fleetQuotes.some(q=>q.id===id));
  const quotes:V2FleetQuote[]=ids.map(id=>({id,riderId,vehicleId:v.id,vehicleLevel:v.level,riderLevel:r.level,mapId:s.selectedMapId,incomeCents:Math.round(slotMapBaseIncomeCents(s.selectedMapId)*effects.incomeFactor*training.incomeFactor),speedRelativeToStarter:effects.speedRelativeToStarter,baseIncomeFactor:training.baseIncomeFactor,fixedServiceReduction:training.fixedServiceReduction,terms:fleetSlotTerms(id,v,r)}));
  const next=clone(this.snapshot);next.state.fleetQuotes.push(...quotes);validateV2EconomySnapshot(next);this.snapshot=next;return clone(quotes);
 }
 settleFleetOrder(id:string):number {
  const s=this.snapshot.state;if(s.settledOrderIds.includes(id))return 0;const q=s.fleetQuotes.find(q=>q.id===id);check(q,'NPC订单未签约');
  const next=clone(this.snapshot);next.state.cashCents+=q.incomeCents;this.record(next.state,'npc_delivery',q.incomeCents,{orderId:id,riderId:q.riderId,vehicleId:q.vehicleId,mapId:q.mapId},`order:${id}`);next.state.npcCompletedOrders++;next.state.settledOrderIds.push(id);next.state.fleetQuotes=next.state.fleetQuotes.filter(q=>q.id!==id);validateV2EconomySnapshot(next);this.snapshot=next;return q.incomeCents;
 }
}
