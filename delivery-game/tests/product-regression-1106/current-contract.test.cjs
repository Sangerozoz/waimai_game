const {test}=require('node:test');
const assert=require('node:assert/strict');
const {domain,map,city,richEconomy,richGame,legacyOrder,legacyGameRaw}=require('./helpers.cjs');
const {V2GameSession}=map('V2GameSession');
const {V2RouteSession}=map('V2RouteSession');
const {V2RuntimeStore,V2_RUNTIME_SAVE_KEY:KEY,V2_SLOT_EPOCH_KEY:EPOCH}=map('V2RuntimeStore');
const {V2DispatchSession}=domain('V2DispatchSession');
const {V2EconomySession,contractTerms,slotOrdinaryIncomeCents}=domain('V2EconomySession');
const {V2FleetSession}=domain('V2FleetSession');
const {V2TripRules}=domain('V2TripRules');
const {slotLoadForOrderId,totalV2Load}=domain('V2LoadRules');
const {foodForV2Order}=map('FoodCatalog');
const clone=x=>JSON.parse(JSON.stringify(x));
function priceContext(id,metres=1000){const result=Object.create(null);result[id]={deliveryMetres:metres};return result;}
function hero(f,id){if(f.economy.usesSlots)f.economy.acceptSlotBatch([{id,kind:'ordinary'}],priceContext(id));else f.economy.acceptOrdinary(id);return f.completeHeroDelivery(id);}
function team(profile='kg-v1',count=1){const e=richEconomy(profile);for(let i=1;i<=count;i++){e.hireRider(`npc-${i}`);e.assignVehicle(`npc-${i}`,e.buyVehicle(1));}return new V2FleetSession(e,0);}
function gameWithCompleted(count){
 const e=richEconomy();for(let i=0;i<count;i++){const id=`price-history-${i}`;e.acceptSlotBatch([{id,kind:'ordinary'}],priceContext(id));e.completeDelivery(id);}
 const raw=JSON.parse(new V2GameSession(city).serialize());raw.dispatch.economy=JSON.parse(e.serialize());raw.dispatch.fleet.economy=clone(raw.dispatch.economy);
 raw.dispatch.fleet.fleet.heroEventCursor=e.state.heroCompletionEvents.length;raw.dispatch.fleet.fleet.heroCompletionsSeen=e.state.heroCompletedOrders;
 return V2GameSession.restore(city,JSON.stringify(raw),{preserveClock:true});
}
function deliveryCity(){return {...city,title:'ten-second isolated fixture',nodes:[{id:'a',x:0,y:0},{id:'c',x:360,y:0}],roads:[{id:'main',nodes:['a','c'],direction:0,kind:'primary',width:3,speed:1,roughness:0,bridge:false}],pois:[{node:'a',name:'A',kind:'shop'},{node:'c',name:'C',kind:'home'}],dispatchBounds:{minX:0,minY:0,maxX:360,maxY:20}};}
function tenSecondGame(nowSeconds=0){const data=deliveryCity(),order=legacyOrder('ten-second','a','c',data),raw=legacyGameRaw(data,[order],{rich:true,npc:true,ready:true,nowSeconds});return V2GameSession.restore(data,JSON.stringify(raw),{preserveClock:true});}
function day(atMs){return new Date(atMs+8*3600000).toISOString().slice(0,10);}
function context(g,nowSeconds){g.dispatch.setLedgerDayKeyResolver(day);g.dispatch.setLedgerContext({nowMs:Math.floor(nowSeconds*1000),dayKey:day(Math.floor(nowSeconds*1000))});}

test('all 30 slot-profile levels and prices match the frozen parameter source and positive integer upgrade differences',()=>{
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const raw=fs.readFileSync(path.resolve(__dirname,'../../../docs/balance/2026-11-06-capacity-slots-economy/parameters.json'));
 const frozen=JSON.parse(raw.toString('utf8')),{V2_SLOT_CONFIG,V2_SLOT_CONFIG_SOURCE_SHA256}=domain('V2SlotEconomyConfig'),profiles=domain('V2EconomyProfiles');
 assert.equal(V2_SLOT_CONFIG_SOURCE_SHA256,crypto.createHash('sha256').update(raw).digest('hex'));assert.deepEqual(V2_SLOT_CONFIG,frozen);assert.equal(frozen.levels.length,30);
 for(let i=0;i<frozen.levels.length;i++){
  const row=frozen.levels[i];assert.equal(row.level,i+1);
  for(const modelId of ['starter',...frozen.vehicles.map(v=>v.id)]){
   const effects=profiles.slotVehicleEffects({modelId,level:row.level}),expected=modelId==='starter'?row.starterCapacitySlots:row.vehicles.find(v=>v.modelId===modelId).capacitySlots;
   assert.equal(effects.capacitySlots,expected);assert.ok(Number.isSafeInteger(effects.capacitySlots)&&effects.capacitySlots>0);
   if(i<29){const next=frozen.levels[i+1],before=modelId==='starter'?row.starterCumulativeUpgradeCoins:row.vehicles.find(v=>v.modelId===modelId).cumulativeUpgradeCoins,after=modelId==='starter'?next.starterCumulativeUpgradeCoins:next.vehicles.find(v=>v.modelId===modelId).cumulativeUpgradeCoins,q=profiles.slotVehicleUpgradeQuote({modelId,level:row.level});assert.equal(q.costCents,(after-before)*100);assert.ok(Number.isSafeInteger(q.costCents)&&q.costCents>0);}
  }
  for(const rider of frozen.riders){const effects=profiles.slotRiderEffects(rider.id,row.level);assert.equal(effects.incomeFactor,rider.baseIncomeFactor*(1+row.riderTrainingIncomeBonus));assert.equal(effects.fixedServiceReduction,row.fixedServiceReduction);if(i<29)assert.equal(profiles.slotRiderUpgradeQuote(rider.id,row.level).costCents,(frozen.levels[i+1].riderCumulativeUpgradeCoins-row.riderCumulativeUpgradeCoins)*100);}
 }
 for(const model of frozen.vehicles)assert.equal(profiles.slotVehiclePurchaseQuote(model.id).costCents,model.price*100);for(const rider of frozen.riders)assert.equal(profiles.slotRiderHireQuote(rider.id).costCents,rider.price*100);for(const m of frozen.maps){assert.equal(profiles.slotMapPurchaseQuote(m.id).costCents,m.price*100);assert.equal(profiles.slotMapBaseIncomeCents(m.id),m.ordinaryBaseFee*100);}
});

test('current slots: finite stable candidates, canonical load, exact capacity and atomic over-capacity rejection',()=>{
 const g=new V2GameSession(city),before=g.serialize(),offers=g.normalCandidates();assert.deepEqual(g.normalCandidates(),offers);assert.equal(g.serialize(),before);
 assert.ok(offers.length>1);assert.ok(offers.every(o=>!('weightKg' in o)&&o.load.version==='slots-v1'&&[1,2].includes(o.load.occupiedSlots)));
 assert.ok(totalV2Load(offers.map(o=>o.load),g.nextBatchEffects.capacity)>g.nextBatchEffects.capacitySlots);
 assert.throws(()=>g.acceptBatch(offers));assert.equal(g.serialize(),before);
 const tampered={...offers[0],load:{version:'slots-v1',occupiedSlots:offers[0].load.occupiedSlots===1?2:1}};
 assert.throws(()=>g.acceptBatch([tampered]));assert.throws(()=>g.acceptBatch([{...offers[0],weightKg:1}]));assert.equal(g.serialize(),before);
 const q=g.acceptBatch([offers[0]])[0];assert.equal(q.terms.version,'slots-v1');assert.deepEqual(q.terms.load,slotLoadForOrderId(q.id));
});

test('different authoritative merchants retain separate pickup/dropoff groups',()=>{
 const g=richGame(),car=g.dispatch.command({type:'buyVehicle',modelId:3});g.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:car});const offers=g.normalCandidates(),first=offers[0],other=offers.find(o=>o.pickupNode!==first.pickupNode);
 assert.ok(other);g.acceptBatch([first,other]);assert.deepEqual(g.routeSnapshot.stops.map(s=>s.kind),['pickup','dropoff','pickup','dropoff']);assert.ok(g.routeSnapshot.stops.filter(s=>s.kind==='pickup').every(s=>s.orderIds.length===1));
});

test('current slots retain the exact 10-delivery first car and 15-delivery first NPC budget without rewards',()=>{
 const e=new V2EconomySession('slots-v1');for(let i=1;i<=10;i++){const id=`current-intro-${i}`;e.acceptSlotBatch([{id,kind:'ordinary'}],priceContext(id));assert.equal(e.completeDelivery(id).incomeCents,2000);}
 const car=e.buyVehicle(1);assert.equal(e.state.cashCents,0);e.assignVehicle('hero',car);
 for(let i=11;i<=15;i++){const id=`current-intro-${i}`;e.acceptSlotBatch([{id,kind:'ordinary'}],priceContext(id));assert.equal(e.completeDelivery(id).incomeCents,2400);}
 e.hireRider('npc-1');e.assignVehicle('npc-1','starter-1');assert.equal(e.state.cashCents,0);assert.equal(e.state.hireCount,1);assert.equal(e.state.riders.find(r=>r.id==='npc-1').vehicleId,'starter-1');assert.ok(e.state.ledger.entries.every(row=>row.category!=='task_reward'));
});

test('larger integer capacity can accept more than the former eight-offer read batch from one finite stable pool',t=>{
 const data={...city,title:'finite expanded supply fixture',nodes:Array.from({length:12},(_,i)=>({id:String(i),x:i*10,y:0})),roads:[{id:'main',nodes:Array.from({length:12},(_,i)=>String(i)),direction:0,kind:'primary',width:3,speed:1,roughness:0,bridge:false}],pois:Array.from({length:12},(_,i)=>({node:String(i),name:`P${i}`,kind:'shop'})),dispatchBounds:{minX:0,minY:0,maxX:110,maxY:20}};
 const g=richGame(data),car=g.dispatch.command({type:'buyVehicle',modelId:10});g.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:car});
 const offers=g.normalCandidates();assert.ok(offers.length>8);assert.ok(offers.length<=data.pois.length*2);assert.deepEqual(g.normalCandidates(),offers);
 // A 10-slot model is not promised to hold nine mixed 1/2-slot orders. Select real 1-slot offers, as the UI permits.
 let remaining=g.nextBatchEffects.capacitySlots;const selected=[];for(const offer of offers.filter(o=>o.load.occupiedSlots===1))if(offer.load.occupiedSlots<=remaining){selected.push(offer);remaining-=offer.load.occupiedSlots;}
 t.diagnostic(JSON.stringify({capacitySlots:g.nextBatchEffects.capacitySlots,returnedOffers:offers.length,oneSlotOffers:offers.filter(o=>o.load.occupiedSlots===1).length,selectedOrders:selected.length}));
 assert.ok(selected.length>8);assert.equal(g.acceptBatch(selected).length,selected.length);assert.equal(g.snapshot().batchIds.length,selected.length);
});

test('U22 production preview/acceptance share trusted held metres, batch protection and one rounded formula',()=>{
 for(const completed of [14,15]){
  const source=gameWithCompleted(completed),bytes=source.serialize(),offer=source.normalCandidates()[0];
  const preview=V2GameSession.restore(city,bytes,{preserveClock:true}),actual=V2GameSession.restore(city,bytes,{preserveClock:true});
  const quoted=preview.acceptBatch([{...offer,ordinaryPricing:{deliveryMetres:999999},incomeCents:1,factor:999}]);
  const accepted=actual.acceptBatch([offer]);assert.deepEqual(quoted,accepted);assert.equal(source.serialize(),bytes);
  const q=accepted[0],D=Math.max(1,Math.round(source.route.fastest(offer.pickupNode,offer.dropoffNode).heldMetres));
  assert.equal(q.ordinaryPricing.deliveryMetres,D);assert.equal(q.ordinaryPricing.version,'distance-effort-slots-v1');
  const N=completed<15?10000:9000+Math.min(D,2000);const base=2000*q.incomeFactor*q.xpMultiplier;
  assert.equal(q.incomeCents,Math.round(base*(N/10000)));assert.equal(slotOrdinaryIncomeCents(q.mapId,q.incomeFactor,q.xpMultiplier,completed,D),q.incomeCents);
  assert.doesNotThrow(()=>V2GameSession.restore(city,actual.serialize(),{preserveClock:true}));
 }
});

test('legacy U22 protects a whole crossing batch and applies the unrounded post-protection tariff once',()=>{
 const protectedEconomy=richEconomy('kg-v1');for(let i=0;i<14;i++){protectedEconomy.acceptOrdinary(`protected-${i}`);protectedEconomy.completeDelivery(`protected-${i}`);}
 const car=protectedEconomy.buyVehicle(3);protectedEconomy.assignVehicle('hero',car);const byId=Object.create(null),orders=[0,1000,2000].map((metres,i)=>{const id=`cross-${i}`;byId[id]={deliveryMetres:metres};return {id,kind:'ordinary',weightKg:1};});
 const quotes=protectedEconomy.acceptBatch(orders,byId);assert.deepEqual(quotes.map(q=>q.heroOrderOrdinal),[15,16,17]);assert.ok(quotes.every(q=>q.heroCompletedAtAcceptance===14&&q.xpMultiplier===1&&q.incomeCents===3000));assert.equal(quotes[0].ordinaryPricing.deliveryMetres,1);
 const e=richEconomy('kg-v1');for(let i=0;i<15;i++){e.acceptOrdinary(`unprotected-${i}`);e.completeDelivery(`unprotected-${i}`);}const street=e.buyVehicle(1);e.assignVehicle('hero',street);e.buyMap(2);e.selectMap(2);
 const q=e.acceptBatch([{id:'round-once',kind:'ordinary',weightKg:3}],priceContext('round-once',2000))[0];assert.equal(q.xpMultiplier,1.03);assert.equal(q.incomeCents,4005);assert.notEqual(q.incomeCents,Math.round(Math.round(2700*1.2*1.03)*1.2));
});

test('new slots contexts reject missing/extra/inherited metadata atomically and accept an own __proto__ ID',()=>{
 const e=richEconomy(),id='toString',orders=[{id,kind:'ordinary'}],before=e.serialize(),inherited=Object.create({toString:{deliveryMetres:1000}});
 for(const byId of [undefined,null,{},inherited,{toString:{deliveryMetres:1000},extra:{deliveryMetres:1}},{toString:{deliveryMetres:-1}},{toString:{deliveryMetres:NaN}},{toString:{deliveryMetres:1,version:'injected'}}]){assert.throws(()=>e.acceptSlotBatch(orders,byId));assert.equal(e.serialize(),before);}
 const q=e.acceptSlotBatch([{id:'__proto__',kind:'ordinary'}],priceContext('__proto__',0))[0];assert.equal(q.ordinaryPricing.deliveryMetres,1);assert.doesNotThrow(()=>V2EconomySession.restore(e.serialize()));
});

test('new completed and cancelled slot quotes retain strict historical metadata validation',()=>{
 const port={verifyArrival:()=>true};for(const status of ['completed','cancelled']){
  let d=new V2DispatchSession(port,0,'slots-v1');const initial=JSON.parse(d.serialize());initial.economy.state.cashCents=100000000;initial.economy.state.ledger.opening.balanceCents=100000000;initial.fleet.economy=clone(initial.economy);d=V2DispatchSession.restore(JSON.stringify(initial),port,{preserveClock:true});
  const id=`history-${status}`;d.acceptSlotBatch([{id,kind:'ordinary',load:slotLoadForOrderId(id)}],priceContext(id));if(status==='completed')d.completeDelivery(id,'verified',0);else d.cancelDelivery(id);
  const bytes=d.serialize();assert.doesNotThrow(()=>V2DispatchSession.restore(bytes,port));
  for(const mutate of [q=>q.ordinaryPricing=null,q=>q.ordinaryPricing.version='future',q=>q.ordinaryPricing.deliveryMetres=0,q=>q.incomeCents++,q=>q.terms.capacity.capacitySlots++]){const invalid=JSON.parse(bytes);mutate(invalid.orders.find(o=>o.id===id).quote);assert.throws(()=>V2DispatchSession.restore(JSON.stringify(invalid),port));}
 }
});

test('planned ETA is detached and mirrors approved road/service units with safe late suppression',()=>{
 const g=new V2GameSession(city),offer=g.normalCandidates()[0];g.acceptBatch([offer]);const before=g.serialize(),choices=g.routeChoices(),speed=g.deliveryEffects.speedRelativeToStarter;
 assert.ok(choices.length>0);for(const choice of choices){assert.equal(choice.orders.length,choice.arrivals.length);for(const o of choice.orders){const a=choice.arrivals.find(a=>a.id===o.id);assert.ok(a);assert.equal(o.etaRealSeconds,a.roadSeconds/(40*speed)+a.serviceSeconds);assert.equal(o.etaGameSeconds,a.roadSeconds+a.serviceSeconds*30);assert.equal(o.lateGameSeconds,0);}}
 choices[0].arrivals[0].roadSeconds=999;assert.equal(g.serialize(),before);assert.notEqual(g.routeChoices()[0].arrivals[0].roadSeconds,999);
});

test('legacy kg in-flight contracts preserve quote, food draw and units; next accepted batch uses slots',()=>{
 const raw=legacyGameRaw(),oldQuote=clone(raw.dispatch.orders[0].quote),oldTrip=clone(raw.tripState);
 const g=V2GameSession.restore(city,JSON.stringify(raw),{preserveClock:true});assert.equal(g.deliveryEffects.capacity.version,'kg-v1');
 assert.equal(g.snapshot().orders[0].quote.incomeCents,oldQuote.incomeCents);assert.equal(contractTerms(g.snapshot().orders[0].quote).version,'kg-v1');
 assert.equal(g.tripState.version,2);assert.equal(g.tripState.orders[0].draw,oldTrip.orders[0].draw);
 assert.equal(g.tripState.orders[0].deadlineGameSeconds,oldTrip.orders[0].deadlineGameSeconds);
 g.tick(1,.125,true,false);const at=g.routeMotion.position;g.cancelDelivery(oldQuote.id);assert.deepEqual(g.routeMotion.position,at);
 const next=g.normalCandidates()[0];const q=g.acceptBatch([next])[0];assert.equal(q.terms.version,'slots-v1');assert.equal(g.tripState.version,3);
 assert.doesNotThrow(()=>V2GameSession.restore(city,g.serialize(),{preserveClock:true}));
});

test('kg and slots fleet restoration enforce reserved vehicles while allowing the original rider future null/free vehicle',()=>{
 for(const profile of ['kg-v1','slots-v1']){
  const f=team(profile,2);for(let i=0;i<3;i++)hero(f,`reserve-${i}`);f.advanceTo(1);const bytes=f.serialize(),old=f.state.batches.find(b=>b.riderId==='npc-1');
  for(const future of ['null','free']){
   const legal=V2FleetSession.restore(bytes),vehicle=future==='free'?legal.economy.buyVehicle(2):null;legal.economy.assignVehicle('npc-1',vehicle);
   const restored=V2FleetSession.restore(legal.serialize());assert.equal(restored.state.batches.find(b=>b.id===old.id).vehicleId,old.vehicleId);
  }
  for(const other of ['hero','npc-2']){
   const invalid=JSON.parse(bytes);invalid.economy.state.riders.find(r=>r.id==='npc-1').vehicleId=null;invalid.economy.state.riders.find(r=>r.id===other).vehicleId=old.vehicleId;
   assert.throws(()=>V2FleetSession.restore(JSON.stringify(invalid)));
  }
  const invalid=JSON.parse(bytes);invalid.economy.state.riders.find(r=>r.id==='npc-1').vehicleId=null;invalid.economy.state.riders[0].vehicleId=old.vehicleId;
  const e=V2EconomySession.restore(JSON.stringify(invalid.economy));
  if(profile==='slots-v1')e.acceptSlotBatch([{id:'reserved-hero',kind:'ordinary'}],priceContext('reserved-hero'));else e.acceptOrdinary('reserved-hero');
  invalid.economy=JSON.parse(e.serialize());assert.throws(()=>V2FleetSession.restore(JSON.stringify(invalid)));
 }
});

test('NPC zero-quota 0->60 with actual hero completion at 10 equals 0->10->60; repeat/rollback never refill',()=>{
 const coarse=tenSecondGame(),split=tenSecondGame();assert.equal(coarse.dispatch.fleetState.quotaMs,0);
 context(coarse,60);coarse.tick(1,60,true,false);context(split,10);split.tick(1,10,true,false);context(split,60);split.tick(2,60,true,false);
 assert.deepEqual(coarse.dispatch.fleetState,split.dispatch.fleetState);assert.equal(coarse.dispatch.economyState.cashCents,split.dispatch.economyState.cashCents);
 assert.equal(coarse.dispatch.fleetState.quotaMs,10000);assert.equal(coarse.dispatch.economyState.heroCompletedOrders,1);
 const entry=coarse.dispatch.economyState.ledger.entries.find(e=>e.id==='order:ten-second');assert.equal(entry.atMs,10000);
 const cash=coarse.dispatch.economyState.cashCents,quota=coarse.dispatch.fleetState.quotaMs,cursor=coarse.dispatch.fleetState.heroEventCursor;
 coarse.tick(1,60,true,false);coarse.tick(2,5,true,false);assert.equal(coarse.dispatch.economyState.cashCents,cash);assert.equal(coarse.dispatch.fleetState.quotaMs,quota);assert.equal(coarse.dispatch.fleetState.heroEventCursor,cursor);
});

test('hero completion and supply purchase use their own absolute local-day instant and restore frame context',()=>{
 const midnight=Date.UTC(2026,10,6,16),start=midnight/1000-5,g=tenSecondGame(start),end=start+60;context(g,end);
 const frameContext=g.dispatch.economyState.ledgerContext;g.supply('water');
 let entry=g.dispatch.economyState.ledger.entries.find(e=>e.category==='supply_purchase');assert.equal(entry.atMs,Math.floor(start*1000));assert.equal(entry.dayKey,'2026-11-06');assert.deepEqual(g.dispatch.economyState.ledgerContext,frameContext);
 g.tick(1,end,true,false);entry=g.dispatch.economyState.ledger.entries.find(e=>e.id==='order:ten-second');
 assert.equal(entry.atMs,Math.floor(start*1000)+11000);assert.equal(entry.dayKey,'2026-11-07');assert.deepEqual(g.dispatch.economyState.ledgerContext,frameContext);
});

test('Fleet catch-up credits each workAt on its local day without migrating old unknown-date ledger rows',()=>{
 const midnight=Date.UTC(2026,10,6,16),start=midnight-110000,e=richEconomy('kg-v1');e.hireRider('npc-1');e.assignVehicle('npc-1',e.buyVehicle(1));
 const f=new V2FleetSession(e,start);for(let i=0;i<3;i++)hero(f,`date-${i}`);const unknown=f.economy.state.ledger.entries.filter(e=>e.category==='hero_ordinary').map(e=>e.id);
 f.setLedgerDayKeyResolver(day);const end=midnight+60000,frameContext={nowMs:end,dayKey:day(end)};f.economy.setLedgerContext(frameContext);f.advanceTo(end);
 const rows=f.economy.state.ledger.entries.filter(e=>e.category==='npc_delivery');assert.ok(rows.length>=2);assert.deepEqual(new Set(rows.map(e=>e.dayKey)),new Set(['2026-11-06','2026-11-07']));
 for(const row of rows)assert.equal(row.dayKey,day(row.atMs));for(const id of unknown)assert.equal(f.economy.state.ledger.entries.find(e=>e.id===id).dayKey,null);
 assert.deepEqual(f.economy.state.ledgerContext,frameContext);
});

test('same millisecond NPC old due is settled before hero credit and quota sync',()=>{
 const port={verifyArrival:()=>true};let d=new V2DispatchSession(port);const raw=JSON.parse(d.serialize());raw.economy.state.cashCents=100000000;raw.economy.state.ledger.opening.balanceCents=100000000;raw.fleet.economy=clone(raw.economy);d=V2DispatchSession.restore(JSON.stringify(raw),port,{preserveClock:true});
 const car=d.command({type:'buyVehicle',modelId:1});d.command({type:'hireRider',riderId:'npc-1'});d.command({type:'assignVehicle',riderId:'npc-1',vehicleId:car});
 for(let i=0;i<3;i++){d.acceptBatch([{id:`tie-warm-${i}`,kind:'ordinary',weightKg:1}]);d.completeDelivery(`tie-warm-${i}`,'verified',0);}
 d.advanceFleetTo(.001);const fleet=d.fleetState,batch=fleet.batches[0],due=fleet.lastAdvancedAt+batch.orders[batch.paidCount].dueMs-batch.elapsedMs;
 d.acceptBatch([{id:'tie-hero',kind:'ordinary',weightKg:1}]);d.setLedgerDayKeyResolver(day);d.completeDelivery('tie-hero','verified',due/1000);
 const entries=d.economyState.ledger.entries,npc=entries.findIndex(e=>e.id===`order:${batch.orders[0].id}`),heroIndex=entries.findIndex(e=>e.id==='order:tie-hero');
 assert.ok(npc>=0&&npc<heroIndex);assert.equal(entries[npc].atMs,due);assert.equal(entries[heroIndex].atMs,due);
});

test('planned supply consumes real action/cash but not trip deadline clock; active supply retains its clock',()=>{
 const g=richGame(),raw=JSON.parse(g.serialize());raw.tripState.stamina=50;
 const s=V2GameSession.restore(city,JSON.stringify(raw),{preserveClock:true}),offer=s.normalCandidates()[0];s.acceptBatch([offer]);const deadlines=s.tripState.orders.map(o=>o.deadlineGameSeconds);
 s.supply('water');const cash=s.dispatch.economyState.cashCents;s.tick(1,1,true,false);assert.equal(s.tripState.action,null);assert.equal(s.tripState.stamina,70);assert.equal(s.tripState.gameSeconds,0);assert.deepEqual(s.tripState.orders.map(o=>o.deadlineGameSeconds),deadlines);assert.equal(s.dispatch.economyState.cashCents,cash);
 s.beginTrip();s.supply('water');s.tick(2,2,true,false);assert.equal(s.tripState.gameSeconds,30);
});

test('food-risk metadata changes category risk without adding draws; canonical Game inputs and malformed foods reject',()=>{
 const orders=[{id:'food-order',fastestGameSeconds:10,heldMetres:100,safe:false}],legacy=new V2TripRules(),classified=new V2TripRules();
 legacy.begin(1,9,orders);classified.begin(1,9,orders,{'food-order':{version:'food-risk-v1',foodId:'soup-noodles',fragility:'fragile'}});
 assert.equal(legacy.state.seed,classified.state.seed);assert.equal(legacy.state.orders[0].draw,classified.state.orders[0].draw);assert.equal(legacy.state.orders[0].severityDraw,classified.state.orders[0].severityDraw);
 legacy.pickupGroup(['food-order']);classified.pickupGroup(['food-order']);legacy.travel(100,10);classified.travel(100,10);assert.ok(classified.state.orders[0].risk>legacy.state.orders[0].risk);
 const bad=classified.state;bad.orders[0].food=undefined;assert.throws(()=>V2TripRules.restore(bad));
 const g=new V2GameSession(city),offer=g.normalCandidates()[0],before=g.serialize(),food=foodForV2Order(offer.id);assert.throws(()=>g.acceptBatch([{...offer,food:{...food,fragility:food.fragility==='fragile'?'durable':'fragile'}}]));assert.equal(g.serialize(),before);
});

test('snapshot, tick context and nested frozen-effect projections are detached from live authority',()=>{
 const g=richGame(),offer=g.normalCandidates()[0];g.acceptBatch([offer]);const before=g.dispatch.serialize(),snapshot=g.dispatch.snapshot();
 snapshot.orders[0].load.occupiedSlots=99;snapshot.orders[0].quote.terms.capacity.capacitySlots=99;snapshot.batchIds.push('foreign');snapshot.frame.sequence=999;snapshot.economy.state.cashCents=0;snapshot.fleet.economy.state.cashCents=0;snapshot.rewards.autoRemainingSeconds=600;
 assert.equal(g.dispatch.serialize(),before);const ctx=g.dispatch.tickContext;ctx.sequence=999;ctx.pendingAd=true;assert.notEqual(g.dispatch.tickContext.sequence,999);assert.equal(g.dispatch.tickContext.pendingAd,false);
 const capacity=g.deliveryEffects.capacity.capacitySlots,effects=g.deliveryEffects;effects.capacity.capacitySlots=999;assert.equal(g.deliveryEffects.capacity.capacitySlots,capacity);
});

test('slots NPC payouts are per-order idempotent across restore and repeated/rollback advances',()=>{
 const f=team('slots-v1');for(let i=0;i<6;i++)hero(f,`slot-ledger-${i}`);f.advanceTo(300000);
 const entries=f.economy.state.ledger.entries.filter(e=>e.category==='npc_delivery');assert.ok(entries.length>0);assert.equal(new Set(entries.map(e=>e.id)).size,entries.length);
 const before=f.serialize(),cash=f.economy.state.cashCents;assert.equal(f.economy.settleFleetOrder(entries[0].detail.orderId),0);assert.equal(f.economy.state.cashCents,cash);
 f.advanceTo(300000);f.advanceTo(1);assert.equal(f.serialize(),before);const resumed=V2FleetSession.restore(before);resumed.advanceTo(300000);assert.equal(resumed.serialize(),before);
});

test('an accepted slots NPC batch keeps locked effects and prices through vehicle/rider upgrades',()=>{
 const f=team('slots-v1');for(let i=0;i<5;i++)hero(f,`locked-effects-${i}`);f.advanceTo(1);const old=clone(f.state.batches[0]),terms=clone(old.orders[0].terms);
 f.economy.upgradeVehicle(old.vehicleId);f.economy.upgradeRider('npc-1');assert.deepEqual(f.state.batches[0].orders,old.orders);assert.equal(terms.vehicleLevel,1);assert.equal(terms.riderLevel,1);
 const before=f.economy.state.cashCents;f.advanceTo(old.orders[old.orders.length-1].dueMs);assert.equal(f.economy.state.cashCents-before,old.orders.reduce((n,o)=>n+o.incomeCents,0));
 f.advanceTo(f.state.lastAdvancedAt+1);const next=f.state.batches[0];assert.ok(next.id!==old.id);assert.equal(next.orders[0].terms.vehicleLevel,2);assert.equal(next.orders[0].terms.riderLevel,2);assert.doesNotThrow(()=>V2FleetSession.restore(f.serialize()));
});

test('Game automatic 600-second final slice stops at its true in-flight state while NPC wall clock reaches frame end',()=>{
 const g=richGame();g.configureAutoSupply({enabled:true,budgetCents:10000,allowPaid:true});const ticket=g.dispatch.requestAd('auto',null,0,30);g.dispatch.resolveAd(ticket,'completed',1);
 const result=g.tick(1,2000,true,false);assert.equal(result.autoRunSeconds,600);assert.equal(g.snapshot().rewards.autoRemainingSeconds,0);assert.equal(g.snapshot().control,'manual');assert.equal(g.dispatch.fleetState.lastAdvancedAt,2000000);
 assert.ok(g.dispatch.economyState.heroCompletedOrders>0);const position=g.routeMotion.position,completed=g.dispatch.economyState.heroCompletedOrders;g.tick(2,2000,true,false);assert.deepEqual(g.routeMotion.position,position);assert.equal(g.dispatch.economyState.heroCompletedOrders,completed);
 assert.doesNotThrow(()=>V2GameSession.restore(city,g.serialize(),{preserveClock:true}));
});

test('paused/background/resume edges freeze hero but do not freeze already-earned NPC quota',()=>{
 const g=tenSecondGame(),data=deliveryCity();g.tick(1,60,true,false);g.acceptBatch([g.normalCandidates()[0]]);g.beginTrip();
 const position=g.routeMotion.position,clock=g.tripState.gameSeconds;g.tick(2,65,true,true);assert.deepEqual(g.routeMotion.position,position);assert.equal(g.tripState.gameSeconds,clock);assert.equal(g.dispatch.fleetState.quotaMs,5000);
 g.tick(3,67,false,false);g.tick(4,68,true,false);assert.deepEqual(g.routeMotion.position,position);assert.equal(g.tripState.gameSeconds,clock);assert.equal(g.dispatch.fleetState.quotaMs,2000);
 assert.doesNotThrow(()=>V2GameSession.restore(data,g.serialize(),{preserveClock:true}));
});

test('pending advertisement is sampled before expiry, so an expired wait interval cannot become hero travel',()=>{
 const g=tenSecondGame(),candidate=g.dispatch.enterLobby('pending-fixture',0,0);g.dispatch.requestAd('special',candidate.id,0,5);
 const position=g.routeMotion.position,clock=g.tripState.gameSeconds;g.tick(1,60,true,false);assert.deepEqual(g.routeMotion.position,position);assert.equal(g.tripState.gameSeconds,clock);assert.equal(g.dispatch.economyState.heroCompletedOrders,0);assert.equal(g.dispatch.tickContext.pendingAd,false);
 g.tick(2,61,true,false);assert.ok(g.tripState.gameSeconds>clock);assert.equal(g.dispatch.economyState.heroCompletedOrders,0);
});

function storage(seed={}){const values=new Map(Object.entries(seed)),writes=[];return {values,writes,getItem:key=>values.has(key)?values.get(key):null,setItem:(key,value)=>{writes.push([key,value]);values.set(key,value);},removeItem:key=>values.delete(key)};}
function writer(available=true){return {writable:available,async acquire(){return available;},release(){this.writable=false;}};}

test('single slot refuses existing new, corrupt/future restore, lost writer, epoch and external-byte overwrite',async()=>{
 const bytes=new V2GameSession(city).serialize();let fresh=0;
 const existing=storage({[KEY]:bytes,[EPOCH]:'generation'}),newStore=new V2RuntimeStore(existing,writer());await assert.rejects(newStore.open('new',()=>{},()=>{fresh++;}),/已有/);assert.equal(existing.values.get(KEY),bytes);assert.equal(fresh,0);
 for(const invalid of ['{bad',JSON.stringify({format:'county-v2-game',version:99})]){const memory=storage({[KEY]:invalid,[EPOCH]:'g'}),store=new V2RuntimeStore(memory,writer());await assert.rejects(store.open('continue',raw=>V2GameSession.restore(city,raw),()=>{fresh++;}),/保留/);assert.equal(memory.values.get(KEY),invalid);}
 const denied=storage({[KEY]:bytes,[EPOCH]:'g'});await assert.rejects(new V2RuntimeStore(denied,writer(false)).open('continue',()=>{},()=>{}),/关闭/);assert.equal(denied.writes.length,0);
 const memory=storage({[KEY]:bytes,[EPOCH]:'g'}),store=new V2RuntimeStore(memory,writer());await store.open('continue',raw=>V2GameSession.restore(city,raw),()=>{});memory.values.set(KEY,'external');assert.throws(()=>store.commit(bytes),/改变/);assert.equal(memory.values.get(KEY),'external');assert.equal(store.writable,false);
 const epochMemory=storage({[KEY]:bytes,[EPOCH]:'g'}),epochStore=new V2RuntimeStore(epochMemory,writer());await epochStore.open('continue',raw=>V2GameSession.restore(city,raw),()=>{});epochMemory.values.set(EPOCH,'new-g');assert.equal(epochStore.writable,false);assert.throws(()=>epochStore.commit(bytes));assert.equal(epochMemory.values.get(KEY),bytes);
});

test('single slot adapter write failure preserves prewrite bytes and stops later commits',async()=>{
 const bytes=new V2GameSession(city).serialize(),memory=storage({[KEY]:bytes,[EPOCH]:'g'}),normalSet=memory.setItem;
 memory.setItem=(key,value)=>{if(key===KEY)throw new Error('fixture quota failure before write');normalSet(key,value);};
 const store=new V2RuntimeStore(memory,writer());await store.open('continue',raw=>V2GameSession.restore(city,raw),()=>{});assert.throws(()=>store.commit(bytes),/quota/);assert.equal(memory.values.get(KEY),bytes);assert.equal(store.writable,false);assert.throws(()=>store.commit(bytes));
});
