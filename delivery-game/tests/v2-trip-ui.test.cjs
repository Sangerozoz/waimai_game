// Written only. Invoke explicitly after stage authorization; needs the installed Cocos TypeScript.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const editor=process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts=require(path.join(editor,'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
function load(name,ports={}){
 const file=path.resolve(__dirname,'../assets/scripts/map-sample',name+'.ts');
 const m=new Module(file,module);m.filename=file;m.paths=module.paths;
 const decorator=()=>()=>{};
 m.require=id=>{
  if(id in ports)return ports[id];
  if(id==='cc')return {_decorator:{ccclass:decorator,property:()=>{}},Component:class{},Game:{},game:{},sys:{}};
  if(id==='./SampleUI')return {label:(_parent,text)=>({string:text})};
  return {};
 };
 m._compile(ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,experimentalDecorators:true}}).outputText,file);
 return m.exports[name];
}
test('runtime supply commits one candidate before publishing and keeps live state on save failure',()=>{
 let saves=0,fail=false;
 const restore=(_city,raw)=>{
  const state=JSON.parse(raw);
  return {serialize:()=>JSON.stringify(state),tick:()=>{},dispatch:{setLedgerContext:()=>{}},supply:kind=>{state.calls++;state.kind=kind;},get tripState(){return state;}};
 };
 const Runtime=load('V2RuntimeController',{'./V2GameSession':{V2GameSession:{restore}}});
 const runtime=new Runtime();runtime.enableV2=true;runtime.ports={city:{},nowSeconds:()=>0};
 runtime.live=restore({},'{"calls":0}');runtime.store={writable:true,commit:()=>{saves++;if(fail)throw Error('disk full');}};
 runtime.supply('water');assert.equal(saves,1);assert.equal(runtime.tripState.calls,1);
 fail=true;assert.throws(()=>runtime.supply('noodles'),/disk full/);assert.equal(runtime.tripState.calls,1);assert.equal(runtime.tripState.kind,'water');
});
function supplyUI(stamina=0){
 const UI=load('V2GameUI'),ui=new UI(),buttons=[],calls=[],policies=[];
 const options=['water','noodles','drink','fastFood','milkTea','premiumMeal'].map((id,i)=>({id,name:id,unlockMapId:1,costCents:100+i*100,actualRestore:Math.min(20,100-stamina),durationSeconds:1,quantity:i===0?1:0,unlocked:true}));
 ui.runtime={tripState:{stamina,action:null,autoSupplyPolicy:{enabled:false,budgetCents:1000,spentCents:300,allowPaid:false,useInventory:false}},snapshot:{batchIds:['o'],economy:{state:{cashCents:99999}}},supplyOptions:()=>options,supply:(...args)=>calls.push(args),configureAutoSupply:p=>policies.push(p)};
 ui.card=()=>({});ui.text=()=>{};ui.btn=(_p,text,_x,_y,_w,action,enabled=true)=>buttons.push({text,action,enabled});
 ui.navigate=page=>{ui.page=page;};ui.body={};ui.supplyOpen=true;
 return {ui,buttons,calls,policies};
}
test('six supplies offer independent purchase/inventory, close after selection, full stamina disables all',()=>{
 const ports={'./PresentationLayout':{scrollContent:()=>({})},'../domain/V2EconomyConfig':{V2_CONFIG:{maps:[{name:'县城'}]}}};
 // Supply widgets are tested with the same module ports used by the live UI.
 const UI=load('V2GameUI',ports),fixture=supplyUI(),{buttons,calls}=fixture;
 Object.setPrototypeOf(fixture.ui,UI.prototype);fixture.ui.supplies();
 assert.equal(buttons.filter(b=>b.text.startsWith('购买 ')).length,6);
 assert.equal(buttons.filter(b=>b.text==='使用库存').length,6);
 assert.equal(buttons.filter(b=>b.text==='使用库存'&&b.enabled).length,1);
 buttons.find(b=>b.text==='使用库存').action();assert.deepEqual(calls,[['water','inventory']]);assert.equal(fixture.ui.supplyOpen,false);assert.equal(fixture.ui.page,'首页');
 fixture.ui.runtime.tripState.stamina=100;buttons.length=0;fixture.ui.supplies();assert.ok(buttons.filter(b=>/^(购买 |使用库存|免费休息)/.test(b.text)).every(b=>!b.enabled));
});
test('auto toggle forwards explicit authorizations and never resets spent or enables paid use',()=>{
 const UI=load('V2GameUI',{'./PresentationLayout':{scrollContent:()=>({})},'../domain/V2EconomyConfig':{V2_CONFIG:{maps:[{name:'县城'}]}}});
 const f=supplyUI();Object.setPrototypeOf(f.ui,UI.prototype);f.ui.supplies();
 f.buttons.find(b=>b.text==='自动补给：关闭').action();
 assert.deepEqual(f.policies.pop(),{enabled:true,budgetCents:1000,kind:undefined,allowPaid:false,useInventory:false});
 assert.equal(f.buttons.find(b=>b.text==='0币预算').enabled,false);
 assert.equal(f.ui.runtime.tripState.autoSupplyPolicy.spentCents,300);
});
test('batch receipt uses cash baseline and inventory separately; legacy baseline is unknown',()=>{
 const Runtime=load('V2RuntimeController'),r=new Runtime();
 r.live={snapshot:()=>({economy:{state:{ledger:{entries:[{id:'order:a',amountCents:1000},{id:'npc:x',amountCents:900}]}}}}),tripState:{supplySpentCents:800,inventoryUsed:{water:3},batchAccounting:{orderIds:['a'],supplySpentCentsStart:500,inventoryUsedStart:{water:1}}}};
 assert.deepEqual(r.batchSummary,{incomeCents:1000,supplyCents:300,netCents:700,inventoryUsed:2});
 r.live.tripState.batchAccounting.end={supplySpentCents:800,inventoryUsed:{water:3}};r.live.tripState.supplySpentCents=1200;r.live.tripState.inventoryUsed.water=5;assert.deepEqual(r.batchSummary,{incomeCents:1000,supplyCents:300,netCents:700,inventoryUsed:2});
 r.live.tripState.batchAccounting=null;assert.equal(r.batchSummary,null);
});
test('ledger now is sampled once per atomic command; failed save does not publish charge',()=>{
 let sample=0,context,saved;
 const restore=(_city,raw)=>{const state=JSON.parse(raw);return {serialize:()=>JSON.stringify(state),dispatch:{setLedgerContext:c=>{context=c;state.context=c;}},tick:(_seq,now)=>{state.now=now;},supply:()=>{state.cash-=100;},get tripState(){return state;}};};
 const Runtime=load('V2RuntimeController',{'./V2GameSession':{V2GameSession:{restore}}}),r=new Runtime();r.enableV2=true;
 r.ports={city:{},nowSeconds:()=>{sample++;return 1700000000;}};r.live=restore({},'{"cash":1000}');r.store={writable:true,commit:s=>{saved=JSON.parse(s);}};
 r.supply('water');assert.equal(sample,1);assert.equal(context.nowMs,1700000000000);assert.equal(saved.now,1700000000);assert.equal(saved.cash,900);
 r.store.commit=()=>{throw Error('disk full');};assert.throws(()=>r.supply('water'),/disk full/);assert.equal(r.tripState.cash,900);
});
test('receipt displays actual base/final difference without a second deduction',()=>{
 const UI=load('V2GameUI'),ui=new UI();
 const receipt={id:'o1',incomeCents:855,baseIncomeCents:1000,lateGameSeconds:60,damage:'minor',ratingDelta:-2};
 const before=JSON.stringify(receipt),text=ui.receiptSummary(receipt);
 assert.match(text,/8\.55金币/);assert.match(text,/原价 10\.00 \/ 调整 −1\.45/);assert.match(text,/迟到 1分钟/);assert.match(text,/轻微餐损/);
 assert.equal(JSON.stringify(receipt),before);
});
test('bills consume real ledger periods including unknown dates without inferred hero-only totals',()=>{
 const periods={today:{incomeCents:1200,expenseCents:300,netCents:900,byCategory:{hero_ordinary:1200,supply_purchase:-300}},recentSevenDays:{incomeCents:2000,expenseCents:500,netCents:1500,byCategory:{}},cumulative:{incomeCents:3300,expenseCents:700,netCents:2600,byCategory:{npc_delivery:1300,map_purchase:-400}},unknownDate:{incomeCents:1300,expenseCents:0,netCents:1300,byCategory:{npc_delivery:1300}}};
 let received;const UI=load('V2GameUI',{'./PresentationLayout':{scrollContent:()=>({})},'../domain/V2Ledger':{summarizeLedger:(ledger,query)=>{received={ledger,query};return periods;}}});
 const ui=new UI(),rows=[],ledger={opening:{source:'migration'}};ui.runtime={snapshot:{economy:{state:{ledger}}},ledgerQuery:{todayDayKey:'2026-11-04',recentDayKeys:['2026-11-04']}};ui.text=(_p,text)=>rows.push(text);ui.bills();
 assert.equal(received.ledger,ledger);assert.ok(rows.some(x=>x.includes('今日 · 收入 12.00 / 支出 3.00')));assert.ok(rows.some(x=>x.includes('团队配送：13.00')));assert.ok(rows.some(x=>x.includes('迁移前明细未知')));assert.ok(rows.some(x=>x.includes('日期未知')));
});
test('home offers one switchable pure goal; navigation does not issue purchases or rewards',()=>{
 const targets=[{label:'首车',hint:'自主选择',shortfallCents:25000,completed:false,destination:'vehicles',canGo:false},{label:'首NPC',hint:'可前往',shortfallCents:0,completed:false,destination:'riders',canGo:true}];
 const UI=load('V2GameUI',{'../domain/V2ProgressTargets':{queryProgressTargets:()=>targets}}),ui=new UI(),buttons=[],rows=[];
 ui.body={};ui.runtime={snapshot:{economy:{state:{heroCompletedOrders:2,npcCompletedOrders:3}},batchIds:[]},tripState:null};
 ui.text=(_p,text)=>rows.push(text);ui.btn=(_p,text,_x,_y,_w,action,enabled=true)=>buttons.push({text,action,enabled});ui.refreshTripText=()=>{};ui.refreshFeedback=()=>{};ui.home();
 assert.equal(rows.filter(r=>r.includes('自主选择')).length,1);assert.ok(rows.some(r=>r.includes('差 250.00金币')));assert.equal(buttons.find(b=>b.text==='前往').enabled,false);
 buttons.find(b=>b.text==='切换目标').action();assert.equal(ui.targetIndex,1);
});
