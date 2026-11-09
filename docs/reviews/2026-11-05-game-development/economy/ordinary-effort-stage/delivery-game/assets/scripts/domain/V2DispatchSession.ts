import { V2LedgerContext, V2SupplyChargeDetail } from './V2Ledger';
import { V2DeliveryOutcome, settleTripIncome } from './V2TripRules';
import { V2EconomySession, V2DeliveryQuote, V2DeliveryReceipt, V2OrdinaryPricingById, normalizeOrdinaryPricingById, validateOrdinaryPricingQuote, vehicleEffects } from './V2EconomySession';
import { V2FleetSession } from './V2FleetSession';
import { RewardSession, AdBenefit, AdTicket, AdOutcome } from '../rewards-v2/RewardSession';

export interface V2DispatchOrder { id:string; kind:'ordinary'|'special'; weightKg:number }
/** Real route adapter verifies a delivery event. Elapsed time is never arrival evidence. */
export interface V2DispatchPort { verifyArrival(order:Readonly<V2DispatchOrder>,arrivalToken:string):boolean }
export type V2EconomyCommand =
 {type:'buyVehicle';modelId:number}|{type:'hireRider';riderId:string}|
 {type:'assignVehicle';riderId:string;vehicleId:string|null}|{type:'buyMap'|'selectMap';mapId:number}|
 {type:'upgradeVehicle';vehicleId:string}|{type:'upgradeRider';riderId:string};
interface DispatchOrder extends V2DispatchOrder {quote:V2DeliveryQuote;status:'pending'|'completed'|'cancelled';receipt:V2DeliveryReceipt|null}
export interface V2DispatchSnapshot {
 format:'county-v2-dispatch';version:1;economy:unknown;fleet:unknown;rewards:unknown;clockNeedsRebase:boolean;
 orders:DispatchOrder[];batchIds:string[];
 frame:{sequence:number;nowSeconds:number;foreground:boolean;paused:boolean;fingerprint:string};control:'manual'|'auto';
}
export interface V2DispatchTick {autoRunSeconds:number;control:'manual'|'auto'}
const clone=<T>(x:T):T=>JSON.parse(JSON.stringify(x));
function check(x:unknown):asserts x {if(!x)throw new Error('V2 dispatch input/state invalid');}
function finite(x:unknown):asserts x is number {check(typeof x==='number'&&Number.isFinite(x)&&x>=0);}
function identity(x:unknown):asserts x is string {check(typeof x==='string'&&x.length>0&&x.length<=200);}

/** One owner for economic, fleet, reward and delivery states; no storage or Cocos dependency. */
export class V2DispatchSession {
 private economy:V2EconomySession;
 private fleet:V2FleetSession;
 private rewards:RewardSession;
 private orders:DispatchOrder[]=[];
 private batchIds:string[]=[];
 private frame={sequence:0,nowSeconds:0,foreground:true,paused:false,fingerprint:''};
 private control:'manual'|'auto'='manual';
 private firstTickAfterRestore=false;
 private ledgerDayKeyResolver:((atMs:number)=>string)|null=null;
 constructor(private readonly port:V2DispatchPort,nowSeconds=0){
  check(!!port&&typeof port.verifyArrival==='function');finite(nowSeconds);check(Number.isSafeInteger(Math.floor(nowSeconds*1000)));
  this.economy=new V2EconomySession();this.rewards=new RewardSession();
  this.fleet=new V2FleetSession(this.economy,Math.floor(nowSeconds*1000));this.frame.nowSeconds=nowSeconds;
 }
 setLedgerContext(context:V2LedgerContext|null):void {this.economy.setLedgerContext(context);}
 /** Synchronous event scope; transactions may replace economy, so restore on the current owner. */
 withLedgerTime<T>(nowSeconds:number,action:()=>T):T {
  finite(nowSeconds);const nowMs=Math.floor(nowSeconds*1000);check(Number.isSafeInteger(nowMs));
  const previous=this.economy.state.ledgerContext||null;
  this.economy.setLedgerContext({nowMs,dayKey:this.ledgerDayKeyResolver?this.ledgerDayKeyResolver(nowMs):null});
  try{return action();}finally{this.economy.setLedgerContext(previous);}
 }
 /** Transient host calendar policy; restored sessions must be rebound before advancing. */
 setLedgerDayKeyResolver(resolver:((atMs:number)=>string)|null):void {this.fleet.setLedgerDayKeyResolver(resolver);this.ledgerDayKeyResolver=resolver;}
 get economyState(){return this.economy.state;}
 get fleetState(){return this.fleet.state;}
 snapshot():V2DispatchSnapshot {return clone({format:'county-v2-dispatch',version:1,clockNeedsRebase:this.firstTickAfterRestore,economy:JSON.parse(this.economy.serialize()),fleet:JSON.parse(this.fleet.serialize()),rewards:JSON.parse(this.rewards.serialize()),orders:this.orders,batchIds:this.batchIds,frame:this.frame,control:this.control});}
 serialize():string{return JSON.stringify(this.snapshot());}
 private transact<T>(change:(draft:V2DispatchSession)=>T):T {
  const draft=V2DispatchSession.restore(this.serialize(),this.port);draft.firstTickAfterRestore=this.firstTickAfterRestore;
  draft.setLedgerDayKeyResolver(this.ledgerDayKeyResolver);
  const result=change(draft);draft.fleet.syncHeroCompletions();draft.validate();
  this.economy=draft.economy;this.fleet=draft.fleet;this.rewards=draft.rewards;
  this.orders=draft.orders;this.batchIds=draft.batchIds;this.frame=draft.frame;this.control=draft.control;this.firstTickAfterRestore=draft.firstTickAfterRestore;
  return clone(result);
 }
 command(command:V2EconomyCommand):string|null {
  return this.transact(d=>{check(!!command&&d.batchIds.length===0);
   switch(command.type){
    case 'buyVehicle':return d.economy.buyVehicle(command.modelId);
    case 'hireRider':d.economy.hireRider(command.riderId);break;
    case 'assignVehicle':d.economy.assignVehicle(command.riderId,command.vehicleId);break;
    case 'buyMap':d.economy.buyMap(command.mapId);break;
    case 'selectMap':d.economy.selectMap(command.mapId);break;
    case 'upgradeVehicle':d.economy.upgradeVehicle(command.vehicleId);break;
    case 'upgradeRider':d.economy.upgradeRider(command.riderId);break;
    default:throw new Error('Unknown V2 economic command');
   }return null;
  });
 }
 enterLobby(entryId:string,appearanceRoll:number,priceRoll:number){return this.transact(d=>d.rewards.enterLobby(entryId,appearanceRoll,priceRoll));}
 requestAd(kind:AdBenefit,orderId:string|null,nowSeconds:number,ttlSeconds:number):AdTicket{return this.transact(d=>d.rewards.requestAd(kind,orderId,nowSeconds,ttlSeconds));}
 resolveAd(ticket:AdTicket,outcome:AdOutcome,nowSeconds:number):boolean{return this.transact(d=>{const granted=d.rewards.resolveAd(ticket,outcome,nowSeconds);if(granted&&ticket.benefit==='auto'){if(!d.orders.some(o=>d.batchIds.includes(o.id)&&o.kind==='special'))d.control='auto';d.frame.nowSeconds=Math.max(d.frame.nowSeconds,nowSeconds);}return granted;});}
 stopAutomation():void {this.transact(d=>{d.control='manual';return null;});}
 resumeAutomation():void {this.transact(d=>{check(d.rewards.autoRemainingSeconds>0&&!d.orders.some(o=>d.batchIds.includes(o.id)&&o.kind==='special'));d.control='auto';return null;});}
 acceptBatch(orders:V2DispatchOrder[],ordinaryPricingById?:V2OrdinaryPricingById):V2DeliveryQuote[]{return this.transact(d=>{
  check(Array.isArray(orders)&&orders.length>0&&d.batchIds.length===0);
  const seen=new Set<string>();let kg=0;
  for(const order of orders){check(!!order);identity(order.id);finite(order.weightKg);check(order.weightKg>0&&(order.kind==='ordinary'||order.kind==='special'));check(!seen.has(order.id)&&!d.orders.some(o=>o.id===order.id));seen.add(order.id);kg+=order.weightKg;}
  finite(kg);const s=d.economy.state,v=s.vehicles.find(v=>v.id===s.riders[0].vehicleId);check(v&&kg<=vehicleEffects(v).capacityKg);
  if(orders.some(o=>o.kind==='special'))check(d.control==='manual');
  const pricingById=normalizeOrdinaryPricingById(orders,ordinaryPricingById);
  const rewardBatch=d.rewards.beginBatch(orders.map(o=>({id:o.id,kind:o.kind==='ordinary'?'normal':'special'})));
  const quotes=d.economy.acceptBatch(orders.map(o=>({...o,...(o.kind==='special'?{specialCoins:rewardBatch.specialCoins!}:{})})),pricingById);
  d.orders.push(...orders.map((o,i)=>({...clone(o),quote:clone(quotes[i]),status:'pending' as const,receipt:null})));
  d.batchIds=orders.map(o=>o.id);return quotes;
 });}
 chargeSupply(costCents:number,detail?:V2SupplyChargeDetail):void {this.transact(d=>{d.economy.chargeSupply(costCents,detail);return null;});}
 /** Composite owners advance old quota before each event, and flush the wall-clock tail once. */
 advanceFleetTo(nowSeconds:number):void {
  finite(nowSeconds);const nowMs=Math.floor(nowSeconds*1000);check(Number.isSafeInteger(nowMs));
  const progress=this.fleet.clockProgress;
  // A pending hero event still needs the original sync transaction, even at an old clock.
  if(nowMs<=progress.lastAdvancedAt&&progress.heroEventCursor===this.economy.heroCompletionEventCount)return;
  this.transact(d=>{d.fleet.advanceTo(nowMs);return null;});
 }
 completeDelivery(orderId:string,arrivalToken:string,nowSeconds=this.frame.nowSeconds,outcome:V2DeliveryOutcome={lateGameSeconds:0,damage:'none'}):V2DeliveryReceipt {return this.transact(d=>{
  identity(orderId);const order=d.orders.find(o=>o.id===orderId);check(order);
  if(order.status==='completed'){check(order.receipt);return order.receipt;}
  check(order.status==='pending'&&d.batchIds.includes(order.id));identity(arrivalToken);
  check(d.port.verifyArrival({id:order.id,kind:order.kind,weightKg:order.weightKg},arrivalToken)===true);
  finite(nowSeconds);check(Number.isSafeInteger(Math.floor(nowSeconds*1000)));d.fleet.advanceTo(Math.floor(nowSeconds*1000));
  const receipt=d.withLedgerTime(nowSeconds,()=>d.economy.completeDelivery(orderId,outcome));order.status='completed';order.receipt=receipt;d.closeFinishedBatch();return receipt;
 });}
 /** V1 cancellation ends all remaining orders in this batch, preserving completed receipts. */
 cancelRemaining():void {this.transact(d=>{check(d.batchIds.length>0);d.cancelAllRemaining();return null;});}
 cancelBatch():void {this.cancelRemaining();}
 cancelDelivery(orderId:string):void {this.transact(d=>{identity(orderId);check(d.orders.some(o=>o.id===orderId&&o.status==='pending'&&d.batchIds.includes(o.id)));d.cancelAllRemaining();return null;});}
 private cancelAllRemaining():void {for(const o of this.orders.filter(o=>this.batchIds.includes(o.id)&&o.status==='pending')){this.economy.cancelDelivery(o.id);o.status='cancelled';}this.closeFinishedBatch();}
 private closeFinishedBatch():void {if(!this.orders.some(o=>this.batchIds.includes(o.id)&&o.status==='pending')){this.batchIds=[];this.rewards.endBatch();}}
 /** A frame is consumed once. First resume frame only rebases time, never catches up hero movement. */
 consumeAutomaticProgress(seconds:number):void {this.transact(d=>{finite(seconds);check(d.control==='auto');const result=d.rewards.advanceAuto(seconds,true,false);if(result.manualRequired)d.control='manual';return null;});}
 tick(sequence:number,nowSeconds:number,foreground:boolean,paused:boolean,options:{deferAuto?:boolean;deferFleet?:boolean}={}):V2DispatchTick {return this.transact(d=>{
  finite(sequence);check(Number.isSafeInteger(sequence)&&sequence>0);finite(nowSeconds);check(typeof foreground==='boolean'&&typeof paused==='boolean');
  const fingerprint=JSON.stringify([nowSeconds,foreground,paused]);
  if(sequence===d.frame.sequence){check(fingerprint===d.frame.fingerprint);return {autoRunSeconds:0,control:d.control};}
  check(sequence>d.frame.sequence);
  const pendingAd=d.rewards.snapshot().tickets.some(t=>t.status==='pending');
  // This interval began under the SDK pause. Expire now, then resume on the next frame.
  d.rewards.expirePending(nowSeconds);
  const active=foreground&&!paused&&d.frame.foreground&&!d.frame.paused&&!d.firstTickAfterRestore&&!pendingAd;
  const delta=active?Math.max(0,nowSeconds-d.frame.nowSeconds):0;
  let autoRunSeconds=0;
  if(d.control==='auto'){
   if(options.deferAuto){autoRunSeconds=Math.min(delta,d.rewards.autoRemainingSeconds);}else {const result=d.rewards.advanceAuto(delta,active,false);autoRunSeconds=result.runSeconds;if(result.manualRequired)d.control='manual';}
  }
  check(Number.isSafeInteger(Math.floor(nowSeconds*1000)));if(!options.deferFleet)d.fleet.advanceTo(Math.floor(nowSeconds*1000));
  d.frame={sequence,nowSeconds:Math.max(nowSeconds,d.frame.nowSeconds),foreground,paused,fingerprint};d.firstTickAfterRestore=false;
  return {autoRunSeconds,control:d.control};
 });}
 private validate():void {
  const e=this.economy.state,r=this.rewards.snapshot();
  check(Array.isArray(this.orders)&&Array.isArray(this.batchIds));
  const ids=new Set<string>();
  for(const o of this.orders){check(!!o);identity(o.id);finite(o.weightKg);check(o.weightKg>0&&!ids.has(o.id));ids.add(o.id);check(o.kind==='ordinary'||o.kind==='special');check(['pending','completed','cancelled'].includes(o.status));check(o.quote.id===o.id&&o.quote.kind===o.kind&&o.quote.weightKg===o.weightKg);
   validateOrdinaryPricingQuote(o.quote,e);
   if(o.status==='completed'){const r=o.receipt;check(r?.id===o.id&&e.settledOrderIds.includes(o.id));if(r.baseIncomeCents===undefined)check(r.incomeCents===o.quote.incomeCents);else {const final=settleTripIncome(o.quote.incomeCents,{lateGameSeconds:r.lateGameSeconds!,damage:r.damage!});check(r.baseIncomeCents===o.quote.incomeCents&&r.incomeCents===final.incomeCents&&r.lateRetain===final.lateRetain&&r.damageRetain===final.damageRetain&&r.ratingDelta===final.ratingDelta);}}else check(o.receipt===null&&!e.settledOrderIds.includes(o.id));
  }
  check(new Set(this.batchIds).size===this.batchIds.length&&this.batchIds.every(id=>ids.has(id)));
  const pending=this.orders.filter(o=>o.status==='pending');check(pending.every(o=>this.batchIds.includes(o.id)));
  check(pending.length===e.activeQuotes.length&&pending.every(o=>e.activeQuotes.some(q=>JSON.stringify(q)===JSON.stringify(o.quote))));
  if(this.batchIds.length){check(r.activeBatch&&r.activeBatch.orders.length===this.batchIds.length&&r.activeBatch.orders.every(o=>this.batchIds.includes(o.id)&&this.orders.some(stored=>stored.id===o.id&&(stored.kind==='ordinary'?'normal':'special')===o.kind)));check(pending.length>0);
   const batch=this.orders.filter(o=>this.batchIds.includes(o.id));const vehicle=e.vehicles.find(v=>v.id===batch[0].quote.vehicleId);check(vehicle&&batch.every(o=>o.quote.vehicleId===vehicle.id)&&batch.reduce((sum,o)=>sum+o.weightKg,0)<=vehicleEffects(vehicle).capacityKg);
   if(batch.some(o=>o.kind==='special'))check(batch.length===1&&this.control==='manual'&&r.activeBatch.specialCoins! *100===batch[0].quote.incomeCents);
  }else check(r.activeBatch===null);
  finite(this.frame.sequence);check(Number.isSafeInteger(this.frame.sequence));finite(this.frame.nowSeconds);check(typeof this.frame.foreground==='boolean'&&typeof this.frame.paused==='boolean'&&typeof this.frame.fingerprint==='string');
  check(this.control==='manual'||this.control==='auto'&&r.autoRemainingSeconds>0);
 }
 static restore(serialized:string,port:V2DispatchPort,options:{preserveClock?:boolean}={}):V2DispatchSession {
  const s:V2DispatchSnapshot=JSON.parse(serialized);check(!!s&&s.format==='county-v2-dispatch'&&s.version===1);
  const result=new V2DispatchSession(port);result.economy=V2EconomySession.restore(JSON.stringify(s.economy));
  result.fleet=V2FleetSession.restore(JSON.stringify(s.fleet),result.economy);result.rewards=RewardSession.restore(JSON.stringify(s.rewards));
  result.orders=clone(s.orders);result.batchIds=clone(s.batchIds);result.frame=clone(s.frame);result.control=s.control;check(typeof s.clockNeedsRebase==='boolean');result.firstTickAfterRestore=options.preserveClock===true?s.clockNeedsRebase:true;
  result.validate();return result;
 }
}
