// Product-only adapter tests. Runs actual loader code with a narrow fake cc/network
// and fake wall timers; does not launch Cocos, touch a game save, or prove rendering.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const editor=process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts=require(path.join(editor,'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const filename=path.join(__dirname,'../assets/scripts/map-sample/UIArtResources.ts');
const source=ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
const plain=x=>JSON.parse(JSON.stringify(x));
function harness(load,any){
 const timers=new Map(),logs=[],calls=[];let id=0,now=0;
 class Texture2D{constructor(width=100,height=200){this.width=width;this.height=height;this.refs=0;}addRef(){this.refs++;return this;}}
 class JsonAsset{constructor(json){this.json=json;}}
 const api={Texture2D,JsonAsset};
 const cc={Texture2D,JsonAsset,resources:{name:'resources',load(resource,type,done){calls.push({kind:'load',resource});load(resource,type,done,api,calls);}},assetManager:{loadAny(request,options,done){calls.push({kind:'any',request,options});if(!any)throw Error('unexpected loadAny');any(request,options,done,api,calls);}}};
 const scope={exports:{},require:name=>{assert.equal(name,'cc');return cc;},console:{warn:(...x)=>logs.push(x),info:(...x)=>logs.push(x)},Date:class extends Date{static now(){return now;}},setTimeout(fn,ms){const key=++id;timers.set(key,{at:now+ms,fn});return key;},clearTimeout(key){timers.delete(key);}};
 vm.runInNewContext(source,scope,{filename});
 async function settle(p){
  let complete=false,value,error;p.then(v=>{complete=true;value=v;},e=>{complete=true;error=e;});
  for(let guard=0;guard<1000;guard++){
   for(let i=0;i<16;i++)await Promise.resolve();
   if(complete){if(error)throw error;return value;}
   const next=[...timers.entries()].sort((a,b)=>a[1].at-b[1].at||a[0]-b[0])[0];
   if(!next)throw Error('test harness: unresolved Promise without a scheduled timer');
   timers.delete(next[0]);now=next[1].at;next[1].fn();
  }
  throw Error('test harness: timer bound exceeded');
 }
 return {api,calls,logs,settle,advance(ms){now+=ms;},get now(){return now;},...scope.exports};
}
function pack(resource='product/source',derived='ui-v2/web/source/crop'){
 return {version:1,sources:{[resource]:{size:[1000,500],regions:{'10,20,100,200':{resource:derived,size:[50,100]}}}}};
}
test('native concurrent requests share one load and retain once',async()=>{
 let count=0,texture;const h=harness((p,t,done,{Texture2D})=>{count++;texture=new Texture2D();done(null,texture);});
 const a=h.loadArtTexture('product/a'),b=h.loadArtTexture('product/a');assert.equal(a,b);
 assert.equal(await h.settle(a),texture);assert.equal(await h.settle(b),texture);
 assert.equal(count,1);assert.equal(texture.refs,1);assert.equal(await h.settle(h.loadArtTexture('product/a')),texture);assert.equal(count,1);
});
test('native transient failure retries finitely and retains only successful texture',async()=>{
 let count=0,texture;const h=harness((p,t,done,{Texture2D})=>{count++;if(count<3)done(Error('network'));else{texture=new Texture2D();done(null,texture);}});
 assert.equal(await h.settle(h.loadArtTexture('product/retry')),texture);assert.equal(count,3);assert.equal(texture.refs,1);
});
test('exhausted native failure evicts rejected Promise for a later request',async()=>{
 let count=0,up=false;const h=harness((p,t,done,{Texture2D})=>{count++;done(up?null:Error('offline'),up?new Texture2D():undefined);});
 await assert.rejects(h.settle(h.loadArtTexture('product/offline')),/offline/);assert.equal(count,3);
 up=true;const value=await h.settle(h.loadArtTexture('product/offline'));assert.equal(count,4);assert.equal(value.refs,1);
});
test('no-callback native loads reach a finite timeout and late callbacks cannot retain',async()=>{
 const callbacks=[];const h=harness((p,t,done)=>callbacks.push(done));
 await assert.rejects(h.settle(h.loadArtTexture('product/stall')),/timeout/);assert.equal(callbacks.length,3);assert.equal(h.now,183000);
 const late=new h.api.Texture2D();for(const done of callbacks)done(null,late);await Promise.resolve();assert.equal(late.refs,0);
});
test('JSON failure also evicts rather than poisoning subsequent callers',async()=>{
 let calls=0,up=false;const h=harness((p,t,done,{JsonAsset})=>{calls++;done(up?null:Error('json offline'),up?new JsonAsset({version:1}):undefined);});
 await assert.rejects(h.settle(h.loadArtJson('product/manifest')),/json offline/);assert.equal(calls,3);
 up=true;assert.equal((await h.settle(h.loadArtJson('product/manifest'))).json.version,1);assert.equal(calls,4);
});
test('explicit native-only crop does not request optional web index',async()=>{
 const h=harness((p,t,done,{Texture2D})=>done(null,new Texture2D(100,200)));
 const value=await h.settle(h.loadArtRegion('product/native',[.1,.2,.5,.5],{normalized:true,web:false}));
 assert.deepEqual(plain(value.rect),[10,40,50,100]);assert.equal(value.retryWeb,false);assert.equal(h.calls.filter(x=>x.kind==='any').length,0);
});
test('valid derived region keeps source identity and scales slicing insets',async()=>{
 const h=harness(()=>{throw Error('unexpected original fallback');},(request,options,done,{JsonAsset,Texture2D})=>done(null,request.type===JsonAsset?new JsonAsset(pack()):new Texture2D(50,100)));
 const value=await h.settle(h.loadArtRegion('product/source',[10,20,100,200],{inset:{left:10,right:20,top:30,bottom:40}}));
 assert.deepEqual(plain(value.rect),[0,0,50,100]);assert.deepEqual(plain(value.sourceRect),[10,20,100,200]);
 assert.deepEqual(plain(value.inset),{left:5,right:10,top:15,bottom:20});assert.equal(value.retryWeb,false);assert.equal(value.texture.refs,1);
 assert.ok(h.calls.every(x=>x.kind==='any'&&x.options.reloadAsset===true));
});
test('normalized request maps to the same canonical derived crop',async()=>{
 const h=harness(()=>{throw Error('unexpected original');},(request,options,done,{JsonAsset,Texture2D})=>done(null,request.type===JsonAsset?new JsonAsset(pack()):new Texture2D(50,100)));
 const value=await h.settle(h.loadArtRegion('product/source',[.01,.04,.1,.4],{normalized:true}));
 assert.deepEqual(plain(value.sourceRect),[10,20,100,200]);assert.equal(value.retryWeb,false);
});
test('wrong derivative dimensions never become cached success and may later recover',async()=>{
 let valid=false;const rejected=[];const h=harness((p,t,done,{Texture2D})=>done(null,new Texture2D(1000,500)),(request,options,done,{JsonAsset,Texture2D})=>{
  if(request.type===JsonAsset)return done(null,new JsonAsset(pack()));const texture=new Texture2D(valid?50:49,100);if(!valid)rejected.push(texture);done(null,texture);
 });
 const first=await h.settle(h.loadArtRegion('product/source',[10,20,100,200]));assert.equal(first.retryWeb,true);assert.equal(first.texture.width,1000);assert.equal(rejected.length,3);assert.ok(rejected.every(t=>t.refs===0));
 valid=true;const second=await h.settle(h.loadArtRegion('product/source',[10,20,100,200]));assert.equal(second.retryWeb,false);assert.equal(second.texture.width,50);assert.equal(second.texture.refs,1);
});
test('malformed optional index falls back visibly and demand-driven refresh recovers',async()=>{
 let valid=false;const h=harness((p,t,done,{Texture2D})=>done(null,new Texture2D(1000,500)),(request,options,done,{JsonAsset,Texture2D})=>{
  if(request.type===JsonAsset)return done(null,new JsonAsset(valid?pack():pack('product/source','../illegal')));done(null,new Texture2D(50,100));
 });
 const first=await h.settle(h.loadArtRegion('product/source',[10,20,100,200]));assert.equal(first.retryWeb,true);const count=h.calls.filter(x=>x.kind==='any').length;
 h.advance(5000);assert.equal(h.calls.filter(x=>x.kind==='any').length,count);valid=true;
 const second=await h.settle(h.loadArtRegion('product/source',[10,20,100,200]));assert.equal(second.retryWeb,false);
});
test('inconsistent aliased derivative dimensions reject the whole index before retain',async()=>{
 const bad=pack();bad.sources['product/source'].regions['110,20,100,200']={resource:'ui-v2/web/source/crop',size:[51,100]};
 const h=harness((p,t,done,{Texture2D})=>done(null,new Texture2D(1000,500)),(request,options,done,{JsonAsset})=>{assert.equal(request.type,JsonAsset);done(null,new JsonAsset(bad));});
 const value=await h.settle(h.loadArtRegion('product/source',[10,20,100,200]));assert.equal(value.retryWeb,true);assert.equal(h.calls.filter(x=>x.kind==='any').length,1);
});
test('no-callback optional index times out promptly into original art',async()=>{
 const h=harness((p,t,done,{Texture2D})=>done(null,new Texture2D(1000,500)),()=>{});
 const value=await h.settle(h.loadArtRegion('product/source',[10,20,100,200]));assert.equal(value.retryWeb,true);assert.equal(h.now,4000);
});
test('out-of-bounds native crop rejects while a valid later crop remains usable',async()=>{
 const h=harness((p,t,done,{Texture2D})=>done(null,new Texture2D(100,200)));
 await assert.rejects(h.settle(h.loadArtRegion('product/a',[95,0,20,20],{web:false})),/outside texture/);
 const value=await h.settle(h.loadArtRegion('product/a',[5,10,20,30],{web:false}));assert.deepEqual(plain(value.rect),[5,10,20,30]);
});
