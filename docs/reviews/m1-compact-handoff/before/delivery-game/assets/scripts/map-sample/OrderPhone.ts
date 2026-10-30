import { BlockInputEvents, Color, Graphics, Node, UITransform } from 'cc';
import { foodImage } from './FoodImages';
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
  box(this.node,'PhoneShadow',(insets.left-insets.right)/2+6,(insets.bottom-insets.top)/2-8,width+12,height+10,'#081E4270',48);
  box(this.node,'PhoneSide',(insets.left-insets.right)/2+5,(insets.bottom-insets.top)/2-2,width+8,height+2,'#102956',46);
  const frame=box(this.node,'PhoneFrame',(insets.left-insets.right)/2,(insets.bottom-insets.top)/2,width,height,C.navy,46,'#FFFFFF');frame.addComponent(BlockInputEvents);
  box(frame,'SideButton',width/2+3,height/2-180,7,92,C.blue,3);
  box(frame,'Screen',0,0,width-26,height-26,C.paper,34);
  box(frame,'RimHighlight',-width/2+7,0,3,height-76,'#93C7FF',2);
  const top=height/2;
  const header=box(frame,'AppHeader',0,top-104,width-28,180,C.blue,30);
  box(frame,'HeaderJoin',0,top-157,width-28,74,C.blue,0);
  readable(frame,'09:41',-width/2+76,top-38,22,'#FFFFFF',80,true,'center');box(frame,'SpeakerIsland',0,top-38,119,25,C.navy,12);
  for(let i=0;i<3;i++)box(frame,'Signal-'+i,width/2-113+i*7,top-43+i*2,4,5+i*4,'#FFFFFF',1);
  const battery=box(frame,'Battery',width/2-56,top-38,28,13,'#FFFFFF',3);box(battery,'BatteryTip',16,0,3,6,'#FFFFFF',1);
  outline(readable(frame,'接单大厅',-65,top-100,m.body+4,'#FFFFFF',width-190,true),'#14549B');
  readable(frame,'附近10单 · 全程10km以内',-64,top-151,m.aux,'#FFFFFF',width-190);
  closeButton(frame,width/2-55,top-114,64,this.onClose);
  const noticeHeight=Math.max(m.action,88),noticeY=top-190-noticeHeight/2;
  readable(frame,this.book.isFirstDelivery?'首单推荐，先赚第一笔':'每日免费刷新，送完自动补单',-82,noticeY,m.aux,'#806017',width-240,true,'left',noticeHeight);
  this.action(frame,this.book.refreshesLeft?`刷新 ${this.book.refreshesLeft}/2`:'广告未开放',width/2-112,noticeY,174,m.action,this.onRefresh,this.book.refreshesLeft?C.primary:'#EEE9DD',!!this.book.refreshesLeft);
  const listTop=top-202-noticeHeight,listBottom=-top+88,cardWidth=width-64,rows=this.book.list();
  const layouts=rows.map(preview=>{
   const offer=preview.offer,inner=cardWidth-32,remark=buyerRemark(offer);
   const lines=[
    {text:(offer.source==='transfer'?'转单 · ':'')+deadlineText(preview.deadlineSeconds),bold:true,color:offer.source==='transfer'?C.green:C.ink},
    {text:foodDescription(offer),food:true,bold:true},
    {text:`重量 ${offer.weightKg}kg`},
    {text:'取餐 '+this.book.data.pois[offer.from].name},
    {text:'送达 '+this.book.data.pois[offer.to].name},
    {text:`全程 ${((preview.pickupMetres+preview.deliveryMetres)/1000).toFixed(1)}km · ${orderCautions(offer)}`},
    ...(remark?[{text:'买家备注：'+remark}]:[]),
    {text:'配送费 ¥'+(offer.feeCents/100).toFixed(2),bold:true,color:'#9A6500'},
   ].map(line=>({...line,height:Math.max(line.food?116:0,textHeight(line.text,m.body,line.food?inner-128:inner))}));
   return {preview,lines,height:32+lines.reduce((sum,line)=>sum+line.height+12,0)+m.action+24};
  });
  const total=layouts.reduce((sum,row)=>sum+row.height+18,0)+20,content=scrollContent(frame,width-44,listTop,listBottom,total);content.parent!.name='OrderList';content.name='OrderListContent';
  let offset=0;
  for(const {preview,lines,height} of layouts){
   const offer=preview.offer,card=box(content,'Offer-'+offer.id,0,-offset-height/2,cardWidth,height,C.paper,18,C.line);
   let y=height/2-16;
   for(const line of lines){
    y-=line.height/2;
    if(line.food)foodImage(card,offer.food,-cardWidth/2+70,y,108);
    readable(card,line.text,line.food?64:0,y,m.body,line.color||C.ink,line.food?cardWidth-160:cardWidth-32,!!line.bold,'left',line.height);y-=line.height/2+12;
   }
   this.action(card,offer.source==='transfer'?'接受转单':'抢单',0,-height/2+16+m.action/2,cardWidth-32,m.action,()=>this.onAccept(offer.id),offer.source==='transfer'?C.green:C.primary);offset+=height+18;
  }
  readable(frame,`共 ${rows.length} 单 · 上下滑动查看更多`,0,-top+57,m.aux,C.muted,width-60,false,'center');box(frame,'HomeIndicator',0,-top+24,126,5,C.navy,3);
 }
 private action(parent:Node,text:string,x:number,y:number,width:number,height:number,action:()=>void,fill=C.primary,enabled=true):void {
  const node=box(parent,'Button-'+text,x,y,width,height,fill,16);
  if(enabled&&(fill===C.primary||fill===C.light))skin(node,fill===C.primary?'button-yellow':'button-blue');
  if(enabled&&fill===C.green)material(node,width,height,C.green);
  if(!enabled)material(node,width,height,'#C5CCD5');
  const white=enabled&&(fill===C.light||fill===C.green),caption=readable(node,text,0,0,presentationMetrics(this.screenHeight).body,white?'#FFFFFF':enabled?C.ink:C.muted,width-16,true,'center',height-8);
  if(white)outline(caption);if(enabled)tap(node,action);
 }
 close():void{this.node.active=false;this.node.destroy();}
}
