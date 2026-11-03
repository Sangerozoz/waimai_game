import { VEHICLE_GRADES, VEHICLE_NAMES, VEHICLE_LIMITS, VEHICLE_SPEED, VEHICLE_CAPACITY, VEHICLE_INCOME, VEHICLE_PRICE } from './VehicleOwnership';
import { DeliverySound } from './DeliverySound';
import { localBillingDay } from './DeliveryLedger';
import { ClickBoost, ForegroundClock, isTripProfile } from './TripClock';
import { WebWriterLease } from './WebWriterLease';
import { _decorator, BlockInputEvents, Component, EventTouch, Game, game, Graphics, input, Input, JsonAsset, Label, Node, ScrollView, Vec2, Vec3, resources, Sprite, UITransform, ResolutionPolicy, sys, view } from 'cc';
import { CityMap, ROUTE_COLORS } from './CityMap';
import { prepareCity } from './PlaceCatalog';
import { CityData, Point, Preference } from './MapTypes';
import { OrderBook } from './OrderBook';
import { buyerRemark, deadlineText, foodDescription, orderCautions } from './OrderPresentation';
import { compactOrderHeight, compactOrderInfo, CompactOrder } from './CompactOrderInfo';
import { OrderPhone } from './OrderPhone';
import { ReceiptPresentation } from './ReceiptPresentation';
import { CountySaveStore } from './CountySaveStore';
import { receiptIncomeBreakdown } from './CountyRules';
import { COUNTY_VEHICLES as VEHICLES } from './CountyConfig';
import { formatDeliveryTime, formatRemaining, PICKUP_STOP_SECONDS } from './DeliveryClock';
import { billingRows } from './BillingPresentation';
import { box, button, closeButton, C, col, icon, item, label, material, roundAction, topOnlyBar, outline, paintBox, skin, tap } from './SampleUI';
import { cartoonArt } from './CartoonArt';
import { cssUnits, pageMargin, experienceProgress, presentationMetrics, readable, scrollContent, textHeight } from './PresentationLayout';
import { vehicleSideArt } from './VehicleSideArt';
import { SafeInsets, rotatedViewportInsets, viewportInsets } from './SafeAreaLayout';
const {ccclass}=_decorator;
const TITLES:Record<Preference,string>={fast:'快捷路',main:'主干道',smooth:'平稳路'};
type DialogKind='receipt'|'garage'|'demand'|'maps'|'bills'|'pause'|'entry'|'profile';

@ccclass('MapSample')
export class MapSample extends Component {
  private book!:OrderBook;
  private city!:CityMap;
  private root!:Node;
  private panel!:Node;
  private phone:OrderPhone|null=null;
  private gallery:Node|null=null;
  private galleryMine=false;
  private orderCardOpen=true;
  private timer:Label|null=null;
  private tripLabel:Label|null=null;
  private progressFill:Node|null=null;
  private pickupServiceButton:Node|null=null;
  private screenExtra=0;
  private safeInsets:SafeInsets={top:0,bottom:0,left:0,right:0};
  private hidden=false;
  private skipNextFrame=false;
  private store!:CountySaveStore;
  private money!:Label;
  private rating!:Label;
  private experience!:Label;
  private profileCard!:Node;
  private playerName!:Label;
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
  private pendingSave=false;
  private paused=false;
  private cancellationPendingReturn=false;
  private entryGate=false;
  private get gameplayFrozen():boolean{return this.paused||this.entryGate;}
  private readonly writerLease=new WebWriterLease();
  private readonly foregroundClock=new ForegroundClock();
  private readonly clickBoost=new ClickBoost();
  private receiptReturn: boolean|null=null;
  private layoutDone=false;
  private deliveryStatus:Node|null=null;
  private sound:DeliverySound|null=null;
  private pendingSound:'shop'|'pickup'|'success'|null=null;
  private boostControl:Node|null=null;
  private boostLabel:Label|null=null;
  private lastHandoffEvent='';
  private readonly pageHide=()=>this.onHide();
  private readonly viewportResize=()=>this.onResize();

  start():void {
    const canvas=this.node.parent!;this.sound=new DeliverySound(this.node);
    const loading=label(canvas,'正在打开澄川骑手地图…',0,0,26,C.ink,650,true,'center');
    resources.load('map-sample/city',JsonAsset,async(error,asset)=>{
      if(!this.isValid)return;
      if(error){loading.string='地图加载失败，请重新打开';console.error(error);return;}
      let recovery='';
      try {
        await this.writerLease.acquire();if(!this.isValid){this.writerLease.release();return;}
        const data=prepareCity(asset.json as CityData);
        this.store=new CountySaveStore({getItem:key=>sys.localStorage.getItem(key),setItem:(key,value)=>sys.localStorage.setItem(key,value)},undefined,()=>this.writerLease.writable);
        const loaded=this.store.load(raw=>OrderBook.restore(data,raw),()=>new OrderBook(data));this.book=loaded.session;recovery=loaded.message;
      }
      catch(error){loading.string='路网暂时不可用，请重新打开';console.error(error);return;}
      this.entryGate=!!this.book.active;this.onlineAt=this.hidden||this.gameplayFrozen?null:Date.now();loading.node.destroy();this.rebuildLayout();if(!this.gameplayFrozen&&this.book.mode==='arrived')this.act(()=>this.book.settle(this.book.active?.offer.demand==='door'?true:null));this.save();this.renderPanel();if(this.gameplayFrozen)this.openPauseDialog();if(!this.pendingSave&&!this.gameplayFrozen)this.presentHandoff();view.on('canvas-resize',this.onResize,this);
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
    this.sound?.destroy();this.writerLease.release();
    this.city?.cancelLocate();
    view.off('canvas-resize',this.onResize,this);
    game.off(Game.EVENT_HIDE,this.onHide,this);game.off(Game.EVENT_SHOW,this.onShow,this);
    if(typeof window!=='undefined'){
      window.removeEventListener('pagehide',this.pageHide);
      window.removeEventListener('orientationchange',this.viewportResize);
      window.visualViewport?.removeEventListener('resize',this.viewportResize);
    }
  }
  private onHide():void{
    this.sound?.stop();this.pendingSound=null;
    this.clickBoost.reset();this.foregroundClock.reset();
    this.city?.cancelLocate();
    if(!this.gameplayFrozen&&this.writerLease.writable&&!this.pendingSave&&this.book&&!this.hidden&&this.onlineAt!==null)this.book.recordOnlineTime(this.onlineAt,Date.now());
    this.onlineAt=null;this.hidden=true;this.refreshBoost();if(this.book)this.save();
  }
  private onShow():void{
    this.clickBoost.reset();this.foregroundClock.reset();
    this.onlineAt=this.gameplayFrozen?null:Date.now();this.hidden=false;this.skipNextFrame=true;
    if(this.book){
      const next=this.readSafeInsets();
      if(next.top!==this.safeInsets.top||next.bottom!==this.safeInsets.bottom||next.left!==this.safeInsets.left||next.right!==this.safeInsets.right)this.onResize();
    }
  }
  private onResize():void{if(!this.book)return;this.unschedule(this.rebuildLayout);this.scheduleOnce(()=>this.rebuildLayout(),0);}
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
  private rebuildLayout(resetCamera=false):void {
    if(this.book.active)this.orderCardOpen=true;
    const oldScroll=this.panel?.getChildByName('DeliverySheet')?.getChildByName('SheetContent')?.getChildByName('ScrollableContent')?.getComponent(ScrollView);
    const scrollY=oldScroll?.getScrollOffset().y||0;
    const camera=resetCamera?null:this.city?.captureView?.();
    const wasPhone=!!this.phone,wasDialog=this.modalKind,wasGallery=!!this.gallery,wasNotice=this.noticeMessage;
    const frame=view.getFrameSize(),requestedExtra=Math.max(0,720*frame.height/frame.width-1280);
    // Use the next frame's SHOW_ALL scale, rather than the previous layout's extra height.
    const idle=this.book.mode==='idle'||this.book.mode==='done'||!this.orderCardOpen,provisionalHeight=this.sheetHeightFor(1280+requestedExtra),baseMapHeight=idle?1280:640-this.sheetBottomFor(1280+requestedExtra)-provisionalHeight;
    // Very tall windows must still fit the whole map viewport inside town at 100m.
    this.screenExtra=CityMap.fitViewportHeight(this.book.data,baseMapHeight+requestedExtra)-baseMapHeight;
    view.setDesignResolutionSize(720,1280+this.screenExtra,ResolutionPolicy.SHOW_ALL);
    this.safeInsets=this.readSafeInsets();
    const sheetHeight=this.sheetHeight(),bottom=this.safeInsets.bottom,mapHeight=Math.max(1,(idle?1280:640-this.sheetBottom()-sheetHeight)+this.screenExtra-(idle?0:bottom)),mapY=idle?0:(this.sheetBottom()+sheetHeight+640)/2+bottom/2;
    if(this.root){this.city?.cancelLocate();this.root.active=false;this.root.destroy();}this.phone=null;this.gallery=null;this.modal=null;this.modalKind=null;this.billValues=[];this.billDate=null;this.toast=null;this.damageNotice=null;
    this.layoutDone=this.book.mode==='done';this.boostControl=null;this.boostLabel=null;this.deliveryStatus=null;
    this.root=item(this.node.parent!,'DeliveryUI');
    box(this.root,'Background',0,0,720,1280+this.screenExtra,C.light,0);
    this.city=new CityMap(this.root,this.book.data,mapHeight,()=>sys.openURL('https://www.openstreetmap.org/copyright'),mapY,idle&&this.book.mode!=='done'?168+bottom:0,this.safeInsets,1280+this.screenExtra);
    this.city.setVehicle(this.book.player.vehicleTier);
    this.header(item(this.root,'HeaderGroup',0,this.screenExtra/2-this.safeInsets.top));this.controls();
    this.panel=item(this.root,'OrderPanel',0,-this.screenExtra/2+bottom);
    const active=this.book.active;
    if(active&&active.mode!=='done'){
      const from=this.book.data.pois[active.offer.from],to=this.book.data.pois[active.offer.to];
      const point=(id:string):Point=>{const node=this.book.data.nodes.find(n=>n.id===id)!;return [node.x,node.y];};
      if(active.mode!=='done')this.city.setNavigationStops({pickupName:from.name,deliveryName:to.name,food:active.offer.food,pickup:point(from.node),delivery:point(to.node)});
      this.city.setRoutes(active.routes,active.selected);
    }
    const pose=this.book.riderPose;this.city.setRider(pose.point,pose.angle);
    if(camera)this.city.restoreView(camera);else if(active?.mode==='routes')this.city.focusRoute();else this.city.locate(true);
    if(this.damageNoticeSeconds>0)this.renderDamageNotice();
    if(!this.gameplayFrozen&&wasDialog==='receipt'&&!this.modal)this.openReceipt();
    if(wasGallery&&!this.gameplayFrozen)this.openGarage();
    if(wasDialog==='maps'&&!this.modal)this.openMaps();
    if(wasDialog==='bills'&&!this.modal)this.openBills();
    this.renderPanel();const nextScroll=this.panel.getChildByName('DeliverySheet')?.getChildByName('SheetContent')?.getChildByName('ScrollableContent')?.getComponent(ScrollView);if(nextScroll&&scrollY)nextScroll.scrollToOffset(new Vec2(0,scrollY),0);if(wasPhone&&!this.gameplayFrozen)this.openPhone();
    if(this.gameplayFrozen){this.city.cancelLocate();this.openPauseDialog();if(wasGallery)this.openGarage();}
    if(wasNotice)this.showMessage(wasNotice);
  }
  private outerMargin(){return pageMargin(1280+this.screenExtra);}
  private metrics(){return presentationMetrics(1280+this.screenExtra);}
  // OrderPanel already applies -screenExtra/2 and the bottom safe inset.
  // Focused orders have no navigation or central-button clearance to reserve.
  private sheetBottomFor(screenHeight:number):number{return this.book.active?-640-this.safeInsets.bottom:-479.4+pageMargin(screenHeight);}
  private sheetBottom():number{return this.sheetBottomFor(1280+this.screenExtra);}
  private compactData():CompactOrder|null {
    const active=this.book?.active;if(!active)return null;const r=active.routes[active.selected];
    return {offer:active.offer,from:this.book.data.pois[active.offer.from].name,to:this.book.data.pois[active.offer.to].name,metres:r.metres};
  }
  private sheetHeightFor(screenHeight:number):number {
    const data=this.compactData();if(!data)return 440;const m=presentationMetrics(screenHeight),width=720-this.safeInsets.left-this.safeInsets.right-2*pageMargin(screenHeight);
    const body=compactOrderHeight(data,width,screenHeight),route=this.book.active?.mode==='routes'?Math.ceil(m.aux*4.5)+16:60;
    const extra=this.safeInsets.bottom+cssUnits(24,screenHeight)-16;
    return Math.max(440,Math.min(690,body+route+m.action+146))+extra;
  }
  private sheetHeight():number{return this.sheetHeightFor(1280+this.screenExtra);}
  private action(parent:Node,text:string,x:number,y:number,width:number,action:()=>void,fill=C.primary,enabled=true):Node {
    const m=this.metrics(),node=box(parent,'Button-'+text,x,y,width,m.action,fill,16,fill===C.paper?C.line:undefined);
    if(enabled&&(fill===C.primary||fill===C.light))skin(node,fill===C.primary?'button-yellow':'button-blue');
    if(!enabled)material(node,width,m.action,'#C5CCD5');
    const white=enabled&&(fill===C.light||fill==='#DE4258'),caption=readable(node,text,0,0,m.body,white?'#FFFFFF':enabled?C.ink:C.muted,width-20,true,'center',m.action-8);
    if(white)outline(caption);if(enabled)tap(node,action);return node;
  }
  private header(parent:Node):void {
    const width=720-this.safeInsets.left-this.safeInsets.right-2*this.outerMargin(),m=this.metrics();
    this.profileCard=item(parent,'Header',0,0,width,160);
    const content=item(this.profileCard,'HeaderContent');
    const identity=item(content,'ProfileIdentity'),wallet=item(content,'ProfileWallet'),rating=item(content,'ProfileRating');
    
    box(identity,'ExperienceTrack',0,0,1,1,C.line,10);
    box(identity,'ExperienceFill',0,0,1,1,C.primary,10);
    {
      const pause=box(identity,'Button-暂停',0,0,Math.max(112,cssUnits(44,1280+this.screenExtra)),m.action,C.light,12);
      pause.setScale(.5,.5,1);
      const symbol=item(pause,'PauseSymbol');const ink=symbol.addComponent(Graphics);ink.fillColor=col('#FFFFFF');
      for(const x of [-13,5]){ink.roundRect(x,-18,8,36,2);ink.fill();}
      // Small control uses clear native bars; AU05 pause remains available in inventory.
      pause.active=this.canPauseDelivery;
      // Small independent hit target: the rendered frame remains exactly half size.
      const hit=item(pause,'PauseHitTarget',0,0,Math.max(112,2*cssUnits(32,1280+this.screenExtra)),Math.max(m.action,2*cssUnits(32,1280+this.screenExtra)));
      tap(hit,()=>this.pauseGame());
    }
    const avatar=item(identity,'PlayerAvatar',0,0,104,104);
    tap(avatar,()=>{if(!this.modal&&!this.gameplayFrozen)this.openProfile();});
    const face=box(avatar,'AvatarPlaceholder',-10,0,84,90,C.light,17);
    readable(face,'骑',0,0,40,C.muted,80,true,'center',80);
    const avatarArt=cartoonArt(avatar,'avatar',0,0,92,92,face);const alignAvatar=()=>{if(this.money)this.layoutPlayerHeader();};avatarArt.on(Node.EventType.SIZE_CHANGED,alignAvatar);avatarArt.on(Node.EventType.ACTIVE_CHANGED,alignAvatar);
    
    this.experience=readable(identity,'',0,0,m.aux,C.ink,200,true);
    for(const [group,name,mark,art] of [[wallet,'Wallet','¥','coin'],[rating,'Rating','评','heart']] as const){
      box(group,name+'Pill',0,0,1,1,C.light,24,C.line);
      const badge=item(group,name+'Badge',0,0,42,42);
      const symbol=readable(badge,mark,0,0,m.aux,C.ink,38,true,'center',40);
      if(art==='heart'){symbol.node.active=false;const heart=icon(badge,'heart',0,0,C.ink,.8);cartoonArt(badge,'heart',0,0,40,40,heart);}else cartoonArt(badge,art,0,0,40,40,symbol.node);
    }
    this.money=readable(wallet,'',0,0,m.amount,C.ink,160,true,'center');
    this.rating=readable(rating,'',0,0,m.body,C.ink,100,true,'center');
    this.updatePlayerHeader();
  }
  private layoutPlayerHeader():void {
    const card=this.profileCard,m=this.metrics(),margin=this.outerMargin(),width=720-this.safeInsets.left-this.safeInsets.right-2*margin;
    const content=card.getChildByName('HeaderContent')!,identity=content.getChildByName('ProfileIdentity')!,wallet=content.getChildByName('ProfileWallet')!,rating=content.getChildByName('ProfileRating')!;
    const place=(n:Node,x:number,y:number,w:number,h:number)=>{n.setPosition(x,y);n.getComponent(UITransform)!.setContentSize(w,h);};
    const paint=(n:Node,x:number,y:number,w:number,h:number,fill:string,radius:number)=>{place(n,x,y,w,h);paintBox(n,w,h,fill,radius,C.line);};
    const avatar=identity.getChildByName('PlayerAvatar')!,art=avatar.getChildByName('CartoonArt-avatar')!,fallback=avatar.getChildByName('AvatarPlaceholder')!;
    const avatarWidth=art.active?art.getComponent(UITransform)!.width:84,avatarHeight=art.active?92:90;
    place(identity,-width/2+avatarWidth/2,44,avatarWidth,avatarHeight+40);place(avatar,0,0,avatarWidth,avatarHeight);art.setPosition(0,0);fallback.setPosition(0,0);
    // Original PNG contains ~2 design pixels of transparent left edge.
    if(art.active)art.setPosition(-2,0);
    const barY=-avatarHeight/2-22,progress=experienceProgress(this.book.player.experience).progress;
    paint(identity.getChildByName('ExperienceTrack')!,0,barY,avatarWidth,32,C.light,10);
    const fill=identity.getChildByName('ExperienceFill')!;fill.active=progress>0;paint(fill,-avatarWidth*(1-progress)/2,barY,Math.max(0,avatarWidth*progress),32,C.primary,10);
    this.experience.fontSize=28;this.experience.lineHeight=28;place(this.experience.node,0,barY,avatarWidth,32);this.experience.horizontalAlign=Label.HorizontalAlign.CENTER;this.experience.enableWrapText=false;this.experience.overflow=Label.Overflow.SHRINK;
    const pause=identity.getChildByName('Button-暂停');if(pause){pause.active=this.canPauseDelivery;place(pause,-avatarWidth/2+Math.max(112,cssUnits(44,1280+this.screenExtra))/4,barY-16-12-Math.max(m.action/2,cssUnits(32,1280+this.screenExtra))/2,Math.max(112,cssUnits(44,1280+this.screenExtra)),m.action);}
    const font=Math.max(24,Math.ceil(m.body*.8)),iconSize=40,pad=14,gap=12,available=width-avatarWidth-18;
    const wanted=(v:string)=>Math.ceil(Array.from(v).length*font*.66)+iconSize+pad*3;
    const ratingWidth=wanted(this.rating.string),moneyWidth=Math.min(available,wanted(this.money.string));
    const stacked=moneyWidth+ratingWidth+gap>available;
    const layout=(group:Node,name:string,value:Label,w:number,y:number)=>{
      const textWidth=w-iconSize-pad*3,lines=Math.max(1,Math.ceil(Array.from(value.string).length*font*.66/textWidth)),height=Math.max(64,lines*Math.ceil(font*1.42)+16);
      place(group,width/2-w/2,y,w,height);paint(group.getChildByName(name+'Pill')!,0,0,w,height,C.light,26);
      group.getChildByName(name+'Badge')!.setPosition(-w/2+pad+iconSize/2,0);
      value.fontSize=font;value.lineHeight=Math.ceil(font*1.42);place(value.node,(iconSize+pad)/2,0,textWidth,height-12);return height;
    };
    const mh=layout(wallet,'Wallet',this.money,moneyWidth,44);
    if(stacked)layout(rating,'Rating',this.rating,ratingWidth,-mh/2);else {layout(rating,'Rating',this.rating,ratingWidth,44);wallet.setPosition(width/2-ratingWidth-gap-moneyWidth/2,44);}
    const headerY=640-margin-44-avatarHeight/2;
    place(card,(this.safeInsets.left-this.safeInsets.right)/2,headerY,width,180);
    // Reserve the actual lower edge of the header/pause in map-local coordinates.
    const pauseY=pause?.position.y??barY;
    const lower=headerY+44+(this.canPauseDelivery?pauseY-m.action/4:barY-16)+this.screenExtra/2-this.safeInsets.top;
    this.city.setHeaderClearance((this.city.viewport.position.y+this.city.viewport.getComponent(UITransform)!.height/2)-lower+margin);
    const station=this.root.getChildByName('StationEntry');if(station)this.positionStation(station);
  }
  private positionStation(station:Node):void {
    const art=station.getChildByName('CartoonArt-station'),half=Math.max(47,art?.active?(art.getComponent(UITransform)?.width||108)/2:0);
    const base=this.book.mode==='idle'||!this.orderCardOpen?-390:this.sheetBottom()+this.sheetHeight()+110;
    station.setPosition(-360+this.safeInsets.left+this.outerMargin()+half,base-this.screenExtra/2+this.safeInsets.bottom);
  }

  private controls():void {
    const station=item(this.root,'StationEntry',296-this.safeInsets.right,628-this.profileCard.getComponent(UITransform)!.height-70+this.screenExtra/2-this.safeInsets.top,100,100);
    const picture=box(station,'PlaceholderIcon-station',0,11,36,32,'#F0EEE7',8);
    label(picture,'站',0,0,20,'#AAA69C',32,true,'center');const stationArt=cartoonArt(station,'station',0,11,86.4,86.4,picture);stationArt.getComponent(Sprite)!.grayscale=true;
    readable(station,'站点',0,-52,this.metrics().aux,'#AAA69C',94,true,'center');
    const y=this.book.mode==='idle'||!this.orderCardOpen?-400:this.sheetBottom()+this.sheetHeight()+this.metrics().action/2+20;
    const locateSize=Math.max(this.metrics().action,116);const locate=item(this.root,'FollowRider',0,0,locateSize,locateSize);
    const locateArt=icon(locate,'target',0,0,C.ink,86.4/48);tap(locate,()=>this.city.locateAnimated());
    const position=()=>{
      if(!station.isValid||!locate.isValid)return;this.positionStation(station);
      const stationHeight=stationArt.active?stationArt.getComponent(UITransform)!.height:32;
      const targetHeight=locateArt.active?locateArt.getComponent(UITransform)!.height:86.4;
      const stationY=stationArt.active?11:picture.position.y;
      locate.setPosition(360-this.safeInsets.right-locateSize/2-this.outerMargin(),station.position.y+stationY-stationHeight/2+targetHeight/2);
    };
    stationArt.on(Node.EventType.SIZE_CHANGED,position);stationArt.on(Node.EventType.ACTIVE_CHANGED,position);
    locateArt.on(Node.EventType.SIZE_CHANGED,position);locateArt.on(Node.EventType.ACTIVE_CHANGED,position);position();
    const statusHeight=this.metrics().action*.65,statusWidth=cssUnits(94,1280+this.screenExtra);
    const statusY=this.profileCard.position.y+this.screenExtra/2-this.safeInsets.top-90-this.outerMargin()-statusHeight/2;
    this.deliveryStatus=box(this.root,'DeliveryStatus',0,statusY,statusWidth,statusHeight,'#FFFCF5',12);
    readable(this.deliveryStatus,'配送中',0,0,this.metrics().aux,'#111111',statusWidth-12,true,'center',statusHeight);
    this.deliveryStatus.active=this.book.active?.handoff?.phase==='toDropoff';
    if(this.book.active&&this.book.mode!=='done'){
      const buttonWidth=Math.max(cssUnits(64,1280+this.screenExtra),110),x=360-this.safeInsets.right-this.outerMargin()-buttonWidth/2;
      const vehicleEntry=this.action(this.root,'车辆',x,locate.position.y+locateSize/2+this.metrics().action/2+this.outerMargin(),buttonWidth,()=>this.openGarage(),C.light);
      vehicleEntry.name='ActiveVehicleEntry';
    }
    const planning=this.book.mode==='routes'&&this.orderCardOpen;station.active=!planning;locate.active=!planning;this.city.setPlanningControlsHidden?.(planning);
    const viewportBottom=this.city.viewport.position.y-this.city.viewport.getComponent(UITransform)!.height/2;
    const controlTop=Math.max(station.position.y+65,locate.position.y+locateSize/2,y-this.screenExtra/2+this.safeInsets.bottom+this.metrics().action/2);
    this.city.setLowerClearance(planning?this.outerMargin():controlTop-viewportBottom+this.outerMargin());
  }
  private get canBoost():boolean {
    const active=this.book?.active,phase=active?.handoff?.phase;
    return !!active&&isTripProfile(active.tripProfile)&&active.mode==='running'&&
      (phase==='toPickup'||phase==='toDropoff')&&!this.hidden&&!this.gameplayFrozen&&!this.pendingSave&&this.writerLease.writable;
  }
  private refreshBoost():void {
    if(!this.canBoost)this.clickBoost.reset();
    const strength=this.canBoost?Math.max(0,Math.min(1,(this.clickBoost.multiplier-1)/(ClickBoost.MAX-1))):0;
    this.city?.setSpeedEffect(strength);
    if(this.deliveryStatus?.isValid)this.deliveryStatus.active=this.book.active?.handoff?.phase==='toDropoff'&&this.book.mode==='running';
    if(this.boostControl?.isValid)this.boostControl.active=this.canBoost;
    if(this.boostLabel?.isValid)this.boostLabel.string='点击加速';
  }
  private createBoostControl(parent:Node,buttonX:number,buttonY:number,width:number):void {
    const height=this.metrics().action;
    const control=box(parent,'ClickBoost',buttonX,buttonY,width,height,C.primary,16);
    this.boostControl=control;this.boostLabel=readable(control,'点击加速',0,0,this.metrics().aux,C.ink,width-16,true,'center');
    control.addComponent(BlockInputEvents);
    const caption=this.boostLabel.node;
    const release=()=>{if(caption.isValid)caption.setScale(1,1,1);};
    let id:number|null=null,x=0,z=0,cancelled=false;
    const multi=(e:EventTouch)=>{if(e.getAllTouches().length>1){cancelled=true;release();}};
    input.on(Input.EventType.TOUCH_START,multi);
    control.on(Node.EventType.NODE_DESTROYED,()=>input.off(Input.EventType.TOUCH_START,multi));
    control.on(Node.EventType.ACTIVE_IN_HIERARCHY_CHANGED,()=>{id=null;cancelled=true;release();});
    control.on(Node.EventType.TOUCH_START,(e:EventTouch)=>{
      e.propagationStopped=true;if(!this.canBoost||id!==null||e.getAllTouches().length!==1){cancelled=true;return;}
      id=e.getID();const p=e.getUILocation();x=p.x;z=p.y;cancelled=false;caption.setScale(.96,.96,1);
    });
    const moved=(e:EventTouch)=>{const p=e.getUILocation();return (p.x-x)**2+(p.y-z)**2>49;};
    control.on(Node.EventType.TOUCH_MOVE,(e:EventTouch)=>{e.propagationStopped=true;if(moved(e)||e.getAllTouches().length>1){cancelled=true;release();}});
    control.on(Node.EventType.TOUCH_CANCEL,(e:EventTouch)=>{e.propagationStopped=true;id=null;cancelled=true;release();});
    control.on(Node.EventType.TOUCH_END,(e:EventTouch)=>{
      e.propagationStopped=true;if(id===null||id!==e.getID())return;
      const p=e.getUILocation(),local=control.getComponent(UITransform)!.convertToNodeSpaceAR(new Vec3(p.x,p.y));
      const valid=!cancelled&&!moved(e)&&Math.abs(local.x)<=width/2&&Math.abs(local.y)<=height/2&&e.getAllTouches().length<=1;
      id=null;release();if(valid&&this.canBoost&&this.clickBoost.click(performance.now()/1000))this.sound?.play('boost',true);
    });
    this.refreshBoost();
  }
  private openPhone():void {
    if(this.gameplayFrozen||this.phone||this.book.mode!=='idle')return;
    this.phone=new OrderPhone(this.root,this.book,1280+this.screenExtra,id=>this.accept(id),()=>this.closePhone(),()=>{
      if(!this.act(()=>this.book.refreshFree()))return;
      this.closePhone();this.openPhone();
    },this.safeInsets);
  }
  private closePhone():void{if(this.phone)this.phone.close();this.phone=null;}
  private navigation():void {
    if(this.book.active||this.pendingSave)return;
    const idle=this.book.mode==='idle';
    const backdrop=item(this.panel,'NavigationBackdrop',0,-581-this.safeInsets.bottom/2,720,118+this.safeInsets.bottom);topOnlyBar(backdrop,720,118+this.safeInsets.bottom);
    const width=720-this.safeInsets.left-this.safeInsets.right-2*this.outerMargin(),slotWidth=width/5;
    const bar=item(this.panel,'MainNavigation',(this.safeInsets.left-this.safeInsets.right)/2,-581,width,118);bar.addComponent(BlockInputEvents);
    const entries=[
      {key:'recruit',name:'招募',enabled:false,action:()=>{}},
      {key:'vehicle',name:'车辆',enabled:true,action:()=>this.openGarage()},
      {key:'orders',name:idle?'抢单':'订单',enabled:true,action:()=>this.openCurrentOrder()},
      {key:'map',name:'地图',enabled:true,action:()=>this.openMaps()},
      {key:'bills',name:'账单',enabled:true,action:()=>this.openBills()},
    ];
    const sideScale=Math.min(1.725*1.125,Math.max(0,(slotWidth-8)/48));
    const sideNodes:Array<{slot:Node;picture:Node;caption:Node}>=[];
    entries.forEach((entry,index)=>{
      const main=entry.key==='orders',enabled=entry.enabled,foreground=enabled?C.ink:'#AAA69C';
      const slot=item(bar,'Nav-'+entry.key,0,main?28.8:0,main?145.6:slotWidth,main?145.6:100);
      if(main){roundAction(slot,145.6,enabled);cartoonArt(slot,'main-action-glossy',0,0,145.6,145.6,slot.getChildByName('Surface')!);}
      const picture=main?null:icon(slot,entry.key,0,55,foreground,sideScale);if(picture)picture.setScale(.9,.9,1);
      const caption=readable(slot,entry.name,0,main?0:-23,main?57.2:this.metrics().aux,main?'#FFFFFF':foreground,main?132:Math.min(108,slotWidth-8),true,'center',main?62.4:48);outline(caption,enabled?(main?'#831831':C.navy):'#6F747D',3);
      if(picture)sideNodes.push({slot,picture,caption:caption.node});
      if(enabled)tap(slot,entry.action);
    });
    const spread=()=>{
      if(!bar.isValid)return;
      for(const {picture,caption} of sideNodes){const height=picture.active?(picture.getComponent(UITransform)?.height||48*sideScale):48*sideScale;caption.setPosition(0,picture.position.y-height*.9/2-cssUnits(2,1280+this.screenExtra)-caption.getComponent(UITransform)!.height/2);}
      const frame=(i:number)=>{const picture=sideNodes[i].picture;return picture.active?(picture.getComponent(UITransform)?.width||48*sideScale):48*sideScale;};
      for(const [outer,inner,sign] of [[0,1,-1],[3,2,1]] as const){
        const ow=frame(outer),iw=frame(inner),radius=145.6/2;
        const space=Math.max(0,width/2-radius-ow-iw),gap=Math.min(cssUnits(24,1280+this.screenExtra),space/2);
        const outerX=width/2-ow/2,innerX=radius+gap+iw/2;
        sideNodes[outer].slot.setPosition(sign*outerX,0);sideNodes[inner].slot.setPosition(sign*innerX,0);
        const midpoint=(outerX+innerX)/2;
        const outerHit=Math.max(1,2*Math.min(width/2-outerX,outerX-midpoint));
        const innerHit=Math.max(1,2*Math.min(innerX-radius,midpoint-innerX));
        sideNodes[outer].slot.getComponent(UITransform)!.setContentSize(outerHit,100);
        sideNodes[inner].slot.getComponent(UITransform)!.setContentSize(innerHit,100);
      }
    };
    for(const {picture} of sideNodes){picture.on(Node.EventType.SIZE_CHANGED,spread);picture.on(Node.EventType.ACTIVE_CHANGED,spread);}spread();
  }

  private accept(id:string):void {
    if(!this.act(()=>{this.book.accept(id);this.lastHandoffEvent='';}))return;this.closePhone();
    this.orderCardOpen=true;this.rebuildLayout(true);
  }
  private openCurrentOrder():void {
    if(!this.book.active){this.openPhone();return;}
    this.orderCardOpen=true;this.rebuildLayout();
    if(this.book.mode==='done')this.openReceipt();else if(this.book.mode==='arrived'&&this.act(()=>this.book.settle(this.book.active?.offer.demand==='door'?true:null))){this.renderPanel();this.openReceipt();}
  }
  private renderPanel():void {
    for(const child of [...this.panel.children])child.destroy();this.panel.removeAllChildren();
    this.timer=null;this.tripLabel=null;this.progressFill=null;this.pickupServiceButton=null;
    this.updatePlayerHeader();
    this.navigation();
    const active=this.book.active;
    // Keep receipt data in the book, but never construct a completed-order sheet.
    if(active?.mode==='done'){
      if(!this.gameplayFrozen&&!this.pendingSave&&!this.modal&&this.receipts.observe(active))this.openReceipt();
      return;
    }
    if(!active||!this.orderCardOpen)return;
    const height=this.sheetHeight(),inner=720-this.safeInsets.left-this.safeInsets.right-2*this.outerMargin(),m=this.metrics();
    const sheet=item(this.panel,'DeliverySheet',0,this.sheetBottom()+height/2,720,height),surface=item(sheet,'Surface'),ink=surface.addComponent(Graphics);
    ink.fillColor=col(C.paper);ink.roundRect(-360,-height/2,720,height,18);ink.fill();ink.rect(-360,-height/2,720,18);ink.fill();
    const p=item(sheet,'SheetContent',(this.safeInsets.left-this.safeInsets.right)/2,0,inner,height);
    const top=height/2;
    const offer=active.offer,route=active.routes[active.selected],timing=this.book.timingForRoute(route),receipt=active.receipt,phase=active.handoff?.phase;
    const title=readable(p,(offer.source==='transfer'?'转单 · ':'')+deadlineText(active.deadlineSeconds)+(offer.type==='urgent'?' · 加急':''),-36,top-40,m.body,C.ink,inner-90,true,'left',64);

    const planning=active.mode==='routes',footer=this.safeInsets.bottom+cssUnits(24,1280+this.screenExtra)+m.action+16,info=this.compactData()!,infoHeight=compactOrderHeight(info,inner,1280+this.screenExtra);
    const routeHeight=Math.ceil(m.aux*4.5)+16,detailsHeight=infoHeight+(planning?routeHeight+28:70);
    const content=scrollContent(p,inner,top-84,-top+footer,detailsHeight);content.name='OrderDetails';
    const infoNode=item(content,'CompactOrderInfo',0,0,inner,infoHeight);compactOrderInfo(infoNode,info,inner,1280+this.screenExtra);
    if(planning){
      const gap=8,count=active.routes.length,w=(inner-gap*(count-1))/count,y=-infoHeight-12-routeHeight/2;
      active.routes.forEach((r,i)=>{
        const selected=i===active.selected,color=ROUTE_COLORS[r.preference],x=-inner/2+w/2+i*(w+gap);
        const card=box(content,'Route-'+r.preference,x,y,w,routeHeight,selected?'#F8E5CD':'#F7F5EF',12,selected?color:C.line);
        const estimated=this.book.timingForRoute(r).displaySeconds,late=estimated>active.deadlineSeconds;
        readable(card,(selected?'✓ ':'')+TITLES[r.preference],0,routeHeight/2-26,m.aux,color,w-12,true,'center',44);
        readable(card,`${Math.ceil(estimated/60)}分 ${(r.metres/1000).toFixed(1)}km`,0,0,m.aux,C.ink,w-12,true,'center',48);
        readable(card,`${late?'晚到':'准时'} 餐损${Math.round(r.risk*100)}%`,0,-routeHeight/2+28,m.aux,late?'#B76A3A':C.muted,w-12,false,'center',48);
        tap(card,()=>{if(!this.act(()=>this.book.select(i)))return;this.city.setRoutes(active.routes,i,true);this.renderPanel();});
      });
    }else if(active.mode==='running'){
      this.tripLabel=readable(content,'',0,-infoHeight-30,m.body,C.ink,inner,true,'left',60);this.updateProgress();
    }
    const allowCancel=phase?['planning','toPickup','awaitPickup'].indexOf(phase)>=0:(active.mode==='routes'||active.mode==='running'&&this.book.tripStage==='pickup'),buttonY=-top+this.safeInsets.bottom+cssUnits(24,1280+this.screenExtra)+m.action/2,cancelWidth=Math.max(144,cssUnits(44,1280+this.screenExtra),m.body*4+24);
    if(allowCancel)this.action(p,'取消订单',-inner/2+cancelWidth/2,buttonY,cancelWidth,()=>{if(!this.act(()=>this.book.cancel()))return;this.rebuildLayout(true);},'#DE4258');
    const mainWidth=allowCancel?inner-cancelWidth-12:inner,mainX=allowCancel?(cancelWidth+12)/2:0;
    if(active.mode==='routes')this.action(p,'去取餐',mainX,buttonY,mainWidth,()=>{if(!this.act(()=>this.book.depart()))return;this.rebuildLayout();this.city.locate(true);this.presentHandoff();});
    else if(phase==='awaitPickup')this.action(p,'取餐',mainX,buttonY,mainWidth,()=>{if(!this.act(()=>this.book.pickup()))return;this.renderPanel();});
    else if(phase==='awaitDeliveryStart')this.action(p,'去配送',mainX,buttonY,mainWidth,()=>{if(!this.act(()=>this.book.deliver()))return;this.renderPanel();},C.primary,!this.pendingSave);
    else if(phase==='picking'){
      this.pickupServiceButton=this.action(p,'取餐中',mainX,buttonY,mainWidth,()=>{},C.light,false);
      const fill=item(this.pickupServiceButton,'PickupServiceFill');fill.addComponent(Graphics);fill.setSiblingIndex(1);
      const caption=this.pickupServiceButton.getComponentInChildren(Label);if(caption)caption.color=col(C.ink);
      this.updatePickupServiceFill();
    }
    else if(active.mode==='running'){if(isTripProfile(active.tripProfile)&&(phase==='toPickup'||phase==='toDropoff'))this.createBoostControl(p,mainX,buttonY,mainWidth);else this.action(p,phase==='toPickup'?'前往取餐中':'配送中',mainX,buttonY,mainWidth,()=>{},C.light,false);}
  }
  private presentHandoff():void {
    if(this.pendingSave||this.gameplayFrozen)return;
    const active=this.book.active,phase=active?.handoff?.phase||(active?.mode==='done'?'arrived':undefined);if(!active||!phase||['awaitPickup','awaitDeliveryStart','arrived'].indexOf(phase)<0)return;
    const key=active.offer.id+'/'+phase;if(key===this.lastHandoffEvent)return;this.lastHandoffEvent=key;
    this.closeDialog();this.closePhone();this.orderCardOpen=true;this.rebuildLayout();
    if(phase==='arrived'&&this.book.mode==='done'&&this.modalKind!=='receipt')this.openReceipt();else this.city.locate(true);
  }

  update(dt:number):void {
    if(!this.book||this.hidden||!this.writerLease.writable){this.clickBoost.reset();this.city?.setSpeedEffect(0);return;}
    this.refreshBoost();
    dt=this.foregroundClock.frame();
    if(!this.gameplayFrozen)this.city.advanceLocate(dt);

    if(this.skipNextFrame){this.skipNextFrame=false;this.clickBoost.reset();return;}
    if(this.pendingSave){this.saveElapsed+=dt;if(this.saveElapsed>=1){this.saveElapsed=0;if(this.save()){if(this.cancellationPendingReturn){this.finishCancelledDelivery();return;}this.onlineAt=this.gameplayFrozen?null:Date.now();if(this.phone&&this.book.active)this.closePhone();this.rebuildLayout(!this.book.active);if(this.receiptReturn!==null){const open=this.receiptReturn;this.receiptReturn=null;if(open)this.openPhone();}if(!this.gameplayFrozen)this.presentHandoff();}}return;}
    if(this.gameplayFrozen){this.foregroundClock.reset();this.onlineAt=null;return;}
    const now=Date.now();if(this.onlineAt!==null)this.book.recordOnlineTime(this.onlineAt,now);this.onlineAt=now;
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
    const beforePhase=this.book.active?.handoff?.phase, beforeMode=this.book.mode;
    const endMs=now,startMs=endMs-dt*1000;let cursor=startMs,arrived=false;
    while(cursor<endMs){const d=new Date(cursor),midnight=new Date(d.getFullYear(),d.getMonth(),d.getDate()+1).getTime(),end=Math.min(endMs,midnight>cursor?midnight:endMs);
      const seconds=(end-cursor)/1000,integrated=this.canBoost?this.clickBoost.integrate(seconds,this.foregroundClock.time-(endMs-end)/1000):seconds;
      arrived=this.book.advance(seconds,seconds>0?Math.min(ClickBoost.MAX,Math.max(1,integrated/seconds)):1,localBillingDay(d));cursor=end;if(arrived)break;}
    const pose=this.book.riderPose;
    if(arrived)this.clickBoost.reset();this.refreshBoost();
    this.city.setRider(pose.point,pose.angle);this.updateProgress();
    const damaged=this.book.takeDamageNotice();
    if(damaged){this.damageNoticeSeconds=2;this.renderDamageNotice();}
    const afterPhase=this.book.active?.handoff?.phase;
    if(beforePhase==='toPickup'&&afterPhase==='awaitPickup')this.pendingSound='shop';
    if(beforePhase==='picking'&&afterPhase==='awaitDeliveryStart')this.pendingSound='pickup';
    if(beforeMode==='running'&&this.book.mode==='done')this.pendingSound='success';
    if(arrived||damaged||this.saveElapsed>=.5){this.saveElapsed=0;this.save();}
    if(arrived&&!this.pendingSave){this.renderPanel();this.presentHandoff();}
  }
  private act(action:()=>void):boolean {
    if(!this.writerLease.writable){this.showMessage('当前页面只读，请关闭其他游戏页后重新打开。');return false;}
    if(this.gameplayFrozen||this.pendingSave)return false;
    try{
      const before=this.book.active?.handoff?.phase;action();
      if(before!==this.book.active?.handoff?.phase){this.clickBoost.reset();this.foregroundClock.reset();}
      return this.save();
    }
    catch(error){this.showMessage(error instanceof Error?error.message:'操作未完成，请重试');return false;}
  }
  private save():boolean {
    if(!this.book||!this.store)return false;
    if(this.book.mode==='done')this.removeDeliverySheet();
    const ok=this.store.save(this.book.serialize());
    if(!ok&&this.lastSaveError!==this.store.message){this.lastSaveError=this.store.message;this.showMessage(this.store.message);}
    this.pendingSave=!ok;if(!ok&&this.gallery&&!this.gallery.getChildByName('SavePendingBlock')){const block=box(this.gallery,'SavePendingBlock',0,0,720,1280+this.screenExtra,'#00000066',0);block.addComponent(BlockInputEvents);readable(block,'保存失败，正在重试；请勿关闭页面',0,0,this.metrics().body,'#FFFFFF',620,true,'center',100);if(this.modal)this.modal.active=false;}if(ok&&this.pendingSound){const event=this.pendingSound;this.pendingSound=null;this.sound?.play(event,!this.hidden&&!this.gameplayFrozen);}this.refreshBoost();if(ok&&this.lastSaveError){this.lastSaveError='';if(this.toast){this.toast.destroy();this.toast=null;this.noticeMessage='';}}this.updatePlayerHeader();this.updateBills();if(this.book.mode==='done'&&!this.layoutDone)this.rebuildLayout();return ok;
  }
  private updatePlayerHeader():void {
    if(!this.money)return;const p=this.book.player;
    this.city.setVehicle(p.vehicleTier);
    this.money.string=(p.cashCents/100).toFixed(2);
    this.rating.string=String(p.rating);
    const xp=experienceProgress(p.experience);
    this.experience.string=`Lv.${p.level}`;
    this.layoutPlayerHeader();
  }
  private showMessage(message:string):void {
    if(!this.root)return;if(this.toast){this.toast.active=false;this.toast.destroy();}
    this.noticeMessage=message;
    if(this.gameplayFrozen)return;
    const m=this.metrics(),width=720-this.safeInsets.left-this.safeInsets.right-2*this.outerMargin(),height=textHeight(message,m.body,width-32)+24;
    const node=this.toast=box(this.root,'NoticeToast',(this.safeInsets.left-this.safeInsets.right)/2,-230-this.screenExtra/2,width,height,'#FFF0D9',16,'#D6B65A');
    readable(node,message,0,0,m.body,C.ink,width-32,true,'center',height-16);
    this.scheduleOnce(()=>{if(this.pendingSave)return;if(node.isValid)node.destroy();if(this.toast===node){this.toast=null;this.noticeMessage='';}},4);
  }
  private get canPauseDelivery():boolean {return !!this.book?.canCancelDelivery;}
  private pauseGame():void {
    if(!this.canPauseDelivery||this.gameplayFrozen)return;
    if(!this.pendingSave&&this.writerLease.writable&&this.onlineAt!==null&&!this.hidden)this.book.recordOnlineTime(this.onlineAt,Date.now());
    this.sound?.stop();this.pendingSound=null;this.clickBoost.reset();this.paused=true;this.onlineAt=null;this.foregroundClock.reset();this.city.cancelLocate();
    this.closePhone();if(!this.pendingSave)this.save();this.openPauseDialog();
  }
  private openPauseDialog():void {
    if(!this.gameplayFrozen)return;
    const m=this.metrics(),entry=this.entryGate;
    const message=this.pendingSave?(this.store.message||'进度保存待重试，请检查存储权限后重试。'):(entry?'当前配送已保留，点击继续游戏恢复。':'行驶、取餐服务与在线统计已暂停。取消配送将结束本单，不发收益或经验，不扣钱或评价。');
    const requested=textHeight(message,m.aux,580)+m.action*(entry?2:3)+236;
    const {card,width,height,top,bottom}=this.dialog(entry?'继续配送':'游戏已暂停',requested,entry?'entry':'pause',false),inner=width-48;
    const buttonCount=entry?2:3,content=scrollContent(card,inner,top,bottom+buttonCount*(m.action+12)+8,textHeight(message,m.aux,inner)+16);
    readable(content,message,0,-textHeight(message,m.aux,inner)/2,m.aux,C.ink,inner,false,'center');
    const firstY=-height/2+24+m.action/2+(entry?1:2)*(m.action+12);
    this.action(card,'继续游戏',0,firstY,inner,()=>this.resumeGame(),C.primary,!this.cancellationPendingReturn);
    if(!entry)this.action(card,'取消配送',0,-height/2+24+m.action*1.5+12,inner,()=>this.cancelDelivery(),C.light);
    this.action(card,'查看车辆',0,top-30,150,()=>this.openGarage(),C.light);
    this.action(card,this.sound?.isMuted?'音效：关闭':'音效：开启',0,-height/2+24+m.action/2,inner,()=>{this.sound?.toggle();this.openPauseDialog();},C.light);
  }
  private resumeGame():void {
    if(!this.gameplayFrozen)return;
    if(this.cancellationPendingReturn){this.cancelDelivery();return;}
    // Retry the exact frozen snapshot before permitting any new gameplay command.
    if(!this.save()){this.openPauseDialog();return;}
    this.paused=false;this.entryGate=false;this.closeDialog();
    this.clickBoost.reset();this.foregroundClock.reset();this.skipNextFrame=true;this.onlineAt=this.hidden?null:Date.now();
    if(this.book.mode==='arrived'&&!this.act(()=>this.book.settle(this.book.active?.offer.demand==='door'?true:null))){this.rebuildLayout();return;}
    this.rebuildLayout();if(this.book.mode==='done')this.openReceipt();else this.presentHandoff();
  }
  private cancelDelivery():void {
    if(!this.paused||!this.writerLease.writable)return;
    if(!this.cancellationPendingReturn){
      // A pre-existing failed submit must finish before creating another command.
      if(this.pendingSave&&!this.save()){this.openPauseDialog();return;}
      try{this.book.cancelDelivery();this.cancellationPendingReturn=true;}
      catch(error){this.noticeMessage=error instanceof Error?error.message:'取消未完成';this.openPauseDialog();return;}
    }
    if(!this.save()){this.openPauseDialog();return;}
    this.finishCancelledDelivery();
  }
  private finishCancelledDelivery():void {
    this.cancellationPendingReturn=false;this.paused=false;this.entryGate=false;
    this.lastHandoffEvent='';this.closeDialog();this.closePhone();
    this.clickBoost.reset();this.foregroundClock.reset();this.skipNextFrame=true;this.onlineAt=this.hidden?null:Date.now();
    this.rebuildLayout(true);
  }
  private dismissDialog():void {
    if(this.gallery&&this.modalKind==='garage'&&!this.pendingSave){this.closeDialog();return;}
    if(this.gameplayFrozen)return;
    if(this.modalKind==='receipt'){this.finishReceipt(false);return;}
    this.closeDialog();if(this.book?.mode==='arrived'&&this.orderCardOpen)this.renderPanel();
  }
  private closeDialog():void{if(this.modal){this.modal.active=false;this.modal.destroy();this.modal=null;}this.modalKind=null;this.billValues=[];this.billDate=null;}
  private dialog(title:string,requestedHeight:number,kind:DialogKind,dismissible=true):{layer:Node;card:Node;width:number;height:number;top:number;bottom:number} {
    this.closeDialog();this.modalKind=kind;const screenHeight=1280+this.screenExtra,insets=this.safeInsets||{top:0,bottom:0,left:0,right:0};
    const layer=this.modal=item(this.root,'CountyDialog',0,0,720,screenHeight);layer.addComponent(BlockInputEvents);
    const shade=box(layer,'Shade',0,0,720,screenHeight,'#00000099',0);if(dismissible)tap(shade,()=>this.dismissDialog());
    const width=Math.min(684,720-insets.left-insets.right-2*pageMargin(screenHeight)),height=Math.min(requestedHeight,screenHeight-insets.top-insets.bottom-2*pageMargin(screenHeight));
    const card=box(layer,'DialogCard',(insets.left-insets.right)/2,(insets.bottom-insets.top)/2,width,height,C.paper,28);card.addComponent(BlockInputEvents);
    const heading=box(card,'DialogHeader',0,height/2-65,width-12,126,C.violet,26);skin(heading,'panel-violet');
    const m=this.metrics(),headingText=readable(card,title,(kind==='receipt'||kind==='pause'||kind==='entry')?0:-60,height/2-64,m.body+4,'#FFFFFF',width-180,true,(kind==='receipt'||kind==='pause'||kind==='entry')?'center':'left',70);outline(headingText,'#4B329A');
    if(dismissible)closeButton(card,width/2-55,height/2-64,64,()=>this.dismissDialog());
    return {layer,card,width,height,top:height/2-132,bottom:-height/2+24};
  }
  private openDemand():void {
    if(this.book.mode!=='arrived'||this.modalKind==='demand'||this.modalKind)return;
    const {card,width,height,top,bottom}=this.dialog('交付要求',630,'demand',false),m=this.metrics(),inner=width-48;
    const content=scrollContent(card,inner,top,bottom+2*m.action+36,190);
    readable(content,'顾客留言：放门口，别敲门',0,-60,m.body,C.ink,inner,true,'center',110);
    readable(content,'选择期间不消耗配送时间',0,-152,m.aux,C.muted,inner,false,'center',70);
    this.action(card,'敲门交付',0,-height/2+24+m.action*1.5+16,inner,()=>this.deliverAtDoor(false),C.light);
    this.action(card,'按要求放门口',0,-height/2+24+m.action/2,inner,()=>this.deliverAtDoor(true));
  }
  private deliverAtDoor(answer:boolean):void{
    if(this.book.mode!=='arrived')return;
    this.closeDialog();this.act(()=>this.book.settle(answer));
  }
  private renderDamageNotice():void {
    if(this.damageNotice){this.damageNotice.destroy();this.damageNotice=null;}
    const notice=this.damageNotice=box(this.root,'DamageNotice',0,330+this.screenExtra/2,626,88,'#FFF0CF',18,'#DAAB64');
    label(notice,'路程颠簸，餐品损坏了',0,0,25,'#9B592E',590,true,'center');
  }
  private removeDeliverySheet():void {
    const sheet=this.panel?.getChildByName('DeliverySheet');
    if(sheet){sheet.removeFromParent();sheet.destroy();}
    this.timer=null;this.tripLabel=null;this.progressFill=null;this.pickupServiceButton=null;
  }
  private openReceipt():void {
    if(this.book.mode==='done')this.removeDeliverySheet();
    const receipt=this.book.active?.receipt;if(!receipt||this.pendingSave||this.gameplayFrozen)return;
    const m=this.metrics(),inner=Math.min(684,720-this.safeInsets.left-this.safeInsets.right-2*this.outerMargin())-48,offer=this.book.active!.offer;
    const status=[receipt.lateSeconds>0?'晚到':'准时',receipt.damage==='none'?'餐品完好':'餐品损坏',offer.demand==='door'?(receipt.outcome.doorAnswer?'按备注':'未按备注'):'无交付要求'].join(' · ');
    let parts:ReturnType<typeof receiptIncomeBreakdown>=null;try{parts=receiptIncomeBreakdown(offer,receipt);}catch(_){/* Old receipt without sufficient data: show the actual result. */}
    const effect=(label:string,cents:number)=>`${label}影响收益${cents>0?'−':'+'}¥${(Math.abs(cents)/100).toFixed(2)}`;
    const income='¥'+(receipt.incomeCents/100).toFixed(2);
    let incomeSize=m.amount+12;
    const context=typeof document!=='undefined'&&document.createElement?document.createElement('canvas').getContext('2d'):null;
    const incomeWidth=(size:number)=>{if(context){context.font=`bold ${size}px Arial Rounded MT Bold, sans-serif`;return context.measureText(income).width;}return income.length*size*.62;};
    while(incomeSize>1&&incomeWidth(incomeSize)>inner-8)incomeSize--;
    const entries=[{text:'本单收益',size:m.body,bold:true,color:'#A95226'},
      {text:income,size:incomeSize,bold:true,color:'#A95226'},
      {text:status,size:m.body},...(parts&&parts.lateImpact?[{text:effect('晚到',parts.lateImpact),size:m.body}]:[]),
      ...(parts&&parts.damageImpact?[{text:effect('餐损',parts.damageImpact),size:m.body}]:[]),
      {text:`评价 ${receipt.ratingDelta>=0?'+':''}${receipt.ratingDelta} · 经验 +${receipt.experienceGained}`,size:m.body,bold:true}];
    const heights=entries.map(row=>textHeight(row.text,row.size,inner)+12),contentHeight=heights.reduce((a,b)=>a+b,0)+12;
    const {card,height,top,bottom}=this.dialog('配送结算',contentHeight+2*m.action+196,'receipt');
    const content=scrollContent(card,inner,top,bottom+2*m.action+40,contentHeight);
    let offset=0;entries.forEach((row,i)=>{readable(content,row.text,0,-offset-heights[i]/2,row.size,row.color||C.ink,inner,!!row.bold,'center',heights[i]);offset+=heights[i];});
    this.action(card,'继续接单',0,-height/2+24+m.action*1.5+16,inner,()=>this.finishReceipt(true));
    this.action(card,'返回首页',0,-height/2+24+m.action/2,inner,()=>this.finishReceipt(false),C.light);
  }
  private finishReceipt(openOrders:boolean):void {
    if(this.book.mode!=='done'||this.pendingSave||this.gameplayFrozen)return;
    this.receiptReturn=openOrders;
    if(!this.act(()=>this.book.finish())){if(!this.pendingSave)this.receiptReturn=null;return;}
    this.receiptReturn=null;this.closeDialog();this.rebuildLayout();if(openOrders)this.openPhone();
  }
  private openMaps():void {
    const {card,width,top,bottom}=this.dialog('地图',1060,'maps'),m=this.metrics(),inner=width-48;
    const regions=[{name:'县城',requirements:''},{name:'城市',requirements:'100单 · C车 · 招募1名骑手 · 站点2级'},{name:'省会',requirements:'300单 · B车 · C骑手上岗 · 站点3级'},{name:'一线',requirements:'800单 · A车 · A骑手上岗 · 站点4级'},{name:'国际一线',requirements:'2000单 · A车 · A骑手上岗 · 站点5级'}];
    const rowHeight=220,content=scrollContent(card,inner,top,bottom,regions.length*(rowHeight+18));
    regions.forEach((region,i)=>{
      const enabled=i===0,row=box(content,'Region-'+i,0,-i*(rowHeight+18)-rowHeight/2,inner,rowHeight,enabled?'#FFF1BB':'#F0EEE7',16);
      const id='M0'+(i+1);
      if(i===1)cartoonArt(row,'batch-'+id+'-landmark',-inner*.23,0,inner*.5,180);
      else {
        cartoonArt(row,'batch-'+id+'-display',-inner*.27,0,inner*.42,180);
        cartoonArt(row,'batch-'+id+'-landmark',inner*.05,0,inner*.18,135);
      }
      readable(row,region.name+(enabled?'':' · 未开放'),inner*.29,55,m.body,C.ink,inner*.38,true,'center',55);
      if(region.requirements)readable(row,region.requirements,inner*.29,-30,m.aux,C.muted,inner*.38,false,'center',120);
      if(enabled)tap(row,()=>this.dismissDialog());
    });
  }
  private openProfile():void {
    const {card,width,top,bottom}=this.dialog('人物展示',1060,'profile'),m=this.metrics(),inner=width-48;
    const content=scrollContent(card,inner,top,bottom,1480),player=this.book.player;
    readable(content,'当前骑手 · 造型仅供预览',0,-35,m.body,C.ink,inner,true,'center',60);
    readable(content,`等级 ${player.level} · 经验 ${player.experience} · 评价 ${player.rating}`,0,-95,m.aux,C.muted,inner,false,'center',52);
    cartoonArt(content,'profile-master',0,-310,inner*.65,350);
    ['P01','P02','P03'].forEach((id,i)=>{
      const y=-560-i*300;
      readable(content,['全天候造型预览','领队造型预览','运营造型预览'][i],0,y,m.body,C.ink,inner,true,'center',50);
      cartoonArt(content,'batch-'+id,0,y-135,inner*.7,240);
    });
  }

  private openBills():void {
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
        this.billValues[index]=readable(cell,row.value,inner/2-valueWidth/2,0,prominent?m.body+8:m.body,prominent?'#A95226':C.ink,valueWidth,true,'right',rowHeight-10);
        box(cell,'Divider',0,-rowHeight/2,inner,1,C.line,0);offset+=rowHeight;
      }
    }
  }
  private updateBills():void {
    if(this.modalKind!=='bills')return;
    const bill=this.book.billing;if(this.billDate)this.billDate.string=bill.day;
    billingRows(bill).forEach((row,i)=>{if(this.billValues[i])this.billValues[i].string=row.value;});
  }
  private closeGarage():void {
    if(this.pendingSave)return;this.closeDialog();if(this.gallery){this.gallery.active=false;this.gallery.destroy();this.gallery=null;}
    if(this.gameplayFrozen)this.openPauseDialog();
  }
  private openGarage():void {
    this.closeDialog();if(this.gallery){this.gallery.active=false;this.gallery.destroy();}
    const height=1280+this.screenExtra,margin=this.outerMargin(),safe=this.safeInsets,m=this.metrics();
    const page=this.gallery=item(this.root,'VehicleGallery',0,0,720,height);page.addComponent(BlockInputEvents);
    box(page,'GalleryBackground',0,0,720,height,C.paper,0);
    const width=720-safe.left-safe.right-2*margin,cx=(safe.left-safe.right)/2,top=height/2-safe.top-margin,bottom=-height/2+safe.bottom+margin;
    readable(page,'车辆',cx,top-36,m.body+8,C.ink,width-150,true,'center',64);
    closeButton(page,cx-width/2+36,top-36,64,()=>this.closeGarage());
    const inv=this.book.vehicleInventory,current=inv.instances.find(v=>v.id===inv.playerVehicleId)!,tier=current.tier;
    const hero=box(page,'CurrentVehicle',cx,top-178,width,190,'#F8EFE0',18,'#D7B987');
    const fallback=readable(hero,VEHICLE_NAMES[tier-1],-width*.28,0,m.aux,C.muted,width*.38,true,'center').node;
    vehicleSideArt(hero,tier,-width*.28,0,width*.4,160,fallback);
    readable(hero,'当前使用',width*.16,58,m.aux,'#A4582C',width*.55,true,'center',36);
    readable(hero,`${VEHICLE_GRADES[tier-1]} · ${VEHICLE_NAMES[tier-1]}`,width*.16,18,m.body,C.ink,width*.55,true,'center',44);
    readable(hero,`${VEHICLE_SPEED[tier-1]} km/h · 载重 ${VEHICLE_CAPACITY[tier-1]} kg`,width*.16,-26,m.aux,C.ink,width*.55,false,'center',40);
    readable(hero,`余额 ¥${(this.book.player.cashCents/100).toFixed(2)}`,width*.16,-66,m.aux,C.ink,width*.55,true,'center',40);
    const tabWidth=(width-12)/2,tabY=top-315;
    this.action(page,'全部车辆',cx-tabWidth/2-6,tabY,tabWidth,()=>{this.galleryMine=false;this.openGarage();},this.galleryMine?C.light:C.primary);
    this.action(page,'我的车辆',cx+tabWidth/2+6,tabY,tabWidth,()=>{this.galleryMine=true;this.openGarage();},this.galleryMine?C.primary:C.light);
    const rows=this.galleryMine?inv.instances.map(v=>({tier:v.tier,id:v.id})):VEHICLE_GRADES.map((_,i)=>({tier:i+1,id:''}));
    const gap=cssUnits(6,height),columns=(width-2*gap)/3>=cssUnits(100,height)?3:2,cellWidth=(width-gap*(columns-1))/columns,cellHeight=Math.max(220,cellWidth*1.14),rowCount=Math.ceil(rows.length/columns);
    const holder=item(page,'GalleryList',cx,0,width,height),content=scrollContent(holder,width,tabY-m.action/2-18,bottom,rowCount*(cellHeight+gap));
    if(!rows.length)readable(content,'暂无车辆',0,-70,m.body,C.muted,width,true,'center');
    rows.forEach((row,i)=>{
      const t=row.tier,x=-width/2+cellWidth/2+(i%columns)*(cellWidth+gap),y=-Math.floor(i/columns)*(cellHeight+gap)-cellHeight/2;
      const count=inv.instances.filter(v=>v.tier===t).length,using=row.id?row.id===inv.playerVehicleId:current.tier===t,locked=t>2;
      const card=box(content,'Vehicle-'+(row.id||t),x,y,cellWidth,cellHeight,'#FFFBF3',14,using?'#D59A50':'#D8CBB6');
      const fallback=readable(card,VEHICLE_NAMES[t-1],0,15,m.aux,C.muted,cellWidth-16,true,'center').node;
      vehicleSideArt(card,t,0,18,cellWidth-14,cellHeight*.58,fallback);
      const badge=box(card,'Grade',-cellWidth/2+30,cellHeight/2-23,52,34,'#A95E32',10);
      readable(badge,VEHICLE_GRADES[t-1],0,0,m.aux,'#FFFFFF',48,true,'center',32);
      readable(card,VEHICLE_NAMES[t-1],0,-cellHeight/2+62,m.aux,C.ink,cellWidth-12,true,'center',42);
      readable(card,`${count}/${VEHICLE_LIMITS[t-1]}  ${using?'使用中':locked?'未开放':count?'已拥有':'未拥有'}`,0,-cellHeight/2+24,m.aux,using?'#A45A29':C.muted,cellWidth-12,true,'center',40);
      tap(card,()=>this.showVehicleDetail(t,row.id));
    });
  }

  private showVehicleDetail(tier:number,id:string):void {
    const inv=this.book.vehicleInventory,m=this.metrics(),count=inv.instances.filter(v=>v.tier===tier).length;
    const {card,width,height,top,bottom}=this.dialog(VEHICLE_GRADES[tier-1]+' 车辆详情',950,'garage'),inner=width-48;
    const content=scrollContent(card,inner,top,bottom+3*(m.action+12),570);
    const fallback=readable(content,VEHICLE_NAMES[tier-1],0,-110,m.body,C.muted,inner,true,'center').node;
    vehicleSideArt(content,tier,0,-120,inner-30,210,fallback);
    const requirement=tier<=2?'县城可购买':tier<8?'当前阶段尚未开放；需后续车辆与地区功能':`尚未开放：一线车辆线索累计${[3,6,9][tier-8]}条、站点5级及国际地区`;
    readable(content,`${VEHICLE_NAMES[tier-1]} · ${VEHICLE_GRADES[tier-1]}\n速度 ${VEHICLE_SPEED[tier-1]} km/h · 载重 ${VEHICLE_CAPACITY[tier-1]} kg\n收入倍率 ×${VEHICLE_INCOME[tier-1]}\n副本 ¥${(VEHICLE_PRICE[tier-1]/100).toFixed(0)} · 已拥有 ${count}/${VEHICLE_LIMITS[tier-1]}\n${requirement}`,0,-390,m.aux,C.ink,inner,true,'center',270);
    const blocked=!!this.book.active||this.pendingSave||this.gameplayFrozen;
    const buy=tier<=2&&!blocked&&count<VEHICLE_LIMITS[tier-1]&&this.book.player.cashCents>=VEHICLE_PRICE[tier-1];
    const reason=blocked?'配送中不可购买':tier>2?'当前阶段尚未开放':count>=VEHICLE_LIMITS[tier-1]?'已达拥有上限':this.book.player.cashCents<VEHICLE_PRICE[tier-1]?'余额不足':'购买副本';
    this.action(card,reason,0,-height/2+24+m.action*2.5+24,inner,()=>this.confirmVehiclePurchase(tier),C.primary,buy);
    const canSelect=!!id&&id!==inv.playerVehicleId&&!blocked&&tier<=2;
    this.action(card,id===inv.playerVehicleId?'当前使用':'选择此车',0,-height/2+24+m.action*1.5+12,inner,()=>{if(!this.act(()=>this.book.selectPlayerVehicle(id)))return;this.closeDialog();this.openGarage();},C.light,canSelect);
    const canUpgrade=id===inv.playerVehicleId&&tier===1&&!blocked&&this.book.player.cashCents>=20000&&inv.instances.filter(v=>v.tier===2).length<VEHICLE_LIMITS[1];
    this.action(card,'原车升级 D+ · ¥200',0,-height/2+24+m.action/2,inner,()=>{if(!this.act(()=>this.book.upgradeVehicle()))return;this.closeDialog();this.openGarage();},C.light,canUpgrade);
  }
  private confirmVehiclePurchase(tier:number):void {
    const {card,width,height,top,bottom}=this.dialog('确认购买',490,'garage'),inner=width-48,m=this.metrics(),price=VEHICLE_PRICE[tier-1],count=this.book.vehicleInventory.instances.filter(v=>v.tier===tier).length;
    const content=scrollContent(card,inner,top,bottom+m.action+24,160);
    readable(content,`购买 ${VEHICLE_GRADES[tier-1]} 副本\n¥${(price/100).toFixed(2)} · 购买后 ${count+1}/${VEHICLE_LIMITS[tier-1]}\n余额 ¥${((this.book.player.cashCents-price)/100).toFixed(2)}`,0,-75,m.body,C.ink,inner,true,'center',150);
    this.action(card,'确认购买',0,-height/2+24+m.action/2,inner,()=>{if(!this.act(()=>this.book.buyVehicle(tier)))return;this.closeDialog();this.openGarage();});
  }
  private updatePickupServiceFill():void {
    const button=this.pickupServiceButton,active=this.book.active;if(!button||!button.isValid||!active)return;
    const fill=button.getChildByName('PickupServiceFill')?.getComponent(Graphics);if(!fill)return;
    const size=button.getComponent(UITransform)!,fraction=Math.max(0,Math.min(1,(active.pickupWaitElapsed||0)/PICKUP_STOP_SECONDS));
    fill.clear();if(fraction<=0)return;
    const width=(size.width-4)*fraction,height=size.height-4;
    fill.fillColor=col('#F0C574');fill.roundRect(-size.width/2+2,-height/2,width,height,Math.min(12,width/2));fill.fill();
  }
  private updateProgress():void {
    this.updatePickupServiceFill();
    const pause=this.profileCard?.getChildByName('HeaderContent')?.getChildByName('ProfileIdentity')?.getChildByName('Button-暂停');if(pause)pause.active=this.canPauseDelivery;
    const active=this.book.active;if(!active)return;
    const progress=this.book.progress;
    const remaining=active.deadlineSeconds-progress.displaySeconds*progress.progress;
    if(this.tripLabel){const phase=active.handoff?.phase,stage=phase==='awaitPickup'?'已到店，等待取餐':phase==='awaitDeliveryStart'?'取餐完成，准备送餐':this.book.tripStage==='pickup'?'前往餐厅取餐':this.book.tripStage==='collecting'?`正在取餐中 · ${Math.ceil(this.book.pickupWaitRemaining)}秒`:'正在送往顾客';this.tripLabel.string=stage+' · '+(remaining>=0?'剩余 ':'已超时 ')+formatRemaining(Math.abs(remaining));}
    if(this.timer)this.timer.string=active.mode==='done'?'已到达':remaining>=0?'剩余 '+formatRemaining(remaining):'已超时 '+formatRemaining(-remaining);
    if(this.progressFill){this.progressFill.setScale(progress.progress,1,1);this.progressFill.setPosition(-(720-this.safeInsets.left-this.safeInsets.right-2*this.outerMargin())/2*(1-progress.progress),-60);}
  }
}
