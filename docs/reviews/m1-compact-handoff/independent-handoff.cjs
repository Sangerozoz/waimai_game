// Isolated review runner: production sources and developer tests are read only.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),Module=require('node:module');
const root=path.resolve(__dirname,'../../../delivery-game');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const out=fs.mkdtempSync(path.join(os.tmpdir(),'m1-independent-'));
process.on('exit',()=>fs.rmSync(out,{recursive:true,force:true}));
const names=['MapTypes','RiderAnchor','ManualHandoff','CityExtent','SafeAreaLayout','PlaceCatalog','FoodCatalog','RoadRouter','DeliveryClock','CountyRules','OrderBook','ReceiptPresentation','BillingPresentation'];
const program=ts.createProgram(names.map(n=>path.join(root,'assets/scripts/map-sample',n+'.ts')),{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:path.join(root,'assets/scripts'),outDir:out,skipLibCheck:true,types:[]});
const emitted=program.emit();if(ts.getPreEmitDiagnostics(program).length||emitted.emitSkipped)throw Error('Review fixture compilation failed');
process.env.MAP_ROUTER_MODULE=path.join(out,'map-sample/RoadRouter.js');

const filename=path.join(root,'tests/map-hud.test.cjs');let source=fs.readFileSync(filename,'utf8').split('\ntest(')[0];source=source.replace(/require\('\.\/legacy-order-fixture\.cjs'\)\([^\n]+\);/, '');
source=source.replace("const compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),", "const raw=fs.readFileSync(file,'utf8');const compiled=ts.transpileModule(process.env.INDEPENDENT_OLD_EVENT_KEY&&name==='MapSample'?raw.replace(\"this.book.accept(id);this.lastHandoffEvent='';\",\"this.book.accept(id);\"):raw,");
source=source.replace('addChild(n){this.children.push(n);n.parent=this;}', 'addChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}');
source=source.replace('getComponent(Type){return this.components.get(Type);}', 'getComponent(Type){return this.components.get(Type);}');source+='\nmodule.exports={harness};';
const m=new Module(filename,module);m.filename=filename;m.paths=Module._nodeModulePaths(path.dirname(filename));m._compile(source,filename);const {harness}=m.exports;
const {test}=require('node:test'),assert=require('node:assert/strict');const {OrderBook}=require(path.join(out,'map-sample/OrderBook.js'));
function book(){const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0})),data={title:'UI test',width:16000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:'地点'+i,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};const b=new OrderBook(data,()=>.1,()=> '2026-10-30');const offer=b.list().find(p=>p.pickupMetres>0&&p.available);if(!offer)throw Error('no nonzero pickup');b.accept(offer.offer.id);return b;}
function init(b){const h=harness(b);h.sample.rebuildLayout();h.find=n=>h.walk(h.sample.root).find(x=>x.name===n);h.press=n=>{const x=h.find('Button-'+n);assert.ok(x,'missing '+n);h.click(x);};return h;}
function hide(h,mode){if(mode==='hidden')h.click(h.find('DeliverySheet').getChildByName('CloseButton'));else{h.click(h.find('Nav-'+mode));assert.equal(h.sample.modalKind,mode==='vehicle'?'garage':mode==='map'?'maps':mode);}}
for(const trigger of ['pickup','ready','done'])for(const mode of ['hidden','vehicle','map','bills'])test('ui handoff '+trigger+' over '+mode,()=>{
 const b=book(),h=init(b);h.press('去取餐');assert.equal(b.active.handoff.phase,'toPickup');
 if(trigger!=='pickup'){h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');h.press('取餐');assert.equal(b.active.handoff.phase,'picking');}
 if(trigger==='done'){h.sample.update(2);assert.equal(b.active.handoff.phase,'awaitDeliveryStart');h.press('去送餐');assert.equal(b.active.handoff.phase,'toDropoff');}
 hide(h,mode);const oldRoot=h.sample.root;h.sample.update(trigger==='ready'?2:999);
 const phase=trigger==='pickup'?'awaitPickup':trigger==='ready'?'awaitDeliveryStart':'arrived';assert.equal(b.active.handoff.phase,phase);assert.equal(h.sample.modalKind,trigger==='done'?'receipt':null);assert.equal(h.sample.orderCardOpen,true);assert.ok(h.find('DeliverySheet'));assert.notEqual(h.sample.root,oldRoot);
 if(trigger!=='done')h.press(trigger==='pickup'?'取餐':'去送餐');else {const after=JSON.stringify(b.player);h.sample.update(.1);assert.equal(JSON.stringify(b.player),after);}
});
test('ui save failure blocks phase progress and retries before exposing new action',()=>{
 const b=book(),h=init(b);h.sample.store={message:'保存失败',save:()=>false};h.press('去取餐');assert.equal(h.sample.pendingSave,true);const before=JSON.stringify(b.active);h.sample.update(999);assert.equal(JSON.stringify(b.active),before);assert.ok(h.sample.noticeMessage.includes('保存失败'));h.sample.store={save:()=>true};h.sample.update(1);assert.equal(h.sample.pendingSave,false);
});
test('ui same handoff event does not repeatedly reopen after user closes card or opens other view',()=>{
 for(const mode of ['hidden','vehicle','map','bills']){const b=book(),h=init(b);h.press('去取餐');h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');hide(h,mode);const root=h.sample.root,modal=h.sample.modalKind;h.sample.update(.1);h.sample.update(.1);assert.equal(h.sample.root,root);assert.equal(h.sample.modalKind,modal);assert.equal(b.active.handoff.phase,'awaitPickup');}
});
test('ui background freezes movement and only presents arrival after resumed time',()=>{
 const b=book(),h=init(b);h.press('去取餐');h.sample.hidden=true;const old=JSON.stringify(b.active);h.sample.update(999);assert.equal(JSON.stringify(b.active),old);h.sample.hidden=false;h.sample.skipNextFrame=true;h.sample.update(999);assert.equal(JSON.stringify(b.active),old);h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');assert.ok(h.find('Button-取餐'));
});
test('ui normal planning: compact details and routes fit visible viewport at standard and short safe',()=>{
 for(const frame of [{width:720,height:1280},{width:360,height:560}]){const b=book(),h=init(b);h.setFrame(frame);h.setSafeArea(height=>({x:10,y:28,width:700,height:height-64}));h.sample.rebuildLayout();const details=h.find('OrderDetails'),vp=details.parent,size=details.getComponent(h.UITransform),v=vp.getComponent(h.UITransform);console.log('COMPACT',JSON.stringify({frame,content:size.height,viewport:v.height,routeCount:b.active.routes.length}));const routes=h.walk(details).filter(n=>n.name.startsWith('Route-'));const clipped=routes.map(n=>-(n.y-n.getComponent(h.UITransform).height/2)-v.height);console.log('ROUTE_CLIP',JSON.stringify({frame,clipped}));assert.ok(clipped.every(x=>x<=1),'normal route bottom clipped');const sheet=h.find('DeliverySheet'),main=h.find('Button-去取餐');assert.ok(h.bounds(vp).bottom>=h.bounds(main).top);assert.ok(h.walk(sheet).some(n=>n.name.startsWith('Route-')));}
});
test('legacy arrived door snapshot resolves through production settle without demand dialog; done receipt stays unchanged',()=>{
 const fixture=require(path.join(root,'tests/fixtures/m1-before-food-mix.json'));
 for(const state of ['arrived','done']){const b=OrderBook.restore(fixture.data,JSON.stringify(fixture.states[state].snapshot),()=>.1,()=> '2026-10-30'),before=JSON.stringify(b.active.receipt),h=init(b);if(state==='arrived'){assert.equal(b.mode,'arrived');assert.equal(b.active.offer.demand,'door');assert.equal(h.sample.act(()=>b.settle(true)),true);h.sample.renderPanel();}else{h.sample.openReceipt();assert.equal(JSON.stringify(b.active.receipt),before);}assert.equal(b.mode,'done');assert.notEqual(h.sample.modalKind,'demand');assert.equal(h.sample.modalKind,'receipt');const text=h.text(h.sample.modal);console.log('RECEIPT',state,JSON.stringify(text));assert.equal(text.filter(s=>s.includes('经验')).length,1);assert.ok(!text.some(s=>/倍率|余额|基础价/.test(s)));}
});
test('ui cancellation visibility follows actual phase and duplicate action does not advance',()=>{
 const b=book(),h=init(b);assert.ok(h.find('Button-取消订单'));h.press('去取餐');assert.ok(h.find('Button-取消订单'));h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');assert.ok(h.find('Button-取消订单'));const pickup=h.find('Button-取餐');h.click(pickup);h.click(pickup);assert.equal(b.active.handoff.phase,'picking');assert.ok(!h.find('Button-取消订单'));h.sample.update(2);assert.equal(b.active.handoff.phase,'awaitDeliveryStart');assert.ok(!h.find('Button-取消订单'));h.press('去送餐');assert.equal(b.active.handoff.phase,'toDropoff');assert.ok(!h.find('Button-取消订单'));h.sample.update(999);assert.equal(b.mode,'done');assert.ok(!h.find('Button-取消订单'));
});
test('ui extreme text retains real labels, increases scroll range, and fixed actions remain reachable',()=>{
 const b=book(),h=init(b),o=b.active.offer;o.buyerNote='备注长文'.repeat(35);b.data.pois[o.from].name='长取餐地点'.repeat(16);b.data.pois[o.to].name='长送达地点'.repeat(16);h.setFrame({width:360,height:560});h.setSafeArea(height=>({x:10,y:28,width:700,height:height-64}));h.sample.rebuildLayout();
 const details=h.find('OrderDetails'),viewport=details.parent,height=details.getComponent(h.UITransform).height,vh=viewport.getComponent(h.UITransform).height;assert.ok(height>vh,'long content must scroll');const text=h.text(details);assert.ok(text.some(s=>s.includes(o.buyerNote)));assert.ok(text.some(s=>s.includes(b.data.pois[o.from].name)));assert.ok(text.some(s=>s.includes(b.data.pois[o.to].name)));
 const routes=h.walk(details).filter(n=>n.name.startsWith('Route-'));assert.equal(routes.length,b.active.routes.length);for(const r of routes)assert.ok(-(r.y-r.getComponent(h.UITransform).height/2)<=height+1,'last route fits in scroll content');const main=h.find('Button-去取餐'),cancel=h.find('Button-取消订单');assert.ok(h.bounds(viewport).bottom>=h.bounds(main).top);assert.ok(h.bounds(main).bottom>=h.bounds(h.find('DeliverySheet')).bottom);assert.ok(cancel);
});
test('ui same order reaccepted after await-pickup cancel issues a fresh zero-distance arrival event',()=>{
 const b=book(),h=init(b),id=b.active.offer.id;h.press('去取餐');h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');assert.equal(h.sample.lastHandoffEvent,id+'/awaitPickup');h.press('取消订单');assert.equal(b.mode,'idle');assert.ok(b.list().some(p=>p.offer.id===id));
 h.sample.accept(id);assert.equal(h.sample.lastHandoffEvent,'','new acceptance must reset prior presentation identity');assert.equal(b.active.offer.id,id);assert.equal(b.active.handoff.phase,'planning');const root=h.sample.root;h.press('去取餐');assert.equal(b.active.handoff.phase,'awaitPickup');assert.ok(h.find('Button-取餐'));assert.notEqual(h.sample.root,root,'new attempt must present a new arrival event even with same id and phase');
});
