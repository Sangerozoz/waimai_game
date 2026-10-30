import { BlockInputEvents, Color, Graphics, Mask, Node, ScrollView, UITransform } from 'cc';
import { foodImage } from './FoodImages';
import { OrderBook } from './OrderBook';
import { formatDeliveryTime } from './DeliveryClock';
import { box, button, C, item, label } from './SampleUI';

export class OrderPhone {
  readonly node:Node;
  constructor(parent:Node,private readonly book:OrderBook,screenHeight:number,
    private readonly onAccept:(id:string)=>void,private readonly onClose:()=>void,private readonly onRefresh:()=>void) {
    this.node=item(parent,'OrderPhoneModal',0,0,720,screenHeight);
    this.node.addComponent(BlockInputEvents);
    const shade=item(this.node,'Backdrop',0,0,720,screenHeight),g=shade.addComponent(Graphics);
    g.fillColor=new Color(25,22,16,185);g.rect(-360,-screenHeight/2,720,screenHeight);g.fill();
    shade.on(Node.EventType.TOUCH_END,this.onClose);
    this.render();
  }
  private render():void {
    const previous=this.node.getChildByName('PhoneFrame');if(previous){previous.active=false;previous.destroy();}
    const frame=box(this.node,'PhoneFrame',0,0,624,1120,'#302B20',46,'#6B6048');
    frame.addComponent(BlockInputEvents);
    box(frame,'SideButton',316,218,7,92,'#5B513E',3);
    box(frame,'Screen',0,0,590,1086,'#F8F6EF',34);
    label(frame,'09:41',-222,511,17,C.ink,70,true,'center');
    box(frame,'SpeakerIsland',0,511,119,25,'#302B20',12);
    const battery=box(frame,'Battery',238,511,28,13,'#302B20',3);box(battery,'BatteryTip',16,0,3,6,'#302B20',1);
    box(frame,'AppHeader',0,439,586,103,C.primary,0);
    label(frame,'接单大厅',-96,451,29,C.ink,327,true);
    label(frame,'附近10单 · 全程10km以内',-103,414,18,'#69551D',310);
    button(frame,'关闭',226,451,73,49,this.onClose,'#FFE59A',C.ink);
    box(frame,'Notice',0,366,548,42,'#FFF0BE',12);
    label(frame,this.book.isFirstDelivery?'首单推荐，先赚到第一笔收入':'每日免费刷新，送完自动补单',-72,366,18,'#806017',380,true,'center');
    button(frame,this.book.refreshesLeft?`刷新 ${this.book.refreshesLeft}/2`:'广告未开放',208,366,127,38,this.onRefresh,this.book.refreshesLeft?C.primary:'#EEE9DD',C.ink);
    const rows=this.book.list();
    const viewport=item(frame,'OrderList',0,-50,548,782);
    viewport.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
    const content=item(viewport,'OrderListContent',0,391,548,rows.length*154-8);
    content.getComponent(UITransform)!.setAnchorPoint(.5,1);
    rows.forEach((preview,i)=>{
      const offer=preview.offer,card=box(content,'Offer-'+offer.id,0,-73-i*154,548,146,C.paper,15,C.line);
      foodImage(card,offer.food,-211,13,100);
      label(card,offer.food,-20,49,23,C.ink,260,true);
      label(card,'约¥'+(preview.estimatedIncomeCents/100).toFixed(2),207,49,25,'#9A6500',120,true,'right');
      label(card,this.book.data.pois[offer.from].name,-9,17,18,C.muted,286);
      label(card,'送至 '+this.book.data.pois[offer.to].name,-9,-10,18,C.ink,286);
      const tags=[offer.type==='urgent'?'加急':'',offer.fragility==='fragile'?'怕洒':''].filter(Boolean).join(' · ');
      if(tags)label(card,tags,-211,-53,16,'#9A6500',108,true,'center');
      label(card,`${((preview.pickupMetres+preview.deliveryMetres)/1000).toFixed(1)}km · 预计${formatDeliveryTime(preview.timing.displaySeconds)}`,-9,-48,17,'#9A6500',286,true);
      button(card,'接单',211,-21,108,68,()=>this.onAccept(offer.id));
    });
    const scroll=viewport.addComponent(ScrollView);scroll.content=content;scroll.horizontal=false;scroll.vertical=true;scroll.elastic=false;scroll.cancelInnerEvents=true;
    label(frame,`共 ${rows.length} 单 · 上下滑动查看更多`,0,-475,19,C.muted,510,true,'center');
    box(frame,'HomeIndicator',0,-524,126,5,'#302B20',3);
  }
  close():void{this.node.active=false;this.node.destroy();}
}
