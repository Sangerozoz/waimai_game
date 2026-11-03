import { BlockInputEvents, Color, Graphics, Node, UITransform } from 'cc';
import { foodImage } from './FoodImages';
import { compactOrderHeight, compactOrderInfo, CompactOrder } from './CompactOrderInfo';
import { OrderBook } from './OrderBook';
import { buyerRemark, deadlineText, foodDescription, orderCautions } from './OrderPresentation';
import { box, closeButton, C, item, material, outline, skin, tap } from './SampleUI';
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
  box(this.node,'PhoneShadow',(insets.left-insets.right)/2+6,(insets.bottom-insets.top)/2-8,width+4,height+4,'#34373524',48);
  box(this.node,'PhoneSide',(insets.left-insets.right)/2+5,(insets.bottom-insets.top)/2-2,width+2,height+2,'#353B38',46);
  const frame=box(this.node,'PhoneFrame',(insets.left-insets.right)/2,(insets.bottom-insets.top)/2,width,height,C.navy,22,'#FFFCF5');frame.addComponent(BlockInputEvents);
  box(frame,'SideButton',width/2+3,height/2-180,7,92,C.blue,3);
  box(frame,'Screen',0,0,width-18,height-18,C.paper,18);
  box(frame,'RimHighlight',-width/2+7,0,3,height-76,'#D8D1C4',2);
  const top=height/2;
  const header=box(frame,'AppHeader',0,top-104,width-28,180,C.blue,30);
  box(frame,'HeaderJoin',0,top-157,width-28,74,C.blue,0);
  readable(frame,'09:41',-width/2+76,top-38,22,'#FFFCF5',80,true,'center');box(frame,'SpeakerIsland',0,top-38,119,25,C.navy,12);
  for(let i=0;i<3;i++)box(frame,'Signal-'+i,width/2-113+i*7,top-43+i*2,4,5+i*4,'#FFFCF5',1);
  const battery=box(frame,'Battery',width/2-56,top-38,28,13,'#FFFCF5',3);box(battery,'BatteryTip',16,0,3,6,'#FFFCF5',1);
  outline(readable(frame,'接单大厅',-65,top-100,m.body+4,'#FFFCF5',width-190,true),'#14549B');
  readable(frame,'附近10单 · 全程10km以内',-64,top-151,m.aux,'#FFFCF5',width-190);
  closeButton(frame,width/2-55,top-114,64,this.onClose);
  const noticeHeight=Math.max(m.action,88),noticeY=top-190-noticeHeight/2;
  readable(frame,this.book.isFirstDelivery?'首单推荐，先赚第一笔':'每日免费刷新，送完自动补单',-82,noticeY,m.aux,'#806953',width-240,true,'left',noticeHeight);
  this.action(frame,this.book.refreshesLeft?`刷新 ${this.book.refreshesLeft}/2`:'广告未开放',width/2-112,noticeY,174,m.action,this.onRefresh,this.book.refreshesLeft?C.primary:'#EEE9DD',!!this.book.refreshesLeft);
  const listTop=top-202-noticeHeight,listBottom=-top+88,cardWidth=width-64,rows=this.book.list();
  const layouts=rows.map(preview=>{
   const offer=preview.offer,details:CompactOrder={offer,from:this.book.data.pois[offer.from].name,to:this.book.data.pois[offer.to].name,metres:preview.available?preview.pickupMetres+preview.deliveryMetres:null};
   const header=(offer.source==='transfer'?'转单 · ':'')+(preview.available?deadlineText(preview.deadlineSeconds):'暂不可配送')+(offer.type==='urgent'?' · 加急':'');
   const headerHeight=textHeight(header,m.body,cardWidth-32),bodyHeight=compactOrderHeight(details,cardWidth-32,this.screenHeight);
   return {preview,details,header,headerHeight,bodyHeight,height:16+headerHeight+8+bodyHeight+12+m.action+16};
  });
  const total=layouts.reduce((sum,row)=>sum+row.height+18,0)+20,content=scrollContent(frame,width-44,listTop,listBottom,total);content.parent!.name='OrderList';content.name='OrderListContent';
  let offset=0;
  for(const {preview,details,header,headerHeight,bodyHeight,height} of layouts){
   const offer=preview.offer,card=box(content,'Offer-'+offer.id,0,-offset-height/2,cardWidth,height,C.paper,18,C.line);
   readable(card,header,0,height/2-16-headerHeight/2,m.body,offer.source==='transfer'?C.green:C.ink,cardWidth-32,true,'left',headerHeight);
   const body=item(card,'CompactOrderInfo',0,height/2-16-headerHeight-8,cardWidth-32,bodyHeight);compactOrderInfo(body,details,cardWidth-32,this.screenHeight);
   this.action(card,offer.source==='transfer'?'接受转单':'抢单',0,-height/2+16+m.action/2,cardWidth-32,m.action,()=>this.onAccept(offer.id),offer.source==='transfer'?C.green:C.primary,preview.available);offset+=height+18;
  }
  readable(frame,`共 ${rows.length} 单 · 上下滑动查看更多`,0,-top+57,m.aux,C.muted,width-60,false,'center');box(frame,'HomeIndicator',0,-top+24,126,5,C.navy,3);
 }
 private action(parent:Node,text:string,x:number,y:number,width:number,height:number,action:()=>void,fill=C.primary,enabled=true):void {
  const node=box(parent,'Button-'+text,x,y,width,height,fill,16);
  if(enabled&&(fill===C.primary||fill===C.light))skin(node,fill===C.primary?'button-yellow':'button-blue');
  if(enabled&&fill===C.green)material(node,width,height,C.green);
  if(!enabled)material(node,width,height,'#C5CCD5');
  const white=enabled&&(fill===C.light||fill===C.green),caption=readable(node,text,0,0,presentationMetrics(this.screenHeight).body,white?'#FFFCF5':enabled?C.ink:C.muted,width-16,true,'center',height-8);
  if(white)outline(caption);if(enabled)tap(node,action);
 }
 close():void{this.node.active=false;this.node.destroy();}
}
