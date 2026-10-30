import { isValid, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';
import { item } from './SampleUI';
const images=new Map<string,Promise<SpriteFrame>>();
function load(resource:string):Promise<SpriteFrame>{
 const cached=images.get(resource);if(cached)return cached;
 const pending=new Promise<SpriteFrame>((resolve,reject)=>resources.load(resource+'/texture',Texture2D,(error,texture)=>{
  if(error){reject(error);return;}texture.addRef();const frame=new SpriteFrame();frame.texture=texture;
  frame.rect=new Rect(0,0,texture.width,texture.height);frame.originalSize=new Size(texture.width,texture.height);frame.addRef();resolve(frame);
 }));
 images.set(resource,pending);pending.catch(()=>images.delete(resource));return pending;
}
// Each immutable picture belongs to one dialog. Cocos strict validity also rejects queued destruction.
export function vehicleSideArt(parent:Node,tier:number,x:number,y:number,width:number,height:number,fallback:Node):Node {
 const picture=item(parent,'VehicleSideView',x,y,width,height);picture.active=false;
 const sprite=picture.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;
 load('map-sample/vehicles/'+(tier===2?'side-d-plus':'side-d')).then(frame=>{
  if(!isValid(parent,true)||!isValid(picture,true)||parent.activeInHierarchy===false)return;
  const scale=Math.min(width/frame.originalSize.width,height/frame.originalSize.height);
  picture.getComponent(UITransform)!.setContentSize(frame.originalSize.width*scale,frame.originalSize.height*scale);
  sprite.spriteFrame=frame;picture.active=true;if(isValid(fallback,true))fallback.active=false;
 },()=>{/* The named, readable fallback remains visible; failed resources may be retried. */});return picture;
}
