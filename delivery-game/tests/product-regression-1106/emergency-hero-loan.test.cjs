'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const base=path.dirname(process.env.MAP_ROUTER_MODULE);
const {V2GameSession}=require(path.join(base,'V2GameSession.js'));
const {prepareCity}=require(path.join(base,'PlaceCatalog.js'));
const {V2EconomySession}=require(path.join(base,'../domain/V2EconomySession.js'));
const {V2FleetSession}=require(path.join(base,'../domain/V2FleetSession.js'));
const {V2DispatchSession}=require(path.join(base,'../domain/V2DispatchSession.js'));
const {queryProgressTargets}=require(path.join(base,'../domain/V2ProgressTargets.js'));
const {V2_CONFIG_ID}=require(path.join(base,'../domain/V2EconomyConfig.js'));
const {slotVehicleEffects,slotRiderEffects,slotMapBaseIncomeCents}=require(path.join(base,'../domain/V2EconomyProfiles.js'));
const {slotFleetOrderIds,slotLoadForOrderId}=require(path.join(base,'../domain/V2LoadRules.js'));
const ROOT=path.resolve(__dirname,'../../..');
const pm=JSON.parse(fs.readFileSync(path.join(ROOT,'docs/balance/2026-11-06-balance-round-01/pm/only-car-reproduction-1107.json'),'utf8'));
const city=prepareCity(JSON.parse(fs.readFileSync(path.join(ROOT,'delivery-game/assets/resources/map-sample/city.json'),'utf8')));
const restore=raw=>V2GameSession.restore(city,typeof raw==='string'?raw:JSON.stringify(raw),{preserveClock:true});
const legacy=()=>restore(pm.fixtures.signedZeroQuota);
const clone=value=>JSON.parse(JSON.stringify(value));
function advance(g,seconds,foreground=true,paused=false){const frame=g.snapshot().frame;return g.tick(frame.sequence+1,frame.nowSeconds+seconds,foreground,paused);}
function roundTrip(g){const raw=g.serialize(),again=restore(raw);assert.equal(again.serialize(),raw);return again;}
function atomicReject(g,action,pattern){const before=g.serialize();assert.throws(action,pattern);assert.equal(g.serialize(),before);}
function offers(g,count=1){const candidates=g.normalCandidates();if(count===1){assert.ok(candidates.length);return [candidates[0]];}const small=candidates.filter(o=>o.load.occupiedSlots===1);assert.ok(small.length>=count,'actual city must supply enough one-slot orders');return small.slice(0,count);}
function start(g,count=1){const selected=offers(g,count),quotes=g.acceptBatch(selected);g.beginTrip(g.routeChoices()[0].preference);return {selected,quotes};}
function driveUntil(g,predicate,{reload=false,rest=true,onPhase}={}){
 const phases=new Set();
 for(let step=0;step<1500&&!predicate(g);step++){
  const phase=g.route.progress.phase;
  if(!phases.has(phase)){if(reload)g=roundTrip(g);phases.add(phase);if(onPhase)onPhase(g,phase);}
  if(g.tripState.action)advance(g,1);
  else if(g.tripState.blocked&&rest&&!(phase==='service'&&g.route.progress.serviceCharged))g.supply('rest');
  else if(phase==='planned')g.beginTrip(g.routeChoices()[0].preference);
  else if(phase==='pickup')g.pickup();
  else if(phase==='ready')g.continueTrip();
  else advance(g,.5);
 }
 assert.ok(predicate(g),'bounded real Game/Route driver reached its stop');return {g,phases};
}
function finish(g,options){return driveUntil(g,x=>x.snapshot().batchIds.length===0,options).g;}
function finishOne(g){const count=g.dispatch.economyState.heroCompletedOrders;start(g);g=finish(g);assert.equal(g.dispatch.economyState.heroCompletedOrders,count+1);return g;}
function borrowed(){const g=legacy();g.command({type:'borrowEmergencyVehicle',expectedSequence:0});return g;}
// These are explicitly isolated compatibility inputs, not additional naturally reached terminals.
// The original files are read-only. The kg adaptation changes NPC load representation/IDs only;
// it preserves all cash, quota, timing, completed hero history and payable amounts.
function kgCompatibilityTerminal(){
 const raw=clone(pm.fixtures.signedZeroQuota),d=raw.dispatch,b=d.fleet.fleet.batches[0];
 b.orders=b.orders.map((order,i)=>{const {terms,...q}=order;return {...q,id:`fleet-1-${i}`,weightKg:1,capacityKg:2,terms:{version:'kg-v1',profileId:V2_CONFIG_ID}};});
 d.economy.state.fleetQuotes=b.orders.map(({dueMs,...q})=>q);d.fleet.economy=clone(d.economy);
 return raw;
}
function oldReader(name,cache=new Map()){
 if(cache.has(name))return cache.get(name).exports;
 const sourceRoot=path.join(ROOT,'docs/balance/2026-11-06-balance-round-01/pm/emergency-hero-loan-1107/source-before');
 const file=path.join(sourceRoot,name+'.ts');
 if(!fs.existsSync(file))return require(path.join(base,'..',name+'.js'));
 const editor=process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
 const ts=require(path.join(editor,'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
 const js=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText;
 const module={exports:{}};cache.set(name,module);
 const localRequire=id=>id.startsWith('.')?oldReader(path.posix.normalize(path.posix.join(path.posix.dirname(name),id)),cache):require(id);
 new Function('require','module','exports',js)(localRequire,module,module.exports);return module.exports;
}

// Two paid-for vehicles and NPCs come from the preserved historical earned-funds fixture.
// This boundary input freezes quota at zero and adds a hypothetical old second signed batch;
// no owned assets, cash, ledger income or hero completion events are added by the input builder.
function multiNPCCompatibilityTerminal(){
 const history=JSON.parse(fs.readFileSync(path.join(ROOT,'docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/historical-fixtures.json'),'utf8'));
 const f=clone(history.fixtures['slots-v1'].reservedOldCarAndConfiguredNewCar),e=f.economy.state,r=e.riders.find(r=>r.id==='npc-2'),v=e.vehicles.find(v=>v.id===r.vehicleId);
 const effects=slotVehicleEffects(v),training=slotRiderEffects(r.id,r.level),ids=slotFleetOrderIds(2,effects.capacitySlots);
 const road=Math.ceil(60000/effects.speedRelativeToStarter*(1+.25*(ids.length-1))),service=Math.ceil(30000*(1-training.fixedServiceReduction));
 const orders=ids.map((id,i)=>({id,riderId:r.id,vehicleId:v.id,vehicleLevel:v.level,riderLevel:r.level,mapId:1,incomeCents:Math.round(slotMapBaseIncomeCents(1)*effects.incomeFactor*training.incomeFactor),speedRelativeToStarter:effects.speedRelativeToStarter,baseIncomeFactor:training.baseIncomeFactor,fixedServiceReduction:training.fixedServiceReduction,
  terms:{version:'slots-v1',profileId:effects.profileId,pricePolicyId:'slots-fleet-v1',effectPolicyId:'capacity-slots-effects-v1',load:slotLoadForOrderId(id),capacity:effects.capacity,vehicleLevel:v.level,riderLevel:r.level,speedRelativeToStarter:effects.speedRelativeToStarter,incomeFactor:effects.incomeFactor,riderIncomeFactor:training.incomeFactor,fixedServiceReduction:training.fixedServiceReduction},dueMs:road+service*(i+1)}));
 f.fleet.batches.push({id:2,riderId:r.id,vehicleId:v.id,mapId:1,elapsedMs:0,paidCount:0,orders});f.fleet.nextBatchId=3;f.fleet.quotaMs=0;e.fleetQuotes.push(...orders.map(({dueMs,...q})=>q));
 const raw=JSON.parse(new V2GameSession(city,0).serialize());raw.dispatch.economy=clone(f.economy);raw.dispatch.fleet=f;raw.dispatch.frame.nowSeconds=f.fleet.lastAdvancedAt/1000;return raw;
}

test('the preserved zero-quota terminal can explicitly borrow without gifts or permanent assets',()=>{
 const g=legacy(),before=g.snapshot(),trip=g.tripState;
 assert.equal(g.dispatch.emergencyLoanStatus?.phase,'available');
 assert.equal(g.serialize(),JSON.stringify(pm.fixtures.signedZeroQuota));
 g.command({type:'borrowEmergencyVehicle',expectedSequence:0});
 const after=g.snapshot();
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'borrowed');
 assert.deepEqual(after.economy.state.vehicles,before.economy.state.vehicles);
 assert.deepEqual(after.economy.state.riders,before.economy.state.riders);
 for(const key of ['cashCents','heroExperience','heroCompletedOrders','ledger','fleetQuotes'])assert.deepEqual(after.economy.state[key],before.economy.state[key]);
 assert.deepEqual(after.fleet.fleet,before.fleet.fleet);
 assert.deepEqual(after.rewards,before.rewards);assert.deepEqual(g.tripState,trip);
 assert.deepEqual(g.dispatch.nextBatchEffects.capacity,{version:'slots-v1',capacitySlots:2});
 assert.equal(g.dispatch.nextBatchEffects.speedRelativeToStarter,1);
 assert.equal(g.dispatch.nextBatchEffects.incomeFactor,1);
 assert.ok(g.normalCandidates().length>0);
 assert.equal(JSON.parse(g.serialize()).version,7);
 assert.equal(after.version,3);assert.equal(after.economy.version,3);assert.equal(after.fleet.version,3);
 assert.equal(restore(g.serialize()).serialize(),g.serialize());
});

test('loan status is detached and read-only; duplicate and stale commands cannot change the loan',()=>{
 const g=legacy(),raw=g.serialize(),view=g.dispatch.emergencyLoanStatus;
 view.returnVehicleIds.push('fabricated');view.phase='returned';
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'available');assert.equal(g.serialize(),raw);
 for(const expectedSequence of [-1,1,.5,NaN])atomicReject(g,()=>g.command({type:'borrowEmergencyVehicle',expectedSequence}));
 g.command({type:'borrowEmergencyVehicle',expectedSequence:0});
 atomicReject(g,()=>g.command({type:'borrowEmergencyVehicle',expectedSequence:0}));
 atomicReject(g,()=>g.command({type:'returnEmergencyVehicle',loanSequence:2,vehicleId:'starter-1'}));
 atomicReject(g,()=>g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'}),/未付/);
 for(const vehicleId of [null,'starter-1'])atomicReject(g,()=>g.command({type:'assignVehicle',riderId:'hero',vehicleId}),/归还/);
});

test('normal, detachable and genuinely earned affordable-car states cannot borrow',()=>{
 const normal=new V2GameSession(city,0);atomicReject(normal,()=>normal.command({type:'borrowEmergencyVehicle',expectedSequence:0}));
 const detachable=restore(pm.fixtures.beforeNPCSigning);assert.equal(detachable.dispatch.emergencyLoanStatus.phase,'unavailable');
 atomicReject(detachable,()=>detachable.command({type:'borrowEmergencyVehicle',expectedSequence:0}));
 let earned=new V2GameSession(city,0);for(let i=0;i<10;i++)earned=finishOne(earned);
 assert.equal(earned.dispatch.economyState.cashCents,30000);
 earned.command({type:'assignVehicle',riderId:'hero',vehicleId:null});
 atomicReject(earned,()=>earned.command({type:'borrowEmergencyVehicle',expectedSequence:0}));
});

// Synthetic compatibility inputs isolate ONLY the cash predicate. The ledger opening
// offset reconciles the changed test input; it is not earned income, a gameplay grant,
// or another naturally reached terminal. Original fixture files remain untouched.
function cashBoundaryCompatibilityInput(cashCents){
 const raw=clone(pm.fixtures.signedZeroQuota),e=raw.dispatch.economy.state;
 e.ledger.opening.balanceCents+=cashCents-e.cashCents;e.cashCents=cashCents;
 raw.dispatch.fleet.economy=clone(raw.dispatch.economy);return raw;
}
for(const [cashCents,phase] of [[29999,'available'],[30000,'unavailable'],[30001,'unavailable']])test(`isolated cash-only compatibility input: ${cashCents} cents at the 30000-cent car boundary`,()=>{
 const input=cashBoundaryCompatibilityInput(cashCents),normalised=clone(input),original=clone(pm.fixtures.signedZeroQuota);
 for(const economy of [normalised.dispatch.economy,normalised.dispatch.fleet.economy]){
  economy.state.cashCents=original.dispatch.economy.state.cashCents;
  economy.state.ledger.opening.balanceCents=original.dispatch.economy.state.ledger.opening.balanceCents;
 }
 assert.deepEqual(normalised,original,'all non-cash eligibility, contracts, assets, quota and history are identical');
 const g=restore(input),e=V2EconomySession.restore(JSON.stringify(g.snapshot().economy));
 assert.equal(e.minimumVehiclePurchaseCents,30000);assert.deepEqual(e.reclaimableHeroVehicleIds,[]);
 assert.equal(g.snapshot().batchIds.length,0);assert.equal(g.route.progress.phase,'finished');assert.equal(g.tripState.action,null);
 assert.equal(g.dispatch.fleetState.quotaMs,0);assert.equal(g.dispatch.economyState.riders[0].vehicleId,null);
 assert.equal(g.dispatch.emergencyLoanStatus.phase,phase);
 if(cashCents<30000){
  const before=g.dispatch.economyState;g.command({type:'borrowEmergencyVehicle',expectedSequence:0});
  assert.equal(g.dispatch.emergencyLoanStatus.phase,'borrowed');assert.equal(g.dispatch.economyState.cashCents,cashCents);
  assert.deepEqual(g.dispatch.economyState.ledger,before.ledger);assert.deepEqual(g.dispatch.economyState.vehicles,before.vehicles);roundTrip(g);
 }else{
  assert.match(g.dispatch.emergencyLoanStatus.reason,/余额足够购车/);
  atomicReject(g,()=>g.command({type:'borrowEmergencyVehicle',expectedSequence:0}),/余额足够购车/);
  const bought=g.command({type:'buyVehicle',modelId:1});assert.ok(bought);assert.equal(g.dispatch.economyState.cashCents,cashCents-30000);
 }
});

test('real Game deliveries preserve the same-path ten-order car and fifteen-order NPC budgets',()=>{
 let g=new V2GameSession(city,0);for(let i=0;i<10;i++)g=finishOne(g);
 assert.equal(g.dispatch.economyState.cashCents,30000);
 g=roundTrip(g);const vehicleId=g.command({type:'buyVehicle',modelId:1});
 assert.equal(g.dispatch.economyState.cashCents,0);assert.equal(g.dispatch.economyState.vehicles.length,2);
 assert.equal(g.dispatch.economyState.ledger.entries.filter(e=>e.category==='vehicle_purchase'&&e.detail.vehicleId===vehicleId).length,1);
 g.command({type:'assignVehicle',riderId:'hero',vehicleId});
 for(let i=10;i<15;i++)g=finishOne(g);
 assert.equal(g.dispatch.economyState.cashCents,12000);g.command({type:'hireRider',riderId:'npc-1'});
 assert.equal(g.dispatch.economyState.cashCents,0);assert.equal(g.dispatch.economyState.hireCount,1);
 g.command({type:'assignVehicle',riderId:'npc-1',vehicleId:'starter-1'});
 assert.equal('heroEmergencyLoan' in g.dispatch.economyState,false);assert.equal(JSON.parse(g.serialize()).version,6);roundTrip(g);
});

test('an isolated original signed-batch compatibility input with remaining quota cannot borrow',()=>{
 const history=JSON.parse(fs.readFileSync(path.join(ROOT,'docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/historical-fixtures.json'),'utf8'));
 const f=clone(history.fixtures['slots-v1'].signedRemaining),raw=JSON.parse(new V2GameSession(city,0).serialize());
 // Only the empty Game wrapper is new; original signed Fleet/Economy and quota stay unchanged.
 raw.dispatch.economy=clone(f.economy);raw.dispatch.fleet=f;raw.dispatch.frame.nowSeconds=f.fleet.lastAdvancedAt/1000;
 const g=restore(raw);assert.ok(g.dispatch.fleetState.quotaMs>0);assert.equal(g.dispatch.economyState.riders[0].vehicleId,null);
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'unavailable');atomicReject(g,()=>g.command({type:'borrowEmergencyVehicle',expectedSequence:0}),/额度/);
});

test('Game refuses loan commands during real rest actions and all active route phases',()=>{
 let g=legacy();g.supply('rest');atomicReject(g,()=>g.command({type:'borrowEmergencyVehicle',expectedSequence:0}),/补给/);
 advance(g,0);advance(g,20);g.command({type:'borrowEmergencyVehicle',expectedSequence:0});
 const selected=offers(g);g.acceptBatch(selected);
 const driven=driveUntil(g,x=>x.snapshot().batchIds.length===0,{reload:true,onPhase:current=>{
  for(const action of [()=>current.command({type:'borrowEmergencyVehicle',expectedSequence:1}),()=>current.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'})])atomicReject(current,action,/配送/);
 }});g=driven.g;
 assert.ok(driven.phases.has('planned'));assert.ok(driven.phases.has('pickup'));assert.ok(driven.phases.has('ready'));assert.ok(driven.phases.has('travelling'));assert.ok(driven.phases.has('service'));
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'borrowed');
});

test('first real delivery is insufficient; release waits for quota and never confiscates the current batch',()=>{
 let g=borrowed();const oldOrders=clone(g.dispatch.fleetState.batches[0].orders),targets=queryProgressTargets(g.dispatch.economyState);
 const {quotes}=start(g);assert.ok(quotes[0].vehicleRef);assert.equal('vehicleId' in quotes[0],false);
 g=finish(g,{reload:true});assert.equal(g.dispatch.economyState.heroCompletedOrders,2);
 assert.equal(g.dispatch.fleetState.quotaMs+g.dispatch.fleetState.batches[0].elapsedMs-60000,60000,'one delivery refills exactly 60 seconds, including its already consumed frame tail');
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'borrowed');assert.equal(g.dispatch.economyState.fleetQuotes.length,2);
 advance(g,60,false,true);g=roundTrip(g);
 assert.equal(g.dispatch.fleetState.quotaMs,0);assert.equal(g.dispatch.fleetState.batches[0].elapsedMs,120000);assert.equal(g.dispatch.fleetState.batches[0].paidCount,1);
 assert.deepEqual(g.dispatch.fleetState.batches[0].orders,oldOrders);assert.equal(g.dispatch.economyState.fleetQuotes.length,1);
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'borrowed');
 const batch=start(g,2),beforeCount=g.dispatch.economyState.heroCompletedOrders;
 g=driveUntil(g,x=>x.dispatch.economyState.heroCompletedOrders===beforeCount+1).g;
 assert.equal(g.snapshot().batchIds.length,2);assert.equal(g.dispatch.economyState.activeQuotes.length,1);
 const signed=clone(g.snapshot().orders.filter(o=>g.snapshot().batchIds.includes(o.id)).map(o=>o.quote));
 const unsigned=offers(g);assert.ok(unsigned.every(o=>!g.snapshot().orders.some(signed=>signed.id===o.id)));
 advance(g,20,false,true);assert.equal(g.dispatch.emergencyLoanStatus.phase,'returnable');
 assert.deepEqual(g.dispatch.emergencyLoanStatus.returnVehicleIds,['starter-1']);assert.equal(g.dispatch.emergencyLoanStatus.canStartBatch,false);
 assert.equal(g.normalCandidates().length,0);assert.equal(g.specialCandidate('not-an-ad-grant'),null);
 atomicReject(g,()=>g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'}),/配送/);
 assert.deepEqual(g.snapshot().orders.filter(o=>g.snapshot().batchIds.includes(o.id)).map(o=>o.quote),signed);
 g=finish(roundTrip(g));assert.equal(g.dispatch.economyState.heroCompletedOrders,beforeCount+2);
 assert.deepEqual(g.snapshot().orders.filter(o=>batch.quotes.some(q=>q.id===o.id)).map(o=>o.quote),batch.quotes);
 atomicReject(g,()=>g.acceptBatch(unsigned),/归还/);
 const e=V2EconomySession.restore(JSON.stringify(g.snapshot().economy));
 assert.throws(()=>e.acceptSlotBatch(unsigned.map(o=>({id:o.id,kind:o.kind})),Object.fromEntries(unsigned.map(o=>[o.id,{deliveryMetres:100}]))),/归还/);
 const beforeReturn=g.dispatch.economyState;
 g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'});
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'returned');assert.equal(g.dispatch.economyState.riders[0].vehicleId,'starter-1');assert.equal(g.dispatch.economyState.riders.find(r=>r.id==='npc-1').vehicleId,null);
 assert.deepEqual(g.dispatch.economyState.ledger,beforeReturn.ledger);assert.equal(g.dispatch.economyState.cashCents,beforeReturn.cashCents);
 g=roundTrip(g);atomicReject(g,()=>g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'}));
 assert.equal(queryProgressTargets(g.dispatch.economyState).find(t=>t.id==='first-car').progress,targets.find(t=>t.id==='first-car').progress);
 g=finishOne(g);assert.equal(g.snapshot().orders.at(-1).quote.vehicleId,'starter-1');assert.equal('vehicleRef' in g.snapshot().orders.at(-1).quote,false);roundTrip(g);
});

test('cancelled emergency quotes remain valid after return alongside completed histories',()=>{
 let g=borrowed();const {quotes}=start(g),before=g.dispatch.economyState;
 g.cancelDelivery(quotes[0].id);assert.equal(g.dispatch.economyState.cashCents,before.cashCents);assert.equal(g.dispatch.fleetState.quotaMs,0);g=roundTrip(g);
 for(let i=0;i<4&&g.dispatch.emergencyLoanStatus.phase!=='returnable';i++){g=finishOne(g);advance(g,60,false,true);}
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'returnable');
 g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'});g=roundTrip(g);
 assert.equal(g.snapshot().orders.find(o=>o.id===quotes[0].id).status,'cancelled');assert.ok(g.snapshot().orders.some(o=>o.status==='completed'&&o.quote.vehicleRef));
});

test('borrowing cannot satisfy permanent asset, NPC reserve or upgrade requirements',()=>{
 const g=borrowed(),s=g.dispatch.economyState,targets=queryProgressTargets(s);
 assert.equal(s.vehicles.length,1);assert.equal(targets.find(t=>t.id==='first-car').completed,false);
 const e=V2EconomySession.restore(JSON.stringify(g.snapshot().economy));
 assert.equal(e.hasRecoverableHeroVehicle,false);assert.equal(e.vehicleEffectProjection('emergency-1'),null);
 assert.throws(()=>e.upgradeVehicle('emergency-1'));assert.throws(()=>e.assignVehicle('npc-1','emergency-1'));
 assert.throws(()=>e.registerSlotFleetOrders('npc-1',['fake-new-batch']));
 advance(g,3600);assert.equal(g.dispatch.fleetState.nextBatchId,2);assert.equal(g.dispatch.fleetState.quotaMs,0);assert.deepEqual(g.dispatch.economyState,s);
});

test('forged identities, effects, downgrade and mixed versions are rejected after a genuine borrow',()=>{
 const g=borrowed();g.acceptBatch(offers(g));const raw=JSON.parse(g.serialize());
 const mutations=[
  s=>s.version=6,
  s=>s.dispatch.version=2,
  s=>s.dispatch.fleet.version=2,
  s=>s.dispatch.economy.version=2,
  s=>s.dispatch.economy.state.heroEmergencyLoan.policyId='unknown',
  s=>s.dispatch.economy.state.heroEmergencyLoan.active=false,
  s=>s.dispatch.economy.state.heroEmergencyLoan.sequence=0,
  s=>s.dispatch.economy.state.riders[0].vehicleId='starter-1',
  s=>{s.dispatch.economy.state.activeQuotes[0].vehicleId='starter-1';s.dispatch.orders.at(-1).quote.vehicleId='starter-1';},
  s=>{s.dispatch.economy.state.activeQuotes[0].vehicleRef.loanSequence=2;s.dispatch.orders.at(-1).quote.vehicleRef.loanSequence=2;},
  s=>{s.dispatch.economy.state.activeQuotes[0].terms.capacity.capacitySlots=3;s.dispatch.orders.at(-1).quote.terms.capacity.capacitySlots=3;},
  s=>s.dispatch.economy.state.vehicles.push({id:'emergency-1',modelId:'emergency',level:1}),
  s=>s.dispatch.fleet.fleet.batches[0].orders[0].vehicleRef={kind:'emergency',loanSequence:1,policyId:'hero-emergency-base-v1'},
  s=>s.dispatch.economy.state.heroEmergencyLoan.unrecognized=true,
  s=>s.version=8,
 ];
 for(const mutate of mutations){const changed=clone(raw);mutate(changed);changed.dispatch.economy.state.activeQuote=clone(changed.dispatch.economy.state.activeQuotes[0]);changed.dispatch.fleet.economy=clone(changed.dispatch.economy);assert.throws(()=>restore(changed));}
 assert.equal(g.serialize(),JSON.stringify(raw));
});

test('an emergency source marker cannot be smuggled into permanent vehicle inventory',()=>{
 const g=borrowed(),raw=JSON.parse(g.serialize());
 raw.dispatch.economy.state.vehicles[0].vehicleRef={kind:'emergency',loanSequence:1,policyId:'hero-emergency-base-v1'};
 raw.dispatch.fleet.economy=clone(raw.dispatch.economy);
 assert.throws(()=>restore(raw));
});

for(const profile of ['kg-v1','slots-v1'])test(`${profile}: isolated compatibility batch preserves partial payments through real delivery and reload`,()=>{
 const input=profile==='kg-v1'?kgCompatibilityTerminal():clone(pm.fixtures.signedZeroQuota);
 let g=restore(input);assert.equal(g.serialize(),JSON.stringify(input));g.command({type:'borrowEmergencyVehicle',expectedSequence:0});
 const signed=clone(g.dispatch.fleetState.batches[0].orders),cash=g.dispatch.economyState.cashCents;
 g=finishOne(g);advance(g,60,false,true);g=roundTrip(g);
 assert.equal(g.dispatch.fleetState.batches[0].paidCount,1);assert.equal(g.dispatch.fleetState.batches[0].elapsedMs,120000);
 assert.deepEqual(g.dispatch.fleetState.batches[0].orders,signed);assert.equal(g.dispatch.economyState.npcCompletedOrders,1);
 assert.equal(g.dispatch.economyState.ledger.entries.filter(e=>e.id===`order:${signed[0].id}`).length,1);
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'borrowed');
 g=finishOne(g);advance(g,60,false,true);g=roundTrip(g);
 assert.equal(g.dispatch.economyState.npcCompletedOrders,2);assert.equal(g.dispatch.fleetState.batches.length,0);
 for(const q of signed){const paid=g.dispatch.economyState.ledger.entries.filter(e=>e.id===`order:${q.id}`);assert.equal(paid.length,1);assert.equal(paid[0].amountCents,q.incomeCents);}
 assert.ok(g.dispatch.economyState.cashCents>cash);
 g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'});roundTrip(g);
});

test('kg paid NPC history cannot carry an emergency vehicle source',()=>{
 let g=restore(kgCompatibilityTerminal());g.command({type:'borrowEmergencyVehicle',expectedSequence:0});g=finishOne(g);advance(g,60,false,true);
 const raw=JSON.parse(g.serialize());assert.equal(raw.dispatch.fleet.fleet.batches[0].paidCount,1);
 raw.dispatch.fleet.fleet.batches[0].orders[0].vehicleRef={kind:'emergency',loanSequence:1,policyId:'hero-emergency-base-v1'};
 assert.throws(()=>restore(raw));
});

test('isolated two-NPC compatibility input recovers one real car without cancelling other unpaid work',()=>{
 let g=restore(multiNPCCompatibilityTerminal());const before=g.dispatch.economyState;
 assert.equal(before.vehicles.length,2);assert.equal(before.hireCount,2);assert.equal(g.dispatch.emergencyLoanStatus.phase,'available');
 g.command({type:'borrowEmergencyVehicle',expectedSequence:0});
 assert.deepEqual(g.dispatch.economyState.vehicles,before.vehicles);assert.deepEqual(g.dispatch.economyState.ledger,before.ledger);
 const {quotes}=start(g);assert.ok(quotes[0].xpMultiplier>1,'real trained hero keeps the existing experience multiplier');assert.equal(quotes[0].incomeFactor,1);g=finish(g);
 for(let i=0;i<5&&g.dispatch.emergencyLoanStatus.phase!=='returnable';i++){
  for(let step=0;step<240&&g.dispatch.fleetState.quotaMs>0&&g.dispatch.emergencyLoanStatus.phase!=='returnable';step++)advance(g,.5,false,true);
  if(g.dispatch.emergencyLoanStatus.phase!=='returnable')g=finishOne(g);
 }
 assert.equal(g.dispatch.emergencyLoanStatus.phase,'returnable');g=roundTrip(g);
 const target=g.dispatch.emergencyLoanStatus.returnVehicleIds[0],remaining=clone(g.dispatch.economyState.fleetQuotes),ledger=clone(g.dispatch.economyState.ledger),fleet=g.dispatch.fleetState;
 assert.ok(remaining.length>0,'another NPC still owns unpaid signed work at the first real release');
 assert.ok(remaining.every(q=>q.vehicleId!==target));
 g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:target});assert.deepEqual(g.dispatch.economyState.fleetQuotes,remaining);assert.deepEqual(g.dispatch.economyState.ledger,ledger);
 assert.deepEqual(g.dispatch.fleetState,fleet);
 assert.equal(g.dispatch.economyState.riders[0].vehicleId,target);assert.equal(g.dispatch.economyState.vehicles.length,2);roundTrip(g);
});

test('isolated zero-stamina compatibility input borrows without stamina and uses actual free rest',()=>{
 const raw=clone(pm.fixtures.signedZeroQuota);raw.tripState.stamina=0;raw.tripState.blocked=true;
 let g=restore(raw);g.command({type:'borrowEmergencyVehicle',expectedSequence:0});assert.equal(g.tripState.stamina,0);
 atomicReject(g,()=>g.acceptBatch(offers(g)));
 const before=g.dispatch.economyState;g.supply('rest');g=roundTrip(g);advance(g,0);advance(g,20);
 assert.equal(g.tripState.stamina,100);assert.equal(g.tripState.action,null);assert.deepEqual(g.dispatch.economyState,before);assert.equal(g.dispatch.fleetState.quotaMs,0);
 g=finishOne(g);assert.equal(g.dispatch.economyState.heroCompletedOrders,before.heroCompletedOrders+1);roundTrip(g);
});

test('the original frozen readers reject all new containers, including returned loan history',()=>{
 const originals={economy:oldReader('domain/V2EconomySession').V2EconomySession,fleet:oldReader('domain/V2FleetSession').V2FleetSession,dispatch:oldReader('domain/V2DispatchSession').V2DispatchSession,game:oldReader('map-sample/V2GameSession').V2GameSession};
 assert.equal(originals.game.restore(city,JSON.stringify(pm.fixtures.signedZeroQuota),{preserveClock:true}).serialize(),JSON.stringify(pm.fixtures.signedZeroQuota));
 let g=borrowed();
 function rejectAll(){const s=g.snapshot();assert.throws(()=>originals.economy.restore(JSON.stringify(s.economy)));assert.throws(()=>originals.fleet.restore(JSON.stringify(s.fleet)));assert.throws(()=>originals.dispatch.restore(JSON.stringify(s),{verifyArrival:()=>false}));assert.throws(()=>originals.game.restore(city,g.serialize()));}
 rejectAll();g=finishOne(g);advance(g,60,false,true);g=finishOne(g);advance(g,60,false,true);g.command({type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'});rejectAll();roundTrip(g);
 const forged=JSON.parse(g.serialize());forged.dispatch.orders.find(o=>o.quote.vehicleRef).quote.vehicleRef.policyId='forged-returned-history';assert.throws(()=>restore(forged));
});
