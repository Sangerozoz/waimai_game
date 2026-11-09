import { V2_SLOT_CONFIG as C } from './V2SlotEconomyConfig';
import { V2_CONFIG_ID as LEGACY_ID } from './V2EconomyConfig';
import { parseV2Capacity,parseV2Load } from './V2LoadRules';
import type { V2SlotLoad,V2SlotCapacity } from './V2LoadRules';

export const V2_SLOT_PROFILE_ID=C.profileId;
export const V2_SLOT_PRICE_POLICY='distance-effort-slots-v1';
export const V2_SLOT_EFFECT_POLICY='capacity-slots-effects-v1';
export const V2_SLOT_START_CENTS=C.startCoins*100;
export interface V2SlotContractTerms {
 version:'slots-v1';profileId:string;pricePolicyId:string;effectPolicyId:string;
 load:V2SlotLoad;capacity:V2SlotCapacity;vehicleLevel:number;riderLevel:number;
 speedRelativeToStarter:number;incomeFactor:number;riderIncomeFactor:number;fixedServiceReduction:number;
}
/** An opaque marker, not a reconstruction of historical legacy attributes. */
export interface V2LegacyContractTerms {version:'kg-v1';profileId:string;}
export type V2ContractTerms=V2SlotContractTerms|V2LegacyContractTerms;
export interface V2SlotVehicleEffects {
 profileId:typeof V2_SLOT_PROFILE_ID;capacity:V2SlotCapacity;capacitySlots:number;speedRelativeToStarter:number;incomeFactor:number;
}
export interface V2SlotRiderEffects {profileId:typeof V2_SLOT_PROFILE_ID;incomeFactor:number;baseIncomeFactor:number;fixedServiceReduction:number;}
export interface V2SlotUpgradeQuote {fromLevel:number;toLevel:number;costCents:number;profileId:typeof V2_SLOT_PROFILE_ID;}
function check(value:unknown):asserts value {if(!value)throw new Error('容量成长条款或参数无效');}
function levelRow(level:number){check(Number.isInteger(level)&&level>=1&&level<=C.levels.length);const row=C.levels[level-1];check(row.level===level);return row;}
function modelRow(modelId:number|'starter'|'legacy') {
 check(modelId!=='legacy');if(modelId==='starter')return C.starterVehicle;
 const model=C.vehicles.find(row=>row.id===modelId);check(model);return model;
}
function riderRow(riderId:string){const rider=C.riders.find(row=>row.id===riderId);check(rider);return rider;}

export function slotVehicleEffects(vehicle:{modelId:number|'starter'|'legacy';level:number}):V2SlotVehicleEffects {
 const row=levelRow(vehicle.level),model=modelRow(vehicle.modelId);
 const capacitySlots=vehicle.modelId==='starter'?row.starterCapacitySlots:row.vehicles.find(value=>value.modelId===vehicle.modelId)?.capacitySlots;
 check(typeof capacitySlots==='number'&&Number.isSafeInteger(capacitySlots)&&capacitySlots>0);
 return {profileId:V2_SLOT_PROFILE_ID,capacity:{version:'slots-v1',capacitySlots},capacitySlots,
 speedRelativeToStarter:model.speedRelativeToStarter*(1+row.vehicleSpeedBonus),incomeFactor:model.incomeFactor*(1+row.vehicleIncomeBonus)};
}
export function slotRiderEffects(riderId:string,level:number):V2SlotRiderEffects {
 const row=levelRow(level),rider=riderRow(riderId);
 return {profileId:V2_SLOT_PROFILE_ID,baseIncomeFactor:rider.baseIncomeFactor,incomeFactor:rider.baseIncomeFactor*(1+row.riderTrainingIncomeBonus),fixedServiceReduction:row.fixedServiceReduction};
}
export function slotVehicleUpgradeQuote(vehicle:{modelId:number|'starter'|'legacy';level:number}):V2SlotUpgradeQuote&{current:V2SlotVehicleEffects;next:V2SlotVehicleEffects;nextLevel:number} {
 const row=levelRow(vehicle.level);check(vehicle.level<C.levels.length);modelRow(vehicle.modelId);
 const next=levelRow(vehicle.level+1),currentModel=row.vehicles.find(value=>value.modelId===vehicle.modelId),nextModel=next.vehicles.find(value=>value.modelId===vehicle.modelId);
 check(vehicle.modelId==='starter'||currentModel&&nextModel);
 const cost=vehicle.modelId==='starter'?next.starterCumulativeUpgradeCoins-row.starterCumulativeUpgradeCoins:nextModel!.cumulativeUpgradeCoins-currentModel!.cumulativeUpgradeCoins;
 check(Number.isSafeInteger(cost)&&cost>0&&cost===(vehicle.modelId==='starter'?next.starterUpgradeCoins:nextModel!.upgradeCoins));
 return {fromLevel:row.level,toLevel:next.level,costCents:cost*100,profileId:V2_SLOT_PROFILE_ID,current:slotVehicleEffects(vehicle),next:slotVehicleEffects({...vehicle,level:next.level}),nextLevel:next.level};
}
export function slotRiderUpgradeQuote(riderId:string,level:number):V2SlotUpgradeQuote&{current:V2SlotRiderEffects;next:V2SlotRiderEffects;nextLevel:number} {
 riderRow(riderId);const row=levelRow(level);check(level<C.levels.length);const next=levelRow(level+1);
 const cost=next.riderCumulativeUpgradeCoins-row.riderCumulativeUpgradeCoins;
 check(Number.isSafeInteger(cost)&&cost>0&&cost===next.riderUpgradeCoins);
 return {fromLevel:row.level,toLevel:next.level,costCents:cost*100,profileId:V2_SLOT_PROFILE_ID,current:slotRiderEffects(riderId,row.level),next:slotRiderEffects(riderId,next.level),nextLevel:next.level};
}
export function slotRiderHireQuote(riderId:string){const row=riderRow(riderId);return {riderId:row.id,costCents:row.price*100};}
export function slotVehiclePurchaseQuote(modelId:number){const model=C.vehicles.find(row=>row.id===modelId);check(model);return {modelId:model.id,costCents:model.price*100};}
export function slotMapBaseIncomeCents(mapTier:number):number {const map=C.maps.find(row=>row.id===mapTier);check(map);return map.ordinaryBaseFee*100;}
export function slotMapPurchaseQuote(mapId:number){const map=C.maps.find(row=>row.id===mapId);check(map);return {mapId:map.id,costCents:map.price*100};}
export function slotNextHirePriceCents(owned:readonly {id:string}[]):number|null {const candidates=C.riders.filter(row=>!owned.some(r=>r.id===row.id));return candidates.length?Math.min(...candidates.map(row=>row.price*100)):null;}

/** Required, exact metadata; absence and an unknown unit never choose legacy. */
export function parseV2ContractTerms(raw:unknown):V2ContractTerms {
 check(raw&&typeof raw==='object'&&!Array.isArray(raw));const value=raw as Record<string,unknown>;
 if(value.version==='kg-v1'){
  check(Reflect.ownKeys(value).length===2&&Object.prototype.propertyIsEnumerable.call(value,'version')&&Object.prototype.propertyIsEnumerable.call(value,'profileId')&&value.profileId===LEGACY_ID);
  return {version:'kg-v1',profileId:LEGACY_ID};
 }
 const keys=['version','profileId','pricePolicyId','effectPolicyId','load','capacity','vehicleLevel','riderLevel','speedRelativeToStarter','incomeFactor','riderIncomeFactor','fixedServiceReduction'];
 check(Reflect.ownKeys(value).length===keys.length&&keys.every(key=>Object.prototype.propertyIsEnumerable.call(value,key)));
 check(value.version==='slots-v1');const version=value.version;
 const load=parseV2Load(value.load),capacity=parseV2Capacity(value.capacity);check(load.version===version&&capacity.version===version);
 check(value.profileId===V2_SLOT_PROFILE_ID);
 check(value.effectPolicyId===V2_SLOT_EFFECT_POLICY);
 const policies=[V2_SLOT_PRICE_POLICY,'slots-special-v1','slots-fleet-v1'];
 check(typeof value.pricePolicyId==='string'&&policies.includes(value.pricePolicyId));
 check(typeof value.vehicleLevel==='number'&&Number.isInteger(value.vehicleLevel)&&value.vehicleLevel>=1&&value.vehicleLevel<=30);
 check(typeof value.riderLevel==='number'&&Number.isInteger(value.riderLevel)&&value.riderLevel>=1&&value.riderLevel<=30);
 check(typeof value.speedRelativeToStarter==='number'&&Number.isFinite(value.speedRelativeToStarter)&&value.speedRelativeToStarter>0);
 check(typeof value.incomeFactor==='number'&&Number.isFinite(value.incomeFactor)&&value.incomeFactor>0);
 check(typeof value.riderIncomeFactor==='number'&&Number.isFinite(value.riderIncomeFactor)&&value.riderIncomeFactor>0);
 check(typeof value.fixedServiceReduction==='number'&&Number.isFinite(value.fixedServiceReduction)&&value.fixedServiceReduction>=0&&value.fixedServiceReduction<1);
 return {version,profileId:value.profileId as string,pricePolicyId:value.pricePolicyId,effectPolicyId:value.effectPolicyId as string,
 load,capacity,vehicleLevel:value.vehicleLevel,riderLevel:value.riderLevel,speedRelativeToStarter:value.speedRelativeToStarter,
 incomeFactor:value.incomeFactor,riderIncomeFactor:value.riderIncomeFactor,fixedServiceReduction:value.fixedServiceReduction};
}
export function sameV2ContractTerms(left:V2ContractTerms,right:V2ContractTerms):boolean {
 const a=parseV2ContractTerms(left),b=parseV2ContractTerms(right);
 return JSON.stringify(a)===JSON.stringify(b);
}
