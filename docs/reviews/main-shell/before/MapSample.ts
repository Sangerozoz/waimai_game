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
import { box, button, C, icon, item, label, tap } from './SampleUI';
const {ccclass}=_decorator;
const TITLES:Record<Preference,string>={fast:'快捷路',main:'主干道',smooth:'平稳路'};

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
  private hidden=false;
  private skipNextFrame=false;
  private store!:CountySaveStore;
  private money!:Label;
  private rating!:Label;
  private experience!:Label;
  private vehicleBadge!:Label;
  private modal:Node|null=null;
  private modalKind:'receipt'|'garage'|null=null;
  private readonly receipts=new ReceiptPresentation();
  private toast:Node|null=null;
  private noticeMessage='';
  private saveElapsed=0;
  private lastSaveError='';
  private readonly pageHide=()=>this.onHide();

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
      loading.node.destroy();this.rebuildLayout();this.save();view.on('canvas-resize',this.onResize,this);
      if(recovery.indexOf('恢复')>=0||recovery.indexOf('损坏')>=0||!this.store.available)this.showMessage(this.store.available?recovery:this.store.message);
    });
    game.on(Game.EVENT_HIDE,this.onHide,this);game.on(Game.EVENT_SHOW,this.onShow,this);
    if(typeof window!=='undefined')window.addEventListener('pagehide',this.pageHide);
  }
  onDestroy():void {
    view.off('canvas-resize',this.onResize,this);
    game.off(Game.EVENT_HIDE,this.onHide,this);game.off(Game.EVENT_SHOW,this.onShow,this);
    if(typeof window!=='undefined')window.removeEventListener('pagehide',this.pageHide);
  }
  private onHide():void{this.hidden=true;if(this.book)this.save();}
  private onShow():void{this.hidden=false;this.skipNextFrame=true;}
  private onResize():void{this.unschedule(this.rebuildLayout);this.scheduleOnce(this.rebuildLayout,0);}
  private rebuildLayout():void {
    const wasPhone=!!this.phone,wasDialog=this.modalKind,wasNotice=this.noticeMessage;
    const frame=view.getFrameSize(),requestedExtra=Math.max(0,720*frame.height/frame.width-1280);
    const idle=this.book.mode==='idle',baseMapHeight=idle?1008:777,mapY=idle?-18:97.5;
    // Very tall windows must still fit the whole map viewport inside town at 100m.
    this.screenExtra=CityMap.fitViewportHeight(this.book.data,baseMapHeight+requestedExtra)-baseMapHeight;
    view.setDesignResolutionSize(720,1280+this.screenExtra,ResolutionPolicy.SHOW_ALL);
    if(this.root){this.root.active=false;this.root.destroy();}this.phone=null;this.modal=null;this.modalKind=null;this.toast=null;
    this.root=item(this.node.parent!,'DeliveryUI');
    box(this.root,'Background',0,0,720,1280+this.screenExtra,C.light,0);
    this.city=new CityMap(this.root,this.book.data,baseMapHeight+this.screenExtra,()=>sys.openURL('https://www.openstreetmap.org/copyright'),mapY);
    this.city.setVehicle(this.book.player.vehicleTier);
    this.header(item(this.root,'HeaderGroup',0,this.screenExtra/2));this.controls();
    this.panel=item(this.root,'OrderPanel',0,-this.screenExtra/2);
    const active=this.book.active;
    if(active)this.city.setRoutes(active.routes,active.selected,true);
    const pose=this.book.riderPose;this.city.setRider(pose.point,pose.angle);
    this.city.locate(true);
    this.renderPanel();if(wasPhone)this.openPhone();
    if(wasDialog==='receipt'&&!this.modal)this.openReceipt();
    if(wasDialog==='garage')this.openGarage();
    if(wasNotice)this.showMessage(wasNotice);
  }
  private header(parent:Node):void {
    box(parent,'Header',0,563,720,154,C.primary,0);
    label(parent,'送外卖',-185,595,35,C.ink,285,true);
    const badge=box(parent,'CityBadge',213,595,226,38,'#FFE697',18);
    this.vehicleBadge=label(badge,'',0,0,18,C.ink,210,true,'center');tap(badge,()=>this.openGarage());
    this.money=label(parent,'',-222,539,28,C.ink,215,true);
    this.rating=label(parent,'',10,539,21,C.ink,180,true,'center');
    this.experience=label(parent,'',233,539,19,C.ink,210,true,'right');
    this.updatePlayerHeader();
  }
  private controls():void {
    const y=this.book.mode==='idle'?-460:-229;
    const locate=box(this.root,'FollowRider',309,y-this.screenExtra/2,54,54,C.primary,13);
    icon(locate,'target',0,0,C.ink,.85);tap(locate,()=>this.city.locate());
  }
  private openPhone():void {
    if(this.phone||this.book.mode!=='idle')return;
    this.phone=new OrderPhone(this.root,this.book,1280+this.screenExtra,id=>this.accept(id),()=>this.closePhone(),()=>{
      if(!this.act(()=>this.book.refreshFree()))return;
      this.closePhone();this.openPhone();
    });
  }
  private closePhone():void{if(this.phone)this.phone.close();this.phone=null;}
  private accept(id:string):void {
    if(!this.act(()=>this.book.accept(id)))return;this.closePhone();
    this.rebuildLayout();
  }
  private renderPanel():void {
    for(const child of [...this.panel.children])child.destroy();this.panel.removeAllChildren();
    this.timer=null;this.tripLabel=null;this.progressFill=null;
    this.updatePlayerHeader();
    const active=this.book.active;
    if(!active){
      const bar=box(this.panel,'DispatchBar',0,-581,720,118,C.paper,0);
      button(bar,'抢单',0,0,660,76,()=>this.openPhone());
      return;
    }
    const p=box(this.panel,'DeliverySheet',0,-461,700,358,C.paper,24);
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
      label(p,'顾客留言：放门口，别敲门',-8,26,25,C.ink,630,true);
      label(p,'已经送到，按要求交付可获得好评',-8,-15,20,C.muted,630);
      button(p,'敲门交付',-170,-100,300,63,()=>this.deliverAtDoor(false),C.light,C.ink);
      button(p,'按要求放门口',170,-100,300,63,()=>this.deliverAtDoor(true));
      label(p,'交付选择期间不消耗配送时间',0,-150,18,C.muted,650,false,'center');
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
    if(this.skipNextFrame){this.skipNextFrame=false;return;}
    if(this.book.mode!=='running')return;
    const arrived=this.book.advance(dt),pose=this.book.riderPose;
    this.city.setRider(pose.point,pose.angle);this.updateProgress();
    this.saveElapsed+=dt;if(arrived||this.saveElapsed>=.5){this.saveElapsed=0;this.save();}
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
    if(ok)this.lastSaveError='';this.updatePlayerHeader();
  }
  private updatePlayerHeader():void {
    if(!this.money)return;const p=this.book.player;
    this.city.setVehicle(p.vehicleTier);
    this.money.string='¥'+(p.cashCents/100).toFixed(2);this.rating.string='评价 '+p.rating;
    this.experience.string=`Lv.${p.level} · ${p.experience}经验`;
    const vehicle=VEHICLES[p.vehicleTier-1];
    this.vehicleBadge.string=`澄川 · ${vehicle.name} ${vehicle.speedKph}km/h`;
  }
  private showMessage(message:string):void {
    if(!this.root)return;if(this.toast){this.toast.active=false;this.toast.destroy();}
    this.noticeMessage=message;
    const node=this.toast=box(this.root,'NoticeToast',0,-230-this.screenExtra/2,680,68,'#FFF0B7',16,'#D6B65A');
    label(node,message,0,0,18,C.ink,650,true,'center');
    this.scheduleOnce(()=>{if(node.isValid)node.destroy();if(this.toast===node){this.toast=null;this.noticeMessage='';}},4);
  }
  private closeDialog():void{if(this.modal){this.modal.active=false;this.modal.destroy();this.modal=null;}this.modalKind=null;}
  private dialog(title:string,height:number,kind:'receipt'|'garage'):{layer:Node;card:Node} {
    this.closeDialog();this.modalKind=kind;const layer=this.modal=item(this.root,'CountyDialog',0,0,720,1280+this.screenExtra);layer.addComponent(BlockInputEvents);
    const shade=box(layer,'Shade',0,0,720,1280+this.screenExtra,'#00000099',0);shade.on(Node.EventType.TOUCH_END,()=>this.closeDialog());
    const card=box(layer,'DialogCard',0,0,638,height,C.paper,28);card.addComponent(BlockInputEvents);
    label(card,title,-39,height/2-65,29,C.ink,480,true);
    button(card,'关闭',245,height/2-63,75,47,()=>this.closeDialog(),C.light,C.ink);
    return {layer,card};
  }
  private deliverAtDoor(answer:boolean):void{if(this.act(()=>this.book.settle(answer)))this.renderPanel();}
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
    },p.vehicleTier===1&&!gap?C.primary:C.light,C.ink);
  }
  private updateProgress():void {
    const active=this.book.active;if(!active)return;
    const progress=this.book.progress;
    if(this.tripLabel)this.tripLabel.string=this.book.tripStage==='pickup'?'前往餐厅取餐':this.book.tripStage==='collecting'?`取餐中 · ${Math.ceil(this.book.pickupWaitRemaining)}秒`:'正在送往顾客';
    if(this.timer)this.timer.string=active.mode==='done'?'已到达':'剩余 '+formatRemaining(progress.remainingSeconds);
    if(this.progressFill){this.progressFill.setScale(progress.progress,1,1);this.progressFill.setPosition(-320+320*progress.progress,-15);}
  }
}
