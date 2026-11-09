import { Color, Graphics, isValid, Mask, Node, Rect, Size, Sprite, SpriteFrame, UITransform } from 'cc';
import { item, label } from './SampleUI';
import { vehicleSideArt } from './VehicleSideArt';
import { loadArtRegion } from './UIArtResources';

/** These two small product-only textures deliberately bypass the optional Web pack. */
function productImage(parent:Node,name:string,resource:string,w:number,h:number,fit:'cover'|'stretch'):Node {
 const n=item(parent,name,0,0,w,h),sprite=n.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;
 let owned:SpriteFrame|null=null;
 n.on(Node.EventType.NODE_DESTROYED,()=>{if(owned){owned.destroy();owned=null;}});
 loadArtRegion(resource,[0,0,1,1],{normalized:true,web:false}).then(region=>{
  if(!isValid(n,true))return;
  const [x,y,width,height]=region.rect;
  owned=new SpriteFrame();owned.texture=region.texture;owned.rect=new Rect(x,y,width,height);owned.originalSize=new Size(width,height);
  if(fit==='cover'){const scale=Math.max(w/width,h/height);n.getComponent(UITransform)!.setContentSize(width*scale,height*scale);}
  sprite.spriteFrame=owned;n.emit('ui-art-state','ready',resource);
 }).catch(error=>{if(isValid(n,true)){n.emit('ui-art-state','failed',resource);console.warn('[Vehicle product art fallback]',resource,error);}});
 return n;
}

/**
 * Independent native product scenery, never map art or a city-scene substitute.
 * Vehicle pixels, full native aspect and selected-model mapping stay unchanged.
 * The lightweight reusable contact shadow remains a visual candidate until inspected.
 */
export function vehicleProductPreview(parent:Node,modelId:number,x:number,y:number,w:number,h:number):Node {
 const viewport=item(parent,'VehicleProductPreview-'+modelId,x,y,w,h);
 viewport.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
 const surface=item(viewport,'NeutralProductSurface',0,0,w,h),g=surface.addComponent(Graphics);
 const rows=40;
 for(let i=0;i<rows;i++){
  const t=(i+.5)/rows;
  g.fillColor=new Color(Math.round(247-18*t),Math.round(251-14*t),Math.round(253-10*t));
  g.rect(-w/2,h/2-h*(i+1)/rows,w,h/rows+.1);g.fill();
 }
 const sceneState=label(viewport,'场景载入中',0,-h/2+13,12,'#5482AE',w-24,false,'center');
 sceneState.fontFamily='PingFang SC, Microsoft YaHei, sans-serif';
 const background=productImage(viewport,'ProductScenery','ui-v2/showcase/vehicle-product-background-v1',w,h,'cover');background.setSiblingIndex(1);
 background.on('ui-art-state',(state:string)=>{
  if(!isValid(sceneState,true))return;
  if(state==='ready'){surface.active=false;sceneState.node.active=false;}
  else if(state==='failed'){sceneState.string='场景图暂不可用';sceneState.node.active=true;}
 });
 const shadow=productImage(viewport,'VehicleContactShadow','ui-v2/showcase/vehicle-ground-shadow',w*.4,h*.12,'stretch');shadow.setSiblingIndex(2);shadow.active=false;
 const pending=label(viewport,'车型图片载入中',0,0,20,'#5482AE',w-24,false,'center');
 pending.fontFamily='PingFang SC, Microsoft YaHei, sans-serif';
 const picture=vehicleSideArt(viewport,modelId,0,0,w-16,h-16,pending.node);
 picture.on('ui-art-state',(state:string)=>{
  if(!isValid(pending,true))return;
  if(state==='ready'&&isValid(shadow,true)){
   const size=picture.getComponent(UITransform)!;
   shadow.setPosition(size.width*.04,-size.height*.41);shadow.getComponent(UITransform)!.setContentSize(size.width*.68,size.height*.16);shadow.angle=-9;shadow.active=true;
  }else if(state==='failed'){if(isValid(shadow,true))shadow.active=false;pending.string='车型图片未载入，请重新打开本页';pending.node.active=true;}
 });
 return viewport;
}
