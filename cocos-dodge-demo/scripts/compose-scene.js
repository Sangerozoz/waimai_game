// Run through Funplay's execute_javascript in scene context.
const canvas = scene.getChildByName('Canvas');
if (!canvas) throw new Error('Main scene must contain a Canvas.');
const camera = canvas.getChildByName('Camera');
if (camera) camera.setPosition(0, 0, 1000);
const names = ['Background', 'Player', 'Obstacles', 'HUD', 'GameController'];
for (const name of names) {
  let node = canvas.getChildByName(name);
  if (!node) {
    node = new cc.Node(name);
    node.layer = cc.Layers.Enum.UI_2D;
    canvas.addChild(node);
    node.addComponent(cc.UITransform);
  }
  const className = name === 'Player' ? 'PlayerController' : name === 'Obstacles' ? 'ObstacleSpawner' : name;
  if (className !== 'Background') {
    const ctor = cc.js.getClassByName(className);
    if (!ctor) throw new Error(`Script not compiled: ${className}`);
    if (!node.getComponent(ctor)) node.addComponent(ctor);
  }
}
return { scene: scene.name, nodes: names, canvasSize: canvas.getComponent(cc.UITransform).contentSize };
