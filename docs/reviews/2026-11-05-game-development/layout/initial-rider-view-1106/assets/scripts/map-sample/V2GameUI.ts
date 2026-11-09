import { _decorator, BlockInputEvents, Component, isValid, Label, Mask, Node, ScrollView, sys, UITransform, Vec2 } from 'cc';
import { V2RuntimeController } from './V2RuntimeController';
import { CityData } from './MapTypes';
import { CityMap } from './CityMap';
import { col, item, label as baseLabel, tap } from './SampleUI';
import { experienceProgress, scrollContent, textHeight } from './PresentationLayout';
import { V2_SLOT_CONFIG as CONFIG } from '../domain/V2SlotEconomyConfig';
import { V2EconomySnapshot, V2Vehicle, V2DeliveryQuote, contractTerms } from '../domain/V2EconomySession';
import { slotVehicleEffects, slotVehicleUpgradeQuote, slotRiderEffects, slotRiderUpgradeQuote, slotRiderHireQuote, slotVehiclePurchaseQuote, slotMapPurchaseQuote, slotNextHirePriceCents } from '../domain/V2EconomyProfiles';
import { V2Load, V2Capacity, parseV2Load, parseV2Capacity, sameV2Load, totalV2Load, fitsV2Capacity } from '../domain/V2LoadRules';
import { V2FleetSnapshot } from '../domain/V2FleetSession';
import { summarizeLedger } from '../domain/V2Ledger';
import { queryProgressTargets } from '../domain/V2ProgressTargets';
const { ccclass } = _decorator;
type Page='首页'|'骑手'|'车辆'|'订单大厅'|'地图'|'账单';
type FundsState=Readonly<V2EconomySnapshot['state']>;
type UISnapshot=NonNullable<V2RuntimeController['snapshot']>;
type UpgradePresentation=Readonly<{detail:string;costCents:number}>;
const INK=UI.ink;
import { V2_SPACE as S, V2_CONTENT as CW, V2_LAYOUT as L, columnWidth } from './V2Spacing';
import { master as M, portraitDisplayName } from './V2ImageSkin';
import { UI, panel, action, glyph, mainAction, levelBadge, statusBadge, checkbox, portrait, mapPreview, navigationTile } from './V2ApprovedSkin';
import { vehicleSideArt } from './VehicleSideArt';
import { vehicleProductPreview } from './VehicleShowcase';
import { foodImage } from './FoodImages';
import { FOOD_CATALOG, foodPresentationById } from './FoodCatalog';
import { parseV2FoodRisk } from '../domain/V2TripRules';
const actionButton=action;
type RouteState=NonNullable<V2RuntimeController['routeSnapshot']>;
// Trip2 display compatibility only; never supplies a food/risk identity to the session.
function offerFood(id:string){let hash=2166136261;for(let i=0;i<id.length;i++)hash=Math.imul(hash^id.charCodeAt(i),16777619)>>>0;return FOOD_CATALOG[hash%FOOD_CATALOG.length];}
type OrderFoodPresentation=Readonly<{name:string;badge:'脆弱'|'普通'|'耐放'|'旧批';ruleText:string}>;
function orderFoodPresentation(order:{id:string;food?:unknown},tripVersion:number):OrderFoodPresentation {
 const hasFood=Object.prototype.hasOwnProperty.call(order,'food');
 if(tripVersion===2){
  if(hasFood)throw new Error('旧批食品记录无效');
  return {name:offerFood(order.id).name,badge:'旧批',ruleText:'旧批规则 · 沿用原普通风险'};
 }
 if(tripVersion!==3||!hasFood)throw new Error('配送食品记录缺失或版本无效');
 // Defensive shape/ID checks only: Game owns canonical order binding and risk validation.
 const contract=parseV2FoodRisk(order.food),food=foodPresentationById(contract.foodId);
 if(food.fragility!==contract.fragility)throw new Error('配送食品类别不一致');
 const badge=({fragile:'脆弱',normal:'普通',durable:'耐放'} as const)[food.fragility];
 return {name:food.name,badge,ruleText:`食品类别：${badge}`};
}
function label(...args:Parameters<typeof baseLabel>):Label {const result=baseLabel(...args);const lines=args[1].split('\n').length;result.fontFamily='PingFang SC, Microsoft YaHei, sans-serif';result.lineHeight=(args[4]??20)*S.lineHeight;if(lines>1)result.node.getComponent(UITransform)!.setContentSize(args[6]??600,(args[4]??20)*1.45*lines+6);return result;}
function coins(cents:number):string {return Number((cents/100).toFixed(2)).toString();}
function loadText(load:V2Load):string {return load.version==='slots-v1'?`${load.occupiedSlots}格`:`${load.weightKg}kg`;}
function foodTitleLayout(food:OrderFoodPresentation,load:V2Load,size:number,width:number){
 const value=`${food.name} ${loadText(load)}`,extra=Math.max(0,textHeight(value,size,width)-textHeight('字',size,width));
 return {value,extra,height:size*1.6+extra};
}
function capacityText(raw:V2Capacity):string {const capacity=parseV2Capacity(raw);return capacity.version==='slots-v1'?`${capacity.capacitySlots}格`:`${capacity.capacityKg}kg`;}
function loadSummary(loads:readonly V2Load[],raw:V2Capacity):string {
 const capacity=parseV2Capacity(raw),total=totalV2Load(loads,capacity);
 return capacity.version==='slots-v1'?`${total}/${capacity.capacitySlots}格`:`${total}/${capacity.capacityKg}kg`;
}
/** Container terms choose units; a missing new load never becomes one slot or legacy. */
function signedOrderLoad(order:{load?:unknown;weightKg?:number;quote:V2DeliveryQuote}):V2Load {
 const terms=contractTerms(order.quote);
 if(terms.version==='slots-v1'){
  const load=parseV2Load(order.load);
  if('weightKg' in order||!sameV2Load(load,terms.load))throw new Error('本批占用与合同不一致');
  return load;
 }
 if('load' in order)throw new Error('旧批不能混用格子占用');
 return parseV2Load({version:'kg-v1',weightKg:order.weightKg});
}
/** Preserve the existing goal metadata, but never display its legacy price/shortfall. */
function homeProgressTargets(state:FundsState){
 const mapPrices=CONFIG.maps.filter(map=>map.id!==CONFIG.maps[0].id&&!state.ownedMapIds.includes(map.id)).map(map=>slotMapPurchaseQuote(map.id).costCents).filter(cost=>cost>0);
 const prices:Record<string,number|null>={'first-car':slotVehiclePurchaseQuote(CONFIG.vehicles[0].id).costCents,'first-npc':slotNextHirePriceCents(state.riders),'first-paid-map':mapPrices.length?Math.min(...mapPrices):null};
 return queryProgressTargets(state).filter(target=>Object.prototype.hasOwnProperty.call(prices,target.id)).map(target=>{
  const priceCents=prices[target.id];return {...target,priceCents,shortfallCents:target.completed||priceCents===null?0:Math.max(0,priceCents-state.cashCents),canGo:!target.completed&&(priceCents===null||state.cashCents>=priceCents)};
 });
}
@ccclass('V2GameUI')
export class V2GameUI extends Component {
 public onRestartFailure:(()=>void)|null=null;
 private runtime!:V2RuntimeController;
 private root!:Node;
 private body!:Node;
 private map!:CityMap;
 private page:Page='首页';
 private model=3;
 private scrollOffsets=new Map<string,number>();
 private scrollViews=new Map<string,ScrollView>();
 private npcActivity=new Map<string,{status:Label;timer:Label}>();
 private selected=new Set<string>();
 private offers:ReturnType<V2RuntimeController['normalCandidates']>=[];
 private special:ReturnType<V2RuntimeController['enterLobby']>=null;
 private message='';
 private hud!:Label;
 private staminaHUD:Label|null=null;
 private ratingHUD:Label|null=null;
 private heroHUD:Label|null=null;
 private xpBar:Node|null=null;
 private heroLevel:Label|null=null;
 private elapsed=0;
 private routeViewKey='';
 private routeControlKey='';
 private lastRoutePhase='idle';
 private lastRouteTripId:number|null=null;
 private routeText:Label|null=null;
 private tripActionText:Label|null=null;
 private errorText:Label|null=null;
 private configureRider:string|null=null;
 private riderStatuses=new Map<string,Label>();
 private vehicleReturnRider:string|null=null;
 private supplyOpen=false;
 private fundsViews=new Map<Node,(state:FundsState)=>void>();
 private upgradeModal:Node|null=null;
 configure(runtime:V2RuntimeController,data:CityData,canvas:Node):void {
  this.runtime=runtime;this.root=item(canvas,'V2GameUI',0,0,720,1280);
  this.map=new CityMap(this.root,data,1280,()=>sys.openURL('https://www.openstreetmap.org/copyright'),0,128,{left:0,right:0},1280);
  const motion=runtime.routeMotion;
  if(motion){this.map.setRider(motion.position,0);this.map.locate(false);}
  this.body=item(this.root,'V2Pages');this.render();
 }
 private get state(){return (this.runtime.snapshot!.economy as V2EconomySnapshot).state;}
 private act(action:()=>unknown):void {try{action();this.message='';}catch(error){this.message=String(error);}this.render();}
 private text(parent:Node,text:string,y:number,x=0,w=640,size=22):void {label(parent,text,x,y,size,INK,w,false,'center');}
 private card(parent:Node,name:string,x:number,y:number,w:number,h:number):Node{return panel(parent,name,x,y,w,h);}
 private btn(parent:Node,text:string,x:number,y:number,w:number,action:()=>unknown,enabled=true):void {actionButton(parent,text,x,y,w,54,()=>this.act(action),enabled);}
 private navigate(page:Page):void {
  if(page==='订单大厅'&&this.page!=='订单大厅')this.act(()=>{
   this.runtime.setPaused(true);
   this.special=this.runtime.enterLobby('lobby-'+Date.now()+'-'+Math.random().toString(36).slice(2),Math.random(),Math.random());
   this.offers=this.runtime.normalCandidates();this.selected.clear();
  });
  if(page!=='车辆')this.vehicleReturnRider=null;
  this.page=page;this.supplyOpen=false;this.configureRider=null;this.render();
 }
 private render():void {
  this.closeUpgrade();this.fundsViews.clear();
  this.runtime.setPaused(this.supplyOpen||this.page!=='首页');
  const snapshot=this.runtime.snapshot!,state=(snapshot.economy as V2EconomySnapshot).state;
  for(const [key,scroll] of this.scrollViews)if(isValid(scroll,true))this.scrollOffsets.set(key,scroll.getScrollOffset().y);
  this.scrollViews.clear();this.npcActivity.clear();
  this.riderStatuses.clear();
  this.staminaHUD=null;this.ratingHUD=null;this.heroHUD=null;this.heroLevel=null;this.xpBar=null;
  for(const child of [...this.body.children]){child.active=false;child.destroy();}this.routeText=null;this.tripActionText=null;
  const full=this.page==='首页'&&!this.supplyOpen;
  if(!full)panel(this.body,'PageBackground',0,0,720,1280,'#DFF4FF','#DFF4FF');
  if(full){
   const h=panel(this.body,'HeroHUD',M.x(195),M.y(103),M.w(330),M.h(100),'#E5F6FFF2',UI.blue);
   portrait(h,0,-85,0,80,80);
   glyph(h,'pickup-pin',-32,17,22);this.heroHUD=label(h,'',49,17,22,INK,140,true,'center');
   const level=panel(h,'LevelBadge',-20,-20,53,25,UI.blue,UI.blue);this.heroLevel=label(level,'',0,0,18,'#FFFFFF',50,true,'center');
   panel(h,'XPTrack',70,-20,94,12,'#A3BDDC');this.xpBar=panel(h,'XP',24,-20,92,10,UI.blue,UI.blue);
   tap(h,()=>this.act(()=>this.navigate('骑手')));

  }else if(this.supplyOpen||this.page==='订单大厅'||this.page==='骑手'&&this.configureRider){
   // Only the four base-page titles are removed; HUD, configuration and navigation stay intact.
   label(this.body,this.supplyOpen?'补给':this.configureRider?'配置车辆':'订单大厅',M.x(200),M.y(45),M.w(65),INK,M.w(344),true,'left');
  }
  const cashMaster=this.page==='地图'?{x:768,y:51,w:300,h:66}:this.page==='账单'?{x:781,y:59,w:274,h:69}:{x:804,y:42,w:232,h:60};
  const cash=panel(this.body,'CashHUD',full?M.x(487):this.page==='订单大厅'?M.x(555):M.x(cashMaster.x),full?M.y(85):this.page==='订单大厅'?M.y(46):M.y(cashMaster.y),full?M.w(227):M.w(this.page==='订单大厅'?237:cashMaster.w),M.h(full?60:cashMaster.h),'#F4FCFF',UI.blue);
  if(this.page==='订单大厅')label(cash,'¥',-66,0,29,INK,38,true,'center');
  else if(this.page!=='账单')glyph(cash,'coin',-66,0,34);
  this.hud=label(cash,'',this.page==='账单'?-18:-3,0,24,INK,this.page==='账单'?130:100,true,'center');
  const walletPlus=item(cash,'WalletDetails',65,0,30,34);glyph(walletPlus,'plus',0,0,30);tap(walletPlus,()=>this.walletDetails());
  if(full||this.page==='订单大厅'){
   const st=panel(this.body,'StaminaHUD',full?M.x(700):M.x(805),full?M.y(85):M.y(46),full?M.w(185):M.w(230),M.h(60),'#F4FCFF',UI.blue);
   // Separate full 100/100 from its icons without shrinking the value or moving the HUD.
   glyph(st,'energy',full?-57:-53,0,full?22:30);
   this.staminaHUD=label(st,'',full?2:-1,0,21,INK,84,true,'center');glyph(st,'plus',full?58:53,0,full?18:28);
   tap(st,()=>this.act(()=>{this.supplyOpen=true;}));
  }
  if(full){const rating=panel(this.body,'RatingHUD',M.x(860),M.y(85),M.w(118),M.h(60),'#F4FCFF',UI.blue);glyph(rating,'heart',-29,0,30);this.ratingHUD=label(rating,'',15,0,23,INK,60,true,'center');}
  this.refreshHUD(state);
  this.errorText=label(this.body,this.message,0,full?455:549,16,'#BF3E12',660,false,'center');
  if(this.supplyOpen)this.supplies(snapshot);
  else {
   if(this.page==='首页')this.home(snapshot);if(this.page==='骑手')this.riders(state);if(this.page==='车辆')this.vehicles(state);
   if(this.page==='地图')this.maps(state);if(this.page==='账单')this.bills(state);if(this.page==='订单大厅')this.orders(snapshot);
  }
  panel(this.body,'NavigationBase',0,M.y(1591),720,M.h(164),'#17365B','#17365B');
  const pages:Page[]=['骑手','车辆','订单大厅','地图','账单'];
  pages.forEach((p,i)=>{
   const x=M.x([90,325,470,615,850][i]),current=this.page===p&&!this.supplyOpen;
   if(i===2)return;
   const n=navigationTile(this.body,'Navigation-'+p,x,M.y(1583),M.w(i===1||i===3?290:180),M.h(145),current,i===1?'right':i===3?'left':null),opticalX=i===1?-39:i===3?39:0;
   glyph(n,current?'close':['riders','vehicles','','maps','bills'][i],opticalX,current?0:19,current?62:52);
   if(!current)label(n,p,opticalX,-31,33,INK,132,true,'center');tap(n,()=>this.act(()=>this.navigate(current?'首页':p)));
  });
  mainAction(this.body,this.page==='订单大厅'?'×':'抢单',0,M.y(1565),()=>this.act(()=>this.navigate(this.page==='订单大厅'?'首页':'订单大厅')));
 }

 private refreshHUD(s:FundsState=this.state):void {
  const t=this.runtime.tripState;
  this.hud.string=coins(s.cashCents);
  if(this.staminaHUD)this.staminaHUD.string=`${Math.floor(t?.stamina??100)}/100`;
  if(this.ratingHUD)this.ratingHUD.string=String(t?.rating??100);
  if(this.heroHUD){const xp=experienceProgress(s.heroExperience);this.heroHUD.string=CONFIG.maps[s.selectedMapId-1].name+' ›';if(this.heroLevel)this.heroLevel.string=`Lv.${xp.level}`;if(this.xpBar){this.xpBar.setScale(Math.max(.01,xp.progress),1,1);this.xpBar.setPosition(24+46*xp.progress,-20);}}
 }

 /** Refresh only money-dependent labels/actions at the existing HUD cadence. */
 private bindFunds(view:Node,refresh:(state:FundsState)=>void,initial:FundsState=this.state):void {
  this.fundsViews.set(view,refresh);refresh(initial);
 }
 private refreshFunds(state:FundsState):void {
  for(const [view,refresh] of this.fundsViews){
   if(!isValid(view,true)){this.fundsViews.delete(view);continue;}
   if(view.activeInHierarchy)refresh(state);
  }
 }
 private closeUpgrade():void {
  const modal=this.upgradeModal;this.upgradeModal=null;
  if(modal){this.fundsViews.delete(modal);if(isValid(modal,true)){modal.active=false;modal.destroy();}}
 }

 private home(snap:UISnapshot):void {
  const state=(snap.economy as V2EconomySnapshot).state,allTargets=homeProgressTargets(state);
  const targets=['first-car','first-npc','first-paid-map'].map(id=>allTargets.find(t=>t.id===id)).filter((t):t is NonNullable<typeof t>=>!!t&&!t.completed);
  if(targets.length){
   const target=targets[0],c=panel(this.body,'ProgressTarget',-62,-400,558,83,'#EFFAFFA6');
   label(c,target.label,-103,19,21,INK,310,true,'left');const progress=label(c,`${target.progress}/${target.target} · 还差 ${(target.shortfallCents/100).toFixed(2)}金币`,-103,-16,16,UI.muted,310,false,'left');
   this.bindFunds(c,state=>{const current=homeProgressTargets(state).find(row=>row.id===target.id);if(current)progress.string=`${current.progress}/${current.target} · 还差 ${(current.shortfallCents/100).toFixed(2)}金币`;},state);
   action(c,'›',220,0,72,58,()=>this.act(()=>this.navigate(({vehicles:'车辆',riders:'骑手',maps:'地图'} as const)[target.destination])),true,false);
  }
  this.homeNPCs(state);
  // Home keeps HUD/targets/counters; delivery status and receipts live in their detail pages.
  // Do not create floating trip or settlement labels over the map.
  // Keep the two map controls in separate rows above the bottom navigation.
  const locate=panel(this.body,'LocateRider',290,-388,64,64,'#F2FBFF',UI.blue);glyph(locate,'target',0,0,56);tap(locate,()=>this.map.locate(true));
  const supply=panel(this.body,'SupplyShortcut',290,425,76,76,'#EFFAFFEE',UI.blue);glyph(supply,'expense',0,0,54);tap(supply,()=>this.act(()=>{this.supplyOpen=true;}));
  label(this.body,`已送 ${state.heroCompletedOrders} 单 · 团队 ${state.npcCompletedOrders} 单`,-68,-473,17,INK,440,false,'left');
  if(snap.batchIds.length){
   const group=this.pickupGroup();
   action(this.body,group?`${group.name} · ${group.count}份 ›`:'余单 / 路线',-190,-325,260,48,()=>this.act(()=>this.navigate('订单大厅')),true,false);
   this.tripButton(this.body,95,-325,260,48);
  }
 }

 /** Capture real offsets before each redraw and restore after ScrollView's first layout pass. */
 private scrolling(key:string,top:number,bottom:number,height:number):Node {
  const content=scrollContent(this.body,CW,top,bottom,height),scroll=content.parent!.getComponent(ScrollView)!;
  this.scrollViews.set(key,scroll);
  const saved=this.scrollOffsets.get(key)??0;
  const restore=()=>{if(!isValid(scroll,true)||this.scrollViews.get(key)!==scroll)return;scroll.stopAutoScroll();scroll.scrollToOffset(new Vec2(0,Math.max(0,Math.min(saved,scroll.getMaxScrollOffset().y))),0);};
  const offset=Math.max(0,Math.min(saved,Math.max(0,height-(top-bottom))));
  content.setPosition(0,(top-bottom)/2+offset);this.scheduleOnce(restore,0);return content;
 }
 private homeNPCs(state:FundsState):void {
  const npcs=state.riders.filter(r=>r.id!=='hero');if(!npcs.length)return;
  const height=Math.min(3,npcs.length)*76;
  const content=scrollContent(this.body,258,505,505-height,npcs.length*76);
  content.parent!.setPosition(-207,505-height/2);
  const scroll=content.parent!.getComponent(ScrollView)!;this.scrollViews.set('home:npcs',scroll);
  const saved=this.scrollOffsets.get('home:npcs')??0;
  const restore=()=>{if(isValid(scroll,true)&&this.scrollViews.get('home:npcs')===scroll)scroll.scrollToOffset(new Vec2(0,Math.min(Math.max(0,saved),scroll.getMaxScrollOffset().y)),0);};content.setPosition(0,height/2+Math.min(Math.max(0,saved),Math.max(0,npcs.length*76-height)));this.scheduleOnce(restore,0);
  npcs.forEach((r,i)=>{
   const card=panel(content,'Rider-Activity-'+r.id,0,-36-i*76,252,70,'#EFFAFFDB');
   portrait(card,Number(r.id.slice(4)),-97,0,44,58);this.riderName(card,r.id,-18,17,104,21);
   const status=label(card,'',90,17,18,'#009749',68,true,'center');
   const timer=label(card,'',23,-16,17,UI.muted,186,false,'left');
   this.npcActivity.set(r.id,{status,timer});tap(card,()=>this.act(()=>{this.page='骑手';this.configureRider=r.id;}));
  });this.refreshNPCActivity();
 }
 private refreshNPCActivity(snap:UISnapshot=this.runtime.snapshot!):void {
  if(!this.npcActivity.size)return;
  const fleet=(snap.fleet as V2FleetSnapshot).fleet,state=(snap.economy as V2EconomySnapshot).state;
  for(const [id,view] of this.npcActivity){
   const rider=state.riders.find(r=>r.id===id),batch=fleet.batches.find(b=>b.riderId===id),next=batch?.orders[batch.paidCount];
   const working=fleet.quotaMs>0&&!!batch&&!!next;
   view.status.string=working?'配送中':'空闲';view.status.color=col(working?UI.blue:'#009749');
   if(working&&batch&&next){const seconds=Math.max(0,Math.ceil((next.dueMs-batch.elapsedMs)/1000));view.timer.string=`下一单 ${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`;}
   else view.timer.string=!rider?.vehicleId?'待配车':fleet.quotaMs<=0?'经营时长已用完':'等待配送';
  }
 }

 private walletDetails():void {
  const modal=panel(this.root,'WalletShade',0,0,720,1280,'#17365BAA','#17365BAA');modal.addComponent(BlockInputEvents);
  const sheet=panel(modal,'Vehicle-WalletDetails',0,0,610,330);
  const showCoin=this.page!=='账单'||this.supplyOpen;
  if(showCoin)glyph(sheet,'coin',-244,112,38);
  label(sheet,'金币',showCoin?-24:0,112,30,INK,showCoin?390:544,true,showCoin?'left':'center');
  label(sheet,coins(this.state.cashCents),0,38,44,INK,544,true,'center');
  label(sheet,'配送获得金币，收支可在账单中查看',0,-24,22,UI.muted,544,false,'center');
  action(sheet,'关闭',-140,-112,250,52,()=>modal.destroy(),true,false);
  action(sheet,'查看账单',140,-112,250,52,()=>{modal.destroy();this.act(()=>this.navigate('账单'));},true,false);
 }

 private supplies(snap:UISnapshot):void {
  const t=this.runtime.tripState;if(!t)return;
  const options=this.runtime.supplyOptions(),active=snap.batchIds.length>0,state=(snap.economy as V2EconomySnapshot).state;
  const route=this.runtime.routeSnapshot,serviceInProgress=route?.phase==='service'&&route.serviceCharged===true;
  const beforeDeparture=active&&route?.phase==='planned';
  action(this.body,'‹ 返回原页',-226,516,224,42,()=>this.act(()=>{this.supplyOpen=false;}),true,false);
  action(this.body,'回到首页',226,516,224,42,()=>this.act(()=>this.navigate('首页')),true,false);
  const c=this.scrolling('supplies',482,-490,options.length*206+886);
  const energy=panel(c,'Order-SupplyEnergy',0,-62,CW,112,'#F2FBFF');
  glyph(energy,'energy',-299,21,38);label(energy,'原地补给',-176,23,25,INK,190,true,'left');
  label(energy,`${Math.floor(t.stamina)} / 100`,239,23,28,INK,170,true,'right');
  panel(energy,'StaminaTrack',0,-17,CW-36,13,'#ADCBE2','#ADCBE2');
  const fraction=Math.max(0,Math.min(1,t.stamina/100)),barWidth=CW-40;
  if(fraction>0)panel(energy,'StaminaFill',-barWidth*(1-fraction)/2,-17,barWidth*fraction,10,'#13AA8D','#13AA8D');
  label(energy,t.action?'补给进行中，返回首页继续计时':t.stamina>=100?'体力已满':serviceInProgress?'取送服务中，请完成后补给':'选择时暂停主角；确认后回首页继续计时',0,-41,17,UI.muted,CW-26,false,'center');
  const available=t.stamina<100&&!t.action&&!serviceInProgress;
  const supply=(kind:Parameters<V2RuntimeController['supply']>[0],source:'purchase'|'inventory'='purchase')=>{this.runtime.supply(kind,source);this.supplyOpen=false;this.navigate('首页');};
  options.forEach((option,i)=>{
   const card=panel(c,'Order-Supply-'+option.id,0,-232-i*206,CW,190,'#F2FBFF');
   // No bottle/water asset exists. Use energy art rather than inventing a food image.
   const food=({noodles:'鲜汤面',fastFood:'汉堡',milkTea:'奶茶',premiumMeal:'寿司'} as Record<string,string>)[option.id];
   if(food)foodImage(card,food,-265,22,102);else glyph(card,'energy',-265,22,68);
   label(card,option.name,-30,64,27,INK,350,true,'left');
   label(card,`实恢 +${Number(option.actualRestore.toFixed(1))} 点`,-45,28,22,'#009749',320,true,'left');
   label(card,`${option.durationSeconds}秒 · ${!active?'无配送期限推进':beforeDeparture?'未出发，不耗配送期限':`期限推进 ${option.gameSeconds}秒`}`,0,-4,18,UI.muted,410,false,'left');
   label(card,`库存 ${option.quantity}`,258,61,20,INK,130,true,'right');
   label(card,`${option.unlocked?'已开放':'未开放'} · 最高已购地图达到${CONFIG.maps[option.unlockMapId-1].name}`,-10,-35,17,option.unlocked?UI.muted:'#BF3E12',CW-28,false,'center');
   const purchase=item(card,'SupplyPurchase',-157,-68,330,44);
   const canPurchase=(state:FundsState)=>available&&option.unlocked&&state.cashCents>=option.costCents;
   let purchaseEnabled:boolean|undefined,purchaseButton:Node|null=null;
   const refreshPurchase=(state:FundsState)=>{
    const enabled=canPurchase(state);if(enabled===purchaseEnabled)return;purchaseEnabled=enabled;
    if(purchaseButton){purchaseButton.active=false;purchaseButton.destroy();}
    const button=action(purchase,`购买并使用 ${(option.costCents/100).toFixed(2)}金币`,0,0,330,44,()=>{
     if(purchaseButton!==button||!isValid(button,true)||!button.activeInHierarchy)return;
     const current=this.state;if(!canPurchase(current)){refreshPurchase(current);return;}
     this.act(()=>supply(option.id));
    },enabled);purchaseButton=button;
   };
   this.bindFunds(purchase,refreshPurchase,state);
   action(card,option.quantity>0?'使用库存':'暂无库存',181,-68,298,44,()=>this.act(()=>supply(option.id,'inventory')),available&&option.unlocked&&option.quantity>0,false);
  });
  const after=options.length*206+154;
  const rest=panel(c,'Order-FreeRest',0,-after-68,CW,124,'#F2FBFF');
  glyph(rest,'clock',-291,25,36);label(rest,'免费休息',-159,27,25,INK,190,true,'left');
  label(rest,active?beforeDeparture?'10秒 · 未出发，不耗配送期限':'10秒 · 期限推进10分钟':'20秒 · 无配送期限推进',111,27,18,UI.muted,358,false,'right');
  label(rest,`实际恢复 ${Number(Math.min(active?20:100,100-t.stamina).toFixed(1))} 点`,-194,-28,20,'#009749',250,true,'left');
  action(rest,'免费休息',197,-28,236,46,()=>this.act(()=>supply('rest')),available,false);
  const policy=t.autoSupplyPolicy;
  const configure=(patch:Partial<Parameters<V2RuntimeController['configureAutoSupply']>[0]>)=>this.runtime.configureAutoSupply({enabled:policy.enabled,budgetCents:policy.budgetCents,kind:policy.kind,allowPaid:policy.allowPaid,useInventory:policy.useInventory,...patch});
  const auto=panel(c,'Order-AutoSupply',0,-after-250,CW,214,'#F2FBFF');
  label(auto,'自动补给',-203,77,26,INK,220,true,'left');
  action(auto,policy.enabled?'已开启 · 关闭':'已关闭 · 开启',192,77,254,44,()=>this.act(()=>configure({enabled:!policy.enabled})),true,false);
  label(auto,'库存授权',-238,23,23,INK,160,true,'left');
  label(auto,'允许自动消耗已持有补给',-128,-12,18,UI.muted,382,false,'left');
  action(auto,policy.useInventory?'已允许 · 关闭':'未允许 · 开启',192,13,254,44,()=>this.act(()=>configure({useInventory:!policy.useInventory})),true,false);
  label(auto,'付费授权',-238,-53,23,INK,160,true,'left');
  label(auto,'单独授权，且受总预算与余额限制',-91,-87,17,UI.muted,450,false,'left');
  action(auto,policy.allowPaid?'已允许 · 关闭':'未允许 · 开启',192,-63,254,44,()=>this.act(()=>configure({allowPaid:!policy.allowPaid})),true,false);
  const budget=panel(c,'Order-SupplyBudget',0,-after-480,CW,222,'#F2FBFF');
  label(budget,'自动付费总预算',-184,78,25,INK,280,true,'left');glyph(budget,'coin',198,78,30);
  label(budget,`${(policy.budgetCents/100).toFixed(2)}`,269,78,29,'#FF7800',100,true,'right');
  label(budget,`已花 ${(policy.spentCents/100).toFixed(2)} · 剩余 ${((policy.budgetCents-policy.spentCents)/100).toFixed(2)}金币`,0,34,22,INK,CW-28,true,'center');
  [0,5,10].forEach((coins,i)=>action(budget,`${coins}金币`,(i-1)*218,-18,204,45,()=>this.act(()=>configure({budgetCents:coins*100})),coins*100>=policy.spentCents,false));
  label(budget,'开关不会重置已花金额；库存消耗不计现金预算。',0,-67,17,UI.muted,CW-28,false,'center');
  label(budget,'库存获单独授权时优先使用；无合适补给时不自动购买。',0,-94,16,UI.muted,CW-28,false,'center');
 }
 /** Stop membership is authoritative; old single-member snapshots remain display-safe. */
 private pickupGroup(route:RouteState|null=this.runtime.routeSnapshot):{ids:string[];name:string;count:number}|null {
  if(!route)return null;
  const stop=route.stops[route.phase==='ready'?route.cursor-1:route.cursor];
  if(stop?.kind!=='pickup')return null;
  const ids=stop.orderIds?.length?stop.orderIds:[stop.orderId];
  return {ids,name:route.orders.find(order=>order.id===stop.orderId)?.pickupName||'取餐地点未记录',count:ids.length};
 }
 private tripControl():{text:string;enabled:boolean;invoke:()=>void} {
  const route=this.runtime.routeSnapshot,t=this.runtime.tripState,none=()=>{};
  if(t?.action)return {text:`${t.action.kind==='rest'?'休息':'补给'} ${t.action.elapsedSeconds.toFixed(1)}/${t.action.durationSeconds}秒`,enabled:false,invoke:none};
  if(t?.blocked&&!(route?.phase==='service'&&route.serviceCharged))return {text:'体力不足 · 请补给',enabled:false,invoke:none};
  if(route?.phase==='pickup'){
   const group=this.pickupGroup(route);
   return {text:group&&group.count>1?`到店取餐 · ${group.count}份`:'到店取餐',enabled:true,invoke:()=>this.runtime.pickup()};
  }
  if(route?.phase==='ready')return {text:route.stops[route.cursor]?.kind==='dropoff'?'去配送 ›':'去下一站 ›',enabled:true,invoke:()=>this.runtime.continueTrip()};
  if(route?.phase==='service')return {text:`${route.stops[route.cursor]?.kind==='pickup'?'取餐':'交付'} ${route.serviceSeconds.toFixed(1)}/${route.stops[route.cursor]?.kind==='pickup'?2:1}秒`,enabled:false,invoke:none};
  return {text:t?.blocked?'体力不足 · 请补给':route?.phase==='planned'?'请先选择路线':route?.phase==='travelling'?'配送中':route?.phase==='finished'?'本批已完成':'暂无配送',enabled:false,invoke:none};
 }
 private tripButton(parent:Node,x:number,y:number,w:number,h:number):void {
  const control=this.tripControl();
  const button=action(parent,control.text,x,y,w,h,()=>this.act(()=>{control.invoke();this.navigate('首页');}),control.enabled);
  this.tripActionText=button.getComponentInChildren(Label);
 }
 private tripStage():string {
  const t=this.runtime.tripState,route=this.runtime.routeSnapshot;
  if(t?.action){const name=t.action.kind==='rest'?'免费休息':this.runtime.supplyOptions().find(o=>o.id===t.action!.kind)?.name||'补给';return `${name}中 · ${Math.floor(t.action.elapsedSeconds)}/${t.action.durationSeconds}秒`;}
  if(t?.blocked&&!(route?.phase==='service'&&route.serviceCharged))return '体力不足 · 原地补给或免费休息';
  if(route?.phase==='service')return `${route.stops[route.cursor]?.kind==='pickup'?'取餐服务':'顾客交付'}中 · ${route.serviceSeconds.toFixed(1)}/${route.stops[route.cursor]?.kind==='pickup'?2:1}秒`;
  if(route?.phase==='ready')return `取餐已完成 · 等待${route.stops[route.cursor]?.kind==='dropoff'?'去配送':'去下一站'}`;
  return ({idle:'当前没有配送',planned:'待选择路线出发',travelling:'沿原道路配送中',pickup:'已到店 · 等待取餐',finished:'本批配送已完成'} as const)[route?.phase||'idle'];
 }
 private riders(s:FundsState=this.state):void {
  if(this.configureRider){this.vehicleConfiguration(this.configureRider,s);return;}
  const gap=L.riderRowGap,cardW=columnWidth(2,gap),innerW=cardW-2*S.card,buttonW=(innerW-S.gap)/2;
  const portraitX=-cardW/2+S.card+46,infoLeft=-cardW/2+S.card+92+S.imageText,infoW=cardW/2-S.card-infoLeft,infoX=infoLeft+infoW/2;
  const percent=(value:number)=>Number((value*100).toFixed(1));
  const todayDayKey=this.runtime.ledgerQuery.todayDayKey;
  // Keep exact money and readable fonts; long real values grow only their grid row.
  const wrappedExtra=(value:string,size:number,width:number)=>Math.max(0,textHeight(value,size,width)-textHeight('字',size,width));
  const cards=Array.from({length:31},(_,i)=>{
   const id=i===0?'hero':`npc-${i}`,r=s.riders.find(r=>r.id===id);
   const hire=i>0&&!r?slotRiderHireQuote(id):null,upgrade=i>0&&r&&r.level<CONFIG.levels.length?slotRiderUpgradeQuote(id,r.level):null;
   const rows:{value:string;color:string;height:number}[]=[];
   if(i===0){
    const xp=experienceProgress(s.heroExperience);rows.push({value:`经验 ${xp.current}/${xp.required}`,color:INK,height:0});
   }else {
    const e=slotRiderEffects(id,r?.level??1),income=`收入加成 +${percent(e.incomeFactor-1)}%`,saving=`取送省时 ${percent(e.fixedServiceReduction)}%`;
    if(r){
     const today=s.ledger.entries.filter(entry=>entry.category==='npc_delivery'&&entry.dayKey===todayDayKey&&entry.detail.riderId===id).reduce((n,entry)=>n+entry.amountCents,0);
     rows.push({value:`今日收入 ${coins(today)}`,color:'#FF7800',height:0},{value:income,color:INK,height:0},{value:saving,color:INK,height:0});
    }else rows.push({value:income,color:INK,height:0},{value:saving,color:INK,height:0},{value:`价格 ${coins(hire!.costCents)}金币`,color:'#FF7800',height:0});
   }
   rows.forEach(row=>{row.height=26+wrappedExtra(row.value,20,infoW);});
   const upgradeText=upgrade?`升级骑手 ${coins(upgrade.costCents)}`:'已满级';
   const buttonHeight=38+(i>0&&r?wrappedExtra(upgradeText,22,buttonW-10):0);
   return {i,id,r,hire,upgrade,upgradeText,rows,buttonHeight,height:L.riderCardHeight+rows.reduce((n,row)=>n+row.height-26,0)+buttonHeight-38};
  });
  const rowHeights=Array.from({length:Math.ceil(cards.length/2)},(_,row)=>Math.max(...cards.slice(row*2,row*2+2).map(card=>card.height)));
  const rowTops:number[]=[];let contentHeight=0;rowHeights.forEach(height=>{rowTops.push(contentHeight);contentHeight+=height+gap;});
  const c=this.scrolling('riders',M.y(L.riderTop),M.y(L.riderBottom),contentHeight);
  cards.forEach(({i,id,r,hire,upgrade,upgradeText,rows,buttonHeight})=>{
   const row=Math.floor(i/2),cardH=rowHeights[row],x=(i%2===0?-1:1)*(cardW+gap)/2;
   const card=this.card(c,'Rider-'+id,x,-rowTops[row]-cardH/2,cardW,cardH);
   portrait(card,i,portraitX,cardH/2-(i===0?85:57),92,i===0?144:104);
   this.riderIdentity(card,id,i===0?experienceProgress(s.heroExperience).level:r?.level??1,infoLeft,cardH/2-26);
   if(i>0){
    const status=statusBadge(card,r?'待命':'未招募',portraitX,cardH/2-125,!!r,100,24);
    status.fontSize=18;status.lineHeight=23;status.enableWrapText=false;status.overflow=Label.Overflow.CLAMP;status.node.getComponent(UITransform)!.setContentSize(92,24);
    if(r)this.riderStatuses.set(id,status);
   }
   if(i===0){
    const xp=experienceProgress(s.heroExperience),line=rows[0],trackY=cardH/2-98-(line.height-26);
    this.riderLine(card,line.value,infoX,cardH/2-51-line.height/2,infoW,line.height);
    panel(card,'XPTrack',infoX,trackY,infoW,12,'#AECBE7');panel(card,'XPFill',infoX-infoW/2*(1-xp.progress),trackY,Math.max(2,infoW*xp.progress),10,UI.blue,UI.blue);
   }else {
    let top=cardH/2-47;rows.forEach(line=>{this.riderLine(card,line.value,infoX,top-line.height/2,infoW,line.height,20,line.color);top-=line.height+3;});
   }
   const buttonY=-cardH/2+3+buttonHeight/2;
   if(r){
    this.riderAction(card,'配置车辆',i===0?infoX:-(buttonW+S.gap)/2,buttonY,i===0?infoW:buttonW,buttonHeight,()=>this.act(()=>{this.configureRider=id;}),true,false);
    if(i>0)this.riderAction(card,upgradeText,(buttonW+S.gap)/2,buttonY,buttonW,buttonHeight,()=>{if(upgrade)this.showUpgrade('升级骑手',state=>{
     const rider=state.riders.find(row=>row.id===id),quote=rider&&rider.level<CONFIG.levels.length?slotRiderUpgradeQuote(id,rider.level):null;
     return rider&&quote?{detail:`等级 ${rider.level} → ${quote.nextLevel}\n培养收入 +${percent(quote.current.incomeFactor/quote.current.baseIncomeFactor-1)}% → +${percent(quote.next.incomeFactor/quote.next.baseIncomeFactor-1)}%\n取送省时 ${percent(quote.current.fixedServiceReduction)}% → ${percent(quote.next.fixedServiceReduction)}%`,costCents:quote.costCents}:null;
    },()=>this.runtime.command({type:'upgradeRider',riderId:id}));},!!upgrade);
   }else if(hire)this.riderAction(card,'招募',infoX,buttonY,infoW,buttonHeight,()=>this.act(()=>this.runtime.command({type:'hireRider',riderId:id})),s.hireCount<30);
  });
  this.refreshRiderStatuses();
 }

 private riderLine(parent:Node,value:string,x:number,y:number,width:number,height:number,size=20,color=INK):Label {
  const text=label(parent,value,x,y,size,color,width,true,'left');text.enableWrapText=true;text.lineHeight=size*S.lineHeight;text.overflow=Label.Overflow.CLAMP;
  text.node.getComponent(UITransform)!.setContentSize(width,height);return text;
 }
 private riderAction(parent:Node,value:string,x:number,y:number,width:number,height:number,fn:()=>void,enabled=true,primary=true):void {
  const button=action(parent,value,x,y,width,height,fn,enabled,primary),text=button.getComponentInChildren(Label)!;
  text.fontSize=22;text.lineHeight=22*S.lineHeight;text.enableWrapText=true;text.overflow=Label.Overflow.CLAMP;
  text.node.getComponent(UITransform)!.setContentSize(width-10,height-6);
 }
 /** Measure again after the real portrait name arrives; Lv follows the ink, never a fixed remote slot. */
 private riderIdentity(parent:Node,id:string,level:number,left:number,y:number,size=26):void {
  const name=label(parent,id==='hero'?'主角':`骑手 ${id.slice(4)}`,0,y,size,INK,1,true,'left');
  const marker=item(parent,'RiderInlineLevel',0,y,0,24),levelText=label(marker,`Lv.${level}`,0,0,16,'#FFFFFF',1,true,'center');
  levelText.enableWrapText=false;levelText.overflow=Label.Overflow.NONE;levelText.updateRenderData(true);
  const badgeW=Math.max(48,Math.ceil(levelText.node.getComponent(UITransform)!.width)+8);
  const background=panel(marker,'LevelBadge',0,0,badgeW,24,UI.blue,UI.blue);background.setSiblingIndex(0);
  levelText.overflow=Label.Overflow.CLAMP;levelText.lineHeight=21;levelText.node.getComponent(UITransform)!.setContentSize(badgeW-8,24);
  marker.getComponent(UITransform)!.setContentSize(badgeW,24);
  const layout=(value:string)=>{
   if(!isValid(parent,true)||!isValid(name,true)||!isValid(marker,true))return;
   name.string=value;name.enableWrapText=false;name.overflow=Label.Overflow.NONE;name.lineHeight=size*S.lineHeight;name.updateRenderData(true);
   const width=name.node.getComponent(UITransform)!.width;
   name.overflow=Label.Overflow.CLAMP;name.node.getComponent(UITransform)!.setContentSize(width,Math.ceil(size*1.4));
   name.node.setPosition(left+width/2,y);marker.setPosition(left+width+6+badgeW/2,y);
  };
  layout(name.string);
  if(id!=='hero')void portraitDisplayName(id).then(value=>{if(value)layout(value);});
 }
 private refreshRiderStatuses(snap:UISnapshot=this.runtime.snapshot!):void {
  if(!this.riderStatuses.size)return;
  const s=(snap.economy as V2EconomySnapshot).state,fleet=(snap.fleet as V2FleetSnapshot).fleet;
  for(const [id,status] of this.riderStatuses){
   const rider=s.riders.find(r=>r.id===id);
   status.string=!rider?.vehicleId?'待配车':fleet.quotaMs>0&&fleet.batches.some(b=>b.riderId===id)?'配送中':'待命';
  }
 }

 /** Instance labels and art selection are presentation only; effects and prices stay authoritative. */
 private vehicleName(vehicle:V2Vehicle):string {
  return vehicle.modelId==='starter'?'初始旧车':typeof vehicle.modelId==='number'?CONFIG.vehicles[vehicle.modelId-1].name:'保留车辆';
 }
 private riderName(parent:Node,id:string,x:number,y:number,width:number,size=23):void {
  const name=label(parent,id==='hero'?'主角':`骑手 ${id.slice(4)}`,x,y,size,INK,width,true,'left');
  if(id!=='hero')portraitDisplayName(id).then(value=>{if(value&&isValid(name,true))name.string=value;});
 }
 private vehicleConfiguration(id:string,s:FundsState):void {
  const rider=s.riders.find(r=>r.id===id);
  if(!rider){this.configureRider=null;this.riders();return;}
  const current=s.vehicles.find(v=>v.id===rider.vehicleId),heroBusy=id==='hero'&&!!s.activeQuote;
  const header=panel(this.body,'Rider-Configuration',0,418,CW,186);
  portrait(header,id==='hero'?0:Number(id.slice(4)),-CW/2+S.card+52,0,104,146);
  this.riderIdentity(header,id,id==='hero'?experienceProgress(s.heroExperience).level:rider.level,-161,58,28);
  label(header,current?`当前配车：${this.vehicleName(current)} · Lv.${current.level}`:'当前尚未配备车辆',66,13,21,INK,396,true,'left');
  label(header,heroBusy?'请完成主角当前配送后再调整车辆':'选择已拥有的车辆，为这位骑手配备',66,-22,18,UI.muted,396,false,'left');
  action(header,'返回骑手',-41,-64,164,40,()=>this.act(()=>{this.configureRider=null;}),true,false);
  action(header,'卸下车辆',147,-64,184,40,()=>this.act(()=>this.runtime.command({type:'assignVehicle',riderId:id,vehicleId:null})),!!current&&!heroBusy,false);
  label(this.body,`已拥有车辆 · ${s.vehicles.length} 辆`,-161,293,25,INK,350,true,'left');
  action(this.body,'前往车辆页',245,293,174,42,()=>this.act(()=>{this.vehicleReturnRider=id;this.navigate('车辆');}),true,false);
  const cardH=224,step=cardH+S.gap;
  const list=this.scrolling('configuration:'+id,258,M.y(1467),s.vehicles.length*step+S.card);
  s.vehicles.forEach((vehicle,i)=>{
   const equipped=vehicle.id===rider.vehicleId,owner=s.riders.find(r=>r.id!==id&&r.vehicleId===vehicle.id);
   // A vehicle detached from its rider can still be working an immutable fleet batch.
   const oldBatch=s.fleetQuotes.find(q=>q.vehicleId===vehicle.id&&q.riderId!==id);
   const effects=slotVehicleEffects(vehicle),quote=vehicle.level<CONFIG.levels.length?slotVehicleUpgradeQuote(vehicle):null,heroVehicleBusy=!!s.activeQuote&&s.riders[0].vehicleId===vehicle.id;
   const card=panel(list,'Vehicle-Instance-'+i,0,-cardH/2-i*step,CW,cardH,'#EFFAFF',equipped?'#FF8A00':UI.line);
   const pictureW=230,pictureX=-CW/2+S.card+pictureW/2,textLeft=-CW/2+S.card+pictureW+S.imageText,textW=CW/2-S.card-textLeft;
   const fallback=label(card,'车型图片载入中',pictureX,19,18,UI.muted,pictureW,false,'center');
   vehicleSideArt(card,typeof vehicle.modelId==='number'?vehicle.modelId:1,pictureX,25,pictureW,146,fallback.node);
   label(card,this.vehicleName(vehicle),textLeft+(textW-92)/2,78,27,INK,textW-92,true,'left');
   levelBadge(card,`Lv.${vehicle.level}`,CW/2-S.card-39,78,78,28);
   [['speed',`速度 ×${effects.speedRelativeToStarter.toFixed(2)}`],['capacity',`容量 ${capacityText(effects.capacity)}`],['coin-stack',`收入加成 +${Math.round((effects.incomeFactor-1)*100)}%`]].forEach(([icon,text],row)=>{
    glyph(card,icon,textLeft+13,36-row*32,25);label(card,text,textLeft+35+(textW-35)/2,36-row*32,21,INK,textW-35,true,'left');
   });
   const status=equipped?'当前配备':owner?'其他骑手已配备':oldBatch?'仍在执行旧批次':'空闲 · 可以配备';
   label(card,`${status} · ${i+1}号车`,pictureX,owner||oldBatch?-60:-78,18,equipped?UI.orange:owner||oldBatch?UI.muted:UI.blue,pictureW,true,'center');
   if(owner||oldBatch){
    const riderId=owner?.id??oldBatch!.riderId;
    this.riderName(card,riderId,pictureX,-88,pictureW,18);
   }
   const buttonW=(textW-S.gap)/2,buttonY=-cardH/2+S.buttonEdge+22;
   action(card,equipped?'已配备':owner?'已占用':oldBatch?'旧批次中':'配备车辆',textLeft+buttonW/2,buttonY,buttonW,44,()=>this.act(()=>this.runtime.command({type:'assignVehicle',riderId:id,vehicleId:vehicle.id})),!equipped&&!owner&&!oldBatch&&!heroBusy,false);
   action(card,quote?'升级车辆':'已满级',textLeft+buttonW+S.gap+buttonW/2,buttonY,buttonW,44,()=>{
    if(quote)this.showUpgrade('升级车辆',state=>{
     const current=state.vehicles.find(row=>row.id===vehicle.id);
     if(!current||state.activeQuote&&state.riders[0].vehicleId===vehicle.id)return null;
     const upgrade=current.level<CONFIG.levels.length?slotVehicleUpgradeQuote(current):null;
     return upgrade?{detail:`等级 ${current.level} → ${upgrade.nextLevel}\n速度 ×${upgrade.current.speedRelativeToStarter.toFixed(2)} → ×${upgrade.next.speedRelativeToStarter.toFixed(2)}\n容量 ${capacityText(upgrade.current.capacity)} → ${capacityText(upgrade.next.capacity)}\n收入加成 +${Math.round((upgrade.current.incomeFactor-1)*100)}% → +${Math.round((upgrade.next.incomeFactor-1)*100)}%`,costCents:upgrade.costCents}:null;
    },()=>this.runtime.command({type:'upgradeVehicle',vehicleId:vehicle.id}));
   },!!quote&&!heroVehicleBusy);
  });
 }

 private showUpgrade(title:string,readQuote:(state:FundsState)=>UpgradePresentation|null,commit:()=>unknown):void {
  this.closeUpgrade();
  const modal=panel(this.root,'UpgradeShade',0,0,720,1280,'#17365BAA','#17365BAA');modal.addComponent(BlockInputEvents);
  this.upgradeModal=modal;let submitting=false;
  const close=()=>{if(this.upgradeModal===modal)this.closeUpgrade();};
  const sheet=panel(modal,'Vehicle-UpgradeSheet',0,0,636,494,'#EFFAFF',UI.blue);
  glyph(sheet,'wrench',-264,190,38);label(sheet,title,-12,190,31,INK,432,true,'left');
  action(sheet,'×',270,190,54,44,close,true,false);
  panel(sheet,'UpgradeDivider',0,146,580,1,UI.line,UI.line);
  const detail=label(sheet,'',0,61,22,INK,568,false,'center');
  glyph(sheet,'coin',-245,-64,33);
  const cost=label(sheet,'',43,-64,25,INK,482,true,'left');
  const balance=label(sheet,'',0,-108,20,UI.muted,568,false,'center');
  const notice=label(sheet,'',0,-142,19,UI.muted,568,false,'center');
  action(sheet,'返回',-147,-199,268,54,close,true,false);
  const quoteKey=(quote:UpgradePresentation|null)=>quote?JSON.stringify([quote.costCents,quote.detail]):'unavailable';
  let displayedKey:string|null=null,displayedCash:number|null=null,buttonKey='',confirm:Node|null=null;
  const refresh=(state:FundsState)=>{
   if(this.upgradeModal!==modal||!isValid(modal,true))return;
   const quote=readQuote(state),key=quoteKey(quote);
   if(key===displayedKey&&state.cashCents===displayedCash)return;
   displayedKey=key;displayedCash=state.cashCents;
   detail.string=quote?.detail??'当前升级不可用，请返回重新选择';
   const lines=detail.string.split('\n').length;detail.node.getComponent(UITransform)!.setContentSize(568,lines>1?22*1.45*lines+6:22*1.6);
   cost.string=quote?`本次费用 ${(quote.costCents/100).toFixed(2)} 金币`:'当前没有可用升级报价';
   balance.string=`当前余额 ${(state.cashCents/100).toFixed(2)} 金币`;
   const shortfall=quote?Math.max(0,quote.costCents-state.cashCents):0,enabled=!!quote&&shortfall===0;
   notice.string=!quote?'请返回后重新选择升级':shortfall?`余额不足，还差 ${(shortfall/100).toFixed(2)} 金币`:'确认后扣除本次费用并提升等级';
   notice.color=col(!quote||shortfall?'#BF3E12':UI.muted);
   const nextButtonKey=JSON.stringify([key,enabled]);if(nextButtonKey===buttonKey)return;buttonKey=nextButtonKey;
   if(confirm){confirm.active=false;confirm.destroy();}
   const button=action(sheet,'确认升级',147,-199,268,54,()=>{
    if(submitting||this.upgradeModal!==modal||confirm!==button||!isValid(button,true)||!button.activeInHierarchy)return;
    const current=this.state,fresh=readQuote(current);
    if(quoteKey(fresh)!==key){refresh(current);if(fresh)notice.string='升级报价已更新，请核对后再次确认';return;}
    if(!fresh||current.cashCents<fresh.costCents){refresh(current);return;}
    submitting=true;close();this.act(commit);
   },enabled);confirm=button;
  };
  this.bindFunds(modal,refresh);
 }

 private vehicles(s:FundsState):void {
  const v=CONFIG.vehicles[this.model-1],effects=slotVehicleEffects({modelId:v.id,level:1}),price=slotVehiclePurchaseQuote(v.id),detailsH=444,c=this.card(this.body,'VehicleDetails',0,M.y(96)-detailsH/2,CW,detailsH);
  // Independent product scenery; selection, native vehicle pixels and the real purchase remain separate.
  // The neutral surface is only a loading/failure fallback, never a completed scene claim.
  vehicleProductPreview(c,v.id,0,80,CW-2*S.card,268);
  label(c,v.name,-280,-81,32,INK,100,true,'left');
  label(c,`已拥有 ${s.vehicles.filter(x=>x.modelId===v.id).length} 辆`,-65,-81,21,INK,290,true,'left');
  levelBadge(c,'新购 Lv.1',212,-81,126,30);
  glyph(c,'speed',-313,-128,28);label(c,`速度  ×${effects.speedRelativeToStarter}`,-202,-128,22,INK,178,true,'left');
  glyph(c,'capacity',-92,-128,28);label(c,`容量  ${capacityText(effects.capacity)}`,8,-128,22,INK,158,true,'left');
  glyph(c,'coin-stack',-313,-174,28);label(c,`收入加成 +${Math.round((effects.incomeFactor-1)*100)}%`,-139,-174,22,INK,326,true,'left');
  action(c,`购买 ${coins(price.costCents)}金币`,212,-158,212,62,()=>this.act(()=>this.runtime.command({type:'buyVehicle',modelId:v.id})));
  label(this.body,'选择车型',-210,M.y(715),35,INK,260,true,'left');
  if(this.vehicleReturnRider){const id=this.vehicleReturnRider;action(this.body,'返回骑手配车',220,M.y(715),230,44,()=>this.act(()=>{this.navigate('骑手');this.configureRider=id;}),true,false);}

  const tileW=columnWidth(3),tileStep=tileW+S.gap;
  const list=this.scrolling('vehicles',M.y(748),M.y(1490),Math.ceil(CONFIG.vehicles.length/3)*L.vehicleRowStep);
  CONFIG.vehicles.forEach((model,i)=>{
   const tile=panel(list,'Vehicle-'+model.id,(i%3-1)*tileStep,-97-Math.floor(i/3)*L.vehicleRowStep,tileW,L.vehicleTileHeight,'#F0FAFF',model.id===this.model?'#FF8A00':UI.line);
   const f=label(tile,'车型载入中',0,24,18,UI.muted,tileW-24,false,'center');vehicleSideArt(tile,model.id,0,29,tileW+8,150,f.node);
   label(tile,model.name,0,-59,24,INK,tileW-2*S.card,true,'center');label(tile,`已拥有 ${s.vehicles.filter(v=>v.modelId===model.id).length} 辆`,0,-83,18,INK,tileW-2*S.card,true,'center');
   if(model.id===this.model){const badge=panel(tile,'VehicleSelection',tileW/2-20,77,38,36,UI.orange,UI.orange);label(badge,'✓',0,0,30,'#FFFFFF',34,true,'center');}tap(tile,()=>this.act(()=>{this.model=model.id;}));
  });
 }

 private maps(s:FundsState):void {
  const c=this.scrolling('maps',M.y(102),M.y(1492),5*L.mapRowStep);
  CONFIG.maps.forEach((m,i)=>{
   const owned=s.ownedMapIds.includes(m.id),card=panel(c,'Map-'+m.id,0,-L.mapHeight/2-i*L.mapRowStep,CW,L.mapHeight,'#C7E9FA',UI.blue);
   mapPreview(card,m.id,0,0,CW-2*L.mapInset,L.mapHeight-2*L.mapInset);
   const current=s.selectedMapId===m.id,titleW=m.name.length*42+2*S.card,left=-CW/2+S.card;
   const title=label(card,m.name,left+titleW/2,61,42,'#FFFFFF',titleW-2*S.card,true,'left');title.enableOutline=true;title.outlineColor=col('#173C72');title.outlineWidth=2;
   const badgeW=current?78:102;
   statusBadge(card,current?'当前':owned?'已购买':'未解锁',left+titleW+S.gap+badgeW/2,61,owned,badgeW,35);
   if(current)return;
   if(owned)action(card,'选择地图',CW/2-S.card-88,-53,176,78,()=>this.act(()=>this.runtime.command({type:'selectMap',mapId:m.id})),true,false);
   else {
    const buy=action(card,'',CW/2-S.card-88,-53,176,78,()=>this.act(()=>this.runtime.command({type:'buyMap',mapId:m.id})));
    label(buy,'购买',0,19,22,'#FFFFFF',160,true,'center');
    const amount=coins(slotMapPurchaseQuote(m.id).costCents),amountW=amount.length*16,totalW=28+S.gap+amountW;
    glyph(buy,'coin',-totalW/2+14,-15,28);label(buy,amount,(28+S.gap)/2,-15,28,'#FFFFFF',amountW+6,true,'center');
   }
  });
 }

 private bills(s:FundsState):void {
  const query=this.runtime.ledgerQuery,summary=summarizeLedger(s.ledger,query),c=this.scrolling('bills',M.y(135),M.y(1467),1068),money=coins;
  const deliveryCategories=['hero_ordinary','hero_special','npc_delivery','legacy_delivery'];
  const deliveryEntries=s.ledger.entries.filter(e=>deliveryCategories.includes(e.category));
  const todayEntries=deliveryEntries.filter(e=>e.dayKey===query.todayDayKey),deliveryIncome=todayEntries.reduce((n,e)=>n+e.amountCents,0),supplyExpense=Math.abs(summary.today.byCategory.supply_purchase);
  const metric=(parent:Node,name:string,x:number,y:number,w:number,title:string,value:number|null,icon:string|null,blue=false)=>{
   const n=panel(parent,name,x,y,w,112,'#F2FCFF'),textX=icon?30:0,textW=icon?w-73:w-20;
   if(icon)glyph(n,icon,-w/2+39,0,61);
   label(n,title,textX,29,20,INK,textW,true,'center');
   if(value!==null)label(n,money(value),textX,-22,40,blue?UI.blue:'#FF7800',textW,true,'center');
   else label(n,'未记录',textX,-22,22,UI.muted,textW,true,'center');
  };
  const metricW=columnWidth(3,S.gap,CW-2*S.card),metricStep=metricW+S.gap;
  const today=panel(c,'Today',0,-131,CW,262);
  glyph(today,'bills',-309,99,30);label(today,'今日经营',-140,99,29,INK,290,true,'left');
  // U38: income aliases icon-coin-stack; omit that image, not the real amount.
  const todayMetrics:[string,number,string|null][]=[['配送收入',deliveryIncome,null],['补给支出',supplyExpense,'expense'],['配送净赚',deliveryIncome-supplyExpense,'profit']];
  todayMetrics.forEach(([name,value,icon],i)=>metric(today,'TodayMetric-'+i,(i-1)*metricStep,22,metricW,name,value,icon,i===1));
  const heroToday=todayEntries.filter(e=>e.category==='hero_ordinary'||e.category==='hero_special').length,npcToday=todayEntries.filter(e=>e.category==='npc_delivery').length;
  const stats=panel(today,'TodayDetails',0,-83,CW-24,78,'#F2FCFF');
  glyph(stats,'bills',-300,0,37);label(stats,`完成 ${todayEntries.length} 单`,-180,15,24,INK,190,true,'left');
  label(stats,`主角 ${heroToday} · 骑手 ${npcToday}`,-180,-16,17,INK,190,false,'left');
  panel(stats,'StatDivider1',-66,0,1,60,UI.line,UI.line);
  // V2 has neither persisted mileage nor online duration. Preserve the approved slots honestly.
  glyph(stats,'road',-32,0,35);label(stats,'主角里程',55,16,21,INK,130,true,'center');label(stats,'未记录',55,-17,20,UI.muted,130,true,'center');
  panel(stats,'StatDivider2',139,0,1,60,UI.line,UI.line);
  glyph(stats,'clock',173,0,35);label(stats,'在线',254,16,21,INK,120,true,'center');label(stats,'未记录',254,-17,20,UI.muted,120,true,'center');
  const chart=panel(c,'SevenDayChart',0,-420,CW,284);glyph(chart,'bills',-309,116,30);label(chart,'近7日配送收入',-119,116,28,INK,336,true,'left');
  const days=query.recentDayKeys.slice().sort(),values=days.map(day=>deliveryEntries.filter(e=>e.dayKey===day).reduce((n,e)=>n+e.amountCents,0));
  const sevenIncome=values.reduce((n,v)=>n+v,0);label(chart,'合计 '+money(sevenIncome),215,116,23,'#FF7800',230,true,'right');
  const max=Math.max(40000,Math.ceil(Math.max(0,...values)/40000)*40000),plotLeft=-266,plotRight=322,base=-86,plotH=128;
  for(let i=0;i<=4;i++){const yy=base+i*plotH/4;panel(chart,'Grid-'+i,(plotLeft+plotRight)/2,yy,plotRight-plotLeft,1,'#B9DEFA','#B9DEFA');label(chart,String(Number(money(max*i/4))),-299,yy,16,INK,58,false,'right');}
  panel(chart,'YAxis',plotLeft,base+plotH/2,1,plotH,'#5482AE','#5482AE');panel(chart,'XAxis',(plotLeft+plotRight)/2,base,plotRight-plotLeft,1,'#5482AE','#5482AE');
  days.forEach((day,i)=>{const x=plotLeft+42+i*84,h=plotH*values[i]/max;panel(chart,'Bar-'+day,x,base+h/2,54,Math.max(1,h),'#FFA020','#FFAD27');label(chart,money(values[i]),x,base+h+15,16,INK,82,true,'center');label(chart,day===query.todayDayKey?'今日':day.slice(5),x,-116,17,INK,82,false,'center');});
  const total=panel(c,'Cumulative',0,-679,CW,204);glyph(total,'bills',-309,73,30);label(total,'累计账目',-140,73,29,INK,290,true,'left');
  const allDelivery=deliveryEntries.reduce((n,e)=>n+e.amountCents,0);
  metric(total,'TotalMetric-0',-metricStep,-4,metricW,'累计配送收入',allDelivery,null);
  // No task-reward ledger category exists: missing data must not look like a measured zero.
  metric(total,'TotalMetric-1',0,-4,metricW,'任务奖励',null,'trophy');
  metric(total,'TotalMetric-2',metricStep,-4,metricW,'累计支出',summary.cumulative.expenseCents,'cart',true);
  label(total,`初始资金 ${money(summary.opening.balanceCents)}金币 · 余额 ${money(s.cashCents)}金币`,0,-82,18,INK,CW-40,false,'left');
  const detail=panel(c,'ExpenseCategories',0,-902,CW,214);glyph(detail,'bills',-309,78,30);label(detail,'累计支出明细',-112,78,28,INK,350,true,'left');
  const names:[string,string,string][]=[['rider_hire','招募骑手','riders'],['supply_purchase','补给','expense'],['vehicle_purchase','购买车辆','vehicles'],['rider_upgrade','骑手升级','riders'],['vehicle_upgrade','车辆升级','wrench'],['map_purchase','地图购买','maps']];
  names.forEach(([key,name,icon],i)=>{const x=i%2===0?-168:168,y=25-Math.floor(i/2)*49;glyph(detail,icon,x-127,y,28);label(detail,name,x-28,y,20,INK,145,true,'left');label(detail,money(Math.abs(summary.cumulative.byCategory[key as keyof typeof summary.cumulative.byCategory])),x+101,y,21,INK,110,true,'right');});
  const unknown=summary.unknownDate;
  if(unknown.incomeCents||unknown.expenseCents)label(c,`日期未知：收入 ${money(unknown.incomeCents)} / 支出 ${money(unknown.expenseCents)}金币`,0,-1046,18,UI.muted,CW-20,false,'center');
 }

 /** Keep FoodImages' resource API; crop its square presentation into the approved photo slot. */
 private foodThumbnail(parent:Node,name:string,x:number,y:number):void {
  const frame=item(parent,'FoodThumbnail',x,y,146,128);frame.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
  foodImage(frame,name,0,0,146,{background:false});
 }

 private foodBadge(parent:Node,food:OrderFoodPresentation,x:number,y:number):void {
  const badge=panel(parent,'FoodRule',x,y,72,34,'#F2FBFF',UI.line);
  const text=label(badge,food.badge,0,0,20,UI.muted,64,true,'center');
  text.enableWrapText=false;text.overflow=Label.Overflow.CLAMP;
 }
 private drawFoodTitle(parent:Node,title:{value:string;height:number},x:number,y:number,size:number,width:number):void {
  const text=label(parent,title.value,x,y,size,INK,width,true,'left');
  text.enableWrapText=true;text.lineHeight=Math.ceil(size*1.42);text.overflow=Label.Overflow.CLAMP;
  text.node.getComponent(UITransform)!.setContentSize(width,title.height);
 }

 private orders(snap:UISnapshot):void {
  if(snap.batchIds.length){
   const route=this.runtime.routeSnapshot,t=this.runtime.tripState,group=this.pickupGroup(route);
   const batch=snap.orders.filter(o=>snap.batchIds.includes(o.id));
   if(!t)throw new Error('本批行程记录缺失');
   const batchFoods=new Map(batch.map(order=>{
    const recorded=t.orders.find(item=>item.id===order.id);
    if(!recorded)throw new Error('本批食品记录缺失');
    return [order.id,orderFoodPresentation(recorded,t.version)] as const;
   }));
   const batchLoads=new Map(batch.map(order=>[order.id,signedOrderLoad(order)] as const));
   const effects=this.runtime.deliveryEffects;if(!effects)throw new Error('本批车辆条款缺失');
   const capacity=parseV2Capacity(effects.capacity),signedLoad=loadSummary([...batchLoads.values()],capacity);
   let batchHeight=0;
   const batchRows=batch.map(o=>{
    const food=batchFoods.get(o.id)!,title=foodTitleLayout(food,batchLoads.get(o.id)!,26,340),top=batchHeight;
    batchHeight+=204+title.extra;return {o,food,title,top};
   });
   const pending=batch.filter(o=>o.status==='pending'),completed=batch.filter(o=>o.status==='completed');
   const choices=route?.phase==='planned'?this.runtime.routeChoices():[];
   const routeNames={fast:'快捷',main:'均衡',smooth:'平稳'} as const;
   type RouteLine={value:string;size:number;color:string;bold:boolean;height:number};
   const routeLineWidth=CW-2*S.card,routeLineGap=6;
   const duration=(value:number):string=>{const seconds=Math.max(0,Math.ceil(value)),minutes=Math.floor(seconds/60);return minutes?`${minutes}分${seconds%60}秒`:`${seconds}秒`;};
   const routeLine=(value:string,size=20,color=UI.muted,bold=false):RouteLine=>({value,size,color,bold,height:textHeight(value,size,routeLineWidth)});
   const drawRouteLine=(parent:Node,line:RouteLine,top:number):void=>{
    const text=label(parent,line.value,0,top-line.height/2,line.size,line.color,routeLineWidth,line.bold,'left');
    text.enableWrapText=true;text.lineHeight=Math.ceil(line.size*1.42);text.overflow=Label.Overflow.CLAMP;
    text.node.getComponent(UITransform)!.setContentSize(routeLineWidth,line.height);
   };
   const legacyLines:string[]=[];
   if(capacity.version==='kg-v1')legacyLines.push('旧批容量规则 · 沿用原kg重量与容量');
   if(t.version===2)legacyLines.push('旧批食品规则 · 沿用原普通风险；菜名和图片仅为旧展示推测');
   const legacyNotice=legacyLines.length?routeLine(legacyLines.join('\n')):null;
   const legacyNoticeHeight=legacyNotice?legacyNotice.height+S.gap:0;
   const routeNotes=['连续行驶与取送服务的条件估算','不含手动等待及后续补给/事件/停顿'].map(value=>routeLine(value,19));
   const routeCards=choices.map(choice=>{
    const lines=[routeLine(choice.aliases.map(p=>routeNames[p]).join(' / '),23,INK,true),routeLine(`${Math.round(choice.metres)}米 · 预计现实用时 ${duration(choice.seconds)}`),routeLine(`${({clear:'晴天',rain:'小雨',severe:'恶劣天气'} as const)[choice.weather]} · 预计耗体力 ${Number(choice.stamina.toFixed(1))}点`)];
    choice.orders.forEach(eta=>{
     const index=batch.findIndex(order=>order.id===eta.id),place=route?.orders.find(order=>order.id===eta.id);
     const food=batchFoods.get(eta.id);if(!food)throw new Error('路线订单食品记录缺失');
     const load=batchLoads.get(eta.id);if(!load)throw new Error('路线订单占用记录缺失');
     const identity=index>=0?`第${index+1}单 · ${food.name} ${loadText(load)}`:`订单 ${eta.id}`;
     const safe=t?.orders.find(order=>order.id===eta.id)?.safe===true;
     const warning=eta.lateGameSeconds>0?`迟到预警 ${duration(eta.lateGameSeconds)}（游戏时间）`:safe?'保护单 · 不计迟到':'按当前条件预计未迟到';
     lines.push(routeLine(`${identity} → ${place?.dropoffName||'送达地点未记录'}`,21,INK,true));
     lines.push(routeLine(food.ruleText));
     lines.push(routeLine(`预计 ${duration(eta.etaGameSeconds)} 后完成（游戏时间） · ${warning}`,20,eta.lateGameSeconds>0?'#BF3E12':UI.muted));
    });
    return {choice,lines,height:2*S.card+lines.reduce((height,line)=>height+line.height+routeLineGap,0)+50};
   });
   const routeIntroHeight=40+routeNotes.reduce((height,line)=>height+line.height+routeLineGap,0)+S.gap;
   const routeHeight=route?.phase==='planned'?(routeCards.length?routeIntroHeight+routeCards.reduce((height,card)=>height+card.height+S.gap,0):64):group?130:94;
   const effectLine=routeLine(`本批签约 ${signedLoad} · 速度 ×${effects.speedRelativeToStarter.toFixed(2)} · 车辆收益 +${Math.round((effects.incomeFactor-1)*100)}%`,18);
   const summaryGrowth=effectLine.height+12;
   const c=this.scrolling('orders:trip',508,-340,164+summaryGrowth+legacyNoticeHeight+routeHeight+batchHeight+108);
   const summary=panel(c,'Order-BatchSummary',0,-61-summaryGrowth/2,CW,118+summaryGrowth,'#F2FBFF');
   label(summary,'本批配送',-214,33+summaryGrowth/2,27,INK,240,true,'left');
   label(summary,`待完成 ${pending.length} · 已完成 ${completed.length}`,125,33+summaryGrowth/2,23,INK,384,true,'right');
   this.routeText=label(summary,this.tripStage(),0,-4+summaryGrowth/2,22,INK,CW-26,true,'center');
   label(summary,`${({clear:'晴天',rain:'小雨',severe:'恶劣天气'} as const)[t?.weather||'clear']} · 体力 ${Math.floor(t?.stamina??100)}/100 · 查看时暂停主角`,0,-38+summaryGrowth/2,18,UI.muted,CW-26,false,'center');
   drawRouteLine(summary,effectLine,-65+summaryGrowth/2);
   if(legacyNotice)drawRouteLine(c,legacyNotice,-132-summaryGrowth);
   const routeTop=138+summaryGrowth+legacyNoticeHeight;
   label(c,route?.phase==='planned'?'选择本批路线':'当前配送路线',-173,-routeTop-15,24,INK,330,true,'left');
   if(choices.length){
    let noteTop=-routeTop-40;
    routeNotes.forEach(line=>{drawRouteLine(c,line,noteTop);noteTop-=line.height+routeLineGap;});
    let depth=routeTop+routeIntroHeight;
    routeCards.forEach(({choice:r,lines,height})=>{
     const card=panel(c,'Order-Route-'+r.preference,0,-depth-height/2,CW,height,'#F2FBFF');
     let top=height/2-S.card;
     lines.forEach(line=>{drawRouteLine(card,line,top);top-=line.height+routeLineGap;});
     action(card,'选择出发 ›',232,-height/2+S.card+25,188,50,()=>this.act(()=>{this.runtime.beginTrip(r.preference);this.navigate('首页');}),!t?.action);
     depth+=height+S.gap;
    });
   }else{
    label(c,route?.phase==='planned'?'当前无可选路线，请检查体力或先补给':`${routeNames[route?.preference||'fast']}路线 · ${Math.round(route?.legs.reduce((sum,l)=>sum+l.metres,0)||0)}米`,0,-routeTop-56,21,UI.muted,CW-24,false,'center');
    if(group&&route?.phase!=='planned')label(c,`${group.name} · ${group.count}份${group.count>1?'合并取餐':'取餐'}`,0,-routeTop-90,21,INK,CW-24,true,'center');
   }
   const orderTop=routeTop+routeHeight;
   label(c,'本批订单',-226,-orderTop-16,24,INK,220,true,'left');
   batchRows.forEach(({o,food,title,top})=>{
    const place=route?.orders.find(order=>order.id===o.id),trip=t?.orders.find(order=>order.id===o.id),shift=title.extra/2;
    const card=panel(c,'Order-Trip-'+o.id,0,-orderTop-133-top-shift,CW,190+title.extra,'#F2FBFF');
    foodImage(card,food.name,-265,20-shift,112,{background:false});
    this.foodBadge(card,food,-265,-13-shift);
    // Trip3 reads its frozen food; Trip2 retains display-only names and its old risk rules.
    this.drawFoodTitle(card,title,-30,66,26,340);
    const grouped=!!group?.ids.includes(o.id),serving=route?.phase==='service'&&route.stops[route.cursor]?.orderId===o.id;
    const status=o.status==='completed'?'已完成':grouped&&route?.phase==='ready'?'已取餐待发':grouped&&route?.phase==='service'?'取餐服务中':serving?'顾客交付中':grouped&&route?.phase==='pickup'?'到店待取':trip?.picked?'配送中':'待取餐';
    label(card,status,258,65+shift,22,o.status==='completed'?'#009749':UI.blue,130,true,'right');
    const remaining=trip&&t?trip.deadlineGameSeconds-t.gameSeconds:null;
    const deadline=o.status==='completed'?'已送达':remaining===null?'期限未记录':remaining<0?`已超时 ${Math.ceil(-remaining/60)}分钟`:`距期限 ${Math.ceil(remaining/60)}分钟`;
    glyph(card,'clock',-145,27-shift,23);label(card,deadline,67,31-shift,19,remaining!==null&&remaining<0&&o.status!=='completed'?'#BF3E12':UI.muted,382,false,'left');
    const pickup=panel(card,'Pickup',64,-18-shift,520,31,'#CEEBFC','#CEEBFC');
    const pickBadge=panel(pickup,'PickupBadge',-242,0,34,31,UI.blue,UI.blue);label(pickBadge,'取',0,0,19,'#FFFFFF',32,true,'center');
    label(pickup,place?.pickupName||'取餐地点未记录',5,0,20,INK,422,true,'left');
    const dropoff=panel(card,'Dropoff',64,-54-shift,520,31,'#CEEBFC','#CEEBFC');
    const dropBadge=panel(dropoff,'DropoffBadge',-242,0,34,31,'#009749','#009749');label(dropBadge,'送',0,0,19,'#FFFFFF',32,true,'center');
    label(dropoff,place?.dropoffName||'送达地点未记录',5,0,20,INK,422,true,'left');
    label(card,o.receipt?`已入账 ¥${coins(o.receipt.incomeCents)}`:`报价 ¥${coins(o.quote.incomeCents)}`,0,-82-shift,16,o.receipt?'#009749':UI.muted,CW-26,false,'center');
   });
   label(c,'取消全部未完成单：已完成收入与经验保留；未完成无奖，补给不退。',0,-orderTop-50-batchHeight,16,UI.muted,CW-24,false,'center');
   const controls=panel(this.body,'Order-TripControls',0,-425,CW,154,'#DCF4FF',UI.blue);
   action(controls,'回到配送地图',-169,44,326,46,()=>this.act(()=>this.navigate('首页')),true,false);
   this.tripButton(controls,169,44,326,46);
   action(controls,'补给 / 休息',-169,-14,326,46,()=>this.act(()=>{this.supplyOpen=true;}),true,false);
   action(controls,'取消全部未完成单',169,-14,326,46,()=>this.act(()=>{this.runtime.cancelDelivery(pending[0].id);this.navigate('首页');}),pending.length>0,false);
   label(controls,route?.phase==='planned'?'选定路线后出发；返回地图不会自动选择路线':route?.phase==='ready'?'取餐已完成；返回地图仍在原地，需主动继续':route?.phase==='pickup'?'主动取餐后服务2秒；取完需主动继续':route?.phase==='service'?'取送服务中不可重复操作；回到地图继续计时':'沿当前路线配送，查看本页时暂停主角',0,-57,17,UI.muted,CW-24,false,'center');return;
  }
  const extra=this.special?98:0;
  let offerHeight=0;
  const offerRows=this.offers.map(o=>{
   const food=orderFoodPresentation(o,3),load=parseV2Load(o.load);
   if(load.version!=='slots-v1')throw new Error('新候选占用版本无效');
   const title=foodTitleLayout(food,load,28,314),top=offerHeight;offerHeight+=178+title.extra;
   return {o,food,title,top};
  });
  const c=this.scrolling('orders:lobby',M.y(169),M.y(1276),offerHeight+40+extra);
  if(this.special){
   const card=this.card(c,'SpecialOffer',0,-42,CW,82);
   label(card,`高价专送 · ¥${this.special.coins}`,-113,0,25,'#FF7800',400,true,'left');
   // No ad SDK is available: this is a status, never a claimable offer button.
   label(card,'广告未接入',232,0,19,UI.muted,184,true,'right');
  }
  offerRows.forEach(({o,food,title,top})=>{
   const chosen=this.selected.has(o.id),shift=title.extra/2,card=panel(c,'Order-'+o.id,0,-82-top-shift-extra,CW,164+title.extra,'#F2FBFF',chosen?'#FF9600':UI.line);
   this.foodThumbnail(card,food.name,-224,-shift);
   this.foodBadge(card,food,-224,-45-shift);
   let quote:ReturnType<V2RuntimeController['quoteCandidates']>|null=null;try{quote=this.runtime.quoteCandidates([o]);}catch{/* This individual candidate may fail the current route or capacity rules. */}
   this.drawFoodTitle(card,title,5,52,28,314);
   label(card,quote?`¥${coins(quote.totalIncomeCents)}`:'—',251,52+shift,42,'#FF7800',142,true,'right');
   glyph(card,'clock',-146,14-shift,22);label(card,quote?`${Math.ceil(quote.deadlines[0].gameSeconds/60)}分钟内送达`:'当前条件无法接单',31,18-shift,20,quote?UI.ink:UI.muted,310,true,'left');
   const pickup=panel(card,'Pickup',86,-17-shift,488,32,'#CEEBFC','#CEEBFC');const pickBadge=panel(pickup,'PickupBadge',-222,0,36,32,UI.blue,UI.blue);label(pickBadge,'取',0,0,20,'#FFFFFF',32,true,'center');label(pickup,o.pickupName,-4,0,21,INK,370,true,'left');
   const dropoff=panel(card,'Dropoff',86,-53-shift,488,32,'#CEEBFC','#CEEBFC');const dropBadge=panel(dropoff,'DropoffBadge',-222,0,36,32,'#009749','#009749');label(dropBadge,'送',0,0,20,'#FFFFFF',32,true,'center');label(dropoff,o.dropoffName,-4,0,21,INK,370,true,'left');
   checkbox(card,chosen,-312,-shift);
   tap(card,()=>this.act(()=>{if(this.selected.has(o.id))this.selected.delete(o.id);else this.selected.add(o.id);}));
  });
  const chosen=this.offers.filter(o=>this.selected.has(o.id)),capacity=this.runtime.nextBatchEffects?.capacity;
  const loads=chosen.map(o=>parseV2Load(o.load)),fits=!!capacity&&fitsV2Capacity(loads,capacity);
  let batchQuote:ReturnType<V2RuntimeController['quoteCandidates']>|null=null,quoteError='';
  if(chosen.length)try{batchQuote=this.runtime.quoteCandidates(chosen);}catch(error){quoteError=String(error).replace(/^Error: /,'');}
  const summary=panel(this.body,'FixedOrderSummary',0,M.y(1372),CW,105,'#DCF4FF',UI.blue);
  glyph(summary,'capacity',-304,9,43);label(summary,'容量',-241,16,25,INK,74,true,'left');label(summary,capacity?loadSummary(loads,capacity):'未配车',-132,16,30,fits?INK:'#BF3E12',146,true,'left');label(summary,`已选 ${chosen.length} 单`,-170,-24,20,UI.muted,220,true,'left');
  panel(summary,'SummaryDivider',-49,0,1,82,'#79CEFF','#79CEFF');
  label(summary,'预计收入',40,29,20,INK,152,true,'center');label(summary,batchQuote?`¥${coins(batchQuote.totalIncomeCents)}`:'—',40,-13,43,'#FF7800',152,true,'center');
  // Keep each original candidate, including load/sourceOfferId/food/endpoints, for domain validation.
  action(summary,'选择路线 ›',223,1,216,77,()=>this.act(()=>{this.runtime.acceptBatch(chosen);this.selected.clear();}),chosen.length>0&&fits&&!!batchQuote);
  if(quoteError)label(summary,quoteError,0,-49,14,'#BF3E12',CW-20,false,'center');
 }

 update(dt:number):void {
  if(!this.runtime||!this.hud)return;
  // Motion consumes the actual current route position every frame, never extrapolated/tweened time.
  const route=this.runtime.routeMotion;
  if(route){
   this.map.setRider(route.position,0);
   const routeKey=route.tripId+':'+route.phase+':'+route.cursor;
   if(routeKey!==this.routeViewKey){
    const legs=this.runtime.routeSnapshot?.legs||[];
    const view=this.map.captureView();
    this.map.setRoutes(legs[route.cursor]?[legs[route.cursor]]:[],0,false);
    // setRoutes clears follow internally. Restore the user's existing view instead of silently losing it.
    this.map.restoreView(view);
    const departing=route.phase==='travelling'&&(route.tripId!==this.lastRouteTripId||['idle','planned','finished'].includes(this.lastRoutePhase));
    if(departing)this.map.locate(false);
    this.routeViewKey=routeKey;this.lastRoutePhase=route.phase;this.lastRouteTripId=route.tripId;
   }
  }
  // HUD/ledger/status reads stay throttled; they do not gate map motion.
  this.elapsed+=dt;if(this.elapsed<.5)return;this.elapsed=0;
  const snap=this.runtime.snapshot;if(!snap)return;
  this.refreshHUD((snap.economy as V2EconomySnapshot).state);this.refreshRiderStatuses(snap);this.refreshNPCActivity(snap);
  this.refreshFunds((snap.economy as V2EconomySnapshot).state);
  if(this.runtime.lastError&&this.errorText)this.errorText.string=this.runtime.lastError;
  const trip=this.runtime.tripState;
  // Cursor/membership and supply boundaries may change without changing phase or batch IDs.
  // Progress seconds are deliberately excluded: update their real labels, not the whole page.
  // Full stop membership is read only at this HUD cadence, not for frame-by-frame motion.
  const controlKey=JSON.stringify([route?.phase??'idle',route?.tripId,route?.cursor,route?.serviceCharged,this.pickupGroup(this.runtime.routeSnapshot)?.ids,snap.batchIds,trip?.blocked,trip?.action?.kind,trip?.action?.source,trip?.orders.map(order=>[order.id,order.picked,order.delivered])]);
  if(controlKey!==this.routeControlKey){
   if(!snap.batchIds.length){this.offers=this.runtime.normalCandidates();this.selected.clear();}
   this.routeControlKey=controlKey;
   if(this.page==='订单大厅'||this.page==='首页')this.render();
  }
  if(this.routeText)this.routeText.string=this.tripStage();
  if(this.tripActionText)this.tripActionText.string=this.tripControl().text;
 }

 onDestroy():void {this.closeUpgrade();this.fundsViews.clear();this.map?.cancelLocate();this.root?.destroy();}
}
