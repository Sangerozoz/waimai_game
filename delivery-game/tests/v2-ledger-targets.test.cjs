// Pending stage-completion authorization: do not execute during implementation.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const domain=path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'../domain');
const {V2EconomySession}=require(path.join(domain,'V2EconomySession.js'));
const {queryProgressTargets}=require(path.join(domain,'V2ProgressTargets.js'));
const query={todayDayKey:'2026-11-04',recentDayKeys:['2026-11-03','2026-11-04']};
function deliver(s,id){s.acceptOrdinary(id);return s.completeDelivery(id);}
test('opening plus categorized cash movements reconciles and duplicate delivery is inert',()=>{
 const s=new V2EconomySession();s.setLedgerContext({nowMs:1793750400000,dayKey:'2026-11-04'});
 const r=deliver(s,'one');s.completeDelivery('one');s.chargeSupply(100,{supplyId:'water',transactionId:'buy-1'});s.chargeSupply(100,{supplyId:'water',transactionId:'buy-1'});
 const report=s.ledgerSummary(query);assert.equal(report.today.byCategory.hero_ordinary,r.incomeCents);assert.equal(report.today.byCategory.supply_purchase,-100);
 assert.equal(report.reconciliation.balanced,true);assert.equal(s.state.ledger.entries.length,2);
});
test('missing legacy ledger rejects without synthesizing historical flows or a replacement balance',()=>{
 const raw=JSON.parse(new V2EconomySession().serialize());delete raw.state.ledger;raw.state.cashCents=12345;
 assert.throws(()=>V2EconomySession.restore(JSON.stringify(raw)));
 const legal=new V2EconomySession();assert.equal(legal.state.ledger.entries.length,0);assert.equal(legal.ledgerSummary(query).reconciliation.balanced,true);
});
test('dated and unknown flows keep separate scopes and malformed or drifting ledger rejects restoration',()=>{
 const s=new V2EconomySession();deliver(s,'unknown');s.setLedgerContext({nowMs:1793664000000,dayKey:'2026-11-03'});deliver(s,'yesterday');
 const report=s.ledgerSummary(query);assert.equal(report.today.incomeCents,0);assert.equal(report.recentSevenDays.incomeCents,2000);assert.equal(report.unknownDate.incomeCents,2000);
 const raw=JSON.parse(s.serialize());raw.state.cashCents++;assert.throws(()=>V2EconomySession.restore(JSON.stringify(raw)),/账/);
});
test('targets reflect assets and affordability without spending or granting ten percent rewards',()=>{
 const s=new V2EconomySession();for(let i=0;i<10;i++)deliver(s,`o${i}`);
 const before=s.serialize(),targets=queryProgressTargets(s.state),car=targets.find(t=>t.id==='first-car');assert.equal(car.canGo,true);assert.equal(car.priceCents,30000);assert.equal(s.serialize(),before);
 s.buyVehicle(1);assert.equal(s.state.cashCents,0);assert.equal(queryProgressTargets(s.state).find(t=>t.id==='first-car').completed,true);
});
test('every actual asset expense and ordinary/special/NPC income has an actual category',()=>{
 const raw=JSON.parse(new V2EconomySession().serialize());raw.state.cashCents=100000000;raw.state.ledger.opening.balanceCents=raw.state.cashCents;
 const s=V2EconomySession.restore(JSON.stringify(raw));const car=s.buyVehicle(1);s.hireRider('npc-1');s.upgradeVehicle(car);s.upgradeRider('npc-1');s.buyMap(4);s.chargeSupply(1500,{supplyId:'meal',quantity:1,transactionId:'supply-1'});
 deliver(s,'ordinary');s.acceptBatch([{id:'special',kind:'special',weightKg:1,specialCoins:125}]);s.completeDelivery('special');
 s.assignVehicle('npc-1',car);const quote=s.registerFleetOrders('npc-1',['npc-order'],[1])[0];s.settleFleetOrder(quote.id);s.settleFleetOrder(quote.id);
 const categories=new Set(s.state.ledger.entries.map(e=>e.category));for(const c of ['vehicle_purchase','rider_hire','vehicle_upgrade','rider_upgrade','map_purchase','supply_purchase','hero_ordinary','hero_special','npc_delivery'])assert.ok(categories.has(c));
 assert.equal(s.state.ledger.entries.filter(e=>e.id==='order:npc-order').length,1);assert.equal(s.ledgerSummary(query).reconciliation.balanced,true);
 const saved=s.serialize();assert.throws(()=>s.chargeSupply(700,{supplyId:'meal',transactionId:'supply-1'}));assert.equal(s.serialize(),saved);
});
