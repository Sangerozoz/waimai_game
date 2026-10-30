const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {animationSecondsFor,deliveryTiming,deliveryProgress,advancePickupClock}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'DeliveryClock.js'));
test('30 minutes animates in ten seconds and 45 minutes or longer caps at fifteen',()=>{
 assert.equal(animationSecondsFor(1800),10);assert.equal(animationSecondsFor(2700),15);assert.equal(animationSecondsFor(3600),15);assert.throws(()=>animationSecondsFor(-1),RangeError);
});
test('road metres and average kph determine exact display seconds without overhead or rounding',()=>{
 assert.equal(deliveryTiming(6000,12).displaySeconds,1800);assert.ok(Math.abs(deliveryTiming(6001,12).displaySeconds-1800.3)<1e-9);
 assert.equal(deliveryTiming(9000,12).animationSeconds,15);assert.equal(deliveryTiming(12000,12).animationSeconds,15);assert.ok(deliveryTiming(6000,13.2).displaySeconds<1800);
 for(const pair of [[-1,12],[1,0],[Infinity,12],[1,NaN]])assert.throws(()=>deliveryTiming(...pair),RangeError);
});
test('capped animation keeps exact distance progress and remaining delivery clock',()=>{
 const half=deliveryProgress(12000,7.5,12);assert.equal(half.progress,.5);assert.equal(half.routeElapsedMetres,6000);assert.equal(half.remainingSeconds,1800);
 const done=deliveryProgress(12000,99,12);assert.equal(done.progress,1);assert.equal(done.routeElapsedMetres,12000);assert.equal(done.remainingSeconds,0);assert.equal(deliveryProgress(0,0,12).progress,1);
});
test('pickup clock advances the road clock normally before reaching the merchant',()=>{
 assert.deepEqual(advancePickupClock(1,0,1,4,10),{elapsed:2,pickupWaitElapsed:0});
});
test('reaching the merchant spends the rest of the frame on pickup waiting',()=>{
 assert.deepEqual(advancePickupClock(3,0,2,4,10),{elapsed:4,pickupWaitElapsed:1});
});
test('pickup consumes two additional seconds without advancing the road clock',()=>{
 const stopped=advancePickupClock(4,0,2,4,10);
 assert.deepEqual(stopped,{elapsed:4,pickupWaitElapsed:2});
 assert.deepEqual(advancePickupClock(stopped.elapsed,stopped.pickupWaitElapsed,.5,4,10),{elapsed:4.5,pickupWaitElapsed:2});
});
test('a first order starting at the merchant waits before beginning its road animation',()=>{
 const first=advancePickupClock(0,0,1,0,10);
 assert.deepEqual(first,{elapsed:0,pickupWaitElapsed:1});
 const second=advancePickupClock(first.elapsed,first.pickupWaitElapsed,1,0,10);
 assert.deepEqual(second,{elapsed:0,pickupWaitElapsed:2});
 assert.deepEqual(advancePickupClock(second.elapsed,second.pickupWaitElapsed,1,0,10),{elapsed:1,pickupWaitElapsed:2});
});
test('one large frame crosses arrival, pickup and remaining road animation without overshooting',()=>{
 assert.deepEqual(advancePickupClock(3,0,4,4,10),{elapsed:5,pickupWaitElapsed:2});
 assert.deepEqual(advancePickupClock(3,0,20,4,10),{elapsed:10,pickupWaitElapsed:2});
});
test('restored pickup waiting spends only the remaining eight tenths of a second',()=>{
 assert.deepEqual(advancePickupClock(4,1.2,.8,4,10),{elapsed:4,pickupWaitElapsed:2});
 assert.deepEqual(advancePickupClock(4,1.2,1.3,4,10),{elapsed:4.5,pickupWaitElapsed:2});
});
test('zero, negative and non-finite frame times preserve both clocks',()=>{
 for(const delta of [0,-1,NaN,Infinity,-Infinity])assert.deepEqual(advancePickupClock(4,1.2,delta,4,10),{elapsed:4,pickupWaitElapsed:1.2});
});

test('manual handoff stops at every player boundary even with a large frame',()=>{
 const path=require('node:path'),{startPickup,advanceHandoff,startDelivery,beginTrip}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'ManualHandoff.js'));
 let s={version:1,phase:'planning',elapsed:0,serviceElapsed:0};s=beginTrip(s,3);assert.equal(s.phase,'toPickup');s=advanceHandoff(s,100,3,10);assert.equal(s.phase,'awaitPickup');assert.equal(s.elapsed,3);
 assert.deepEqual(advanceHandoff(s,100,3,10),s);s=startPickup(s);assert.equal(s.phase,'picking');s=advanceHandoff(s,100,3,10);assert.equal(s.phase,'awaitDeliveryStart');assert.equal(s.serviceElapsed,2);assert.equal(s.elapsed,3);
 s=startDelivery(s);assert.equal(s.phase,'toDropoff');s=advanceHandoff(s,100,3,10);assert.equal(s.phase,'arrived');assert.equal(s.elapsed,10);
});
test('pickup service preserves partial time and rejects repeat commands',()=>{
 const path=require('node:path'),{startPickup,startDelivery,advanceHandoff}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'ManualHandoff.js'));
 let s={version:1,phase:'awaitPickup',elapsed:3,serviceElapsed:0};s=startPickup(s);s=advanceHandoff(s,1,3,10);assert.equal(s.serviceElapsed,1);assert.throws(()=>startPickup(s));assert.throws(()=>startDelivery(s));s=advanceHandoff(s,1,3,10);assert.equal(s.serviceElapsed,2);assert.equal(s.phase,'awaitDeliveryStart');
});

test('stored handoff must have consistent phase, movement and service progress',()=>{
 const path=require('node:path'),{validateHandoff}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'ManualHandoff.js'));
 for(const [phase,elapsed,serviceElapsed]of [['planning',0,0],['toPickup',1,0],['awaitPickup',3,0],['picking',3,1],['awaitDeliveryStart',3,2],['toDropoff',5,2],['arrived',10,2]])assert.doesNotThrow(()=>validateHandoff({version:1,phase,elapsed,serviceElapsed},3,10));
 for(const bad of [{phase:'picking',elapsed:2,serviceElapsed:0},{phase:'toDropoff',elapsed:4,serviceElapsed:1},{phase:'awaitPickup',elapsed:3,serviceElapsed:2},{phase:'arrived',elapsed:9,serviceElapsed:2},{phase:'future',elapsed:0,serviceElapsed:0}])assert.throws(()=>validateHandoff({version:1,...bad},3,10));
});
