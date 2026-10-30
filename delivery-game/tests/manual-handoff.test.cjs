const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
function random(){let n=731;return()=>((n=(n*1664525+1013904223)>>>0)/4294967296);}
function city(){
 const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0}));
 return {title:'测试城',width:16000,height:1000,nodes,roads:[{id:'road',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
}
test('manual delivery saves each boundary and cannot skip pickup or departure',()=>{
 const data=city();let b=new OrderBook(data,random());const offer=b.list().find(p=>p.pickupMetres>0).offer;b.accept(offer.id);assert.equal(b.active.handoff.phase,'planning');
 const restore=()=>{b=OrderBook.restore(data,b.serialize(),()=>.99);};restore();b.depart();assert.equal(b.active.handoff.phase,'toPickup');b.advance(999);assert.equal(b.active.handoff.phase,'awaitPickup');restore();
 b.advance(999);assert.equal(b.active.handoff.phase,'awaitPickup');b.pickup();b.advance(1);assert.equal(b.active.handoff.phase,'picking');restore();assert.equal(b.active.pickupWaitElapsed,1);assert.throws(()=>b.cancel());b.advance(999);assert.equal(b.active.handoff.phase,'awaitDeliveryStart');restore();b.advance(999);assert.equal(b.active.handoff.phase,'awaitDeliveryStart');b.deliver();restore();b.advance(999);assert.equal(b.mode,'done');const receipt=b.active.receipt;assert.equal(b.settle().incomeCents,receipt.incomeCents);restore();assert.equal(b.active.receipt.incomeCents,receipt.incomeCents);
});
test('free cancellation mid-road retains the exact point, candidates and legal next route after reload',()=>{
 const data=city();let b=new OrderBook(data,random()),before=b.list(),offer=before.find(p=>p.pickupMetres>200).offer;b.accept(offer.id);b.depart();b.advance(.1);const pose=b.riderPose.point,player=b.player,ids=b.list().map(p=>p.offer.id);b.cancel();assert.deepEqual(b.riderPose.point,pose);assert.deepEqual(b.player,player);assert.deepEqual(b.list().map(p=>p.offer.id),ids);
 b=OrderBook.restore(data,b.serialize(),()=>.99);assert.deepEqual(b.riderPose.point,pose);b.accept(b.list()[0].offer.id);assert.ok(b.active.routes[0].origin);assert.deepEqual(b.riderPose.point,pose);b=OrderBook.restore(data,b.serialize(),()=>.99);assert.deepEqual(b.riderPose.point,pose);
});

test('unfinished legacy door order retains automatic movement and auto obeys its delivery requirement',()=>{
 const data=city(),book=new OrderBook(data,()=>.1);const offer=book.list().find(p=>p.offer.demand==='door').offer;book.accept(offer.id);const raw=JSON.parse(book.serialize());raw.version=3;delete raw.riderAnchor;delete raw.active.handoff;
 const old=OrderBook.restore(data,JSON.stringify(raw),()=>.99);old.depart();old.advance(999);assert.equal(old.mode,'done');assert.equal(old.active.receipt.outcome.doorAnswer,true);assert.equal(old.completed,1);
});

test('two cancellations inside a one-way prefix preserve all offers and never teleport',()=>{
 const data=city();data.roads[0].direction=1;let b=new OrderBook(data,random());const ids=b.list().map(p=>p.offer.id),choice=b.list().find(p=>p.available&&p.pickupMetres>400);assert.ok(choice);
 b.accept(choice.offer.id);b.depart();b.advance(.1);const first=b.riderPose.point;b.cancel();assert.deepEqual(b.riderPose.point,first);
 const rows=b.list();assert.equal(rows.length,10);assert.deepEqual(rows.map(p=>p.offer.id),ids);assert.ok(rows.some(p=>!p.available));
 const next=rows.find(p=>p.available&&p.pickupMetres>0);assert.ok(next);b.accept(next.offer.id);assert.deepEqual(b.riderPose.point,first);b.depart();b.advance(.001);const second=b.riderPose.point;b.cancel();assert.deepEqual(b.riderPose.point,second);
 b=OrderBook.restore(data,b.serialize(),()=>.99);assert.deepEqual(b.riderPose.point,second);assert.deepEqual(b.list().map(p=>p.offer.id),ids);
});

test('refresh after cancelling on a one-way segment generates only offers reachable from the exact position',()=>{
 const data=city();data.roads[0].direction=1;const b=new OrderBook(data,random());const chosen=b.list().find(p=>p.offer.from>=4&&p.available);assert.ok(chosen);b.accept(chosen.offer.id);b.depart();b.advance(.05);b.cancel();const position=b.riderPose.point;b.refreshFree();assert.deepEqual(b.riderPose.point,position);
 const list=b.list();assert.equal(list.length,10);assert.ok(list.every(p=>p.available));assert.ok(list.every(p=>data.nodes.find(n=>n.id===data.pois[p.offer.from].node).x>=position[0]));
});
