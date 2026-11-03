import { _decorator, Camera, Color, Component, DirectionalLight, EffectAsset, Material, MeshRenderer, Node, Quat, Vec3, Vec4, primitives, resources, utils } from 'cc';
const { ccclass } = _decorator;
type V = [number, number, number];
type Shape = { name:string; type:string; material:string; position:V; rotation?:V; size?:V; radius?:number; radiusTop?:number; height?:number; segments?:number; scale?:V; vertices?:number[]; indices?:number[]; normals?:number[]; castShadow?:boolean; receiveShadow?:boolean };
type Design = { version:number; camera:{ position:V; target:V; orthoHeight:number }; materials:Record<string,{ color:string; roughness:number; metallic?:number; emissive?:string }>; objects:Shape[] };
type Batch = { positions:number[]; normals:number[]; indices:number[]; material:string; cast:boolean; receive:boolean };
const vec = (v:V) => new Vec3(v[0],v[1],v[2]);
function generatedNormals(p:number[], idx:number[]):number[] {
 const n=new Array(p.length).fill(0);
 for(let i=0;i<idx.length;i+=3){const a=idx[i]*3,b=idx[i+1]*3,c=idx[i+2]*3;const ab=new Vec3(p[b]-p[a],p[b+1]-p[a+1],p[b+2]-p[a+2]),ac=new Vec3(p[c]-p[a],p[c+1]-p[a+1],p[c+2]-p[a+2]),cross=new Vec3();Vec3.cross(cross,ab,ac);for(const k of [a,b,c]){n[k]+=cross.x;n[k+1]+=cross.y;n[k+2]+=cross.z;}}
 for(let i=0;i<n.length;i+=3){const length=Math.hypot(n[i],n[i+1],n[i+2])||1;n[i]/=length;n[i+1]/=length;n[i+2]/=length;}return n;
}
function geometry(o:Shape):{ positions:number[]; normals:number[]; indices:number[] } {
 let g:any;
 if(o.type==='box'){if(!o.size)throw Error('盒体缺少尺寸: '+o.name);g=primitives.box({width:o.size[0],height:o.size[1],length:o.size[2]});}
 else if(o.type==='cylinder'){if(o.radius==null||o.height==null)throw Error('圆柱缺少尺寸: '+o.name);g=primitives.cylinder(o.radiusTop??o.radius,o.radius,o.height,{radialSegments:o.segments||16});}
 else if(o.type==='sphere'){if(o.radius==null)throw Error('球体缺少半径: '+o.name);g=primitives.sphere(o.radius,{segments:16});}
 else if(o.type==='mesh'){if(!o.vertices||!o.indices)throw Error('网格缺少顶点或索引: '+o.name);g={positions:o.vertices,indices:o.indices,normals:o.normals};}
 else throw Error('不支持的形状: '+o.type);
 const p=Array.from(g.positions) as number[],idx=Array.from(g.indices) as number[],norm=g.normals?Array.from(g.normals) as number[]:generatedNormals(p,idx),q=new Quat(),rot=o.rotation||[0,0,0],s=o.type==='sphere'?(o.scale||[1,1,1]):[1,1,1];Quat.fromEuler(q,rot[0],rot[1],rot[2]);
 for(let i=0;i<p.length;i+=3){const v=new Vec3(p[i]*s[0],p[i+1]*s[1],p[i+2]*s[2]);Vec3.transformQuat(v,v,q);p[i]=v.x+o.position[0];p[i+1]=v.y+o.position[1];p[i+2]=v.z+o.position[2];const normal=new Vec3(norm[i]/s[0],norm[i+1]/s[1],norm[i+2]/s[2]);Vec3.transformQuat(normal,normal,q);Vec3.normalize(normal,normal);norm[i]=normal.x;norm[i+1]=normal.y;norm[i+2]=normal.z;}
 return {positions:p,normals:norm,indices:idx};
}
@ccclass('StreetCorner')
export class StreetCorner extends Component {
 private camera:Camera|null=null; private initialHeight=30; private controls:HTMLElement|null=null;
 async start(){
  try{
   const response=await fetch('scene-design.json',{cache:'no-store'});if(!response.ok)throw Error('街景资源未找到');const design=await response.json() as Design;if(design.version!==1||!design.camera||!design.materials||!Array.isArray(design.objects))throw Error('街景资源格式不正确');
   const scene=this.node.scene!;const ambient=scene.globals.ambient;ambient.skyColor=new Vec4(.90,.88,.84,1);ambient.groundAlbedo=new Vec4(.70,.66,.60,1);ambient.skyIllum=20000;scene.globals.shadows.enabled=true;scene.globals.shadows.type=1;
   const sun=new Node('Sun');scene.addChild(sun);sun.setRotationFromEuler(-48,-35,0);const light=sun.addComponent(DirectionalLight);light.color=new Color(255,244,228,255);light.illuminance=65000;light.shadowEnabled=true;light.shadowPcf=2;light.shadowDistance=100;light.shadowBias=.0001;light.shadowNormalBias=.2;
   const cameraNode=new Node('StreetCamera');scene.addChild(cameraNode);cameraNode.setPosition(vec(design.camera.position));cameraNode.lookAt(vec(design.camera.target));const camera=cameraNode.addComponent(Camera);camera.projection=Camera.ProjectionType.ORTHO;camera.orthoHeight=design.camera.orthoHeight;camera.aperture=Camera.Aperture.F14_0;camera.near=.1;camera.far=500;camera.clearColor=new Color(219,229,234,255);this.camera=camera;this.initialHeight=design.camera.orthoHeight;
   const standard=await new Promise<EffectAsset>((resolve,reject)=>resources.load('street-standard',EffectAsset,(error,asset)=>error?reject(error):resolve(asset)));
   const mats:Record<string,Material>={};for(const [name,spec] of Object.entries(design.materials)){const m=new Material();m.initialize({effectAsset:standard});if(!m.passes.length)throw Error('标准材质无渲染 pass: '+name);m.setProperty('mainColor',Color.fromHEX(new Color(),spec.color));m.setProperty('roughness',spec.roughness);m.setProperty('metallic',spec.metallic||0);if(spec.emissive)m.setProperty('emissive',Color.fromHEX(new Color(),spec.emissive));mats[name]=m;}
   const batches:Batch[]=[];const current=new Map<string,Batch>();for(const o of design.objects){if(!mats[o.material])throw Error('未知材质: '+o.material);const shape=geometry(o),cast=o.castShadow!==false,receive=o.receiveShadow!==false,key=`${o.material}|${cast}|${receive}`;let b=current.get(key);if(!b||b.positions.length/3+shape.positions.length/3>60000){b={positions:[],normals:[],indices:[],material:o.material,cast,receive};batches.push(b);current.set(key,b);}const offset=b.positions.length/3;for(const v of shape.positions)b.positions.push(v);for(const v of shape.normals)b.normals.push(v);for(const index of shape.indices)b.indices.push(index+offset);}
   for(const [i,b] of batches.entries()){const n=new Node(`Geometry-${i}-${b.material}`);scene.addChild(n);const renderer=n.addComponent(MeshRenderer);renderer.setMaterial(mats[b.material],0);renderer.mesh=utils.createMesh({positions:b.positions,normals:b.normals,indices:b.indices});renderer.shadowCastingMode=b.cast?MeshRenderer.ShadowCastingMode.ON:MeshRenderer.ShadowCastingMode.OFF;renderer.receiveShadow=b.receive?MeshRenderer.ShadowReceivingMode.ON:MeshRenderer.ShadowReceivingMode.OFF;}
   this.addControls();
  }catch(e){console.error('[street-corner-3d]',e);this.showError(e instanceof Error?e.message:String(e));}
 }
 private addControls(){if(typeof document==='undefined')return;const bar=document.createElement('div');bar.style.cssText='position:fixed;right:12px;bottom:max(12px,env(safe-area-inset-bottom));z-index:20;display:flex;gap:6px';for(const [label,factor] of [['−',1.2],['复位',0],['+',1/1.2]] as Array<[string,number]>){const button=document.createElement('button');button.textContent=label;button.setAttribute('aria-label',label==='−'?'缩小':label==='+'?'放大':'复位');button.style.cssText='font:16px system-ui;color:#314654;background:#ffffffdf;border:1px solid #c9d2d3;border-radius:8px;min-width:40px;height:40px';button.onclick=()=>{if(this.camera)this.camera.orthoHeight=factor?Math.max(this.initialHeight*.45,Math.min(this.initialHeight*2,this.camera.orthoHeight*factor)):this.initialHeight;};bar.appendChild(button);}document.body.appendChild(bar);this.controls=bar;}
 private showError(message:string){if(typeof document==='undefined')return;const panel=document.createElement('div');panel.textContent='街景加载失败：'+message;panel.style.cssText='position:fixed;top:16px;left:16px;right:16px;padding:14px;border-radius:8px;background:#fff;color:#8c302a;z-index:20;font:15px system-ui';document.body.appendChild(panel);this.controls=panel;}
 onDestroy(){this.controls?.remove();}
}
