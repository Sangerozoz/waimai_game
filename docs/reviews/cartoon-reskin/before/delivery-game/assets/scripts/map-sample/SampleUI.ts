import { Color, EventTouch, Graphics, Label, Layers, Node, UITransform } from 'cc';
export const C={navy:'#302B20',ink:'#302B20',muted:'#64695F',paper:'#FFFFFF',primary:'#FFC52D',gold:'#B58015',green:'#348866',line:'#E3E2D8',light:'#F6F3EA'};
export function col(hex:string):Color{return new Color(parseInt(hex.slice(1,3),16),parseInt(hex.slice(3,5),16),parseInt(hex.slice(5,7),16),hex.length===9?parseInt(hex.slice(7,9),16):255);}
export function item(parent:Node,name:string,x=0,y=0,w=0,h=0):Node{const n=new Node(name);n.layer=Layers.Enum.UI_2D;parent.addChild(n);n.setPosition(x,y);n.addComponent(UITransform).setContentSize(w,h);return n;}
export function box(parent:Node,name:string,x:number,y:number,w:number,h:number,fill:string,radius=16,stroke?:string):Node{
 const n=item(parent,name,x,y,w,h),g=n.addComponent(Graphics);g.fillColor=col(fill);g.roundRect(-w/2,-h/2,w,h,radius);g.fill();
 if(stroke){g.strokeColor=col(stroke);g.lineWidth=1.5;g.roundRect(-w/2+1,-h/2+1,w-2,h-2,radius);g.stroke();}return n;
}
export function label(parent:Node,value:string,x:number,y:number,size=20,fill=C.ink,width=600,bold=false,align:'left'|'center'|'right'='left'):Label{
 const n=item(parent,'Label',x,y,width,size*1.6);const l=n.addComponent(Label);l.string=value;l.fontSize=size;l.lineHeight=size*1.45;l.color=col(fill);l.isBold=bold;
 l.horizontalAlign=align==='left'?Label.HorizontalAlign.LEFT:align==='right'?Label.HorizontalAlign.RIGHT:Label.HorizontalAlign.CENTER;l.verticalAlign=Label.VerticalAlign.CENTER;l.overflow=Label.Overflow.SHRINK;return l;
}
export function tap(n:Node,action:()=>void):void{
 // Match ScrollView's 7 UI-pixel drag threshold; a move event alone is not a drag.
 let touchId:number|null=null,startX=0,startY=0,dragged=false;
 const beyondTap=(event:EventTouch):boolean=>{const p=event.getUILocation();return (p.x-startX)**2+(p.y-startY)**2>49;};
 n.on(Node.EventType.TOUCH_START,(event:EventTouch)=>{
  const id=event.getID();if(id===null||touchId!==null&&touchId!==id)return;
  const p=event.getUILocation();touchId=id;startX=p.x;startY=p.y;dragged=false;
  // Keep the hit target's transform unchanged while the engine tests the release position.
 });
 n.on(Node.EventType.TOUCH_MOVE,(event:EventTouch)=>{if(touchId!==null&&event.getID()===touchId&&beyondTap(event))dragged=true;});
 n.on(Node.EventType.TOUCH_CANCEL,(event:EventTouch)=>{if(event.getID()===null||event.getID()===touchId){touchId=null;dragged=false;}});
 n.on(Node.EventType.TOUCH_END,(event:EventTouch)=>{
  if(touchId===null||event.getID()!==touchId)return;
  const activate=!dragged&&!beyondTap(event);touchId=null;dragged=false;
  if(activate)action();
 });
}
export function button(parent:Node,text:string,x:number,y:number,w:number,h:number,action:()=>void,fill=C.primary,foreground=C.ink,enabled=true):Node{
 const n=box(parent,'Button-'+text,x,y,w,h,fill,14,fill===C.paper?C.line:undefined);label(n,text,0,0,22,foreground,w-12,true,'center');if(enabled)tap(n,action);return n;
}
export function icon(parent:Node,kind:string,x:number,y:number,fill=C.navy,scale=1):Node{
 const n=item(parent,'Icon-'+kind,x,y,32,32),g=n.addComponent(Graphics);n.setScale(scale,scale,1);g.lineWidth=2.4;g.strokeColor=col(fill);g.fillColor=col(fill);
 if(kind==='target'){g.circle(0,0,9);g.stroke();g.circle(0,0,3);g.fill();for(const [a,b,c,d] of [[-15,0,-10,0],[10,0,15,0],[0,-15,0,-10],[0,10,0,15]]){g.moveTo(a,b);g.lineTo(c,d);g.stroke();}}
 else if(kind==='map'){g.moveTo(-13,-10);g.lineTo(-5,-6);g.lineTo(5,-10);g.lineTo(13,-6);g.lineTo(13,12);g.lineTo(5,8);g.lineTo(-5,12);g.lineTo(-13,8);g.close();g.stroke();for(const xx of [-5,5]){g.moveTo(xx,-6);g.lineTo(xx,8);g.stroke();}}
 else if(kind==='recruit'){g.circle(0,7,5);g.stroke();g.roundRect(-10,-14,20,14,6);g.stroke();}
 else if(kind==='vehicle'){g.circle(-9,-8,5);g.stroke();g.circle(11,-8,5);g.stroke();g.moveTo(-9,-8);g.lineTo(-1,6);g.lineTo(7,-8);g.lineTo(-9,-8);g.moveTo(7,-8);g.lineTo(9,10);g.lineTo(15,10);g.moveTo(-5,6);g.lineTo(1,6);g.stroke();}
 else if(kind==='bills'){g.roundRect(-10,-14,20,28,2);g.stroke();for(const y of [7,0,-7]){g.moveTo(-6,y);g.lineTo(y===-7?3:6,y);g.stroke();}}
 else if(kind==='plus'||kind==='minus'){g.moveTo(-9,0);g.lineTo(9,0);g.stroke();if(kind==='plus'){g.moveTo(0,-9);g.lineTo(0,9);g.stroke();}}
 else if(kind==='sun'){g.circle(0,0,6);g.stroke();for(let i=0;i<8;i++){const a=i*Math.PI/4;g.moveTo(Math.cos(a)*10,Math.sin(a)*10);g.lineTo(Math.cos(a)*13,Math.sin(a)*13);g.stroke();}}
 return n;
}
