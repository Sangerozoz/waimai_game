import { _decorator, Component, JsonAsset, Label, Node, resources, sys, UITransform } from 'cc';
import { CityData } from './MapTypes';
import { prepareCity } from './PlaceCatalog';
import { item, label } from './SampleUI';
import { V2RuntimeController } from './V2RuntimeController';
import { V2RuntimeStore } from './V2RuntimeStore';
import { V2GameUI } from './V2GameUI';
import { panel, action, portrait, UI } from './V2ApprovedSkin';
const { ccclass } = _decorator;
/** Single current progress. Legacy game saves are discarded, never imported. */
@ccclass('V2GameBootstrap')
export class V2GameBootstrap extends Component {
 private gate:Node|null=null;
 private opening=false;
 private disposed=false;
 private preparation:V2RuntimeStore|null=null;
 start():void { this.showEntry(); }
 private showEntry():void {
  this.gate=item(this.node.parent!,'V2Entry',0,0,720,1280);
  panel(this.gate,'EntryBackground',0,0,720,1280,'#E3F5FF','#E3F5FF');
  panel(this.gate,'EntryCard',0,0,650,660,'#F2FBFF',UI.line);
  portrait(this.gate,0,0,245,82,82);
  label(this.gate,'晴川骑手',0,170,32,'#254B70',640,true,'center');
  const notice=label(this.gate,'仅保留一份当前进度，正在准备…',0,80,20,'#254B70',620,false,'center');
  notice.node.getComponent(UITransform)!.setContentSize(620,100);
  const open=()=>{
   if(this.opening)return;this.opening=true;notice.string='正在载入原路网…';
   resources.load('map-sample/city',JsonAsset,async(error,asset)=>{
    if(this.disposed||!this.isValid)return;
    if(error){notice.string='地图加载失败，请重试';this.opening=false;return;}
    let runtime:V2RuntimeController|null=null;
    try{
     const data=prepareCity(asset.json as CityData);
     runtime=this.node.addComponent(V2RuntimeController);
     runtime.enableV2=true;
     runtime.configure({city:data,nowSeconds:()=>Date.now()/1000,ads:{show:()=>{throw new Error('广告暂不可用');}}});
     await runtime.startOrContinue();
     if(this.disposed||!this.isValid){runtime.destroy();return;}
     const ui=this.node.addComponent(V2GameUI);ui.configure(runtime,data,this.node.parent!);
     this.gate?.destroy();this.gate=null;
    }catch(err){runtime?.destroy();notice.string=String(err);this.opening=false;}
   });
  };
  const start=action(this.gate,'开始 / 继续游戏',0,-20,440,70,open);
  label(this.gate,'仅一份当前进度 · 自动保存',0,-150,19,'#254B70',620,false,'center');
  const preparation=new V2RuntimeStore({getItem:key=>sys.localStorage.getItem(key),setItem:(key,value)=>sys.localStorage.setItem(key,value),removeItem:key=>sys.localStorage.removeItem(key)});
  this.preparation=preparation;
  this.opening=true;
  preparation.prepare().then(has=>{
   if(this.disposed||!this.isValid)return;
   // Button caption is cosmetic; open always reads the latest slot under the lock.
   const caption=start.getComponentInChildren(Label);
   if(caption)caption.string=has?'继续游戏':'开始游戏';
   notice.string=has?'继续唯一当前进度':'从新进度开始，自动保存到本机';
  }).catch(error=>{if(!this.disposed&&this.isValid)notice.string=String(error);}).finally(()=>{preparation.close();this.preparation=null;this.opening=false;});
 }
 onDestroy():void {this.disposed=true;this.preparation?.close();this.gate?.destroy();}
}
