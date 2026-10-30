import { Graphics, Node } from 'cc';
import type { RouteId } from '../domain/GameConfig';
import { color, node, Palette, panel, text } from './Widgets';

type Point = { x: number; y: number };
const START: Point = { x: -248, y: -62 };
const DESTINATIONS: Point[] = [
  { x: 210, y: 70 }, { x: 190, y: -20 }, { x: 90, y: 100 },
  { x: -30, y: 94 }, { x: 235, y: -80 },
];
export const PLACE_NAMES = ['东门公寓', '桂花小区', '河畔宿舍', '文化广场', '南街店铺'];
const ROUTE_COLORS: Record<RouteId, string> = { fast: '#DCA14B', main: '#7198B2', smooth: '#489979' };

export class TownMap {
  private readonly root: Node;
  private readonly routeDrawing: Graphics;
  private readonly scooter: Node;
  private readonly target: Node;
  private destination = 0;
  private currentRoute: RouteId = 'fast';

  constructor(parent: Node) {
    panel(parent, 'MapFrame', 0, 243, 656, 308, '#E8EFDE', 24);
    this.root = node(parent, 'TownMap', 0, 237, 640, 280);
    const g = this.root.addComponent(Graphics);
    this.drawTown(g);
    this.routeDrawing = node(this.root, 'SelectedRoad').addComponent(Graphics);
    this.target = node(this.root, 'Destination', 0, 0, 38, 44);
    const pin = this.target.addComponent(Graphics);
    pin.fillColor = color('#D68D35');
    pin.circle(0, 8, 14); pin.fill();
    pin.moveTo(-9, 2); pin.lineTo(0, -14); pin.lineTo(9, 2); pin.close(); pin.fill();
    pin.fillColor = color('#FFF7E3'); pin.circle(0, 8, 5); pin.fill();
    this.scooter = node(this.root, 'Rider', START.x, START.y, 40, 44);
    this.drawScooter(this.scooter.addComponent(Graphics));
    this.reset();
    text(parent, '东门生活区', -211, 382, 17, Palette.green, 200, 'left', true);
    text(parent, '小城的一天，从这一单开始', 146, 382, 14, '#7C917B', 300, 'right');
  }

  setDestination(index: number, route: RouteId | null = null): void {
    this.destination = Math.abs(index) % DESTINATIONS.length;
    const point = DESTINATIONS[this.destination];
    this.target.active = true;
    this.target.setPosition(point.x, point.y + 11);
    this.routeDrawing.clear();
    if (route) {
      this.currentRoute = route;
      this.stroke(this.routeDrawing, this.points(route), 10, ROUTE_COLORS[route]);
    } else {
      for (const id of ['smooth', 'main', 'fast'] as RouteId[]) this.stroke(this.routeDrawing, this.points(id), 4, ROUTE_COLORS[id]);
    }
    this.scooter.setPosition(START.x, START.y);
    this.scooter.angle = 0;
  }

  setProgress(progress: number): void {
    const points = this.points(this.currentRoute);
    const lengths = points.slice(1).map((point, i) => Math.hypot(point.x - points[i].x, point.y - points[i].y));
    let remaining = Math.max(0, Math.min(1, progress)) * lengths.reduce((sum, value) => sum + value, 0);
    for (let i = 0; i < lengths.length; i++) {
      if (remaining <= lengths[i] || i === lengths.length - 1) {
        const a = points[i]; const b = points[i + 1];
        const t = lengths[i] === 0 ? 1 : Math.min(1, remaining / lengths[i]);
        this.scooter.setPosition(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t);
        this.scooter.angle = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
        return;
      }
      remaining -= lengths[i];
    }
  }

  reset(): void {
    this.routeDrawing.clear();
    this.target.active = false;
    this.scooter.setPosition(START.x, START.y);
    this.scooter.angle = 0;
  }

  private points(route: RouteId): Point[] {
    const end = DESTINATIONS[this.destination];
    if (route === 'fast') return [START, { x: -120, y: -62 }, { x: -120, y: end.y }, end];
    if (route === 'main') return [START, { x: -248, y: 32 }, { x: 30, y: 32 }, { x: 30, y: end.y }, end];
    return [START, { x: -248, y: -110 }, { x: 250, y: -110 }, { x: 250, y: end.y }, end];
  }

  private stroke(g: Graphics, points: Point[], width: number, fill: string): void {
    g.strokeColor = color(fill); g.lineWidth = width;
    g.moveTo(points[0].x, points[0].y);
    for (const point of points.slice(1)) g.lineTo(point.x, point.y);
    g.stroke();
  }

  private drawTown(g: Graphics): void {
    const road = '#F9F7EE';
    for (const y of [-110, 32, 100]) this.stroke(g, [{ x: -300, y }, { x: 300, y }], 24, road);
    for (const x of [-248, -120, 30, 250]) this.stroke(g, [{ x, y: -128 }, { x, y: 128 }], 20, road);
    this.stroke(g, [{ x: -248, y: -62 }, { x: -120, y: -62 }], 23, road);
    const buildings: Array<[number, number, number, number, string]> = [
      [-183, 68, 76, 39, '#D7BDA0'], [-183, -7, 74, 54, '#E3CEA7'],
      [-54, 69, 108, 40, '#CBD2AD'], [-55, -38, 90, 66, '#D5C5AD'],
      [128, 66, 142, 40, '#C7D5C2'], [125, -43, 142, 70, '#D6C2B0'],
    ];
    for (const [x, y, w, h, fill] of buildings) {
      g.fillColor = color('#D4DDC7'); g.roundRect(x - w / 2 + 3, y - h / 2 - 4, w, h, 7); g.fill();
      g.fillColor = color(fill); g.roundRect(x - w / 2, y - h / 2, w, h, 7); g.fill();
      g.fillColor = color('#F7F0DB');
      for (let windowX = x - w / 2 + 12; windowX < x + w / 2 - 8; windowX += 22) {
        g.roundRect(windowX, y - 5, 10, 12, 2); g.fill();
      }
    }
    for (const [x, y] of [[-293, -34], [-287, 60], [-94, -85], [207, 120], [286, 42], [58, -84], [-77, 121]]) {
      g.fillColor = color('#B5C89E'); g.circle(x + 2, y - 3, 11); g.fill();
      g.fillColor = color('#85AD80'); g.circle(x, y + 1, 10); g.fill();
      g.fillColor = color('#A5C195'); g.circle(x - 3, y + 5, 6); g.fill();
    }
    panel(this.root, 'Restaurant', -282, -67, 44, 36, '#E5A64C', 7);
    text(this.root, '餐', -282, -65, 22, '#FFFFFF', 38, 'center', true);
    text(this.root, '东门饭铺', -274, -94, 12, '#7E755B', 90, 'center');
    text(this.root, '桂花街', 89, -108, 11, '#A6AD99', 100, 'center');
  }

  private drawScooter(g: Graphics): void {
    g.fillColor = color('#384A3E'); g.roundRect(-14, -13, 26, 7, 3); g.fill();
    g.roundRect(-14, 6, 26, 7, 3); g.fill();
    g.fillColor = color('#2F8262'); g.roundRect(-17, -9, 34, 18, 7); g.fill();
    g.fillColor = color('#F3C45E'); g.roundRect(-17, -8, 15, 16, 3); g.fill();
    g.fillColor = color('#FFF3D5'); g.circle(8, 0, 7); g.fill();
    g.fillColor = color('#22553E'); g.circle(11, 0, 5); g.fill();
  }
}
