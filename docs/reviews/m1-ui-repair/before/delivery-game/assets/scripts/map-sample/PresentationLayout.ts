import { Label, Mask, Node, ScrollView, UITransform, view } from 'cc';
import { C, item, label } from './SampleUI';
import { countyExperienceLevel } from './CountyConfig';

// Convert reading and touch targets to design units after SHOW_ALL letterboxing.
export function presentationMetrics(screenHeight=1280):{body:number;aux:number;amount:number;action:number} {
 const frame=view.getFrameSize(),scale=Math.min(frame.width/720,frame.height/screenHeight)||.5;
 return {body:Math.max(28,Math.ceil(15/scale)),aux:Math.max(24,Math.ceil(13/scale)),amount:Math.max(44,Math.ceil(26/scale)),action:Math.max(78,Math.ceil(44/scale))};
}
export function textHeight(value:string,size:number,width:number):number {
 const lines=value.split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil([...line].reduce((sum,char)=>sum+(/[\x00-\xff]/.test(char)?.56:1),0)*size/width)),0);
 return Math.ceil(lines*size*1.42+8);
}
// Fixed readable type: wrap in the supplied area, never shrink an entire paragraph.
export function readable(parent:Node,value:string,x:number,y:number,size:number,fill=C.ink,width=600,bold=false,align:'left'|'center'|'right'='left',height=textHeight(value,size,width)):Label {
 const result=label(parent,value,x,y,size,fill,width,bold,align);
 result.enableWrapText=true;result.lineHeight=Math.ceil(size*1.42);result.overflow=Label.Overflow.CLAMP;
 result.node.getComponent(UITransform)!.setContentSize(width,height);return result;
}
export function scrollContent(parent:Node,width:number,top:number,bottom:number,contentHeight:number):Node {
 const height=Math.max(1,top-bottom),viewport=item(parent,'ScrollableContent',0,(top+bottom)/2,width,height);
 viewport.addComponent(Mask).type=Mask.Type.GRAPHICS_RECT;
 const content=item(viewport,'Content',0,height/2,width,Math.max(height,contentHeight));
 content.getComponent(UITransform)!.setAnchorPoint(.5,1);
 const scroll=viewport.addComponent(ScrollView);scroll.content=content;scroll.horizontal=false;scroll.vertical=true;scroll.elastic=false;scroll.cancelInnerEvents=true;
 return content;
}

// Presentation only: discover the authoritative level boundaries without another XP table.
export function experienceProgress(experience:number):{level:number;start:number;end:number;current:number;required:number;progress:number} {
 const value=Math.min(Number.MAX_SAFE_INTEGER,Math.max(0,Math.floor(Number.isFinite(experience)?experience:0))),level=countyExperienceLevel(value);
 const boundary=(next:boolean):number=>{
  let low=0,high=Number.MAX_SAFE_INTEGER;
  while(low<high){const mid=low+Math.floor((high-low)/2),at=countyExperienceLevel(mid);if(next?at>level:at>=level)high=mid;else low=mid+1;}
  return low;
 };
 const start=boundary(false),end=boundary(true),required=Math.max(1,end-start),current=value-start;
 return {level,start,end,current,required,progress:Math.min(1,Math.max(0,current/required))};
}
