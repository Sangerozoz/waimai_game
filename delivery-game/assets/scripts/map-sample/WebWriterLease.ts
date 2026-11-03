import { COUNTY_SAVE_KEY } from './CountySaveStore';
/** An origin-wide exclusive Web Lock, held until this page is destroyed. No lease timeout. */
export class WebWriterLease {
 private releaseLock:(()=>void)|null=null;
 private owned=false;
 get writable():boolean{return this.owned;}
 async acquire():Promise<boolean> {
  const locks=typeof navigator!=='undefined'?(navigator as any).locks:null;
  if(!locks?.request)return false;
  return new Promise(resolve=>{
   try{locks.request(COUNTY_SAVE_KEY+':writer',{mode:'exclusive',ifAvailable:true},async(lock:unknown)=>{
    if(!lock){resolve(false);return;}
    this.owned=true;
    await new Promise<void>(release=>{this.releaseLock=release;resolve(true);});
    this.owned=false;
   }).catch(()=>resolve(false));}catch{resolve(false);}
  });
 }
 release():void{this.owned=false;this.releaseLock?.();this.releaseLock=null;}
}
