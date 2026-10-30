export interface SafeInsets { top:number; bottom:number; left:number; right:number }
export interface SafeRect { x:number; y:number; width:number; height:number }

// The engine returns UI coordinates, including SHOW_ALL's letterbox offsets.
// Intersect with the game first so external black bars do not become extra padding.
export function viewportInsets(width:number,height:number,rect?:SafeRect):SafeInsets {
  const none={top:0,bottom:0,left:0,right:0};
  if(!rect||![width,height,rect.x,rect.y,rect.width,rect.height].every(Number.isFinite)||width<=0||height<=0||rect.width<=0||rect.height<=0)return none;
  const left=Math.max(0,rect.x),right=Math.min(width,rect.x+rect.width);
  const bottom=Math.max(0,rect.y),top=Math.min(height,rect.y+rect.height);
  return right>left&&top>bottom?{left,right:width-right,bottom,top:height-top}:none;
}

// Cocos web rotates a portrait-locked GameDiv clockwise in landscape, but its
// sys safe rect still uses unrotated CSS edges. Convert before clipping black bars.
export function rotatedViewportInsets(width:number,height:number,frame:{width:number;height:number},physical:SafeInsets):SafeInsets {
  const scale=Math.min(frame.width/width,frame.height/height);
  if(!Number.isFinite(scale)||scale<=0)return {top:0,bottom:0,left:0,right:0};
  const offsetX=(frame.width-width*scale)/2,offsetY=(frame.height-height*scale)/2;
  const top=physical.right,bottom=physical.left,left=physical.top,right=physical.bottom;
  return viewportInsets(width,height,{x:(left-offsetX)/scale,y:(bottom-offsetY)/scale,
    width:(frame.width-left-right)/scale,height:(frame.height-top-bottom)/scale});
}

export function safePanelTransform(width:number,height:number,screenHeight:number,insets:SafeInsets={top:0,bottom:0,left:0,right:0}):{x:number;y:number;scale:number} {
  return {x:(insets.left-insets.right)/2,y:(insets.bottom-insets.top)/2,
    scale:Math.max(0,Math.min(1,(720-insets.left-insets.right-24)/width,(screenHeight-insets.top-insets.bottom-24)/height))};
}
