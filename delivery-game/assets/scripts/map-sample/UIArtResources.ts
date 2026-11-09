import { assetManager, JsonAsset, resources, Texture2D } from 'cc';

// Share native textures across both UI loaders, including the original hero portrait.
// Only requested art is loaded. No page-wide preloading or global downloader changes.
const textures=new Map<string,Promise<Texture2D>>();
const jsonAssets=new Map<string,Promise<JsonAsset>>();
const ATTEMPTS=3, TIMEOUT_MS=60000;

function attempt<T>(path:string,begin:(done:(error:Error|null,value?:T)=>void)=>void,timeoutMs=TIMEOUT_MS):Promise<T> {
 return new Promise<T>((resolve,reject)=>{
  let settled=false;
  const done=(error:Error|null,value?:T)=>{
   if(settled)return;settled=true;clearTimeout(timer);clearTimeout(slowTimer);
   if(error||!value)reject(error||new Error('empty resource: '+path));else resolve(value);
  };
  // resources.load has no cancellation API. Ignore a late callback; never attach it
  // to a destroyed/replaced node. Retries remain bounded and shared by resource key.
  const slowTimer=setTimeout(()=>console.warn(`[UI resource slow] ${path}; elapsedMs=10000; waiting for engine callback`),10000);
  const timer=setTimeout(()=>done(new Error(`resource timeout after ${timeoutMs}ms: ${path}`)),timeoutMs);
  try{begin(done);}catch(error){done(error instanceof Error?error:new Error(String(error)));}
 });
}
function cachedLoad<T>(cache:Map<string,Promise<T>>,path:string,begin:(done:(error:Error|null,value?:T)=>void)=>void,retain?:(value:T)=>void,timeoutMs=TIMEOUT_MS,validate?:(value:T)=>void):Promise<T> {
 const cached=cache.get(path);if(cached)return cached;
 const started=Date.now();
 const pending=(async()=>{
  for(let n=1;n<=ATTEMPTS;n++){
   try{
    const value=await attempt(path,begin,timeoutMs);validate?.(value);retain?.(value);
    if(n>1||Date.now()-started>10000)console.info(`[UI resource ready] ${path}; attempt=${n}; elapsedMs=${Date.now()-started}`);
    return value;
   }catch(error){
    console.warn(`[UI resource ${n===ATTEMPTS?'failed':'retry'}] ${path}; attempt=${n}/${ATTEMPTS}; elapsedMs=${Date.now()-started}`,error);
    if(n===ATTEMPTS)throw error;
    await new Promise<void>(resolve=>setTimeout(resolve,n*1000));
   }
  }
  throw new Error('resource retry exhausted: '+path);
 })();
 cache.set(path,pending);
 // Reopening a page can recover even after all attempts failed. Do not poison the
 // session with a rejected Promise, or evict a newer request's cache entry.
 void pending.catch(()=>{if(cache.get(path)===pending)cache.delete(path);});
 return pending;
}
export function loadArtTexture(resource:string):Promise<Texture2D> {
 const path=resource+'/texture';
 // Optional derived textures also fail back promptly (at most 3×4s + 1s/2s).
 // Preserve the existing 3×60s policy for every original texture/manifest.
 const timeoutMs=resource.startsWith('ui-v2/web/')?4000:TIMEOUT_MS;
 return cachedLoad(textures,path,done=>resources.load(path,Texture2D,done),texture=>texture.addRef(),timeoutMs);
}
export function loadArtJson(path:string):Promise<JsonAsset> {
 return cachedLoad(jsonAssets,path,done=>resources.load(path,JsonAsset,done));
}

export type ArtRect=[number,number,number,number];
export interface ArtInsets {left:number;right:number;top:number;bottom:number}
type ArtSize=[number,number];
interface WebRegion {resource:string;size:ArtSize}
interface WebSource {size:ArtSize;regions:Record<string,WebRegion>}
interface WebPack {version:number;sources:Record<string,WebSource>}
export interface LoadedArtRegion {
 texture:Texture2D;
 rect:ArtRect;
 sourceRect:ArtRect;
 inset?:ArtInsets;
 /** A valid original fallback must not prevent a later derivative retry. */
 retryWeb:boolean;
}
let webPack:Promise<WebPack>|null=null;
let webPackRetryAt=0;
const WEB_TIMEOUT_MS=4000;
function record(value:unknown):value is Record<string,unknown> {
 return !!value&&typeof value==='object'&&!Array.isArray(value);
}
function artSize(value:unknown):value is ArtSize {
 return Array.isArray(value)&&value.length===2&&value.every(v=>Number.isSafeInteger(v)&&v>0);
}
function validateWebPack(data:unknown):WebPack {
 if(!record(data)||data.version!==1||!record(data.sources))throw new Error('unsupported UI web pack');
 const sources:Record<string,WebSource>=Object.create(null),sizes=new Map<string,ArtSize>();
 for(const resource of Object.keys(data.sources)){
  const source=data.sources[resource];
  if(!record(source)||!artSize(source.size)||!record(source.regions))throw new Error('invalid UI web source: '+resource);
  const size:ArtSize=[source.size[0],source.size[1]],regions:Record<string,WebRegion>=Object.create(null);
  for(const key of Object.keys(source.regions)){
   const crop=key.split(',').map(Number),region=source.regions[key];
   if(crop.length!==4||!crop.every(Number.isSafeInteger)||crop.join(',')!==key)throw new Error('invalid UI web crop: '+key);
   checkRect(crop as ArtRect,size[0],size[1]);
   if(!record(region)||typeof region.resource!=='string'||!/^ui-v2\/web\/[a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)*$/.test(region.resource)||!artSize(region.size))throw new Error('invalid UI web region: '+key);
   const expected=sizes.get(region.resource),regionSize:ArtSize=[region.size[0],region.size[1]];
   if(expected&&(expected[0]!==regionSize[0]||expected[1]!==regionSize[1]))throw new Error('inconsistent UI web texture dimensions: '+region.resource);
   sizes.set(region.resource,regionSize);regions[key]={resource:region.resource,size:regionSize};
  }
  sources[resource]={size,regions};
 }
 // Do not publish the engine JsonAsset's mutable, only partly checked structure.
 return {version:1,sources};
}
function invalidateWebPack(pending:Promise<WebPack>):void {
 if(webPack!==pending)return;
 webPack=null;webPackRetryAt=Date.now()+WEB_TIMEOUT_MS;
}
function loadWebPack():Promise<WebPack> {
 if(webPack)return webPack;
 if(Date.now()<webPackRetryAt)return Promise.reject(new Error('UI web pack refresh cooling down'));
 // This optional index is not a startup prerequisite. One short, shared attempt
 // avoids holding every UI picture behind a missing pack for 3×60 seconds.
 // Only a later UI request refreshes an incomplete index; no timer polls it.
 const path='ui-v2/web/pack';
 const pending=attempt<JsonAsset>(path,done=>assetManager.loadAny({path,type:JsonAsset,bundle:resources.name},{reloadAsset:true},done),WEB_TIMEOUT_MS).then(value=>{
  if(!(value instanceof JsonAsset))throw new Error('invalid UI web pack asset');
  return validateWebPack(value.json);
 });
 webPack=pending;
 void pending.catch(()=>invalidateWebPack(pending));
 return pending;
}
function loadWebTexture(region:WebRegion):Promise<Texture2D> {
 const path=region.resource+'/texture',[w,h]=region.size,key=path+'@'+w+'x'+h;
 // Cocos 3.8.8 propagates these global options to ImageAsset/native dependencies.
 // Successful import/native loads clear files/parsed; reloadAsset bypasses the
 // remaining UUID asset cache. No release/destroy of textures held by other frames.
 // Application successes are shared, but every new optional attempt is reloadable.
 return cachedLoad(textures,key,done=>assetManager.loadAny({path,type:Texture2D,bundle:resources.name},{reloadAsset:true},done),texture=>texture.addRef(),WEB_TIMEOUT_MS,texture=>{
  if(!(texture instanceof Texture2D)||texture.width!==w||texture.height!==h)throw new Error('UI web texture dimensions differ from mapping');
 });
}
function pixelRect(rect:ArtRect,width:number,height:number,normalized:boolean):ArtRect {
 if(!normalized)return [...rect];
 const [left,top,w,h]=rect,x=Math.round(left*width),y=Math.round(top*height);
 return [x,y,Math.round((left+w)*width)-x,Math.round((top+h)*height)-y];
}
function checkRect(rect:ArtRect,width:number,height:number):void {
 const [x,y,w,h]=rect;
 if(!rect.every(Number.isFinite)||x<0||y<0||w<=0||h<=0||x+w>width||y+h>height)throw new Error('art rectangle outside texture');
}
/** Shared crop mapping for both loaders. Original resource paths/manifests stay immutable.
 * Only UI callers opt in; maps, world sprites and showcase keep their native path.
 * Failed JSON/texture attempts retain the existing bounded recovery and never
 * replace the source's cache key with a failed derivative or a sticky fallback.
 */
export async function loadArtRegion(resource:string,rect:ArtRect,options:{normalized?:boolean;inset?:ArtInsets;web?:boolean}={}):Promise<LoadedArtRegion> {
 const retryWeb=options.web!==false;
 if(retryWeb){
  try{
   const pending=loadWebPack(),pack=await pending;
   let sourceRect:ArtRect,derived:WebRegion;
   try{
    const source=pack.sources[resource];
    if(!source)throw new Error('missing UI web source: '+resource);
    sourceRect=pixelRect(rect,source.size[0],source.size[1],!!options.normalized);
    checkRect(sourceRect,source.size[0],source.size[1]);
    derived=source.regions[sourceRect.join(',')];
    if(!derived)throw new Error('missing UI web region: '+resource);
   }catch(error){invalidateWebPack(pending);throw error;}
   const texture=await loadWebTexture(derived),[w,h]=derived.size;
   const inset=options.inset?{left:options.inset.left*w/sourceRect[2],right:options.inset.right*w/sourceRect[2],top:options.inset.top*h/sourceRect[3],bottom:options.inset.bottom*h/sourceRect[3]}:undefined;
   return {texture,rect:[0,0,w,h],sourceRect,inset,retryWeb:false};
  }catch(error){console.warn(`[UI web original fallback] ${resource}`,error);}
 }
 const texture=await loadArtTexture(resource);
 const sourceRect=pixelRect(rect,texture.width,texture.height,!!options.normalized);
 checkRect(sourceRect,texture.width,texture.height);
 return {texture,rect:sourceRect,sourceRect,inset:options.inset,retryWeb};
}
