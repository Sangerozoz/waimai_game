// Pending stage-completion authorization. No route simulation or SDK success stub is production code.
const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const base=path.dirname(process.env.MAP_ROUTER_MODULE);
const {V2DispatchSession}=require(path.join(base,'../domain/V2DispatchSession.js'));
const port={verifyArrival:(order,token)=>token===`arrived:${order.id}`};
const order=(id,weightKg=1)=>({id,weightKg,kind:'ordinary'});
const done=(s,id)=>s.completeDelivery(id,`arrived:${id}`);
test('batch capacity, individual arrival and idempotent payment with cancellation',()=>{
 const s=new V2DispatchSession(port);
 assert.throws(()=>s.acceptBatch([order('too-heavy',3)]));
 s.acceptBatch([order('a'),order('b')]);
 assert.throws(()=>s.completeDelivery('a','not arrived'));
 done(s,'b');assert.equal(s.economyState.heroCompletedOrders,1);
 const balance=s.economyState.cashCents;done(s,'b');assert.equal(s.economyState.cashCents,balance);
 s.cancelDelivery('a');assert.equal(s.economyState.heroCompletedOrders,1);
 assert.throws(()=>done(s,'a'));assert.throws(()=>s.acceptBatch([order('a')]));
});
test('batch errors leave all three states unchanged and snapshots restore partial completion',()=>{
 const s=new V2DispatchSession(port);const before=s.serialize();
 assert.throws(()=>s.acceptBatch([order('a'),order('a')]));assert.equal(s.serialize(),before);
 s.acceptBatch([order('a'),order('b')]);done(s,'a');
 const r=V2DispatchSession.restore(s.serialize(),port);done(r,'b');
 assert.equal(r.economyState.heroCompletedOrders,2);assert.equal(r.economyState.heroExperience,20);
 assert.equal(r.economyState.cashCents,14000);
});
test('special advertised price is fixed and exclusive, authorization consumed once',()=>{
 const s=new V2DispatchSession(port),c=s.enterLobby('open',0,.9999);
 const special={id:c.id,kind:'special',weightKg:1};
 assert.throws(()=>s.acceptBatch([special]));
 const t=s.requestAd('special',c.id,0,30);s.resolveAd(t,'completed',1);
 const before=s.serialize();assert.throws(()=>s.acceptBatch([special,order('n')]));assert.equal(s.serialize(),before);
 s.acceptBatch([special]);done(s,c.id);assert.equal(s.economyState.cashCents,25000);
 assert.throws(()=>s.acceptBatch([special]));
});
test('frame IDs freeze foreground budget, duplicate does not move twice, final slice hands off',()=>{
 const s=new V2DispatchSession(port),t=s.requestAd('auto',null,0,30);s.resolveAd(t,'completed',1);
 s.acceptBatch([order('a')]);
 assert.equal(s.tick(1,100,false,false).autoRunSeconds,0);
 assert.equal(s.tick(2,200,true,true).autoRunSeconds,0);
 assert.equal(s.tick(3,200,true,false).autoRunSeconds,0);
 assert.equal(s.tick(4,799,true,false).autoRunSeconds,599);
 assert.equal(s.tick(4,799,true,false).autoRunSeconds,0);
 assert.throws(()=>s.tick(4,800,true,false));
 const r=V2DispatchSession.restore(s.serialize(),port);
 assert.equal(r.tick(5,1000,true,false).autoRunSeconds,0);
 const last=r.tick(6,1050,true,false);
 assert.equal(last.autoRunSeconds,1);assert.equal(last.control,'manual');
 assert.equal(r.economyState.heroCompletedOrders,0); // elapsed time never fabricates arrival
 assert.equal(r.tick(7,1060,true,false).autoRunSeconds,0);
 done(r,'a');assert.equal(r.economyState.heroCompletedOrders,1);
});
test('restore rejects mismatched economic/reward/order state and replay counters',()=>{
 const s=new V2DispatchSession(port);s.acceptBatch([order('a')]);
 for(const edit of [x=>x.orders[0].weightKg=999,x=>x.rewards.activeBatch=null,x=>x.orders[0].id='wrong',x=>x.frame.sequence=-1]){
  const raw=JSON.parse(s.serialize());edit(raw);assert.throws(()=>V2DispatchSession.restore(JSON.stringify(raw),port));
 }
});
test('cancel named pending order cancels the entire remainder, preserving prior deliveries',()=>{
 const s=new V2DispatchSession(port);s.acceptBatch([order('a',.5),order('b',.5),order('c',.5)]);
 done(s,'a');s.cancelDelivery('b');
 assert.equal(s.economyState.heroCompletedOrders,1);assert.equal(s.economyState.cashCents,12000);
 assert.throws(()=>done(s,'b'));assert.throws(()=>done(s,'c'));assert.equal(s.snapshot().batchIds.length,0);
});
test('work-memory clones preserve automatic clock while clock rollback cannot replay elapsed time',()=>{
 let s=new V2DispatchSession(port),t=s.requestAd('auto',null,0,30);s.resolveAd(t,'completed',1);
 s=V2DispatchSession.restore(s.serialize(),port,{preserveClock:true});
 assert.equal(s.tick(1,11,true,false).autoRunSeconds,10);
 assert.equal(s.tick(2,5,true,false).autoRunSeconds,0);
 assert.equal(s.tick(3,12,true,false).autoRunSeconds,1);
});
test('hero completion refills fleet exactly once and all three states restore together',()=>{
 const s=new V2DispatchSession(port);
 for(let i=0;i<10;i++){s.acceptBatch([order(`first${i}`)]);done(s,`first${i}`);}
 const car=s.command({type:'buyVehicle',modelId:1});s.command({type:'assignVehicle',riderId:'hero',vehicleId:car});
 for(let i=0;i<5;i++){s.acceptBatch([order(`next${i}`)]);done(s,`next${i}`);}
 s.command({type:'hireRider',riderId:'npc-1'});s.command({type:'assignVehicle',riderId:'npc-1',vehicleId:'starter-1'});
 const quota=s.fleetState.quotaMs;done(s,'next4');assert.equal(s.fleetState.quotaMs,quota);
 s.tick(1,1,true,false);const saved=s.serialize(),r=V2DispatchSession.restore(saved,port);
 assert.equal(r.fleetState.quotaMs,s.fleetState.quotaMs);assert.equal(r.economyState.cashCents,s.economyState.cashCents);
 const corrupt=JSON.parse(saved);corrupt.economy.state.cashCents++;assert.throws(()=>V2DispatchSession.restore(JSON.stringify(corrupt),port));
});
test('SDK missing callback expires on tick, expired wait interval never becomes hero travel',()=>{
 const s=new V2DispatchSession(port);s.requestAd('auto',null,0,30);s.tick(1,100,true,false);
 assert.equal(s.snapshot().rewards.tickets[0].status,'expired');assert.equal(s.snapshot().control,'manual');
 const t=s.requestAd('auto',null,100,30);assert.equal(s.resolveAd(t,'completed',101),true);
 assert.equal(s.tick(2,102,true,false).autoRunSeconds,1);
});
test('auto ad resolving during authorized special keeps special manual but preserves auto entitlement',()=>{
 const s=new V2DispatchSession(port),special=s.enterLobby('entry',0,0);const t=s.requestAd('special',special.id,0,30);s.resolveAd(t,'completed',1);
 const auto=s.requestAd('auto',null,1,30);s.acceptBatch([{id:special.id,kind:'special',weightKg:1}]);
 assert.equal(s.resolveAd(auto,'completed',2),true);assert.equal(s.snapshot().control,'manual');assert.equal(s.snapshot().rewards.autoRemainingSeconds,600);
 done(s,special.id);s.resumeAutomation();assert.equal(s.snapshot().control,'auto');
});
