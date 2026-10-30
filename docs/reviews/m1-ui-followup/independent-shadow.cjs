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
test('followup shadow: real CityMap owns one shadow below vehicle and tracks position, angle, zoom',()=>{
 const h=harness(),ui=h.load('./SampleUI');
 const cc={Node:h.Node,Graphics:h.Graphics,Label:h.Label,UITransform:h.UITransform,Mask:class{static Type={GRAPHICS_RECT:1};}};
 const file=path.join(root,'assets/scripts/map-sample/CityMap.ts'),compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES5,module:ts.ModuleKind.CommonJS}}).outputText;
 const scope={exports:{},require:id=>id==='cc'?cc:id==='./SampleUI'?ui:id==='./MapVehicle'?{MapVehicle:class{setTier(){}}}:{}};vm.runInNewContext(compiled,scope,{filename:file});
 const {CityMap}=scope.exports;

 // Only unrelated geometry/vehicle drawing is stubbed; constructor attribution and tap stay real.
 CityMap.prototype.drawCity=function(){};CityMap.prototype.sync=function(){};CityMap.prototype.pin=function(){return ui.item(h.root,'Pin');};CityMap.prototype.drawRider=function(){};
 let calls=0;const city=new CityMap(h.root,{nodes:[],labels:[],pois:[]},748,()=>calls++),n=city.viewport.getChildByName('MapAttribution'),v=n.getChildByName('PressVisual');
 assert.equal(n.children.length,1);assert.equal(v.children.length,1);assert.equal(v.children[0].getComponent(h.Label).string,'© OpenStreetMap contributors');assert.equal(n.getComponent(h.Label),undefined);
 const overlay=city.overlay,shadow=overlay.getChildByName('VehicleGroundShadow'),rider=overlay.getChildByName('DeliveryRider');
 assert.ok(overlay.children.indexOf(shadow)<overlay.children.indexOf(rider));
 for(const scale of [.6,2,6])for(const angle of [0,90])for(const tier of [1,2,1]){
  city.scale=scale;city.offset=[13,-27];city.riderPoint=[100,200];city.riderAngle=angle;city.setVehicle(tier);city.syncOverlay();
  assert.equal(shadow.x,rider.x+3);assert.equal(shadow.y,rider.y-8);assert.equal(rider.angle,angle);assert.equal(overlay.children.filter(n=>n.name==='VehicleGroundShadow').length,1);
 }
 const size=n.getComponent(h.UITransform),w=size.width,ev={getID:()=>1,getUILocation:()=>({x:0,y:0})};n.events.get('start')(ev);assert.equal(v.scaleX,.96);assert.equal(n.scaleX??1,1);assert.equal(size.width,w);n.events.get('end')(ev);assert.equal(calls,1);n.events.get('end')(ev);assert.equal(calls,1);n.events.get('start')(ev);n.events.get('cancel')(ev);assert.equal(v.scaleX,1);n.events.get('end')(ev);assert.equal(calls,1);
});
