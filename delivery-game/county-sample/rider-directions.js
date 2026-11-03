/* Independent eight-frame interface. No generated frame is assumed present. */
window.CountySampleRider={
 frames:Object.create(null),
 // Call after loading and inspecting the actual eight-frame manifest.
 registerFrames(frames){for(const name of ['n','ne','e','se','s','sw','w','nw'])if(frames[name])this.frames[name]=frames[name];},
 directionForVector(dx,dy,previous='s'){
  if(!Number.isFinite(dx)||!Number.isFinite(dy)||Math.hypot(dx,dy)<1e-8)return previous;
  const screenX=.8660254*(dx-dy),screenY=-.5*(dx+dy);
  const names=['e','se','s','sw','w','nw','n','ne'];
  return names[(Math.round(Math.atan2(screenY,screenX)/(Math.PI/4))+8)%8];
 },
 // frame: { image, crop: [x,y,w,h], contact: [x,y], wheelPixels, wheelbaseMetres, heading }.
 // The original sprite is drawn upright; direction is selected by frame, never canvas rotation.
 draw(ctx,frame,screenPoint,pixelsPerMetre){
  if(!frame?.image||!Array.isArray(frame.crop)||!Array.isArray(frame.contact)||!(frame.wheelPixels>0)||!(frame.wheelbaseMetres>0))return false;
  const [x,y,w,h]=frame.crop;if(!(w>0&&h>0))return false;
  const names=['e','se','s','sw','w','nw','n','ne'],index=names.indexOf(frame.heading);if(index<0)return false;
  const angle=index*Math.PI/4,sx=Math.cos(angle),sy=Math.sin(angle);
  const groundX=sx/(2*.8660254)-sy,groundY=-sx/(2*.8660254)-sy,projectedGain=1/Math.hypot(groundX,groundY);
  const sourceScale=frame.wheelbaseMetres*projectedGain/frame.wheelPixels*pixelsPerMetre,width=w*sourceScale,height=h*sourceScale;
  ctx.drawImage(frame.image,x,y,w,h,screenPoint[0]-(frame.contact[0]-x)/w*width,screenPoint[1]-(frame.contact[1]-y)/h*height,width,height);return true;
 }
};
