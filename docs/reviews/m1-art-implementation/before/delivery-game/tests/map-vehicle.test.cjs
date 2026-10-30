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
 class Texture2D {constructor(id){this.id=id;this.width=500;this.height=800;}addRef(){return this;}}
 function node(name='rider'){return {name,alive:true,active:true,children:[],angle:0,addComponent(Type){const c=new Type();c.node=this;this.component=c;return c;}};}
 const cc={Sprite,SpriteFrame,Texture2D,isValid:n=>n.alive,Rect:class{constructor(x,y,width,height){Object.assign(this,{x,y,width,height});}},Size:class{constructor(width,height){Object.assign(this,{width,height});}},resources:{load(url,type,callback){requests.push({url,callback});}}};
 const modules={};
 function load(name){
  if(modules[name])return modules[name];
  const file=path.join(root,'assets/scripts/map-sample',name+'.ts');
  assert.ok(fs.existsSync(file),name+' implementation is required');
  const compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2015,module:ts.ModuleKind.CommonJS}}).outputText;
  const scope={exports:{},require(id){
   if(id==='cc')return cc;
   if(id==='./SampleUI')return {item(parent,name,x,y,width,height){const n=node(name);Object.assign(n,{width,height});parent.children.push(n);return n;}};
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
 assert.equal(picture.width/picture.height,500/800);
 for(const [road,want] of [[0,[1,0]],[90,[0,1]],[180,[-1,0]],[-90,[0,-1]]]){
  const front=(90+picture.angle+road)*Math.PI/180;
  assert.ok(Math.abs(Math.cos(front)-want[0])<1e-9&&Math.abs(Math.sin(front)-want[1])<1e-9);
 }
});

test('a late D image cannot overwrite the newly selected D+ vehicle',async()=>{
 const h=harness(),{MapVehicle}=h.load('MapVehicle'),parent=h.node(),fallback={enabled:true};
 const view=new MapVehicle(parent,fallback);view.setTier(1);view.setTier(1);assert.equal(h.requests.length,1);
 view.setTier(2);assert.equal(h.requests.length,2);
 h.requests[1].callback(null,h.texture('D+'));await flush();
 assert.equal(parent.children[0].component.spriteFrame.texture.id,'D+');
 h.requests[0].callback(null,h.texture('D'));await flush();
 assert.equal(parent.children[0].component.spriteFrame.texture.id,'D+');
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
