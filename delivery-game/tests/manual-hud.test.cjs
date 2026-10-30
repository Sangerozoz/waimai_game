const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
function harness(book){
 class Node{
  static EventType={TOUCH_START:'start',TOUCH_MOVE:'move',TOUCH_CANCEL:'cancel',TOUCH_END:'end'};
  constructor(name){this.name=name;this.children=[];this.components=new Map();this.events=new Map();this.active=true;}
  addChild(n){this.children.push(n);n.parent=this;}
  addComponent(Type){const c=new Type();c.node=this;this.components.set(Type,c);return c;}
  getComponent(Type){return this.components.get(Type);}
  setPosition(x,y){Object.assign(this,{x,y});}setScale(x,y=x){this.scaleX=x;this.scaleY=y;}on(event,callback){this.events.set(event,callback);}
  setSiblingIndex(){}
  getChildByName(name){return this.children.find(n=>n.name===name);}
  destroy(){this.destroyed=true;}removeAllChildren(){this.children=[];}
 }
 class Color{constructor(r,g,b,a){Object.assign(this,{r,g,b,a});}}
 class Graphics{constructor(){this.fills=[];this.linePoints=[];}clear(){this.fills=[];this.linePoints=[];}roundRect(x,y,width,height){this.rect(x,y,width,height);}rect(x,y,width,height){this.lastRect={x,y,width,height};}fill(){this.fills.push({color:this.fillColor,rect:this.lastRect});}stroke(){}circle(){}moveTo(x,y){this.linePoints.push([x,y]);}lineTo(x,y){this.linePoints.push([x,y]);}ellipse(){}bezierCurveTo(){}close(){}}
 class UITransform{setContentSize(width,height){Object.assign(this,{width,height});}setAnchorPoint(){}}
 class Sprite{static SizeMode={CUSTOM:0};}
 class Label{static HorizontalAlign={LEFT:0,RIGHT:1,CENTER:2};static VerticalAlign={CENTER:0};static Overflow={SHRINK:0,CLAMP:1};}
 class Camera{constructor(...args){this.args=args;}static fitViewportHeight(_data,height){return height;}setVehicle(){}setRider(){}setRoutes(_routes,selected,fit){this.selected=selected;if(fit)this.focusRoute();}focusRoute(){this.focused=true;}advanceLocate(){}cancelLocate(){}locateAnimated(){}locate(){this.focused=false;}}
 let frame={width:390,height:844},designHeight=1280,safeRect=h=>({x:0,y:0,width:720,height:h});
 const browser={rotated:false,edges:{top:0,bottom:0,left:0,right:0}};
 class Mask{static Type={GRAPHICS_RECT:0};}
 const cc={Tween:{stopAllByTarget(){}},Vec3:class{constructor(x,y,z){Object.assign(this,{x,y,z});}},tween:()=>({to(){return this;},start(){}}),isValid:n=>!n.destroyed,Sprite,resources:{load(){}},Node,Color,Graphics,UITransform,Label,Mask,ScrollView:class{getScrollOffset(){return {y:0};}scrollToOffset(){}},Vec2:class{constructor(x,y){Object.assign(this,{x,y});}},BlockInputEvents:class{},Component:class{},sys:{getSafeAreaRect(symmetric){assert.equal(symmetric,false);return safeRect(designHeight);}},view:{getFrameSize:()=>frame,setDesignResolutionSize(_w,h){designHeight=h;}},ResolutionPolicy:{SHOW_ALL:1},Layers:{Enum:{UI_2D:1}},_decorator:{ccclass:()=>Type=>Type}},modules={};
 function load(name){
  if(modules[name])return modules[name];
  const file=path.resolve(__dirname,'../assets/scripts/map-sample',name+'.ts');
  const compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,experimentalDecorators:true}}).outputText;
  const scope={exports:{},document:{documentElement:{},getElementById:()=>({style:{transform:browser.rotated?'rotate(90deg)':'rotate(0deg)'}})},getComputedStyle:()=>({getPropertyValue:name=>`${browser.edges[name.replace('--safe-','')]}px`}),require(id){if(id==='cc')return cc;if(id==='./CityMap')return {CityMap:Camera,ROUTE_COLORS:{fast:'gold',main:'orange',smooth:'green'}};if(id==='./MapVehicle')return {MapVehicle:class{}};if(id==='./FoodImages')return {foodImage(){}};if(id==='./CartoonArt')return {cartoonArt(parent,key,x,y,w,h){const n=new Node('CartoonArt-'+key);parent.addChild(n);n.setPosition(x,y);n.addComponent(UITransform).setContentSize(w,h);n.addComponent(Sprite);return n;},cartoonChrome(parent,key,w,h){const n=new Node('CartoonChrome-'+key);parent.addChild(n);n.addComponent(UITransform).setContentSize(w,h);return n;},resizeCartoonChrome(n,w,h){n.getComponent(UITransform).setContentSize(w,h);}};if(['./CountyRules','./CompactOrderInfo','./MapTypes','./OrderPresentation','./PresentationLayout','./VehicleSideArt','./SampleUI','./SafeAreaLayout','./OrderPhone','./CountyConfig','./ReceiptPresentation','./CityExtent','./DeliveryClock','./BillingPresentation','../domain/GameConfig'].includes(id))return load(id);return {};}};
  vm.runInNewContext(compiled,scope,{filename:file});modules[name]=scope.exports;return scope.exports;
 }
 const {MapSample}=load('MapSample'),sample=new MapSample(),root=new Node('Root'),panel=new Node('Panel');root.addChild(panel);
 let located=0,opened=0,saved=0;
 Object.assign(sample,{node:{parent:new Node('Canvas')},root,panel,screenExtra:0,scheduleOnce(){},unschedule(){},city:{setVehicle(){},setRider(){},advanceLocate(){},cancelLocate(){},locateAnimated(){located++;},locate(){located++;}},store:{available:true,save(){saved++;return true;}},book:{mode:'idle',active:null,riderPose:{point:[0,0],angle:0},completed:0,data:{nodes:[],pois:[]},player:{cashCents:10000,rating:80,level:1,experience:0,vehicleTier:1,completedOrders:0},serialize:()=> 'unchanged-progress'}});
 if(book)sample.book=book;
 sample.openPhone=()=>{opened++;};sample.header(root);sample.controls();sample.renderPanel();
 const walk=n=>[n,...n.children.flatMap(walk)],text=n=>walk(n).map(n=>n.getComponent(Label)?.string).filter(x=>typeof x==='string');
 const click=n=>{const event={getID:()=>0,getUILocation:()=>({x:0,y:0})};n.events.get(Node.EventType.TOUCH_START)?.(event);n.events.get(Node.EventType.TOUCH_END)?.(event);};
 function bounds(node){
  const size=node.getComponent(UITransform);let x=node.x||0,y=node.y||0,sx=node.scaleX??1,sy=node.scaleY??1;
  for(let p=node.parent;p;p=p.parent){x=(p.x||0)+x*(p.scaleX??1);y=(p.y||0)+y*(p.scaleY??1);sx*=p.scaleX??1;sy*=p.scaleY??1;}
  return {left:x-size.width*sx/2,right:x+size.width*sx/2,bottom:y-size.height*sy/2,top:y+size.height*sy/2};
 }
 return {sample,root,panel,walk,text,click,Node,Label,Graphics,UITransform,bounds,load,setRotatedBrowser(edges){browser.rotated=true;browser.edges=edges;},setSafeArea(fn){safeRect=fn;},setFrame(v){frame=v;},height:()=>designHeight,openRealPhone:()=>MapSample.prototype.openPhone.call(sample),counts:()=>({located,opened,saved})};
}


function realBook(random=()=>.1){
 const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
 const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0}));
 const data={title:'县城测试',width:16000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
 return new OrderBook(data,random);
}

test('manual order actions stay behind each player boundary and cancellation keeps the order',()=>{
 const b=realBook(),h=harness(b);h.sample.accept(b.list().find(p=>p.pickupMetres>0).offer.id);const find=name=>h.walk(h.sample.root).find(n=>n.name===name);
 assert.ok(find('Button-取消订单'));h.click(find('Button-去取餐'));assert.equal(b.active.handoff.phase,'toPickup');b.advance(999);h.sample.renderPanel();assert.ok(find('Button-取餐'));h.click(find('Button-取餐'));assert.equal(b.active.handoff.phase,'picking');assert.ok(!find('Button-取消订单'));
 b.advance(999);h.sample.renderPanel();assert.ok(find('Button-去送餐'));h.click(find('Button-去送餐'));b.advance(999);assert.equal(b.mode,'done');
});

test('manual milestones interrupt a bill or closed card exactly once, and receipt awards once',()=>{
 const b=realBook(),h=harness(b);h.sample.accept(b.list().find(p=>p.pickupMetres>0).offer.id);const find=name=>h.walk(h.sample.root).find(n=>n.name===name);h.click(find('Button-去取餐'));
 h.click(find('CloseButton'));assert.equal(h.sample.orderCardOpen,false);h.sample.openBills();assert.equal(h.sample.modalKind,'bills');h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');assert.equal(h.sample.modalKind,null);assert.equal(h.sample.orderCardOpen,true);assert.ok(find('Button-取餐'));
 h.sample.openBills();h.sample.update(1);assert.equal(h.sample.modalKind,'bills','same waiting event cannot repeatedly interrupt');h.sample.dismissDialog();h.click(find('Button-取餐'));h.sample.openBills();h.sample.update(2);assert.equal(b.active.handoff.phase,'awaitDeliveryStart');assert.equal(h.sample.modalKind,null);assert.ok(find('Button-去送餐'));
 h.click(find('Button-去送餐'));h.sample.openBills();h.sample.update(999);assert.equal(b.mode,'done');assert.equal(h.sample.modalKind,'receipt');const cash=b.player.cashCents,completed=b.completed;h.sample.update(999);assert.equal(b.player.cashCents,cash);assert.equal(b.completed,completed);
});

test('failed boundary saves freeze movement and retry the same fixed result',()=>{
 const b=realBook(),h=harness(b),offer=b.list().find(p=>p.pickupMetres>0).offer;let fail=true,writes=0;h.sample.store={available:true,message:'写入失败',save(){writes++;return !fail;}};
 h.sample.accept(offer.id);assert.equal(h.sample.pendingSave,true);assert.equal(b.active.handoff.phase,'planning');h.sample.update(999);assert.equal(b.active.handoff.phase,'planning');assert.ok(writes>=2);
 fail=false;h.sample.update(1);assert.equal(h.sample.pendingSave,false);const find=name=>h.walk(h.sample.root).find(n=>n.name===name);fail=true;h.click(find('Button-去取餐'));assert.equal(b.active.handoff.phase,'toPickup');const damage=b.active.damage;h.sample.update(999);assert.equal(b.active.elapsed,0);assert.equal(b.active.damage,damage);
 fail=false;h.sample.update(1);assert.equal(b.active.elapsed,0);assert.equal(b.active.damage,damage);h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');
});

test('background freezes manual movement and foreground ignores its first compensating frame',()=>{
 const b=realBook(),h=harness(b);h.sample.accept(b.list().find(p=>p.pickupMetres>0).offer.id);const find=name=>h.walk(h.sample.root).find(n=>n.name===name);h.click(find('Button-去取餐'));const before=b.active.elapsed;
 h.sample.onHide();h.sample.update(999);assert.equal(b.active.elapsed,before);h.sample.onShow();h.sample.update(999);assert.equal(b.active.elapsed,before);h.sample.update(.01);assert.ok(b.active.elapsed>before);
});

test('reaccepting the same cancelled order gets a fresh pickup presentation event',()=>{
 const b=realBook(),h=harness(b),id=b.list().find(p=>p.pickupMetres>0).offer.id;h.sample.accept(id);let find=name=>h.walk(h.sample.root).find(n=>n.name===name);h.click(find('Button-去取餐'));h.sample.update(999);assert.equal(b.active.handoff.phase,'awaitPickup');assert.ok(find('Button-取餐'));
 h.click(find('Button-取消订单'));assert.equal(b.mode,'idle');h.sample.accept(id);assert.equal(b.active.handoff.phase,'planning');h.sample.orderCardOpen=false;h.sample.openBills();assert.equal(h.sample.act(()=>b.depart()),true);assert.equal(b.active.handoff.phase,'awaitPickup');h.sample.presentHandoff();assert.equal(h.sample.modalKind,null);assert.equal(h.sample.orderCardOpen,true);assert.ok(find('Button-取餐'));
});
