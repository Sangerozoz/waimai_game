// Isolated domain fixtures only. Never reads a browser or a real storage adapter.
const path = require('node:path');
const mapDir = path.dirname(process.env.MAP_ROUTER_MODULE);
const domain = name => require(path.join(mapDir, '../domain', name + '.js'));
const map = name => require(path.join(mapDir, name + '.js'));
const { V2GameSession } = map('V2GameSession');
const { V2RouteSession } = map('V2RouteSession');
const { V2DispatchSession } = domain('V2DispatchSession');
const { V2EconomySession } = domain('V2EconomySession');
const { V2TripRules } = domain('V2TripRules');
const city = { title:'isolated directed fixture', width:100, height:100,
  nodes:[{id:'a',x:0,y:0},{id:'b',x:10,y:0},{id:'c',x:20,y:0},{id:'outside',x:100,y:100}],
  roads:[{id:'main',nodes:['a','b','c'],direction:0,kind:'primary',width:3,speed:1,roughness:0,bridge:false},
    {id:'outside',nodes:['a','outside','c'],direction:0,kind:'primary',width:3,speed:100,roughness:0,bridge:false}],
  pois:[{node:'a',name:'A',kind:'shop'},{node:'b',name:'B',kind:'shop'},{node:'c',name:'C',kind:'home'}],
  buildings:[],areas:[],waterways:[],labels:[],dispatchBounds:{minX:0,minY:0,maxX:20,maxY:20} };
function fundEconomyRaw(raw, cents=100000000) {
  raw.state.cashCents=cents;raw.state.ledger.opening.balanceCents=cents;return raw;
}
function richEconomy(profile='slots-v1') {
  return V2EconomySession.restore(JSON.stringify(fundEconomyRaw(JSON.parse(new V2EconomySession(profile).serialize()))));
}
function richGame(data=city) {
  const raw=JSON.parse(new V2GameSession(data).serialize());
  fundEconomyRaw(raw.dispatch.economy);fundEconomyRaw(raw.dispatch.fleet.economy);
  return V2GameSession.restore(data,JSON.stringify(raw),{preserveClock:true});
}
function legacyOrder(id='legacy-order',pickupNode='b',dropoffNode='c',data=city) {
  return {id,kind:'ordinary',weightKg:1,pickupNode,dropoffNode,
    pickupName:data.pois.find(p=>p.node===pickupNode).name,dropoffName:data.pois.find(p=>p.node===dropoffNode).name};
}
function legacyGameRaw(data=city, orders=[legacyOrder()], options={}) {
  const route=new V2RouteSession(data),trip=new V2TripRules();
  let dispatch=new V2DispatchSession({verifyArrival:(order,token)=>route.verifyArrival(order,token)},options.nowSeconds||0);
  if(options.rich){const raw=JSON.parse(dispatch.serialize());fundEconomyRaw(raw.economy);fundEconomyRaw(raw.fleet.economy);dispatch=V2DispatchSession.restore(JSON.stringify(raw),{verifyArrival:(order,token)=>route.verifyArrival(order,token)},{preserveClock:true});}
  if(options.npc){const vehicleId=dispatch.command({type:'buyVehicle',modelId:1});dispatch.command({type:'hireRider',riderId:'npc-1'});dispatch.command({type:'assignVehicle',riderId:'npc-1',vehicleId});}
  route.plan(orders);dispatch.acceptBatch(orders);
  trip.begin(1,route.progress.tripId,orders.map(o=>({id:o.id,...route.fastest(o.pickupNode,o.dropoffNode),fastestGameSeconds:route.fastest(o.pickupNode,o.dropoffNode).gameSeconds,safe:true})));
  route.beginTrip(dispatch.snapshot());
  if(options.ready){
    route.advance(2,true,1,{roadTimeFactor:1,travel:(m,s)=>trip.travel(m,s),service:(id,kind)=>trip.service(id,kind),pickupGroup:ids=>trip.pickupGroup(ids),serviceTime:s=>trip.serviceTime(s)});
    if(route.progress.phase!=='ready')throw new Error('Ready fixture must use a pickup at its starting node');
    route.continueTrip();
  }
  return {format:'county-v2-game',version:4,route:route.snapshot(),dispatch:dispatch.snapshot(),tripState:trip.state};
}
function legacyIdleRaw(data=city) {
  const route=new V2RouteSession(data).snapshot();route.version=1;route.timeProfile='road40-service2-1-v1';delete route.stopPolicy;
  return {format:'county-v2-game',version:1,route,dispatch:new V2DispatchSession({verifyArrival:()=>false}).snapshot()};
}
module.exports={domain,map,city,richEconomy,richGame,legacyOrder,legacyGameRaw,legacyIdleRaw};
