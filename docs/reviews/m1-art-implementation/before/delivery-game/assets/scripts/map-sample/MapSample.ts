import { _decorator, BlockInputEvents, Component, Game, game, JsonAsset, Label, Node, resources, ResolutionPolicy, sys, view } from 'cc';
import { CityMap, ROUTE_COLORS } from './CityMap';
import { prepareCity } from './PlaceCatalog';
import { CityData, Preference } from './MapTypes';
import { OrderBook } from './OrderBook';
import { OrderPhone } from './OrderPhone';
import { ReceiptPresentation } from './ReceiptPresentation';
import { CountySaveStore } from './CountySaveStore';
import { COUNTY_VEHICLES as VEHICLES } from './CountyConfig';
import { formatDeliveryTime, formatRemaining } from './DeliveryClock';
import { billingRows } from './BillingPresentation';
import { box, button, C, icon, item, label, tap } from './SampleUI';
import { SafeInsets, rotatedViewportInsets, safePanelTransform, viewportInsets } from './SafeAreaLayout';
const {ccclass}=_decorator;
const TITLES:Record<Preference,string>={fast:'快捷路',main:'主干道',smooth:'平稳路'};
type DialogKind='receipt'|'garage'|'demand'|'maps'|'bills';

@ccclass('MapSample')
export class MapSample extends Component {
  private book!:OrderBook;
  private city!:CityMap;
  private root!:Node;
  private panel!:Node;
  private phone:OrderPhone|null=null;
  private timer:Label|null=null;
  private tripLabel:Label|null=null;
  private progressFill:Node|null=null;
  private screenExtra=0;
  private safeInsets:SafeInsets={top:0,bottom:0,left:0,right:0};
  private hidden=false;
  private skipNextFrame=false;
  private store!:CountySaveStore;
  private money!:Label;
  private rating!:Label;
  private experience!:Label;
  private modal:Node|null=null;
  private modalKind:DialogKind|null=null;
  private billValues:Label[]=[];
  private billDate:Label|null=null;
  private billElapsed=0;
  private onlineAt:number|null=null;
  private damageNotice:Node|null=null;
  private damageNoticeSeconds=0;
  private readonly receipts=new ReceiptPresentation();
  private toast:Node|null=null;
  private noticeMessage='';
  private saveElapsed=0;
  private lastSaveError='';
  private readonly pageHide=()=>this.onHide();
  private readonly viewportResize=()=>this.onResize();

  start():void {
    const canvas=this.node.parent!;
    const loading=label(canvas,'正在打开澄川骑手地图…',0,0,26,C.ink,650,true,'center');
    resources.load('map-sample/city',JsonAsset,(error,asset)=>{
      if(!this.isValid)return;
      if(error){loading.string='地图加载失败，请重新打开';console.error(error);return;}
      let recovery='';
      try {
        const data=prepareCity(asset.json as CityData);
        this.store=new CountySaveStore({getItem:key=>sys.localStorage.getItem(key),setItem:(key,value)=>sys.localStorage.setItem(key,value)});
        const loaded=this.store.load(raw=>OrderBook.restore(data,raw),()=>new OrderBook(data));this.book=loaded.session;recovery=loaded.message;
      }
      catch(error){loading.string='路网暂时不可用，请重新打开';console.error(error);return;}
      this.onlineAt=this.hidden?null:Date.now();loading.node.destroy();this.rebuildLayout();this.save();view.on('canvas-resize',this.onResize,this);
      if(recovery.indexOf('恢复')>=0||recovery.indexOf('损坏')>=0||!this.store.available)this.showMessage(this.store.available?recovery:this.store.message);
    });
    game.on(Game.EVENT_HIDE,this.onHide,this);game.on(Game.EVENT_SHOW,this.onShow,this);
    if(typeof window!=='undefined'){
      window.addEventListener('pagehide',this.pageHide);
      window.addEventListener('orientationchange',this.viewportResize);
      window.visualViewport?.addEventListener('resize',this.viewportResize);
    }
  }
  onDestroy():void {
    view.off('canvas-resize',this.onResize,this);
    game.off(Game.EVENT_HIDE,this.onHide,this);game.off(Game.EVENT_SHOW,this.onShow,this);
    if(typeof window!=='undefined'){
      window.removeEventListener('pagehide',this.pageHide);
      window.removeEventListener('orientationchange',this.viewportResize);
      window.visualViewport?.removeEventListener('resize',this.viewportResize);
    }
  }
  private onHide():void{
    if(this.book&&!this.hidden&&this.onlineAt!==null)this.book.recordOnlineTime(this.onlineAt,Date.now());
    this.onlineAt=null;this.hidden=true;if(this.book)this.save();
  }
  private onShow():void{
    this.onlineAt=Date.now();this.hidden=false;this.skipNextFrame=true;
    if(this.book){
      const next=this.readSafeInsets();
      if(next.top!==this.safeInsets.top||next.bottom!==this.safeInsets.bottom||next.left!==this.safeInsets.left||next.right!==this.safeInsets.right)this.onResize();
    }
  }
  private onResize():void{if(!this.book)return;this.unschedule(this.rebuildLayout);this.scheduleOnce(this.rebuildLayout,0);}
  private readSafeInsets():SafeInsets {
    if(typeof document!=='undefined'){
      const style=document.getElementById('GameDiv')?.style;
      if((style?.transform||style?.webkitTransform)==='rotate(90deg)'){
        const css=getComputedStyle(document.documentElement);
        const edge=(name:string):number=>Math.max(0,parseFloat(css.getPropertyValue('--safe-'+name))||0);
        return rotatedViewportInsets(720,1280+this.screenExtra,view.getFrameSize(),{top:edge('top'),bottom:edge('bottom'),left:edge('left'),right:edge('right')});
      }
    }
    return viewportInsets(720,1280+this.screenExtra,sys?.getSafeAreaRect?.(false));
  }
  private rebuildLayout():void {
    const wasPhone=!!this.phone,wasDialog=this.modalKind,wasNotice=this.noticeMessage;
    const frame=view.getFrameSize(),requestedExtra=Math.max(0,720*frame.height/frame.width-1280);
    const idle=this.book.mode==='idle',baseMapHeight=idle?1280:813;
    // Very tall windows must still fit the whole map viewport inside town at 100m.
    this.screenExtra=CityMap.fitViewportHeight(this.book.data,baseMapHeight+requestedExtra)-baseMapHeight;
    view.setDesignResolutionSize(720,1280+this.screenExtra,ResolutionPolicy.SHOW_ALL);
    this.safeInsets=this.readSafeInsets();
    const bottom=this.safeInsets.bottom,mapHeight=Math.max(1,baseMapHeight+this.screenExtra-(idle?0:bottom)),mapY=idle?0:233.5+bottom/2;
    if(this.root){this.root.active=false;this.root.destroy();}this.phone=null;this.modal=null;this.modalKind=null;this.billValues=[];this.billDate=null;this.toast=null;this.damageNotice=null;
    this.root=item(this.node.parent!,'DeliveryUI');
    box(this.root,'Background',0,0,720,1280+this.screenExtra,C.light,0);
    this.city=new CityMap(this.root,this.book.data,mapHeight,()=>sys.openURL('https://www.openstreetmap.org/copyright'),mapY,idle?118+bottom:0,this.safeInsets);
    this.city.setVehicle(this.book.player.vehicleTier);
    this.header(item(this.root,'HeaderGroup',0,this.screenExtra/2-this.safeInsets.top));this.controls();
    this.panel=item(this.root,'OrderPanel',0,-this.screenExtra/2+bottom);
    const active=this.book.active;
    if(active)this.city.setRoutes(active.routes,active.selected,true);
    const pose=this.book.riderPose;this.city.setRider(pose.point,pose.angle);
    this.city.locate(true);
    if(this.damageNoticeSeconds>0)this.renderDamageNotice();
    this.renderPanel();if(wasPhone)this.openPhone();
    if(wasDialog==='receipt'&&!this.modal)this.openReceipt();
    if(wasDialog==='garage')this.openGarage();
    if(wasDialog==='maps'&&!this.modal)this.openMaps();
    if(wasDialog==='bills'&&!this.modal)this.openBills();
    if(wasNotice)this.showMessage(wasNotice);
  }
  private header(parent:Node):void {
    const width=720-this.safeInsets.left-this.safeInsets.right-36;
    const card=box(parent,'Header',(this.safeInsets.left-this.safeInsets.right)/2,564,width,128,C.paper,18);
    const content=item(card,'HeaderContent');content.setScale(width/684,1,1);
    const avatar=box(content,'PlayerAvatar',-286,0,72,72,'#F1F2F4',36);
    label(avatar,'骑',0,0,30,'#555B63',65,true,'center');
    label(content,'澄川骑手',-153,19,25,C.ink,176,true);
    this.experience=label(content,'',-145,-19,18,'#757A80',192);
    label(content,'余额',55,26,18,'#757A80',170,false,'center');
    this.money=label(content,'',55,-13,27,C.ink,180,true,'center');
    label(content,'评价',259,26,18,'#757A80',100,false,'center');
    this.rating=label(content,'',259,-13,27,C.ink,100,true,'center');
    this.updatePlayerHeader();
  }
  private controls():void {
    const station=item(this.root,'StationEntry',309-this.safeInsets.right,375+this.screenExtra/2-this.safeInsets.top,72,80);
    const picture=box(station,'PlaceholderIcon-station',0,11,36,32,'#F0EEE7',8);
    label(picture,'站',0,0,20,'#AAA69C',32,true,'center');label(station,'站点',0,-24,18,'#AAA69C',70,true,'center');
    const y=this.book.mode==='idle'?-460:-111;
    const locate=box(this.root,'FollowRider',309-this.safeInsets.right,y-this.screenExtra/2+this.safeInsets.bottom,54,54,C.primary,13);
    icon(locate,'target',0,0,C.ink,.85);tap(locate,()=>this.city.locate());
  }
  private openPhone():void {
    if(this.phone||this.book.mode!=='idle')return;
    this.phone=new OrderPhone(this.root,this.book,1280+this.screenExtra,id=>this.accept(id),()=>this.closePhone(),()=>{
      if(!this.act(()=>this.book.refreshFree()))return;
      this.closePhone();this.openPhone();
    },this.safeInsets);
  }
  private closePhone():void{if(this.phone)this.phone.close();this.phone=null;}
  private navigation():void {
    const idle=this.book.mode==='idle';
    const bar=item(this.panel,'MainNavigation',(this.safeInsets.left-this.safeInsets.right)/2,-581,720,118);bar.addComponent(BlockInputEvents);
    bar.setScale((720-this.safeInsets.left-this.safeInsets.right)/720,1,1);
    const entries=[
      {key:'recruit',name:'招募',glyph:'人',x:-280,enabled:false,action:()=>{}},
      {key:'vehicle',name:'车辆',glyph:'车',x:-150,enabled:idle,action:()=>this.openGarage()},
      {key:'orders',name:'抢单',glyph:'单',x:0,enabled:idle,action:()=>this.openPhone()},
      {key:'map',name:'地图',glyph:'图',x:150,enabled:true,action:()=>this.openMaps()},
      {key:'bills',name:'账单',glyph:'账',x:280,enabled:true,action:()=>this.openBills()},
    ];
    for(const entry of entries){
      const main=entry.key==='orders',enabled=entry.enabled,foreground=enabled?C.ink:'#AAA69C';
      const slot=main?box(bar,'Nav-'+entry.key,entry.x,0,136,100,enabled?C.primary:'#EAE7DE',30):item(bar,'Nav-'+entry.key,entry.x,0,100,100);
      if(main)label(slot,entry.name,0,0,34,foreground,124,true,'center');
      else{
        const pictogram=box(slot,'PlaceholderIcon-'+entry.key,0,23,36,32,enabled?'#FFF1BB':'#F0EEE7',8);
        if(entry.key==='map')icon(pictogram,'map',0,0,foreground,.7);else label(pictogram,entry.glyph,0,0,20,foreground,32,true,'center');
        label(slot,entry.name,0,-10,21,foreground,94,true,'center');
      }
      if(enabled)tap(slot,entry.action);
    }
  }
  private accept(id:string):void {
    if(!this.act(()=>this.book.accept(id)))return;this.closePhone();
    this.rebuildLayout();
  }
  private renderPanel():void {
    for(const child of [...this.panel.children])child.destroy();this.panel.removeAllChildren();
    this.timer=null;this.tripLabel=null;this.progressFill=null;
    this.updatePlayerHeader();
    this.navigation();
    const active=this.book.active;
    if(!active)return;
    const p=box(this.panel,'DeliverySheet',0,-343,700,358,C.paper,24);
    p.setPosition((this.safeInsets.left-this.safeInsets.right)/2,-343);p.setScale((720-this.safeInsets.left-this.safeInsets.right)/720,1,1);
    box(p,'Handle',0,166,50,4,'#E7E1D5',2);
    const offer=active.offer,route=active.routes[active.selected],timing=this.book.timingForRoute(route);
    label(p,`${this.book.data.pois[offer.from].name} → ${this.book.data.pois[offer.to].name}`,-12,119,25,C.ink,620,true);
    label(p,`${offer.food} · ${offer.weightKg}kg · ${offer.fragility==='fragile'?'怕洒':offer.fragility==='durable'?'耐放':'普通餐品'}`,-130,80,18,C.muted,390);
    const receipt=active.receipt;
    label(p,(receipt?'+¥':'基础¥')+((receipt?receipt.incomeCents:offer.feeCents)/100).toFixed(2),218,82,28,'#9A6500',190,true,'right');
    if(active.mode==='routes'){
      const width=(650-(active.routes.length-1)*12)/active.routes.length;
      active.routes.forEach((r,i)=>{
        const selected=i===active.selected,x=-325+width/2+i*(width+12),color=ROUTE_COLORS[r.preference];
        const card=box(p,'Route-'+r.preference,x,5,width,106,selected?'#FFF5CE':'#F7F5EF',12,selected?color:C.line);
        label(card,TITLES[r.preference],0,31,21,selected?color:C.ink,width-20,true,'center');
        const estimated=this.book.timingForRoute(r).displaySeconds,late=estimated>active.deadlineSeconds;
        label(card,formatDeliveryTime(estimated),0,0,25,C.ink,width-16,true,'center');
        label(card,`${late?'预计晚到':'准时'} · 餐损${Math.round(r.risk*100)}%`,0,-32,17,late?'#B76A3A':C.muted,width-12,false,'center');
        tap(card,()=>{if(!this.act(()=>this.book.select(i)))return;this.city.setRoutes(active.routes,i);this.renderPanel();});
      });
      button(p,'返回接单',-247,-91,150,61,()=>{if(!this.act(()=>this.book.cancel()))return;this.rebuildLayout();this.openPhone();},C.light,C.ink);
      button(p,'出发配送',88,-91,490,61,()=>{if(!this.act(()=>this.book.depart()))return;this.city.locate(true);this.renderPanel();});
      label(p,`${offer.type==='urgent'?'加急 · ':''}${offer.demand==='door'?'放门口，别敲门':'直接交付'} · ${formatDeliveryTime(active.deadlineSeconds)}内送达`,0,-148,18,C.muted,650,false,'center');
    }else if(active.mode==='arrived'){
      label(p,'已到达顾客',-8,26,25,C.ink,630,true);
      label(p,'请在弹窗中选择交付方式',-8,-15,20,C.muted,630);
      this.openDemand();
    }else if(active.mode==='done'&&receipt){
      label(p,'配送完成 · 收入已到账',-8,30,26,C.green,630,true);
      label(p,`评价 ${receipt.ratingAfter}（${receipt.ratingDelta>=0?'+':''}${receipt.ratingDelta}） · 经验 +${receipt.experienceGained} · Lv.${receipt.levelAfter}`,-8,-7,21,C.ink,630,true);
      label(p,receipt.summary.slice(0,2).join(' · '),-8,-43,19,C.muted,630);
      button(p,'结算详情',-247,-104,150,60,()=>this.openReceipt(),C.light,C.ink);
      button(p,'继续接单',88,-104,490,60,()=>this.continueOrders());
      if(this.receipts.observe(active))this.openReceipt();
    }else{
      this.tripLabel=label(p,'',-104,27,25,C.ink,440,true);
      this.timer=label(p,'',209,27,22,C.ink,200,true,'right');
      box(p,'ProgressTrack',0,-15,640,8,'#EDE7D8',4);
      this.progressFill=box(p,'ProgressFill',-320,-15,640,8,C.primary,4);
      label(p,`${TITLES[route.preference]} · 全程 ${(route.metres/1000).toFixed(1)}km · 预计${formatDeliveryTime(timing.displaySeconds)}`,0,-46,19,C.muted,640);
      this.updateProgress();
    }
  }
  update(dt:number):void {
    if(!this.book||this.hidden)return;
    const now=Date.now();if(this.onlineAt!==null)this.book.recordOnlineTime(this.onlineAt,now);this.onlineAt=now;
    if(this.skipNextFrame){this.skipNextFrame=false;return;}
    this.saveElapsed+=dt;this.billElapsed+=dt;
    if(this.billElapsed>=1){this.billElapsed=0;this.updateBills();}
    if(this.damageNoticeSeconds>0){
      this.damageNoticeSeconds=Math.max(0,this.damageNoticeSeconds-dt);
      if(this.damageNoticeSeconds===0&&this.damageNotice){this.damageNotice.destroy();this.damageNotice=null;}
    }
    if(this.book.mode!=='running'){
      if(this.saveElapsed>=5){this.saveElapsed=0;this.save();}
      return;
    }
    const arrived=this.book.advance(dt),pose=this.book.riderPose;
    this.city.setRider(pose.point,pose.angle);this.updateProgress();
    const damaged=this.book.takeDamageNotice();
    if(damaged){this.damageNoticeSeconds=2;this.renderDamageNotice();}
    if(arrived||damaged||this.saveElapsed>=.5){this.saveElapsed=0;this.save();}
    if(arrived)this.renderPanel();
  }
  private act(action:()=>void):boolean {
    try{action();this.save();return true;}
    catch(error){this.showMessage(error instanceof Error?error.message:'操作未完成，请重试');return false;}
  }
  private save():void {
    if(!this.book||!this.store)return;
    const ok=this.store.save(this.book.serialize());
    if(!ok&&this.lastSaveError!==this.store.message){this.lastSaveError=this.store.message;this.showMessage(this.store.message);}
    if(ok)this.lastSaveError='';this.updatePlayerHeader();this.updateBills();
  }
  private updatePlayerHeader():void {
    if(!this.money)return;const p=this.book.player;
    this.city.setVehicle(p.vehicleTier);
    this.money.string='¥'+(p.cashCents/100).toFixed(2);this.rating.string=String(p.rating);
    this.experience.string=`Lv.${p.level} · ${p.experience}经验`;
  }
  private showMessage(message:string):void {
    if(!this.root)return;if(this.toast){this.toast.active=false;this.toast.destroy();}
    this.noticeMessage=message;
    const node=this.toast=box(this.root,'NoticeToast',0,-230-this.screenExtra/2,680,68,'#FFF0B7',16,'#D6B65A');
    label(node,message,0,0,18,C.ink,650,true,'center');
    this.scheduleOnce(()=>{if(node.isValid)node.destroy();if(this.toast===node){this.toast=null;this.noticeMessage='';}},4);
  }
  private closeDialog():void{if(this.modal){this.modal.active=false;this.modal.destroy();this.modal=null;}this.modalKind=null;this.billValues=[];this.billDate=null;}
  private dialog(title:string,height:number,kind:DialogKind,dismissible=true):{layer:Node;card:Node} {
    this.closeDialog();this.modalKind=kind;const layer=this.modal=item(this.root,'CountyDialog',0,0,720,1280+this.screenExtra);layer.addComponent(BlockInputEvents);
    const shade=box(layer,'Shade',0,0,720,1280+this.screenExtra,'#00000099',0);if(dismissible)tap(shade,()=>this.closeDialog());
    const card=box(layer,'DialogCard',0,0,638,height,C.paper,28);card.addComponent(BlockInputEvents);
    const placement=safePanelTransform(638,height,1280+this.screenExtra,this.safeInsets);
    card.setPosition(placement.x,placement.y);card.setScale(placement.scale,placement.scale,1);
    label(card,title,-39,height/2-65,29,C.ink,480,true);
    if(dismissible)button(card,'关闭',245,height/2-63,75,47,()=>this.closeDialog(),C.light,C.ink);
    return {layer,card};
  }
  private openDemand():void {
    if(this.book.mode!=='arrived'||this.modalKind==='demand')return;
    const {card}=this.dialog('交付要求',440,'demand',false);
    label(card,'顾客留言：放门口，别敲门',0,71,24,C.ink,565,true,'center');
    label(card,'请选择交付方式',0,22,21,C.muted,565,false,'center');
    button(card,'敲门交付',-145,-63,270,65,()=>this.deliverAtDoor(false),C.light,C.ink);
    button(card,'按要求放门口',145,-63,270,65,()=>this.deliverAtDoor(true));
    label(card,'选择期间不消耗配送时间',0,-146,18,C.muted,565,false,'center');
  }
  private deliverAtDoor(answer:boolean):void{
    if(this.book.mode!=='arrived')return;
    if(this.act(()=>this.book.settle(answer))){this.closeDialog();this.renderPanel();}
  }
  private renderDamageNotice():void {
    if(this.damageNotice){this.damageNotice.destroy();this.damageNotice=null;}
    const notice=this.damageNotice=box(this.root,'DamageNotice',0,330+this.screenExtra/2,626,88,'#FFF0CF',18,'#DAAB64');
    label(notice,'路程颠簸，餐品损坏了',0,0,25,'#9B592E',590,true,'center');
  }
  private openReceipt():void {
    const receipt=this.book.active?.receipt;if(!receipt)return;
    const {card}=this.dialog('配送结算',800,'receipt');
    label(card,'+¥'+(receipt.incomeCents/100).toFixed(2),0,237,57,'#9A6500',565,true,'center');
    label(card,`基础价 ¥${(receipt.basePriceCents/100).toFixed(2)} · 本单实际收入`,0,183,19,C.muted,565,false,'center');
    receipt.summary.forEach((line,i)=>label(card,'· '+line,-2,117-i*40,20,C.ink,565));
    label(card,`评价 ${receipt.ratingBefore} → ${receipt.ratingAfter}（${receipt.ratingDelta>=0?'+':''}${receipt.ratingDelta}）`,-2,-169,22,C.ink,565,true);
    label(card,`经验 +${receipt.experienceGained} · 等级 Lv.${receipt.levelBefore} → Lv.${receipt.levelAfter}`,-2,-210,21,C.ink,565);
    label(card,'余额 ¥'+(receipt.newCashCents/100).toFixed(2),-2,-252,24,C.ink,565,true);
    button(card,'确认，继续接单',0,-326,565,63,()=>this.continueOrders());
  }
  private continueOrders():void {
    if(!this.act(()=>this.book.finish()))return;
    this.closeDialog();this.rebuildLayout();this.openPhone();
  }
  private openMaps():void {
    if(this.book.mode==='arrived')return;
    const {card}=this.dialog('地图',920,'maps');
    const regions=[
      {name:'县城',requirements:''},
      {name:'城市',requirements:'100单 · C车 · 招募1名骑手 · 站点2级'},
      {name:'省会',requirements:'300单 · B车 · C骑手上岗 · 站点3级'},
      {name:'一线',requirements:'800单 · A车 · A骑手上岗 · 站点4级'},
      {name:'国际一线',requirements:'2000单 · A车 · A骑手上岗 · 站点5级'},
    ];
    regions.forEach((region,i)=>{
      const enabled=i===0,foreground=enabled?C.ink:'#AAA69C';
      const row=box(card,'Region-'+i,0,270-i*136,565,112,enabled?'#FFF1BB':'#F0EEE7',16);
      icon(row,'map',-236,0,foreground,1);
      label(row,region.name,20,enabled?0:22,27,foreground,425,true);
      if(region.requirements)label(row,region.requirements,20,-24,17,foreground,425);
      if(enabled)tap(row,()=>this.closeDialog());
    });
  }
  private openBills():void {
    if(this.book.mode==='arrived')return;
    const {card}=this.dialog('账单',1000,'bills'),bill=this.book.billing;
    this.billDate=label(card,bill.day,0,380,17,C.muted,565,false,'center');
    billingRows(bill).forEach((row,i)=>{
      const cell=box(card,'BillMetric-'+i,i%2?146:-146,300-Math.floor(i/2)*136,270,116,'#FAF7ED',15);
      label(cell,row.title,0,28,19,C.muted,250,false,'center');
      this.billValues.push(label(cell,row.value,0,-17,27,C.ink,250,true,'center'));
    });
  }
  private updateBills():void {
    if(this.modalKind!=='bills')return;
    const bill=this.book.billing;if(this.billDate)this.billDate.string=bill.day;
    billingRows(bill).forEach((row,i)=>{if(this.billValues[i])this.billValues[i].string=row.value;});
  }
  private openGarage():void {
    if(this.book.mode!=='idle'){this.showMessage('先送完当前订单，再升级车辆');return;}
    const p=this.book.player,current=VEHICLES[p.vehicleTier-1],next=VEHICLES[1],{card}=this.dialog('我的车辆',740,'garage');
    const badge=box(card,'VehicleGrade',-182,173,150,128,'#FFF1BB',18);label(badge,current.name,0,0,62,C.ink,135,true,'center');
    label(card,current.name+' 级电动车',92,204,28,C.ink,310,true);
    label(card,`载重 ${current.capacityKg}kg · ${current.speedKph}km/h`,90,157,20,C.muted,310);
    label(card,`跑单收入 ×${current.incomeMultiplier.toFixed(2)}`,90,117,20,C.muted,310);
    box(card,'UpgradeCard',0,-34,565,154,'#FAF7ED',17);
    label(card,p.vehicleTier===1?`升级 ${next.name} · ¥${(next.upgradeFeeCents/100).toFixed(2)}`:`${next.name} 已拥有`,0,5,28,C.ink,520,true,'center');
    label(card,`${next.speedKph}km/h · 收入 +${Math.round((next.incomeMultiplier-1)*100)}% · 载重 ${next.capacityKg}kg`,0,-44,19,C.muted,530,false,'center');
    label(card,'当前余额 ¥'+(p.cashCents/100).toFixed(2),0,-145,23,C.ink,550,true,'center');
    const gap=Math.max(0,next.upgradeFeeCents-p.cashCents),text=p.vehicleTier===2?'已达当前站点上限':gap?`还差 ¥${(gap/100).toFixed(2)}`:`花 ¥${(next.upgradeFeeCents/100).toFixed(0)} 升级 ${next.name}`;
    button(card,text,0,-226,565,67,()=>{
      if(!this.act(()=>this.book.upgradeVehicle()))return;
      this.closeDialog();this.renderPanel();this.showMessage('已升级为 D+');
    },p.vehicleTier===1&&!gap?C.primary:C.light,p.vehicleTier===1&&!gap?C.ink:'#AAA69C',p.vehicleTier===1&&!gap);
  }
  private updateProgress():void {
    const active=this.book.active;if(!active)return;
    const progress=this.book.progress;
    if(this.tripLabel)this.tripLabel.string=this.book.tripStage==='pickup'?'前往餐厅取餐':this.book.tripStage==='collecting'?`正在取餐中 · ${Math.ceil(this.book.pickupWaitRemaining)}秒`:'正在送往顾客';
    if(this.timer)this.timer.string=active.mode==='done'?'已到达':'剩余 '+formatRemaining(progress.remainingSeconds);
    if(this.progressFill){this.progressFill.setScale(progress.progress,1,1);this.progressFill.setPosition(-320+320*progress.progress,-15);}
  }
}
