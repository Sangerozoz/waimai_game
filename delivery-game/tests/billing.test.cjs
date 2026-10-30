const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
require('./legacy-order-fixture.cjs')(OrderBook);
function setup(){
 const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0}));
 const data={title:'账单测试',width:16000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
 let day='2026-10-28';const today=()=>day;return {b:new OrderBook(data,()=>.99,today),data,today,setDay:d=>{day=d;}};
}
function complete(b){b.accept(b.list()[0].offer.id);const metres=b.active.routes[b.active.selected].metres;b.depart();b.advance(99);if(b.mode==='arrived')b.settle(true);return {receipt:b.active.receipt,metres};}
test('new bill starts with the actual wallet and no earned fees or completed deliveries',()=>{
 const {b}=setup();assert.ok(b.billing,'the player can read a bill');
 assert.equal(b.billing.walletCents,10000);assert.equal(b.billing.completedOrders,0);assert.equal(b.billing.totalIncomeCents,0);assert.equal(b.billing.today.orders,0);assert.equal(b.billing.partialHistory,false);
});
test('settlement records real income and full road distance exactly once across reload and repeated receipt viewing',()=>{
 const {b,data,today}=setup(),{receipt,metres}=complete(b);
 assert.equal(b.billing.today.incomeCents,2180);assert.equal(b.billing.today.orders,1);assert.equal(b.billing.today.metres,metres);assert.equal(b.billing.today.late,0);
 assert.equal(b.billing.totalIncomeCents,2180);assert.equal(b.billing.highestDailyOrders,1);
 const before=b.billing;b.settle();const restored=OrderBook.restore(data,b.serialize(),()=>.99,today);assert.deepEqual(restored.billing,before);assert.deepEqual(restored.settle(),receipt);assert.deepEqual(restored.billing,before);
});
test('cancelled offers and vehicle purchases do not count as deliveries or reduce delivery income',()=>{
 const {b}=setup();b.accept(b.list()[0].offer.id);b.cancel();assert.equal(b.billing.today.orders,0);
 for(let i=0;i<6;i++){complete(b);b.finish();}
 const fees=b.billing.totalIncomeCents,orders=b.billing.today.orders,wallet=b.billing.walletCents;b.upgradeVehicle();
 assert.equal(b.billing.totalIncomeCents,fees);assert.equal(b.billing.today.orders,orders);assert.equal(b.billing.walletCents,wallet-20000);
});
test('daily records roll over without resetting lifetime income and peak daily completed count',()=>{
 const {b,setDay,data,today}=setup();complete(b);b.finish();complete(b);b.finish();const fees=b.billing.totalIncomeCents;
 setDay('2026-10-29');assert.equal(b.billing.today.orders,0);assert.equal(b.billing.totalIncomeCents,fees);assert.equal(b.billing.highestDailyOrders,2);
 complete(b);assert.equal(b.billing.today.orders,1);assert.equal(b.billing.completedOrders,3);assert.equal(b.billing.highestDailyOrders,2);
 const restored=OrderBook.restore(data,b.serialize(),()=>.99,today);assert.deepEqual(restored.billing,b.billing);
});
test('online time splits at local midnight and never counts backwards or invalid spans',()=>{
 const {b,setDay}=setup(),start=new Date(2026,9,28,23,59,59,0).getTime(),end=start+3000;
 b.recordOnlineTime(start,end);assert.equal(b.billing.today.onlineMs,1000);
 setDay('2026-10-29');assert.equal(b.billing.today.onlineMs,2000);
 for(const pair of [[end,start],[NaN,end],[start,Infinity]])b.recordOnlineTime(...pair);
 assert.equal(b.billing.today.onlineMs,2000);
});
test('old saves preserve actual lifetime orders and wallet while marking unavailable history as partial',()=>{
 const {b,data,today,setDay}=setup();complete(b);b.finish();const raw=JSON.parse(b.serialize());delete raw.billing;
 const restored=OrderBook.restore(data,JSON.stringify(raw),()=>.99,today);assert.equal(restored.billing.completedOrders,1);assert.equal(restored.billing.walletCents,b.player.cashCents);
 assert.equal(restored.billing.partialHistory,true);assert.equal(restored.billing.partialToday,true);assert.equal(restored.billing.today.orders,0);
 complete(restored);assert.equal(restored.billing.completedOrders,2);assert.equal(restored.billing.today.orders,1);
 setDay('2026-10-29');assert.equal(restored.billing.partialToday,false);assert.equal(restored.billing.today.orders,0);
 const again=OrderBook.restore(data,restored.serialize(),()=>.99,today);assert.deepEqual(again.billing,restored.billing);
});
test('malformed bill fields and totals inconsistent with completed orders are rejected',()=>{
 const {b,data,today}=setup();complete(b);
 for(const edit of [s=>s.billing=null,s=>s.billing.baselineOrders=-1,s=>s.billing.lastCompletedOrders++,s=>s.billing.days['2026-10-28'].orders++,s=>s.billing.days['2026-10-28'].late=2,s=>s.billing.days['2026-10-28'].onlineMs=-1,s=>s.billing.days['2026-10-28'].incomeCents=.5]){
  const raw=JSON.parse(b.serialize());assert.ok(raw.billing);edit(raw);assert.throws(()=>OrderBook.restore(data,JSON.stringify(raw),()=>.99,today),/存档/);
 }
});
test('legacy doorstep deliveries follow the required instruction automatically',()=>{
 const {b}=setup();complete(b);b.finish();
 // The same honest county outcome model drives both receipt and statistics.
 const raw=JSON.parse(b.serialize());raw.offers[0].demand='door';
 const edited=OrderBook.restore(b.data,JSON.stringify(raw),()=>.99,()=> '2026-10-28');
 edited.accept(edited.list()[0].offer.id);edited.depart();edited.advance(99);edited.settle(false);
 assert.equal(edited.active.receipt.outcome.doorAnswer,true);assert.equal(edited.active.receipt.ratingDelta,2);assert.equal(edited.billing.today.bad,0);assert.equal(edited.billing.today.good,1);assert.equal(edited.billing.today.late,0);
});
test('late and positive receipts produce correct rate, review counts and unit-formatted bill values',()=>{
 const base=path.dirname(process.env.MAP_ROUTER_MODULE),{DeliveryLedger}=require(path.join(base,'DeliveryLedger.js'));
 const {countySettlement,newCountyPlayer}=require(path.join(base,'CountyRules.js')),{billingRows}=require(path.join(base,'BillingPresentation.js'));
 const ledger=new DeliveryLedger(undefined,0,'2026-10-28'),offer={id:'CC-1',feeCents:2000,type:'normal',fragility:'normal',demand:'none'};
 const late=countySettlement(newCountyPlayer(),offer,{displaySeconds:900,deadlineSeconds:600,damage:'none',doorAnswer:null});
 ledger.recordDelivery(late.receipt,1200,'2026-10-28');
 const good=countySettlement(late.player,{...offer,id:'CC-2',type:'urgent'},{displaySeconds:600,deadlineSeconds:600,damage:'none',doorAnswer:null});
 ledger.recordDelivery(good.receipt,1800,'2026-10-28');
 ledger.recordOnlineTime(new Date(2026,9,28,10).getTime(),new Date(2026,9,28,10,2,10).getTime());
 const rows=Object.fromEntries(billingRows(ledger.view('2026-10-28',good.player.cashCents,2)).map(r=>[r.title,r.value]));
 assert.equal(rows['准时率'],'50.0%');assert.equal(rows['今日好评'],'1');assert.equal(rows['差评'],'1');assert.equal(rows['超时'],'1');
 assert.equal(rows['配送里程'],'3.00 km');assert.equal(rows['在线时长'],'0:02:10');assert.equal(rows['今日收入'],'¥43.36');assert.equal(rows['钱包余额'],'¥143.36');
});
test('incomplete legacy history is never presented as an exact percentage or exact lifetime fee',()=>{
 const base=path.dirname(process.env.MAP_ROUTER_MODULE),{DeliveryLedger}=require(path.join(base,'DeliveryLedger.js')),{billingRows}=require(path.join(base,'BillingPresentation.js'));
 const ledger=new DeliveryLedger(undefined,9,'2026-10-28',true);
 const rows=Object.fromEntries(billingRows(ledger.view('2026-10-28',22238,9)).map(r=>[r.title,r.value]));
 assert.equal(rows['累计完成订单'],'9');assert.equal(rows['钱包余额'],'¥222.38');assert.equal(rows['准时率'],'—');assert.equal(rows['今日订单数'],'≥0');assert.equal(rows['累计配送费'],'≥¥0.00');
});
