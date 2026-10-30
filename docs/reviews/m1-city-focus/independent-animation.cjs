// Isolated review runner: production sources and developer tests are read only.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),Module=require('node:module');
const root=path.resolve(__dirname,'../../../delivery-game');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const out=fs.mkdtempSync(path.join(os.tmpdir(),'m1-independent-'));
process.on('exit',()=>fs.rmSync(out,{recursive:true,force:true}));
const names=['MapTypes','CityExtent','SafeAreaLayout','PlaceCatalog','FoodCatalog','RoadRouter','DeliveryClock','CountyRules','OrderBook','ReceiptPresentation','BillingPresentation'];
const program=ts.createProgram(names.map(n=>path.join(root,'assets/scripts/map-sample',n+'.ts')),{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:path.join(root,'assets/scripts'),outDir:out,skipLibCheck:true,types:[]});
const emitted=program.emit();if(ts.getPreEmitDiagnostics(program).length||emitted.emitSkipped)throw Error('Review fixture compilation failed');
process.env.MAP_ROUTER_MODULE=path.join(out,'map-sample/RoadRouter.js');
const filename=path.join(root,'tests/map-hud.test.cjs');
let source=fs.readFileSync(filename,'utf8');
// Model actual reparenting: a child exists in exactly one parent's children list.
source=source.replace("static EventType={TOUCH_START:'start'", "static EventType={ACTIVE_IN_HIERARCHY_CHANGED:'active',NODE_DESTROYED:'destroy',TOUCH_START:'start'");
source=source.replace('addChild(n){this.children.push(n);n.parent=this;}', 'addChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}');
source=source.replace('destroy(){this.destroyed=true;}', "get activeInHierarchy(){return this.active&&(!this.parent||this.parent.activeInHierarchy);}destroy(){this.events.get('destroy')?.();this.destroyed=true;}");



source=source.replace('const cc={Tween:', 'const cc={game:{off(){}},Game:{EVENT_HIDE:1,EVENT_SHOW:2},Tween:').replace('view:{getFrameSize:', 'view:{off(){},getFrameSize:');
source+='\nmodule.exports.hud=()=>harness(realBook());';
const m=new Module(filename,module);m.filename=filename;m.paths=Module._nodeModulePaths(path.dirname(filename));m._compile(source,filename);require.cache[filename]=m;
const file=path.join(root,'tests/map-gestures.test.cjs');let gestures=fs.readFileSync(file,'utf8');gestures+=`
test('city-focus independent: real rebuild and onDestroy cancel the former camera state',()=>{
 const h=require(${JSON.stringify(filename)}).hud(),c=boundedCamera(748);c.overview();c.locateAnimated();h.sample.city=c;h.sample.rebuildLayout();assert.equal(c.locating,null);
 c.locateAnimated();h.sample.city=c;h.sample.onDestroy();assert.equal(c.locating,null);const scale=c.scale;c.advanceLocate(1);assert.equal(c.scale,scale);
});

test('city-focus independent: visible near-edge stationary rider does not leave viewport during zoom',()=>{
 const c=boundedCamera(1280);c.overview();c.offset=[1264,0];c.sync();const before=c.project(c.riderPoint)[0];assert.ok(before>330&&before<350);c.locateAnimated();c.advanceLocate(.3);console.log('EDGE',before,c.project(c.riderPoint)[0]);assert.ok(Math.abs(c.project(c.riderPoint)[0])<=360,'near-edge visible rider left viewport');
});

test('city-focus independent: stationary world center stays on segment and distance converges without overshoot',()=>{
 const c=boundedCamera(1280);c.overview();c.offset=[1200,0];c.sync();const start=c.offset.map(v=>-v/c.scale),target=Array.from(c.riderPoint),delta=target.map((v,i)=>v-start[i]);c.locateAnimated();let last=Math.hypot(...delta);
 for(let i=0;i<60;i++){c.advanceLocate(.01);const center=c.offset.map(v=>-v/c.scale),v=center.map((x,i)=>x-start[i]),e=v[0]/delta[0],distance=Math.hypot(...center.map((x,i)=>target[i]-x));assert.ok(e>=-1e-8&&e<=1+1e-8,'center passed target');assert.ok(Math.abs(v[1]-e*delta[1])<1e-7,'center left interpolation segment');assert.ok(distance<=last+1e-7,'center moves away from rider');last=distance;}assert.ok(last<1e-7);
});

test('city-focus independent: initially visible rider stays visible through stationary locate',()=>{
 const c=boundedCamera(1280);c.overview();c.offset=[1200,0];c.sync();assert.ok(Math.abs(c.project(c.riderPoint)[0])<360);c.locateAnimated();c.advanceLocate(.3);console.log('OVERSHOOT',JSON.stringify({scale:c.scale,project:c.project(c.riderPoint)}));assert.ok(Math.abs(c.project(c.riderPoint)[0])<=360,'visible rider left viewport during locate');
});

test('city-focus independent: actual button and MapSample.update animate idle and running frames jointly',()=>{
 for(const running of [false,true]){
 const h=require(${JSON.stringify(filename)}).hud(),c=boundedCamera(748);c.overview();c.offset=[1600,0];if(running){h.sample.book.accept(h.sample.book.list()[0].offer.id);h.sample.book.depart();}h.sample.city=c;h.sample.onlineAt=null;h.sample.saveElapsed=0;h.sample.billElapsed=0;
 const n=h.walk(h.sample.root).find(n=>n.name==='FollowRider');h.click(n);assert.equal(c.scale,.6);assert.deepEqual(Array.from(c.offset),[1600,0]);const frames=[{t:0,s:c.scale,x:c.offset[0]}];
 for(let i=1;i<=4;i++){h.sample.update(.15);frames.push({t:i*.15,s:c.scale,x:c.offset[0]});assert.ok(c.scale>frames[i-1].s);assert.notEqual(c.offset[0],frames[i-1].x);}
 assert.equal(c.scale,2);assert.equal(c.scaleLabel.string,'30 m');assert.equal(c.follow,true);assert.ok(c.project(c.riderPoint).every(v=>Math.abs(v)<1e-8));console.log('FRAMES',running?'running':'idle',JSON.stringify(frames));
 c.overview();h.click(n);h.sample.update(.15);const s=c.scale,x=c.offset[0];h.click(n);assert.equal(c.scale,s);assert.equal(c.offset[0],x);h.sample.update(.15);assert.ok(c.scale>s);
 for(const kind of ['drag','pinch','wheel','hide']){c.overview();h.click(n);h.sample.update(.15);if(kind==='wheel')c.zoom(1.1);else if(kind==='hide'){h.sample.onHide();h.sample.hidden=false;}else {c.touchStart(touch(1,0));if(kind==='pinch')c.touchStart(touch(2,20));}const at=c.scale;c.advanceLocate(.6);assert.equal(c.scale,at);assert.equal(c.locating,null);}
 }
});
`;const gm=new Module(file,module);gm.filename=file;gm.paths=Module._nodeModulePaths(path.dirname(file));gm._compile(gestures,file);
