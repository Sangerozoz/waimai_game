'use strict';
// Direct Dispatch compatibility inputs, not SDK success or browser/player paths.
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
module.exports=function matrix(variants,originalTerminal){
 const def={deferAuto:true,deferFleet:true},cases=[];
 const scenarios=['clock-edges','stopped-auto','pending-expiry','unseen-event','active-and-historical-batch','equal-separate-wallet','changed-port','accessor-port','invalid-clock','bad-wallet','bad-history','bad-reward','bad-version','bad-rebase','mixed-wallet','option-reads','option-auto-throws','option-auto-reentry','option-fleet-throws','option-inherited'];
 function run(v,profile,name){
  const port={verifyArrival:()=>true},D=v.Dispatch,E=v.Economy,records=[];let d=new D(port,0,profile);
  function step(label,action){
   const before=d.serialize();let result,error=null;
   try{result=action();}catch(e){error={name:e.name};assert.equal(d.serialize(),before,'rejection changed state: '+name+'/'+label);}
   const bytes=d.serialize();records.push({label,result:result===undefined?null:result,error,stateSHA256:sha(bytes),stateBytes:bytes});
  }
  function accept(id){
   if(profile==='kg-v1')d.acceptBatch([{id,kind:'ordinary',weightKg:1}]);
   else {
    // Use the real signed slot load for the same ID in both versions.
    const probe=new v.Economy('slots-v1'),quote=probe.acceptSlotBatch([{id,kind:'ordinary'}],{[id]:{deliveryMetres:100}})[0];
    d.acceptSlotBatch([{id,kind:'ordinary',load:quote.terms.load}],{[id]:{deliveryMetres:100}});
   }
  }
  switch(name){
   case 'clock-edges':
    for(const [seq,now,fg,paused] of [[1,10,false,false],[2,20,true,true],[3,20,true,false],[4,5,true,false],[5,21,true,false],[5,21,true,false],[5,22,true,false]])step('tick-'+seq+'-'+now,()=>d.tick(seq,now,fg,paused,def));
    d=D.restore(d.serialize(),port);step('restored-duplicate',()=>d.tick(5,21,true,false,def));step('restored-next',()=>d.tick(6,30,true,false,def));break;
   case 'stopped-auto':{
    const ticket=d.requestAd('auto',null,0,30);d.resolveAd(ticket,'completed',1);d.stopAutomation();
    step('manual-with-rights',()=>d.tick(1,2,true,false,def));step('resume',()=>d.resumeAutomation());step('auto',()=>d.tick(2,3,true,false,def));break;
   }
   case 'pending-expiry':{
    const ticket=d.requestAd('auto',null,0,1);step('expire',()=>d.tick(1,2,true,false,def));step('after-expire',()=>d.tick(2,3,true,false,def));step('stale-callback',()=>d.resolveAd(ticket,'completed',3));break;
   }
   case 'unseen-event':{
    const raw=d.snapshot(),e=E.restore(JSON.stringify(raw.economy));
    if(profile==='kg-v1')e.acceptOrdinary('matrix-unseen');else e.acceptSlotBatch([{id:'matrix-unseen',kind:'ordinary'}],{'matrix-unseen':{deliveryMetres:100}});
    e.completeDelivery('matrix-unseen');raw.economy=JSON.parse(e.serialize());raw.fleet.economy=JSON.parse(e.serialize());d=D.restore(JSON.stringify(raw),port,{preserveClock:true});
    step('pending-event',()=>d.tick(1,1,true,false,def));step('consumed-event',()=>d.tick(2,2,true,false,def));break;
   }
   case 'active-and-historical-batch':
    accept('matrix-history');step('before-complete',()=>d.tick(1,1,true,false,def));step('complete',()=>d.completeDelivery('matrix-history','arrival'));
    accept('matrix-pending');step('next-batch',()=>d.tick(2,2,true,false,def));step('cancel',()=>d.cancelRemaining());step('after-cancel',()=>d.tick(3,3,true,false,def));break;
   case 'equal-separate-wallet':
    Object.defineProperty(d.fleet,'economy',{value:E.restore(d.economy.serialize())});step('equal-wallet',()=>d.tick(1,1,true,false,def));step('upgrade',()=>d.command({type:'upgradeVehicle',vehicleId:'starter-1'}));step('after-upgrade',()=>d.tick(2,2,true,false,def));break;
   case 'changed-port':port.verifyArrival=null;step('invalid-port',()=>d.tick(1,1,true,false,def));break;
   case 'accessor-port':Object.defineProperty(port,'verifyArrival',{get(){return ()=>true;}});step(name,()=>d.tick(1,1,true,false,def));break;
   case 'option-reads':{
    let autoReads=0,fleetReads=0;const options={get deferAuto(){autoReads++;return true;},get deferFleet(){fleetReads++;return true;}};
    step(name,()=>({result:d.tick(1,1,true,false,options),autoReads,fleetReads}));assert.deepEqual([autoReads,fleetReads],[0,1]);break;
   }
   case 'option-auto-throws':{
    const options={get deferAuto(){throw Error('manual deferAuto must not run');},deferFleet:true};step(name,()=>d.tick(1,1,true,false,options));break;
   }
   case 'option-auto-reentry':{
    const options={get deferAuto(){d.command({type:'upgradeVehicle',vehicleId:'starter-1'});return true;},deferFleet:true};step(name,()=>d.tick(1,1,true,false,options));break;
   }
   case 'option-fleet-throws':{
    const options={deferAuto:true,get deferFleet(){throw Error('isolated deferFleet failure');}};step(name,()=>d.tick(1,1,true,false,options));break;
   }
   case 'option-inherited':step(name,()=>d.tick(1,1,true,false,Object.create({deferAuto:true,deferFleet:true})));break;
   case 'invalid-clock':
    step('valid-start',()=>d.tick(1,1,true,false,def));
    for(const [label,args] of [['zero',[0,2,true,false]],['fraction',[1.5,2,true,false]],['NaN-sequence',[NaN,2,true,false]],['negative-now',[2,-1,true,false]],['infinite-now',[2,Infinity,true,false]],['unsafe-ms',[2,1e20,true,false]],['bad-foreground',[2,2,1,false]],['bad-pause',[2,2,true,null]]])step(label,()=>d.tick(...args,def));break;
   case 'bad-wallet':d.economy.snapshot.state.cashCents++;step(name,()=>d.tick(1,1,true,false,def));break;
   case 'bad-history':accept('matrix-bad-history');d.completeDelivery('matrix-bad-history','arrival');d.orders[0].receipt.incomeCents++;step(name,()=>d.tick(1,1,true,false,def));break;
   case 'bad-reward':d.rewards.state.autoRemainingSeconds=600;step(name,()=>d.tick(1,1,true,false,def));break;
   case 'bad-version':d.version=99;step(name,()=>d.tick(1,1,true,false,def));break;
   case 'bad-rebase':d.firstTickAfterRestore='invalid';step(name,()=>d.tick(1,1,true,false,def));break;
   case 'mixed-wallet':{
    const e=E.restore(d.economy.serialize());e.upgradeVehicle('starter-1');Object.defineProperty(d.fleet,'economy',{value:e});step(name,()=>d.tick(1,1,true,false,def));break;
   }
   default:throw Error('Unknown scenario');
  }
  return records;
 }
 for(const profile of ['kg-v1','slots-v1'])for(const name of scenarios){
  const before=run(variants[0],profile,name),after=run(variants[1],profile,name);assert.equal(before.length,after.length);
  for(let i=0;i<before.length;i++){
   assert.equal(after[i].stateBytes,before[i].stateBytes,profile+'/'+name+'/'+before[i].label);
   assert.deepEqual(after[i].result,before[i].result);assert.deepEqual(after[i].error,before[i].error);
  }
  cases.push({profile,name,steps:before.map(({stateBytes,...record})=>record)});
 }
 const loan=variants.map(v=>{const port={verifyArrival:()=>true},d=v.Dispatch.restore(JSON.stringify(JSON.parse(originalTerminal).dispatch),port,{preserveClock:true});d.command({type:'borrowEmergencyVehicle',expectedSequence:0});const c=d.tickContext,result=d.tick(c.sequence+1,c.nowSeconds+1,true,false,def);return {result,bytes:d.serialize()};});
 assert.equal(loan[0].bytes,loan[1].bytes);assert.deepEqual(loan[0].result,loan[1].result);
 return {scope:'direct Dispatch paired compatibility/corruption inputs; ad rights from explicit isolated domain events, not SDK verification; error names, results and complete state bytes compared, error diagnostic text is not part of this equality claim',scenarioCount:cases.length+1,stepComparisons:cases.reduce((sum,c)=>sum+c.steps.length,0)+1,cases,emergencyClock:{result:loan[0].result,stateSHA256:sha(loan[0].bytes)}};
};
