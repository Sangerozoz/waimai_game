const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const editor=process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts=require(path.join(editor,'Contents/Resources/app.asar.unpacked/node_modules/typescript'));

// Cocos rendering needs the editor runtime. Keep our dialog and drawing helpers real,
// replacing only the engine boundary with recorded nodes and graphics commands.
class Node {
  static EventType={TOUCH_START:'start',TOUCH_MOVE:'move',TOUCH_CANCEL:'cancel',TOUCH_END:'end'};
  constructor(name){this.name=name;this.children=[];this.components=new Map();this.events=new Map();this.active=true;}
  addChild(child){this.children.push(child);child.parent=this;}
  addComponent(Type){const value=new Type();value.node=this;this.components.set(Type,value);return value;}
  getComponent(Type){return this.components.get(Type);}
  setPosition(x,y){this.position={x,y};}
  setScale(){}
  on(event,callback){this.events.set(event,callback);}
  destroy(){this.destroyed=true;}
}
class Color {constructor(r,g,b,a){Object.assign(this,{r,g,b,a});}}
class Graphics {roundRect(){} fill(){this.drawnFill=this.fillColor;} stroke(){}}
class UITransform {setContentSize(width,height){Object.assign(this,{width,height});}}
class Label {
  static HorizontalAlign={LEFT:0,RIGHT:1,CENTER:2};
  static VerticalAlign={CENTER:0};
  static Overflow={SHRINK:0};
}
class BlockInputEvents {}
class UIOpacity {constructor(){this.opacity=255;}}
const cc={Node,Color,Graphics,UITransform,Label,BlockInputEvents,UIOpacity,Component:class {},Layers:{Enum:{UI_2D:1}},_decorator:{ccclass:()=>Type=>Type}};
function load(name,dependencies){
  const filename=path.join(__dirname,'../assets/scripts/map-sample',name+'.ts');
  const compiled=ts.transpileModule(fs.readFileSync(filename,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,experimentalDecorators:true}});
  const module={exports:{}};
  vm.runInNewContext(compiled.outputText,{module,exports:module.exports,require:id=>id==='cc'?cc:dependencies[id]||{}},{filename});
  return module.exports;
}
const ui=load('SampleUI',{});
const {MapSample}=load('MapSample',{'./SampleUI':ui,'./SafeAreaLayout':load('SafeAreaLayout',{})});
function dialog(){
  const sample=Object.create(MapSample.prototype);
  Object.assign(sample,{root:new Node('Root'),screenExtra:160,modal:null,modalKind:null});
  const result=sample.dialog('配送结算',800,'receipt');
  return {sample,...result,shade:result.layer.children.find(node=>node.name==='Shade')};
}

test('color parsing preserves alpha in RGBA and opacity in existing RGB colors',()=>{
  for(const [hex,rgba] of [['#00000099',[0,0,0,153]],['#12345600',[18,52,86,0]],['#FFFFFF',[255,255,255,255]],['#302B20',[48,43,32,255]]]){
    const color=ui.col(hex);assert.deepEqual([color.r,color.g,color.b,color.a],rgba);
  }
});
test('receipt dialog draws a 60 percent black shade while its card stays opaque',()=>{
  const {layer,card,shade}=dialog();
  const color=shade.getComponent(Graphics).drawnFill;
  assert.deepEqual([color.r,color.g,color.b,color.a],[0,0,0,153]);
  assert.equal(card.getComponent(Graphics).drawnFill.a,255);
  assert.equal(layer.getComponent(UIOpacity)?.opacity??255,255);
  assert.equal(shade.getComponent(UIOpacity)?.opacity??255,255);
  assert.equal(shade.getComponent(UITransform).height,1440);
});
test('transparent shade still blocks map input and closes the dialog on touch',()=>{
  const {sample,layer,card,shade}=dialog();
  assert.ok(layer.getComponent(BlockInputEvents));assert.ok(card.getComponent(BlockInputEvents));
  const touch={getID:()=>0,getUILocation:()=>({x:0,y:0})};
  shade.events.get(Node.EventType.TOUCH_START)(touch);shade.events.get(Node.EventType.TOUCH_END)(touch);
  assert.equal(sample.modal,null);assert.equal(sample.modalKind,null);
  assert.equal(layer.active,false);assert.equal(layer.destroyed,true);
});
