// Pending stage-completion authorization. Never executed during implementation.
const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const base=path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'../domain');
const {V2EconomySession}=require(path.join(base,'V2EconomySession.js'));
const {V2FleetSession}=require(path.join(base,'V2FleetSession.js'));
function rich(){const raw=JSON.parse(new V2EconomySession().serialize());raw.state.cashCents=100000000;raw.state.ledger.opening.balanceCents=raw.state.cashCents;return V2EconomySession.restore(JSON.stringify(raw));}
function team(count=1){const e=rich();for(let i=1;i<=count;i++){e.hireRider(`npc-${i}`);e.assignVehicle(`npc-${i}`,e.buyVehicle(1));}return new V2FleetSession(e,0);}
function hero(f,id){f.economy.acceptOrdinary(id);f.completeHeroDelivery(id);}
test('no NPC can bank quota; repeat hero receipt does not refill; NPC-less elapsed time does not burn quota',()=>{
 const f=new V2FleetSession(new V2EconomySession(),0);hero(f,'h');f.completeHeroDelivery('h');f.advanceTo(3600000);
 assert.equal(f.state.quotaMs,60000);assert.equal(f.state.heroCompletionsSeen,1);
});
test('one real minute costs one shared minute regardless of NPC count; NPC never refills quota',()=>{
 const f=team(2);hero(f,'h');const before=f.economy.state.cashCents;f.advanceTo(60000);
 assert.equal(f.state.quotaMs,0);assert.equal(f.economy.state.cashCents,before); // street car needs road+service >60s
 const progress=f.state.batches.map(b=>b.elapsedMs);f.advanceTo(999999);assert.deepEqual(f.state.batches.map(b=>b.elapsedMs),progress);
});
test('online steps and offline interval give same unique payouts, preserve partial progress, ignore replay and rollback',()=>{
 const f=team();for(let i=0;i<5;i++)hero(f,`h${i}`);const initial=f.serialize();
 const online=V2FleetSession.restore(initial),offline=V2FleetSession.restore(initial);
 for(let t=1000;t<=300000;t+=1000)online.advanceTo(t);offline.advanceTo(300000);
 assert.equal(online.economy.state.cashCents,offline.economy.state.cashCents);
 assert.deepEqual(online.state,offline.state);const settled=offline.serialize();offline.advanceTo(200000);offline.advanceTo(300000);assert.equal(offline.serialize(),settled);
 const restored=V2FleetSession.restore(settled);restored.advanceTo(300000);assert.equal(restored.serialize(),settled);
});
test('old batch keeps old price and timing through upgrade, reassignment and map switch',()=>{
 const f=team();for(let i=0;i<5;i++)hero(f,`h${i}`);f.advanceTo(1000);const old=f.state.batches[0],q=old.orders[0];
 f.economy.upgradeVehicle(old.vehicleId);f.economy.upgradeRider('npc-1');f.economy.buyMap(2);f.economy.selectMap(2);f.economy.assignVehicle('npc-1',null);
 const before=f.economy.state.cashCents;f.advanceTo(old.orders[old.orders.length-1].dueMs);
 assert.equal(f.economy.state.cashCents-before,old.orders.reduce((s,o)=>s+o.incomeCents,0));
 assert.equal(q.incomeCents,2400);assert.equal(f.state.batches.length,0);
});
test('legal deterministic integer batches obey capacity; new batch uses current equipment and map',()=>{
 const f=team();for(let i=0;i<10;i++)hero(f,`h${i}`);f.advanceTo(1);const first=f.state.batches[0];
 assert.ok(first.orders.every(o=>Number.isInteger(o.weightKg)&&o.weightKg>0));assert.ok(first.orders.reduce((s,o)=>s+o.weightKg,0)<=3);
 f.economy.buyMap(2);f.economy.selectMap(2);f.advanceTo(first.orders[first.orders.length-1].dueMs+1);
 assert.equal(f.state.batches[0].mapId,2);assert.equal(f.state.batches[0].orders[0].incomeCents,3240);
});
test('quota thresholds grow without gifts and only hero completions refill',()=>{
 const f=new V2FleetSession(rich(),0);for(let i=0;i<59;i++)hero(f,`a${i}`);assert.equal(f.quotaCapacityMs,900000);
 hero(f,'60');assert.equal(f.quotaCapacityMs,1200000);assert.equal(f.state.quotaMs,1020000);
 for(let i=61;i<=240;i++)hero(f,`a${i}`);assert.equal(f.quotaCapacityMs,1500000);assert.equal(f.state.quotaMs,1320000);
 for(let i=241;i<=700;i++)hero(f,`a${i}`);assert.equal(f.quotaCapacityMs,1800000);assert.equal(f.state.quotaMs,1680000);
});
test('reject malformed clocks, inconsistent combined saves and forged income atomically',()=>{
 const f=team();hero(f,'h');const before=f.serialize();for(const t of [NaN,Infinity,-1,.5])assert.throws(()=>f.advanceTo(t));assert.equal(f.serialize(),before);
 f.advanceTo(1);const raw=JSON.parse(f.serialize());raw.fleet.batches[0].orders[0].incomeCents++;assert.throws(()=>V2FleetSession.restore(JSON.stringify(raw)));
 const e=f.economy.serialize();assert.throws(()=>f.economy.settleFleetOrder('unknown'));assert.equal(f.economy.serialize(),e);
});
test('economy multiple accepted orders complete in any order, keep quotes and cancel remainder without income',()=>{
 const e=rich();const q=e.acceptBatch([{id:'a',kind:'ordinary',weightKg:1},{id:'b',kind:'ordinary',weightKg:1}]);
 assert.equal(q[0].incomeCents,2000);const before=e.state.cashCents;e.completeDelivery('b');assert.equal(e.state.cashCents,before+2000);assert.equal(e.state.activeQuote.id,'a');
 e.cancelDelivery('a');assert.equal(e.state.heroCompletedOrders,1);assert.equal(e.state.heroExperience,10);assert.equal(e.state.activeQuote,null);
 assert.throws(()=>e.completeDelivery('a'));assert.equal(e.state.cashCents,before+2000);
});
test('a vehicle reserved by an accepted old NPC batch cannot be reused by another rider',()=>{
 const f=team(2);hero(f,'h');f.advanceTo(1);const car=f.state.batches[0].vehicleId;f.economy.assignVehicle('npc-1',null);assert.throws(()=>f.economy.assignVehicle('hero',car),/旧批次/);
});
test('restored historic hero count is a baseline and never creates retroactive quota',()=>{
 const e=rich();for(let i=0;i<5;i++){e.acceptOrdinary(`h${i}`);e.completeDelivery(`h${i}`);}
 const f=new V2FleetSession(e,0);f.syncHeroCompletions();assert.equal(f.state.quotaMs,0);hero(f,'new');assert.equal(f.state.quotaMs,60000);
});
