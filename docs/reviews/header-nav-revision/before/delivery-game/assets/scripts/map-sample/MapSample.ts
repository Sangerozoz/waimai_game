import { _decorator, BlockInputEvents, Component, Game, game, JsonAsset, Label, Node, resources, UITransform, ResolutionPolicy, sys, view } from 'cc';
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
import { presentationMetrics, readable, scrollContent, textHeight } from './PresentationLayout';
import { vehicleSideArt } from './VehicleSideArt';
import { SafeInsets, rotatedViewportInsets, viewportInsets } from './SafeAreaLayout';
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
    // Use the next frame's SHOW_ALL scale, rather than the previous layout's extra height.
    const idle=this.book.mode==='idle',sheetHeight=Math.max(520,presentationMetrics(1280+requestedExtra).body*16),baseMapHeight=idle?1280:1162-sheetHeight;
    // Very tall windows must still fit the whole map viewport inside town at 100m.
    this.screenExtra=CityMap.fitViewportHeight(this.book.data,baseMapHeight+requestedExtra)-baseMapHeight;
    view.setDesignResolutionSize(720,1280+this.screenExtra,ResolutionPolicy.SHOW_ALL);
    this.safeInsets=this.readSafeInsets();
    const bottom=this.safeInsets.bottom,mapHeight=Math.max(1,baseMapHeight+this.screenExtra-(idle?0:bottom)),mapY=idle?0:(sheetHeight-1162+1280)/2+bottom/2;
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
  private metrics(){return presentationMetrics(1280+this.screenExtra);}
  private sheetHeight():number{return Math.max(520,this.metrics().body*16);}
  private action(parent:Node,text:string,x:number,y:number,width:number,action:()=>void,fill=C.primary,enabled=true):Node {
    const m=this.metrics(),node=box(parent,'Button-'+text,x,y,width,m.action,fill,16,fill===C.paper?C.line:undefined);
    readable(node,text,0,0,m.body,enabled?C.ink:C.muted,width-20,true,'center',m.action-8);if(enabled)tap(node,action);return node;
  }
  private header(parent:Node):void {
    const width=720-this.safeInsets.left-this.safeInsets.right-36,m=this.metrics(),height=220;
    const card=box(parent,'Header',(this.safeInsets.left-this.safeInsets.right)/2,628-height/2,width,height,C.paper,18);
    const content=item(card,'HeaderContent');
    const avatar=box(content,'PlayerAvatar',-width/2+54,62,64,64,'#F1F2F4',32);readable(avatar,'骑',0,0,30,C.muted,60,true,'center');
    readable(content,'澄川骑手',-width/2+210,69,m.body,C.ink,220,true);
    this.experience=readable(content,'',width/2-126,69,m.aux,C.muted,228,false,'right',52);
    readable(content,'余额',-width/2+62,20,m.aux,C.muted,84);
    this.money=readable(content,'',-74,-43,m.amount,C.ink,width-190,true,'left',100);
    readable(content,'评价',width/2-78,20,m.aux,C.muted,112,false,'center');
    this.rating=readable(content,'',width/2-78,-43,m.body+8,C.ink,112,true,'center',100);
    this.updatePlayerHeader();
  }
  private controls():void {
    const station=item(this.root,'StationEntry',309-this.safeInsets.right,330+this.screenExtra/2-this.safeInsets.top,100,100);
    const picture=box(station,'PlaceholderIcon-station',0,11,36,32,'#F0EEE7',8);
    label(picture,'站',0,0,20,'#AAA69C',32,true,'center');readable(station,'站点',0,-24,this.metrics().aux,'#AAA69C',94,true,'center');
    const y=this.book.mode==='idle'?-450:-522+this.sheetHeight()+this.metrics().action/2+20;
    const locate=box(this.root,'FollowRider',360-this.safeInsets.right-this.metrics().action/2-13,y-this.screenExtra/2+this.safeInsets.bottom,this.metrics().action,this.metrics().action,C.primary,13);
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
      const slot=main?box(bar,'Nav-'+entry.key,entry.x,0,136,100,enabled?C.primary:'#EAE7DE',30):item(bar,'Nav-'+entry.key,entry.x,0,116,100);
      if(main)label(slot,entry.name,0,0,34,foreground,124,true,'center');
      else{
        const pictogram=box(slot,'PlaceholderIcon-'+entry.key,0,23,36,32,enabled?'#FFF1BB':'#F0EEE7',8);
        if(entry.key==='map')icon(pictogram,'map',0,0,foreground,.7);else label(pictogram,entry.glyph,0,0,20,foreground,32,true,'center');
        readable(slot,entry.name,0,-20,this.metrics().aux,foreground,108,true,'center');
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
    const height=this.sheetHeight(),width=720-this.safeInsets.left-this.safeInsets.right-20,m=this.metrics();
    const p=box(this.panel,'DeliverySheet',(this.safeInsets.left-this.safeInsets.right)/2,-522+height/2,width,height,C.paper,24);
    const top=height/2,inner=width-40;
    box(p,'Handle',0,top-12,50,4,C.line,2);
    const offer=active.offer,route=active.routes[active.selected],timing=this.book.timingForRoute(route);
    const metadata=`${offer.food} · ${offer.weightKg}kg · ${offer.fragility==='fragile'?'怕洒':offer.fragility==='durable'?'耐放':'普通餐品'}`;
    const metadataHeight=Math.max(58,textHeight(metadata,m.aux,inner-200)),metadataExtra=metadataHeight-58;
    const heading=active.mode==='routes'?scrollContent(p,inner,top-24,-top+m.action+116,435+metadataExtra):p;
    const headingTop=active.mode==='routes'?0:top-24;
    readable(heading,`${this.book.data.pois[offer.from].name} → ${this.book.data.pois[offer.to].name}`,0,headingTop-55,m.body,C.ink,inner,true,'left',104);
    readable(heading,metadata,-100,headingTop-111-metadataHeight/2,m.aux,C.muted,inner-200,false,'left',metadataHeight);
    const receipt=active.receipt;
    readable(heading,(receipt?'+¥':'基础¥')+((receipt?receipt.incomeCents:offer.feeCents)/100).toFixed(2),inner/2-95,headingTop-140,m.body,'#795020',190,true,'right',58);
    if(active.mode==='routes'){
      const gap=10,w=(inner-(active.routes.length-1)*gap)/active.routes.length,routeY=-310-metadataExtra;
      active.routes.forEach((r,i)=>{
        const selected=i===active.selected,x=-inner/2+w/2+i*(w+gap),color=ROUTE_COLORS[r.preference];
        const card=box(heading,'Route-'+r.preference,x,routeY,w,210,selected?'#FFF5CE':'#F7F5EF',12,selected?color:C.line);
        readable(card,(selected?'✓ ':'')+TITLES[r.preference],0,75,m.aux,selected?color:C.ink,w-12,true,'center',50);
        const estimated=this.book.timingForRoute(r).displaySeconds,late=estimated>active.deadlineSeconds;
        readable(card,formatDeliveryTime(estimated),0,18,m.body,C.ink,w-12,true,'center',50);
        readable(card,`${late?'预计晚到':'准时'}\n餐损${Math.round(r.risk*100)}%`,0,-58,m.aux,late?'#B76A3A':C.muted,w-12,false,'center',90);
        tap(card,()=>{if(!this.act(()=>this.book.select(i)))return;this.city.setRoutes(active.routes,i);this.renderPanel();});
      });
      const buttonY=-top+100+m.action/2,secondary=Math.max(170,inner*.29);
      this.action(p,'返回接单',-inner/2+secondary/2,buttonY,secondary,()=>{if(!this.act(()=>this.book.cancel()))return;this.rebuildLayout();this.openPhone();},C.light);
      this.action(p,'出发配送',secondary/2+8,buttonY,inner-secondary-16,()=>{if(!this.act(()=>this.book.depart()))return;this.city.locate(true);this.renderPanel();});
      readable(p,`${offer.type==='urgent'?'加急 · ':''}${offer.demand==='door'?'放门口，别敲门':'直接交付'} · ${formatDeliveryTime(active.deadlineSeconds)}内送达`,0,-top+48,m.aux,C.muted,inner,false,'center',76);
    }else if(active.mode==='arrived'){
      readable(p,'已到达顾客',0,-metadataExtra,m.body,C.ink,inner,true);readable(p,'请在弹窗中选择交付方式',0,-58-metadataExtra,m.aux,C.muted,inner);this.openDemand();
    }else if(active.mode==='done'&&receipt){
      readable(p,'配送完成 · 收入已到账',0,top-230-metadataExtra,m.body,C.green,inner,true);
      readable(p,`评价 ${receipt.ratingAfter}（${receipt.ratingDelta>=0?'+':''}${receipt.ratingDelta}） · 经验 +${receipt.experienceGained} · Lv.${receipt.levelAfter}`,0,top-300-metadataExtra,m.aux,C.ink,inner,true,'left',76);
      this.action(p,'结算详情',-inner/2+100,-top+70,200,()=>this.openReceipt(),C.light);
      this.action(p,'继续接单',108,-top+70,inner-216,()=>this.continueOrders());
      if(this.receipts.observe(active))this.openReceipt();
    }else{
      this.tripLabel=readable(p,'',-104,top-254-metadataExtra,m.body,C.ink,inner-210,true,'left',90);
      this.timer=readable(p,'',inner/2-105,top-254-metadataExtra,m.aux,C.ink,210,true,'right',90);
      const progression=item(p,'DeliveryProgress',0,-metadataExtra);
      box(progression,'ProgressTrack',0,-60,inner,10,C.line,5);
      this.progressFill=box(progression,'ProgressFill',-inner/2,-60,inner,10,C.primary,5);
      readable(progression,`${TITLES[route.preference]} · 全程 ${(route.metres/1000).toFixed(1)}km · 预计${formatDeliveryTime(timing.displaySeconds)}`,0,-140,m.aux,C.muted,inner,false,'left',90);this.updateProgress();
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
    this.money.string='¥'+(p.cashCents/100).toFixed(2);
    const m=this.metrics(),moneyWidth=this.money.node.getComponent(UITransform)!.width;
    this.money.fontSize=textHeight(this.money.string,m.amount,moneyWidth)>100?m.body:m.amount;this.money.lineHeight=Math.ceil(this.money.fontSize*1.42);
    this.rating.string=String(p.rating);
    this.experience.string=`Lv.${p.level} · ${p.experience}经验`;
  }
  private showMessage(message:string):void {
    if(!this.root)return;if(this.toast){this.toast.active=false;this.toast.destroy();}
    this.noticeMessage=message;
    const m=this.metrics(),width=720-this.safeInsets.left-this.safeInsets.right-36,height=textHeight(message,m.body,width-32)+24;
    const node=this.toast=box(this.root,'NoticeToast',(this.safeInsets.left-this.safeInsets.right)/2,-230-this.screenExtra/2,width,height,'#FFF0B7',16,'#D6B65A');
    readable(node,message,0,0,m.body,C.ink,width-32,true,'center',height-16);
    this.scheduleOnce(()=>{if(node.isValid)node.destroy();if(this.toast===node){this.toast=null;this.noticeMessage='';}},4);
  }
  private closeDialog():void{if(this.modal){this.modal.active=false;this.modal.destroy();this.modal=null;}this.modalKind=null;this.billValues=[];this.billDate=null;}
  private dialog(title:string,requestedHeight:number,kind:DialogKind,dismissible=true):{layer:Node;card:Node;width:number;height:number;top:number;bottom:number} {
    this.closeDialog();this.modalKind=kind;const screenHeight=1280+this.screenExtra,insets=this.safeInsets||{top:0,bottom:0,left:0,right:0};
    const layer=this.modal=item(this.root,'CountyDialog',0,0,720,screenHeight);layer.addComponent(BlockInputEvents);
    const shade=box(layer,'Shade',0,0,720,screenHeight,'#00000099',0);if(dismissible)tap(shade,()=>this.closeDialog());
    const width=Math.min(684,720-insets.left-insets.right-36),height=Math.min(requestedHeight,screenHeight-insets.top-insets.bottom-36);
    const card=box(layer,'DialogCard',(insets.left-insets.right)/2,(insets.bottom-insets.top)/2,width,height,C.paper,28);card.addComponent(BlockInputEvents);
    const m=this.metrics();readable(card,title,-60,height/2-64,m.body+4,C.ink,width-180,true,'left',70);
    if(dismissible)this.action(card,'关闭',width/2-72,height/2-64,108,()=>this.closeDialog(),C.light);
    return {layer,card,width,height,top:height/2-132,bottom:-height/2+24};
  }
  private openDemand():void {
    if(this.book.mode!=='arrived'||this.modalKind==='demand')return;
    const {card,width,height,top,bottom}=this.dialog('交付要求',630,'demand',false),m=this.metrics(),inner=width-48;
    const content=scrollContent(card,inner,top,bottom+2*m.action+36,190);
    readable(content,'顾客留言：放门口，别敲门',0,-60,m.body,C.ink,inner,true,'center',110);
    readable(content,'选择期间不消耗配送时间',0,-152,m.aux,C.muted,inner,false,'center',70);
    this.action(card,'敲门交付',0,-height/2+24+m.action*1.5+16,inner,()=>this.deliverAtDoor(false),C.light);
    this.action(card,'按要求放门口',0,-height/2+24+m.action/2,inner,()=>this.deliverAtDoor(true));
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
    const {card,width,height,top,bottom}=this.dialog('配送结算',1040,'receipt'),m=this.metrics(),inner=width-48;
    const entries=[
      {text:'+¥'+(receipt.incomeCents/100).toFixed(2),size:m.amount+12,bold:true,color:'#795020'},
      {text:`基础价 ¥${(receipt.basePriceCents/100).toFixed(2)} · 本单实际收入`,size:m.aux},
      ...receipt.summary.map(line=>({text:'· '+line,size:m.body})),
      {text:`评价 ${receipt.ratingBefore} → ${receipt.ratingAfter}（${receipt.ratingDelta>=0?'+':''}${receipt.ratingDelta}）`,size:m.body,bold:true},
      {text:`经验 +${receipt.experienceGained} · 等级 Lv.${receipt.levelBefore} → Lv.${receipt.levelAfter}`,size:m.body},
      {text:'余额 ¥'+(receipt.newCashCents/100).toFixed(2),size:m.body,bold:true},
    ];
    const heights=entries.map(row=>textHeight(row.text,row.size,inner)+16),content=scrollContent(card,inner,top,bottom+m.action+24,heights.reduce((a,b)=>a+b,0)+20);
    let offset=0;entries.forEach((row,i)=>{readable(content,row.text,0,-offset-heights[i]/2,row.size,row.color||C.ink,inner,!!row.bold,'left',heights[i]);offset+=heights[i];});
    this.action(card,'确认，继续接单',0,-height/2+24+m.action/2,inner,()=>this.continueOrders());
  }
  private continueOrders():void {
    if(!this.act(()=>this.book.finish()))return;
    this.closeDialog();this.rebuildLayout();this.openPhone();
  }
  private openMaps():void {
    if(this.book.mode==='arrived')return;
    const {card,width,top,bottom}=this.dialog('地图',1060,'maps'),m=this.metrics(),inner=width-48;
    const regions=[{name:'县城',requirements:''},{name:'城市',requirements:'100单 · C车 · 招募1名骑手 · 站点2级'},{name:'省会',requirements:'300单 · B车 · C骑手上岗 · 站点3级'},{name:'一线',requirements:'800单 · A车 · A骑手上岗 · 站点4级'},{name:'国际一线',requirements:'2000单 · A车 · A骑手上岗 · 站点5级'}];
    const rowHeights=regions.map(region=>region.requirements?textHeight(region.requirements,m.aux,inner-40)+90:110),content=scrollContent(card,inner,top,bottom,rowHeights.reduce((a,b)=>a+b+18,0));
    let offset=0;regions.forEach((region,i)=>{
      const enabled=i===0,foreground=enabled?C.ink:'#AAA69C',height=rowHeights[i],row=box(content,'Region-'+i,0,-offset-height/2,inner,height,enabled?'#FFF1BB':'#F0EEE7',16);
      readable(row,region.name,0,height/2-40,m.body,foreground,inner-40,true);
      if(region.requirements)readable(row,region.requirements,0,-34,m.aux,foreground,inner-40,false,'left',height-80);
      if(enabled)tap(row,()=>this.closeDialog());offset+=height+18;
    });
  }
  private openBills():void {
    if(this.book.mode==='arrived')return;
    const {card,width,top,bottom}=this.dialog('账单',1100,'bills'),m=this.metrics(),inner=width-48,bill=this.book.billing;
    this.billDate=readable(card,bill.day,0,top-20,m.aux,C.muted,inner,false,'center');
    const groups=[{name:'钱包',indices:[3]},{name:'今日',indices:[0,1,2,4,5,6,7,8]},{name:'累计',indices:[9,10,11]}],rows=billingRows(bill);
    // Reserve the largest legal monetary value (including a historical lower-bound mark).
    // Live updates only replace strings, so a growing balance cannot clip or reset scrolling.
    const maximumMoney='≥¥'+(Number.MAX_SAFE_INTEGER/100).toFixed(2);
    const rowHeight=Math.max(86,m.body*3.1,textHeight(maximumMoney,m.body+8,inner*.55)+16),content=scrollContent(card,inner,top-60,bottom,12*rowHeight+3*74+24);
    let offset=0;for(const group of groups){
      readable(content,group.name,0,-offset-36,m.body,C.ink,inner,true);offset+=74;
      for(const index of group.indices){
        const row=rows[index],prominent=index===3||index===0,cell=item(content,'BillMetric-'+index,0,-offset-rowHeight/2,inner,rowHeight);
        const titleWidth=inner*.43,valueWidth=inner*.55;
        readable(cell,row.title,-inner/2+titleWidth/2,0,m.aux,C.muted,titleWidth,false,'left',rowHeight-10);
        this.billValues[index]=readable(cell,row.value,inner/2-valueWidth/2,0,prominent?m.body+8:m.body,prominent?'#795020':C.ink,valueWidth,true,'right',rowHeight-10);
        box(cell,'Divider',0,-rowHeight/2,inner,1,C.line,0);offset+=rowHeight;
      }
    }
  }
  private updateBills():void {
    if(this.modalKind!=='bills')return;
    const bill=this.book.billing;if(this.billDate)this.billDate.string=bill.day;
    billingRows(bill).forEach((row,i)=>{if(this.billValues[i])this.billValues[i].string=row.value;});
  }
  private openGarage():void {
    if(this.book.mode!=='idle'){this.showMessage('先送完当前订单，再升级车辆');return;}
    const p=this.book.player,current=VEHICLES[p.vehicleTier-1],next=VEHICLES[1],{card,width,height,top,bottom}=this.dialog('我的车辆',1100,'garage'),m=this.metrics(),inner=width-48;
    const gap=Math.max(0,next.upgradeFeeCents-p.cashCents),enabled=p.vehicleTier===1&&!gap;
    const text=p.vehicleTier===2?'已达当前站点上限':gap?`还差 ¥${(gap/100).toFixed(2)}`:`花 ¥${(next.upgradeFeeCents/100).toFixed(0)} 升级 ${next.name}`;
    const content=scrollContent(card,inner,top,bottom+m.action+24,740);
    const artName=p.vehicleTier===2?'翻新电动车':'旧电动车';
    readable(content,artName+' · '+current.name,0,-34,m.body,C.ink,inner,true,'center');
    const fallback=readable(content,artName,0,-190,m.body,C.muted,inner,true,'center').node;
    vehicleSideArt(content,p.vehicleTier,0,-194,inner-30,230,fallback);
    readable(content,`当前 ${current.speedKph}km/h · 载重 ${current.capacityKg}kg`,0,-358,m.body,C.ink,inner,false,'center',90);
    readable(content,`跑单收入 ×${current.incomeMultiplier.toFixed(2)}`,0,-428,m.body,C.ink,inner,false,'center',72);
    const upgrade=box(content,'UpgradeCard',0,-550,inner,154,C.light,18);
    readable(upgrade,p.vehicleTier===1?`升级 ${next.name} · ¥${(next.upgradeFeeCents/100).toFixed(2)}`:`${next.name} 已拥有`,0,42,m.body,C.ink,inner-24,true,'center',65);
    readable(upgrade,`${next.speedKph}km/h · 收入 +${Math.round((next.incomeMultiplier-1)*100)}% · 载重 ${next.capacityKg}kg`,0,-34,m.aux,C.muted,inner-24,false,'center',80);
    readable(content,'当前余额 ¥'+(p.cashCents/100).toFixed(2),0,-686,m.body,C.ink,inner,true,'center',88);
    this.action(card,text,0,-height/2+24+m.action/2,inner,()=>{if(!this.act(()=>this.book.upgradeVehicle()))return;this.closeDialog();this.renderPanel();this.showMessage('已升级为 D+');},enabled?C.primary:C.light,enabled);
  }
  private updateProgress():void {
    const active=this.book.active;if(!active)return;
    const progress=this.book.progress;
    if(this.tripLabel)this.tripLabel.string=this.book.tripStage==='pickup'?'前往餐厅取餐':this.book.tripStage==='collecting'?`正在取餐中 · ${Math.ceil(this.book.pickupWaitRemaining)}秒`:'正在送往顾客';
    if(this.timer)this.timer.string=active.mode==='done'?'已到达':'剩余 '+formatRemaining(progress.remainingSeconds);
    if(this.progressFill){this.progressFill.setScale(progress.progress,1,1);this.progressFill.setPosition(-(720-this.safeInsets.left-this.safeInsets.right-60)/2*(1-progress.progress),-60);}
  }
}
