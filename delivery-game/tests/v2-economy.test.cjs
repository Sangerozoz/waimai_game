// Pending stage-completion authorization: intentionally not executed during implementation.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {V2EconomySession}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'../domain/V2EconomySession.js'));
const {V2_CONFIG}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'../domain/V2EconomyConfig.js'));
function deliver(session,id){session.acceptOrdinary(id);return session.completeDelivery(id);}
test('ten ordinary deliveries buy first new car; fifteen hire first NPC and reuse starter',()=>{
 const s=new V2EconomySession();
 for(let i=1;i<=9;i++)deliver(s,`o${i}`);
 assert.throws(()=>s.buyVehicle(1),/余额/);
 deliver(s,'o10');const car=s.buyVehicle(1);s.assignVehicle('hero',car);
 assert.equal(s.state.cashCents,0);
 for(let i=11;i<=15;i++)assert.equal(deliver(s,`o${i}`).incomeCents,2400);
 s.hireRider('npc-1');s.assignVehicle('npc-1','starter-1');
 assert.equal(s.state.cashCents,0);assert.equal(s.state.riders[1].vehicleId,'starter-1');
});
test('fixed identity recruit quote and failed transactions preserve ownership',()=>{
 const s=new V2EconomySession();assert.throws(()=>s.hireRider('npc-1'),/余额/);
 assert.equal(s.nextHirePriceCents,12000);assert.equal(s.state.hireCount,0);
});
test('new prices and table-driven cumulative upgrade totals match latest frontloaded candidate',()=>{
 assert.deepEqual(V2_CONFIG.vehicles.map(v=>v.price),[300,600,1000,1800,3000,5000,8000,12000,80000,160000]);
 assert.equal(V2_CONFIG.riders[24].price,880000);assert.equal(V2_CONFIG.upgradeLevels[29].riderCumulativeCost,1600);
});
test('reloading a completed receipt never pays twice; accepted quote survives equipment changes',()=>{
 const s=new V2EconomySession();s.acceptOrdinary('a');assert.throws(()=>s.assignVehicle('hero','starter-1'),/配送/);
 const receipt=s.completeDelivery('a'),saved=s.serialize();const restored=V2EconomySession.restore(saved);
 assert.deepEqual(restored.completeDelivery('a'),receipt);assert.equal(restored.state.cashCents,12000);
 assert.throws(()=>restored.acceptOrdinary('a'),/重复/);
});
test('unknown future schema/config fails closed and malformed assignments are rejected',()=>{
 const raw=JSON.parse(new V2EconomySession().serialize());raw.version=99;
 assert.throws(()=>V2EconomySession.restore(JSON.stringify(raw)),/版本/);
 raw.version=1;raw.state.riders.push({id:'npc-1',level:1,vehicleId:'starter-1'});raw.state.hireCount=1;
 assert.throws(()=>V2EconomySession.restore(JSON.stringify(raw)),/存档/);
});
test('money alone buys highest vehicle/map, upgrades exactly one instance, and assignment stays unique',()=>{
 const raw=JSON.parse(new V2EconomySession().serialize());raw.state.cashCents=100000000;raw.state.ledger.opening.balanceCents=raw.state.cashCents;
 const s=V2EconomySession.restore(JSON.stringify(raw));s.buyMap(5);
 const one=s.buyVehicle(10),two=s.buyVehicle(10);s.upgradeVehicle(one);
 assert.equal(s.state.vehicles.find(v=>v.id===one).level,2);assert.equal(s.state.vehicles.find(v=>v.id===two).level,1);
 s.hireRider('npc-12');s.assignVehicle('npc-12',one);assert.throws(()=>s.assignVehicle('hero',one),/占用/);
 const before=s.serialize();assert.throws(()=>s.buyMap(5),/已拥有/);assert.equal(s.serialize(),before);
});

test('a repeated old completion callback cannot settle a newer active order',()=>{
 const s=new V2EconomySession();const first=deliver(s,'old');s.acceptOrdinary('new');
 assert.deepEqual(s.completeDelivery('old'),first);assert.equal(s.state.activeQuote.id,'new');assert.equal(s.state.cashCents,12000);
 assert.throws(()=>s.completeDelivery('unrelated'),/不匹配/);assert.equal(s.completeDelivery('new').id,'new');
});
