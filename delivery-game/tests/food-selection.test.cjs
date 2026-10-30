const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const dir=path.dirname(process.env.MAP_ROUTER_MODULE);
const foods=require(path.join(dir,'FoodCatalog.js'));
const {OrderBook}=require(path.join(dir,'OrderBook.js'));
require('./legacy-order-fixture.cjs')(OrderBook);
function random(seed){let n=seed;return()=>((n=(Math.imul(n,1664525)+1013904223)>>>0)/4294967296);}
function city(local){
 const data={title:'抽样测试',width:1000,height:1000,nodes:[{id:'a',x:0,y:0},{id:'b',x:100,y:0}],roads:[{id:'r',nodes:['a','b'],speed:6,direction:0,roughness:.1,kind:'residential',width:5,bridge:false}],pois:[{name:'唯一店',node:'a',kind:'restaurant'},{name:'唯一家',node:'b',kind:'home'}],buildings:[],areas:[],waterways:[],labels:[]};
 if(local){data.playBounds={minX:-500,maxX:500,minY:-500,maxY:500};data.dispatchBounds={...data.playBounds};}
 return data;
}
// Catches either real generator retaining the old 5/16 rotation. Fake dates only reset this test's quota.
for(const local of [false,true])test(`new ${local?'local':'fallback'} offers keep fragile food near ten percent`,()=>{
 let day=0;const book=new OrderBook(city(local),random(817),()=>`test-day-${day}`),counts={fragile:0,normal:0,durable:0},ids=new Set(),allFoods=new Set();
 for(let batch=0;batch<210;batch++){
  for(const {offer} of book.list()){
   assert.ok(!ids.has(offer.id));ids.add(offer.id);
   if(offer.id==='CC-1'){assert.equal(offer.food,'鸡腿饭 · 1份');continue;}
   counts[offer.fragility]++;const food=foods.foodForOffer(offer.food);allFoods.add(food.id);
   assert.equal(food.fragility,offer.fragility);assert.equal(offer.weightKg,food.unitWeightKg*Number(offer.food.match(/(\d+)份/)[1]));assert.ok(offer.weightKg<=5);
  }
  if(batch<209){day++;book.refreshFree();}
 }
 const total=Object.values(counts).reduce((a,b)=>a+b,0);console.log('food-integration',JSON.stringify({local,total,counts}));
 assert.equal(total,2099);assert.ok(Math.abs(counts.fragile/total-.1)<=.03,`fragile ${counts.fragile}/${total} should be 10% ±3pp`);assert.equal(allFoods.size,16);
});

test('class boundaries select real foods without changing image or fragility identity',()=>{
 for(const [roll,want] of [[0,'fragile'],[.1-1e-12,'fragile'],[.1,'normal'],[56/110-1e-12,'normal'],[56/110,'durable'],[1-Number.EPSILON,'durable']]){
  for(const itemRoll of [0,1-Number.EPSILON]){
   const food=foods.selectFoodForOffer(roll,itemRoll,[]);
   assert.equal(food.fragility,want);assert.ok(foods.FOOD_CATALOG.includes(food));assert.equal(foods.foodForOffer(food.name),food);
  }
 }
});

test('diversity prefers unseen foods within the chosen class and safely reuses exhausted pools',()=>{
 for(const [roll,category,size] of [[0,'fragile',5],[.1,'normal',5],[.9,'durable',6]]){
  const shown=[];
  for(let i=0;i<size;i++){const food=foods.selectFoodForOffer(roll,.5,shown);assert.equal(food.fragility,category);assert.ok(!shown.includes(food.id));shown.push(food.id);}
  const repeated=foods.selectFoodForOffer(roll,.5,shown);assert.equal(repeated.fragility,category);assert.ok(shown.includes(repeated.id));
 }
});

test('invalid samples, malformed weights and positive classes without foods fail explicitly',()=>{
 for(const invalid of [NaN,Infinity,-.001,1,2]){
  assert.throws(()=>foods.selectFoodForOffer(invalid,.5,[]),/sample/i);assert.throws(()=>foods.selectFoodForOffer(.5,invalid,[]),/sample/i);
 }
 // Load the real compiled selector with a bad configuration; no test-only production API.
 function configured(weights){
  const exports={};vm.runInNewContext(fs.readFileSync(path.join(dir,'FoodCatalog.js'),'utf8'),{exports,require:name=>name==='./CountyConfig'?{COUNTY_FOOD_MIX:{id:'invalid',weights}}:require(path.resolve(dir,name))});return exports;
 }
 for(const weights of [{fragile:NaN,normal:45,durable:54},{fragile:-1,normal:45,durable:54},{fragile:0,normal:0,durable:0}])assert.throws(()=>configured(weights).selectFoodForOffer(.5,.5,[]),/weight/i);
 const missing=configured({fragile:11,normal:45,durable:54});missing.FOOD_CATALOG.splice(0,missing.FOOD_CATALOG.length,...foods.FOOD_CATALOG.filter(f=>f.fragility!=='fragile'));
 assert.throws(()=>missing.selectFoodForOffer(.5,.5,[]),/empty/i);
});

test('four seeded long runs preserve class probabilities even with per-lobby diversity',()=>{
 for(const seed of [1,817,20261029,0xffffffff]){
  const rng=random(seed),counts={fragile:0,normal:0,durable:0},allFoods=new Set();let shown=[];
  for(let i=0;i<10000;i++){if(i%10===0)shown=[];const f=foods.selectFoodForOffer(rng(),rng(),shown);counts[f.fragility]++;shown.push(f.id);allFoods.add(f.id);}
  console.log('food-selector',JSON.stringify({seed,total:10000,counts}));
  assert.ok(Math.abs(counts.fragile/10000-.1)<=.015);assert.ok(Math.abs(counts.normal/10000-45/110)<=.025);assert.ok(Math.abs(counts.durable/10000-54/110)<=.025);assert.equal(allFoods.size,16);
 }
});

test('pre-patch idle, routes, running, collecting, arrived and done saves retain all drawn state without RNG',()=>{
 const fixture=require('./fixtures/m1-before-food-mix.json');
 for(const [name,state] of Object.entries(fixture.states)){
  const rng=()=>{throw Error(`must not reroll ${name}`);};
  const book=OrderBook.restore(fixture.data,JSON.stringify(state.snapshot),rng,()=> '2026-10-29');
  assert.deepEqual(JSON.parse(book.serialize()),state.snapshot,name);assert.deepEqual(book.riderPose,state.pose,name);assert.deepEqual(book.progress,state.progress,name);assert.equal(book.tripStage,state.stage,name);
  const before=book.serialize();book.list();if(book.mode==='idle'){book.accept(book.list()[0].offer.id);book.cancel();}if(book.mode==='done')book.settle(false);
  assert.equal(book.serialize(),before,name);assert.equal(OrderBook.restore(fixture.data,before,rng,()=> '2026-10-29').serialize(),before,name);
 }
});
