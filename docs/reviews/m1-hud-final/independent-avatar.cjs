const fs=require('node:fs'),path=require('node:path'),Module=require('node:module'),assert=require('node:assert/strict'),{test}=require('node:test');
const root=path.resolve(__dirname,'../../../delivery-game'),file=path.join(root,'tests/map-hud.test.cjs');
let src=fs.readFileSync(file,'utf8').split("\ntest(")[0];
src=src.replace("static EventType={TOUCH_START:'start'", "static EventType={SIZE_CHANGED:'size',ACTIVE_CHANGED:'activeChanged',TOUCH_START:'start'");
src=src.replace('addChild(n){this.children.push(n);n.parent=this;}', 'get active(){return this._active;}set active(value){if(this._active===value)return;this._active=value;this.events?.get("activeChanged")?.();}get activeInHierarchy(){return this.active&&(!this.parent||this.parent.activeInHierarchy);}addChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}');
src=src.replace('setContentSize(width,height){Object.assign(this,{width,height});}', 'setContentSize(width,height){const changed=this.width!==width||this.height!==height;Object.assign(this,{width,height});if(changed)this.node?.events.get("size")?.();}');
src=src.replace('const cc={Tween:', 'const requests=[];const cc={Texture2D:class{},SpriteFrame:class{addRef(){}},Rect:class{constructor(x,y,width,height){Object.assign(this,{x,y,width,height});}},Size:class{constructor(width,height){Object.assign(this,{width,height});}},Tween:');
src=src.replace('resources:{load(){}}', 'resources:{load(url,type,callback){requests.push({url,callback});}}');
const a=src.indexOf("if(id==='./CartoonArt')return {"),b=src.indexOf(";if(['./PresentationLayout'",a);assert.ok(a>0&&b>a);src=src.slice(0,a)+"if(id==='./CartoonArt')return load(id)"+src.slice(b);
src=src.replace('return {sample,root,panel,','return {requests,sample,root,panel,');src+='\nmodule.exports={harness};';
const mod=new Module(file,module);mod.filename=file;mod.paths=Module._nodeModulePaths(path.dirname(file));mod._compile(src,file);const {harness}=mod.exports;
const flush=async()=>{for(let i=0;i<10;i++)await Promise.resolve();};

function verify(h){const get=name=>h.walk(h.sample.root).find(n=>n.name===name),art=get('CartoonArt-avatar'),fallback=get('AvatarPlaceholder'),track=get('ExperienceTrack'),actual=art.active?art:fallback;assert.ok(Math.abs(actual.getComponent(h.UITransform).width-track.getComponent(h.UITransform).width)<1e-9);assert.ok(h.bounds(track).top<h.bounds(actual).bottom);assert.ok(!h.text(h.sample.root).includes('澄川骑手'));return track.getComponent(h.UITransform).width;}
test('HUD-final real loader: XP equals displayed avatar before response, success/failure, update and rebuild',async()=>{
 for(const fail of [false,true]){
  const h=harness();verify(h);h.setFrame({width:360,height:560});h.sample.rebuildLayout();verify(h);
  h.requests[0].callback(fail?Error('isolated avatar offline'):null,{width:1280,height:1280,addRef(){}});await flush();const width=verify(h);assert.ok(width>=84&&width<=92);h.sample.updatePlayerHeader();verify(h);h.sample.save();verify(h);h.sample.rebuildLayout();await flush();verify(h);
 }
});
