const {test}=require('node:test');
const assert=require('node:assert/strict');
const {RoadRouter,routePosition}=require(process.env.MAP_ROUTER_MODULE);
const importedCity=require('../assets/resources/map-sample/city.json');
const road=(id,nodes,direction=0,speed=10,roughness=0.1,kind='residential')=>({id,nodes,direction,speed,roughness,kind,width:5,bridge:false});
const city={title:'test',width:100,height:100,nodes:[{id:'a',x:0,y:0},{id:'b',x:100,y:0},{id:'c',x:100,y:100},{id:'d',x:0,y:100},{id:'bridge',x:50,y:0},{id:'isolated',x:50,y:50}],roads:[road('one',['a','b'],1),road('two',['b','c']),road('three',['a','d']),road('four',['d','c'])],buildings:[],areas:[],waterways:[],labels:[],pois:[]};
test('routes obey one-way streets even when the reverse is shorter',()=>{
 const route=new RoadRouter(city).find('b','a','fast');
 assert.ok(route);assert.deepEqual(route.nodes,['b','c','d','a']);assert.equal(route.metres,300);
});
test('geometrically coincident bridge or disconnected nodes do not create junctions',()=>{
 const router=new RoadRouter(city);assert.equal(router.find('bridge','c','fast'),null);assert.equal(router.find('a','isolated','fast'),null);
});
test('animation uses segment durations and reaches exact destination',()=>{
 const route={preference:'fast',nodes:['a','b','c'],points:[[0,0],[100,0],[100,100]],segments:[{from:'a',to:'b',road:'1',metres:100,seconds:5,roughness:0},{from:'b',to:'c',road:'2',metres:100,seconds:10,roughness:0}],metres:200,seconds:15,risk:0};
 assert.deepEqual(routePosition(route,10).point,[100,50]);assert.deepEqual(routePosition(route,25).point,[100,100]);assert.deepEqual(routePosition(route,-4).point,[0,0]);
});
test('smooth preference can trade distance for a lower-risk path',()=>{
 const data={...city,roads:[road('rough',['a','b','c'],0,10,1),road('smooth',['a','d','c'],0,8,0.02,'secondary')]};
 const router=new RoadRouter(data);const fast=router.find('a','c','fast');const smooth=router.find('a','c','smooth');
 assert.deepEqual(fast.nodes,['a','b','c']);assert.deepEqual(smooth.nodes,['a','d','c']);assert.ok(smooth.risk<fast.risk);assert.ok(smooth.seconds>fast.seconds);
});

test('all fictional POIs are reachable in both directions with paths on imported roads',()=>{
 const router=new RoadRouter(importedCity);
 const nodes=new Map(importedCity.nodes.map(n=>[n.id,n]));
 const allowed=new Map();
 for(const r of importedCity.roads){
   for(let i=1;i<r.nodes.length;i++){
     const a=r.nodes[i-1],b=r.nodes[i];
     assert.ok(nodes.has(a)&&nodes.has(b),'source road must reference existing nodes');
     if(r.direction!==-1)allowed.set(`${r.id}/${a}/${b}`,true);
     if(r.direction!==1)allowed.set(`${r.id}/${b}/${a}`,true);
   }
 }
 let checked=0;
 for(const from of importedCity.pois.slice(0,8))for(const to of importedCity.pois.slice(0,8)){
   if(from===to)continue;
   for(const preference of ['fast','main','smooth']){
     const route=router.find(from.node,to.node,preference);
     assert.ok(route,`${from.name} → ${to.name}: ${preference}`);
     assert.equal(route.nodes[0],from.node);assert.equal(route.nodes.at(-1),to.node);
     let distance=0,duration=0;
     route.segments.forEach((s,i)=>{
       assert.ok(allowed.has(`${s.road}/${s.from}/${s.to}`),'route step must obey imported direction');
       const a=nodes.get(s.from),b=nodes.get(s.to);
       const metres=Math.hypot(b.x-a.x,b.y-a.y);
       assert.ok(Math.abs(s.metres-metres)<1e-8);
       assert.ok(s.seconds>0);
       assert.equal(s.from,route.nodes[i]);assert.equal(s.to,route.nodes[i+1]);
       const midpoint=routePosition(route,duration+s.seconds/2).point;
       assert.ok(Math.hypot(midpoint[0]-(a.x+b.x)/2,midpoint[1]-(a.y+b.y)/2)<1e-6,'rider must remain on the timed source edge');
       distance+=metres;duration+=s.seconds;
     });
     assert.ok(Math.abs(route.metres-distance)<1e-8);assert.ok(Math.abs(route.seconds-duration)<1e-8);
     assert.deepEqual(routePosition(route,route.seconds+1).point,route.points.at(-1));
     checked++;
   }
 }
 assert.equal(checked,168);
});

test('the delivery map exposes at least eighty distinct customer road addresses',()=>{
 const customers=importedCity.pois.filter(p=>p.kind!=='restaurant');
 assert.ok(customers.length>=80);
 assert.equal(new Set(customers.map(p=>p.node)).size,customers.length);
 const router=new RoadRouter(importedCity),start=importedCity.pois[0].node;
 for(let i=0;i<customers.length;i+=7){
  assert.ok(router.find(start,customers[i].node,'fast'));
  assert.ok(router.find(customers[i].node,start,'fast'));
 }
});

test('the first sample order offers distinct routes with an observable time and risk tradeoff',()=>{
 const router=new RoadRouter(importedCity);
 const routes=['fast','main','smooth'].map(p=>router.find(importedCity.pois[0].node,importedCity.pois[5].node,p));
 assert.equal(new Set(routes.map(r=>r.nodes.join('/'))).size,3);
 assert.ok(routes[0].seconds<routes[2].seconds);
 assert.ok(routes[0].risk>routes[2].risk);
});
