import { V2SupplyId, V2_SUPPLY_CATALOG, V2_SUPPLY_REWARDS, supplyItem, emptySupplyInventory } from './V2SupplyCatalog';
import type { Fragility } from './GameConfig';
/** Pure, persisted hero-trip rules. No wall clock, storage or unseeded randomness. */
export type V2SupplyKind=V2SupplyId|'rest';
export type V2SupplySource='purchase'|'inventory'|'rest';
export type V2Damage='none'|'minor'|'moderate'|'severe';
export interface V2DeliveryOutcome {lateGameSeconds:number;damage:V2Damage}
export interface V2FinalSettlement extends V2DeliveryOutcome {baseIncomeCents:number;lateRetain:number;damageRetain:number;ratingDelta:number}
export function settleTripIncome(base:number,outcome:V2DeliveryOutcome){
 if(!Number.isSafeInteger(base)||base<0||!Number.isFinite(outcome.lateGameSeconds)||outcome.lateGameSeconds<0||!['none','minor','moderate','severe'].includes(outcome.damage))throw new Error('交付结果无效');
 const late=outcome.lateGameSeconds,li=late<=0?0:late<=300?1:late<=600?2:3,di=['none','minor','moderate','severe'].indexOf(outcome.damage);
 const lateRetain=[1,.95,.85,.75][li],damageRetain=[1,.9,.75,.5][di];
 return {incomeCents:Math.round(base*lateRetain*damageRetain),baseIncomeCents:base,lateRetain,damageRetain,lateGameSeconds:late,damage:outcome.damage,ratingDelta:li===0&&di===0?1:-Math.min(10,[0,1,3,5][li]+[0,1,3,5][di])};
}
export type V2FoodRiskContract=Readonly<{version:'food-risk-v1';foodId:string;fragility:Fragility}>;
export type V2FoodRiskById=Readonly<Record<string,V2FoodRiskContract>>;
export interface V2TripOrder {id:string;deadlineGameSeconds:number;picked:boolean;delivered:boolean;risk:number;draw:number;severityDraw:number;heldMetres:number;safe:boolean;food?:V2FoodRiskContract}
export interface V2AutoSupplyPolicy {enabled:boolean;budgetCents:number;spentCents:number;kind?:V2SupplyId;allowPaid:boolean;useInventory:boolean}
export interface V2AutoSupplyInput {enabled:boolean;budgetCents:number;kind?:V2SupplyId;allowPaid?:boolean;useInventory?:boolean}
export interface V2LegacyTripState {
 version:2;stamina:number;rating:number;gameSeconds:number;weather:'clear'|'rain'|'severe';seed:number;mapId:number;preference:'fast'|'main'|'smooth';blocked:boolean;
 orders:(V2TripOrder&{food?:never})[];supplySpentCents:number;
 batchAccounting:{orderIds:string[];supplySpentCentsStart:number;inventoryUsedStart:Record<V2SupplyId,number>;end?:{supplySpentCents:number;inventoryUsed:Record<V2SupplyId,number>}}|null;
 inventory:Record<V2SupplyId,number>;inventoryUsed:Record<V2SupplyId,number>;supplyGrants:{grantId:string;rewardId:string}[];
 action:{kind:V2SupplyKind;source:V2SupplySource;elapsedSeconds:number;durationSeconds:number;gameSeconds:number;restore:number;costCents:number}|null;
 autoSupplyPolicy:V2AutoSupplyPolicy;
}
export type V2TripState=V2LegacyTripState|(Omit<V2LegacyTripState,'version'|'orders'>&{version:3;orders:(V2TripOrder&{food:V2FoodRiskContract})[]});
const clone=<T>(s:T):T=>JSON.parse(JSON.stringify(s));
function check(v:unknown):asserts v {if(!v)throw new Error('体力行程状态无效');}
const finite=(v:number)=>Number.isFinite(v)&&v>=0;
const own=(value:object,key:string)=>Object.prototype.hasOwnProperty.call(value,key);
export function parseV2FoodRisk(raw:unknown):V2FoodRiskContract {
 check(raw&&typeof raw==='object'&&!Array.isArray(raw));
 check(Reflect.ownKeys(raw).length===3&&['version','foodId','fragility'].every(key=>Object.prototype.propertyIsEnumerable.call(raw,key)));
 const food=raw as Record<string,unknown>;
 check(food.version==='food-risk-v1'&&typeof food.foodId==='string'&&food.foodId.length>0&&typeof food.fragility==='string'&&['fragile','normal','durable'].indexOf(food.fragility)>=0);
 return {version:'food-risk-v1',foodId:food.foodId,fragility:food.fragility as Fragility};
}
const FOOD_DAMAGE_BASE:Readonly<Record<Fragility,Readonly<Record<'fast'|'main'|'smooth',number>>>>={fragile:{fast:.12,main:.06,smooth:.02},normal:{fast:.06,main:.03,smooth:.01},durable:{fast:.02,main:.01,smooth:0}};
export class V2TripRules {
 private s:V2TripState={version:2,stamina:100,rating:80,gameSeconds:0,weather:'clear',seed:1,mapId:1,preference:'fast',blocked:false,orders:[],supplySpentCents:0,batchAccounting:null,inventory:emptySupplyInventory(),inventoryUsed:emptySupplyInventory(),supplyGrants:[],action:null,autoSupplyPolicy:{enabled:false,budgetCents:0,spentCents:0,allowPaid:false,useInventory:false}};
 get state():V2TripState{return clone(this.s);}
 get roadTimeFactor(){return this.s.weather==='rain'?1.1:this.s.weather==='severe'?1.25:1;}
 private roll(){this.s.seed=(Math.imul(this.s.seed,1664525)+1013904223)>>>0;return this.s.seed/4294967296;}
 begin(mapId:number,tripId:number,orders:{id:string;fastestGameSeconds:number;heldMetres:number;safe:boolean}[],foodById?:V2FoodRiskById):void {
  check(!this.s.action&&Number.isInteger(mapId)&&mapId>=1&&mapId<=5&&Array.isArray(orders)&&orders.length>0);
  const classified=arguments.length>=4;let foods:Record<string,V2FoodRiskContract>|null=null;
  if(classified){
   check(foodById&&typeof foodById==='object'&&!Array.isArray(foodById)&&(Object.getPrototypeOf(foodById)===null||Object.getPrototypeOf(foodById)===Object.prototype));
   check(Number.isInteger(tripId)&&tripId>=0&&orders.every(o=>o&&typeof o.id==='string'&&o.id.length>0&&finite(o.fastestGameSeconds)&&finite(o.heldMetres)&&typeof o.safe==='boolean'));
   check(Reflect.ownKeys(foodById).length===orders.length&&new Set(orders.map(o=>o.id)).size===orders.length&&orders.every(o=>own(foodById,o.id)));
   foods=Object.create(null);for(const order of orders)foods![order.id]=parseV2FoodRisk(foodById[order.id]);
  }else check(this.s.version===2);
  this.s.seed=(tripId^0x79a75d31)>>>0;this.s.mapId=mapId;this.s.gameSeconds=0;this.s.blocked=this.s.stamina===0;
  this.s.batchAccounting={orderIds:orders.map(o=>o.id),supplySpentCentsStart:this.s.supplySpentCents,inventoryUsedStart:{...this.s.inventoryUsed}};
  const safe=orders.every(o=>o.safe),r=this.roll()*100;this.s.weather=safe?'clear':r<[0,1,2,3,5][mapId-1]?'severe':r<[5,11,17,23,30][mapId-1]?'rain':'clear';
  const nextOrders=orders.map(o=>({id:o.id,deadlineGameSeconds:o.fastestGameSeconds*this.roadTimeFactor+300,picked:false,delivered:false,risk:0,draw:this.roll(),severityDraw:this.roll(),heldMetres:Math.max(1,o.heldMetres),safe:o.safe}));
  this.s=foods?{...this.s,version:3,orders:nextOrders.map(o=>({...o,food:foods![o.id]}))}:{...this.s,version:2,orders:nextOrders};
 }
 choose(preference:'fast'|'main'|'smooth'){this.s.preference=preference;}
 configureAutoSupply(policy:V2AutoSupplyInput):void {
  check(typeof policy.enabled==='boolean'&&Number.isSafeInteger(policy.budgetCents)&&policy.budgetCents>=this.s.autoSupplyPolicy.spentCents&&(policy.kind===undefined||!!supplyItem(policy.kind))&&(policy.allowPaid===undefined||typeof policy.allowPaid==='boolean')&&(policy.useInventory===undefined||typeof policy.useInventory==='boolean'));
  this.s.autoSupplyPolicy={...policy,allowPaid:policy.allowPaid===true,useInventory:policy.useInventory===true,spentCents:this.s.autoSupplyPolicy.spentCents};
 }
 /** A task may submit only a reviewed reward key, never an arbitrary amount. */
 claimSupplyReward(grantId:string,rewardId:string):boolean {
  check(typeof grantId==='string'&&grantId.length>0&&grantId.length<=160);
  const previous=this.s.supplyGrants.find(g=>g.grantId===grantId);
  if(previous){check(previous.rewardId===rewardId);return false;}
  check(!this.s.supplyGrants.some(g=>g.rewardId===rewardId));
  const reward=V2_SUPPLY_REWARDS.find(r=>r.id===rewardId);check(reward&&reward.items.length>0);
  const quantities={...this.s.inventory};for(const item of reward.items){check(!!supplyItem(item.kind)&&Number.isSafeInteger(item.quantity)&&item.quantity>0&&Number.isSafeInteger(quantities[item.kind]+item.quantity));quantities[item.kind]+=item.quantity;}
  this.s.inventory=quantities;this.s.supplyGrants.push({grantId,rewardId});return true;
 }
 chooseAutoSupply(highestMapId:number,cashCents:number):{kind:V2SupplyId;source:'inventory'|'purchase'}|null {
  const p=this.s.autoSupplyPolicy;if(!p.enabled||this.s.action||this.s.stamina>=100)return null;
  const deficit=100-this.s.stamina;
  const available=V2_SUPPLY_CATALOG.filter(item=>item.unlockMapId<=highestMapId);
  // Prefer explicitly authorized inventory. Within each source minimize waste,
  // then maximize useful recovery, then prefer shorter actions and cheaper items.
  const rank=(a:typeof V2_SUPPLY_CATALOG[number],b:typeof V2_SUPPLY_CATALOG[number])=>Math.max(0,a.restore-deficit)-Math.max(0,b.restore-deficit)||Math.min(deficit,b.restore)-Math.min(deficit,a.restore)||a.durationSeconds-b.durationSeconds||a.costCents-b.costCents;
  const inventory=p.useInventory?available.filter(item=>this.s.inventory[item.id]>0).sort(rank)[0]:undefined;
  if(inventory)return {kind:inventory.id,source:'inventory'};
  const paid=p.allowPaid?available.filter(item=>item.costCents<=cashCents&&p.spentCents+item.costCents<=p.budgetCents).sort(rank)[0]:undefined;
  return paid?{kind:paid.id,source:'purchase'}:null;
 }
 startSupply(kind:V2SupplyKind,active:boolean,charge:(cents:number)=>void,automatic=false,source:'purchase'|'inventory'='purchase',highestMapId=1):void {
  check(!this.s.action&&this.s.stamina<100&&typeof active==='boolean'&&['purchase','inventory'].includes(source));
  const item=supplyItem(kind),rest=kind==='rest',p=this.s.autoSupplyPolicy;
  check(rest||!!item&&item.unlockMapId<=highestMapId);check(!rest||source==='purchase');
  const cost=rest||source==='inventory'?0:item!.costCents;
  if(automatic)check(p.enabled&&!rest&&(source==='inventory'?p.useInventory:p.allowPaid&&p.spentCents+cost<=p.budgetCents));
  if(source==='inventory')check(!!item&&this.s.inventory[item.id]>0&&Number.isSafeInteger(this.s.inventoryUsed[item.id]+1));
  check(Number.isSafeInteger(this.s.supplySpentCents+cost));
  // All validation precedes the single charge. Action keeps its source/cost across reload.
  if(cost>0)charge(cost);
  if(source==='inventory'){this.s.inventory[item!.id]--;this.s.inventoryUsed[item!.id]++;}
  if(automatic)p.spentCents+=cost;this.s.supplySpentCents+=cost;
  this.s.action={kind,source:rest?'rest':source,costCents:cost,elapsedSeconds:0,durationSeconds:rest?active?10:20:item!.durationSeconds,gameSeconds:rest?active?600:0:item!.gameSeconds,restore:rest?active?20:100:item!.restore};
 }
 advanceSupply(seconds:number,advanceTripClock:boolean=true):number {check(finite(seconds)&&typeof advanceTripClock==='boolean');const a=this.s.action;if(!a)return seconds;const used=Math.min(seconds,a.durationSeconds-a.elapsedSeconds);a.elapsedSeconds+=used;if(advanceTripClock)this.s.gameSeconds+=used/a.durationSeconds*a.gameSeconds;
  if(a.elapsedSeconds>=a.durationSeconds){this.s.stamina=Math.min(100,this.s.stamina+a.restore);this.s.blocked=false;this.s.action=null;}return seconds-used;
 }
 pickupGroup(ids:string[]):boolean {
  check(Array.isArray(ids)&&ids.length>0&&ids.every(id=>typeof id==='string'&&id.length>0)&&new Set(ids).size===ids.length);
  const orders=ids.map(id=>this.s.orders.find(o=>o.id===id));
  // Resolve and validate the whole group before either the debit or any picked flag.
  check(orders.every(o=>!!o&&!o.picked&&!o.delivered));
  if(this.s.stamina<1){this.s.blocked=true;return false;}
  this.s.stamina-=1;this.s.blocked=this.s.stamina===0;for(const order of orders)order!.picked=true;return true;
 }
 service(id:string,kind:'pickup'|'dropoff'):boolean {
  check(kind==='pickup'||kind==='dropoff');if(kind==='pickup')return this.pickupGroup([id]);
  const o=this.s.orders.find(o=>o.id===id);check(o&&o.picked&&!o.delivered);
  if(this.s.stamina<1){this.s.blocked=true;return false;}this.s.stamina-=1;this.s.blocked=this.s.stamina===0;return true;
 }
 travel(metres:number,gameSeconds:number):number {
  check(finite(metres)&&finite(gameSeconds));const cost=metres/1000*[2,2,3,3,4][this.s.mapId-1],fraction=cost>0?Math.min(1,this.s.stamina/cost):1;
  this.s.stamina=Math.max(0,this.s.stamina-cost*fraction);this.s.blocked=this.s.stamina===0;this.s.gameSeconds+=gameSeconds*fraction;
  const normalBase=this.s.preference==='fast'?.06:this.s.preference==='main'?.03:.01,weather=this.s.weather==='rain'?.02:this.s.weather==='severe'?.05:0;
  for(const o of this.s.orders)if(o.picked&&!o.delivered&&!o.safe){const base=this.s.version===3?FOOD_DAMAGE_BASE[o.food!.fragility][this.s.preference]:normalBase;o.risk=Math.min(.25,o.risk+(base*[.25,.5,.75,1,1.25][this.s.mapId-1]+weather)*metres*fraction/o.heldMetres);}
  return fraction;
 }
 serviceTime(seconds:number):void {check(finite(seconds));this.s.gameSeconds+=seconds*30;}
 outcome(id:string):V2DeliveryOutcome {const o=this.s.orders.find(o=>o.id===id);check(o&&o.picked);return {lateGameSeconds:o.safe?0:Math.max(0,this.s.gameSeconds-o.deadlineGameSeconds),damage:!o.safe&&o.draw<o.risk?(o.severityDraw<.7?'minor':o.severityDraw<.95?'moderate':'severe'):'none'};}
 delivered(id:string,ratingDelta:number):void {const o=this.s.orders.find(o=>o.id===id);check(o);if(o.delivered)return;o.delivered=true;this.s.rating=Math.max(20,Math.min(100,this.s.rating+ratingDelta));if(this.s.orders.every(order=>order.delivered))this.endBatchAccounting();}
 private endBatchAccounting():void {const batch=this.s.batchAccounting;if(batch&&!batch.end)batch.end={supplySpentCents:this.s.supplySpentCents,inventoryUsed:{...this.s.inventoryUsed}};}
 cancel():void {this.endBatchAccounting();this.s.orders=[];this.s.blocked=this.s.stamina===0;}
 static restore(raw:V2TripState):V2TripRules {
  // Inspect presence before JSON cloning can erase an explicit undefined food.
  check(raw&&[1,2,3].indexOf(raw.version)>=0&&Array.isArray(raw.orders));
  for(const order of raw.orders){check(order&&typeof order==='object'&&!Array.isArray(order));if(raw.version===3){check(Object.prototype.propertyIsEnumerable.call(order,'food'));parseV2FoodRisk(order.food);}else check(!('food' in order));}
  const t=new V2TripRules(),s=clone(raw);check(s&&[1,2,3].indexOf(s.version)>=0);
  const legacy=(s.version as number)===1;
  if(legacy){check((!s.action||['water','noodles','rest'].includes(s.action.kind))&&s.autoSupplyPolicy&&['water','noodles'].includes(s.autoSupplyPolicy.kind!));s.version=2;s.batchAccounting=null;s.inventory=emptySupplyInventory();s.inventoryUsed=emptySupplyInventory();s.supplyGrants=[];if(s.autoSupplyPolicy){s.autoSupplyPolicy.allowPaid=false;s.autoSupplyPolicy.useInventory=false;}if(s.action)s.action.source=s.action.kind==='rest'?'rest':'purchase';}
  check(finite(s.stamina)&&s.stamina<=100&&finite(s.rating)&&s.rating>=20&&s.rating<=100&&finite(s.gameSeconds)&&Number.isInteger(s.seed)&&s.seed>=0&&s.seed<=4294967295&&Number.isInteger(s.mapId)&&s.mapId>=1&&s.mapId<=5&&['fast','main','smooth'].includes(s.preference)&&['clear','rain','severe'].includes(s.weather)&&typeof s.blocked==='boolean'&&Number.isSafeInteger(s.supplySpentCents)&&s.supplySpentCents>=0);
  check(Array.isArray(s.orders)&&new Set(s.orders.map(o=>o.id)).size===s.orders.length);for(const o of s.orders)check(typeof o.id==='string'&&o.id.length>0&&finite(o.deadlineGameSeconds)&&typeof o.picked==='boolean'&&typeof o.delivered==='boolean'&&(!o.delivered||o.picked)&&finite(o.risk)&&o.risk<=.25&&finite(o.draw)&&o.draw<1&&finite(o.severityDraw)&&o.severityDraw<1&&finite(o.heldMetres)&&o.heldMetres>0&&typeof o.safe==='boolean');
  const p=s.autoSupplyPolicy;check(p&&typeof p.enabled==='boolean'&&Number.isSafeInteger(p.budgetCents)&&p.budgetCents>=0&&Number.isSafeInteger(p.spentCents)&&p.spentCents>=0&&p.spentCents<=p.budgetCents&&p.spentCents<=s.supplySpentCents&&(p.kind===undefined||!!supplyItem(p.kind))&&typeof p.allowPaid==='boolean'&&typeof p.useInventory==='boolean');
  check(Array.isArray(s.supplyGrants)&&new Set(s.supplyGrants.map(g=>g.grantId)).size===s.supplyGrants.length&&new Set(s.supplyGrants.map(g=>g.rewardId)).size===s.supplyGrants.length);
  const totals=emptySupplyInventory();for(const g of s.supplyGrants){check(typeof g.grantId==='string'&&g.grantId.length>0&&g.grantId.length<=160);const reward=V2_SUPPLY_REWARDS.find(r=>r.id===g.rewardId);check(reward);for(const item of reward.items)totals[item.kind]+=item.quantity;}
  for(const record of [s.inventory,s.inventoryUsed])check(record&&Object.keys(record).length===V2_SUPPLY_CATALOG.length&&V2_SUPPLY_CATALOG.every(item=>Number.isSafeInteger(record[item.id])&&record[item.id]>=0));
  for(const item of V2_SUPPLY_CATALOG)check(Number.isSafeInteger(totals[item.id])&&s.inventory[item.id]+s.inventoryUsed[item.id]===totals[item.id]);
  const batch=s.batchAccounting;check(batch===null||!!batch&&Array.isArray(batch.orderIds)&&batch.orderIds.length>0&&batch.orderIds.every(id=>typeof id==='string'&&id.length>0)&&new Set(batch.orderIds).size===batch.orderIds.length&&Number.isSafeInteger(batch.supplySpentCentsStart)&&batch.supplySpentCentsStart>=0&&batch.supplySpentCentsStart<=s.supplySpentCents&&!!batch.inventoryUsedStart&&Object.keys(batch.inventoryUsedStart).length===V2_SUPPLY_CATALOG.length&&V2_SUPPLY_CATALOG.every(item=>Number.isSafeInteger(batch.inventoryUsedStart[item.id])&&batch.inventoryUsedStart[item.id]>=0&&batch.inventoryUsedStart[item.id]<=s.inventoryUsed[item.id])&&s.orders.every(order=>batch.orderIds.includes(order.id)));
  if(batch?.end){const end=batch.end;check(Number.isSafeInteger(end.supplySpentCents)&&end.supplySpentCents>=batch.supplySpentCentsStart&&end.supplySpentCents<=s.supplySpentCents&&end.inventoryUsed&&Object.keys(end.inventoryUsed).length===V2_SUPPLY_CATALOG.length&&V2_SUPPLY_CATALOG.every(item=>Number.isSafeInteger(end.inventoryUsed[item.id])&&end.inventoryUsed[item.id]>=batch.inventoryUsedStart[item.id]&&end.inventoryUsed[item.id]<=s.inventoryUsed[item.id])&&s.orders.every(order=>order.delivered));}
  check(s.action===null||!!s.action&&typeof s.action==='object');
  if(s.action){const a=s.action,item=supplyItem(a.kind),rest=a.kind==='rest';check((rest||!!item)&&finite(a.elapsedSeconds)&&a.elapsedSeconds<a.durationSeconds&&finite(a.durationSeconds)&&a.durationSeconds>0);
   if(rest)check(a.source==='rest'&&a.costCents===0&&((a.restore===20&&a.durationSeconds===10&&a.gameSeconds===600)||(a.restore===100&&a.durationSeconds===20&&a.gameSeconds===0)));
   else check(!!item&&['purchase','inventory'].includes(a.source)&&a.costCents===(a.source==='purchase'?item.costCents:0)&&a.durationSeconds===item.durationSeconds&&a.gameSeconds===item.gameSeconds&&a.restore===item.restore&&(a.source==='purchase'?s.supplySpentCents>=a.costCents:s.inventoryUsed[item.id]>0));
  }
  if(s.version===3)for(const order of s.orders)parseV2FoodRisk(order.food);
  t.s=s;return t;
 }
}
