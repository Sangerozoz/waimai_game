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


source+=`
test('independent HUD-final: circle stays circular with asymmetric safe sides and root stable while pressed',()=>{
 const h=harness(realBook());h.setFrame({width:360,height:560});h.setSafeArea(height=>({x:42,y:64,width:620,height:height-100}));h.sample.rebuildLayout();const n=h.walk(h.sample.root).find(n=>n.name==='Nav-orders'),b=h.bounds(n);assert.ok(Math.abs(b.right-b.left-(b.top-b.bottom))<1e-9);const w=b.right-b.left;const e={getID:()=>1,getUILocation:()=>({x:0,y:0})};n.events.get('start')(e);assert.equal(h.bounds(n).right-h.bounds(n).left,w);assert.equal(n.getChildByName('PressVisual').scaleX,.96);
});
test('independent HUD-final: station avoids footer, scale and delivery sheet in idle/routes/running',()=>{
 const b=realBook(),h=harness(b);h.setFrame({width:360,height:560});h.setSafeArea(height=>({x:10,y:28,width:700,height:height-64}));
 for(const mode of ['idle','routes','running']){
  if(mode==='routes')b.accept(b.list()[0].offer.id);if(mode==='running')b.depart();h.sample.rebuildLayout();
  const station=h.walk(h.sample.root).find(n=>n.name==='StationEntry'),text=station.children.find(n=>n.getComponent(h.Label)),art=station.getChildByName('CartoonArt-station'),footer=h.walk(h.sample.root).find(n=>n.name==='NavigationBackdrop'),sheet=h.walk(h.sample.root).find(n=>n.name==='DeliverySheet');
  const lower=Math.min(h.bounds(text).bottom,h.bounds(art).bottom);assert.ok(lower>h.bounds(footer).top,'station clears footer');if(sheet)assert.ok(lower>h.bounds(sheet).top,'station clears active panel');assert.equal(station.events.size,0);
 }
});
test('independent HUD-final: numeric capsules preserve full money at all required sizes and wrap without changing value',()=>{
 const b=realBook(),h=harness(b);for(const frame of [{width:720,height:1280},{width:360,height:560}])for(const cents of [10000,1000000000,10000000000,100000000000,Number.MAX_SAFE_INTEGER]){
 h.setFrame(frame);h.setSafeArea(height=>({x:10,y:28,width:700,height:height-64}));b.playerState.cashCents=cents;h.sample.rebuildLayout();assert.equal(h.sample.money.string,(cents/100).toFixed(2));assert.equal(h.sample.money.fontSize,h.sample.rating.fontSize);assert.equal(h.sample.money.isBold,h.sample.rating.isBold);assert.ok(!h.text(h.sample.root).includes('澄川骑手'));
 const n=h.sample.money.node,size=n.getComponent(h.UITransform);assert.ok(size.height>=h.sample.money.lineHeight);const wallet=h.walk(h.sample.root).find(n=>n.name==='WalletPill');assert.ok(h.bounds(n).right<h.bounds(wallet).right);}
});
`;
source+='\nmodule.exports._hudHarness=()=>harness(realBook());';
const m=new Module(filename,module);m.filename=filename;m.paths=Module._nodeModulePaths(path.dirname(filename));m._compile(source,filename);

const gestureFile=path.join(root,'tests/map-gestures.test.cjs');
let gesture=fs.readFileSync(gestureFile,'utf8');
gesture+=`
test('independent HUD-final: real Locate button changes real camera from dragged 100m to current rider and continues following',()=>{
 const h=require(${JSON.stringify(filename)}).hudHarness();const c=boundedCamera(748);c.overview();c.setRider([-2500,100],37);c.offset=[123,456];h.sample.city=c;
 const n=h.walk(h.sample.root).find(n=>n.name==='FollowRider');h.click(n);assert.equal(c.scale,2);assert.equal(c.scaleLabel.string,'30 m');assert.equal(c.follow,true);assert.ok(c.project(c.riderPoint).every(v=>Math.abs(v)<1e-9));
 c.setRider([-2490,110],40);assert.ok(c.project(c.riderPoint).every(v=>Math.abs(v)<1e-9));assert.equal(c.rider.angle,40);assertViewport(c);
});
`;
m.exports.hudHarness=()=>{const f=m.exports._hudHarness;return f();};
const gm=new Module(gestureFile,module);gm.filename=gestureFile;gm.paths=Module._nodeModulePaths(path.dirname(gestureFile));
// Make the in-memory HUD module available only to this test without altering production files.
require.cache[filename]=m;
gm._compile(gesture,gestureFile);
