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
test('followup independent receipt X and shade preserve assets, rider, restore and rebuild idempotency',()=>{
 for(const target of ['CloseButton','Shade']){
  const b=realBook();b.accept(b.list()[0].offer.id);b.depart();b.advance(99);if(b.mode==='arrived')b.settle(true);
  const h=harness(b),assets=JSON.stringify(b.player),bill=JSON.stringify(b.billing),pose=JSON.stringify(b.riderPose);h.sample.openReceipt();
  h.sample.closeDialog();assert.equal(b.mode,'done','internal destroy must not finish');h.sample.openReceipt();
  const close=h.walk(h.sample.modal).find(n=>n.name===target);h.click(close);h.click(close);
  assert.equal(b.mode,'idle');assert.equal(h.counts().opened,0);assert.equal(JSON.stringify(b.player),assets);assert.equal(JSON.stringify(b.billing),bill);assert.ok(b.riderPose.point.every((v,i)=>Math.abs(v-JSON.parse(pose).point[i])<1e-8));assert.equal(b.riderPose.angle,JSON.parse(pose).angle);
  h.sample.rebuildLayout();assert.equal(h.sample.modal,null);assert.ok(!h.walk(h.sample.panel).some(n=>n.name==='DeliverySheet'));
  const restored=b.constructor.restore(b.data,b.serialize());assert.equal(restored.mode,'idle');assert.equal(JSON.stringify(restored.player),assets);assert.ok(restored.riderPose.point.every((v,i)=>Math.abs(v-JSON.parse(pose).point[i])<1e-8));assert.equal(restored.riderPose.angle,JSON.parse(pose).angle);
 }
});
test('followup independent receipt failure toast survives rebuild, retry saves idle without double award',()=>{
 const b=realBook();b.accept(b.list()[0].offer.id);b.depart();b.advance(99);if(b.mode==='arrived')b.settle(true);const h=harness(b),assets=JSON.stringify(b.player);let writes=0,last;
 h.sample.store={available:false,message:'独立检查：保存失败',save:()=>false};h.sample.openReceipt();h.click(h.walk(h.sample.modal).find(n=>n.name==='CloseButton'));assert.equal(b.mode,'idle');assert.ok(h.text(h.sample.root).some(s=>s.includes('独立检查：保存失败')));
 h.sample.store={available:true,save(value){writes++;last=value;return true;}};h.sample.save();assert.equal(writes,1);assert.equal(b.constructor.restore(b.data,last).mode,'idle');assert.equal(JSON.stringify(b.player),assets);
});
test('followup independent native footer covers bottom safe inset and number styles agree',()=>{
 const h=harness();h.setSafeArea(height=>({x:10,y:64,width:700,height:height-100}));h.sample.rebuildLayout();
 const bg=h.walk(h.sample.root).find(n=>n.name==='NavigationBackdrop');assert.equal(h.bounds(bg).bottom,-h.height()/2);assert.equal(bg.getComponent(h.UITransform).width,720);
 assert.equal(h.sample.money.fontSize,h.sample.rating.fontSize);assert.equal(h.sample.money.lineHeight,h.sample.rating.lineHeight);assert.equal(h.sample.money.isBold,h.sample.rating.isBold);
 const station=h.walk(h.sample.root).find(n=>n.name==='StationEntry');assert.equal(station.events.size,0);const art=h.walk(station).find(n=>n.name==='CartoonArt-station');assert.ok(art);assert.ok(h.bounds(art).right<=350,'expanded station remains inside right safe edge');
});
`;
const m=new Module(filename,module);m.filename=filename;m.paths=Module._nodeModulePaths(path.dirname(filename));m._compile(source,filename);
