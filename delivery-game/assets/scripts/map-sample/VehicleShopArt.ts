import { Color, isValid, Mask, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';
import { item } from './SampleUI';

const root='map-sample/anime/vehicle-shop-20261101/';
const frames=new Map<string,Promise<SpriteFrame>>();
function frame(name:string):Promise<SpriteFrame> {
 const old=frames.get(name);if(old)return old;
 const pending=new Promise<SpriteFrame>((resolve,reject)=>resources.load(root+name+'/texture',Texture2D,(error,texture)=>{
  if(error){reject(error);return;}
  const f=new SpriteFrame();f.texture=texture;
  if(name==='metal-panel'){
   f.rect=new Rect(40,137,2093,433);f.originalSize=new Size(2093,433);
   f.insetLeft=145;f.insetRight=145;f.insetTop=90;f.insetBottom=90;
  }
  if(name==='card-frame'){
   f.rect=new Rect(23,35,1077,1332);f.originalSize=new Size(1077,1332);
   f.insetLeft=120;f.insetRight=120;f.insetTop=120;f.insetBottom=120;
  }
  if(name==='metal-grade-badge'){
   f.rect=new Rect(76,110,1102,1036);f.originalSize=new Size(1102,1036);
  }
  if(name==='primary-amber-button'){
   f.rect=new Rect(59,161,2054,394);f.originalSize=new Size(2054,394);
   f.insetLeft=145;f.insetRight=145;f.insetTop=100;f.insetBottom=100;
  }
  f.addRef();resolve(f);
 }));
 frames.set(name,pending);pending.catch(()=>{if(frames.get(name)===pending)frames.delete(name);});return pending;
}
/** Display the environment with an aspect-preserving centered cover crop. */
export function shopBackground(parent:Node,width:number,height:number):void {
 const clip=item(parent,'ShopEnvironment',0,0,width,height);clip.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
 const picture=item(clip,'EnvironmentImage',0,0,width,height),sprite=picture.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;
 frame('garage-clean-background').then(f=>{
  if(!isValid(clip,true)||!isValid(picture,true))return;
  const scale=Math.max(width/f.originalSize.width,height/f.originalSize.height);
  picture.getComponent(UITransform)!.setContentSize(f.originalSize.width*scale,f.originalSize.height*scale);sprite.spriteFrame=f;
 },()=>{});
}
/** Nine-slice keeps the original frame corners while the center adapts to each control. */
export function shopPanel(parent:Node,width:number,height:number,name='metal-panel'):void {
 const scale=.2,picture=item(parent,'ShopMetalSkin',0,0,width/scale,height/scale);picture.setScale(scale,scale,1);
 picture.setSiblingIndex(Math.min(1,parent.children.length-1));
 const sprite=picture.addComponent(Sprite);sprite.type=Sprite.Type.SLICED;sprite.sizeMode=Sprite.SizeMode.CUSTOM;
 frame(name).then(f=>{if(isValid(parent,true)&&isValid(picture,true))sprite.spriteFrame=f;},()=>{});
}

/** Shared metal grade blank; grade colors are presentation only. */
export function shopGradeMetal(parent:Node,width:number,height:number,tint:Color):void {
 const picture=item(parent,'GradeMetal',0,0,width,height),sprite=picture.addComponent(Sprite);
 sprite.sizeMode=Sprite.SizeMode.CUSTOM;sprite.color=tint;
 frame('metal-grade-badge').then(f=>{
  if(!isValid(parent,true)||!isValid(picture,true))return;
  const scale=Math.min(width/f.originalSize.width,height/f.originalSize.height);
  picture.getComponent(UITransform)!.setContentSize(f.originalSize.width*scale,f.originalSize.height*scale);sprite.spriteFrame=f;
 },()=>{});
}
