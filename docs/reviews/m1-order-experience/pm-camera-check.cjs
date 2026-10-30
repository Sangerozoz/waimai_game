const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const root=process.cwd(),dir=path.join(root,'delivery-game/assets/scripts/map-sample');
function load(name,deps={}){const scope={exports:{},require(id){if(id in deps)return deps[id];throw new Error(id);}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(dir,name+'.ts'),'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText,scope);return scope.exports;}
const extent=load('CityExtent'),{CityMap}=load('CityMap',{'cc':{},'./CityExtent':extent,'./SampleUI':{C:{}},'./MapVehicle':{}});
function camera(height,pad){const c=Object.create(CityMap.prototype),n=()=>({setPosition(){},setScale(){}});Object.assign(c,{scale:2,offset:[0,0],mapHeight:height,routeInsets:pad,data:{width:12000,height:14000,playBounds:{minX:-4530,maxX:-570,minY:-1410,maxY:1110}},routes:[],selected:0,riderPoint:[-1540,-130],riderAngle:0,follow:false,routeOverview:false,autoFit:false,touchPoints:new Map(),world:n(),rider:n(),startPin:n(),endPin:n(),scaleLabel:{},labels:[],poiDots:[],detailElapsed:0});c.drawMajorRoads=c.drawRoutes=c.syncDetails=()=>{};c.local=e=>e.point;return c;}
const geometries=[
 [[-1540,-130],[-4600,1800],[-600,900],[-2400,-900]],
 [[-1540,-130],[-9000,-3000],[3000,4000],[-2400,-900]],
 [[-1540,-130],[-1400,-130],[-1400,-100],[-1500,-110]],
];
let cases=0;
for(const height of [668,626,590])for(const safe of [0,24]){
 const pad={top:232+safe,bottom:252,left:90+safe,right:90+safe};
 for(const points of geometries){
  const c=camera(height,pad);c.routes=[{points,pickupIndex:1,preference:'fast'}];c.focusRoute();assert.ok(c.scale>0);assert.equal(c.autoFit,true);
  for(const p of points){const q=c.project(p);assert.ok(q[0]>=-360+pad.left-1e-7&&q[0]<=360-pad.right+1e-7,'horizontal fit');assert.ok(q[1]>=-height/2+pad.bottom-1e-7&&q[1]<=height/2-pad.top+1e-7,'vertical fit');}
  const e=(x,y)=>({getID:()=>1,point:[x,y]});c.touchStart(e(0,0));c.touchMove(e(17,-13));c.touchEnd(e(17,-13));const state=c.captureView();assert.equal(state.autoFit,false);
  const rebuilt=camera(height+18,pad);rebuilt.routes=c.routes;rebuilt.restoreView(state);assert.equal(rebuilt.scale,state.scale);assert.deepEqual(Array.from(rebuilt.offset),Array.from(state.offset));
  c.locateAnimated();let distance=Math.hypot(...c.project(c.riderPoint));for(let i=0;i<4;i++){c.advanceLocate(.15);const d=Math.hypot(...c.project(c.riderPoint));assert.ok(d<=distance+1e-7,'locate converges');distance=d;}assert.equal(c.scale,2);assert.equal(c.follow,true);assert.ok(distance<1e-7);cases++;
 }
}
const records=JSON.parse(fs.readFileSync(path.join(__dirname,'browser-check-evidence.json')));let points=0,marks=0;
for(const row of records){const m=row.measurements,v=m.viewport,scale=Math.min(row.width/720,row.height/1280);assert.ok(m.gap*scale>=12-1e-7);for(const q of m.points){assert.ok(q[0]>=-360+90+m.insets.left-1e-6&&q[0]<=360-90-m.insets.right+1e-6);assert.ok(q[1]>=-v.height/2+252-1e-6&&q[1]<=v.height/2-232-m.insets.top+1e-6);points++;}for(const b of [m.vehicle,...m.pins]){assert.ok(b.x>=v.x-1e-6&&b.x+b.width<=v.x+v.width+1e-6);assert.ok(b.y>=v.y-1e-6&&b.y+b.height<=v.y+v.height+1e-6);marks++;}}
console.log(JSON.stringify({productionCameraCases:cases,renderedViewports:records.length,renderedRoutePoints:points,renderedVehicleAndPins:marks,result:'PASS',boundary:'Camera methods use renderer stubs; browser measurements supplied by the isolated real-Cocos fixture, independently asserted here; not real FPS or user-page operations.'},null,2));
