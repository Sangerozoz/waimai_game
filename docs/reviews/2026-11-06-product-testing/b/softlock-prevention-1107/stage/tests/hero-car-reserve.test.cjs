// Behavioral tests of public commands; no real storage, ads, wallet or quota injection.
'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const base=path.dirname(process.env.MAP_ROUTER_MODULE);
const {V2EconomySession}=require(path.join(base,'../domain/V2EconomySession.js'));
const {V2FleetSession}=require(path.join(base,'../domain/V2FleetSession.js'));
const {V2GameSession}=require(path.join(base,'V2GameSession.js'));
const {prepareCity}=require(path.join(base,'PlaceCatalog.js'));
const ROOT=process.env.HERO_CAR_RESERVE_ROOT||path.resolve(__dirname,'../../..');
const history=JSON.parse(fs.readFileSync(process.env.HERO_CAR_RESERVE_HISTORY||path.join(ROOT,'docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/historical-fixtures.json'),'utf8'));
const pm=JSON.parse(fs.readFileSync(path.join(ROOT,'docs/balance/2026-11-06-balance-round-01/pm/only-car-reproduction-1107.json'),'utf8'));
const city=prepareCity(JSON.parse(fs.readFileSync(path.join(ROOT,'delivery-game/assets/resources/map-sample/city.json'),'utf8')));
const message=/请为主角保留一辆可用车辆/;
const historic=(profile,name)=>V2FleetSession.restore(JSON.stringify(history.fixtures[profile][name]));
function completeHero(f,id){
 const e=f.economy;
 if(e.usesSlots)e.acceptSlotBatch([{id,kind:'ordinary'}],{[id]:{deliveryMetres:100}});else e.acceptOrdinary(id);
 return f.completeHeroDelivery(id);
}
function register(e,id){return e.usesSlots?e.registerSlotFleetOrders('npc-1',[id]):e.registerFleetOrders('npc-1',[id],[1]);}
function earnedTeam(profile,count=30){const f=new V2FleetSession(new V2EconomySession(profile),0);for(let i=0;i<count;i++)completeHero(f,'earned-'+profile+'-'+i);return f;}
test('one earned delivery cannot surrender the last recoverable hero car',()=>{
 const e=new V2EconomySession('slots-v1'),id='reserve-first';
 e.acceptSlotBatch([{id,kind:'ordinary'}],{[id]:{deliveryMetres:100}});
 assert.equal(e.completeDelivery(id).incomeCents,2000);
 e.hireRider('npc-1');assert.equal(e.state.cashCents,0);
 e.assignVehicle('hero',null);const before=e.serialize();
 assert.throws(()=>e.assignVehicle('npc-1','starter-1'),/请为主角保留一辆可用车辆/);
 assert.equal(e.serialize(),before);
 e.assignVehicle('hero','starter-1');assert.equal(e.state.riders[0].vehicleId,'starter-1');
});

test('real Game/Dispatch commands reject surrender atomically and the hero can continue delivery',()=>{
 const g=new V2GameSession(city,0);let now=0,sequence=0;
 function finishOne(){
  g.acceptBatch([g.normalCandidates()[0]]);g.beginTrip(g.routeChoices()[0].preference);
  const previous=g.dispatch.economyState.heroCompletedOrders;
  for(let i=0;g.dispatch.economyState.heroCompletedOrders===previous&&i<1000;i++){
   const phase=g.route.progress.phase;
   if(phase==='pickup')g.pickup();else if(phase==='ready')g.continueTrip();else g.tick(++sequence,now+=.5,true,false);
  }
  assert.equal(g.dispatch.economyState.heroCompletedOrders,previous+1);
 }
 finishOne();assert.equal(g.dispatch.economyState.cashCents,12000);
 g.dispatch.command({type:'hireRider',riderId:'npc-1'});
 g.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:null});
 const before=g.serialize();
 assert.throws(()=>g.dispatch.command({type:'assignVehicle',riderId:'npc-1',vehicleId:'starter-1'}),message);
 assert.equal(g.serialize(),before);assert.equal(g.dispatch.economyState.cashCents,0);
 g.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:'starter-1'});
 finishOne();assert.equal(g.dispatch.economyState.cashCents,2000);
});

for(const profile of ['kg-v1','slots-v1']){
 test(profile+': proposed assignments reserve a real owned car, not future purchasing power',()=>{
  const f=earnedTeam(profile),e=f.economy;
  e.hireRider('npc-1');assert.ok(e.state.cashCents>=30000);
  e.assignVehicle('hero',null);let before=e.serialize();
  assert.throws(()=>e.assignVehicle('npc-1','starter-1'),message);assert.equal(e.serialize(),before);
  const paid=e.buyVehicle(1);e.hireRider('npc-2');e.assignVehicle('npc-1',paid);
  before=e.serialize();assert.throws(()=>e.assignVehicle('npc-2','starter-1'),message);assert.equal(e.serialize(),before);
  e.assignVehicle('npc-1',null);e.assignVehicle('npc-2','starter-1');
  assert.equal(e.hasRecoverableHeroVehicle,true);e.assignVehicle('hero',paid);
 });

 test(profile+': both public contract registration profiles reject dangerous historic state atomically',()=>{
  const f=historic(profile,'beforeSigning'),e=f.economy,before=e.serialize();
  assert.throws(()=>register(e,'reserve-direct-'+profile),message);
  assert.equal(e.serialize(),before);assert.equal(e.state.fleetQuotes.length,0);
 });

 test(profile+': restore accepts the old risky assignment, repeated nonempty assignment is guarded, detaching permits recovery',()=>{
  const raw=JSON.stringify(history.fixtures[profile].beforeSigning),f=V2FleetSession.restore(raw),e=f.economy;
  assert.equal(f.serialize(),raw);const before=e.serialize();
  assert.equal(e.hasRecoverableHeroVehicle,false);assert.equal(e.serialize(),before);
  assert.throws(()=>e.assignVehicle('npc-1','starter-1'),message);assert.equal(e.serialize(),before);
  e.assignVehicle('npc-1',null);assert.equal(e.hasRecoverableHeroVehicle,true);
  e.assignVehicle('hero','starter-1');assert.equal(e.state.riders[0].vehicleId,'starter-1');
 });

 test(profile+': Fleet skips unsafe automatic signing without throwing, spending quota or minting money',()=>{
  const f=historic(profile,'beforeSigning'),quota=f.state.quotaMs,cash=f.economy.state.cashCents,ledger=f.economy.state.ledger;
  assert.doesNotThrow(()=>f.advanceTo(300000));
  assert.equal(f.state.batches.length,0);assert.equal(f.state.nextBatchId,1);assert.equal(f.state.quotaMs,quota);
  assert.equal(f.economy.state.cashCents,cash);assert.deepEqual(f.economy.state.ledger,ledger);
  assert.equal(f.economy.state.fleetQuotes.length,0);assert.equal(f.state.lastAdvancedAt,300000);
  f.economy.assignVehicle('npc-1',null);f.economy.assignVehicle('hero','starter-1');
  assert.equal(f.economy.state.riders[0].vehicleId,'starter-1');
 });

 test(profile+': a historic signed batch still finishes with its original quota and terms, without signing another unsafe batch',()=>{
  const f=historic(profile,'signedRemaining'),e=f.economy,old=f.state.batches[0],cash=e.state.cashCents;
  assert.equal(f.state.quotaMs,179000);assert.equal(old.elapsedMs,1000);
  f.advanceTo(50000);assert.equal(f.state.batches[0].elapsedMs,50000);
  assert.deepEqual(f.state.batches[0].orders,old.orders);assert.equal(e.state.cashCents,cash);
  f.advanceTo(300000);
  assert.equal(e.state.npcCompletedOrders,profile==='slots-v1'?2:1);
  assert.equal(e.state.cashCents,cash+(profile==='slots-v1'?4000:2000));
  assert.equal(f.state.quotaMs,profile==='slots-v1'?45000:90000);
  assert.equal(f.state.nextBatchId,2);assert.equal(f.state.batches.length,0);assert.equal(e.state.fleetQuotes.length,0);
  const quota=f.state.quotaMs;f.advanceTo(600000);assert.equal(f.state.quotaMs,quota);assert.equal(f.state.batches.length,0);
  e.assignVehicle('npc-1',null);e.assignVehicle('hero','starter-1');
  assert.equal(V2FleetSession.restore(f.serialize()).serialize(),f.serialize());
 });

 test(profile+': an unequipped old contract vehicle never counts as a spare for a different configured NPC',()=>{
  const f=historic(profile,'reservedOldCarAndConfiguredNewCar'),e=f.economy,car=e.state.riders.find(r=>r.id==='npc-2').vehicleId;
  const contracts=e.state.fleetQuotes,before=e.serialize();assert.equal(e.hasRecoverableHeroVehicle,false);
  assert.throws(()=>e.assignVehicle('npc-2',car),message);assert.equal(e.serialize(),before);
  assert.throws(()=>e.usesSlots?e.registerSlotFleetOrders('npc-2',['reserve-old-contract']):e.registerFleetOrders('npc-2',['reserve-old-contract'],[1]),message);
  assert.equal(e.serialize(),before);e.assignVehicle('npc-2',null);assert.equal(e.hasRecoverableHeroVehicle,true);
  assert.throws(()=>e.assignVehicle('hero','starter-1'),/旧批次/);e.assignVehicle('hero',car);
  assert.deepEqual(e.state.fleetQuotes,contracts);
 });

 test(profile+': ten/fifteen earned-order budgets and an idle spare allow NPC assignment and direct signing',()=>{
  const f=earnedTeam(profile,10),e=f.economy,car=e.buyVehicle(1);e.assignVehicle('hero',car);
  assert.equal(e.state.cashCents,0);
  for(let i=10;i<15;i++)assert.equal(completeHero(f,'budget-'+profile+'-'+i).incomeCents,2400);
  e.hireRider('npc-1');assert.equal(e.state.cashCents,0);e.assignVehicle('hero',null);
  e.assignVehicle('npc-1','starter-1');assert.equal(e.hasRecoverableHeroVehicle,true);
  const raw=e.serialize();assert.equal(e.hasRecoverableHeroVehicle,true);assert.equal(e.serialize(),raw);
  const direct=V2EconomySession.restore(raw);assert.equal(register(direct,'reserve-allowed-'+profile).length,1);
  assert.equal(direct.hasRecoverableHeroVehicle,true);
  e.assignVehicle('hero',car);f.advanceTo(1000);assert.equal(f.state.batches.length,1);
 });
}

test('PM real Game historic pre-sign fixture restores unchanged and can return the car after skipped signing',()=>{
 const raw=JSON.stringify(pm.fixtures.beforeNPCSigning),g=V2GameSession.restore(city,raw,{preserveClock:true});
 assert.equal(g.serialize(),raw);const s=g.snapshot(),quota=s.fleet.fleet.quotaMs;
 g.tick(s.frame.sequence+1,s.frame.nowSeconds+60,true,false);
 assert.equal(g.dispatch.fleetState.quotaMs,quota);assert.equal(g.dispatch.fleetState.batches.length,0);
 assert.equal(g.dispatch.economyState.cashCents,0);
 g.dispatch.command({type:'assignVehicle',riderId:'npc-1',vehicleId:null});
 g.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:'starter-1'});
 assert.ok(g.normalCandidates().length>0);
});

test('PM real Game signed zero-quota fixture remains readable with identical contracts and no implicit rescue',()=>{
 const raw=JSON.stringify(pm.fixtures.signedZeroQuota),g=V2GameSession.restore(city,raw,{preserveClock:true});
 assert.equal(g.serialize(),raw);const s=g.snapshot(),contracts=g.dispatch.economyState.fleetQuotes,batches=g.dispatch.fleetState.batches;
 g.tick(s.frame.sequence+1,s.frame.nowSeconds+3600,true,false);
 assert.equal(g.dispatch.fleetState.quotaMs,0);assert.equal(g.dispatch.economyState.cashCents,0);
 assert.deepEqual(g.dispatch.economyState.fleetQuotes,contracts);assert.deepEqual(g.dispatch.fleetState.batches,batches);
 g.dispatch.command({type:'assignVehicle',riderId:'npc-1',vehicleId:null});const before=g.serialize();
 assert.throws(()=>g.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:'starter-1'}),/旧批次/);
 assert.equal(g.serialize(),before);assert.equal(g.normalCandidates().length,0);
 assert.equal(V2GameSession.restore(city,g.serialize(),{preserveClock:true}).serialize(),g.serialize());
});
