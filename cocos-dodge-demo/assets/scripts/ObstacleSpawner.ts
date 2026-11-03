import { _decorator, Component, Node } from 'cc';
import { FIELD, Obstacle } from './GameSession';
import { box, CORAL } from './UI';

const { ccclass } = _decorator;

@ccclass('ObstacleSpawner')
export class ObstacleSpawner extends Component {
  private visuals = new Map<number, Node>();

  sync(obstacles: readonly Obstacle[]): void {
    const live = new Set(obstacles.map(obstacle => obstacle.id));
    for (const [id, node] of this.visuals) {
      if (!live.has(id)) { node.destroy(); this.visuals.delete(id); }
    }
    for (const obstacle of obstacles) {
      let node = this.visuals.get(obstacle.id);
      if (!node) {
        node = box(this.node, `Obstacle-${obstacle.id}`, FIELD.obstacleWidth, FIELD.obstacleHeight, CORAL);
        this.visuals.set(obstacle.id, node);
      }
      node.setPosition(obstacle.x, obstacle.y, 0);
    }
  }

  reset(): void {
    for (const node of this.visuals.values()) node.destroy();
    this.visuals.clear();
  }
}
