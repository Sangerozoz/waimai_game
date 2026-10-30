const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const dir=path.dirname(process.env.MAP_ROUTER_MODULE);
const extent=require(path.join(dir,'CityExtent.js'));
const places=require(path.join(dir,'PlaceCatalog.js'));
const foods=require(path.join(dir,'FoodCatalog.js'));
const {OrderBook}=require(path.join(dir,'OrderBook.js'));
const {countyMapId}=require(path.join(dir,'CountySnapshot.js'));
const raw=require('../assets/resources/map-sample/city.json');
function random(){let n=817;return()=>((n=(n*1664525+1013904223)>>>0)/4294967296);}
const inside=(b,p)=>p[0]>=b.minX&&p[0]<=b.maxX&&p[1]>=b.minY&&p[1]<=b.maxY;

test('camera subtracts viewport half extents on every axis at all supported scales',()=>{
 const b={minX:-4530,maxX:-570,minY:-1410,maxY:1110};
 for(const h of [748,1030,1348])for(const scale of [.6,1.2,2])for(const offset of [[1e6,1e6],[-1e6,-1e6],[0,0]]){
  const [x,y]=extent.clampCamera(b,offset,scale,720,h);
  assert.ok((-360-x)/scale>=b.minX-1e-8);assert.ok((360-x)/scale<=b.maxX+1e-8);
  assert.ok((-h/2-y)/scale>=b.minY-1e-8);assert.ok((h/2-y)/scale<=b.maxY+1e-8);
 }
});

test('catalog preparation is deterministic, preserves the graph and old POI indices, and adds real distinct addresses',()=>{
 const data=places.prepareCity(raw),again=places.prepareCity(JSON.parse(JSON.stringify(raw)));
 assert.equal(data.nodes,raw.nodes);assert.equal(data.roads,raw.roads);assert.equal(raw.pois.length,128);
 assert.deepEqual(data.pois.slice(0,128).map(({name,node,kind})=>({name,node,kind})),raw.pois);assert.deepEqual(data.pois,again.pois);
 assert.equal(places.prepareCity(data),data);assert.equal(places.prepareCity(raw),data);
 assert.ok(data.legacyMapIds.includes(countyMapId(raw)));assert.ok(!data.legacyMapIds.includes(countyMapId({...raw,nodes:raw.nodes.map((n,i)=>i? n:{...n,x:n.x+1})})));
 const nodes=new Map(data.nodes.map(n=>[n.id,n])),city=data.pois.filter(p=>{const n=nodes.get(p.node);return inside(data.playBounds,[n.x,n.y]);});
 assert.ok(city.filter(p=>p.kind==='restaurant').length>=40);assert.ok(city.filter(p=>p.kind!=='restaurant').length>=120);
 assert.ok(city.every(p=>p.address));assert.equal(new Set(city.map(p=>p.address)).size,city.length);
 assert.equal(new Set(data.pois.map(p=>p.name)).size,data.pois.length);
 assert.equal(new Set(data.pois.map(p=>p.node)).size,data.pois.length);
 const {RoadRouter}=require(process.env.MAP_ROUTER_MODULE),router=new RoadRouter({...data,nodes:data.nodes.filter(n=>inside(data.playBounds,[n.x,n.y]))});
 for(const p of data.pois.slice(128)){assert.ok(p.address);assert.ok(router.find(data.pois[0].node,p.node,'fast'));assert.ok(router.find(p.node,data.pois[0].node,'fast'));}
 assert.equal(new Set(data.pois.slice(128).map(p=>p.address)).size,data.pois.length-128);
});

test('food images and terms cover all sixteen meals and historic text has stable compatible pictures',()=>{
 assert.deepEqual(foods.FOOD_CATALOG.map(f=>f.name),['鸡腿饭','牛肉饭','红烧肉饭','麻婆豆腐饭','鲜汤面','拌面','馄饨','小火锅','饺子','包子','披萨','汉堡','轻食沙拉','寿司','蛋糕','奶茶']);
 assert.deepEqual(foods.FOOD_CATALOG.map(f=>f.imageIndex),Array.from({length:16},(_,i)=>i));
 assert.equal(foods.foodForOffer('家常饭盒 · 1份').imageIndex,0);
 assert.equal(foods.foodForOffer('家常饭 · 3份').imageIndex,0);
 assert.equal(foods.foodForOffer('小炒套餐 · 2份').imageIndex,2);
 assert.equal(foods.foodForOffer('鲜汤面 · 2份').imageIndex,4);
 assert.equal(foods.foodForOffer('奶茶 · 2份').fragility,'fragile');
});

test('actual prepared city dispatch stays within bounded roads with diverse batches and refreshes',()=>{
 const data=places.prepareCity(raw),book=new OrderBook(data,random()),destinations=new Set(),merchants=new Set();
 for(let batch=0;batch<3;batch++){
  const page=book.list();assert.equal(page.length,10);assert.equal(new Set(page.map(p=>p.offer.to)).size,10);
  assert.ok(new Set(page.map(p=>p.offer.from)).size>=7);
  // Class probabilities take priority over a forced number of dishes in ten random offers.
  // Within each class, all real dishes are used before any is repeated.
  for(const kind of ['fragile','normal','durable']){
   const ids=page.filter(p=>p.offer.fragility===kind).map(p=>foods.foodForOffer(p.offer.food).id);
   const poolSize=foods.FOOD_CATALOG.filter(f=>f.fragility===kind).length;
   assert.equal(new Set(ids).size,Math.min(poolSize,ids.length));
  }
  for(const {offer,pickupMetres,deliveryMetres} of page){
   destinations.add(offer.to);merchants.add(offer.from);
   assert.ok(pickupMetres+deliveryMetres<=10000);
   assert.equal(offer.fragility,foods.foodForOffer(offer.food).fragility);
   book.accept(offer.id);for(const r of book.active.routes){assert.ok(r.metres<=10000);for(const p of r.points)assert.ok(inside(data.playBounds,p));}book.cancel();
  }
  if(batch<2)book.refreshFree();
 }
 // Local dispatch keeps merchant diversity within the rider's neighbourhood rather than rotating across the entire town.
 assert.ok(destinations.size>=25);assert.ok(merchants.size>=10);
});

test('old map identity restores fixed activity and outside position, then returns through legal road legs',()=>{
 const data=places.prepareCity(raw),saved=require('../../docs/reviews/stage-one-final/pre-scenery-valid-save.json');
 const original=typeof saved==='string'?saved:JSON.stringify(saved);
 const before=OrderBook.restore(raw,original,()=>.99),book=OrderBook.restore(data,original,()=>{throw Error('migration must not consume RNG');});
 assert.equal(book.riderNode,before.riderNode);assert.deepEqual(book.riderPose,before.riderPose);
 for(const key of ['cashCents','rating','experience','vehicleTier'])assert.equal(book.player[key],before.player[key]);
 if(before.active){assert.deepEqual(book.active.routes,before.active.routes);assert.deepEqual(book.active.damage,before.active.damage);assert.deepEqual(book.active.receipt,before.active.receipt);}
 if(book.mode==='routes')book.depart();book.advance(99);if(book.mode==='arrived')book.settle(true);if(book.mode==='done')book.finish();
 for(const preview of book.list())assert.ok(preview.pickupMetres+preview.deliveryMetres<=10000);
 book.accept(book.list()[0].offer.id);assert.equal(book.active.routes[0].nodes[0],book.riderNode);
 const stable=book.serialize();assert.equal(OrderBook.restore(data,stable,()=>{throw Error('stable restore rerolled');}).serialize(),stable);
 const forged=JSON.parse(original);forged.mapId='forged-map';assert.throws(()=>OrderBook.restore(data,JSON.stringify(forged)),/路网/);
});

test('preview and all accepted choices use the bounded graph even when a faster road exits town',()=>{
 const nodes=[{id:'a',x:100,y:100},{id:'b',x:300,y:100},{id:'c',x:500,y:100},{id:'d',x:700,y:100},{id:'out',x:400,y:1200}];
 const road=(id,ids,speed)=>({id,nodes:ids,speed,direction:0,roughness:.1,kind:'residential',width:5,bridge:false});
 const data={title:'有界城',width:2000,height:3000,nodes,roads:[road('inside',['a','b','c','d'],1),road('shortcut',['a','out','d'],100)],pois:[{name:'甲店',node:'a',kind:'restaurant'},{name:'乙店',node:'c',kind:'restaurant'},{name:'甲家',node:'b',kind:'home'},{name:'乙家',node:'d',kind:'home'}],buildings:[],areas:[],waterways:[],labels:[],playBounds:{minX:0,maxX:1000,minY:0,maxY:1000}};
 const b=new OrderBook(data,()=>.99);
 for(const preview of b.list()){
  b.accept(preview.offer.id);assert.equal(b.active.routes[0].metres,preview.pickupMetres+preview.deliveryMetres);
  for(const route of b.active.routes)assert.ok(!route.nodes.includes('out'));b.cancel();
 }
});

test('a tiny map repeats legal destinations without hanging and food weights match servings',()=>{
 const data={title:'小城',width:1000,height:1000,nodes:[{id:'a',x:0,y:0},{id:'b',x:100,y:0}],roads:[{id:'r',nodes:['a','b'],speed:6,direction:0,roughness:.1,kind:'residential',width:5,bridge:false}],pois:[{name:'唯一店',node:'a',kind:'restaurant'},{name:'唯一家',node:'b',kind:'home'}],buildings:[],areas:[],waterways:[],labels:[]};
 const b=new OrderBook(data,()=>.99);b.refreshFree();
 assert.equal(b.list().length,10);assert.equal(new Set(b.list().map(p=>p.offer.to)).size,1);
 for(const {offer} of b.list()){
  const food=foods.foodForOffer(offer.food),quantity=Number(offer.food.match(/(\d+)份/)[1]);
  assert.equal(offer.weightKg,food.unitWeightKg*quantity);assert.ok(offer.weightKg<=5);assert.equal(offer.fragility,food.fragility);
 }
});

test('distant legacy positions preserve location and can dispatch within ten kilometres without an immediate city return',()=>{
 const data=places.prepareCity(raw),seedBook=new OrderBook(raw,()=>.99),saved=JSON.parse(seedBook.serialize());
 for(const index of [8,31,55,89,115,127]){
  saved.currentNode=raw.pois[index].node;
  const b=OrderBook.restore(data,JSON.stringify(saved),()=>{throw Error('migration rerolled');});
  assert.equal(b.riderNode,saved.currentNode);assert.equal(b.list().length,10);
  for(const p of b.list())assert.ok(p.pickupMetres+p.deliveryMetres<=10000);
  b.accept(b.list()[0].offer.id);assert.equal(b.active.routes[0].nodes[0],saved.currentNode);
 }
});

test('map identity migration keeps an already drawn outside delivery route, pose and damage unchanged',()=>{
 const data=places.prepareCity(raw),old=new OrderBook(raw,random()),nodes=new Map(raw.nodes.map(n=>[n.id,n]));
 const offer=old.list().find(({offer})=>{const n=nodes.get(raw.pois[offer.to].node);return !inside(data.playBounds,[n.x,n.y]);}).offer;
 old.accept(offer.id);old.depart();old.advance(.5);
 const frozen=JSON.parse(old.serialize());
 const b=OrderBook.restore(data,old.serialize(),()=>{throw Error('migration rerolled');});
 assert.deepEqual(b.active,frozen.active);assert.deepEqual(b.riderPose,old.riderPose);assert.equal(b.riderNode,old.riderNode);
 assert.ok(b.list().some(p=>p.offer.id===offer.id));
 const again=OrderBook.restore(data,b.serialize(),()=>{throw Error('migration rerolled');});assert.deepEqual(again.active,frozen.active);
});

test('operating places leave room for pins at every town edge without moving historic addresses',()=>{
 const data=places.prepareCity(raw),baseline=require('./fixtures/locality-v3-baseline.json');
 assert.ok(data.dispatchBounds,'operating bounds are separate from the camera boundary');
 const b=data.dispatchBounds,p=data.playBounds,nodes=new Map(data.nodes.map(n=>[n.id,n]));
 assert.ok(b.minX>=p.minX+150&&b.maxX<=p.maxX-150&&b.minY>=p.minY+150&&b.maxY<=p.maxY-150);
 assert.deepEqual(data.pois.slice(0,baseline.catalog.pois.length),baseline.catalog.pois);
 assert.ok(data.legacyMapIds.includes(countyMapId({...raw,...baseline.catalog})));
 const operating=data.pois.filter(p=>{const n=nodes.get(p.node);return inside(b,[n.x,n.y]);});
 assert.ok(operating.filter(p=>p.kind==='restaurant').length>=40);
 assert.ok(operating.filter(p=>p.kind!=='restaurant').length>=120);
});

function assertLocalLobby(book,data){
 const rows=book.list(),nodes=new Map(data.nodes.map(n=>[n.id,n]));
 assert.equal(rows.length,10);assert.equal(new Set(rows.map(p=>p.offer.to)).size,10);
 assert.ok(rows.every(p=>p.timing.displaySeconds<=1800),'all ordinary trips finish within 30 minutes');
 assert.ok(rows.filter(p=>p.timing.displaySeconds<=1200).length>=8,'at least eight trips are within 20 minutes');
 for(const p of rows)for(const index of [p.offer.from,p.offer.to]){
  const n=nodes.get(data.pois[index].node);assert.ok(inside(data.dispatchBounds,[n.x,n.y]),'ordinary endpoints stay in operating bounds');
 }
}

test('actual city trips stay local after refreshing, moving and upgrading the vehicle',()=>{
 const data=places.prepareCity(raw),book=new OrderBook(data,random());
 for(let batch=0;batch<3;batch++){
  assertLocalLobby(book,data);
  assert.ok(book.list().filter(p=>p.timing.displaySeconds>=600&&p.timing.displaySeconds<=1200).length>=6,'10–20 minute trips form the majority');
  if(batch<2)book.refreshFree();
 }
 for(let i=0;i<12;i++){
  assertLocalLobby(book,data);const offer=book.list()[i%10].offer;
  book.accept(offer.id);for(const r of book.active.routes)assert.ok(book.timingForRoute(r).displaySeconds<=1800);
  book.depart();book.advance(99);if(book.mode==='arrived')book.settle(true);book.finish();
 }
 book.upgradeVehicle();assertLocalLobby(book,data);
});

test('the previous v3 lobby migrates without losing progress or redrawing accepted activity',()=>{
 const data=places.prepareCity(raw),fixture=require('./fixtures/locality-v3-baseline.json');
 for(const [mode,saved] of Object.entries(fixture.states)){
  const book=OrderBook.restore(data,JSON.stringify(saved),()=>{throw Error('migration consumed business RNG');});
  assert.deepEqual(book.player,saved.player);assert.equal(book.riderNode,saved.currentNode);
  assert.deepEqual(JSON.parse(book.serialize()).daily,saved.daily);
  assert.deepEqual(book.active,saved.active,mode+' activity changed');
  if(mode==='idle'||mode==='done')assertLocalLobby(book,data);
  const stable=book.serialize();assert.equal(OrderBook.restore(data,stable,()=>{throw Error('reload consumed RNG');}).serialize(),stable);
 }
});
