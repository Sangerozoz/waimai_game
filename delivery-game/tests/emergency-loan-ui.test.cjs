'use strict';
// UI boundary evidence: real V2GameUI logic; only Cocos drawing/art ports are headless.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ts=require(path.join(process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app','Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const root=path.resolve(__dirname,'../..'),scripts=path.join(root,'delivery-game/assets/scripts');
const historic=JSON.parse(fs.readFileSync(path.join(root,'docs/balance/2026-11-06-balance-round-01/pm/only-car-reproduction-1107.json'),'utf8')).fixtures.signedZeroQuota;

function fixture(phase='available',busy=false,page='骑手'){
 const buttons=[],labels=[],calls=[],cache=new Map();
 class UITransform{constructor(){this.width=72;}setContentSize(width){this.width=width;}setAnchorPoint(){}}
 class ScrollView{getScrollOffset(){return {y:0};}getMaxScrollOffset(){return {y:0};}stopAutoScroll(){}scrollToOffset(){}}
 class Node{
  constructor(name='node',parent=null){this.name=name;this.children=[];this.active=true;this.destroyed=false;this.parent=parent;this.components=new Map();if(parent)parent.children.push(this);}
  get activeInHierarchy(){return this.active&&!this.destroyed&&(!this.parent||this.parent.activeInHierarchy);}
  addComponent(Type){const component=new Type();component.node=this;this.components.set(Type,component);return component;}
  getComponent(Type){return this.components.get(Type)||this.addComponent(Type);}
  setPosition(){}
  setScale(){}
  setSiblingIndex(){}
  destroy(){this.destroyed=true;this.active=false;}
 }
 const valid=n=>!!n&&!n.destroyed;
 const panel=(parent,name)=>new Node(name,parent);
 const label=(parent,text)=>{const value={node:new Node('label',parent),string:text,updateRenderData(){}};labels.push(value);return value;};
 const action=(parent,text,_x,_y,_w,_h,invoke,enabled=true)=>{
  const n=new Node(text,parent);n.text=text;n.enabled=enabled;n.click=()=>{if(n.enabled&&n.activeInHierarchy)invoke();};buttons.push(n);return n;
 };
 const skin={UI:{ink:'#123',muted:'#678',blue:'#08F',line:'#ABC',orange:'#F80'},panel,action,glyph(){},portrait(){},levelBadge(){},statusBadge:label,checkbox(){},mainAction:(parent,text,x,y,fn)=>action(parent,text,x,y,100,100,fn),navigationTile:panel};
 const mocks={
  cc:{_decorator:{ccclass:()=>klass=>klass},Component:class{scheduleOnce(fn){fn();}},Node,isValid:valid,Label:{Overflow:{CLAMP:0,NONE:1}},UITransform,BlockInputEvents:class{},ScrollView,Mask:class{static Type={GRAPHICS_RECT:0};},Vec2:class{constructor(x,y){this.x=x;this.y=y;}}},
  'map-sample/SampleUI':{col:x=>x,item:panel,label,tap(node,fn){node.click=fn;}},
  'map-sample/V2ApprovedSkin':skin,
  'map-sample/V2ImageSkin':{master:{x:x=>x,y:y=>y,w:w=>w,h:h=>h},portraitDisplayName:async()=>null},
  'map-sample/VehicleSideArt':{vehicleSideArt(){}},'map-sample/VehicleShowcase':{vehicleProductPreview(){}},
  'map-sample/FoodImages':{foodImage(){}},'map-sample/CityMap':{CityMap:class{}},
 };
 function load(id){
  if(mocks[id])return mocks[id];if(cache.has(id))return cache.get(id);
  const exports={};cache.set(id,exports);const file=path.join(scripts,id+'.ts');let registration;
  const code=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.System,target:ts.ScriptTarget.ES2020,experimentalDecorators:true}}).outputText;
  vm.runInNewContext(code,{System:{register(deps,declare){registration={deps,declare};}},console,Map,Set,Date,Math,Promise,Object,Number,JSON},{filename:file});
  const module=registration.declare((name,value)=>{if(typeof name==='string')exports[name]=value;else Object.assign(exports,name);return value;},{id});
  registration.deps.forEach((dep,i)=>module.setters[i](load(dep==='cc'?'cc':path.posix.normalize(path.posix.join(path.posix.dirname(id),dep)))));module.execute();return exports;
 }
 const UI=load('map-sample/V2GameUI').V2GameUI,ui=new UI();
 const state=JSON.parse(JSON.stringify(historic.dispatch.economy.state));
 if(phase==='unavailable'){state.riders[0].vehicleId='starter-1';state.riders.find(r=>r.id!=='hero').vehicleId=null;state.fleetQuotes=[];}
 if(phase==='returnable')state.fleetQuotes=[];
 if(busy)state.activeQuote={id:'loan-in-flight'};
 let status={phase,sequence:phase==='available'?0:1,loanSequence:phase==='available'?null:1,returnVehicleIds:phase==='returnable'?['starter-1']:[],canStartBatch:phase==='borrowed',reason:'旧合同保留，亲送补额度'};
 const runtime={snapshot:{economy:{state},fleet:historic.dispatch.fleet,orders:[],batchIds:busy?['loan-in-flight']:[]},tripState:{action:null,stamina:100,rating:100,orders:[]},routeMotion:null,routeSnapshot:null,lastError:null,ledgerQuery:{todayDayKey:'2026-11-07'},get emergencyLoanStatus(){return status;},get nextBatchEffects(){return ['borrowed','returned','unavailable'].includes(status.phase)?{capacity:{version:'slots-v1',capacitySlots:2}}:null;},setPaused(){},enterLobby:()=>null,command:command=>{calls.push(JSON.parse(JSON.stringify(command)));if(command.type==='assignVehicle')state.riders.find(r=>r.id===command.riderId).vehicleId=command.vehicleId;},normalCandidates:()=>[]};
 ui.runtime=runtime;ui.body=new Node('body');ui.root=new Node('root');ui.page=page;ui.configureRider=page==='骑手'?'hero':null;
 let renders=0;const render=ui.render;ui.render=function(){renders++;return render.call(this);};ui.render();
 return {ui,buttons,labels,calls,runtime,state,setStatus:value=>{status=value;},get status(){return status;},get renders(){return renders;},find:text=>buttons.find(b=>b.text===text&&b.activeInHierarchy),visibleText:text=>labels.some(l=>l.string===text&&l.node.activeInHierarchy)};
}

test('eligible recovery offers borrowing separately from the one permanent car',()=>{
 const f=fixture();
 assert.ok(f.find('应急借车'),'eligible legacy save must expose the recovery action');
 assert.ok(f.labels.some(l=>l.string==='已拥有车辆 · 1 辆'));
 assert.equal(f.calls.length,0);
});

test('borrowing confirmation can cancel and submits the displayed sequence only once',()=>{
 const f=fixture();assert.ok(f.find('应急借车'));f.find('应急借车').click();
 assert.ok(f.labels.some(l=>/旧合同/.test(l.string)));
 f.find('取消').click();assert.deepEqual(f.calls,[]);
 f.find('应急借车').click();const confirm=f.find('确认借用');assert.ok(confirm);confirm.click();confirm.click();
 assert.deepEqual(f.calls,[{type:'borrowEmergencyVehicle',expectedSequence:0}]);
});

test('returnable car may still belong to an NPC and one confirmation returns it atomically',()=>{
 const f=fixture('returnable');const take=f.find('取回并归还');assert.ok(take);assert.equal(take.enabled,true);
 take.click();const confirm=f.find('确认归还');assert.ok(confirm);confirm.click();confirm.click();
 assert.deepEqual(f.calls,[{type:'returnEmergencyVehicle',loanSequence:1,vehicleId:'starter-1'}]);
 assert.ok(f.labels.some(l=>l.string==='已拥有车辆 · 1 辆'));
});

test('an existing hero batch keeps the emergency car and disables return',()=>{
 const f=fixture('returnable',true);const take=f.find('取回并归还');assert.ok(take);assert.equal(take.enabled,false);take.click();assert.deepEqual(f.calls,[]);
 assert.ok(f.labels.some(l=>/应急借车/.test(l.string)));
 assert.equal(f.find('应急借车'),undefined);
});

test('a stale borrowing dialog cannot submit after the eligibility changes',()=>{
 const f=fixture();assert.ok(f.find('应急借车'));f.find('应急借车').click();const confirm=f.find('确认借用');assert.ok(confirm);
 f.setStatus({...f.status,phase:'unavailable'});confirm.click();assert.deepEqual(f.calls,[]);
});

test('ordinary unavailable saves keep the ordinary car configuration without a loan action',()=>{
 const f=fixture('unavailable');assert.equal(f.find('应急借车'),undefined);assert.equal(f.find('取回并归还'),undefined);const unload=f.find('卸下车辆');assert.ok(unload);assert.equal(unload.enabled,true);unload.click();assert.deepEqual(f.calls,[{type:'assignVehicle',riderId:'hero',vehicleId:null}]);assert.equal(f.state.riders[0].vehicleId,null);
});

test('the home recovery entry actually opens hero configuration',()=>{
 const f=fixture('available',false,'首页');assert.ok(f.find('应急借车'));f.find('应急借车').click();
 assert.equal(f.ui.page,'骑手');assert.equal(f.ui.configureRider,'hero');assert.ok(f.visibleText('应急借车 · 临时基础车'));assert.ok(f.find('应急借车'));assert.deepEqual(f.calls,[]);
});

test('the lobby recovery entry opens configuration through the real navigation action',()=>{
 const f=fixture('available',false,'首页');assert.ok(f.find('抢单'));f.find('抢单').click();assert.equal(f.ui.page,'订单大厅');
 assert.ok(f.visibleText(f.status.reason));assert.ok(f.find('前往主角配车'));f.find('前往主角配车').click();assert.equal(f.ui.page,'骑手');assert.equal(f.ui.configureRider,'hero');assert.ok(f.find('应急借车'));assert.deepEqual(f.calls,[]);
});

test('eligibility refresh waits for the existing half-second cadence',()=>{
 const f=fixture('unavailable',false,'首页');f.ui.update(.5);const baseline=f.renders;assert.equal(f.find('应急借车'),undefined);
 f.state.riders[0].vehicleId=null;f.setStatus({...f.status,phase:'available',sequence:0,loanSequence:null,canStartBatch:false});f.ui.update(.49);
 assert.equal(f.renders,baseline);assert.equal(f.find('应急借车'),undefined);f.ui.update(.02);assert.ok(f.renders>baseline);assert.ok(f.find('应急借车'));
});

test('NPC old-contract release refreshes the real return action at the HUD cadence',()=>{
 const f=fixture('borrowed');f.ui.update(.5);assert.equal(f.find('取回并归还').enabled,false);const baseline=f.renders;
 f.state.fleetQuotes=[];f.setStatus({...f.status,phase:'returnable',returnVehicleIds:['starter-1'],canStartBatch:false});f.ui.update(.49);
 assert.equal(f.renders,baseline);assert.equal(f.find('取回并归还').enabled,false);f.ui.update(.02);assert.equal(f.find('取回并归还').enabled,true);
});

test('a reason-only eligibility change refreshes the lobby explanation',()=>{
 const f=fixture('available',false,'订单大厅');f.ui.update(.5);const before=f.status.reason,next='主角配送尚未结束，请完成整批后归还';assert.ok(f.visibleText(before));
 f.setStatus({...f.status,reason:next});f.ui.update(.5);assert.ok(f.visibleText(next));assert.equal(f.visibleText(before),false);
});
