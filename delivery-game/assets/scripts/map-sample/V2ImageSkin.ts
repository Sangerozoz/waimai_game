import { isValid, Node, Rect, Size, Sprite, SpriteFrame, UITransform } from 'cc';
import { item } from './SampleUI';
import { loadArtJson, loadArtRegion } from './UIArtResources';

/** All rectangles/insets use native PNG pixels, with a top-left origin. */
export interface ImageSkinAsset {
 resource:string;
 rect:[number,number,number,number];
 inset?:{left:number;right:number;top:number;bottom:number};
 status:'candidate'|'usable'|'rejected';
 displayName?:string;
 source?:string;
 sha256?:string;
}
interface ImageSkinManifest {version:number;assets:Record<string,ImageSkinAsset>}
const manifests=new Map<string,Promise<ImageSkinManifest>>();
const warnings=new Set<string>();
function warn(key:string,reason:string):void {
 if(warnings.has(key))return;warnings.add(key);
 console.warn(`[V2 image skin candidate fallback] ${key}: ${reason}`);
}
function loadManifest(name:string):Promise<ImageSkinManifest> {
 const cached=manifests.get(name);if(cached)return cached;
 const pending=loadArtJson('ui-v2/'+name).then(value=>{
  const data=value.json as ImageSkinManifest;
  if(!data||data.version!==1||!data.assets)throw new Error('unsupported skin manifest: '+name);
  return data;
 });
 manifests.set(name,pending);
 void pending.catch(()=>{if(manifests.get(name)===pending)manifests.delete(name);});
 return pending;
}
/** Decoration only. The fallback and all dynamic text/hit targets stay live until load succeeds. */
export function imageSkin(node:Node,key:string,onReady?:()=>void,manifestName='manifest',fit:'stretch'|'contain'|'cover'='stretch'):void {
 let frame:SpriteFrame|null=null;
 let picture:Node|null=null;
 node.emit('ui-art-state','loading',manifestName+'/'+key);
 node.on(Node.EventType.NODE_DESTROYED,()=>{if(frame){frame.destroy();frame=null;}});
 loadManifest(manifestName).then(async data=>{
  if(!isValid(node,true))return;
  const asset=data.assets[key];
  if(!asset||asset.status==='rejected')throw new Error('no usable native asset');
  const region=await loadArtRegion(asset.resource,asset.rect,{inset:asset.inset,web:manifestName!=='maps'}),texture=region.texture;
  if(!isValid(node,true))return;
  const [x,y,w,h]=region.rect;
  if(![x,y,w,h].every(Number.isFinite)||x<0||y<0||w<=0||h<=0||x+w>texture.width||y+h>texture.height)throw new Error('native rectangle outside texture');
  const insets=region.inset;
  if(insets&&(!Object.values(insets).every(v=>Number.isFinite(v)&&v>=0)||insets.left+insets.right>w||insets.top+insets.bottom>h))throw new Error('invalid native slice insets');
  frame=new SpriteFrame();frame.texture=texture;frame.rect=new Rect(x,y,w,h);frame.originalSize=new Size(w,h);
  if(insets){frame.insetLeft=insets.left;frame.insetRight=insets.right;frame.insetTop=insets.top;frame.insetBottom=insets.bottom;}
  const size=node.getComponent(UITransform)!;
  let drawWidth=size.width,drawHeight=size.height,drawScale=1;
  if(insets){
   // Native 60px slice corners must not become 60 logical pixels on a small card.
   drawScale=Math.min(1,size.width/w,size.height/h,12/Math.max(1,...Object.values(insets)));
   drawWidth/=drawScale;drawHeight/=drawScale;
  }else if(fit!=='stretch'||key.startsWith('icon-')){const scale=fit==='cover'?Math.max(size.width/w,size.height/h):Math.min(size.width/w,size.height/h);drawWidth=w*scale;drawHeight=h*scale;}
  picture=item(node,'ImageSkin-'+key,0,0,drawWidth,drawHeight);picture.setScale(drawScale,drawScale,1);picture.setSiblingIndex(0);
  const sprite=picture.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;sprite.type=insets?Sprite.Type.SLICED:Sprite.Type.SIMPLE;sprite.spriteFrame=frame;
  node.emit('ui-art-state','ready',manifestName+'/'+key);
  onReady?.();
 }).catch(error=>{if(isValid(node,true)){node.emit('ui-art-state','failed',manifestName+'/'+key,String(error));warn(manifestName+'/'+key,String(error));}});
}
export async function portraitDisplayName(id:string):Promise<string|undefined> {
 try{return (await loadManifest('portraits')).assets[id]?.displayName;}catch(error){warn('portraits/names',String(error));return undefined;}
}
/** 940×1673 approved master to the 720×1280 Cocos design canvas. */
export const master={
 x:(x:number)=>(x-470)*720/940,
 y:(y:number)=>(836.5-y)*1280/1673,
 w:(w:number)=>w*720/940,
 h:(h:number)=>h*1280/1673,
};
