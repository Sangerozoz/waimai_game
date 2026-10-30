const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const EventType={ACTIVE_IN_HIERARCHY_CHANGED:'active',NODE_DESTROYED:'destroy',TOUCH_START:'start',TOUCH_MOVE:'move',TOUCH_CANCEL:'cancel',TOUCH_END:'end'};
const source=fs.readFileSync(process.env.PRESS_UI_SOURCE||path.join(__dirname,'../assets/scripts/map-sample/SampleUI.ts'),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2015,module:ts.ModuleKind.CommonJS}}).outputText;
class Node{static EventType=EventType;constructor(name){this.name=name;this.children=[];this.scale={x:1,y:1,z:1};}addChild(n){this.children.push(n);n.parent=this;}setPosition(){}setScale(x,y,z){this.scale={x,y,z};}addComponent(){return {setContentSize(){}};}getComponent(){return null;}}
const scope={exports:{},require:()=>({Node,Layers:{Enum:{UI_2D:1}},Vec3:class{constructor(x,y,z){Object.assign(this,{x,y,z});}},UITransform:class{},Tween:{stopAllByTarget(){}},tween:()=>({to(){return this;},start(){}})})};vm.runInNewContext(compiled,scope,{filename:'SampleUI.js'});
function button(){
 const events=new Map(),n={children:[new Node('caption')],activeInHierarchy:true,scale:{x:1,y:1,z:1},addChild(n){this.children.push(n);},getComponent(){return null;},on(type,handler){events.set(type,handler);},setScale(x,y,z){this.scale={x,y,z};}};
 let calls=0;scope.exports.tap(n,()=>calls++);
 return {node:n,calls:()=>calls,emit(type,x=0,y=0,id=1){events.get(type)?.({getID:()=>id,getUILocation:()=>({x,y}),getLocation:()=>({x,y})});}};
}
test('the first tap activates once even when the pointer moves by one pixel',()=>{
 const b=button();b.emit('start',100,100);b.emit('move',101,100);b.emit('end',101,100);assert.equal(b.calls(),1);
});
test('a zero-distance move event does not turn a tap into a drag',()=>{
 const b=button();b.emit('start',100,100);b.emit('move',100,100);b.emit('end',100,100);assert.equal(b.calls(),1);
});
test('a real list drag cannot accept an order even when it returns near the start',()=>{
 const b=button();b.emit('start',100,100);b.emit('move',100,140);b.emit('move',100,101);b.emit('end',100,101);assert.equal(b.calls(),0);
});
test('a cancelled touch cannot activate on a later end event',()=>{
 const b=button();b.emit('start');b.emit('cancel');b.emit('end');assert.equal(b.calls(),0);
});
test('touch end without a matching press never activates a button',()=>{
 const b=button();b.emit('end');assert.equal(b.calls(),0);
});
test('a different finger cannot finish the active button press',()=>{
 const b=button();b.emit('start',100,100,1);b.emit('start',100,100,2);b.emit('end',100,100,2);assert.equal(b.calls(),0);b.emit('end',100,100,1);assert.equal(b.calls(),1);
});
test('pressing preserves the existing hit area so edge taps are not cancelled by scaling',()=>{
 const b=button();b.node.scale={x:.8,y:1.2,z:1};b.emit('start',49,0);assert.deepEqual(b.node.scale,{x:.8,y:1.2,z:1});b.emit('end',49,0);assert.deepEqual(b.node.scale,{x:.8,y:1.2,z:1});assert.equal(b.calls(),1);
});
test('a distant release is rejected even when the platform omits move events',()=>{
 const b=button();b.emit('start');b.emit('end',50,0);assert.equal(b.calls(),0);
});
test('each separate tap activates once and duplicate releases do not repeat an action',()=>{
 const b=button();b.emit('start');b.emit('end');b.emit('end');assert.equal(b.calls(),1);b.emit('start');b.emit('end');assert.equal(b.calls(),2);
});
test('the mouse touch identifier zero is a valid press',()=>{
 const b=button();b.emit('start',10,10,0);b.emit('end',10,10,0);assert.equal(b.calls(),1);
});
test('a new press can recover when the platform omitted the previous release',()=>{
 const b=button();b.emit('start',10,10);b.emit('start',100,100);b.emit('end',100,100);assert.equal(b.calls(),1);
});

test('press changes only the visual subtree immediately and cancel restores it',()=>{const b=button();b.emit('start');const visual=b.node.children.find(n=>n.name==='PressVisual');assert.ok(visual);assert.equal(visual.scale.x,.96);assert.equal(b.node.scale.x,1);b.emit('cancel');assert.equal(visual.scale.x,1);assert.equal(b.calls(),0);});
test('drag immediately restores visual and cannot activate on return',()=>{const b=button();b.emit('start');const v=b.node.children.find(n=>n.name==='PressVisual');b.emit('move',8,0);assert.equal(v.scale.x,1);b.emit('end');assert.equal(b.calls(),0);});
test('deactivation clears the active touch and restores visual',()=>{const b=button();b.emit('start');const v=b.node.children.find(n=>n.name==='PressVisual');b.node.activeInHierarchy=false;b.emit('active');assert.equal(v.scale.x,1);b.emit('end');assert.equal(b.calls(),0);});

test('destroy clears touch and visual without dispatching the action',()=>{const b=button();b.emit('start');const v=b.node.children.find(n=>n.name==='PressVisual');b.emit('destroy');assert.equal(v.scale.x,1);b.emit('end');assert.equal(b.calls(),0);});
test('release calls action synchronously while its visual recovery is pending',()=>{const b=button();b.emit('start');b.emit('end');assert.equal(b.calls(),1);assert.equal(b.node.scale.x,1);});
test('an inactive root cannot begin or finish a press',()=>{const b=button();b.node.activeInHierarchy=false;b.emit('start');b.emit('end');assert.equal(b.calls(),0);assert.equal(b.node.children.find(n=>n.name==='PressVisual').scale.x,1);});
