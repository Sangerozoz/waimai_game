const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const dir=path.dirname(process.env.MAP_ROUTER_MODULE),{prepareCity}=require(path.join(dir,'PlaceCatalog.js')),{OrderBook}=require(path.join(dir,'OrderBook.js'));
const raw=require('../assets/resources/map-sample/city.json');
function random(){let n=817;return()=>((n=(Math.imul(n,1664525)+1013904223)>>>0)/4294967296);}
const areaFor=(data,offer,start)=>require(path.join(dir,'DispatchAreas.js')).dispatchAreaForTrip(data,offer.from,offer.to,start);

test('normal operating points leave 450 metres at every edge and concentrate half of places in built-up cells',()=>{
 const data=prepareCity(raw),old=require('./fixtures/feedback-v3-baseline.json'),b=data.dispatchBounds,p=data.playBounds;
 assert.ok(b.minX>=p.minX+450&&b.maxX<=p.maxX-450&&b.minY>=p.minY+450&&b.maxY<=p.maxY-450,'450m operating inset');
 assert.equal(data.operatingPOIs.length,160);assert.equal(data.operatingPOIs.filter(i=>data.pois[i].kind==='restaurant').length,40);
 const urban=data.operatingPOIs.filter(i=>data.dispatchAreas[data.pois[i].node]==='urban');assert.ok(urban.length>=80);
 assert.deepEqual(data.pois.slice(0,old.catalog.pois.length),old.catalog.pois,'saved place indices and positions remain stable');
});

test('city lobbies favour urban orders with sparse remote and cross-town trips while keeping local travel times',()=>{
 const data=prepareCity(raw);assert.ok(data.dispatchAreas,'actual building-density areas are required');
 const book=new OrderBook(data,random()),totals={urban:0,suburb:0,remote:0,cross:0};
 for(let batch=0;batch<3;batch++){
  const rows=book.list(),counts={urban:0,suburb:0,remote:0,cross:0};
  for(const row of rows){const area=areaFor(data,row.offer,book.riderNode);counts[area]++;totals[area]++;assert.ok(row.timing.displaySeconds<=1800);}
  assert.ok(counts.urban>=5,JSON.stringify(counts));assert.ok(counts.cross<=1);assert.ok(counts.remote<=2);
  assert.ok(rows.filter(r=>r.timing.displaySeconds<=1200).length>=8);assert.equal(new Set(rows.map(r=>r.offer.to)).size,10);
  if(batch<2)book.refreshFree();
 }
 assert.ok(totals.urban>=15);assert.ok(totals.suburb>totals.remote&&totals.remote>totals.cross,JSON.stringify(totals));assert.ok(totals.cross<=2);
 for(let i=0;i<8;i++){
  const offer=book.list()[i%10].offer;book.accept(offer.id);book.depart();book.advance(99);if(book.mode==='arrived')book.settle(true);book.finish();
  assert.ok(book.list().filter(r=>areaFor(data,r.offer,book.riderNode)==='urban').length>=5,'moving must not scatter the next lobby');
 }
});

function lineCity(){
 const nodes=Array.from({length:9},(_,i)=>({id:String(i),x:i*400,y:0}));
 return {title:'取餐停顿',width:4000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:'点'+i,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
}
test('arrival at the merchant holds for two real seconds and resumes the remaining hold after reload',()=>{
 const data=lineCity(),book=new OrderBook(data,()=>.99),offer=book.list().find(r=>r.pickupMetres>0).offer;book.accept(offer.id);book.depart();
 const route=book.active.routes[0],pickup=route.segments.slice(0,route.pickupIndex).reduce((n,s)=>n+s.metres,0),at=book.progress.animationSeconds*pickup/route.metres;
 book.advance(at);assert.equal(book.tripStage,'collecting');const pose=book.riderPose,remaining=book.progress.remainingSeconds;
 book.advance(.8);assert.deepEqual(book.riderPose,pose);assert.equal(book.progress.remainingSeconds,remaining);
 const restored=OrderBook.restore(data,book.serialize(),()=>{throw Error('hold restore must not reroll');});
 restored.advance(1.19);assert.equal(restored.tripStage,'collecting');assert.deepEqual(restored.riderPose,pose);
 restored.advance(.02);assert.equal(restored.tripStage,'delivery');assert.notDeepEqual(restored.riderPose.point,pose.point);
 const invalid=JSON.parse(book.serialize());invalid.active.pickupWaitElapsed=2.1;assert.throws(()=>OrderBook.restore(data,JSON.stringify(invalid)),/存档/);
});

test('starting at the merchant still collects the food for two seconds without inflating travel minutes',()=>{
 const data=lineCity(),book=new OrderBook(data,()=>.99),row=book.list()[0];book.accept(row.offer.id);book.depart();
 const start=book.riderPose.point,display=book.progress.displaySeconds;assert.equal(book.tripStage,'collecting');
 book.advance(1.9);assert.deepEqual(book.riderPose.point,start);assert.equal(book.progress.displaySeconds,display);
 book.advance(.2);assert.equal(book.tripStage,'delivery');assert.notDeepEqual(book.riderPose.point,start);
});

test('the previous v3 activity keeps its road clock, drawn outcome and receipt during the new-area migration',()=>{
 const data=prepareCity(raw),fixture=require('./fixtures/feedback-v3-baseline.json');
 for(const saved of Object.values(fixture.states)){
  const book=OrderBook.restore(data,JSON.stringify(saved),()=>{throw Error('migration must not consume business RNG');});
  assert.deepEqual(book.active,saved.active);assert.deepEqual(book.player,saved.player);assert.equal(book.riderNode,saved.currentNode);
  const stable=book.serialize();assert.equal(OrderBook.restore(data,stable,()=>{throw Error('second restore must not reroll');}).serialize(),stable);
 }
});
