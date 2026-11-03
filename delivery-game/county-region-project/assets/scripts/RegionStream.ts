import { ImageAsset, Node, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';
import { AtlasModel, Bounds, ImageSpec, Region } from './AtlasModel';
export type NativeSprite={node:Node;dispose:()=>void};
export async function nativeSprite(spec:ImageSpec,parent:Node,w:number,h:number,anchor:[number,number],signal:AbortSignal,ownership?:[number,number][]):Promise<NativeSprite>{
 if(spec.file.startsWith('/')||spec.file.split('/').includes('..'))throw Error('Invalid local asset path');
 const response=await fetch('assets/'+spec.file,{signal});if(!response.ok)throw Error('Missing '+spec.file);const bytes=await response.arrayBuffer();const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(b=>b.toString(16).padStart(2,'0')).join('');if(digest!==spec.sha256)throw Error('SHA mismatch '+spec.file);
 const url=URL.createObjectURL(new Blob([bytes]));let im:HTMLImageElement;try{im=await new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(Error('Cannot decode '+spec.file));image.src=url;});}finally{URL.revokeObjectURL(url);}
 if(signal.aborted)throw Error('Cancelled');if(im.naturalWidth!==spec.nativeSize[0]||im.naturalHeight!==spec.nativeSize[1])throw Error('Native size mismatch '+spec.file);
 let source:HTMLImageElement|HTMLCanvasElement=im;
 if(ownership){const canvas=document.createElement('canvas');canvas.width=im.naturalWidth;canvas.height=im.naturalHeight;const c=canvas.getContext('2d');if(!c)throw Error('Ownership clipping unavailable');c.beginPath();ownership.forEach((p,i)=>i?c.lineTo(p[0]*canvas.width,p[1]*canvas.height):c.moveTo(p[0]*canvas.width,p[1]*canvas.height));c.closePath();c.clip();c.drawImage(im,0,0);source=canvas;}
 const image=new ImageAsset(source),texture=new Texture2D();texture.image=image;const frame=new SpriteFrame();frame.texture=texture;const node=new Node(spec.file);parent.addChild(node);const ui=node.addComponent(UITransform);ui.setAnchorPoint(anchor[0],1-anchor[1]);ui.setContentSize(w,h);const sprite=node.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;sprite.spriteFrame=frame;
 return {node,dispose:()=>{node.destroy();frame.destroy();texture.destroy();image.destroy();}};
}
const intersects=(a:Bounds,b:Bounds)=>a.minX<=b.maxX&&a.maxX>=b.minX&&a.minY<=b.maxY&&a.maxY>=b.minY;
export class RegionStream {
 private live=new Map<string,{sprite:NativeSprite;lastSeen:number}>();private pending=new Set<string>();private failures=new Map<string,string>();private desired:Region[]=[];private controller=new AbortController();private stopped=false;private clock=0;private overview:NativeSprite|null=null;private nativeMode=false;
 constructor(private model:AtlasModel,private parent:Node,overview:NativeSprite|null=null){this.overview=overview;if(overview)this.parent.active=false;}

 update(bounds:Bounds,dt:number,screenPixelsPerUnit:number):void{
  this.clock+=dt;const center=[(bounds.minX+bounds.maxX)/2,(bounds.minY+bounds.maxY)/2];const distance=(r:Region)=>{const b=this.model.imageBounds(r);return Math.hypot((b.minX+b.maxX)/2-center[0],(b.minY+b.maxY)/2-center[1]);};
  const candidates=this.model.atlas.regions.filter(r=>intersects(this.model.imageBounds(r),bounds)).sort((a,b)=>distance(a)-distance(b));
  const lod=this.model.atlas.displayLOD;
  const near=!lod||screenPixelsPerUnit>=lod.pixelsPerUnit;
  // A full-viewport substitution, never partial native overlays over a flattened overview.
  this.desired=near&&candidates.length<=24?candidates:[];

  const wanted=new Set(this.desired.map(r=>r.id));for(const [id,item] of this.live){if(wanted.has(id))item.lastSeen=this.clock;else if(this.clock-item.lastSeen>(this.model.atlas.streaming?.releaseDelaySeconds??3)){item.sprite.dispose();this.live.delete(id);}}
  // Reclaim stale viewport assets before loading replacements; cap native residents + pending at 24.
  for(const [id,item] of this.live){if(this.live.size+this.pending.size<24)break;if(!wanted.has(id)){item.sprite.dispose();this.live.delete(id);}}
  const limit=this.model.atlas.streaming?.maxConcurrentLoads??2;for(const r of this.desired){if(this.pending.size>=limit||this.live.size+this.pending.size>=24)break;if(this.live.has(r.id)||this.pending.has(r.id)||this.failures.has(r.id))continue;this.load(r);}
  this.nativeMode=this.desired.length>0&&this.desired.every(r=>this.live.has(r.id));
  this.parent.active=this.nativeMode;
  if(this.overview)this.overview.node.active=!this.nativeMode;
 }
 private async load(r:Region):Promise<void>{this.pending.add(r.id);try{const s=await nativeSprite(r,this.parent,r.nativeSize[0]/r.nativePixelsPerUnit,r.nativeSize[1]/r.nativePixelsPerUnit,r.anchorUV,this.controller.signal,r.ownershipPolygonUV);if(this.stopped||!this.desired.some(d=>d.id===r.id)){s.dispose();return;}const p=this.model.projection.projectMap(...r.anchorMap);s.node.setPosition(p[0],-p[1],0);this.live.set(r.id,{sprite:s,lastSeen:this.clock});const ordered=this.model.atlas.regions.slice().sort((a,b)=>a.sortOrder-b.sortOrder||(a.id<b.id?-1:a.id>b.id?1:0));ordered.forEach((region,i)=>this.live.get(region.id)?.sprite.node.setSiblingIndex(i));}catch(e){if(!this.stopped)this.failures.set(r.id,String(e));}finally{this.pending.delete(r.id);}}
 get status(){return {loaded:this.live.size,loading:this.pending.size,total:this.model.atlas.regions.length,visibleBudget:24,displayMode:this.nativeMode?'native':'overview',overviewSources:this.model.atlas.displayLOD?.sourceRegionIds.length??0,errors:Object.fromEntries(this.failures)};}
 retry():void{this.failures.clear();}
 destroy():void{this.stopped=true;this.controller.abort();this.live.forEach(s=>s.sprite.dispose());this.live.clear();}
}
