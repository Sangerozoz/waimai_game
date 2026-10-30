// Minimal closure checks; production and developer tests stay read only.
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module'),vm=require('node:vm');
const {test}=require('node:test'),assert=require('node:assert/strict');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const root=path.resolve(__dirname,'../../../delivery-game'),filename=path.join(root,'tests/map-hud.test.cjs');
let fixture=fs.readFileSync(filename,'utf8').split("test('header groups")[0];
fixture=fixture.replace('addChild(n){this.children.push(n);n.parent=this;}', 'addChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}');
// Reproduce the old compilation boundary: string spread downlevels without an iterator.
fixture=fixture.replaceAll('ts.ScriptTarget.ES2020','ts.ScriptTarget.ES5');
fixture=fixture.replace('Component:class{}','Component:function(){}');
fixture+='\nmodule.exports={harness};';
const mod=new Module(filename,module);mod.filename=filename;mod.paths=Module._nodeModulePaths(path.dirname(filename));mod._compile(fixture,filename);
const harness=mod.exports.harness;
test('F1: ES5 compilation preserves per-character default balance measurement at short viewport',()=>{
 const h=harness();h.setFrame({width:360,height:560});h.sample.rebuildLayout();
 const money=h.sample.money,size=money.node.getComponent(h.UITransform),units=Array.from(money.string).length*.66;
 assert.equal(money.string,'100.00');assert.ok(money.fontSize*units<=size.width,'default balance fits one estimated line');assert.ok(size.height>=money.lineHeight);assert.ok(money.fontSize<50,'must not mistake six characters for one');
});
test('F1: ES5 compilation keeps full long balance with safe insets and enough line height',()=>{
 const h=harness();h.setFrame({width:360,height:560});h.setSafeArea(height=>({x:10,y:28,width:700,height:height-64}));h.sample.book.player.cashCents=12345678900;h.sample.rebuildLayout();
 const money=h.sample.money,size=money.node.getComponent(h.UITransform);assert.equal(money.string,'123456789.00');assert.ok(size.height>=2*money.lineHeight);const b=h.bounds(money.node),header=h.bounds(h.sample.profileCard);assert.ok(b.top<=header.top&&b.bottom>=header.bottom);
});
test('F2: actual CityMap constructor puts its attribution Label in PressVisual and preserves click root',()=>{
 const h=harness(),ui=h.load('./SampleUI');
 const cc={Node:h.Node,Graphics:h.Graphics,Label:h.Label,UITransform:h.UITransform,Mask:class{static Type={GRAPHICS_RECT:1};}};
 const file=path.join(root,'assets/scripts/map-sample/CityMap.ts'),compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES5,module:ts.ModuleKind.CommonJS}}).outputText;
 const scope={exports:{},require:id=>id==='cc'?cc:id==='./SampleUI'?ui:id==='./MapVehicle'?{MapVehicle:class{}}:{}};vm.runInNewContext(compiled,scope,{filename:file});
 const {CityMap}=scope.exports;
 // Only unrelated geometry/vehicle drawing is stubbed; constructor attribution and tap stay real.
 CityMap.prototype.drawCity=function(){};CityMap.prototype.sync=function(){};CityMap.prototype.pin=function(){return ui.item(h.root,'Pin');};CityMap.prototype.drawRider=function(){};
 let calls=0;const city=new CityMap(h.root,{nodes:[],labels:[],pois:[]},748,()=>calls++),n=city.viewport.getChildByName('MapAttribution'),v=n.getChildByName('PressVisual');
 assert.equal(n.children.length,1);assert.equal(v.children.length,1);assert.equal(v.children[0].getComponent(h.Label).string,'© OpenStreetMap contributors');assert.equal(n.getComponent(h.Label),undefined);
 const size=n.getComponent(h.UITransform),w=size.width,ev={getID:()=>1,getUILocation:()=>({x:0,y:0})};n.events.get('start')(ev);assert.equal(v.scaleX,.96);assert.equal(n.scaleX??1,1);assert.equal(size.width,w);n.events.get('end')(ev);assert.equal(calls,1);n.events.get('end')(ev);assert.equal(calls,1);n.events.get('start')(ev);n.events.get('cancel')(ev);assert.equal(v.scaleX,1);n.events.get('end')(ev);assert.equal(calls,1);
});
