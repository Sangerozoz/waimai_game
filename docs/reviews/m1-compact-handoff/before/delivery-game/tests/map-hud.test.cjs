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
  const scope={exports:{},document:{documentElement:{},getElementById:()=>({style:{transform:browser.rotated?'rotate(90deg)':'rotate(0deg)'}})},getComputedStyle:()=>({getPropertyValue:name=>`${browser.edges[name.replace('--safe-','')]}px`}),require(id){if(id==='cc')return cc;if(id==='./CityMap')return {CityMap:Camera,ROUTE_COLORS:{fast:'gold',main:'orange',smooth:'green'}};if(id==='./MapVehicle')return {MapVehicle:class{}};if(id==='./FoodImages')return {foodImage(){}};if(id==='./CartoonArt')return {cartoonArt(parent,key,x,y,w,h){const n=new Node('CartoonArt-'+key);parent.addChild(n);n.setPosition(x,y);n.addComponent(UITransform).setContentSize(w,h);n.addComponent(Sprite);return n;},cartoonChrome(parent,key,w,h){const n=new Node('CartoonChrome-'+key);parent.addChild(n);n.addComponent(UITransform).setContentSize(w,h);return n;},resizeCartoonChrome(n,w,h){n.getComponent(UITransform).setContentSize(w,h);}};if(['./OrderPresentation','./PresentationLayout','./VehicleSideArt','./SampleUI','./SafeAreaLayout','./OrderPhone','./CountyConfig','./ReceiptPresentation','./CityExtent','./DeliveryClock','./BillingPresentation','../domain/GameConfig'].includes(id))return load(id);return {};}};
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

test('compact avatar has no nickname and XP follows displayed width; capsules hug full numeric text',()=>{const h=harness(realBook());assert.ok(!h.text(h.root).includes('澄川骑手'));const get=name=>h.walk(h.sample.root).find(n=>n.name===name);const xp=get('ExperienceTrack');assert.equal(xp.getComponent(h.UITransform).width,get('CartoonArt-avatar').getComponent(h.UITransform).width);const y=h.bounds(xp);assert.ok(y.top<h.bounds(get('PlayerAvatar')).bottom);const original=get('WalletPill').getComponent(h.UITransform).width;for(const cents of [1000000000,10000000000,100000000000,Number.MAX_SAFE_INTEGER]){h.sample.book.playerState.cashCents=cents;h.sample.updatePlayerHeader();assert.equal(h.sample.money.string,(cents/100).toFixed(2));assert.ok(get('WalletPill').getComponent(h.UITransform).width>=original);assert.equal(h.sample.money.fontSize,h.sample.rating.fontSize);}});

test('XP presentation follows county thresholds and updates the actual fill through level transitions',()=>{
 const h=harness(),progress=h.load('./PresentationLayout').experienceProgress;
 for(const [xp,start,end,fraction] of [[0,0,50,0],[40,0,50,.8],[50,50,185,0],[100,50,185,50/135],[150,50,185,100/135],[185,185,367,0],[366,185,367,181/182]]){
  const p=progress(xp);assert.deepEqual([p.start,p.end,p.progress],[start,end,fraction]);
  Object.assign(h.sample.book.player,{experience:xp,level:p.level});h.sample.updatePlayerHeader();
  const nodes=h.walk(h.sample.root),fill=nodes.find(n=>n.name==='ExperienceFill'),track=nodes.find(n=>n.name==='ExperienceTrack');
  assert.ok(Math.abs(fill.getComponent(h.UITransform).width/track.getComponent(h.UITransform).width-fraction)<1e-10);
  assert.equal(fill.active,fraction>0);assert.equal(h.sample.experience.string,`Lv.${p.level}`);
 }
 for(const xp of [Number.MAX_SAFE_INTEGER,Infinity,-1]){const p=progress(xp);assert.ok(Number.isFinite(p.progress)&&p.progress>=0&&p.progress<=1);}
 const extreme=progress(Number.MAX_SAFE_INTEGER);Object.assign(h.sample.book.player,{experience:Number.MAX_SAFE_INTEGER,level:extreme.level});h.sample.updatePlayerHeader();
 assert.equal(h.sample.experience.string,`Lv.${extreme.level}`);
 assert.equal(h.sample.experience.overflow,h.Label.Overflow.SHRINK);assert.equal(h.sample.experience.node.getComponent(h.UITransform).width,h.walk(h.sample.root).find(n=>n.name==='ExperienceTrack').getComponent(h.UITransform).width);
});

test('notch and home indicator insets move real profile and all five menu touch targets into the safe rect',()=>{
 const h=harness(realBook());h.setSafeArea(height=>({x:0,y:64,width:720,height:height-174}));const before=h.sample.book.serialize();h.sample.rebuildLayout();
 const top=h.height()/2-110,bottom=-h.height()/2+64,nodes=h.walk(h.sample.root);
 const avatar=nodes.find(n=>n.name==='PlayerAvatar');assert.ok(h.bounds(avatar).top<=top-12);
 assert.ok(h.bounds(h.sample.money.node).top<=top-12);
 for(const node of nodes.filter(n=>n.name.startsWith('Nav-')))assert.ok(h.bounds(node).bottom>=bottom+8,node.name);
 const header=nodes.find(n=>n.name==='Header');assert.equal(h.bounds(header).top,top-12,'card leaves a gap below the safe top edge');
 assert.equal(h.sample.book.serialize(),before);h.sample.rebuildLayout();
 assert.ok(Math.abs(h.bounds(h.walk(h.sample.root).find(n=>n.name==='Nav-orders')).bottom-(bottom+15))<1e-7,'no doubled inset');
});

test('safe-area changes restore normal spacing while preserving an open bill and saved game state',()=>{
 const h=harness(realBook()),before=h.sample.book.serialize();h.setSafeArea(height=>({x:0,y:64,width:720,height:height-174}));h.sample.rebuildLayout();h.sample.openBills();
 h.setSafeArea(height=>({x:0,y:0,width:720,height}));h.sample.rebuildLayout();
 assert.equal(h.sample.modalKind,'bills');assert.equal(h.sample.book.serialize(),before);
 assert.ok(Math.abs(h.bounds(h.walk(h.sample.root).find(n=>n.name==='Nav-orders')).bottom-(-h.height()/2+15))<1e-7);
});

test('delivery sheet, rider locator and map attribution rise together above the bottom safe area',()=>{
 const b=realBook();b.accept(b.list()[0].offer.id);const h=harness(b);h.setSafeArea(height=>({x:0,y:64,width:720,height:height-174}));h.sample.rebuildLayout();
 const nodes=h.walk(h.sample.root),sheet=nodes.find(n=>n.name==='DeliverySheet'),nav=nodes.find(n=>n.name==='MainNavigation'),locate=nodes.find(n=>n.name==='FollowRider');
 assert.ok(h.bounds(sheet).bottom>=h.bounds(nav).top);assert.ok(h.bounds(locate).bottom>h.bounds(sheet).top);
 const [, ,mapHeight,,mapY]=h.sample.city.args;assert.ok(Math.abs(mapY-mapHeight/2-h.bounds(sheet).top)<1);
 for(const frame of [{width:320,height:1000},{width:1280,height:720},{width:390,height:844}]){h.setFrame(frame);h.sample.rebuildLayout();const sheet=h.walk(h.sample.root).find(n=>n.name==='DeliverySheet'),[, ,height,,y]=h.sample.city.args;assert.ok(Math.abs(y-height/2-h.bounds(sheet).top)<1,'resizing keeps the actual sheet and map boundary together');}
});

test('asymmetric side insets keep menus and modal actions inside the usable screen',()=>{
 const h=harness(realBook());h.setSafeArea(height=>({x:42,y:62,width:620,height:height-170}));h.sample.rebuildLayout();h.sample.openBills();
 for(const node of h.walk(h.sample.root).filter(n=>n.name.startsWith('Nav-'))){const r=h.bounds(node);assert.ok(r.left>=-318&&r.right<=302,node.name);}
 const card=h.walk(h.sample.modal).find(n=>n.name==='DialogCard'),r=h.bounds(card);
 assert.ok(r.left>=-318&&r.right<=302);assert.ok(r.top<=h.height()/2-108&&r.bottom>=-h.height()/2+62);
});

test('the real order phone fits between the notch and home indicator in a short viewport',()=>{
 const h=harness(realBook());h.setFrame({width:390,height:600});h.setSafeArea(height=>({x:0,y:100,width:720,height:height-260}));h.sample.rebuildLayout();const before=h.sample.book.serialize();h.openRealPhone();
 const frame=h.walk(h.sample.phone.node).find(n=>n.name==='PhoneFrame'),r=h.bounds(frame);
 assert.ok(r.top<=h.height()/2-160&&r.bottom>=-h.height()/2+100);assert.equal(h.sample.book.serialize(),before);
});

test('letterboxing outside the game and unavailable safe-area readings do not add duplicate padding',()=>{
 const h=harness(realBook());
 for(const fn of [height=>({x:-40,y:-30,width:800,height:height+60}),()=>({x:NaN,y:0,width:720,height:1200})]){
  h.setSafeArea(fn);h.sample.rebuildLayout();assert.ok(Math.abs(h.bounds(h.walk(h.sample.root).find(n=>n.name==='Nav-orders')).bottom-(-h.height()/2+15))<1e-7);
 }
});

test('portrait-locked canvas rotation maps physical notch and gesture edges before UI layout',()=>{
 for(const edges of [{left:59,right:0,top:0,bottom:21},{left:0,right:59,top:0,bottom:21}]){
  const h=harness(realBook());h.setRotatedBrowser(edges);h.sample.rebuildLayout();const scale=390/720,top=h.height()/2-edges.right/scale,bottom=-h.height()/2+edges.left/scale;
  const nodes=h.walk(h.sample.root),avatar=nodes.find(n=>n.name==='PlayerAvatar'),claim=nodes.find(n=>n.name==='Nav-orders');
  assert.ok(h.bounds(avatar).top<=top-12);assert.ok(h.bounds(claim).bottom>=bottom+8);
  assert.ok(Math.abs(h.bounds(claim).bottom-(bottom+15))<1e-7,'notch switches to the correct logical edge, once');
  const locate=nodes.find(n=>n.name==='FollowRider');assert.ok(h.bounds(locate).right<=360-21/scale-12);
 }
});

test('the real map footer keeps scale line, scale label and attribution inside horizontal safe bounds',()=>{
 const h=harness(),{CityMap}=h.load('CityMap');CityMap.prototype.drawCity=CityMap.prototype.sync=()=>{};
 const data={nodes:[],pois:[],labels:[],roads:[],areas:[],buildings:[],waterways:[],width:1000,height:1000};
 const map=new CityMap(h.root,data,1280,()=>{},0,180,{left:42,right:58});
 for(const node of h.walk(map.viewport).filter(n=>['30 m','© OpenStreetMap contributors'].includes(n.getComponent(h.Label)?.string))){const r=h.bounds(node);assert.ok(r.left>=-318&&r.right<=302,node.getComponent(h.Label).string);}
 const line=h.walk(map.viewport).find(n=>n.name==='MapScale'),xs=line.getComponent(h.Graphics).linePoints.map(p=>h.bounds(line).left+p[0]);assert.ok(Math.min(...xs)>=-318&&Math.max(...xs)<=302);
});

test('the five navigation entries keep unavailable features inert and claim opens the phone',()=>{
 const h=harness(),nav=h.walk(h.panel).find(n=>n.name==='MainNavigation');assert.ok(nav);
 for(const name of ['招募','车辆','抢单','地图','账单'])assert.ok(h.text(nav).includes(name));
 const before=h.sample.book.serialize();
 for(const key of ['recruit']){
  const slot=h.walk(nav).find(n=>n.name==='Nav-'+key);assert.ok(slot);assert.equal(slot.events.size,0);
  h.click(slot);assert.equal(h.sample.book.serialize(),before);assert.equal(h.sample.modal,null);
 }
 const claim=h.walk(nav).find(n=>n.name==='Nav-orders');h.click(claim);assert.equal(h.counts().opened,1);
});
test('station moves to the map lower left while bills occupy the rightmost bottom entry',()=>{
 const h=harness(realBook()),nav=h.walk(h.panel).find(n=>n.name==='MainNavigation');
 assert.ok(!h.walk(nav).some(n=>n.name==='Nav-station'));const station=h.walk(h.root).find(n=>n.name==='StationEntry');
 assert.ok(station);assert.ok(station.x<0&&station.y<0);assert.equal(station.events.size,0);
 const map=h.walk(nav).find(n=>n.name==='Nav-map'),bills=h.walk(nav).find(n=>n.name==='Nav-bills');
 assert.equal(map.x,158);assert.equal(bills.x,280);h.click(bills);assert.equal(h.sample.modalKind,'bills');
 for(const name of ['今日收入','今日订单数','今日好评','钱包余额','在线时长','配送里程','准时率','超时','差评','累计配送费','累计完成订单','单日最高订单数'])assert.ok(h.text(h.sample.modal).includes(name));
 const before=h.sample.book.serialize();h.sample.rebuildLayout();assert.equal(h.sample.modalKind,'bills');assert.equal(h.sample.book.serialize(),before);
});
test('foreground time is counted while idle but background and the closed interval are excluded',()=>{
 const b=realBook(),h=harness(b),now=Date.now();h.sample.onlineAt=now-2000;h.sample.update(.1);
 const counted=b.billing.today.onlineMs;assert.ok(counted>=2000);
 h.sample.hidden=true;h.sample.onlineAt=now-50000;h.sample.update(50);assert.equal(b.billing.today.onlineMs,counted);
 h.sample.onHide();assert.equal(b.billing.today.onlineMs,counted,'a second hide event must not charge an interval that was already hidden');
 h.sample.onShow();h.sample.update(.1);assert.ok(b.billing.today.onlineMs<counted+1000);
});
test('an already open bill refreshes both its date and daily values across midnight',()=>{
 const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));let day='2026-10-28';
 const b=new OrderBook(realBook().data,()=>.99,()=>day),h=harness(b);
 h.click(h.walk(h.panel).find(n=>n.name==='Nav-bills'));assert.ok(h.text(h.sample.modal).includes('2026-10-28'));
 day='2026-10-29';h.sample.updateBills();assert.ok(h.text(h.sample.modal).includes('2026-10-29'));assert.ok(!h.text(h.sample.modal).includes('2026-10-28'));
});
test('the map keeps only its lower-right rider locator and hides routine saved/shift prompts',()=>{
 const h=harness(),nodes=h.walk(h.root),names=nodes.map(n=>n.name);
 assert.equal(names.filter(n=>n==='FollowRider').length,1);
 assert.ok(!names.some(n=>n==='MapStatus'||n==='ShiftStatus'||n.startsWith('MapControl-')));
 assert.ok(!h.text(h.root).some(s=>/自主接单|今日配送|已保存|资金已够|攒够|下一单，去哪里|合作商家|配送地址|已送/.test(s)));
 h.click(nodes.find(n=>n.name==='FollowRider'));assert.equal(h.counts().located,1);
 h.sample.save();assert.equal(h.counts().saved,1,'hiding the saved badge must not disable persistence');
});
test('a save error remains visible when claiming an order rebuilds the map layout',()=>{
 const h=harness();h.sample.store.message='保存失败，请重试';h.sample.store.save=()=>false;
 h.sample.save();assert.ok(h.text(h.sample.root).includes('保存失败，请重试'));
 h.sample.rebuildLayout();assert.ok(h.text(h.sample.root).includes('保存失败，请重试'),'rebuilding must not silently erase a deduplicated save error');
});
test('the map navigation opens unlockable regions without spending or moving the rider',()=>{
 const h=harness(realBook()),before=h.sample.book.serialize(),entry=h.walk(h.panel).find(n=>n.name==='Nav-map');
 h.click(entry);assert.equal(h.sample.modalKind,'maps');
 for(const name of ['县城','城市','省会','一线','国际一线'])assert.ok(h.text(h.sample.modal).includes(name));
 for(let i=1;i<5;i++){
  const region=h.walk(h.sample.modal).find(n=>n.name==='Region-'+i);assert.ok(region);assert.equal(region.events.size,0);h.click(region);
  assert.equal(h.sample.book.serialize(),before);assert.equal(h.sample.modalKind,'maps');
 }
 h.sample.rebuildLayout();assert.equal(h.sample.modalKind,'maps');assert.equal(h.sample.book.serialize(),before);
 const county=h.walk(h.sample.modal).find(n=>n.name==='Region-0');h.click(county);assert.equal(h.sample.modalKind,null);assert.equal(h.sample.book.serialize(),before);
});
test('opening the map catalog during delivery does not hide the required arrival demand',()=>{
 const b=doorstep();const saved=JSON.parse(b.serialize());saved.active.mode='running';saved.active.elapsed-=.001;saved.currentNode=saved.active.routes[0].nodes[0];
 const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
 const h=harness(OrderBook.restore(b.data,JSON.stringify(saved),()=>.99));h.click(h.walk(h.panel).find(n=>n.name==='Nav-map'));assert.equal(h.sample.modalKind,'maps');
 h.sample.update(.01);assert.equal(h.sample.modalKind,'maps');h.sample.rebuildLayout();assert.equal(h.sample.modalKind,'maps');h.sample.dismissDialog();assert.equal(h.sample.modalKind,'demand');
});

function realBook(random=()=>.1){
 const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
 const nodes=Array.from({length:81},(_,i)=>({id:String(i),x:i*200,y:0}));
 const data={title:'县城测试',width:16000,height:1000,nodes,roads:[{id:'r',nodes:nodes.map(n=>n.id),direction:0,speed:6,roughness:.1,kind:'secondary',width:8,bridge:false}],pois:nodes.map((n,i)=>({name:`地点${i}`,node:n.id,kind:i%4===0?'restaurant':'home'})),areas:[],buildings:[],labels:[],waterways:[]};
 return new OrderBook(data,random);
}
function doorstep(){
 const b=realBook();b.accept(b.list()[0].offer.id);b.depart();b.advance(99);b.finish();
 b.accept(b.list()[0].offer.id);b.depart();b.advance(99);assert.equal(b.mode,'arrived');return b;
}
test('profile replaces the title with identity and live balances while locked passive income is absent',()=>{
 const h=harness(realBook());assert.ok(h.walk(h.root).some(n=>n.name==='PlayerAvatar'));
 assert.ok(!h.text(h.root).includes('澄川骑手'));assert.ok(!h.text(h.root).includes('送外卖'));
 assert.ok(h.text(h.root).includes('100.00'));assert.ok(h.text(h.walk(h.root).find(n=>n.name==='WalletBadge')).includes('¥'));assert.ok(h.text(h.root).some(s=>s.includes('Lv.1')));
 assert.ok(!h.text(h.root).some(s=>/被动|每分钟|\/m|¥0\.00/.test(s)));
});
test('the vehicle entry opens the real garage and an unaffordable upgrade has no tap handler',()=>{
 const h=harness(realBook()),vehicle=h.walk(h.panel).find(n=>n.name==='Nav-vehicle');assert.ok(vehicle);h.click(vehicle);
 assert.equal(h.sample.modalKind,'garage');const gap=h.walk(h.sample.modal).find(n=>n.name.startsWith('Button-还差'));
 assert.ok(gap);assert.equal(gap.events.size,0);const balance=h.sample.book.player.cashCents;h.click(gap);assert.equal(h.sample.book.player.cashCents,balance);
});
test('merchant waiting communicates progress and running navigation cannot accept or upgrade',()=>{
 const b=realBook();b.accept(b.list()[0].offer.id);b.depart();assert.equal(b.tripStage,'collecting');
 const h=harness(b);assert.ok(h.text(h.panel).some(s=>s.includes('正在取餐中')&&s.includes('2秒')));
 for(const key of ['orders','vehicle']){const slot=h.walk(h.sample.panel).find(n=>n.name==='Nav-'+key);assert.ok(slot);assert.ok(slot.events.size>0);h.click(slot);}
 assert.equal(h.counts().opened,0);assert.equal(b.mode,'running');assert.equal(h.sample.modalKind,'garage');assert.ok(h.text(h.sample.modal).includes('配送中暂不可升级'));
 b.advance(1);h.sample.updateProgress();assert.ok(h.text(h.sample.panel).some(s=>s.includes('正在取餐中')&&s.includes('1秒')));
 b.advance(1.01);h.sample.updateProgress();assert.ok(!h.text(h.sample.panel).some(s=>s.includes('正在取餐中')));
});
test('doorstep demand opens a required modal with no bottom choices and cannot be skipped',()=>{
 const b=doorstep(),before=b.player.cashCents,h=harness(b);
 assert.equal(h.sample.modalKind,'demand');assert.ok(h.text(h.sample.modal).includes('顾客留言：放门口，别敲门'));
 assert.ok(!h.text(h.panel).some(s=>s==='敲门交付'||s==='按要求放门口'));
 assert.ok(!h.text(h.sample.modal).includes('关闭'));
 const shade=h.walk(h.sample.modal).find(n=>n.name==='Shade');h.click(shade);assert.equal(h.sample.modalKind,'demand');assert.equal(b.player.cashCents,before);
 h.sample.renderPanel();assert.equal(h.walk(h.sample.root).filter(n=>n.name==='CountyDialog'&&!n.destroyed).length,1);
 const choose=h.walk(h.sample.modal).find(n=>n.name==='Button-按要求放门口');h.click(choose);const after=b.player.cashCents;
 assert.equal(b.mode,'done');assert.ok(after>before);assert.equal(h.sample.modalKind,'receipt');h.click(choose);assert.equal(b.player.cashCents,after);
});
test('restoring and resizing a waiting delivery reopens its demand modal without early settlement',()=>{
 const b=doorstep(),{OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
 const restored=OrderBook.restore(b.data,b.serialize(),()=>.99),before=restored.player.cashCents,h=harness(restored);
 assert.equal(h.sample.modalKind,'demand');h.sample.rebuildLayout();assert.equal(h.sample.modalKind,'demand');assert.equal(restored.player.cashCents,before);
 const choose=h.walk(h.sample.modal).find(n=>n.name==='Button-敲门交付');h.click(choose);assert.equal(restored.mode,'done');
 assert.ok(restored.active.receipt.ratingDelta<0);assert.equal(restored.player.completedOrders,b.player.completedOrders+1);
});
test('damage event appears in transit once, survives layout rebuilding, freezes in background and expires after two seconds',()=>{
 let roll=.1;const b=realBook(()=>roll);b.accept(b.list()[0].offer.id);roll=0;b.depart();assert.notEqual(b.active.damage,'none');
 const h=harness(b);h.sample.update(2+b.progress.animationSeconds/2+.01);
 const visible=()=>h.walk(h.sample.root).some(n=>n.name==='DamageNotice'&&!n.destroyed);
 assert.equal(visible(),true);assert.ok(h.text(h.sample.root).includes('路程颠簸，餐品损坏了'));assert.equal(b.active.damageNoticeShown,true);assert.equal(h.sample.modalKind,null);
 h.sample.rebuildLayout();assert.equal(visible(),true);
 h.sample.hidden=true;h.sample.update(9);assert.equal(visible(),true);
 h.sample.hidden=false;h.sample.update(1);assert.equal(visible(),true);h.sample.update(1.01);assert.equal(visible(),false);
 h.sample.renderPanel();assert.equal(visible(),false);
});

// Actual page rendering on a short device: content must remain reachable without scaling text.
test('short-screen bills and receipts scroll their complete content with fixed safe actions',()=>{
 const b=realBook(),h=harness(b);h.setFrame({width:320,height:568});h.setSafeArea(height=>({x:0,y:64,width:720,height:height-174}));h.sample.rebuildLayout();
 const saved=b.serialize();h.sample.openBills();
 let nodes=h.walk(h.sample.modal),viewport=nodes.find(n=>n.name==='ScrollableContent');assert.ok(viewport,'bill has a scroll viewport');
 let content=viewport.children.find(n=>n.name==='Content');assert.ok(content.getComponent(h.UITransform).height>viewport.getComponent(h.UITransform).height);
 assert.equal(h.sample.billValues.length,12);assert.ok(h.text(content).includes('单日最高订单数'));assert.equal(b.serialize(),saved);
 b.accept(b.list()[0].offer.id);b.depart();b.advance(99);h.sample.openReceipt();nodes=h.walk(h.sample.modal);
 viewport=nodes.find(n=>n.name==='ScrollableContent');content=viewport.children.find(n=>n.name==='Content');
 for(const line of b.active.receipt.summary)assert.ok(h.text(content).some(s=>s.includes(line)));
 const action=nodes.find(n=>n.name==='Button-确认，继续接单');assert.ok(h.bounds(action).bottom>=-h.height()/2+64);
 assert.equal(h.walk(h.sample.modal).find(n=>n.name==='DialogCard').scaleX??1,1);
});

test('regrouped billing keeps live values attached to their original metrics',()=>{
 const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));
 const b=new OrderBook(realBook().data,()=>.1,()=> '2026-10-29'),h=harness(b),start=new Date(2026,9,29,12).getTime();h.sample.openBills();b.recordOnlineTime(start,start+3600000);h.sample.updateBills();
 const nodes=h.walk(h.sample.modal),metric=index=>h.text(nodes.find(n=>n.name==='BillMetric-'+index));
 assert.ok(metric(3).includes('钱包余额'));assert.ok(metric(3).includes('¥100.00'));
 assert.ok(metric(0).includes('今日收入'));assert.ok(metric(0).includes('¥0.00'));
 assert.ok(metric(4).includes('在线时长'));assert.ok(metric(4).includes('1:00:00'));
});

test('a valid long food description remains complete above routes and in delivery on a narrow device',()=>{
 const b=realBook();b.accept(b.list()[0].offer.id);Object.assign(b.active.offer,{food:'麻婆豆腐饭 · 3份',quantity:3,weightKg:3,fragility:'normal'});
 const h=harness(b);h.setFrame({width:320,height:568});h.sample.rebuildLayout();
 const description='麻婆豆腐饭 · 3份';
 const metadata=()=>h.walk(h.sample.panel).map(n=>n.getComponent(h.Label)).find(l=>l?.string===description);
 let info=metadata();assert.ok(info);assert.ok(info.node.getComponent(h.UITransform).height>=info.lineHeight,'food has a readable line');
 const route=h.walk(h.sample.panel).find(n=>n.name.startsWith('Route-'));assert.ok(h.bounds(info.node).bottom>h.bounds(route).top,'routes stay below all metadata lines');
 const content=route.parent;assert.ok(content.getComponent(h.UITransform).height>=-route.y+route.getComponent(h.UITransform).height/2+16,'the whole route remains scrollable');
 const action=h.walk(h.sample.panel).find(n=>n.name==='Button-去取餐'),sheet=h.walk(h.sample.panel).find(n=>n.name==='DeliverySheet'),[, ,mapHeight,,mapY]=h.sample.city.args;
 assert.ok(h.bounds(action).bottom>=-h.height()/2);assert.ok(Math.abs(mapY-mapHeight/2-h.bounds(sheet).top)<1);
 b.depart();h.sample.renderPanel();info=metadata();assert.ok(info.node.getComponent(h.UITransform).height>=info.lineHeight);
 const progress=h.walk(h.sample.panel).find(n=>n.name==='ProgressTrack');assert.ok(h.bounds(h.sample.tripLabel.node).bottom>h.bounds(progress).top,'delivery progress follows the reflowed stage text');
 b.advance(99);h.sample.renderPanel();info=metadata();const done=h.walk(h.sample.panel).find(n=>n.getComponent(h.Label)?.string==='配送完成 · 收入已到账');assert.ok(done);assert.ok(h.bounds(info.node).bottom>h.bounds(done).top,'completed delivery follows all metadata lines');
});

test('an open bill keeps its scroll position and readable wallet row when the balance grows',()=>{
 const b=realBook(),h=harness(b);h.setFrame({width:320,height:568});h.sample.rebuildLayout();h.sample.openBills();
 const modal=h.sample.modal,wallet=h.sample.billValues[3],content=wallet.node.parent.parent;content.setPosition(0,123);
 const raw=JSON.parse(b.serialize());raw.player.cashCents=123456789012345;
 const {OrderBook}=require(path.join(path.dirname(process.env.MAP_ROUTER_MODULE),'OrderBook.js'));h.sample.book=OrderBook.restore(b.data,JSON.stringify(raw),()=>.1);h.sample.updateBills();
 assert.equal(h.sample.modal,modal);assert.equal(content.y,123);assert.equal(h.sample.billValues[3],wallet);assert.equal(wallet.string,'¥1234567890123.45');
 assert.ok(wallet.node.getComponent(h.UITransform).height>=2*wallet.lineHeight,'the grown value has space for both lines');
 assert.ok(h.text(wallet.node.parent).includes('钱包余额'));assert.equal(h.sample.billValues[0].string,'¥0.00');
 h.sample.openBills();const reopened=h.sample.billValues[3];assert.equal(reopened.string,'¥1234567890123.45');assert.ok(reopened.node.getComponent(h.UITransform).height>=2*reopened.lineHeight);
});

test('receipt user dismiss finishes display only and restores an idle home without reopening lobby',()=>{
 const b=realBook();b.accept(b.list()[0].offer.id);b.depart();b.advance(99);if(b.mode==='arrived')b.settle(true);
 const h=harness(b),before=JSON.stringify(b.player),billing=JSON.stringify(b.billing);h.sample.openReceipt();const close=h.walk(h.sample.modal).find(n=>n.name==='CloseButton');h.click(close);
 assert.equal(b.mode,'idle');assert.equal(h.sample.modal,null);assert.equal(h.counts().opened,0);assert.equal(JSON.stringify(b.player),before);assert.equal(JSON.stringify(b.billing),billing);assert.ok(!h.walk(h.sample.panel).some(n=>n.name==='DeliverySheet'));
 const restored=b.constructor.restore(b.data,b.serialize());assert.equal(restored.mode,'idle');
});

test('receipt continue and lobby close return idle without reissuing settled assets',()=>{const b=realBook();b.accept(b.list()[0].offer.id);b.depart();b.advance(99);if(b.mode==='arrived')b.settle(true);const h=harness(b),before=JSON.stringify(b.player);h.sample.openReceipt();h.click(h.walk(h.sample.modal).find(n=>n.name==='Button-确认，继续接单'));assert.equal(b.mode,'idle');assert.equal(h.counts().opened,1);assert.equal(JSON.stringify(b.player),before);h.sample.continueOrders();assert.equal(h.counts().opened,1);h.openRealPhone();h.sample.closePhone();assert.equal(h.sample.phone,null);assert.ok(!h.walk(h.sample.panel).some(n=>n.name==='DeliverySheet'));});
test('receipt dismissal preserves the existing visible save failure protocol',()=>{const b=realBook();b.accept(b.list()[0].offer.id);b.depart();b.advance(99);if(b.mode==='arrived')b.settle(true);const h=harness(b);h.sample.store={available:false,message:'保存失败，请重试',save:()=>false};h.sample.openReceipt();h.click(h.walk(h.sample.modal).find(n=>n.name==='CloseButton'));assert.equal(b.mode,'idle');assert.ok(h.sample.noticeMessage.includes('保存失败'));});

test('CSS 12px header edges follow SHOW_ALL game scale rather than design pixels',()=>{const h=harness(realBook());h.setFrame({width:360,height:560});h.sample.rebuildLayout();const card=h.walk(h.sample.root).find(n=>n.name==='Header'),r=h.bounds(card),scale=Math.min(360/720,560/h.height());assert.ok(Math.abs((r.left+360)*scale-12)<.01);assert.ok(Math.abs((360-r.right)*scale-12)<.01);const locate=h.walk(h.sample.root).find(n=>n.name==='FollowRider');assert.ok(locate.getComponent(h.UITransform).width>=100.8);});

test('explicit locator forwards default zoom reset to the real camera',()=>{const h=harness(realBook());let reset=false;h.sample.city.locateAnimated=()=>{reset=true;};h.click(h.walk(h.sample.root).find(n=>n.name==='FollowRider'));assert.equal(reset,true);});

// ORDER-EXPERIENCE: measurable presentation contracts before implementation.
test('claim circle grows by 1.3 with proportional type inside a stable circular hit root',()=>{
 const h=harness(),claim=h.walk(h.root).find(n=>n.name==='Nav-orders');
 assert.equal(claim.getComponent(h.UITransform).width,145.6);assert.equal(claim.getComponent(h.UITransform).height,145.6);
 const caption=h.walk(claim).map(n=>n.getComponent(h.Label)).find(Boolean);assert.equal(caption.fontSize,57.2);
});
test('phone blue header includes status bar and has a separate shaded chassis',()=>{
 const h=harness(realBook());h.openRealPhone();const nodes=h.walk(h.sample.phone.node),frame=nodes.find(n=>n.name==='PhoneFrame'),header=nodes.find(n=>n.name==='AppHeader');
 assert.ok(h.bounds(header).top>=h.bounds(frame).top-14);assert.ok(nodes.some(n=>n.name==='PhoneShadow'));assert.ok(nodes.some(n=>n.name==='PhoneSide'));
});

test('rebuilding a planning order keeps route overview instead of overwriting it with rider locate',()=>{
 const b=realBook();b.accept(b.list()[0].offer.id);const h=harness(b);h.sample.rebuildLayout();assert.equal(h.sample.city.focused,true);
 const cards=h.walk(h.sample.panel).filter(n=>n.name.startsWith('Route-'));for(let i=0;i<cards.length;i++){h.sample.city.focused=false;h.click(cards[i]);assert.equal(h.sample.city.focused,true);assert.equal(h.sample.city.selected,i);assert.equal(b.active.selected,i);}
});

test('order sheet closes and reopens without changing the order, with twelve CSS pixels above the circular menu',()=>{
 const b=realBook();b.accept(b.list()[0].offer.id);const h=harness(b);h.setFrame({width:360,height:560});h.sample.rebuildLayout();const before=b.serialize();
 const get=name=>h.walk(h.sample.root).find(n=>n.name===name),sheet=get('DeliverySheet'),claim=get('Nav-orders'),scale=560/h.height();
 assert.ok((h.bounds(sheet).bottom-h.bounds(claim).top)*scale>=12-1e-7);
 assert.ok(h.text(sheet).includes('去取餐'));assert.ok(!h.text(sheet).includes('返回接单'));assert.ok(!h.text(sheet).includes('出发配送'));
 h.click(sheet.getChildByName('CloseButton'));assert.equal(get('DeliverySheet'),undefined);assert.equal(b.serialize(),before);
 h.click(get('Nav-orders'));assert.ok(get('DeliverySheet'));assert.equal(b.serialize(),before);
 for(const key of ['vehicle','map','bills']){h.click(get('Nav-'+key));assert.ok(h.sample.modal);h.sample.dismissDialog();assert.ok(get('DeliverySheet'));assert.equal(b.serialize(),before);}
});
