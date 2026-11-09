// Pending authorization: these tests have not been executed.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const dir=path.dirname(process.env.MAP_ROUTER_MODULE);
const {OrderBook}=require(path.join(dir,'OrderBook.js'));
const {CountyV2Session}=require(path.join(dir,'CountyV2Session.js'));
const {CountySaveStore}=require(path.join(dir,'CountySaveStore.js'));
const city={title:'test',width:2000,height:100,nodes:Array.from({length:12},(_,i)=>({id:String(i),x:i*100,y:0})),roads:[{id:'r',nodes:Array.from({length:12},(_,i)=>String(i)),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:Array.from({length:12},(_,i)=>({name:`p${i}`,node:String(i),kind:i%3===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
test('retired legacy migration rejects instead of manufacturing legacy assets or a new wallet',()=>{
 const old=new OrderBook(city,()=>.99),raw=JSON.parse(old.serialize());raw.futureExtension={keep:'exact'};
 const bytes=JSON.stringify(raw),before=old.serialize();
 assert.throws(()=>CountyV2Session.migrate(city,bytes));
 assert.equal(old.serialize(),before);assert.equal(JSON.parse(bytes).futureExtension.keep,'exact');
 assert.equal(CountyV2Session.fresh().economy.state.cashCents,10000);
});
test('retired old in-flight facade does not migrate or settle into the current economy',()=>{
 const old=new OrderBook(city,()=>.99);old.accept(old.list()[0].offer.id);old.depart();
 const bytes=old.serialize(),cash=old.player.cashCents;
 assert.throws(()=>CountyV2Session.migrate(city,bytes));
 assert.equal(old.serialize(),bytes);assert.equal(old.player.cashCents,cash);
 const fresh=CountyV2Session.fresh();assert.throws(()=>fresh.settleLegacy(city,true),/没有/);
 assert.equal(fresh.economy.state.heroCompletedOrders,0);
});
test('future V2 schema/config blocks storage writes and leaves primary bytes intact',()=>{
 for(const edit of [s=>s.version=99,s=>s.configId='future']){
  const raw=JSON.parse(CountyV2Session.fresh().serialize());edit(raw);const bytes=JSON.stringify(raw),writes=[];
  const storage={getItem:()=>bytes,setItem:(...args)=>writes.push(args)},store=new CountySaveStore(storage,'isolated-test',()=>true);
  store.load(s=>CountyV2Session.restore(s),()=>CountyV2Session.fresh());
  assert.equal(store.save(CountyV2Session.fresh().serialize()),false);assert.equal(writes.length,0);assert.match(store.message,/版本/);
 }
});
