import { isValid, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D } from 'cc';
import { foodForOffer } from './FoodCatalog';
import { box, C, item, label } from './SampleUI';

// One shared texture and at most sixteen frames, reused by every phone opening.
let atlas:Promise<Texture2D>|null=null;
const frames=new Map<number,SpriteFrame>();
function loadAtlas():Promise<Texture2D> {
  if(!atlas)atlas=new Promise<Texture2D>((resolve,reject)=>{
    resources.load('map-sample/food-atlas-v1/texture',Texture2D,(error,texture)=>{
      if(error){atlas=null;reject(error);return;}
      texture.addRef();resolve(texture);
    });
  });
  return atlas;
}
function frameFor(texture:Texture2D,index:number):SpriteFrame {
  const cached=frames.get(index);if(cached)return cached;
  const column=index%4,row=Math.floor(index/4);
  const x=Math.round(column*texture.width/4),y=Math.round(row*texture.height/4);
  const right=Math.round((column+1)*texture.width/4),bottom=Math.round((row+1)*texture.height/4);
  const frame=new SpriteFrame();frame.texture=texture;frame.rect=new Rect(x,y,right-x,bottom-y);frame.originalSize=new Size(right-x,bottom-y);
  frame.addRef();frames.set(index,frame);return frame;
}
export function foodImage(parent:Node,food:string,x:number,y:number,size:number):Node {
  const node=box(parent,'FoodImage',x,y,size,size,'#F6F0E3',9);
  const fallback=label(node,'餐图加载中',0,0,14,C.muted,size-8,false,'center');
  const alive=()=>isValid(node,true)&&node.activeInHierarchy;
  loadAtlas().then(texture=>{
    if(!alive())return;
    const picture=item(node,'FoodPhoto',0,0,size,size),sprite=picture.addComponent(Sprite);
    sprite.sizeMode=Sprite.SizeMode.CUSTOM;sprite.spriteFrame=frameFor(texture,foodForOffer(food).imageIndex);
    fallback.node.destroy();
  }).catch(()=>{if(alive())fallback.string='餐图暂不可用';});
  return node;
}
