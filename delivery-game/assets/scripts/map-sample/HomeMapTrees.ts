import { isValid, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';
import { TreePlacement } from './HomeMapArt';
import { item } from './SampleUI';
const cache=new Map<string,Promise<SpriteFrame>>();
function frame(name:string):Promise<SpriteFrame>{
 const found=cache.get(name);if(found)return found;
 const pending=new Promise<SpriteFrame>((resolve,reject)=>resources.load('map-sample/anime/home-map-20261101/'+name+'/texture',Texture2D,(err,asset)=>{
  if(err){reject(err);return;}const f=new SpriteFrame();f.texture=asset;
  const rect=name==='HE01-tree-green'?[29,62,1205,1158]:[81,98,1104,1079];
  f.rect=new Rect(rect[0],rect[1],rect[2],rect[3]);f.originalSize=new Size(rect[2],rect[3]);f.addRef();resolve(f);
 }));cache.set(name,pending);pending.catch(()=>{if(cache.get(name)===pending)cache.delete(name);});return pending;
}
/** Visible-only sprite budget; source positions are fixed and no per-tree mask is used. */
export class HomeMapTrees {
 readonly node:Node;
 private readonly active=new Map<string,Node>();
 constructor(parent:Node){this.node=item(parent,'StreetTrees');}
 sync(trees:TreePlacement[],left:number,bottom:number,right:number,top:number,scale:number):void{
  const cx=(left+right)/2,cy=(bottom+top)/2;
  const selected=scale<.8?[]:trees.filter(v=>v.point[0]>=left-12&&v.point[0]<=right+12&&v.point[1]>=bottom-12&&v.point[1]<=top+12)
   .sort((a,b)=>Math.hypot(a.point[0]-cx,a.point[1]-cy)-Math.hypot(b.point[0]-cx,b.point[1]-cy)).slice(0,100);
  const wanted=new Set(selected.map(t=>t.id));
  for(const [key,node] of this.active)if(!wanted.has(key)){node.active=false;node.destroy();this.active.delete(key);}
  for(const tree of selected){
   if(this.active.has(tree.id))continue;
   const picture=item(this.node,'Tree-'+tree.id,tree.point[0],tree.point[1],tree.diameter,tree.diameter),sprite=picture.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;
   frame(tree.warm?'HE02-tree-warm':'HE01-tree-green').then(f=>{
    if(!isValid(picture,true))return;const scale=tree.diameter/Math.max(f.originalSize.width,f.originalSize.height);
    picture.getComponent(UITransform)!.setContentSize(f.originalSize.width*scale,f.originalSize.height*scale);sprite.spriteFrame=f;
   },()=>{/* Graphics fallback is drawn in the same tile. */});
   this.active.set(tree.id,picture);
  }
 }
}
