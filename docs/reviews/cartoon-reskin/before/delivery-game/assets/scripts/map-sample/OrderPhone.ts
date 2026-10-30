import { BlockInputEvents, Color, Graphics, Node, UITransform } from 'cc';
import { foodImage } from './FoodImages';
import { OrderBook } from './OrderBook';
import { formatDeliveryTime } from './DeliveryClock';
import { box, C, item, tap } from './SampleUI';
import { SafeInsets } from './SafeAreaLayout';
import { presentationMetrics, readable, scrollContent, textHeight } from './PresentationLayout';

export class OrderPhone {
 readonly node:Node;
 constructor(parent:Node,private readonly book:OrderBook,private readonly screenHeight:number,
  private readonly onAccept:(id:string)=>void,private readonly onClose:()=>void,private readonly onRefresh:()=>void,private readonly safeInsets:SafeInsets={top:0,bottom:0,left:0,right:0}) {
  this.node=item(parent,'OrderPhoneModal',0,0,720,screenHeight);this.node.addComponent(BlockInputEvents);
  const shade=item(this.node,'Backdrop',0,0,720,screenHeight),g=shade.addComponent(Graphics);
  g.fillColor=new Color(0,0,0,153);g.rect(-360,-screenHeight/2,720,screenHeight);g.fill();tap(shade,this.onClose);this.render();
 }
 private render():void {
  const m=presentationMetrics(this.screenHeight),insets=this.safeInsets;
  const width=Math.min(684,720-insets.left-insets.right-36),height=Math.min(1240,this.screenHeight-insets.top-insets.bottom-24);
  const frame=box(this.node,'PhoneFrame',(insets.left-insets.right)/2,(insets.bottom-insets.top)/2,width,height,'#302B20',46,'#6B6048');frame.addComponent(BlockInputEvents);
  box(frame,'SideButton',width/2+3,height/2-180,7,92,'#5B513E',3);
  box(frame,'Screen',0,0,width-26,height-26,'#F8F6EF',34);
  const top=height/2;
  readable(frame,'09:41',-width/2+76,top-38,22,C.ink,80,true,'center');box(frame,'SpeakerIsland',0,top-38,119,25,'#302B20',12);
  const battery=box(frame,'Battery',width/2-56,top-38,28,13,'#302B20',3);box(battery,'BatteryTip',16,0,3,6,'#302B20',1);
  box(frame,'AppHeader',0,top-120,width-28,122,C.primary,0);
  readable(frame,'接单大厅',-65,top-100,m.body+4,C.ink,width-190,true);
  readable(frame,'附近10单 · 全程10km以内',-64,top-151,m.aux,'#69551D',width-190);
  this.action(frame,'关闭',width/2-76,top-114,100,m.action,this.onClose,'#FFE59A');
  const noticeHeight=Math.max(m.action,88),noticeY=top-190-noticeHeight/2;
  readable(frame,this.book.isFirstDelivery?'首单推荐，先赚第一笔':'每日免费刷新，送完自动补单',-82,noticeY,m.aux,'#806017',width-240,true,'left',noticeHeight);
  this.action(frame,this.book.refreshesLeft?`刷新 ${this.book.refreshesLeft}/2`:'广告未开放',width/2-112,noticeY,174,m.action,this.onRefresh,this.book.refreshesLeft?C.primary:'#EEE9DD',!!this.book.refreshesLeft);
  const listTop=top-202-noticeHeight,listBottom=-top+88,cardWidth=width-64,rows=this.book.list();
  const layouts=rows.map(preview=>{
   const merchant=this.book.data.pois[preview.offer.from].name,destination='送至 '+this.book.data.pois[preview.offer.to].name;
   const titleH=textHeight(preview.offer.food,m.body,cardWidth-160),headH=Math.max(148,titleH+76);
   const merchantH=textHeight('取餐 '+merchant,m.aux,cardWidth-32),destinationH=textHeight(destination,m.body,cardWidth-32);
   return {preview,merchant,destination,titleH,headH,merchantH,destinationH,height:headH+merchantH+destinationH+88+m.action+42};
  });
  const total=layouts.reduce((sum,row)=>sum+row.height+18,0)+20,content=scrollContent(frame,width-44,listTop,listBottom,total);content.parent!.name='OrderList';content.name='OrderListContent';
  let offset=0;
  for(const row of layouts){
   const {preview,merchant,destination,titleH,headH,merchantH,destinationH,height}=row,offer=preview.offer;
   const card=box(content,'Offer-'+offer.id,0,-offset-height/2,cardWidth,height,C.paper,18,C.line),t=height/2;
   foodImage(card,offer.food,-cardWidth/2+70,t-76,108);
   readable(card,offer.food,72,t-18-titleH/2,m.body,C.ink,cardWidth-164,true,'left',titleH);
   readable(card,'约¥'+(preview.estimatedIncomeCents/100).toFixed(2),72,t-headH+42,m.amount,'#9A6500',cardWidth-164,true,'left',76);
   let y=t-headH-merchantH/2;readable(card,'取餐 '+merchant,0,y,m.aux,C.muted,cardWidth-32,false,'left',merchantH);
   y-=merchantH/2+destinationH/2+8;readable(card,destination,0,y,m.body,C.ink,cardWidth-32,false,'left',destinationH);
   y-=destinationH/2+40;
   const tags=[offer.type==='urgent'?'加急':'',offer.fragility==='fragile'?'怕洒':''].filter(Boolean).join(' · ');
   readable(card,`${((preview.pickupMetres+preview.deliveryMetres)/1000).toFixed(1)}km · 预计${formatDeliveryTime(preview.timing.displaySeconds)}${tags?' · '+tags:''}`,0,y,m.aux,'#795020',cardWidth-32,true,'left',76);
   this.action(card,'接单',0,-height/2+20+m.action/2,cardWidth-32,m.action,()=>this.onAccept(offer.id));offset+=height+18;
  }
  readable(frame,`共 ${rows.length} 单 · 上下滑动查看更多`,0,-top+57,m.aux,C.muted,width-60,false,'center');box(frame,'HomeIndicator',0,-top+24,126,5,'#302B20',3);
 }
 private action(parent:Node,text:string,x:number,y:number,width:number,height:number,action:()=>void,fill=C.primary,enabled=true):void {
  const node=box(parent,'Button-'+text,x,y,width,height,fill,16);readable(node,text,0,0,presentationMetrics(this.screenHeight).body,enabled?C.ink:C.muted,width-16,true,'center',height-8);if(enabled)tap(node,action);
 }
 close():void{this.node.active=false;this.node.destroy();}
}
