const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
require('./legacy-order-fixture.cjs')(OrderBook);
function random(){let n=731;return()=>((n=(n*1664525+1013904223)>>>0)/4294967296);}
function city(){
 const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0}));
 return {title:'测试城',width:16000,height:1000,nodes,roads:[{id:'road',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
}
test('the lobby exposes ten stable nearby orders and opening it does not move the rider',()=>{
 const book=new OrderBook(city(),random()),ids=book.list().map(o=>o.offer.id),start=book.riderNode;
 assert.equal(ids.length,10);
 book.advance(30);assert.equal(book.mode,'idle');assert.equal(book.riderNode,start);
 assert.deepEqual(book.list().map(o=>o.offer.id),ids);
});
test('an accepted route starts at the rider, reaches the restaurant, then delivers to the customer',()=>{
 const data=city(),book=new OrderBook(data,random());const offer=book.list()[1].offer;
 book.accept(offer.id);const route=book.active.routes[0];
 assert.equal(route.nodes[0],book.riderNode);
 assert.equal(route.nodes[route.pickupIndex],data.pois[offer.from].node);
 assert.equal(route.nodes.at(-1),data.pois[offer.to].node);
 assert.throws(()=>book.accept(book.list()[2].offer.id));
 book.cancel();assert.equal(book.mode,'idle');assert.ok(book.list().some(o=>o.offer.id===offer.id));
});
test('delivery keeps advancing and settlement preserves nearby candidates while keeping ten orders',()=>{
 const book=new OrderBook(city(),random()),before=book.list().map(o=>o.offer.id),offer=book.list()[0].offer;
 book.accept(offer.id);book.depart();const total=book.progress.animationSeconds;
 assert.ok(total<=15);book.advance(total/2);book.togglePause();const elapsed=book.active.elapsed;
 book.advance(50);assert.ok(book.active.elapsed>elapsed);book.advance(total);
 assert.equal(book.mode,'done');assert.equal(book.completed,1);assert.equal(book.riderNode,book.data.pois[offer.to].node);
 book.advance(999);assert.equal(book.completed,1);book.finish();
 const after=book.list().map(o=>o.offer.id);
 assert.ok(!after.includes(offer.id));assert.equal(after.length,10);assert.equal(new Set(after).size,10);
});
test('continuous deliveries visit many destinations and never exceed the animation limit',()=>{
 const book=new OrderBook(city(),random()),destinations=new Set();
 for(let i=0;i<20;i++){
  const offer=book.list()[0].offer;destinations.add(offer.to);book.accept(offer.id);book.depart();
  assert.ok(book.progress.animationSeconds<=15);book.advance(20);if(book.mode==='arrived')book.settle(true);assert.equal(book.mode,'done');book.finish();
 }
 assert.ok(destinations.size>12);assert.equal(book.completed,20);
});

test('the actual city keeps ordinary dispatch and all offered route choices within ten kilometres',()=>{
 const data=require('../assets/resources/map-sample/city.json'),book=new OrderBook(data,random());
 const page=book.list(),times=page.map(p=>p.timing.displaySeconds);
 assert.ok(Math.min(...times)<20*60);
 assert.ok(Math.max(...times)>30*60);
 assert.equal(page.length,10);assert.equal(new Set(page.map(p=>p.offer.to)).size,10);
 for(const p of page)assert.ok(p.pickupMetres+p.deliveryMetres<=10000);
 for(const preview of page)assert.ok(preview.timing.animationSeconds<=15);
 const targets=new Set();
 for(let i=0;i<30;i++){
  const nearby=book.list();assert.equal(nearby.length,10);for(const p of nearby)assert.ok(p.pickupMetres+p.deliveryMetres<=10000);
  const offer=nearby[0].offer,start=book.riderNode;book.accept(offer.id);
  for(const route of book.active.routes){
   assert.ok(route.metres<=10000);
   assert.equal(route.nodes[0],start);
   assert.equal(route.nodes[route.pickupIndex],data.pois[offer.from].node);
   assert.equal(route.nodes.at(-1),data.pois[offer.to].node);
  }
  targets.add(offer.to);book.depart();assert.ok(book.progress.animationSeconds<=15);
  book.advance(99);if(book.mode==='arrived')book.settle(true);assert.equal(book.mode,'done');book.finish();
 }
 assert.ok(targets.size>12);
});


test('nearby dispatch uses both road legs and rejects a restaurant that is close only in a straight line',()=>{
 const nodes=[{id:'o',x:0,y:0},{id:'n',x:0,y:1000},{id:'a',x:0,y:6000},{id:'b',x:200,y:6000},{id:'r',x:200,y:0},{id:'d',x:400,y:0}];
 const data={title:'绕路城',width:1000,height:12000,nodes,roads:[{id:'loop',nodes:['o','n','a','b','r','d'],direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:[{name:'起点餐厅',node:'o',kind:'restaurant'},{name:'近点客户',node:'n',kind:'home'},{name:'近看远走餐厅',node:'r',kind:'restaurant'},{name:'近看远走客户',node:'d',kind:'home'}],areas:[],buildings:[],labels:[],waterways:[]};
 const book=new OrderBook(data,random());
 assert.equal(book.list().length,10);
 for(const p of book.list()){
  assert.equal(p.offer.from,0);assert.equal(p.offer.to,1);
  assert.equal(p.pickupMetres,0);assert.equal(p.deliveryMetres,1000);
 }
});

test('the next delivery starts at the previous customer and switches from pickup to delivery at the restaurant',()=>{
 const data=city(),book=new OrderBook(data,random());
 const first=book.list()[1].offer;
 book.accept(first.id);book.depart();book.advance(99);if(book.mode==='arrived')book.settle(true);book.finish();
 const end=data.pois[first.to].node,at=data.nodes.find(n=>n.id===end);
 assert.equal(book.riderNode,end);assert.deepEqual(book.riderPose.point,[at.x,at.y]);
 const restored=OrderBook.restore(data,book.serialize(),random());
 assert.equal(restored.riderNode,end);assert.deepEqual(restored.riderPose.point,[at.x,at.y]);
 const next=restored.list()[0].offer;restored.accept(next.id);
 const route=restored.active.routes[0];assert.equal(route.nodes[0],end);
 assert.equal(route.nodes[route.pickupIndex],data.pois[next.from].node);assert.equal(route.nodes.at(-1),data.pois[next.to].node);
 const pickup=route.segments.slice(0,route.pickupIndex).reduce((s,r)=>s+r.metres,0);
 assert.ok(pickup>0);restored.depart();assert.equal(restored.tripStage,'pickup');
 const total=restored.progress.animationSeconds;
 restored.advance(total*pickup/route.metres*.5);assert.equal(restored.tripStage,'pickup');
 restored.advance(total*pickup/route.metres*.5+.000001);assert.equal(restored.tripStage,'collecting');restored.advance(2);assert.equal(restored.tripStage,'delivery');
 restored.advance(99);if(restored.mode==='arrived')restored.settle(true);restored.finish();
 assert.equal(restored.riderNode,data.pois[next.to].node);
 for(const p of restored.list())assert.ok(p.pickupMetres+p.deliveryMetres<=10000);
});

test('new source and quantity survive reload; old absent fields remain absent; malformed metadata is rejected',()=>{
 const data=city(),book=new OrderBook(data,random()),before=JSON.parse(book.serialize());
 assert.equal(before.offers[0].source,'direct');for(const offer of before.offers){assert.ok(['direct','transfer'].includes(offer.source));assert.ok(offer.quantity>0);}
 const restored=OrderBook.restore(data,book.serialize(),()=>{throw Error('restore redrew an offer');});assert.equal(restored.serialize(),book.serialize());
 for(const offer of before.offers){delete offer.source;delete offer.quantity;delete offer.buyerNote;}
 const old=JSON.stringify(before);assert.equal(OrderBook.restore(data,old,()=>{throw Error('old restore redrew');}).serialize(),old);
 for(const [key,value]of [['source','market'],['quantity',0],['quantity',1.5],['buyerNote','x'.repeat(301)]]){const bad=JSON.parse(old);bad.offers[0][key]=value;assert.throws(()=>OrderBook.restore(data,JSON.stringify(bad)));}
});
test('lobby deadline agrees with the accepted frozen legal-route deadline for each candidate',()=>{
 const book=new OrderBook(city(),random());for(const preview of book.list()){book.accept(preview.offer.id);assert.equal(book.active.deadlineSeconds,preview.deadlineSeconds);book.cancel();}
});
test('source is stable near twenty percent and quantity/remarks use actual offer semantics',()=>{
 const {newOfferSource,offerQuantity,buyerRemark,foodDescription}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderPresentation.js'));
 let transfers=0;for(let i=2;i<=10001;i++){if(newOfferSource('CC-'+i)==='transfer')transfers++;assert.equal(newOfferSource('CC-'+i),newOfferSource('CC-'+i));}assert.ok(transfers>1700&&transfers<2300);
 const old={food:'麻婆豆腐饭 · 3份',demand:'none'};assert.equal(offerQuantity(old),3);assert.equal(offerQuantity({...old,food:'份数未知'}),null);assert.equal(buyerRemark(old),'');assert.equal(buyerRemark({...old,demand:'door'}),'放门口，别敲门');assert.equal(foodDescription({...old,quantity:2}),'麻婆豆腐饭 · 2份');
});

