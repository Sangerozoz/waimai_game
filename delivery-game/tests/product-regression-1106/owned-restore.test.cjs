'use strict';
// The input to every restore is a string. The observed JSON encoder forwards
// real calls; only redundant whole-aggregate encodings are counted, not timings.
const {test}=require('node:test'),assert=require('node:assert/strict');
const {domain}=require('./helpers.cjs');
const {V2EconomySession}=domain('V2EconomySession');
const {V2FleetSession}=domain('V2FleetSession');
const {V2DispatchSession}=domain('V2DispatchSession');
const port={verifyArrival:()=>true};

function observeEncoding(predicate,action){
 const original=JSON.stringify;let calls=0,result;
 JSON.stringify=function(value,...args){if(predicate(value))calls++;return Reflect.apply(original,this,[value,...args]);};
 try{result=action();}finally{JSON.stringify=original;}
 return {calls,result};
}
function accepted(d,id){
 if(d.usesSlots)d.acceptSlotBatch([{id,kind:'ordinary',load:domain('V2LoadRules').slotLoadForOrderId(id)}],{[id]:{deliveryMetres:100}});
 else d.acceptBatch([{id,kind:'ordinary',weightKg:1}]);
}

for(const profile of ['kg-v1','slots-v1']){
 test(`${profile}: Economy restore does not encode its privately parsed wallet again`,()=>{
  const raw=new V2EconomySession(profile).serialize();
  const observed=observeEncoding(v=>v?.format==='county-v2-economy',()=>V2EconomySession.restore(raw));
  assert.equal(observed.calls,0,'validated, freshly parsed economy must not be serialized again just to copy it');
  assert.equal(observed.result.serialize(),raw);
 });
 test(`${profile}: Fleet restore does not encode its privately parsed clock aggregate again`,()=>{
  const raw=new V2FleetSession(new V2EconomySession(profile),0).serialize();
  const observed=observeEncoding(v=>v&&typeof v==='object'&&!Array.isArray(v)&&'quotaMs' in v&&'heroEventCursor' in v&&'batches' in v,()=>V2FleetSession.restore(raw));
  assert.equal(observed.calls,0,'parsed fleet aggregate must not be serialized again just to detach it');
  assert.equal(observed.result.serialize(),raw);
 });
 test(`${profile}: Dispatch restore does not encode its privately parsed order history again`,()=>{
  const source=new V2DispatchSession(port,0,profile);accepted(source,'owned-history');source.completeDelivery('owned-history','arrival');
  const raw=source.serialize();
  const observed=observeEncoding(v=>Array.isArray(v)&&v.length>0&&v.every(o=>o&&typeof o==='object'&&'status' in o&&'quote' in o),()=>V2DispatchSession.restore(raw,port,{preserveClock:true}));
  assert.equal(observed.calls,0,'parsed dispatch history must not be serialized again just to copy it');
  assert.equal(observed.result.serialize(),raw);
 });
 test(`${profile}: independent restores and detached projections cannot share mutable authority`,()=>{
  const source=new V2DispatchSession(port,0,profile);accepted(source,'owned-pending');
  const bytes=source.serialize(),first=V2DispatchSession.restore(bytes,port,{preserveClock:true}),second=V2DispatchSession.restore(bytes,port,{preserveClock:true});
  const exposed=first.snapshot();exposed.orders[0].quote.incomeCents=1;exposed.batchIds.length=0;exposed.frame.sequence=999;
  exposed.economy.state.cashCents=0;exposed.fleet.economy.state.cashCents=0;exposed.fleet.fleet.lastAdvancedAt=999;
  assert.equal(first.serialize(),bytes);assert.equal(second.serialize(),bytes);
  first.completeDelivery('owned-pending','arrival');
  assert.equal(first.snapshot().economy.state.heroCompletedOrders,1);assert.equal(second.serialize(),bytes);assert.equal(source.serialize(),bytes);
  const wallet=V2EconomySession.restore(JSON.stringify(source.snapshot().economy)),walletBytes=wallet.serialize(),view=wallet.state;
  view.riders[0].vehicleId=null;view.ledger.opening.balanceCents=0;view.activeQuotes.length=0;assert.equal(wallet.serialize(),walletBytes);
 });
 test(`${profile}: full restore still rejects mismatched wallets and forged completed income`,()=>{
  const d=new V2DispatchSession(port,0,profile);accepted(d,'owned-receipt');d.completeDelivery('owned-receipt','arrival');
  const bytes=d.serialize(),walletMismatch=JSON.parse(bytes);walletMismatch.fleet.economy.state.cashCents++;
  assert.throws(()=>V2DispatchSession.restore(JSON.stringify(walletMismatch),port));
  const forged=JSON.parse(bytes);forged.orders[0].receipt.incomeCents++;
  assert.throws(()=>V2DispatchSession.restore(JSON.stringify(forged),port));assert.equal(d.serialize(),bytes);
 });
}

test('replaceFrom adopts separate parsed authority and rejects a forged wallet atomically',()=>{
 const source=new V2EconomySession('slots-v1'),target=new V2EconomySession('kg-v1');
 target.replaceFrom(source.serialize());const before=target.serialize();
 source.upgradeVehicle('starter-1');assert.equal(target.serialize(),before);
 const forged=JSON.parse(before);forged.state.cashCents++;
 assert.throws(()=>target.replaceFrom(JSON.stringify(forged)));assert.equal(target.serialize(),before);
});
