const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {createHash}=require('node:crypto');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const root=path.join(__dirname,'..');

// Replace only the Cocos rendering/resource boundary; run the actual loader and grade mapping.
function harness(){
 const requests=[];
 class Sprite {static SizeMode={CUSTOM:0};}
 class SpriteFrame {addRef(){return this;}}
 class Texture2D {constructor(id){this.id=id;this.width=1280;this.height=1280;}addRef(){return this;}}
 class Node {constructor(name='rider'){Object.assign(this,{name,alive:true,active:true,children:[],components:new Map(),angle:0});}addChild(n){this.children.push(n);n.parent=this;}setPosition(x,y){Object.assign(this,{x,y});}addComponent(Type){const c=new Type();c.node=this;this.components.set(Type,c);this.component=c;return c;}getComponent(Type){return this.components.get(Type);}get activeInHierarchy(){return this.active&&(!this.parent||this.parent.activeInHierarchy);}}
 function node(name='rider'){return new Node(name);}
 class UITransform{setContentSize(width,height){Object.assign(this,{width,height});}}
 const cc={Node,UITransform,Sprite,SpriteFrame,Texture2D,Layers:{Enum:{UI_2D:1}},isValid:n=>n.alive,Rect:class{constructor(x,y,width,height){Object.assign(this,{x,y,width,height});}},Size:class{constructor(width,height){Object.assign(this,{width,height});}},resources:{load(url,type,callback){requests.push({url,callback});}}};
 const modules={};
 function load(name){
  if(modules[name])return modules[name];
  const file=path.join(root,'assets/scripts/map-sample',name+'.ts');
  assert.ok(fs.existsSync(file),name+' implementation is required');
  const compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2015,module:ts.ModuleKind.CommonJS}}).outputText;
  const scope={exports:{},require(id){
   if(id==='cc')return cc;
   if(id==='./SampleUI')return {item(parent,name,x,y,width,height){const n=node(name);parent.addChild(n);n.setPosition(x,y);n.addComponent(UITransform).setContentSize(width,height);return n;}};
   return load(id.replace('./',''));
  }};
  vm.runInNewContext(compiled,scope,{filename:name+'.js'});modules[name]=scope.exports;return scope.exports;
 }
 return {load,requests,node,texture:id=>new Texture2D(id)};
}
const flush=async()=>{await Promise.resolve();await Promise.resolve();await Promise.resolve();};

test('all ten vehicle grades use the corresponding supplied top-view image',()=>{
 const h=harness(),{MAP_VEHICLES,vehicleArtForTier}=h.load('VehicleCatalog');
 const names=['旧电动车','翻新电动车','品牌电动车','长续航电动车','大箱摩托车','运动摩托车','豪华摩托车','限量豪华摩托车','黄金限量摩托车','至尊飞行摩托车 · 隐藏'];
 assert.equal(MAP_VEHICLES.length,10);
 names.forEach((name,i)=>{
  const art=vehicleArtForTier(i+1);assert.equal(art.name,name);
  const imported=fs.readFileSync(path.join(root,'assets/resources',art.resource+'.png'));
  const source=require('../../docs/reviews/map-vehicle-art/assets.json').find(record=>record.tier===i+1);
  assert.equal(source.name,name);assert.equal(source.resource,art.resource);
  assert.equal(createHash('sha256').update(imported).digest('hex'),source.sha256);
 });
 assert.equal(vehicleArtForTier(0).tier,1);assert.equal(vehicleArtForTier(99).tier,1);
});

test('the top-view front follows east, north, west and south road headings',async()=>{
 const h=harness(),{MapVehicle}=h.load('MapVehicle'),parent=h.node(),fallback={enabled:true};
 const view=new MapVehicle(parent,fallback);view.setTier(1);
 h.requests[0].callback(null,h.texture('D'));await flush();
 const picture=parent.children[0];assert.equal(fallback.enabled,false);assert.equal(picture.active,true);
 assert.equal(h.requests[0].url,'map-sample/cartoon/vehicle-sheet/texture');
 assert.equal(picture.component.spriteFrame.rect.width/picture.component.spriteFrame.rect.height,380/608);
 for(const [road,want] of [[0,[1,0]],[90,[0,1]],[180,[-1,0]],[-90,[0,-1]]]){
  const front=(90+picture.angle+road)*Math.PI/180;
  assert.ok(Math.abs(Math.cos(front)-want[0])<1e-9&&Math.abs(Math.sin(front)-want[1])<1e-9);
 }
});

test('changing from D to D+ before the shared atlas resolves displays D+ art',async()=>{
 const h=harness(),{MapVehicle}=h.load('MapVehicle'),parent=h.node(),fallback={enabled:true};
 const view=new MapVehicle(parent,fallback);view.setTier(1);view.setTier(1);assert.equal(h.requests.length,1);
 view.setTier(2);assert.equal(h.requests.length,1);
 h.requests[0].callback(null,h.texture('shared'));await flush();
 assert.deepEqual([parent.children[0].component.spriteFrame.rect.x,parent.children[0].component.spriteFrame.rect.y],[760,632]);
});

test('a layout rebuild reuses the image and discards callbacks for the destroyed map',async()=>{
 const h=harness(),{MapVehicle}=h.load('MapVehicle'),old=h.node(),next=h.node();
 new MapVehicle(old,{enabled:true}).setTier(2);old.alive=false;
 new MapVehicle(next,{enabled:true}).setTier(2);assert.equal(h.requests.length,1);
 h.requests[0].callback(null,h.texture('D+'));await flush();
 assert.equal(old.children[0].component.spriteFrame,undefined);
 assert.equal(next.children[0].component.spriteFrame.texture.id,'D+');
});

test('a failed vehicle image keeps the fallback and can be retried',async()=>{
 const h=harness(),{MapVehicle}=h.load('MapVehicle'),parent=h.node(),fallback={enabled:true};
 const view=new MapVehicle(parent,fallback);view.setTier(1);
 h.requests[0].callback(new Error('missing texture'));await flush();
 assert.equal(fallback.enabled,true);assert.equal(parent.children[0].active,false);
 view.setTier(1);assert.equal(h.requests.length,2);
 h.requests[1].callback(null,h.texture('D'));await flush();assert.equal(fallback.enabled,false);
});

test('side art caches loads and ignores a closed garage while preserving its fallback on failure',async()=>{
 const h=harness(),{vehicleSideArt}=h.load('VehicleSideArt'),old=h.node(),next=h.node(),fallback=h.node();
 vehicleSideArt(old,1,0,0,400,240,fallback);old.active=false;
 vehicleSideArt(next,1,0,0,400,240,h.node());assert.equal(h.requests.length,1);assert.equal(h.requests[0].url,'map-sample/cartoon/vehicle-sheet/texture');
 h.requests[0].callback(null,h.texture('D'));await flush();assert.equal(old.children[0].component.spriteFrame,undefined);assert.equal(next.children[0].component.spriteFrame.texture.id,'D');
 const failed=h.node(),hint=h.node();vehicleSideArt(failed,2,0,0,400,240,hint);await flush();assert.equal(hint.active,false,'the shared successful atlas supplies D+ without another request');
 assert.equal(h.requests.length,1);
});
