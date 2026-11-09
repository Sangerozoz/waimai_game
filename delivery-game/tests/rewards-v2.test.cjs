const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
// Same isolated TypeScript transpile convention as cartoon-art.test.cjs. No game boot/save access.
const ts=require(path.join(process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app','Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const source=fs.readFileSync(path.join(__dirname,'../assets/scripts/rewards-v2/RewardSession.ts'),'utf8');
const scope={exports:{}};
vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText,scope);
const {RewardSession}=scope.exports;
const plain=x=>JSON.parse(JSON.stringify(x));
test('real entry IDs roll once, 80% boundary and prices are deterministic',()=>{
 const r=new RewardSession();
 assert.equal(r.enterLobby('a',.8,0),null);
 assert.equal(r.enterLobby('a',0,0),null);
 const c=r.enterLobby('b',.7999,.99999);
 assert.equal(c.coins,150);assert.equal(r.enterLobby('b',0,0).id,c.id);
 assert.equal(r.enterLobby('c',.8,0),null);
 assert.equal(r.enterLobby('b',0,0),null);
 for(const v of [NaN,Infinity,-.1,1,'0'])assert.throws(()=>r.enterLobby('bad',v,0));
});
test('ticket binds callback to order and benefit, duplicate and expired callbacks grant nothing',()=>{
 const r=new RewardSession(),c=r.enterLobby('a',0,0);
 const t=r.requestAd('special',c.id,0,30);
 assert.equal(r.resolveAd({...t,orderId:'wrong'},'completed',1),false);
 assert.equal(r.resolveAd(t,'completed',1),true);
 assert.equal(r.resolveAd(t,'completed',2),false);
 assert.throws(()=>r.beginBatch([{id:c.id,kind:'special'},{id:'n',kind:'normal'}]));
 r.beginBatch([{id:c.id,kind:'special'}]);r.endBatch();
 assert.equal(r.enterLobby('a',0,0),null);
 const a=r.requestAd('auto',null,10,30);
 assert.equal(r.resolveAd(a,'completed',40),false);
 assert.equal(r.autoRemainingSeconds,0);
});
test('cancel/failure cannot later succeed; unknown callback cannot grant',()=>{
 for(const outcome of ['cancelled','failed']){
  const r=new RewardSession(),t=r.requestAd('auto',null,0,10);
  assert.equal(r.resolveAd(t,outcome,1),false);
  assert.equal(r.resolveAd(t,'completed',2),false);
  assert.equal(r.autoRemainingSeconds,0);
 }
 const r=new RewardSession();assert.equal(r.resolveAd({id:'unknown',benefit:'auto',orderId:null,expiresAt:10},'completed',0),false);
});
test('auto budget clips final frame, freezes in background/pause and restores without offline accrual',()=>{
 let r=new RewardSession(),t=r.requestAd('auto',null,0,20);r.resolveAd(t,'completed',1);
 assert.equal(r.advanceAuto(500,false,false).runSeconds,0);
 assert.equal(r.advanceAuto(500,true,true).runSeconds,0);
 assert.equal(r.advanceAuto(599,true,false).runSeconds,599);
 r=RewardSession.restore(r.serialize());
 const last=r.advanceAuto(20,true,false);
 assert.equal(last.runSeconds,1);assert.equal(last.manualRequired,true);
 assert.equal(r.advanceAuto(20,true,false).runSeconds,0);
 assert.throws(()=>r.advanceAuto(-1,true,false));assert.throws(()=>r.advanceAuto(1,'true',false));
});
test('ordinary batches work; special requires rewarded ticket and consumes once',()=>{
 const r=new RewardSession(),c=r.enterLobby('a',0,0);
 assert.throws(()=>r.beginBatch([{id:c.id,kind:'special'}]));
 r.beginBatch([{id:'n',kind:'normal'}]);assert.throws(()=>r.beginBatch([{id:'n2',kind:'normal'}]));r.endBatch();
 const t=r.requestAd('special',c.id,0,10);r.resolveAd(t,'completed',1);
 const batch=r.beginBatch([{id:c.id,kind:'special'}]);assert.equal(batch.specialCoins,100);r.endBatch();
 assert.throws(()=>r.beginBatch([{id:c.id,kind:'special'}]));
});
test('restore rejects corrupt budgets, ticket binding and dangling entry references',()=>{
 const r=new RewardSession();r.enterLobby('a',0,0);r.requestAd('auto',null,0,20);
 for(const mutate of [s=>s.autoRemainingSeconds=601,s=>s.tickets[0].benefit='coins',s=>s.entries[0].candidateId='missing',s=>s.candidates[0].coins=99,s=>s.version=999]){
  const state=JSON.parse(r.serialize());mutate(state);assert.throws(()=>RewardSession.restore(JSON.stringify(state)));
 }
 assert.deepEqual(plain(RewardSession.restore(r.serialize()).snapshot()),plain(r.snapshot()));
});
test('pending request restores with its binding and cannot complete before issuance',()=>{
 let r=new RewardSession();const c=r.enterLobby('entry',0,.5),t=r.requestAd('special',c.id,10,20);
 r=RewardSession.restore(r.serialize());
 assert.throws(()=>r.resolveAd(t,'completed',9));
 assert.equal(r.resolveAd(t,'completed',11),true);
 assert.equal(r.beginBatch([{id:c.id,kind:'special'}]).specialCoins,125);
 assert.equal(RewardSession.restore(r.serialize()).snapshot().activeBatch.specialCoins,125);
});
test('normal relabeling, duplicate orders and automatic entitlement stacking are refused',()=>{
 const r=new RewardSession(),c=r.enterLobby('entry',0,0);
 assert.throws(()=>r.beginBatch([{id:c.id,kind:'normal'}]));
 assert.throws(()=>r.beginBatch([{id:'n',kind:'normal'},{id:'n',kind:'normal'}]));
 const t=r.requestAd('auto',null,0,10);
 assert.throws(()=>r.requestAd('auto',null,0,10));
 r.resolveAd(t,'completed',1);assert.throws(()=>r.requestAd('auto',null,2,10));
});

test('new entries roll independently while paid and pending rights survive a failed appearance roll',()=>{
 const r=new RewardSession(),c=r.enterLobby('a',0,0),t=r.requestAd('special',c.id,0,10);
 assert.equal(r.enterLobby('b',.9,0),null);
 assert.equal(r.resolveAd(t,'completed',1),true);
 assert.equal(r.enterLobby('c',.9,0),null);
 assert.equal(r.enterLobby('d',0,.9).id,c.id);
 r.beginBatch([{id:c.id,kind:'special'}]);
 assert.throws(()=>r.advanceAuto(1,true,false));
 assert.throws(()=>r.requestAd('auto',null,2,10));
});
test('auto request refuses an existing ordinary batch',()=>{
 const r=new RewardSession();r.beginBatch([{id:'normal',kind:'normal'}]);
 assert.throws(()=>r.requestAd('auto',null,0,10));
});
