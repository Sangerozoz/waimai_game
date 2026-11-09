'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {domain}=require('./helpers.cjs');
const {V2DispatchSession}=domain('V2DispatchSession');
const {V2EconomySession}=domain('V2EconomySession');
const deferred={deferAuto:true,deferFleet:true};
const make=profile=>new V2DispatchSession({verifyArrival:()=>true},0,profile);
function encodedCalls(d,action){
 const original=d.serialize;let count=0,result;
 d.serialize=function(){count++;return original.call(this);};
 try{result=action();}finally{d.serialize=original;}
 return {count,result};
}
function accept(d,id){if(d.usesSlots)d.acceptSlotBatch([{id,kind:'ordinary',load:domain('V2LoadRules').slotLoadForOrderId(id)}],{[id]:{deliveryMetres:100}});else d.acceptBatch([{id,kind:'ordinary',weightKg:1}]);}

for(const profile of ['kg-v1','slots-v1']){
 test(`${profile}: eligible deferred manual clock does not encode a whole Dispatch draft`,()=>{
  const d=make(profile),before=d.snapshot();
  const observed=encodedCalls(d,()=>d.tick(1,1,true,false,deferred));
  assert.equal(observed.count,0,'manual event-free clock must not serialize and restore the complete dispatch history');
  assert.deepEqual(observed.result,{autoRunSeconds:0,control:'manual'});
  const after=d.snapshot();assert.deepEqual(after.economy,before.economy);assert.deepEqual(after.fleet,before.fleet);assert.deepEqual(after.rewards,before.rewards);
  assert.deepEqual(after.frame,{sequence:1,nowSeconds:1,foreground:true,paused:false,fingerprint:'[1,true,false]'});
  observed.result.control='auto';const context=d.tickContext;context.sequence=999;assert.equal(d.tickContext.sequence,1);assert.equal(d.controlMode,'manual');
 });
 test(`${profile}: pause, foreground, rollback, duplicate and real restore keep the original clock contract`,()=>{
  let d=make(profile);
  const cases=[[1,10,false,false,10],[2,20,true,true,20],[3,20,true,false,20],[4,5,true,false,20],[5,21,true,false,21]];
  for(const [sequence,now,foreground,paused,high] of cases){
   assert.deepEqual(d.tick(sequence,now,foreground,paused,deferred),{autoRunSeconds:0,control:'manual'});
   assert.deepEqual(d.snapshot().frame,{sequence,nowSeconds:high,foreground,paused,fingerprint:JSON.stringify([now,foreground,paused])});
  }
  const before=d.serialize();assert.deepEqual(d.tick(5,21,true,false,deferred),{autoRunSeconds:0,control:'manual'});assert.equal(d.serialize(),before);
  assert.throws(()=>d.tick(5,22,true,false,deferred));assert.equal(d.serialize(),before);
  d=V2DispatchSession.restore(before,{verifyArrival:()=>true});assert.equal(d.tickContext.clockNeedsRebase,true);
  d.tick(5,21,true,false,deferred);assert.equal(d.tickContext.clockNeedsRebase,true);
  d.tick(6,100,true,false,deferred);assert.equal(d.tickContext.clockNeedsRebase,false);assert.equal(d.tickContext.nowSeconds,100);
 });
 test(`${profile}: malformed clock inputs reject without changing any stored field`,()=>{
  const d=make(profile);d.tick(1,1,true,false,deferred);const before=d.serialize();
  for(const args of [[0,2,true,false],[-1,2,true,false],[NaN,2,true,false],[1.5,2,true,false],[2,-1,true,false],[2,Infinity,true,false],[2,NaN,true,false],[2,1e20,true,false],[2,2,1,false],[2,2,true,null]]){
   assert.throws(()=>d.tick(...args,deferred));assert.equal(d.serialize(),before);
  }
 });
 test(`${profile}: missing defer flags, auto control and pending ad use the original transaction`,()=>{
  for(const options of [{},{deferFleet:true},{deferAuto:true}]){
   const d=make(profile),observed=encodedCalls(d,()=>d.tick(1,1,true,false,options));assert.ok(observed.count>0);
  }
  const d=make(profile),ticket=d.requestAd('auto',null,0,30);d.resolveAd(ticket,'completed',1);
  const observed=encodedCalls(d,()=>d.tick(1,2,true,false,deferred));assert.ok(observed.count>0);assert.deepEqual(observed.result,{autoRunSeconds:1,control:'auto'});assert.equal(d.snapshot().rewards.autoRemainingSeconds,600);
  const pending=make(profile);pending.requestAd('auto',null,0,1);
  const expired=encodedCalls(pending,()=>pending.tick(1,2,true,false,deferred));assert.ok(expired.count>0);assert.equal(pending.snapshot().rewards.tickets[0].status,'expired');assert.equal(pending.tickContext.pendingAd,false);
 });
 test(`${profile}: stopped automatic entitlement remains available during an eligible manual tick`,()=>{
  const d=make(profile),ticket=d.requestAd('auto',null,0,30);d.resolveAd(ticket,'completed',1);d.stopAutomation();
  const rights=d.snapshot().rewards;const observed=encodedCalls(d,()=>d.tick(1,2,true,false,deferred));
  assert.equal(observed.count,0);assert.deepEqual(d.snapshot().rewards,rights);d.resumeAutomation();assert.equal(d.controlMode,'auto');
 });
 test(`${profile}: a changed arrival port still rejects a deferred clock atomically`,()=>{
  const port={verifyArrival:()=>true},d=new V2DispatchSession(port,0,profile),before=d.serialize();port.verifyArrival=null;
  assert.throws(()=>d.tick(1,1,true,false,deferred));assert.equal(d.serialize(),before);
 });
 test(`${profile}: cross-wallet mismatch and forged historical income remain rejected`,()=>{
  const d=make(profile);accept(d,'clock-history');d.completeDelivery('clock-history','arrival');
  d.orders[0].receipt.incomeCents++;const before=d.serialize();assert.throws(()=>d.tick(1,1,true,false,deferred));assert.equal(d.serialize(),before);
  const mixed=make(profile),other=V2EconomySession.restore(mixed.economy.serialize());other.upgradeVehicle('starter-1');
  // Explicit internal corruption fixture, not a naturally reachable player state.
  Object.defineProperty(mixed.fleet,'economy',{value:other});const bytes=mixed.serialize();assert.throws(()=>mixed.tick(1,1,true,false,deferred));assert.equal(mixed.serialize(),bytes);
 });
 test(`${profile}: complete wallet, reward, schema and rebase guards remain active`,()=>{
  const corruptions=[d=>{d.economy.snapshot.state.cashCents++;},d=>{d.rewards.state.autoRemainingSeconds=600;},d=>{d.version=99;},d=>{d.firstTickAfterRestore='invalid';},d=>{d.economy.replaceFrom(new V2EconomySession(profile==='kg-v1'?'slots-v1':'kg-v1').serialize());}];
  for(const corrupt of corruptions){const d=make(profile);corrupt(d);const bytes=d.serialize();assert.throws(()=>d.tick(1,1,true,false,deferred));assert.equal(d.serialize(),bytes);}
 });
 test(`${profile}: an exception from final validation cannot publish a half-updated clock`,()=>{
  const d=make(profile),before=d.serialize(),original=V2DispatchSession.prototype.validate;let calls=0;
  V2DispatchSession.prototype.validate=function(){original.call(this);if(++calls===2)throw Error('isolated final-validation failure');};
  try{assert.throws(()=>d.tick(1,1,true,false,deferred),/isolated final-validation failure/);}finally{V2DispatchSession.prototype.validate=original;}
  assert.equal(d.serialize(),before);
 });
}

test('a restored unseen hero event stays on the original transaction and refills exactly once',()=>{
 const initial=make('kg-v1').snapshot(),economy=V2EconomySession.restore(JSON.stringify(initial.economy));economy.acceptOrdinary('clock-unseen');economy.completeDelivery('clock-unseen');
 // Compatible isolated boundary: wallet receipt exists, original fleet cursor lags.
 initial.economy=JSON.parse(economy.serialize());initial.fleet.economy=JSON.parse(economy.serialize());
 const d=V2DispatchSession.restore(JSON.stringify(initial),{verifyArrival:()=>true},{preserveClock:true});
 const first=encodedCalls(d,()=>d.tick(1,1,true,false,deferred));assert.ok(first.count>0);assert.equal(d.snapshot().fleet.fleet.quotaMs,60000);assert.equal(d.snapshot().fleet.fleet.heroEventCursor,1);
 const second=encodedCalls(d,()=>d.tick(2,2,true,false,deferred));assert.equal(second.count,0);assert.equal(d.snapshot().fleet.fleet.quotaMs,60000);
});

test('an accessor-based arrival port retains the original transactional path',()=>{
 const port={get verifyArrival(){return ()=>true;}},d=new V2DispatchSession(port,0,'slots-v1');
 const observed=encodedCalls(d,()=>d.tick(1,1,true,false,deferred));
 assert.ok(observed.count>0,'an external accessor must not be invoked inside an in-place clock update');
 assert.deepEqual(observed.result,{autoRunSeconds:0,control:'manual'});
});

test('manual options do not introduce a deferAuto getter read',()=>{
 const d=make('slots-v1');let autoReads=0,fleetReads=0;
 const options={get deferAuto(){autoReads++;return true;},get deferFleet(){fleetReads++;return true;}};
 const observed=encodedCalls(d,()=>d.tick(1,1,true,false,options));
 assert.deepEqual([autoReads,fleetReads],[0,1]);assert.ok(observed.count>0);
});

test('a throwing deferAuto getter remains uncalled by the original manual semantics',()=>{
 const d=make('slots-v1'),options={get deferAuto(){throw Error('deferAuto must not run in manual');},deferFleet:true};
 assert.doesNotThrow(()=>d.tick(1,1,true,false,options));assert.equal(d.tickContext.sequence,1);
});

test('a reentrant deferAuto getter cannot introduce an economic command into a manual clock',()=>{
 const d=make('slots-v1'),before=d.snapshot().economy;
 const options={get deferAuto(){d.command({type:'upgradeVehicle',vehicleId:'starter-1'});return true;},deferFleet:true};
 d.tick(1,1,true,false,options);assert.deepEqual(d.snapshot().economy,before);
});

test('a throwing deferFleet getter retains original transaction entry and atomic rejection',()=>{
 const d=make('slots-v1'),before=d.serialize(),options={deferAuto:true,get deferFleet(){throw Error('isolated option getter failure');}};let thrown;
 const observed=encodedCalls(d,()=>{try{d.tick(1,1,true,false,options);}catch(error){thrown=error;}});
 assert.match(thrown?.message||'',/isolated option getter failure/);assert.ok(observed.count>0);assert.equal(d.serialize(),before);
});

test('inherited defer flags retain the original generic path',()=>{
 const d=make('slots-v1'),options=Object.create({deferAuto:true,deferFleet:true});
 const observed=encodedCalls(d,()=>d.tick(1,1,true,false,options));assert.ok(observed.count>0);assert.equal(d.tickContext.sequence,1);
});
