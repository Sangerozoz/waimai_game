import { Color, EventTouch, Graphics, Label, Layers, Node, Sprite, UITransform, Tween, tween, Vec3 } from 'cc';
import { cartoonArt } from './CartoonArt';
export const C={navy:'#343735',ink:'#303633',muted:'#777B73',paper:'#FFFCF5',primary:'#ED782E',gold:'#BB6028',green:'#4C8269',line:'#D8D1C4',light:'#ECE8DE',blue:'#444C48',violet:'#444C48'};
export function col(hex:string):Color{return new Color(parseInt(hex.slice(1,3),16),parseInt(hex.slice(3,5),16),parseInt(hex.slice(5,7),16),hex.length===9?parseInt(hex.slice(7,9),16):255);}
export function item(parent:Node,name:string,x=0,y=0,w=0,h=0):Node{const n=new Node(name);n.layer=Layers.Enum.UI_2D;parent.addChild(n);n.setPosition(x,y);n.addComponent(UITransform).setContentSize(w,h);return n;}
// One surface drawn at the final target size, inside the touch rectangle.
export function paintBox(n:Node,w:number,h:number,fill:string,radius=16,stroke?:string):void {
 const surface=n.getChildByName('Surface')||item(n,'Surface');
 const g=surface.getComponent(Graphics)||surface.addComponent(Graphics);g.clear();
 const r=Math.max(0,Math.min(radius,18,w/2,h/2));
 if(radius>0&&w>60&&h>42){g.fillColor=col('#36382F14');g.roundRect(-w/2+1,-h/2-3,w,h,r);g.fill();}
 g.fillColor=col(fill);g.roundRect(-w/2,-h/2,w,h,r);g.fill();
 if(radius>0||stroke){g.strokeColor=col(stroke||C.line);g.lineWidth=1;g.roundRect(-w/2+.5,-h/2+.5,w-1,h-1,r);g.stroke();}
}

// Original geometry inspired by the approved references; dynamic captions remain separate.
function refinedButton(g:Graphics,w:number,h:number,primary:boolean):void {
 const tip=Math.min(12,h*.16),half=w/2,hh=h/2;
 const contour=(inset:number)=>{const x=half-inset,y=hh-inset,t=Math.max(2,tip-inset*.25);g.moveTo(-x+t,-y);g.lineTo(x-t,-y);g.lineTo(x,0);g.lineTo(x-t,y);g.lineTo(-x+t,y);g.lineTo(-x,0);g.close();};
 g.fillColor=col('#35271922');contour(0);g.fill();
 const bottom=col(primary?'#EDAC63':'#392C24E8'),top=col(primary?'#F9E6B8':'#63503BE8');
 // Bands follow the bevel contour, avoiding an external texture or shader dependency.
 const steps=36;
 for(let i=0;i<steps;i++){
  const y0=-hh+h*i/steps,y1=-hh+h*(i+1)/steps,t=(i+.5)/steps;
  const edge=(y:number)=>half-tip*Math.abs(y)/hh;
  g.fillColor=new Color(Math.round(bottom.r+(top.r-bottom.r)*t),Math.round(bottom.g+(top.g-bottom.g)*t),Math.round(bottom.b+(top.b-bottom.b)*t),primary?255:232);
  g.moveTo(-edge(y0),y0);g.lineTo(edge(y0),y0);g.lineTo(edge(y1),y1);g.lineTo(-edge(y1),y1);g.close();g.fill();
 }
 g.strokeColor=col(primary?'#BE8B46':'#BDA078');g.lineWidth=1.3;contour(1);g.stroke();
 g.strokeColor=col(primary?'#FFF3D1B8':'#E2C59A65');g.lineWidth=.8;contour(4);g.stroke();
 if(w>150){
  const d=Math.min(3.5,h*.045),cx=half-tip-3;
  for(const sign of [-1,1]){const x=cx*sign;g.fillColor=col(primary?'#FFF4D7':'#D7B77D');g.moveTo(x-d,0);g.lineTo(x,d*1.4);g.lineTo(x+d,0);g.lineTo(x,-d*1.4);g.close();g.fill();}
 }
}
export function material(n:Node,w:number,h:number,fill:string,radius=Math.min(h*.35,w/2)):void {
 const surface=n.getChildByName('Surface')||item(n,'Surface'),g=surface.getComponent(Graphics)||surface.addComponent(Graphics);g.clear();
 if(n.name.startsWith('Button-')&&(fill===C.primary||fill===C.blue||fill===C.light)){refinedButton(g,w,h,fill===C.primary);return;}
 const face=fill===C.light?C.blue:fill,r=Math.min(14,radius);
 g.fillColor=col('#30362D1C');g.roundRect(-w/2,-h/2-3,w,h,r);g.fill();
 g.fillColor=col(face);g.roundRect(-w/2,-h/2,w,h,r);g.fill();
 g.strokeColor=col('#34373522');g.lineWidth=1;g.roundRect(-w/2+.5,-h/2+.5,w-1,h-1,r);g.stroke();
}
export function box(parent:Node,name:string,x:number,y:number,w:number,h:number,fill:string,radius=16,stroke?:string):Node{
 const n=item(parent,name,x,y,w,h);paintBox(n,w,h,fill,radius,stroke);if(/^(Button-|CloseButton|NavigationBackdrop|Region-|Route-)/.test(name))material(n,w,h,fill,radius===0?18:Math.min(h*.35,w/2));return n;
}
export type ChromeKey='panel-blue'|'panel-violet'|'button-yellow'|'button-blue';
// Geometry is drawn at its final dimensions; PNG chrome is no longer stretched.
export function skin(node:Node,key:ChromeKey):Node {
 const size=node.getComponent(UITransform)!;
 if(key.startsWith('button-'))material(node,size.width,size.height,key==='button-yellow'?C.primary:C.blue);else paintBox(node,size.width,size.height,key==='panel-violet'?C.violet:C.blue,18,C.line);
 return node;
}
export function outline(text:Label,color='#124784',width=3):void {
 text.enableOutline=false;text.outlineColor=col(color);text.outlineWidth=0;
}
export function label(parent:Node,value:string,x:number,y:number,size=20,fill=C.ink,width=600,bold=false,align:'left'|'center'|'right'='left'):Label{
 const n=item(parent,'Label',x,y,width,size*1.6);const l=n.addComponent(Label);l.string=value;l.fontSize=size;l.lineHeight=size*1.45;l.color=col(fill);l.isBold=bold;l.fontFamily='Arial Rounded MT Bold, sans-serif';
 l.horizontalAlign=align==='left'?Label.HorizontalAlign.LEFT:align==='right'?Label.HorizontalAlign.RIGHT:Label.HorizontalAlign.CENTER;l.verticalAlign=Label.VerticalAlign.CENTER;l.overflow=Label.Overflow.SHRINK;return l;
}
export function tap(n:Node,action:()=>void):void{
 // Match ScrollView's 7 UI-pixel drag threshold; a move event alone is not a drag.
 const decorative=!/Shade|Backdrop/.test(n.name);
 const visual=decorative?item(n,'PressVisual'):null;
 if(visual)for(const child of [...n.children])if(child!==visual)visual.addChild(child);
 const reset=(immediate=true)=>{if(!visual)return;Tween.stopAllByTarget(visual);if(immediate)visual.setScale(1,1,1);else tween(visual).to(.12,{scale:new Vec3(1,1,1)},{easing:'quadOut'}).start();};
 let touchId:number|null=null,startX=0,startY=0,dragged=false;
 const cancel=()=>{touchId=null;dragged=false;reset();};
 n.on(Node.EventType.ACTIVE_IN_HIERARCHY_CHANGED,cancel);n.on(Node.EventType.NODE_DESTROYED,cancel);
 const beyondTap=(event:EventTouch):boolean=>{const p=event.getUILocation();return (p.x-startX)**2+(p.y-startY)**2>49;};
 n.on(Node.EventType.TOUCH_START,(event:EventTouch)=>{
  const id=event.getID();if(n.activeInHierarchy===false||id===null||touchId!==null&&touchId!==id)return;
  const p=event.getUILocation();touchId=id;startX=p.x;startY=p.y;dragged=false;
  if(visual){Tween.stopAllByTarget(visual);visual.setScale(.96,.96,1);}
 });
 n.on(Node.EventType.TOUCH_MOVE,(event:EventTouch)=>{if(touchId!==null&&event.getID()===touchId&&beyondTap(event)){dragged=true;reset();}});
 n.on(Node.EventType.TOUCH_CANCEL,(event:EventTouch)=>{if(event.getID()===null||event.getID()===touchId){cancel();}});
 n.on(Node.EventType.TOUCH_END,(event:EventTouch)=>{
  if(touchId===null||event.getID()!==touchId)return;
  const activate=n.activeInHierarchy!==false&&!dragged&&!beyondTap(event);touchId=null;dragged=false;reset(!activate);
  if(activate)action();
 });
}
export function button(parent:Node,text:string,x:number,y:number,w:number,h:number,action:()=>void,fill=C.primary,foreground=C.ink,enabled=true):Node{
 const n=box(parent,'Button-'+text,x,y,w,h,fill,14,fill===C.paper?C.line:undefined);if(enabled&&fill===C.primary)skin(n,'button-yellow');if(!enabled)material(n,w,h,'#C5CCD5');label(n,text,0,0,22,foreground,w-12,true,'center');if(enabled)tap(n,action);return n;
}
export function icon(parent:Node,kind:string,x:number,y:number,fill=C.navy,scale=1):Node{
 const generated=['avatar','station','coin','star','bag','confirm','vehicle','bills','map','recruit','target','close'].indexOf(kind)>=0;
 const n=item(parent,'Icon-'+kind,x,y,32,32),g=n.addComponent(Graphics);n.setScale(scale,scale,1);g.lineWidth=2.4;g.strokeColor=col(fill);g.fillColor=col(fill);
 if(kind==='heart'){
  const heart=(scale:number,dy:number,color:string)=>{g.fillColor=col(color);g.moveTo(0,-14*scale+dy);g.bezierCurveTo(-30*scale,5*scale+dy,-12*scale,25*scale+dy,0,13*scale+dy);g.bezierCurveTo(12*scale,25*scale+dy,30*scale,5*scale+dy,0,-14*scale+dy);g.fill();};
  heart(1.06,-2,'#8E183C');heart(1,0,'#CB244D');heart(.91,2,'#EB3D67');heart(.75,5,'#FF6683');heart(.49,8,'#FF91A6');g.fillColor=col('#FFE9F1');g.ellipse(-7,10,4,2);g.fill();
 }
 else if(kind==='close'){g.lineWidth=4;g.moveTo(-9,-9);g.lineTo(9,9);g.moveTo(-9,9);g.lineTo(9,-9);g.stroke();}
 else if(kind==='target'){g.circle(0,0,9);g.stroke();g.circle(0,0,3);g.fill();for(const [a,b,c,d] of [[-15,0,-10,0],[10,0,15,0],[0,-15,0,-10],[0,10,0,15]]){g.moveTo(a,b);g.lineTo(c,d);g.stroke();}}
 else if(kind==='map'){g.moveTo(-13,-10);g.lineTo(-5,-6);g.lineTo(5,-10);g.lineTo(13,-6);g.lineTo(13,12);g.lineTo(5,8);g.lineTo(-5,12);g.lineTo(-13,8);g.close();g.stroke();for(const xx of [-5,5]){g.moveTo(xx,-6);g.lineTo(xx,8);g.stroke();}}
 else if(kind==='recruit'){g.circle(-4,8,6);g.fill();g.roundRect(-16,-14,24,14,6);g.fill();g.lineWidth=2;g.circle(12,0,7);g.stroke();g.moveTo(8,0);g.lineTo(16,0);g.moveTo(12,-4);g.lineTo(12,4);g.stroke();}
 else if(kind==='vehicle'){g.circle(-9,-8,5);g.stroke();g.circle(11,-8,5);g.stroke();g.moveTo(-9,-8);g.lineTo(-1,6);g.lineTo(7,-8);g.lineTo(-9,-8);g.moveTo(7,-8);g.lineTo(9,10);g.lineTo(15,10);g.moveTo(-5,6);g.lineTo(1,6);g.stroke();}
 else if(kind==='bills'){g.roundRect(-10,-14,20,28,2);g.stroke();for(const y of [7,0,-7]){g.moveTo(-6,y);g.lineTo(y===-7?3:6,y);g.stroke();}}
 else if(kind==='plus'||kind==='minus'){g.moveTo(-9,0);g.lineTo(9,0);g.stroke();if(kind==='plus'){g.moveTo(0,-9);g.lineTo(0,9);g.stroke();}}
 else if(kind==='sun'){g.circle(0,0,6);g.stroke();for(let i=0;i<8;i++){const a=i*Math.PI/4;g.moveTo(Math.cos(a)*10,Math.sin(a)*10);g.lineTo(Math.cos(a)*13,Math.sin(a)*13);g.stroke();}}
 else if(generated){g.circle(0,0,12);g.stroke();g.circle(0,0,5);g.fill();}
 if(generated){
  const picture=cartoonArt(parent,kind,x,y,48*scale,48*scale,n);
  if(fill==='#AAA69C')picture.getComponent(Sprite)!.grayscale=true;
  return picture;
 }
 return n;
}

export function closeButton(parent:Node,x:number,y:number,size:number,action:()=>void):Node{
 const n=box(parent,'CloseButton',x,y,size,size,'#DE4258',size/2,'#FFFFFF');icon(n,'close',0,0,'#FFFFFF',1);tap(n,action);return n;
}

export function roundAction(node:Node,size:number,enabled=true):void {
 const surface=item(node,'Surface'),g=surface.addComponent(Graphics),r=size/2;
 g.fillColor=col('#34373522');g.circle(0,-4,r);g.fill();
 g.fillColor=col(enabled?C.primary:'#AAA99F');g.circle(0,0,r-2);g.fill();
 g.strokeColor=col(enabled?'#DDB376':C.paper);g.lineWidth=1.5;g.circle(0,0,r-2);g.stroke();
 g.strokeColor=col('#FFE5AD99');g.lineWidth=1;g.circle(0,0,r-6);g.stroke();
}
export function topOnlyBar(node:Node,w:number,h:number):void {
 const g=item(node,'Surface').addComponent(Graphics);g.fillColor=col(C.paper);g.rect(-w/2,-h/2,w,h);g.fill();
 g.strokeColor=col(C.line);g.lineWidth=1;g.moveTo(-w/2,h/2);g.lineTo(w/2,h/2);g.stroke();
}
