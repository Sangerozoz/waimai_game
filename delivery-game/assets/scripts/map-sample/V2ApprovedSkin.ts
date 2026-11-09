import { Graphics, isValid, Label, Mask, Node, Rect, Sprite, SpriteFrame, UIOpacity, UITransform } from 'cc';
import { col, item, label as baseLabel, tap } from './SampleUI';
import { loadCartoonFrame, cartoonArt } from './CartoonArt';
import { V2_SPACE as S } from './V2Spacing';
import { imageSkin } from './V2ImageSkin';
function label(...args:Parameters<typeof baseLabel>){const l=baseLabel(...args);l.fontFamily='PingFang SC, Microsoft YaHei, sans-serif';l.lineHeight=(args[4]??20)*S.lineHeight;return l;}
export const UI={ink:'#061344',blue:'#087FFF',line:'#79CEFF',paper:'#EFFAFF',orange:'#FF7808',muted:'#5482AE'};
/** Clip native skin spill at the component contour; never stretch its dirty outer pixels into a border. */
function skinSurface(node:Node,key:string,onReady:()=>void,radius=8,opacity=255):void {
 const {width:w,height:h}=node.getComponent(UITransform)!;
 const viewport=item(node,'SkinViewport-'+key,0,0,w,h);viewport.setSiblingIndex(0);if(opacity<255)viewport.addComponent(UIOpacity).opacity=opacity;
 viewport.addComponent(Mask).type=Mask.Type.GRAPHICS_STENCIL;
 const stencil=viewport.getComponent(Graphics)!;stencil.clear();stencil.fillColor=col('#FFFFFF');
 stencil.roundRect(-w/2,-h/2,w,h,Math.min(radius,w/2,h/2));stencil.fill();
 imageSkin(viewport,key,onReady);
}
// Local V2 chrome: leaves the historical sample's global palette untouched.
export function panel(parent:Node,name:string,x:number,y:number,w:number,h:number,fill='#E5F6FF',stroke=UI.line):Node {
 const n=item(parent,name,x,y,w,h),g=n.addComponent(Graphics),r=Math.min(12,h/3,w/3);
 g.fillColor=col(fill);g.roundRect(-w/2,-h/2,w,h,r);g.fill();
 g.strokeColor=col(stroke);g.lineWidth=1.4;g.roundRect(-w/2,-h/2,w,h,r);g.stroke();
 g.strokeColor=col('#FFFFFF');g.lineWidth=1;g.moveTo(-w/2+r,h/2-2);g.lineTo(w/2-r,h/2-2);g.stroke();
 const key=/^(TodayMetric-|TotalMetric-)/.test(name)?'bill-metric':name==='XPTrack'?'xp-track':name==='XP'||name==='XPFill'?'xp-fill':name==='LevelBadge'?'level-badge':name.startsWith('V2Action-')?null:name==='PageBackground'?'page-paper':name.startsWith('Navigation-')?(fill==='#FFF1B1'?'nav-selected':'nav-tile'):/HUD$|RiderCount/.test(name)?'hud-shell':/XP/.test(name)||h<25?null:/^(Rider-|Vehicle-|VehicleDetails|Order-|SpecialOffer|ProgressTarget|Today|SevenDayChart|Cumulative|ExpenseCategories|TotalMetric-|PortraitFrame|Map-)/.test(name)?'panel-glass':null;
 if(key)skinSurface(n,key,()=>{g.enabled=false;
  if(key==='bill-metric'||(key==='panel-glass'&&stroke!==UI.line)){const edge=item(n,'GlassEdge',0,0,w,h),outline=edge.addComponent(Graphics);outline.strokeColor=col(stroke);outline.lineWidth=stroke==='#FF9600'||stroke==='#FF8A00'?2.4:1.8;outline.roundRect(-w/2+.4,-h/2+.4,w-.8,h-.8,Math.min(8,h/3,w/3));outline.stroke();edge.setSiblingIndex(1);}
 },8,fill.length===9?parseInt(fill.slice(7,9),16):255);return n;
}

/** Image tile clipped at the central lower corner, following the approved four-tab bar. */
export function navigationTile(parent:Node,name:string,x:number,y:number,w:number,h:number,current:boolean,inner:'left'|'right'|null):Node {
 const n=item(parent,name,x,y,w,h),mask=n.addComponent(Mask);mask.type=Mask.Type.GRAPHICS_STENCIL;
 const g=n.getComponent(Graphics)!;g.clear();
 const hw=w/2,hh=h/2,cut=inner?58:0;
 g.moveTo(-hw,hh);g.lineTo(hw,hh);g.lineTo(hw,-hh+(inner==='right'?cut:0));
 if(inner==='right')g.lineTo(hw-cut,-hh);
 g.lineTo(-hw+(inner==='left'?cut:0),-hh);
 if(inner==='left')g.lineTo(-hw,-hh+cut);
 g.close();g.fill();
 panel(n,name+'Face',0,0,w,h,current?'#FFF1B1':'#D6F0FF',current?'#FFB73B':UI.blue);
 return n;
}

export function action(parent:Node,text:string,x:number,y:number,w:number,h:number,fn:()=>void,enabled=true,primary=true):Node {
 const n=panel(parent,'V2Action-'+text,x,y,w,h,enabled?(primary?'#FF8314':'#C9EDFF'):'#C6D7E5',enabled?(primary?'#FFAC38':UI.blue):'#9FB7CA');
 // No disabled skin is registered; keep the existing gray chrome and disabled hit target.
 if(enabled)skinSurface(n,primary?'button-orange':'button-blue',()=>{const g=n.getComponent(Graphics);if(g)g.enabled=false;});
 label(n,text,0,0,Math.min(25,h*.58),enabled&&primary?'#FFFFFF':UI.ink,w-10,true,'center');if(enabled)tap(n,fn);return n;
}
export function glyph(parent:Node,kind:string,x:number,y:number,size=46):void {
 const opticalSize=kind==='vehicles'?size*1.18:size;
 const n=item(parent,'NavIcon-'+kind,x,y,opticalSize,opticalSize);
 // Temporary existing PNG art is explicit candidate fallback; no coarse hand-drawn icons.
 const fallback=item(n,'CandidateIcon',0,0,size,size);
 if(kind==='close')label(fallback,'×',0,0,size*1.25,UI.ink,size*1.3,true,'center');
 else if(kind==='plus')label(fallback,'+',0,0,size,UI.blue,size,true,'center');
 else if(kind==='energy')label(fallback,'ϟ',0,0,size,'#16A777',size,true,'center');
 else if(['clock','speed','capacity','income','expense','profit','trophy','cart','wrench','road','refresh','pickup','dropoff'].includes(kind))label(fallback,({clock:'时',speed:'速',capacity:'重',income:'收',expense:'支',profit:'净',trophy:'奖',cart:'购',wrench:'修',road:'路',refresh:'↻',pickup:'取',dropoff:'送'} as Record<string,string>)[kind],0,0,size*.65,UI.blue,size,true,'center');
 else {
  // Caller-specific fallback aliases, not an asset-registry query. Never send an unknown kind through.
  const aliases:Record<string,[string,string]>={riders:['recruit','骑'],vehicles:['vehicle','车'],maps:['map','图'],bills:['bills','账'],coin:['coin','币'],'coin-stack':['coin','币'],heart:['heart','心'],target:['target','定'],pin:['map','位'],'pickup-pin':['map','取'],'delivery-pin':['map','送']};
  const art=Object.prototype.hasOwnProperty.call(aliases,kind)?aliases[kind]:undefined;
  const pending=label(fallback,art?.[1]||'?',0,0,size*.65,UI.blue,size,true,'center');
  if(art)cartoonArt(fallback,art[0],0,0,size,size,pending.node);
 }
 imageSkin(n,'icon-'+kind,()=>{fallback.active=false;});
}
export function mainAction(parent:Node,text:string,x:number,y:number,fn:()=>void):void {
 const n=item(parent,'V2MainAction',x,y,146,146),g=n.addComponent(Graphics);
 for(const [r,c] of [[61,'#FF7816'],[58,'#FFFFFF'],[55,'#FF8B17'],[51,'#FF7705']] as [number,string][]){g.fillColor=col(c);g.circle(0,0,r);g.fill();}
 g.strokeColor=col('#FFD68B');g.lineWidth=2;g.circle(0,0,52);g.stroke();imageSkin(n,'dispatch-disc',()=>{g.enabled=false;});// Close glyph in the supplied photo sits ~20px below the disc center at ~210px diameter.
 // +12 design units compensates that visible-ink offset; the disc and hit target stay fixed.
 label(n,text,0,text==='×'?12:4,text==='×'?72:43,'#FFFFFF',112,true,'center');tap(n,fn);
}
/** Cover crop within its own viewport; used only for existing art, never screenshot UI. */
export function artCrop(parent:Node,key:string,x:number,y:number,w:number,h:number,crop?:[number,number,number,number]):Node {
 const n=item(parent,'V2Art-'+key,x,y,w,h);n.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
 const placeholder=label(n,'图片载入中',0,0,16,UI.muted,w-8,false,'center');
 const picture=item(n,'Picture',0,0,w,h),sp=picture.addComponent(Sprite);sp.sizeMode=Sprite.SizeMode.CUSTOM;let ownedFrame:SpriteFrame|null=null;
 n.on(Node.EventType.NODE_DESTROYED,()=>{if(ownedFrame){ownedFrame.destroy();ownedFrame=null;}});
 loadCartoonFrame(key).then(source=>{if(!isValid(n,true)||!isValid(picture,true))return;let frame=source;
  if(crop){frame=new SpriteFrame();ownedFrame=frame;frame.texture=source.texture;const r=source.rect;frame.rect=new Rect(r.x+r.width*crop[0],r.y+r.height*crop[1],r.width*crop[2],r.height*crop[3]);}
  const scale=Math.max(w/frame.rect.width,h/frame.rect.height);picture.getComponent(UITransform)!.setContentSize(frame.rect.width*scale,frame.rect.height*scale);sp.spriteFrame=frame;placeholder.node.active=false;
 }).catch(()=>{if(isValid(placeholder,true))placeholder.string='图片暂不可用';});return n;
}
export function levelBadge(parent:Node,text:string,x:number,y:number,w=55,h=27):void {
 const n=panel(parent,'LevelBadge',x,y,w,h,UI.blue,UI.blue);label(n,text,0,0,18,'#FFFFFF',w-4,true,'center');
}
export function statusBadge(parent:Node,text:string,x:number,y:number,active=false,w=72,h=27):Label {
 const n=panel(parent,'StatusBadge',x,y,w,h,active?UI.blue:'#70869D',active?UI.blue:'#70869D');
 skinSurface(n,active?'status-blue':'status-gray',()=>{const g=n.getComponent(Graphics);if(g)g.enabled=false;},h/2);
 return label(n,text,0,0,Math.min(23,h*.67),'#FFFFFF',w-4,true,'center');
}
export function checkbox(parent:Node,chosen:boolean,x:number,y:number):void {
 const n=panel(parent,'SelectOrder',x,y,36,36,chosen?'#FF8C0A':'#FFFFFF',chosen?'#FF9600':UI.muted);
 const fallback=label(n,chosen?'✓':'',0,0,27,'#FFFFFF',32,true,'center');imageSkin(n,chosen?'checkbox-checked':'checkbox-unchecked',()=>{const g=n.getComponent(Graphics);if(g)g.enabled=false;fallback.node.active=false;});
}
export function portrait(parent:Node,index:number,x:number,y:number,w:number,h:number):void {
 const border=item(parent,'PortraitFrame',x,y,w+4,h+4);
 if(index===0)artCrop(parent,'avatar',x,y,w,h);
 else {
  const n=item(parent,'Portrait-npc-'+index,x,y,w,h);n.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
  const fallback=item(n,'PortraitPending',0,0,w,h);
  const state=label(fallback,'头像载入中',0,12,13,UI.muted,w,true,'center');
  label(fallback,String(index).padStart(2,'0'),0,-12,16,UI.muted,w,true,'center');
  n.on('ui-art-state',(status:string)=>{if(status==='failed'&&isValid(state,true))state.string='头像未载入';});
  imageSkin(n,'npc-'+index,()=>{fallback.active=false;},'portraits','cover');
 }
 // U12 has a transparent center. Overlay its frame, never fill the portrait with it.
 border.setSiblingIndex(parent.children.length-1);imageSkin(border,'portrait-frame');
}

/** New street-view art only; names, ownership, prices and buttons stay in V2GameUI. */
export function mapPreview(parent:Node,id:number,x:number,y:number,w:number,h:number):void {
 const n=item(parent,'MapPreview-'+id,x,y,w,h);n.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
 const pending=label(n,'地图插图载入中',0,0,20,UI.ink,w-24,false,'center');
 n.on('ui-art-state',(status:string)=>{if(!isValid(pending,true))return;if(status==='failed'){pending.string='地图插图未载入，请重新打开本页';pending.node.active=true;}});
 imageSkin(n,String(id),()=>{pending.node.active=false;},'maps','cover');
}
