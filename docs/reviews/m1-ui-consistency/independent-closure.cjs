const fs=require('node:fs'),path=require('node:path'),Module=require('node:module'),assert=require('node:assert/strict'),{test}=require('node:test');
const root=path.resolve(__dirname,'../../../delivery-game'),file=path.join(root,'tests/map-hud.test.cjs');
let src=fs.readFileSync(file,'utf8').split("test('header groups")[0];
src=src.replace("static EventType={TOUCH_START:'start'", "static EventType={SIZE_CHANGED:'size',ACTIVE_CHANGED:'activeChanged',TOUCH_START:'start'");
src=src.replace('addChild(n){this.children.push(n);n.parent=this;}', 'get active(){return this._active;}set active(value){if(this._active===value)return;this._active=value;this.events?.get("activeChanged")?.();}get activeInHierarchy(){return this.active&&(!this.parent||this.parent.activeInHierarchy);}addChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}');
src=src.replace('setContentSize(width,height){Object.assign(this,{width,height});}', 'setContentSize(width,height){const changed=this.width!==width||this.height!==height;Object.assign(this,{width,height});if(changed)this.node?.events.get("size")?.();}');
src=src.replace('const cc={Tween:', 'const requests=[];const cc={Texture2D:class{},SpriteFrame:class{addRef(){}},Rect:class{constructor(x,y,width,height){Object.assign(this,{x,y,width,height});}},Size:class{constructor(width,height){Object.assign(this,{width,height});}},Tween:');
src=src.replace('resources:{load(){}}', 'resources:{load(url,type,callback){requests.push({url,callback});}}');
const a=src.indexOf("if(id==='./CartoonArt')return {"),b=src.indexOf(";if(['./PresentationLayout'",a);assert.ok(a>0&&b>a);src=src.slice(0,a)+"if(id==='./CartoonArt')return load(id)"+src.slice(b);
src=src.replace('return {sample,root,panel,','return {requests,sample,root,panel,');src+='\nmodule.exports={harness};';
const mod=new Module(file,module);mod.filename=file;mod.paths=Module._nodeModulePaths(path.dirname(file));mod._compile(src,file);const {harness}=mod.exports;
const flush=async()=>{for(let i=0;i<10;i++)await Promise.resolve();};
function margin(h){const station=h.walk(h.sample.root).find(n=>n.name==='StationEntry'),art=station.getChildByName('CartoonArt-station'),label=station.children.find(n=>n.getComponent(h.Label));const right=Math.max(h.bounds(label).right,art.active?h.bounds(art).right:-Infinity);const scale=Math.min(360/720,560/h.height());return(350-right)*scale;}
test('closure F1: real loader triggers resize/active listeners; before, failure, success, save and rebuild keep visible margin',async()=>{
 for(const failed of [false,true]){
  const h=harness();h.setFrame({width:360,height:560});h.setSafeArea(height=>({x:10,y:28,width:700,height:height-64}));h.sample.rebuildLayout();assert.ok(Math.abs(margin(h)-12)<.01);
  h.requests[0].callback(failed?Error('isolated offline'):null,{width:1280,height:1280,addRef(){}});await flush();assert.ok(Math.abs(margin(h)-12)<.01);
  h.sample.updatePlayerHeader();assert.ok(Math.abs(margin(h)-12)<.01);h.sample.save();assert.ok(Math.abs(margin(h)-12)<.01);h.sample.rebuildLayout();await flush();assert.ok(Math.abs(margin(h)-12)<.01);
 }
});
function checkDisabled(h,n){const g=n.getChildByName('Surface').getComponent(h.Graphics);assert.ok(g.fills.some(f=>f.color.r===197&&f.color.g===204&&f.color.b===213),'actual drawing includes gray face');assert.ok(!g.fills.some(f=>f.color.r===40&&f.color.g===120&&f.color.b===235),'no blue face remains');assert.equal(n.events.get('start'),undefined);assert.equal(n.events.get('end'),undefined);}
test('closure F2: all three production entry points draw gray disabled faces and register no touch',()=>{
 const h=harness(),ui=h.load('./SampleUI');let calls=0;
 checkDisabled(h,ui.button(h.root,'disabled',0,0,200,80,()=>calls++,ui.C.light,ui.C.ink,false));
 checkDisabled(h,h.sample.action(h.root,'disabled-map',0,0,200,()=>calls++,ui.C.light,false));
 const {OrderPhone}=h.load('./OrderPhone'),phone=Object.create(OrderPhone.prototype);phone.screenHeight=1280;
 phone.action(h.root,'disabled-phone',0,0,200,80,()=>calls++,ui.C.light,false);checkDisabled(h,h.root.getChildByName('Button-disabled-phone'));assert.equal(calls,0);
});
test('closure F2: production phone with no free refreshes draws disabled gray without refresh callback',()=>{
 const h=harness(),{OrderPhone}=h.load('./OrderPhone');let calls=0;
 const book={isFirstDelivery:false,refreshesLeft:0,list:()=>[]};const phone=new OrderPhone(h.root,book,1280,()=>{},()=>{},()=>calls++);const n=h.walk(phone.node).find(n=>n.name==='Button-广告未开放');checkDisabled(h,n);h.click(n);assert.equal(calls,0);
});
