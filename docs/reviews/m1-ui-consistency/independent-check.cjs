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
test('consistency independent loaded avatar and rating use 12 CSS pixels at actual fit dimensions',()=>{
 for(const frame of [{width:720,height:1280},{width:360,height:560}]){
  const h=harness();h.setFrame(frame);h.setSafeArea(height=>({x:10,y:28,width:700,height:height-64}));h.sample.rebuildLayout();
  const avatar=h.walk(h.sample.root).find(n=>n.name==='CartoonArt-avatar');avatar.getComponent(h.UITransform).setContentSize(92*327/344,92);h.sample.layoutPlayerHeader();
  const rating=h.walk(h.sample.root).find(n=>n.name==='RatingPill'),scale=Math.min(frame.width/720,frame.height/h.height());
  assert.ok(Math.abs((h.bounds(avatar).left-(-350))*scale-12)<.01);assert.ok(Math.abs((350-h.bounds(rating).right)*scale-12)<.01);
 }
});
test('consistency independent station visible pre-load and post-load margin must both equal 12 CSS pixels',()=>{
 const h=harness();h.setFrame({width:720,height:1280});h.sample.rebuildLayout();const station=h.walk(h.sample.root).find(n=>n.name==='StationEntry'),art=station.getChildByName('CartoonArt-station'),text=station.children.find(n=>n.getComponent(h.Label));
 art.active=false;const before=360-h.bounds(text).right;
 art.getComponent(h.UITransform).setContentSize(108*321/334,108);art.active=true;h.sample.positionStation(station,station.y);const after=360-Math.max(h.bounds(art).right,h.bounds(text).right);
 assert.ok(Math.abs(after-12)<.01);assert.ok(Math.abs(before-12)<=1,'preload visible margin is '+before+'px; loaded margin is '+after+'px');
});
test('consistency independent locator dimensions grow 1.5 and visual stays inside stable hit root',()=>{
 const h=harness(),n=h.walk(h.sample.root).find(n=>n.name==='FollowRider'),art=h.walk(n).find(n=>n.name==='CartoonArt-target'),size=art.getComponent(h.UITransform),hit=n.getComponent(h.UITransform);assert.ok(Math.abs(size.width/(48*1.4)-1.5)<1e-10);assert.ok(Math.abs(size.height/(48*1.4)-1.5)<1e-10);assert.ok(hit.width>=size.width&&hit.height>=size.height);
 const e={getID:()=>1,getUILocation:()=>({x:0,y:0})};n.events.get('start')(e);assert.equal(n.scaleX??1,1);assert.equal(n.getChildByName('PressVisual').scaleX,.96);n.events.get('move')({...e,getUILocation:()=>({x:8,y:0})});n.events.get('end')(e);assert.equal(h.counts().located,0);
});
`;
const m=new Module(filename,module);m.filename=filename;m.paths=Module._nodeModulePaths(path.dirname(filename));m._compile(source,filename);
