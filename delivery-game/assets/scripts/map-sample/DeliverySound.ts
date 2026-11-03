import { AudioClip, AudioSource, input, Input, Node, resources } from 'cc';

type SoundEvent='boost'|'shop'|'pickup'|'success';
const sounds:Record<SoundEvent,{file:string;volume:number}>={boost:{file:'m2_boost_click',volume:.45},shop:{file:'m2_arrive_shop',volume:.55},pickup:{file:'m2_pickup_complete',volume:.55},success:{file:'m2_delivery_success',volume:.60}};
/** Ephemeral feedback: no playback or event queue survives a page reload. */
export class DeliverySound {
 private readonly clips:Partial<Record<SoundEvent,AudioClip>>={};
 private readonly boost:AudioSource;private readonly event:AudioSource;
 private unlocked=false;private muted=false;private lastBoost=-Infinity;
 private readonly unlock=()=>{this.unlocked=true;};
 constructor(parent:Node){
  const node=new Node('DeliverySound');parent.addChild(node);this.boost=node.addComponent(AudioSource);
  const second=new Node('DeliveryEventSound');node.addChild(second);this.event=second.addComponent(AudioSource);
  for(const key of Object.keys(sounds) as SoundEvent[])resources.load('map-sample/audio/'+sounds[key].file,AudioClip,(error,clip)=>{if(!error&&node.isValid)this.clips[key]=clip;});
  input.on(Input.EventType.TOUCH_START,this.unlock);
 }
 get isMuted():boolean{return this.muted;}
 toggle():void{this.muted=!this.muted;if(this.muted)this.stop();}
 stop():void{this.boost.stop();this.event.stop();}
 destroy():void{input.off(Input.EventType.TOUCH_START,this.unlock);this.stop();}
 play(key:SoundEvent,allowed:boolean):void{
  if(!allowed||!this.unlocked||this.muted)return;const clip=this.clips[key];if(!clip)return;
  try{if(key==='boost'){const now=performance.now();if(now-this.lastBoost<100)return;this.lastBoost=now;this.boost.stop();this.boost.clip=clip;this.boost.volume=sounds[key].volume*.7;this.boost.play();}
  else{this.boost.stop();this.event.stop();this.event.clip=clip;this.event.volume=sounds[key].volume*.7;this.event.play();}}catch(_){/* Audio is optional; gameplay never depends on playback. */}
 }
}
