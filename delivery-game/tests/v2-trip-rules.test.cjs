// Written, not run. Requires explicit stage-completion authorization through run-v2.cjs.
const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const base=path.dirname(process.env.MAP_ROUTER_MODULE);
const {V2TripRules,settleTripIncome}=require(path.join(base,'../domain/V2TripRules.js'));
const {V2GameSession}=require(path.join(base,'V2GameSession.js'));
const {V2DispatchSession}=require(path.join(base,'../domain/V2DispatchSession.js'));
const city={title:'trip fixture',width:100,height:100,nodes:[{id:'a',x:0,y:0},{id:'b',x:10,y:0},{id:'c',x:20,y:0}],roads:[{id:'r',nodes:['a','b','c'],direction:0,kind:'primary',width:3,speed:1,roughness:0}],pois:[{node:'a',name:'A',kind:'shop'},{node:'b',name:'B',kind:'shop'},{node:'c',name:'C',kind:'home'}],buildings:[],areas:[],waterways:[],labels:[]};
const begin=()=>{const s=new V2GameSession(city),o=s.normalCandidates(1)[0];s.acceptBatch([o]);s.beginTrip();return {s,o};};
test('zero stamina truncates exact shared travel, supply cost/progress persists once',()=>{
 const t=new V2TripRules();const state=t.state;state.stamina=.5;const r=V2TripRules.restore(state);
 assert.equal(r.travel(1000,100),.25);assert.equal(r.state.stamina,0);assert.equal(r.state.gameSeconds,25);
 let paid=0;r.startSupply('water',true,c=>paid+=c);assert.equal(paid,100);r.advanceSupply(.5);
 const resumed=V2TripRules.restore(r.state);resumed.advanceSupply(.5);assert.equal(resumed.state.stamina,20);assert.equal(resumed.state.gameSeconds,55);assert.equal(paid,100);
 assert.throws(()=>r.startSupply('water',true,c=>paid+=c));
});
test('late and damage each apply once, reputation never multiplies signed base',()=>{
 const f=settleTripIncome(12001,{lateGameSeconds:301,damage:'moderate'});assert.equal(f.incomeCents,Math.round(12001*.85*.75));assert.equal(f.ratingDelta,-6);
 const d=new V2DispatchSession({verifyArrival:()=>true});const q=d.acceptBatch([{id:'late',kind:'ordinary',weightKg:1}])[0];
 const a=d.completeDelivery('late','arrival',0,{lateGameSeconds:601,damage:'severe'}),cash=d.economyState.cashCents;
 assert.equal(a.baseIncomeCents,q.incomeCents);assert.equal(a.incomeCents,Math.round(q.incomeCents*.75*.5));
 d.completeDelivery('late','arrival');assert.equal(d.economyState.cashCents,cash);assert.doesNotThrow(()=>V2DispatchSession.restore(d.serialize(),{verifyArrival:()=>true}));
});
test('service blocked before charge can open water and survives reload',()=>{
 const {s}=begin();s.tick(1,10,true,false);s.pickup();const raw=JSON.parse(s.serialize());raw.tripState.stamina=0;raw.tripState.blocked=true;
 const r=V2GameSession.restore(city,JSON.stringify(raw));const cash=r.dispatch.economyState.cashCents;r.supply('water');
 assert.equal(r.dispatch.economyState.cashCents,cash-100);assert.equal(r.tripState.action.kind,'water');
 const resumed=V2GameSession.restore(city,r.serialize(),{preserveClock:true});resumed.tick(2,11,true,false);assert.equal(resumed.tripState.stamina,0);assert.equal(resumed.tripState.action.elapsedSeconds,0);
 resumed.tick(3,12,true,false);assert.equal(resumed.tripState.stamina,20);
});
test('blocked automatic trip preserves entitlement while fleet frame progresses',()=>{
 const s=new V2GameSession(city);const ticket=s.dispatch.requestAd('auto',null,0,30);s.dispatch.resolveAd(ticket,'completed',1);const offer=s.normalCandidates(1)[0];s.acceptBatch([offer]);s.beginTrip();const raw=JSON.parse(s.serialize());raw.tripState.stamina=0;raw.tripState.blocked=true;
 const r=V2GameSession.restore(city,JSON.stringify(raw),{preserveClock:true}),before=r.snapshot().rewards.autoRemainingSeconds,cash=r.dispatch.economyState.cashCents;
 r.tick(1,101,true,false);assert.equal(r.snapshot().rewards.autoRemainingSeconds,before);assert.equal(r.dispatch.economyState.cashCents,cash);assert.equal(r.snapshot().frame.nowSeconds,101);
});
test('automatic budget cannot reset spent, future versions and old in-flight snapshots reject',()=>{
 const t=new V2TripRules();t.travel(1000,10);t.configureAutoSupply({enabled:true,budgetCents:100,kind:'water',allowPaid:true});t.startSupply('water',true,()=>{},true);
 assert.throws(()=>t.configureAutoSupply({enabled:true,budgetCents:0,kind:'water'}));assert.equal(t.state.autoSupplyPolicy.spentCents,100);
 const {s}=begin(),raw=JSON.parse(s.serialize());raw.version=99;assert.throws(()=>V2GameSession.restore(city,JSON.stringify(raw)));
 raw.version=1;delete raw.tripState;assert.throws(()=>V2GameSession.restore(city,JSON.stringify(raw)));
 const idle=JSON.parse(new V2GameSession(city).serialize());idle.version=1;delete idle.tripState;assert.throws(()=>V2GameSession.restore(city,JSON.stringify(idle)));
 const {legacyIdleRaw}=require('./product-regression-1106/helpers.cjs');assert.doesNotThrow(()=>V2GameSession.restore(city,JSON.stringify(legacyIdleRaw(city))));
});
