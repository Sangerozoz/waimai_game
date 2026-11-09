// Pending stage authorization: written only, never executed in this batch.
const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const base=path.dirname(process.env.MAP_ROUTER_MODULE);
const {V2TripRules}=require(path.join(base,'../domain/V2TripRules.js'));
const {V2_SUPPLY_CATALOG}=require(path.join(base,'../domain/V2SupplyCatalog.js'));
function depleted(stamina=0){const s=new V2TripRules().state;s.stamina=stamina;s.blocked=stamina===0;return V2TripRules.restore(s);}
test('six supplies retain V1 price/effect/time and highest purchased map unlock',()=>{
 assert.deepEqual(V2_SUPPLY_CATALOG.map(x=>[x.costCents,x.restore,x.durationSeconds,x.gameSeconds]),[[100,20,1,30],[300,70,3,120],[400,40,1,30],[900,90,2,60],[700,60,1,30],[1500,100,1,30]]);
 for(const item of V2_SUPPLY_CATALOG){const t=depleted();let paid=0;assert.throws(()=>t.startSupply(item.id,true,c=>paid+=c,false,'purchase',0));t.startSupply(item.id,true,c=>paid+=c,false,'purchase',5);assert.equal(paid,item.costCents);t.advanceSupply(item.durationSeconds/2);const resumed=V2TripRules.restore(t.state);resumed.advanceSupply(item.durationSeconds/2);assert.equal(resumed.state.stamina,item.restore);assert.equal(paid,item.costCents);}
});
test('full stamina and absent inventory never charge, unknown reward never grants',()=>{
 const t=new V2TripRules();let paid=0;assert.throws(()=>t.startSupply('water',true,c=>paid+=c));assert.equal(paid,0);
 const r=depleted();assert.throws(()=>r.startSupply('water',true,c=>paid+=c,false,'inventory'));assert.equal(paid,0);assert.throws(()=>r.claimSupplyReward('grant-1','unconfigured'));assert.equal(r.state.inventory.water,0);
});
test('automatic defaults are no paid/no inventory; budget lifetime survives toggles',()=>{
 const t=depleted(55);t.configureAutoSupply({enabled:true,budgetCents:1000});assert.equal(t.chooseAutoSupply(5,1000),null);
 t.configureAutoSupply({enabled:true,budgetCents:1000,allowPaid:true});assert.equal(t.chooseAutoSupply(5,1000).kind,'drink');
 const choice=t.chooseAutoSupply(5,1000);t.startSupply(choice.kind,true,()=>{},true,choice.source,5);const spent=t.state.autoSupplyPolicy.spentCents;
 t.configureAutoSupply({enabled:false,budgetCents:1000});t.configureAutoSupply({enabled:true,budgetCents:1000});assert.equal(t.state.autoSupplyPolicy.spentCents,spent);assert.throws(()=>t.configureAutoSupply({enabled:true,budgetCents:spent-1}));
});
test('legacy pending purchases migrate once; source/cost tampering rejects',()=>{
 const t=depleted();t.startSupply('water',true,()=>{});const raw=t.state;raw.version=1;delete raw.batchAccounting;delete raw.inventory;delete raw.inventoryUsed;delete raw.supplyGrants;delete raw.action.source;raw.autoSupplyPolicy.kind='water';delete raw.autoSupplyPolicy.allowPaid;delete raw.autoSupplyPolicy.useInventory;
 const r=V2TripRules.restore(raw);assert.equal(r.state.action.source,'purchase');assert.equal(r.state.autoSupplyPolicy.allowPaid,false);r.advanceSupply(1);assert.equal(r.state.stamina,20);
 const bad=t.state;bad.action.source='inventory';assert.throws(()=>V2TripRules.restore(bad));
});
test('approved fixture grants are idempotent, inventory action spends no cash and restores once',()=>{
 // Test-only approved task table, never added to the shipped empty reward catalog.
 const catalog=require(path.join(base,'../domain/V2SupplyCatalog.js')),previous=catalog.V2_SUPPLY_REWARDS;
 catalog.V2_SUPPLY_REWARDS=[{id:'fixture-completed-task',items:[{kind:'water',quantity:2}]}];
 try{
  const t=depleted();assert.equal(t.claimSupplyReward('fixture-grant','fixture-completed-task'),true);assert.equal(t.claimSupplyReward('fixture-grant','fixture-completed-task'),false);assert.equal(t.state.inventory.water,2);assert.throws(()=>t.claimSupplyReward('new-grant','fixture-completed-task'));assert.throws(()=>t.claimSupplyReward('fixture-grant','different-task'));
  let charged=0;t.startSupply('water',true,c=>charged+=c,false,'inventory');assert.equal(charged,0);assert.equal(t.state.inventory.water,1);assert.equal(t.state.inventoryUsed.water,1);assert.equal(t.state.action.source,'inventory');
  t.advanceSupply(.5);const resumed=V2TripRules.restore(t.state);resumed.advanceSupply(.5);assert.equal(resumed.state.stamina,20);assert.equal(resumed.state.inventory.water,1);assert.equal(resumed.state.inventoryUsed.water,1);
  const tampered=t.state;tampered.inventory.water++;assert.throws(()=>V2TripRules.restore(tampered));
  const full=t.state;full.action=null;full.stamina=100;const r=V2TripRules.restore(full);assert.throws(()=>r.startSupply('water',false,()=>charged++,false,'inventory'));assert.equal(r.state.inventory.water,1);
 }finally{catalog.V2_SUPPLY_REWARDS=previous;}
});
test('batch supply accounting starts uniformly at begin and survives cancel/restore',()=>{
 const t=depleted(50);t.startSupply('water',false,()=>{});t.advanceSupply(1);
 t.begin(1,1,[{id:'batch-a',fastestGameSeconds:5,heldMetres:10,safe:true}]);assert.equal(t.state.batchAccounting.supplySpentCentsStart,100);
 t.startSupply('water',true,()=>{});t.advanceSupply(1);assert.equal(t.state.supplySpentCents-t.state.batchAccounting.supplySpentCentsStart,100);
 t.cancel();const restored=V2TripRules.restore(t.state);assert.deepEqual(restored.state.batchAccounting.orderIds,['batch-a']);
 restored.begin(1,2,[{id:'batch-b',fastestGameSeconds:5,heldMetres:10,safe:true}]);assert.equal(restored.state.batchAccounting.supplySpentCentsStart,200);
});
test('finished and cancelled batch costs freeze before idle supplies',()=>{
 const t=depleted(20);t.begin(1,1,[{id:'a',fastestGameSeconds:10,heldMetres:10,safe:true}]);t.service('a','pickup');t.startSupply('water',true,()=>{});t.advanceSupply(1);t.delivered('a',1);
 const cost=t.state.batchAccounting.end.supplySpentCents;t.startSupply('water',false,()=>{});t.advanceSupply(1);assert.equal(t.state.batchAccounting.end.supplySpentCents,cost);assert.ok(t.state.supplySpentCents>cost);assert.doesNotThrow(()=>V2TripRules.restore(t.state));
});
