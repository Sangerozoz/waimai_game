const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
function trip(damaged=true){
 const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0}));
 const data={title:'事件测试',width:16000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
 let roll=.99,calls=0;const b=new OrderBook(data,()=>{calls++;return roll;});b.accept(b.list()[0].offer.id);roll=damaged?0:.99;b.depart();
 return {b,data,calls:()=>calls};
}
test('predrawn food damage notifies only halfway through delivery, never while collecting and never rerolls',()=>{
 const {b,calls}=trip(),startCalls=calls(),damage=b.active.damage;assert.equal(damage,'minor');
 assert.equal(b.takeDamageNotice(),false);b.advance(2+b.progress.animationSeconds/2-.001);assert.equal(b.takeDamageNotice(),false);
 b.advance(.002);assert.equal(b.takeDamageNotice(),true);assert.equal(b.takeDamageNotice(),false);
 assert.equal(calls(),startCalls);assert.equal(b.active.damage,damage);
});
test('damage notice stays consumed after reload and does not alter the existing receipt or award',()=>{
 const {b,data}=trip();b.advance(2+b.progress.animationSeconds/2+.01);
 const withoutNotice=OrderBook.restore(data,b.serialize(),()=>.99);assert.equal(b.takeDamageNotice(),true);
 const restored=OrderBook.restore(data,b.serialize(),()=>.99);assert.equal(restored.takeDamageNotice(),false);
 withoutNotice.advance(99);restored.advance(99);assert.deepEqual(restored.active.receipt,withoutNotice.active.receipt);
 const before=restored.player.cashCents;restored.settle();assert.equal(restored.player.cashCents,before);
});
test('healthy orders and an already completed frame never show damage events',()=>{
 const {b}=trip(false);b.advance(2+b.progress.animationSeconds*.6);assert.equal(b.takeDamageNotice(),false);
 const broken=trip().b;broken.advance(99);assert.equal(broken.takeDamageNotice(),false);
});
test('old missing notice fields load as unseen while malformed notice state is rejected',()=>{
 const {b,data}=trip();b.advance(2+b.progress.animationSeconds*.6);
 const old=JSON.parse(b.serialize());delete old.active.damageNoticeShown;
 const restored=OrderBook.restore(data,JSON.stringify(old),()=>.99);assert.equal(restored.takeDamageNotice(),true);
 for(const value of ['true',1,{},null]){const invalid=JSON.parse(b.serialize());invalid.active.damageNoticeShown=value;assert.throws(()=>OrderBook.restore(data,JSON.stringify(invalid)),/存档/);}
});
test('legacy routes with different segment speeds trigger at distance midpoint rather than time midpoint',()=>{
 const data=trip().data;
 data.nodes.forEach((node,i)=>{node.x=i===0?0:i===1?200:2000+(i-2)*200;});
 data.roads[0].nodes=data.nodes.slice(1).map(n=>n.id);data.roads[0].speed=20;
 data.roads.push({id:'slow',nodes:['0','1'],direction:0,speed:1,roughness:.1,kind:'secondary',width:8,bridge:false});
 const initial=new OrderBook(data,()=>.99),raw=JSON.parse(initial.serialize());raw.offers[0].to=2;
 const b=OrderBook.restore(data,JSON.stringify(raw),()=>0);b.accept(b.list()[0].offer.id);b.depart();
 const saved=JSON.parse(b.serialize()),active=saved.active;
 active.ruleVersion=1;delete active.pickupWaitElapsed;
 const {legacyDeliveryTiming}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'DeliveryClock.js'));
 const timing=legacyDeliveryTiming(active.routes[active.selected].seconds,1);
 active.elapsed=timing.animationSeconds/2;active.deadlineSeconds=timing.displaySeconds+300;
 const legacy=OrderBook.restore(data,JSON.stringify(saved),()=>.99);
 assert.equal(legacy.riderPose.point[0],145);assert.equal(legacy.takeDamageNotice(),false,'145m is far short of the 1000m damage location');
 legacy.advance(timing.animationSeconds*(241/290-.5));assert.ok(legacy.riderPose.point[0]>=1000);assert.equal(legacy.takeDamageNotice(),true);
});
