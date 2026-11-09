import { V2_CONFIG as C, V2_CONFIG_ID } from './V2EconomyConfig';
import { V2EconomySession, V2EconomySnapshot, V2FleetQuote, V2DeliveryReceipt, vehicleEffects,contractTerms,wrapLegacyQuote,validateSlotFleetQuote } from './V2EconomySession';
import { V2_SLOT_PROFILE_ID,slotVehicleEffects,sameV2ContractTerms } from './V2EconomyProfiles';
import { slotFleetOrderIds,fitsV2Capacity } from './V2LoadRules';

export interface V2FleetOrder extends V2FleetQuote { dueMs:number }
export interface V2FleetBatch { id:number; riderId:string; vehicleId:string; mapId:number; elapsedMs:number; paidCount:number; orders:V2FleetOrder[] }
export interface V2FleetState { quotaMs:number; lastAdvancedAt:number; heroEventCursor:number; heroCompletionsSeen:number; nextBatchId:number; batches:V2FleetBatch[] }
export interface V2FleetSnapshot { format:'county-v2-fleet';version:1|2|3;configId:string;economy:V2EconomySnapshot;fleet:V2FleetState }
const copy=<T>(v:T):T=>JSON.parse(JSON.stringify(v));
function check(v:unknown,message='车队存档校验失败'):asserts v {if(!v)throw new Error(message);}
function integer(v:unknown,min=0,max=Number.MAX_SAFE_INTEGER):v is number {return typeof v==='number'&&Number.isSafeInteger(v)&&v>=min&&v<=max;}
function stage(completed:number):{capacity:number;refill:number} {
 return completed>=700?{capacity:1800000,refill:180000}:completed>=240?{capacity:1500000,refill:120000}:completed>=60?{capacity:1200000,refill:120000}:{capacity:900000,refill:60000};
}
function timing(q:V2FleetQuote,count:number):{road:number;service:number} {
 return {road:Math.ceil(60000*[1,1.1,1.25,1.45,1.6][q.mapId-1]/q.speedRelativeToStarter*(1+.25*(count-1))),service:Math.ceil(30000*(1-q.fixedServiceReduction))};
}
/** Deterministic integer order supply, finite shared clock, no storage or wall-clock reads.
 * Timing is the versioned design model, not actual map routing or visible rider movement.
 */
export class V2FleetSession {
 readonly economy:V2EconomySession;
 private value:V2FleetState;
 private version:1|2|3;
 // Host-local calendar policy is transient; never serialize a callback or infer a timezone.
 private ledgerDayKeyResolver:((atMs:number)=>string)|null=null;
 constructor(economy:V2EconomySession,nowMs=0){
  check(integer(nowMs),'经营时钟无效');check(economy.state.fleetQuotes.length===0,'已有车队合同须恢复组合快照');this.economy=economy;this.version=economy.schemaVersion;
  this.value={quotaMs:0,lastAdvancedAt:nowMs,heroEventCursor:economy.state.heroCompletionEvents.length,heroCompletionsSeen:economy.state.heroCompletedOrders,nextBatchId:1,batches:[]};
 }
 get state():Readonly<V2FleetState>{return copy(this.value);}
 /** Detached clock scalars, not a mutable fleet or economic snapshot. */
 get clockProgress():Readonly<Pick<V2FleetState,'lastAdvancedAt'|'heroEventCursor'>> {return {lastAdvancedAt:this.value.lastAdvancedAt,heroEventCursor:this.value.heroEventCursor};}
 setLedgerDayKeyResolver(resolver:((atMs:number)=>string)|null):void {check(resolver===null||typeof resolver==='function','账目日期解析器无效');this.ledgerDayKeyResolver=resolver;}
 get quotaCapacityMs():number {const e=this.economy.state;return stage(e.heroCompletedOrders+e.npcCompletedOrders).capacity;}
 serialize():string {return JSON.stringify({format:'county-v2-fleet',version:this.version,configId:this.version===1?V2_CONFIG_ID:V2_SLOT_PROFILE_ID,economy:JSON.parse(this.economy.serialize()),fleet:this.value});}
 /** Wrap only after the original fleet AND economy invariants have accepted the old payload. */
 enableSlots():void {if(this.version!==1)return;this.validate();this.economy.enableSlots();this.value={...this.value,batches:this.value.batches.map(b=>({...b,orders:b.orders.map(wrapLegacyQuote)}))};this.version=2;this.validate();}
 static restore(serialized:string,sharedEconomy?:V2EconomySession):V2FleetSession {
  const raw=JSON.parse(serialized) as V2FleetSnapshot;check(raw&&raw.format==='county-v2-fleet'&&(raw.version===1&&raw.configId===V2_CONFIG_ID||(raw.version===2||raw.version===3)&&raw.configId===V2_SLOT_PROFILE_ID),'车队版本不受支持');
  const e=V2EconomySession.restore(JSON.stringify(raw.economy));if(sharedEconomy)check(sharedEconomy.serialize()===e.serialize(),'车队与钱包快照不一致');
  // Construction bypass is private to validated restoration; fresh construction never accepts outstanding contracts.
  const f=Object.create(V2FleetSession.prototype) as V2FleetSession;
  f.ledgerDayKeyResolver=null;f.version=raw.version;check(e.schemaVersion===f.version);
  Object.defineProperty(f,'economy',{value:sharedEconomy||e,enumerable:true});f.value=copy(raw.fleet);f.validate();return f;
 }
 private validate():void {
  check(this.economy.schemaVersion===this.version);
  const s=this.value,e=this.economy.state;check(s&&integer(s.quotaMs,0,this.quotaCapacityMs)&&integer(s.lastAdvancedAt)&&integer(s.heroEventCursor,0,e.heroCompletionEvents.length)&&integer(s.heroCompletionsSeen,0,e.heroCompletedOrders)&&integer(s.nextBatchId,1)&&Array.isArray(s.batches));
  // Older migrated completions are the baseline, never retroactively replenished.
  check(s.heroCompletionsSeen===e.heroCompletedOrders-(e.heroCompletionEvents.length-s.heroEventCursor));
  const ids=new Set<number>(),riders=new Set<string>(),vehicles=new Set<string>(),unpaid=new Set<string>();
  for(const b of s.batches){check(b&&integer(b.id,1,s.nextBatchId-1)&&!ids.has(b.id)&&!riders.has(b.riderId)&&!vehicles.has(b.vehicleId)&&integer(b.elapsedMs)&&Array.isArray(b.orders)&&b.orders.length>0&&integer(b.paidCount,0,b.orders.length-1));ids.add(b.id);riders.add(b.riderId);vehicles.add(b.vehicleId);
   // The signed vehicle stays reserved; its owner may choose another idle vehicle or null for future work.
   check(e.riders.every(r=>r.id===b.riderId||r.vehicleId!==b.vehicleId)&&e.activeQuotes.every(q=>q.vehicleId!==b.vehicleId),'在途车辆被其他人物或主角合同占用');
   const first=b.orders[0];check(first&&b.riderId===first.riderId&&b.vehicleId===first.vehicleId&&b.mapId===first.mapId);const t=timing(first,b.orders.length);let weight=0;
   const firstTerms=this.version!==1?contractTerms(first):null,slots=firstTerms?.version==='slots-v1';
   if(firstTerms?.version==='slots-v1')check(JSON.stringify(b.orders.map(o=>o.id))===JSON.stringify(slotFleetOrderIds(b.id,firstTerms.capacity.capacitySlots)));
   if(this.version===1)check(b.orders.every(o=>!('terms' in o)));
   for(let i=0;i<b.orders.length;i++){const o=b.orders[i];check(o&&!('vehicleRef' in o)&&(slots||o.id===`fleet-${b.id}-${i}`)&&o.riderId===b.riderId&&o.vehicleId===b.vehicleId&&o.mapId===b.mapId&&o.vehicleLevel===first.vehicleLevel&&o.riderLevel===first.riderLevel&&o.baseIncomeFactor===first.baseIncomeFactor&&o.fixedServiceReduction===first.fixedServiceReduction&&o.capacityKg===first.capacityKg&&o.speedRelativeToStarter===first.speedRelativeToStarter&&o.incomeCents===first.incomeCents&&integer(o.dueMs,1)&&o.dueMs===t.road+t.service*(i+1));
    if(this.version!==1)check(contractTerms(o).version===firstTerms!.version);
    if(slots){validateSlotFleetQuote(o,e);}else{check(integer(o.weightKg,1));weight+=o.weightKg;}
    if(i<b.paidCount)check(e.settledOrderIds.includes(o.id)&&b.elapsedMs>=o.dueMs);
    else{check(b.elapsedMs<o.dueMs&&!unpaid.has(o.id));unpaid.add(o.id);const q=e.fleetQuotes.find(q=>q.id===o.id);check(q&&Object.keys(q).every(k=>k==='terms'?sameV2ContractTerms(contractTerms(q),contractTerms(o)):(q as unknown as Record<string,unknown>)[k]===(o as unknown as Record<string,unknown>)[k]),'车队与入账合同不一致');}
   }
   if(slots){check(firstTerms?.version==='slots-v1');check(fitsV2Capacity(b.orders.map(o=>{const terms=contractTerms(o);check(terms.version==='slots-v1');check(JSON.stringify(terms.capacity)===JSON.stringify(firstTerms.capacity));return terms.load;}),firstTerms.capacity));}
   else check(typeof first.capacityKg==='number'&&weight<=first.capacityKg);
  }
  check(unpaid.size===e.fleetQuotes.length&&e.fleetQuotes.every(q=>unpaid.has(q.id)),'车队合同丢失');
 }
 private atomic<T>(change:(draft:V2FleetSession)=>T):T {
  const d=V2FleetSession.restore(this.serialize());d.setLedgerDayKeyResolver(this.ledgerDayKeyResolver);const result=change(d);d.validate();
  this.economy.replaceFrom(d.economy.serialize());this.value=d.value;this.version=d.version;return result;
 }
 private syncDraft():void {
  const events=this.economy.state.heroCompletionEvents;
  for(let i=this.value.heroEventCursor;i<events.length;i++){const row=stage(events[i].teamCompletedAfter);this.value.quotaMs=Math.min(row.capacity,this.value.quotaMs+row.refill);this.value.heroCompletionsSeen++;}
  this.value.heroEventCursor=events.length;
 }
 /** The quota check and loan activation share the authoritative fleet/economy draft. */
 borrowEmergencyVehicle(expectedSequence:number):number {
  return this.atomic(d=>{d.syncDraft();check(d.value.quotaMs===0,'经营额度尚未耗尽，不能应急借车');d.enableSlots();const sequence=d.economy.beginHeroEmergencyLoan(expectedSequence);d.version=3;return sequence;});
 }
 /** Consume each real hero completion event exactly once. Call at the completion instant. */
 syncHeroCompletions():void {
  if(this.value.heroEventCursor===this.economy.heroCompletionEventCount)return;
  this.atomic(d=>d.syncDraft());
 }
 completeHeroDelivery(id:string):V2DeliveryReceipt {return this.atomic(d=>{const r=d.economy.completeDelivery(id);d.syncDraft();return r;});}
 private startBatches():void {
  if(!this.economy.hasRecoverableHeroVehicle)return;
  const e=this.economy.state;
  for(const rider of e.riders){if(rider.id==='hero'||!rider.vehicleId||this.value.batches.some(b=>b.riderId===rider.id||b.vehicleId===rider.vehicleId))continue;
   if(this.version!==1){
    const vehicle=e.vehicles.find(v=>v.id===rider.vehicleId)!;const capacity=slotVehicleEffects(vehicle).capacitySlots,ids=slotFleetOrderIds(this.value.nextBatchId,capacity);
    if(!ids.length)continue;const id=this.value.nextBatchId++,quotes=this.economy.registerSlotFleetOrders(rider.id,ids),t=timing(quotes[0],quotes.length);
    this.value.batches.push({id,riderId:rider.id,vehicleId:vehicle.id,mapId:e.selectedMapId,elapsedMs:0,paidCount:0,orders:quotes.map((q,i)=>({...q,dueMs:t.road+t.service*(i+1)}))});continue;
   }
   const vehicle=e.vehicles.find(v=>v.id===rider.vehicleId)!;const capacity=vehicleEffects(vehicle).capacityKg,map=C.maps[e.selectedMapId-1];const distribution=e.selectedMapId<=2?[1,2,3]:e.selectedMapId===3?[1,3,5]:[1,3,6];
   const weights:number[]=[];let remaining=capacity;
   // Versioned deterministic supply: repeated saves and partitioned advances use identical batches.
   for(let i=0;i<map.expectedBatchDensityCap;i++){const candidates=i===0?distribution.filter(w=>w<=remaining):distribution;if(!candidates.length)break;const w=candidates[(this.value.nextBatchId+i)%candidates.length];if(w>remaining)break;weights.push(w);remaining-=w;}
   if(!weights.length)continue;const id=this.value.nextBatchId++,quotes=this.economy.registerFleetOrders(rider.id,weights.map((_,i)=>`fleet-${id}-${i}`),weights),t=timing(quotes[0],quotes.length);
   this.value.batches.push({id,riderId:rider.id,vehicleId:vehicle.id,mapId:e.selectedMapId,elapsedMs:0,paidCount:0,orders:quotes.map((q,i)=>({...q,dueMs:t.road+t.service*(i+1)}))});
  }
 }
 /** Absolute safe-integer milliseconds. Online and offline call the identical path.
  * Idle/no-quota intervals advance the high-water mark, never retroactively accrue work.
  */
 advanceTo(nowMs:number):void {
  check(integer(nowMs),'经营时钟无效');if(nowMs<=this.value.lastAdvancedAt)return;
  this.atomic(d=>{d.syncDraft();const ledgerContext=d.economy.state.ledgerContext||null;let workAt=d.value.lastAdvancedAt;let remaining=nowMs-d.value.lastAdvancedAt;d.value.lastAdvancedAt=nowMs;
   while(remaining>0&&d.value.quotaMs>0){d.startBatches();if(!d.value.batches.length)break;
    const nextDue=Math.min(...d.value.batches.map(b=>b.orders[b.paidCount].dueMs-b.elapsedMs));const step=Math.min(remaining,d.value.quotaMs,nextDue);check(integer(step,1),'经营进度无效');
    for(const b of d.value.batches)b.elapsedMs+=step;remaining-=step;d.value.quotaMs-=step;workAt+=step;
    // Resolve each work instant, not the frame end or the host's current date.
    d.economy.setLedgerContext({nowMs:workAt,dayKey:d.ledgerDayKeyResolver?d.ledgerDayKeyResolver(workAt):null});
    for(const b of d.value.batches){while(b.paidCount<b.orders.length&&b.orders[b.paidCount].dueMs<=b.elapsedMs){d.economy.settleFleetOrder(b.orders[b.paidCount].id);b.paidCount++;}}
    d.value.batches=d.value.batches.filter(b=>b.paidCount<b.orders.length);
   }
   d.economy.setLedgerContext(ledgerContext);
  });
 }
}
