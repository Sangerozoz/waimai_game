import { OrderBook } from './OrderBook';
import { CityData, routePoints } from './MapTypes';
/** Opt-in display adapter only: the original OrderBook retains all gameplay authority. */
export class CountySampleBridge {
 private panel:HTMLDivElement|null=null;
 private frame:HTMLIFrameElement|null=null;
 private elapsed=0;
 private points:Map<string,[number,number]>|null=null;
 private pointsData:CityData|null=null;
 constructor(){
  if(typeof window==='undefined'||new URLSearchParams(window.location.search).get('countySample')!=='live')return;
  const panel=document.createElement('div');panel.style.cssText='position:fixed;z-index:9999;left:2%;right:2%;top:max(8px,env(safe-area-inset-top));height:54%;background:#f9fcf9;border:1px solid #b6cbc6;border-radius:12px;overflow:hidden;box-shadow:0 4px 18px #283f3b55;';
  const close=document.createElement('button');close.type='button';close.textContent='关闭样板';close.style.cssText='position:absolute;z-index:2;right:8px;top:8px;padding:8px;border:1px solid #87a8a4;border-radius:8px;background:#fff;color:#24433f;';
  const frame=document.createElement('iframe');frame.title='县城样板 · 实时只读显示';frame.src='county-sample/?live=1';frame.style.cssText='width:100%;height:100%;border:0;';
  close.onclick=()=>this.destroy();panel.append(frame,close);document.body.appendChild(panel);this.panel=panel;this.frame=frame;
 }
 update(dt:number,book:OrderBook):void{
  if(!this.frame||typeof window==='undefined')return;this.elapsed+=dt;if(this.elapsed<.25)return;this.elapsed=0;
  const active=book.active,route=active?.routes[active.selected];
  if(this.pointsData!==book.data){this.points=new Map(book.data.nodes.map(n=>[n.id,[n.x,n.y] as [number,number]]));this.pointsData=book.data;}
  const pointFor=(index:number)=>{const poi=book.data.pois[index],point=poi&&this.points!.get(poi.node);return point?{name:poi.name,point}:null;};
  const pose=book.riderPose;
  this.frame.contentWindow?.postMessage({type:'county-sample-live-v1',rider:pose.point,riderAngle:pose.angle,vehicleTier:book.player.vehicleTier,route:route?routePoints(route):[],stops:active?[pointFor(active.offer.from),pointFor(active.offer.to)].filter(Boolean):[]},window.location.origin);
 }
 destroy():void{this.panel?.remove();this.panel=null;this.frame=null;}
}
