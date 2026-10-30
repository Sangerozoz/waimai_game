import { Color, Graphics, Label, Layers, Node, UITransform } from 'cc';

export const Palette = {
  page: '#F6F3EA', paper: '#FFFFFF', ink: '#253E36', muted: '#7E8E82',
  green: '#27785B', lightGreen: '#E5F0E7', gold: '#D98C28', lightGold: '#FFF0D6',
  red: '#BE654B', border: '#E5E7DB', blue: '#638CAA',
};

export function color(hex: string): Color {
  return new Color(Number.parseInt(hex.slice(1, 3), 16), Number.parseInt(hex.slice(3, 5), 16), Number.parseInt(hex.slice(5, 7), 16), 255);
}

export function node(parent: Node, name: string, x = 0, y = 0, width = 0, height = 0): Node {
  const item = new Node(name);
  item.layer = Layers.Enum.UI_2D;
  parent.addChild(item);
  item.setPosition(x, y);
  item.addComponent(UITransform).setContentSize(width, height);
  return item;
}

export function panel(parent: Node, name: string, x: number, y: number, width: number, height: number, fill = Palette.paper, radius = 18, outline?: string): Node {
  const item = node(parent, name, x, y, width, height);
  const drawing = item.addComponent(Graphics);
  drawing.fillColor = color(fill);
  drawing.roundRect(-width / 2, -height / 2, width, height, radius);
  drawing.fill();
  if (outline) {
    drawing.strokeColor = color(outline);
    drawing.lineWidth = 1.5;
    drawing.roundRect(-width / 2 + 1, -height / 2 + 1, width - 2, height - 2, radius);
    drawing.stroke();
  }
  return item;
}

export function text(parent: Node, content: string, x: number, y: number, size = 20, fill = Palette.ink, width = 600, align: 'left' | 'center' | 'right' = 'left', bold = false, height = size * 1.6): Label {
  const item = node(parent, 'Text', x, y, width, height);
  const label = item.addComponent(Label);
  label.string = content;
  label.fontSize = size;
  label.lineHeight = Math.ceil(size * 1.45);
  label.color = color(fill);
  label.isBold = bold;
  label.overflow = Label.Overflow.SHRINK;
  label.horizontalAlign = align === 'left' ? Label.HorizontalAlign.LEFT : align === 'right' ? Label.HorizontalAlign.RIGHT : Label.HorizontalAlign.CENTER;
  label.verticalAlign = Label.VerticalAlign.CENTER;
  return label;
}

export function button(parent: Node, title: string, x: number, y: number, width: number, height: number, handler: () => void, fill = Palette.green, foreground = '#FFFFFF'): Node {
  const item = panel(parent, 'Button', x, y, width, height, fill, Math.min(16, height / 3));
  text(item, title, 0, 0, 21, foreground, width - 16, 'center', true);
  item.on(Node.EventType.TOUCH_START, () => item.setScale(0.98, 0.98, 1));
  item.on(Node.EventType.TOUCH_CANCEL, () => item.setScale(1, 1, 1));
  item.on(Node.EventType.TOUCH_END, () => {
    item.setScale(1, 1, 1);
    handler();
  });
  return item;
}

export function money(cents: number): string {
  return (cents / 100).toFixed(2);
}
