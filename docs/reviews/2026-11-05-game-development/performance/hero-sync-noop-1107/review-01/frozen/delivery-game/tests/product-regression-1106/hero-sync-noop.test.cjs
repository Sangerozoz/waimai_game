'use strict';
// Isolated real economy/fleet instances. Counts wallet serialization as a resource
// boundary; forwards every observed call and does not replace domain behavior.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {domain}=require('./helpers.cjs');
const {V2EconomySession}=domain('V2EconomySession');
const {V2FleetSession}=domain('V2FleetSession');

function complete(e,id){
 if(e.usesSlots)e.acceptSlotBatch([{id,kind:'ordinary'}],{[id]:{deliveryMetres:100}});
 else e.acceptOrdinary(id);
 return e.completeDelivery(id);
}

function assertNoOpWithoutWalletSerialization(f){
 const before=f.serialize(),e=f.economy,serialize=e.serialize;
 let calls=0;
 e.serialize=function(){calls++;return serialize.call(this);};
 try{
  for(let i=0;i<10;i++)f.syncHeroCompletions();
  assert.equal(calls,0,'already-consumed events must not repeatedly serialize the entire wallet');
 }finally{e.serialize=serialize;}
 assert.equal(f.serialize(),before,'no-op sync must preserve the complete combined state');
}

for(const profile of ['kg-v1','slots-v1']){
 test(`${profile}: an empty completion history sync avoids wallet serialization`,()=>{
  const f=new V2FleetSession(new V2EconomySession(profile),0);
  assertNoOpWithoutWalletSerialization(f);
  assert.equal(f.state.quotaMs,0);
 });

 test(`${profile}: consumed receipts do not trigger another wallet transaction or refill`,()=>{
  const f=new V2FleetSession(new V2EconomySession(profile),0);
  complete(f.economy,'sync-first');f.syncHeroCompletions();
  complete(f.economy,'sync-second');f.syncHeroCompletions();
  assert.equal(f.state.quotaMs,120000);assert.equal(f.state.heroCompletionsSeen,2);
  assertNoOpWithoutWalletSerialization(V2FleetSession.restore(f.serialize()));
 });

 test(`${profile}: restored unsynchronized events replenish once and later events remain visible`,()=>{
  const f=new V2FleetSession(new V2EconomySession(profile),0);
  complete(f.economy,'sync-pending');
  const restored=V2FleetSession.restore(f.serialize()),cash=restored.economy.state.cashCents;
  assert.equal(restored.state.heroEventCursor,0);assert.equal(restored.state.quotaMs,0);
  restored.syncHeroCompletions();
  assert.equal(restored.state.heroEventCursor,1);assert.equal(restored.state.heroCompletionsSeen,1);
  assert.equal(restored.state.quotaMs,60000);assert.equal(restored.economy.state.cashCents,cash);
  assertNoOpWithoutWalletSerialization(restored);
  complete(restored.economy,'sync-later');restored.syncHeroCompletions();
  assert.equal(restored.state.heroEventCursor,2);assert.equal(restored.state.heroCompletionsSeen,2);
  assert.equal(restored.state.quotaMs,120000);
  assertNoOpWithoutWalletSerialization(restored);
 });

 test(`${profile}: restore still rejects a cursor beyond history or an inconsistent completion count`,()=>{
  const f=new V2FleetSession(new V2EconomySession(profile),0);
  complete(f.economy,'sync-validated');f.syncHeroCompletions();
  const raw=JSON.parse(f.serialize());raw.fleet.heroEventCursor=2;
  assert.throws(()=>V2FleetSession.restore(JSON.stringify(raw)));
  raw.fleet.heroEventCursor=1;raw.fleet.heroCompletionsSeen=0;
  assert.throws(()=>V2FleetSession.restore(JSON.stringify(raw)));
 });
}
