import { Color, Graphics, Label, Layers, Node, UITransform } from 'cc';

export const INK = new Color(237, 245, 255);
export const MUTED = new Color(131, 151, 177);
export const MINT = new Color(98, 239, 200);
export const CORAL = new Color(255, 122, 132);

export function box(parent: Node, name: string, width: number, height: number, color: Color, x = 0, y = 0, radius = 12): Node {
  const node = new Node(name);
  node.layer = Layers.Enum.UI_2D;
  parent.addChild(node);
  node.setPosition(x, y);
  node.addComponent(UITransform).setContentSize(width, height);
  const g = node.addComponent(Graphics);
  g.fillColor = color;
  g.roundRect(-width / 2, -height / 2, width, height, radius);
  g.fill();
  return node;
}

export function text(parent: Node, name: string, content: string, fontSize: number, x: number, y: number, color = INK): Label {
  const node = new Node(name);
  node.layer = Layers.Enum.UI_2D;
  parent.addChild(node);
  node.setPosition(x, y);
  node.addComponent(UITransform).setContentSize(650, fontSize * 1.5);
  const label = node.addComponent(Label);
  label.string = content;
  label.fontSize = fontSize;
  label.lineHeight = fontSize * 1.45;
  label.horizontalAlign = Label.HorizontalAlign.CENTER;
  label.verticalAlign = Label.VerticalAlign.CENTER;
  label.color = color;
  label.isBold = fontSize >= 34;
  return label;
}
