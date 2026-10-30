const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');

// Exercise the actual gesture methods. Only the engine/renderer boundary is replaced;
// a full project typecheck and built-browser checks cover that boundary separately.
const source=fs.readFileSync(path.join(__dirname,'../assets/scripts/map-sample/CityMap.ts'),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2015,module:ts.ModuleKind.CommonJS}}).outputText;
const scope={exports:{},require(id){
 if(id==='cc')return {};
 if(id==='./SampleUI')return {C:{blue:'blue',gold:'gold',green:'green'}};
 if(id==='./MapTypes')return require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'MapTypes.js'));
 if(id==='./CityExtent')return require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'CityExtent.js'));
 if(id==='./MapVehicle')return {};
 throw new Error(`Unexpected dependency: ${id}`);
}};
vm.runInNewContext(compiled,scope,{filename:'CityMap.js'});
const {CityMap}=scope.exports;

function camera(scale=1){
 const city=Object.create(CityMap.prototype);
 Object.assign(city,{scale,offset:[0,0],touchPoints:new Map(),follow:false});
 city.sync=()=>{};
 city.local=e=>e.point;
 return city;
}
const touch=(id,x,y=0)=>({getID:()=>id,point:[x,y]});

test('translating both fingers moves the map in the same direction without changing zoom',()=>{
 const city=camera();
 city.touchStart(touch(1,-100));city.touchStart(touch(2,100));
 city.touchMove(touch(1,0));city.touchMove(touch(2,200));
 assert.equal(city.scale,1);
 assert.deepEqual(Array.from(city.offset),[100,0]);
});

function boundedCamera(height=1348){
 const city=Object.create(CityMap.prototype),node={setPosition(){},setScale(){}};
 Object.assign(city,{scale:.6,offset:[0,0],mapHeight:height,data:{width:11672,height:12245,playBounds:{minX:-4530,maxX:-570,minY:-1410,maxY:1110}},riderPoint:[-1540,-130],riderAngle:0,routes:[],selected:0,follow:false,touchPoints:new Map(),world:node,scaleLabel:{},labels:[],poiDots:[],rider:{...node},startPin:{...node},endPin:{...node}});
 city.vehicle={tier:0,setTier(tier){this.tier=tier;}};
 city.drawMajorRoads=city.drawRoutes=city.syncDetails=()=>{};city.local=e=>e.point;
 return city;
}
function assertViewport(city){
 const b=city.data.playBounds,[x,y]=city.offset,s=city.scale,h=city.mapHeight;
 assert.ok((-360-x)/s>=b.minX-1e-8);assert.ok((360-x)/s<=b.maxX+1e-8);
 assert.ok((-h/2-y)/s>=b.minY-1e-8);assert.ok((h/2-y)/s<=b.maxY+1e-8);
}
test('real drag, zoom, locate, route focus and following all apply viewport-aware clamps',()=>{
 for(const h of [748,1030,1348]){
  const c=boundedCamera(h);c.locate();assertViewport(c);
  c.setRider([-4529,-1409],45);assertViewport(c);
  c.touchStart(touch(1,0));c.touchMove(touch(1,100000,100000));assertViewport(c);c.touchEnd(touch(1,0));
  c.zoom(.3);assertViewport(c);c.zoom(3);assertViewport(c);c.overview();assertViewport(c);
  c.locate();assertViewport(c);
  c.routes=[{points:[[-4500,-1400],[-600,1100]]}];c.focusRoute();for(const p of c.routes[0].points){const [x,y]=c.project(p);assert.ok(Math.abs(x)<=320&&Math.abs(y)<=h/2);}
 }
});
test('legacy outside rider and route remain visible in a continuous compatibility camera',()=>{
 const c=boundedCamera();c.routes=[{points:[[1490,-3333],[-1540,-130]]}];
 c.setRider([1490,-3333],0);c.locate();
 const p=c.project(c.riderPoint);assert.ok(Math.abs(p[0])<=360&&Math.abs(p[1])<=674);
 c.setRider([1000,-3000],45);const next=c.project(c.riderPoint);assert.ok(Math.abs(next[0])<=360&&Math.abs(next[1])<=674);
});

test('historic edge addresses are not drawn as ordinary operating dots',()=>{
 const c=boundedCamera(748),node=()=>({active:true,setPosition(){}}),edge=node(),inside=node();
 c.data.dispatchBounds={minX:-4380,maxX:-720,minY:-1260,maxY:960};
 c.poiDots=[{n:edge,x:-4529,y:0},{n:inside,x:-4200,y:0}];
 c.offset=[2400,0];c.syncOverlay();
 assert.equal(edge.active,false);assert.equal(inside.active,true);
});

test('every operating address can be located with its full rider and destination pin visible',()=>{
 const {prepareCity}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'PlaceCatalog.js'));
 const data=prepareCity(require('../assets/resources/map-sample/city.json')),nodes=new Map(data.nodes.map(n=>[n.id,n])),b=data.dispatchBounds;
 for(const poi of data.pois){
  const n=nodes.get(poi.node);if(n.x<b.minX||n.x>b.maxX||n.y<b.minY||n.y>b.maxY)continue;
  for(const height of [748,1348,1512])for(const scale of [.6,2,6]){
   const c=boundedCamera(height);c.data=data;c.scale=scale;c.riderPoint=[n.x,n.y];c.locate();
   // An 80×128 vehicle fits inside a 76px radius at any heading, including diagonals.
   const p=c.project(c.riderPoint);assert.ok(Math.abs(p[0])+76<=360);assert.ok(p[1]+76<=height/2);assert.ok(p[1]-76>=-height/2);
  }
 }
});

test('responsive layout keeps the actual hundred-metre camera inside town on narrow tall screens',()=>{
 const frame={width:320,height:1000},visible={width:720,height:1280};
 const view={getFrameSize:()=>frame,getVisibleSize:()=>visible,setDesignResolutionSize(w,h,policy){visible.width=w;visible.height=policy==='fixed-width'?frame.height/frame.width*w:h;}};
 const source=fs.readFileSync(path.join(__dirname,'../assets/scripts/map-sample/MapSample.ts'),'utf8');
 const compiled=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2015,module:ts.ModuleKind.CommonJS,experimentalDecorators:true}}).outputText;
 const scope={exports:{},require(id){
  if(id==='cc')return {_decorator:{ccclass:()=>target=>target},Component:class{},view,ResolutionPolicy:{FIXED_WIDTH:'fixed-width',SHOW_ALL:'show-all'}};
  if(id==='./CityMap')return {CityMap:new Proxy(CityMap,{construct(_target,[_parent,_data,height,_attribution,mapY]){const city=boundedCamera(height);city.mapY=mapY;return city;}})};
  if(id==='./SampleUI')return {item:()=>({destroy(){},getChildByName(){return null;}}),box(){},C:{}};
  if(id==='./PresentationLayout'){const compiled=ts.transpileModule(fs.readFileSync(path.join(__dirname,'../assets/scripts/map-sample/PresentationLayout.ts'),'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2015,module:ts.ModuleKind.CommonJS}}).outputText;const metricsScope={exports:{},require:dep=>dep==='cc'?{view}:{}};vm.runInNewContext(compiled,metricsScope);return metricsScope.exports;}
  if(id==='./ReceiptPresentation')return {ReceiptPresentation:class{}};
  if(id==='./SafeAreaLayout')return require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'SafeAreaLayout.js'));
  return {};
 }};
 vm.runInNewContext(compiled,scope,{filename:'MapSample.js'});
 const sample=new scope.exports.MapSample();
 Object.assign(sample,{node:{parent:{}},book:{mode:'idle',data:boundedCamera().data,player:{vehicleTier:2},active:null,riderPose:{point:[-1540,-130],angle:0}}});
 sample.header=sample.controls=sample.renderPanel=()=>{};
 for(const mode of ['idle','routes','running','done'])for(const [width,height] of [[320,1000],[320,1200],[390,844],[720,1280],[1280,720]]){
  sample.book.mode=mode;
  Object.assign(frame,{width,height});sample.rebuildLayout();sample.city.overview();
  assertViewport(sample.city);
  assert.equal(sample.city.scale,.6);
  assert.ok(sample.city.mapHeight>0&&sample.city.mapHeight<=visible.height,'active presentation leaves a positive camera viewport');
  assert.ok(Math.abs(sample.city.mapY+sample.city.mapHeight/2-visible.height/2)<1e-7,'map extends behind the fading header');
  assert.equal(sample.city.vehicle.tier,2,'restored and rebuilt maps show the owned vehicle');
 }
});

test('spreading two fingers around a stationary midpoint keeps that map point pinned',()=>{
 const city=camera();
 city.touchStart(touch(1,-100));city.touchStart(touch(2,100));
 city.touchMove(touch(1,-200));city.touchMove(touch(2,200));
 assert.equal(city.scale,2);
 assert.ok(Math.hypot(...city.offset)<1e-8);
});

test('the pinch midpoint remains stable when zoom reaches its upper limit',()=>{
 const city=camera(6);
 city.touchStart(touch(1,-100));city.touchStart(touch(2,100));
 city.touchMove(touch(1,-300));city.touchMove(touch(2,300));
 assert.equal(city.scale,6);
 assert.ok(Math.hypot(...city.offset)<1e-8);
});


test('locating for departure restores thirty metres and all zoom paths stay within ten to one hundred metres',()=>{
 const city=camera(.65);
 Object.assign(city,{riderPoint:[1200,-300],data:{width:12000,height:12000},mapHeight:748,routes:[{points:[[0,0],[10000,10000]]}]});
 city.locate(true);assert.equal(city.scale,2);assert.equal(city.follow,true);
 assert.deepEqual(Array.from(city.offset),[-2400,600]);
 city.zoom(.0001);assert.equal(city.scale,.6);
 city.zoom(10000);assert.equal(city.scale,6);
 city.overview();assert.equal(city.scale,.6);
 city.focusRoute();assert.ok(city.scale>0&&city.scale<.6);city.zoom(1);assert.equal(city.scale,.6);
});

test('explicit default locate restores actual 30m scale and follows current rider',()=>{const c=boundedCamera(748);c.overview();assert.equal(c.scale,.6);c.setRider([-2500,0],45);c.locate(true);assert.equal(c.scale,2);assert.equal(c.scaleLabel.string,'30 m');assert.equal(c.follow,true);assert.deepEqual(Array.from(c.project(c.riderPoint)),[0,0]);c.setRider([-2490,0],45);assert.deepEqual(Array.from(c.project(c.riderPoint)),[0,0]);});

test('explicit animated locate interpolates pan and scale together, redirects to moving rider and cancels on manual input',()=>{const c=boundedCamera(748);c.overview();c.offset=[1700,0];c.locateAnimated();c.advanceLocate(.3);assert.ok(c.scale>.6&&c.scale<2);assert.notEqual(c.offset[0],1700);c.setRider([-2400,0],0);c.advanceLocate(.3);assert.equal(c.scale,2);assert.equal(c.follow,true);assert.deepEqual(Array.from(c.project(c.riderPoint)),[0,0]);c.overview();c.locateAnimated();c.advanceLocate(.2);c.zoom(1.1);const scale=c.scale;c.advanceLocate(1);assert.equal(c.scale,scale);assert.equal(c.follow,false);});

test('animated locate retargets from current view and cancels on drag or lifecycle stop',()=>{const c=boundedCamera(748);c.overview();c.locateAnimated();c.advanceLocate(.2);const start=c.scale;c.locateAnimated();c.advanceLocate(.01);assert.ok(c.scale>=start&&c.scale<2);c.touchStart(touch(1,0));const at=c.scale;c.advanceLocate(1);assert.equal(c.scale,at);c.touchEnd(touch(1,0));c.locateAnimated();c.cancelLocate();c.advanceLocate(1);assert.equal(c.scale,at);});
test('static rider stays visible while world center converges monotonically',()=>{const c=boundedCamera(748);c.overview();c.offset=[1200,0];let distance=Math.hypot(-c.offset[0]/c.scale-c.riderPoint[0],-c.offset[1]/c.scale-c.riderPoint[1]);c.locateAnimated();for(let i=0;i<6;i++){c.advanceLocate(.1);const next=Math.hypot(-c.offset[0]/c.scale-c.riderPoint[0],-c.offset[1]/c.scale-c.riderPoint[1]);assert.ok(next<=distance+1e-8);assert.ok(Math.abs(c.project(c.riderPoint)[0])<360);distance=next;}});

test('ordinary and edge-visible rider converge without overshoot using fixed final camera offsets',()=>{for(const startX of [276,340]){const c=boundedCamera(748);c.overview();c.offset=[startX-c.riderPoint[0]*c.scale,0];const startCenter=-c.offset[0]/c.scale,target=c.riderPoint[0];let lastDistance=Math.abs(startCenter-target),lastScreen=startX;c.locateAnimated();for(let i=0;i<12;i++){c.advanceLocate(.05);const center=-c.offset[0]/c.scale,project=c.project(c.riderPoint)[0];assert.ok(center>=Math.min(startCenter,target)-1e-8&&center<=Math.max(startCenter,target)+1e-8);assert.ok(Math.abs(center-target)<=lastDistance+1e-8);assert.ok(project>=-1e-8&&project<=lastScreen+1e-8);lastDistance=Math.abs(center-target);lastScreen=project;}c.advanceLocate(.001);assert.equal(c.scale,2);assert.equal(c.follow,true);}});

test('automatic route overview fits every bend below HUD while manual locate keeps 30m',()=>{
 const c=boundedCamera(600);c.routes=[{points:[[-4500,-1400],[-400,2100],[-6200,0],[-600,1100]]}];
 c.focusRoute();assert.ok(c.scale<.6);
 for(const p of c.routes[0].points){const [x,y]=c.project(p);assert.ok(x>=-320&&x<=320,`x=${x}`);assert.ok(y>=-48-1e-7&&y<=68+1e-7,`y=${y}`);}
 assert.equal(c.scaleLabel.string,`${Math.round(60/c.scale)} m`);c.locate(true);assert.equal(c.scale,2);
});

test('manual pan in planning overview survives capture and layout restoration at the actual low scale',()=>{
 const c=boundedCamera(748);c.routes=[{points:[[-4500,-1400],[-600,1100]]}];c.focusRoute();assert.ok(c.scale<.6);
 c.touchStart(touch(1,0));c.touchMove(touch(1,60,20));c.touchEnd(touch(1,60,20));const before=c.captureView();
 const next=boundedCamera(748);next.routes=c.routes;next.restoreView(before);assert.equal(next.scale,before.scale);assert.deepEqual(Array.from(next.offset),Array.from(before.offset));
});

test('locating from the new low planning scale retains smooth projected convergence to 30m',()=>{
 const c=boundedCamera(748);c.routes=[{points:[[-4500,-1400],[-600,1100]]}];c.focusRoute();const start=Array.from(c.project(c.riderPoint));c.locateAnimated();c.advanceLocate(.3);
 for(let i=0;i<2;i++)assert.ok(Math.abs(c.project(c.riderPoint)[i]-start[i]*.5)<1e-7);c.advanceLocate(.3);assert.equal(c.scale,2);assert.equal(c.isFollowing,true);
});
