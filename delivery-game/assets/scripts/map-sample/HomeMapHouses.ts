import { isValid, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';
import { HousePlacement } from './HomeMapArt';
import { item } from './SampleUI';
const assets=[
 {path:'T01-restaurant-tile-original',rect:[60,288,1133,678],width:18,height:11},
 {path:'T02-restaurant-flat-original',rect:[139,298,980,672],width:15,height:9},
 {path:'T03-home-low-original',rect:[158,258,948,770],width:16,height:14},
];
const frames=new Map<number,Promise<SpriteFrame>>();
function load(variant:number):Promise<SpriteFrame>{
 const old=frames.get(variant);if(old)return old;const spec=assets[variant];
 const pending=new Promise<SpriteFrame>((resolve,reject)=>resources.load('map-sample/anime/existing-20261031/'+spec.path+'/texture',Texture2D,(err,asset)=>{
  if(err){reject(err);return;}const f=new SpriteFrame();f.texture=asset;f.rect=new Rect(spec.rect[0],spec.rect[1],spec.rect[2],spec.rect[3]);f.originalSize=new Size(spec.rect[2],spec.rect[3]);f.addRef();resolve(f);
 }));frames.set(variant,pending);pending.catch(()=>{if(frames.get(variant)===pending)frames.delete(variant);});return pending;
}
/** Full module images are used only on protected empty land, never as real-building geometry. */
export class HomeMapHouses {
 readonly node:Node;
 private readonly active=new Map<string,Node>();
 constructor(parent:Node){this.node=item(parent,'StreetHouses');}
 sync(houses:HousePlacement[],left:number,bottom:number,right:number,top:number,scale:number):void{
  const cx=(left+right)/2,cy=(bottom+top)/2;
  const selected=scale<.8?[]:houses.filter(v=>v.point[0]>=left-20&&v.point[0]<=right+20&&v.point[1]>=bottom-20&&v.point[1]<=top+20)
   .sort((a,b)=>Math.hypot(a.point[0]-cx,a.point[1]-cy)-Math.hypot(b.point[0]-cx,b.point[1]-cy)).slice(0,40);
  const wanted=new Set(selected.map(h=>h.id));
  for(const [id,node] of this.active)if(!wanted.has(id)){node.active=false;node.destroy();this.active.delete(id);}
  for(const house of selected){
   if(this.active.has(house.id))continue;const spec=assets[house.variant];
   const picture=item(this.node,'House-'+house.id,house.point[0],house.point[1],spec.width,spec.height),sprite=picture.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;
   load(house.variant).then(f=>{
    if(!isValid(picture,true))return;const scale=Math.min(spec.width/f.originalSize.width,spec.height/f.originalSize.height);
    picture.getComponent(UITransform)!.setContentSize(f.originalSize.width*scale,f.originalSize.height*scale);sprite.spriteFrame=f;
   },()=>{/* Native courtyard and roof remain as fallback. */});
   this.active.set(house.id,picture);
  }
 }
}
