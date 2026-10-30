import { Node } from 'cc';
import { DeliveryOffer } from './OrderBook';
import { buyerRemark, foodDescription, orderCautions } from './OrderPresentation';
import { foodImage } from './FoodImages';
import { C } from './SampleUI';
import { presentationMetrics, readable, textHeight } from './PresentationLayout';

// Keep the same font sizes while using compact, readable line spacing.
function compactHeight(text:string,size:number,width:number):number {
 const raw=textHeight(text,size,width),lines=Math.max(1,Math.round((raw-8)/(size*1.42)));return lines*Math.ceil(size*1.18)+4;
}
function compactText(parent:Node,text:string,x:number,y:number,size:number,fill:string,width:number,bold:boolean,align:'left'|'center'|'right',height:number):void {
 const label=readable(parent,text,x,y,size,fill,width,bold,align,height);label.lineHeight=Math.ceil(size*1.18);
}

// Match SampleUI's actual web font; reserve the food column before fitting long prices.
function amountLayout(fee:string,size:number,width:number):{price:number;size:number} {
 const context=typeof document!=='undefined'&&document.createElement?document.createElement('canvas').getContext('2d'):null;
 const measure=(fontSize:number)=>{if(context){context.font=`bold ${fontSize}px Arial Rounded MT Bold, sans-serif`;return context.measureText(fee).width;}return fee.length*fontSize*.62;};
 const price=Math.min(Math.max(210,Math.ceil(measure(size))+8),Math.max(100,width-88-24-100));
 while(size>1&&measure(size)>price-8)size--;
 return {price,size};
}
export interface CompactOrder {offer:DeliveryOffer;from:string;to:string;metres:number|null}
export function compactOrderHeight(data:CompactOrder,width:number,screenHeight:number):number {
 const m=presentationMetrics(screenHeight),image=88,amount=amountLayout('¥'+(data.offer.feeCents/100).toFixed(2),m.amount,width),price=amount.price,middle=Math.max(100,width-image-price-24),side=(width-54)/2;
 const foodHeight=Math.max(image,compactHeight(foodDescription(data.offer),m.body,middle)+compactHeight(`${data.offer.weightKg}kg · ${orderCautions(data.offer)}`,m.aux,middle),compactHeight('¥'+(data.offer.feeCents/100).toFixed(2),amount.size,price)+compactHeight(data.metres===null?'距离不可用':(data.metres/1000).toFixed(1)+'km',m.aux,price));
 const addressHeight=Math.max(compactHeight('取餐\n'+data.from,m.aux,side),compactHeight('送达\n'+data.to,m.aux,side));
 const note=buyerRemark(data.offer),noteHeight=note?compactHeight('备注：'+note,m.aux,width):0;
 return foodHeight+addressHeight+noteHeight+20+(note?8:0);
}
/** Common compact data layout used by both the lobby and current order. */
export function compactOrderInfo(parent:Node,data:CompactOrder,width:number,screenHeight:number):number {
 const m=presentationMetrics(screenHeight),image=88,amount=amountLayout('¥'+(data.offer.feeCents/100).toFixed(2),m.amount,width),price=amount.price,middle=Math.max(100,width-image-price-24),side=(width-54)/2;
 const food=foodDescription(data.offer),weight=`${data.offer.weightKg}kg · ${orderCautions(data.offer)}`,nameH=compactHeight(food,m.body,middle),weightH=compactHeight(weight,m.aux,middle);
 const fee='¥'+(data.offer.feeCents/100).toFixed(2),feeH=compactHeight(fee,amount.size,price),distanceH=compactHeight(data.metres===null?'距离不可用':(data.metres/1000).toFixed(1)+'km',m.aux,price);
 const foodH=Math.max(image,nameH+weightH,feeH+distanceH),mx=-width/2+image+12+middle/2,px=width/2-price/2;
 foodImage(parent,data.offer.food,-width/2+image/2,-foodH/2,image);
 const middleTop=-(foodH-nameH-weightH)/2;
 compactText(parent,food,mx,middleTop-nameH/2,m.body,C.ink,middle,true,'left',nameH);
 compactText(parent,weight,mx,middleTop-nameH-weightH/2,m.aux,C.muted,middle,false,'left',weightH);
 compactText(parent,fee,px,-feeH/2,amount.size,'#B87513',price,true,'right',feeH);
 compactText(parent,data.metres===null?'距离不可用':(data.metres/1000).toFixed(1)+'km',px,-feeH-distanceH/2,m.aux,C.ink,price,false,'right',distanceH);
 let y=-foodH-10;const from='取餐\n'+data.from,to='送达\n'+data.to,fh=compactHeight(from,m.aux,side),th=compactHeight(to,m.aux,side),ah=Math.max(fh,th);
 compactText(parent,from,-width/2+side/2,y-ah/2,m.aux,C.ink,side,true,'left',ah);
 compactText(parent,'→',0,y-ah/2,m.body,C.muted,46,true,'center',ah);
 compactText(parent,to,width/2-side/2,y-ah/2,m.aux,C.ink,side,true,'right',ah);y-=ah+10;
 const note=buyerRemark(data.offer);if(note){const text='备注：'+note,h=compactHeight(text,m.aux,width);compactText(parent,text,0,y-h/2,m.aux,C.ink,width,false,'left',h);y-=h+8;}
 return -y;
}
