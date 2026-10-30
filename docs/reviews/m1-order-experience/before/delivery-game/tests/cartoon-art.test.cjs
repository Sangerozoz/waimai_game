const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
function harness(){
 const requests=[];
 class Node{static EventType={NODE_DESTROYED:'node-destroyed'};constructor(name){Object.assign(this,{name,active:true,alive:true,queued:false,children:[],components:new Map(),events:new Map()});}addChild(n){this.children.push(n);n.parent=this;}setPosition(x,y){Object.assign(this,{x,y});}setScale(x,y){this.scaleX=x;this.scaleY=y;}addComponent(T){const c=new T();this.components.set(T,c);c.node=this;return c;}getComponent(T){return this.components.get(T);}on(type,callback){this.events.set(type,callback);}destroy(){this.events.get(Node.EventType.NODE_DESTROYED)?.();this.alive=false;}get activeInHierarchy(){return this.active&&(!this.parent||this.parent.activeInHierarchy);} }
 class UITransform{setContentSize(width,height){Object.assign(this,{width,height});}}
 class Color{constructor(r,g,b,a){Object.assign(this,{r,g,b,a});}}
 class Graphics{clear(){}roundRect(){}fill(){}stroke(){}circle(){}moveTo(){}lineTo(){}bezierCurveTo(){}bezierCurveTo(){}close(){}}
 class Sprite{static SizeMode={CUSTOM:0};static Type={SLICED:1};}class SpriteFrame{addRef(){this.refs=(this.refs||0)+1;return this;}decRef(){this.refs--;}}class Texture2D{constructor(){this.width=1280;this.height=1280;}addRef(){return this;}}
 const cc={Node,UITransform,Color,Graphics,Sprite,SpriteFrame,Texture2D,Layers:{Enum:{UI_2D:1}},isValid:(n,strict)=>n.alive&&(!strict||!n.queued),Rect:class{constructor(x,y,width,height){Object.assign(this,{x,y,width,height});}},Size:class{constructor(width,height){Object.assign(this,{width,height});}},resources:{load(url,T,callback){requests.push({url,callback});}}};
 const filename=path.join(__dirname,'../assets/scripts/map-sample/CartoonArt.ts');
 assert.ok(fs.existsSync(filename),'CartoonArt loader is required');
 const compiled=ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
 const scope={exports:{},require:id=>{assert.equal(id,'cc');return cc;}};vm.runInNewContext(compiled,scope);
 const uiFilename=path.join(__dirname,'../assets/scripts/map-sample/SampleUI.ts');
 const uiCompiled=ts.transpileModule(fs.readFileSync(uiFilename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
 const uiScope={exports:{},require:id=>id==='cc'?cc:id==='./CartoonArt'?scope.exports:assert.fail('unexpected dependency '+id)};
 vm.runInNewContext(uiCompiled,uiScope);
 return {...scope.exports,requests,node:()=>new Node('parent'),texture:()=>new Texture2D(),Sprite,UITransform,Graphics,ui:uiScope.exports};
}
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
test('one atlas request shares immutable frames and fits the manifest crop into each requested box',async()=>{
 const h=harness(),parent=h.node(),fallback=h.node(),a=h.cartoonArt(parent,'avatar',0,0,100,100,fallback),b=h.cartoonArt(parent,'coin',0,0,50,40);
 assert.equal(h.requests.length,1);assert.equal(h.requests[0].url,'map-sample/cartoon/ui-icons/texture');
 h.requests[0].callback(null,h.texture());await flush();
 const frame=a.getComponent(h.Sprite).spriteFrame;assert.deepEqual([frame.rect.x,frame.rect.y,frame.rect.width,frame.rect.height],[2,120,327,344]);
 const size=a.getComponent(h.UITransform);assert.ok(Math.abs(size.height-100)<1e-8);assert.ok(Math.abs(size.width-100*327/344)<1e-8);assert.equal(fallback.active,false);assert.equal(b.active,true);
 const again=await h.loadCartoonFrame('avatar');assert.equal(again,frame);assert.equal(h.requests.length,1);
});
test('failed atlas remains readable through its fallback and a later opening retries',async()=>{
 const h=harness(),parent=h.node(),fallback=h.node(),first=h.cartoonArt(parent,'vehicle',0,0,80,80,fallback);
 h.requests[0].callback(new Error('offline'));await flush();assert.equal(first.active,false);assert.equal(fallback.active,true);
 h.cartoonArt(parent,'vehicle',0,0,80,80);assert.equal(h.requests.length,2);h.requests[1].callback(null,h.texture());await flush();assert.equal(parent.children[1].active,true);
});
test('closed, queued-destroyed and destroyed-picture views never reactivate on a late response',async()=>{
 for(const state of ['closed','queued','picture']){
  const h=harness(),parent=h.node(),fallback=h.node(),picture=h.cartoonArt(parent,'map',0,0,80,80,fallback);
  if(state==='closed')parent.active=false;else if(state==='queued')parent.queued=true;else picture.alive=false;
  h.requests[0].callback(null,h.texture());await flush();assert.equal(picture.active,false);assert.equal(picture.getComponent(h.Sprite).spriteFrame,undefined);assert.equal(fallback.active,true);
 }
});
test('normalized vehicle crops scale with imported texture size and unknown keys never load',async()=>{
 const h=harness(),pending=h.loadCartoonFrame('top-d-plus'),texture=h.texture();texture.width=640;texture.height=640;
 h.requests[0].callback(null,texture);const frame=await pending;
 assert.deepEqual([frame.rect.x,frame.rect.y,frame.rect.width,frame.rect.height],[380,316,190,304]);
 await assert.rejects(h.loadCartoonFrame('missing'),/Unknown cartoon art/);assert.equal(h.requests.length,1);
});
test('generated locator retains native fallback on atlas failure',async()=>{const h=harness(),parent=h.node(),picture=h.ui.icon(parent,'target',0,0,h.ui.C.ink,1);const fallback=parent.children.find(n=>n.getComponent(h.Graphics));assert.equal(h.requests.length,1);assert.equal(picture.active,false);h.requests[0].callback(new Error('offline'));await flush();assert.equal(fallback.active,true);assert.equal(picture.active,false);});
