const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
require('./legacy-order-fixture.cjs')(OrderBook);
function city(){
 const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0}));
 return {title:'县城测试',width:16000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
}
function complete(book){book.accept(book.list()[0].offer.id);book.depart();book.advance(99);if(book.mode==='arrived')book.settle(true);return book.settle();}
function tamper(book,edit){const saved=JSON.parse(book.serialize());edit(saved);return JSON.stringify(saved);}

test('new county wallet and the first actual routed receipt survive reload without a second award',()=>{
 const data=city(),book=new OrderBook(data,()=>.99),receipt=complete(book);
 assert.equal(receipt.incomeCents,2180);assert.equal(book.player.cashCents,12180);assert.equal(book.player.experience,10);
 const restored=OrderBook.restore(data,book.serialize(),()=>{throw new Error('loading must not consume RNG');});
 assert.equal(restored.mode,'done');assert.deepEqual(restored.settle(),receipt);assert.equal(restored.player.cashCents,12180);
 restored.finish();assert.equal(restored.mode,'idle');assert.equal(restored.completed,1);assert.equal(restored.list().length,10);
});
test('in-transit reload preserves route, damage and both clocks and resumes automatically',()=>{
 const data=city();let roll=.99;const book=new OrderBook(data,()=>roll);
 book.accept(book.list()[0].offer.id);roll=0;book.depart();book.advance(.5);
 const savedPose=book.riderPose.point,damage=book.active.damage;
 let allow=false;const restored=OrderBook.restore(data,book.serialize(),()=>{assert.ok(allow,'restore must not reroll');return .99;});
 assert.equal(restored.mode,'running');assert.deepEqual(restored.riderPose.point,savedPose);assert.equal(restored.active.damage,damage);
 allow=true;restored.advance(99);
 assert.equal(restored.settle().damage,'minor');assert.equal(restored.player.cashCents,11951);
});
test('legacy doorstep arrival automatically follows the request and retains its single award',()=>{
 const data=city(),book=new OrderBook(data,()=>.1);complete(book);book.finish();book.accept(book.list()[0].offer.id);
 const routes=OrderBook.restore(data,book.serialize(),()=>.99),before=routes.player.cashCents;routes.depart();routes.advance(99);
 assert.equal(routes.mode,'done');assert.equal(routes.active.receipt.outcome.doorAnswer,true);const receipt=routes.active.receipt;
 const restored=OrderBook.restore(data,routes.serialize(),()=>.99);assert.equal(restored.player.cashCents,before+receipt.incomeCents);assert.deepEqual(restored.settle(false),receipt);
});
test('real earnings buy exactly one D+ and preserve its speed, income and capacity after reload',()=>{
 const data=city(),book=new OrderBook(data,()=>.99);
 assert.throws(()=>book.upgradeVehicle(),/余额/);assert.equal(book.player.cashCents,10000);
 for(let i=0;i<10;i++){complete(book);book.finish();}
 const balance=book.player.cashCents,before=book.timing(1800).displaySeconds;
 book.upgradeVehicle();assert.equal(book.player.cashCents,balance-20000);assert.equal(book.player.vehicleTier,2);
 assert.ok(book.timing(1800).displaySeconds<before);const after=book.player.cashCents;assert.throws(()=>book.upgradeVehicle());assert.equal(book.player.cashCents,after);
 const restored=OrderBook.restore(data,book.serialize());assert.equal(restored.player.vehicleTier,2);
 restored.accept(restored.list()[0].offer.id);assert.throws(()=>restored.upgradeVehicle());
});
test('daily two-free-refresh quota survives reload, resets next day, and never blocks ordinary deliveries',()=>{
 const data=city();let day='2026-10-28';const book=new OrderBook(data,()=>.99,()=>day);
 const first=book.list().map(p=>p.offer.id);book.refreshFree();book.refreshFree();assert.equal(book.refreshesLeft,0);
 assert.throws(()=>book.refreshFree(),/免费刷新/);assert.notDeepEqual(book.list().map(p=>p.offer.id),first);
 const restored=OrderBook.restore(data,book.serialize(),()=>.99,()=>day);assert.equal(restored.refreshesLeft,0);
 complete(restored);restored.finish();day='2026-10-29';assert.equal(restored.refreshesLeft,2);
 restored.refreshFree();assert.equal(restored.refreshesLeft,1);
 restored.accept(restored.list()[0].offer.id);assert.throws(()=>restored.refreshFree());
});
test('corrupt or changed-graph snapshots are rejected rather than damaging a valid running session',()=>{
 const data=city(),book=new OrderBook(data,()=>.99);book.accept(book.list()[0].offer.id);book.depart();book.advance(.2);
 for(const edit of [s=>s.player.cashCents=-1,s=>s.active.damage=null,s=>s.active.elapsed=90,s=>s.active.routes[0].points[0][0]+=1,s=>s.offers[1].id=s.offers[0].id,s=>s.sequence=1]){
  assert.throws(()=>OrderBook.restore(data,tamper(book,edit)),/存档/);
 }
 const changed=city();changed.nodes[1].x+=1;assert.throws(()=>OrderBook.restore(changed,book.serialize()),/路网/);
 assert.equal(book.player.cashCents,10000);
});


test('a valid old thirty-order save migrates to ten nearby orders without losing progress or refresh quota',()=>{
 const data=city(),book=new OrderBook(data,()=>.99);complete(book);book.finish();book.refreshFree();
 const saved=JSON.parse(book.serialize()),before=book.player,node=book.riderNode;
 saved.version=1;saved.player.level=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'../domain/GameConfig.js')).getExperienceLevel(saved.player.experience);
 while(saved.offers.length<30)saved.offers.push({...saved.offers[0],id:'CC-'+(1000+saved.offers.length),from:0,to:79});
 saved.sequence=2000;
 const restored=OrderBook.restore(data,JSON.stringify(saved),()=>.99);
 assert.deepEqual(restored.player,before);assert.equal(restored.riderNode,node);assert.equal(restored.refreshesLeft,1);
 assert.equal(restored.list().length,10);for(const p of restored.list())assert.ok(p.pickupMetres+p.deliveryMetres<=10000);
 assert.equal(JSON.parse(restored.serialize()).version,3);
 const again=OrderBook.restore(data,restored.serialize(),()=>{throw new Error('current saves do not reroll');});
 assert.deepEqual(again.list().map(p=>p.offer.id),restored.list().map(p=>p.offer.id));
});


test('cancelling a migrated legacy long order retains its candidate without refreshing',()=>{
 const {RoadRouter}=require(process.env.MAP_ROUTER_MODULE);
 const data=city(),book=new OrderBook(data,()=>.99);book.accept(book.list()[0].offer.id);
 const saved=JSON.parse(book.serialize()),offer={...saved.active.offer,from:0,to:79};
 const route=new RoadRouter(data).find('0','79','fast');route.pickupIndex=0;route.risk=.08;
 saved.version=1;saved.player.level=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'../domain/GameConfig.js')).getExperienceLevel(saved.player.experience);saved.offers[0]=offer;saved.active.offer=offer;saved.active.routes=[route];
 delete saved.active.pickupWaitElapsed; // v1 activity predates the optional pickup stop clock.
 saved.active.deadlineSeconds=Math.ceil((480+route.seconds*1.6)/60)*60+300;
 while(saved.offers.length<30)saved.offers.push({...saved.offers[1],id:'CC-'+(1000+saved.offers.length)});
 saved.sequence=2000;
 const restored=OrderBook.restore(data,JSON.stringify(saved),()=>.99),before=restored.player;
 assert.ok(restored.active.routes[0].metres>10000);
 restored.cancel();assert.equal(restored.mode,'idle');assert.deepEqual(restored.player,before);
 assert.equal(restored.refreshesLeft,2);assert.equal(restored.list().length,10);
 assert.ok(restored.list().some(p=>p.offer.id===offer.id&&!p.available));
 for(const preview of restored.list().filter(p=>p.available))assert.ok(preview.pickupMetres+preview.deliveryMetres<=10000);
 restored.accept(restored.list().find(p=>p.available).offer.id);assert.ok(restored.active.routes.every(r=>r.metres<=10000));
});

test('exactly 200 yuan upgrades D+ once while 199.99 is insufficient',()=>{
 const data=city(),book=new OrderBook(data,()=>.99);
 for(const cashCents of [19999,20000]){
  const saved=JSON.parse(book.serialize());saved.player.cashCents=cashCents;const b=OrderBook.restore(data,JSON.stringify(saved),()=>{throw Error('no random at restore');});
  if(cashCents===19999){assert.throws(()=>b.upgradeVehicle(),/余额/);assert.equal(b.player.cashCents,19999);}
  else{b.upgradeVehicle();assert.equal(b.player.cashCents,0);assert.equal(b.player.vehicleTier,2);assert.throws(()=>b.upgradeVehicle());assert.equal(b.player.cashCents,0);}
 }
});
test('genuine ZIP-baseline v2 states migrate without rerolls, changed receipts or changed old poses',()=>{
 const fixture=require('./fixtures/county-v2-baseline.json');
 for(const [name,{snapshot,pose,progress}] of Object.entries(fixture.states)){
  let allow=false;const rng=()=>{assert.ok(allow,'migration must preserve random choices');return .99;};
  const b=OrderBook.restore(fixture.data,JSON.stringify(snapshot),rng,()=> '2026-10-28');
  for(const key of ['cashCents','rating','experience','vehicleTier'])assert.equal(b.player[key],snapshot.player[key],name);
  const {countyExperienceLevel}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'CountyConfig.js'));assert.equal(b.player.level,countyExperienceLevel(snapshot.player.experience),name);
  assert.equal(b.refreshesLeft,2-snapshot.daily.used,name);assert.equal(b.riderNode,snapshot.currentNode,name);assert.deepEqual(b.riderPose,pose,name);
  assert.deepEqual(b.list().map(p=>p.offer.id),snapshot.offers.map(o=>o.id),name);
  if(snapshot.active){for(const key of ['damage','deadlineSeconds','receipt'])assert.deepEqual(b.active[key],snapshot.active[key],name);for(const key of ['displaySeconds','animationSeconds'])assert.equal(b.progress[key],progress[key],name);}
  if(snapshot.active?.mode==='running'||snapshot.active?.mode==='paused')assert.equal(b.mode,'running',name);
  const serialized=b.serialize();assert.equal(JSON.parse(serialized).version,3);
  const again=OrderBook.restore(fixture.data,serialized,rng,()=> '2026-10-28');assert.equal(again.serialize(),serialized,name);allow=true;
  if(snapshot.active?.mode==='done'){assert.deepEqual(again.settle(),snapshot.active.receipt);assert.equal(again.player.cashCents,snapshot.player.cashCents);}
  if(snapshot.active?.mode==='running'||snapshot.active?.mode==='paused'){again.advance(99);if(again.mode==='arrived')again.settle(true);assert.equal(again.mode,'done');}
 }
});
test('new trips move and switch pickup by metres across unequal road speeds',()=>{
 const data=city();data.roads=[{...data.roads[0],id:'slow',nodes:['0','1','2'],speed:1},{...data.roads[0],id:'fast',nodes:data.nodes.slice(2).map(n=>n.id),speed:20}];
 const b=new OrderBook(data,()=>.99);b.accept(b.list()[0].offer.id);b.depart();const r=b.active.routes[0];b.advance(2);b.advance(b.progress.animationSeconds/2);assert.ok(Math.abs(b.riderPose.point[0]-r.metres/2)<1e-6);
 b.advance(99);if(b.mode==='arrived')b.settle(true);b.finish();b.accept(b.list()[0].offer.id);b.depart();const next=b.active.routes[0],pickup=next.segments.slice(0,next.pickupIndex).reduce((n,s)=>n+s.metres,0);
 assert.ok(pickup>0);b.advance(b.progress.animationSeconds*pickup/next.metres-.000001);assert.equal(b.tripStage,'pickup');b.advance(.000002);assert.equal(b.tripStage,'collecting');b.advance(2);assert.equal(b.tripStage,'delivery');
});

test('legacy level-one departure at fifty XP finishes at frozen income then continues at recomputed level',()=>{
 const fixture=require('./fixtures/county-v2-baseline.json'),saved=fixture.states.fiftyRunning.snapshot;
 const b=OrderBook.restore(fixture.data,JSON.stringify(saved),()=>.99);
 assert.equal(saved.player.level,1);assert.equal(b.player.level,2);assert.equal(b.active.playerBefore.level,1);
 b.advance(99);if(b.mode==='arrived')b.settle(true);assert.deepEqual(b.settle(),fixture.states.fiftyDone.snapshot.active.receipt);
 assert.equal(b.player.level,2);const again=OrderBook.restore(fixture.data,b.serialize(),()=>{throw Error('no reroll');});assert.equal(again.player.level,2);
 again.finish();again.accept(again.list()[0].offer.id);assert.equal(again.active.playerBefore.level,2);assert.equal(again.active.ruleVersion,2);
});

test('v3 rejects unknown rules, wrong current levels, tampered receipts and timing without consuming random',()=>{
 const fixture=require('./fixtures/county-v2-baseline.json');
 const b=OrderBook.restore(fixture.data,JSON.stringify(fixture.states.fiftyDone.snapshot),()=>{throw Error('no reroll');});
 for(const edit of [s=>s.player.level=1,s=>s.active.ruleVersion=7,s=>delete s.active.ruleVersion,s=>s.active.receipt.incomeCents++,s=>s.active.elapsed--,s=>s.active.deadlineSeconds++])assert.throws(()=>OrderBook.restore(fixture.data,tamper(b,edit),()=>{throw Error('no reroll');}),/存档/);
});
