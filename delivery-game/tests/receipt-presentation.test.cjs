const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const dir=path.dirname(process.env.MAP_ROUTER_MODULE);
const {OrderBook}=require(path.join(dir,'OrderBook.js'));
require('./legacy-order-fixture.cjs')(OrderBook);
const {ReceiptPresentation}=require(path.join(dir,'ReceiptPresentation.js'));
function city(){
 const nodes=Array.from({length:21},(_,i)=>({id:String(i),x:i*200,y:0}));
 return {title:'弹窗流程',width:5000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
}
test('direct delivery asks to present once; rebuild and manual reopen never award again',()=>{
 const book=new OrderBook(city(),()=>.99),presentation=new ReceiptPresentation();
 assert.equal(presentation.observe(book.active),false);
 book.accept(book.list()[0].offer.id);assert.equal(presentation.observe(book.active),false);
 book.depart();book.advance(99);assert.equal(book.mode,'done');
 const wallet=book.player;
 assert.equal(presentation.observe(book.active),true);
 for(let i=0;i<4;i++){assert.equal(presentation.observe(book.active),false);book.settle();}
 assert.deepEqual(book.player,wallet);
 book.finish();assert.equal(presentation.observe(book.active),false);assert.equal(book.list().length,10);
 book.accept(book.list()[0].offer.id);book.depart();book.advance(99);
 assert.equal(presentation.observe(book.active),true);
});
test('automatic door delivery and a reloaded receipt never recompute the award',()=>{
 const data=city(),book=new OrderBook(data,()=>.1),presentation=new ReceiptPresentation();
 book.accept(book.list()[0].offer.id);book.depart();book.advance(99);book.finish();
 const before=book.player;book.accept(book.list()[0].offer.id);book.depart();book.advance(99);
 assert.equal(book.mode,'done');assert.equal(book.active.receipt.outcome.doorAnswer,true);
 assert.equal(presentation.observe(book.active),true);
 const saved=book.serialize(),wallet=book.player;
 assert.equal(wallet.completedOrders,before.completedOrders+1);
 const restored=OrderBook.restore(data,saved,()=>{throw Error('receipt restore must not reroll');});
 const reloaded=new ReceiptPresentation();assert.equal(reloaded.observe(restored.active),true);
 assert.equal(reloaded.observe(restored.active),false);assert.deepEqual(restored.player,wallet);
 restored.settle(false);assert.deepEqual(restored.player,wallet);
 restored.finish();assert.equal(restored.mode,'idle');assert.equal(restored.list().length,10);
});
