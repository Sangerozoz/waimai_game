import { Graphics, isValid, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D } from 'cc';
import { item } from './SampleUI';
import { vehicleArtForTier } from './VehicleCatalog';
import { loadCartoonFrame } from './CartoonArt';

// Share the current vehicle image across map layout rebuilds; load other grades only when used.
const images=new Map<string,Promise<SpriteFrame>>();
function loadImage(resource:string):Promise<SpriteFrame> {
  const cached=images.get(resource);if(cached)return cached;
  const loading=new Promise<SpriteFrame>((resolve,reject)=>{
    resources.load(resource+'/texture',Texture2D,(error,texture)=>{
      if(error){reject(error);return;}
      texture.addRef();
      const frame=new SpriteFrame();frame.texture=texture;
      frame.rect=new Rect(0,0,texture.width,texture.height);frame.originalSize=new Size(texture.width,texture.height);
      frame.addRef();resolve(frame);
    });
  });
  images.set(resource,loading);loading.catch(()=>images.delete(resource));return loading;
}

export class MapVehicle {
  private readonly picture:Node;
  private readonly sprite:Sprite;
  private tier=0;
  private request=0;
  constructor(private readonly parent:Node,private readonly fallback:Graphics){
    this.picture=item(parent,'VehicleTopView',0,0,80,128);
    // Source art faces north; route angles use east as zero.
    this.picture.angle=-90;this.picture.active=false;
    this.sprite=this.picture.addComponent(Sprite);this.sprite.sizeMode=Sprite.SizeMode.CUSTOM;
  }
  setTier(tier:number):void {
    const art=vehicleArtForTier(tier);if(this.tier===art.tier)return;
    this.tier=art.tier;const request=++this.request;
    this.picture.active=false;this.fallback.enabled=true;
    const current=()=>request===this.request&&isValid(this.parent,true)&&isValid(this.picture,true)&&this.parent.activeInHierarchy!==false;
    (art.tier<=2?loadCartoonFrame(art.tier===2?'top-d-plus':'top-d'):loadImage(art.resource)).then(frame=>{
      if(!current())return;
      this.sprite.spriteFrame=frame;this.picture.active=true;this.fallback.enabled=false;
    },()=>{if(current())this.tier=0;});
  }
}
