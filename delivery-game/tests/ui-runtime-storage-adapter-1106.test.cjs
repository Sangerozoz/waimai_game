// Narrow adapter unit evidence only: real V2RuntimeStore implementation, in-memory
// StoragePort and WriterPort fixtures. No browser profile, real save or game boot.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ts=require(path.join(process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app','Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const filename=path.join(__dirname,'../assets/scripts/map-sample/V2RuntimeStore.ts');
const code=ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
const scope={exports:{},require:name=>{assert.equal(name,'./WebWriterLease');return {WebWriterLease:class{constructor(){throw Error('test must inject its own lease');}}};}};
vm.runInNewContext(code,scope,{filename});
const {V2RuntimeStore,V2_RUNTIME_SAVE_KEY:SLOT,V2_SLOT_EPOCH_KEY:EPOCH,LEGACY_GAME_SAVE_KEYS:OLD}=scope.exports;
function fixture(initial={}){
 const data=new Map(Object.entries(initial)),writes=[],removes=[];
 const writer={writable:false,acquires:0,releases:0,async acquire(){this.acquires++;this.writable=true;return true;},release(){this.releases++;this.writable=false;}};
 const storage={getItem:key=>data.has(key)?data.get(key):null,setItem(key,value){writes.push([key,value]);data.set(key,value);},removeItem(key){removes.push(key);data.delete(key);}};
 return {data,writes,removes,writer,storage,store:new V2RuntimeStore(storage,writer)};
}
test('empty continue creates no primary bytes until explicit successful commit',async()=>{
 const f=fixture({'unrelated-key':'keep'});let fresh=0;
 const value=await f.store.open('continue',()=>{throw Error('unexpected restore');},()=>{fresh++;return {cash:100};});
 assert.equal(value.cash,100);assert.equal(fresh,1);assert.equal(f.data.has(SLOT),false);assert.equal(f.data.get('unrelated-key'),'keep');
 f.store.commit('new-snapshot');assert.equal(f.data.get(SLOT),'new-snapshot');assert.ok(f.data.has(EPOCH));f.store.close();
});
test('valid existing nonzero primary is restored exactly without fresh replacement',async()=>{
 const bytes=JSON.stringify({cash:235,settled:['paid-1'],paused:true}),f=fixture({[SLOT]:bytes,[EPOCH]:'epoch-1'});let received;
 const value=await f.store.open('continue',raw=>{received=raw;return JSON.parse(raw);},()=>{throw Error('unexpected fresh');});
 assert.equal(received,bytes);assert.equal(value.cash,235);assert.equal(value.paused,true);assert.deepEqual(value.settled,['paid-1']);assert.equal(f.writes.length,0);assert.equal(f.data.get(SLOT),bytes);f.store.close();
});
test('explicit new refuses an existing primary rather than overwriting it',async()=>{
 const f=fixture({[SLOT]:'preserved',[EPOCH]:'epoch-1'});let fresh=0;
 await assert.rejects(f.store.open('new',()=>({}),()=>{fresh++;return {};}),/已有当前进度/);
 assert.equal(f.data.get(SLOT),'preserved');assert.equal(fresh,0);assert.equal(f.writes.length,0);assert.equal(f.writer.releases,1);
});
test('restore without a primary refuses without inventing a progress snapshot',async()=>{
 const f=fixture({[EPOCH]:'epoch-1'});
 await assert.rejects(f.store.open('restore',()=>({}),()=>{throw Error('unexpected fresh');}),/没有当前进度/);
 assert.equal(f.data.has(SLOT),false);assert.equal(f.writer.releases,1);
});
test('malformed or future primary retains exact bytes and never falls back to fresh',async()=>{
 for(const bytes of ['not-json',JSON.stringify({version:999,cash:735})]){
  const f=fixture({[SLOT]:bytes,[EPOCH]:'epoch-1'});let fresh=0;
  await assert.rejects(f.store.open('continue',()=>{throw Error('unsupported snapshot');},()=>{fresh++;return {};}),/已保留原进度/);
  assert.equal(f.data.get(SLOT),bytes);assert.equal(fresh,0);assert.equal(f.writes.length,0);assert.equal(f.writer.releases,1);
 }
});
test('lost writer stops publication and never changes the primary',async()=>{
 const f=fixture({[SLOT]:'old',[EPOCH]:'epoch-1'});await f.store.open('continue',raw=>raw,()=>null);
 f.writer.writable=false;assert.equal(f.store.writable,false);assert.match(f.store.message,/写入权/);
 assert.throws(()=>f.store.commit('new'),/写入已停止/);assert.equal(f.data.get(SLOT),'old');assert.equal(f.writes.length,0);
});
test('changed epoch invalidates an older instance without touching replacement progress',async()=>{
 const f=fixture({[SLOT]:'replacement',[EPOCH]:'epoch-1'});await f.store.open('continue',raw=>raw,()=>null);
 f.data.set(EPOCH,'epoch-2');assert.equal(f.store.writable,false);assert.throws(()=>f.store.commit('stale'),/写入已停止/);
 assert.equal(f.data.get(SLOT),'replacement');assert.equal(f.data.get(EPOCH),'epoch-2');assert.equal(f.writes.length,0);
});
test('primary byte conflict rejects stale commit even when epoch is unchanged',async()=>{
 const f=fixture({[SLOT]:'old',[EPOCH]:'epoch-1'});await f.store.open('continue',raw=>raw,()=>null);
 f.data.set(SLOT,'external-new');assert.throws(()=>f.store.commit('stale'),/其他操作改变/);assert.equal(f.data.get(SLOT),'external-new');assert.equal(f.store.writable,false);assert.equal(f.writes.length,0);
});
test('failed primary write freezes further commits and keeps previous bytes',async()=>{
 const f=fixture({[SLOT]:'old',[EPOCH]:'epoch-1'});await f.store.open('continue',raw=>raw,()=>null);
 f.storage.setItem=()=>{throw Error('storage quota');};assert.throws(()=>f.store.commit('new'),/storage quota/);
 assert.equal(f.data.get(SLOT),'old');assert.equal(f.store.writable,false);assert.throws(()=>f.store.commit('retry'),/写入已停止/);
});
test('close during pending acquisition releases a late grant without initializing storage',async()=>{
 const f=fixture({[SLOT]:'old',[EPOCH]:'epoch-1'});let resolve;
 f.writer.acquire=()=>new Promise(done=>{resolve=()=>{f.writer.writable=true;done(true);};});
 const pending=f.store.open('continue',raw=>raw,()=>null);f.store.close();resolve();
 await assert.rejects(pending,/存储已关闭/);assert.equal(f.writer.writable,false);assert.equal(f.store.writable,false);assert.equal(f.writes.length,0);assert.equal(f.data.get(SLOT),'old');
});
test('prepare deletes only the explicit legacy keys and preserves current/unrelated storage',async()=>{
 const initial={[SLOT]:'current',[EPOCH]:'epoch-1','delivery-game-save-v1-custom':'keep','other-app':'untouched'};for(const key of OLD)initial[key]='obsolete';
 const f=fixture(initial);assert.equal(await f.store.prepare(),true);
 for(const key of OLD)assert.equal(f.data.has(key),false);
 assert.equal(f.removes.length,OLD.length);assert.equal(f.data.get(SLOT),'current');assert.equal(f.data.get(EPOCH),'epoch-1');assert.equal(f.data.get('delivery-game-save-v1-custom'),'keep');assert.equal(f.data.get('other-app'),'untouched');assert.equal(f.writer.writable,false);
});
test('legacy cleanup failure releases its lease and does not create a replacement primary',async()=>{
 const f=fixture({[OLD[0]]:'obsolete',[SLOT]:'current'});delete f.storage.removeItem;
 await assert.rejects(f.store.prepare(),/不支持清除/);assert.equal(f.data.get(SLOT),'current');assert.equal(f.data.get(OLD[0]),'obsolete');assert.equal(f.writer.writable,false);assert.equal(f.writes.length,0);
});
test('denied acquisition cannot read or write a primary through open',async()=>{
 const f=fixture({[SLOT]:'current',[EPOCH]:'epoch-1'});f.writer.acquire=async()=>false;let restored=0;
 await assert.rejects(f.store.open('continue',()=>{restored++;return {};},()=>({})),/请先关闭其他游戏页/);
 assert.equal(restored,0);assert.equal(f.writes.length,0);assert.equal(f.data.get(SLOT),'current');
});
test('transient read failure is propagated without replacement progress or a fresh call',async()=>{
 const f=fixture({[SLOT]:'current',[EPOCH]:'epoch-1'});let fresh=0;const get=f.storage.getItem;
 f.storage.getItem=key=>{if(key===SLOT)throw Error('storage temporarily inaccessible');return get(key);};
 await assert.rejects(f.store.open('continue',raw=>raw,()=>{fresh++;return 'new';}),/temporarily inaccessible/);
 assert.equal(fresh,0);assert.equal(f.data.get(SLOT),'current');assert.equal(f.writes.length,0);assert.equal(f.writer.writable,false);
});
test('closed storage refuses later preparation and commit',async()=>{
 const f=fixture({[SLOT]:'current',[EPOCH]:'epoch-1'});await f.store.open('continue',raw=>raw,()=>null);f.store.close();
 assert.equal(f.store.writable,false);assert.throws(()=>f.store.commit('new'),/写入已停止/);await assert.rejects(f.store.prepare(),/请先关闭其他游戏页/);assert.equal(f.data.get(SLOT),'current');
});
