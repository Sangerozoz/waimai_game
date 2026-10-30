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

const emit=(n,type,x=0,y=0,id=1)=>n.events.get(type)?.({getID:()=>id,getUILocation:()=>({x,y})});
test('independent: reparented button visual includes background and caption; hit root stays fixed',()=>{
 const h=harness(),ui=h.load('./SampleUI');let calls=0;
 const b=ui.button(h.root,'test',10,20,200,78,()=>calls++),v=b.getChildByName('PressVisual');
 assert.equal(b.children.length,1);assert.equal(v.children.length,2);assert.ok(v.getChildByName('Surface'));assert.ok(v.getChildByName('Label'));
 emit(b,'start');assert.equal(v.scaleX,.96);assert.equal(b.scaleX??1,1);assert.equal(b.getComponent(h.UITransform).width,200);
 emit(b,'end');assert.equal(calls,1);emit(b,'end');assert.equal(calls,1);
});
test('independent: disabled buttons, destruction, cancellation and second-finger cancellation do not misfire',()=>{
 const h=harness(),ui=h.load('./SampleUI');let calls=0;
 const disabled=ui.button(h.root,'disabled',0,0,200,78,()=>calls++,ui.C.primary,ui.C.ink,false);emit(disabled,'start');emit(disabled,'end');assert.equal(calls,0);
 for(const mode of ['cancel','destroy','active','drag']){
  const b=ui.button(h.root,'enabled',0,0,200,78,()=>calls++),v=b.getChildByName('PressVisual');emit(b,'start');
  if(mode==='destroy')b.destroy();else if(mode==='active'){b.active=false;emit(b,'active');b.active=true;}else if(mode==='drag')emit(b,'move',8);else emit(b,'cancel');
  assert.equal(v.scaleX,1);emit(b,'end');assert.equal(calls,0);
 }
 const b=ui.button(h.root,'multi',0,0,200,78,()=>calls++);emit(b,'start');emit(b,'cancel',0,0,2);emit(b,'end');assert.equal(calls,1);
});
test('independent: real nav children reparent and real callback stays live; disabled recruit has no action',()=>{
 const h=harness(),nodes=h.walk(h.root),orders=nodes.find(n=>n.name==='Nav-orders'),v=orders.getChildByName('PressVisual');
 assert.equal(orders.children.length,1);assert.ok(v.getChildByName('CartoonArt-bag'));assert.ok(v.getChildByName('Label'));
 h.click(orders);assert.equal(h.counts().opened,1);const recruit=nodes.find(n=>n.name==='Nav-recruit');assert.equal(recruit.getChildByName('PressVisual'),undefined);h.click(recruit);assert.equal(h.counts().opened,1);
});
test('independent: shared dialogs use one geometric header and icon close still destroys modal',()=>{
 const h=harness();for(const kind of ['garage','bills','maps','receipt']){
  const d=h.sample.dialog(kind,900,kind),header=d.card.getChildByName('DialogHeader');assert.equal(header.children.length,1);assert.ok(header.getChildByName('Surface'));
  const b=d.card.getChildByName('CloseButton');assert.ok(b.getChildByName('PressVisual').getChildByName('Icon-close'));h.click(b);assert.equal(h.sample.modal,null);assert.equal(d.layer.active,false);
 }
});
test('independent: root-attached label tap leaves visible renderer outside PressVisual (reproduces attribution feedback gap)',()=>{
 const h=harness(),ui=h.load('./SampleUI');let calls=0;
 // Same production calling pattern as CityMap.ts:60-61.
 const caption=ui.label(h.root,'© OpenStreetMap contributors',0,0);ui.tap(caption.node,()=>calls++);emit(caption.node,'start');
 const v=caption.node.getChildByName('PressVisual');assert.equal(v.scaleX,.96);assert.equal(v.children.length,0);assert.equal(caption.node.getComponent(h.Label),caption);assert.equal(caption.node.scaleX??1,1);emit(caption.node,'end');assert.equal(calls,1);
});
`;
const m=new Module(filename,module);m.filename=filename;m.paths=Module._nodeModulePaths(path.dirname(filename));m._compile(source,filename);
// Exercise the real async loader after SampleUI has reparented its picture and fallback.
const artFilename=path.join(root,'tests/cartoon-art.test.cjs');
let artSource=fs.readFileSync(artFilename,'utf8');
artSource=artSource.replace('addChild(n){this.children.push(n);n.parent=this;}', 'addChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}');
artSource=artSource.replace('getComponent(T){return this.components.get(T);}', "getComponent(T){return this.components.get(T);}getChildByName(name){return this.children.find(c=>c.name===name);}");
artSource=artSource.replace('const cc={Node,', 'const cc={Tween:{stopAllByTarget(){}},tween:()=>({to(){return this;},start(){}}),Vec3:class{},Node,');
artSource+=`
test('independent: async icon success after reparent fits once and hides the moved fallback',async()=>{
 const h=harness(),parent=h.node(),picture=h.ui.icon(parent,'vehicle',0,0,h.ui.C.ink,2.25);
 h.ui.tap(parent,()=>{});const v=parent.getChildByName('PressVisual');assert.equal(parent.children.length,1);assert.equal(picture.parent,v);
 h.requests[0].callback(null,h.texture());await flush();assert.equal(picture.active,true);assert.equal(v.getChildByName('Icon-vehicle').active,false);
 const dim=picture.getComponent(h.UITransform),frame=picture.getComponent(h.Sprite).spriteFrame;
 assert.ok(Math.abs(dim.width/dim.height-frame.originalSize.width/frame.originalSize.height)<1e-10);
});
test('independent: late icon callback after owning button closes cannot reactivate its moved subtree',async()=>{
 const h=harness(),parent=h.node(),picture=h.ui.icon(parent,'vehicle',0,0,h.ui.C.ink,2.25);h.ui.tap(parent,()=>{});parent.active=false;
 h.requests[0].callback(null,h.texture());await flush();assert.equal(picture.active,false);assert.equal(picture.getComponent(h.Sprite).spriteFrame,undefined);
});
`;
const artModule=new Module(artFilename,module);artModule.filename=artFilename;artModule.paths=Module._nodeModulePaths(path.dirname(artFilename));artModule._compile(artSource,artFilename);
