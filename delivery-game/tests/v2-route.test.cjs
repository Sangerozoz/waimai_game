// Written only. Run after explicit stage-completion authorization with run-v2.cjs.
const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const base=path.dirname(process.env.MAP_ROUTER_MODULE);
const {V2GameSession}=require(path.join(base,'V2GameSession.js'));
const city={title:'directed fixture',width:100,height:100,nodes:[{id:'a',x:0,y:0},{id:'b',x:10,y:0},{id:'c',x:20,y:0},{id:'outside',x:100,y:100}],roads:[{id:'main',nodes:['a','b','c'],direction:0,kind:'primary',width:3,speed:1,roughness:0},{id:'outside',nodes:['a','outside','c'],direction:0,kind:'primary',width:3,speed:100,roughness:0}],pois:[{node:'a',name:'A',kind:'shop'},{node:'b',name:'B',kind:'shop'},{node:'c',name:'C',kind:'home'}],buildings:[],areas:[],waterways:[],labels:[],dispatchBounds:{minX:0,minY:0,maxX:20,maxY:20}};
const one=(s)=>{const o=s.normalCandidates(1)[0];s.acceptBatch([o]);s.beginTrip();return o;};
test('actual directed in-bounds legs, route alternatives merge and manual pickup blocks elapsed-time rewards',()=>{
 const s=new V2GameSession(city),o=s.normalCandidates(1)[0];s.acceptBatch([o]);
 assert.equal(s.routeChoices().length,1);assert.equal(s.routeChoices()[0].aliases.length,3);s.beginTrip();
 assert.ok(s.routeSnapshot.legs.every(l=>l.nodes.every(id=>id!=='outside')));
 assert.throws(()=>s.completeDelivery(o.id,'arrival:1:1:'+o.id));
 s.tick(1,100,true,false);assert.equal(s.routeSnapshot.phase,'pickup');assert.equal(s.snapshot().orders[0].status,'pending');
 s.pickup();s.tick(2,200,true,false);assert.equal(s.routeSnapshot.phase,'ready');assert.equal(s.snapshot().orders[0].status,'pending');
 const stopped=s.routeSnapshot.position,clock=s.tripState.gameSeconds;s.tick(3,250,true,false);assert.deepEqual(s.routeSnapshot.position,stopped);assert.equal(s.tripState.gameSeconds,clock);
 s.continueTrip();s.tick(4,300,true,false);assert.equal(s.snapshot().orders[0].status,'completed');
 const money=s.dispatch.economyState.cashCents;s.completeDelivery(o.id,s.routeSnapshot.arrivals[0].token);assert.equal(s.dispatch.economyState.cashCents,money);
});
test('integer slot offers and same-merchant multi-order pickup merge exactly once',()=>{
 const {richGame}=require('./product-regression-1106/helpers.cjs');const s=richGame(city),vehicle=s.dispatch.command({type:'buyVehicle',modelId:3});s.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:vehicle});
 const offers=s.normalCandidates(5);assert.ok(offers.every(o=>!('weightKg' in o)&&o.load.version==='slots-v1'&&[1,2].includes(o.load.occupiedSlots)));
 const first=offers[0],selected=offers.filter(o=>o.pickupNode===first.pickupNode&&o.pickupName===first.pickupName).slice(0,2);assert.equal(selected.length,2);s.acceptBatch(selected);s.beginTrip('smooth');
 assert.deepEqual(s.routeSnapshot.stops.map(t=>t.kind),['pickup','dropoff','dropoff']);assert.equal(s.routeSnapshot.stops[0].orderIds.length,2);
 s.tick(1,100,true,false);s.pickup();const stamina=s.tripState.stamina;s.tick(2,102,true,false);assert.equal(s.routeSnapshot.phase,'ready');assert.equal(s.tripState.stamina,stamina-1);s.continueTrip();s.tick(3,200,true,false);
 assert.equal(s.dispatch.economyState.heroCompletedOrders,2);
});
test('road/service progress and dispatch use the same checkpoint; restore has no offline hero travel',()=>{
 const s=new V2GameSession(city);one(s);s.tick(1,5,true,false);const before=s.routeSnapshot.position;
 const resumed=V2GameSession.restore(city,s.serialize());resumed.tick(2,1000,true,false);assert.deepEqual(resumed.routeSnapshot.position,before);
 assert.equal(resumed.routeSnapshot.legSeconds,s.routeSnapshot.legSeconds);assert.equal(resumed.dispatch.economyState.cashCents,s.dispatch.economyState.cashCents);
 resumed.tick(3,1005,true,false);assert.equal(resumed.routeSnapshot.phase,'pickup');resumed.pickup();resumed.tick(4,1006,true,false);
 const service=V2GameSession.restore(city,resumed.serialize());assert.equal(service.routeSnapshot.serviceSeconds,1);
});
test('cancel midway does not teleport and next trip starts at exact edge progress',()=>{
 const s=new V2GameSession(city),o=one(s);s.tick(1,.125,true,false);const at=s.routeSnapshot.position;s.cancelDelivery(o.id);assert.deepEqual(s.routeSnapshot.position,at);
 one(s);assert.deepEqual(s.routeSnapshot.position,at);const r=V2GameSession.restore(city,s.serialize());assert.deepEqual(r.routeSnapshot.position,at);
});
test('restore rejects forged token, shortened leg, premature service and future/map changes',()=>{
 const s=new V2GameSession(city);one(s);const raw=JSON.parse(s.serialize());
 const forged=structuredClone(raw);forged.route.arrivals=[{id:raw.route.orders[0].id,token:'fake'}];assert.throws(()=>V2GameSession.restore(city,JSON.stringify(forged)));
 const leg=structuredClone(raw);leg.route.legs[0].seconds=0;assert.throws(()=>V2GameSession.restore(city,JSON.stringify(leg)));
 const service=structuredClone(raw);service.route.phase='service';assert.throws(()=>V2GameSession.restore(city,JSON.stringify(service)));
 const future=structuredClone(raw);future.version=99;assert.throws(()=>V2GameSession.restore(city,JSON.stringify(future)));
 assert.throws(()=>V2GameSession.restore({...city,title:'same geometry',nodes:[...city.nodes,{id:'new',x:1,y:1}]},s.serialize()));
});
test('unreachable plan failure leaves accepted dispatch unchanged',()=>{
 const s=new V2GameSession(city),o=s.normalCandidates(1)[0],before=s.serialize();assert.throws(()=>s.acceptBatch([{...o,dropoffNode:'outside'}]));assert.equal(s.serialize(),before);
});
test('automatic entitlement accepts ordinary capacity batch and loops next frame, never special',()=>{
 const s=new V2GameSession(city),ticket=s.dispatch.requestAd('auto',null,0,30);s.dispatch.resolveAd(ticket,'completed',1);
 s.tick(1,101,true,false);assert.ok(s.dispatch.economyState.heroCompletedOrders>0);assert.ok(['travelling','pickup','service','ready','finished'].includes(s.routeSnapshot.phase));
 const completed=s.dispatch.economyState.heroCompletedOrders;s.tick(2,201,true,false);assert.ok(s.dispatch.economyState.heroCompletedOrders>completed);assert.ok(s.snapshot().orders.every(o=>o.kind==='ordinary'));
 const raw=s.serialize(),restored=V2GameSession.restore(city,raw);const budget=restored.snapshot().rewards.autoRemainingSeconds;restored.tick(3,10000,true,false);assert.equal(restored.snapshot().rewards.autoRemainingSeconds,budget);
});
