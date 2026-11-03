export const FIELD = { width: 720, height: 1280, playerY: -456, playerWidth: 64, playerHeight: 50, obstacleWidth: 82, obstacleHeight: 54 };
export type GameState = 'ready' | 'playing' | 'game-over';
export interface Obstacle { id: number; x: number; y: number; }

/** Engine-independent rules, shared by Cocos components and behavioral tests. */
export class GameSession {
  state: GameState = 'ready';
  score = 0;
  playerX = 0;
  obstacles: Obstacle[] = [];
  elapsed = 0;
  private spawnClock = 0;
  private nextId = 0;
  constructor(private random: () => number = Math.random) {}
  setPlayerX(x: number): void { this.playerX = Math.max(-300, Math.min(300, x)); }
  start(): void {
    this.state = 'playing';
    this.score = 0;
    this.playerX = 0;
    this.obstacles = [];
    this.elapsed = 0;
    this.spawnClock = 0;
    this.nextId = 0;
  }
  step(deltaTime: number): void {
    if (this.state !== 'playing' || deltaTime <= 0) return;
    this.elapsed += deltaTime;
    this.spawnClock += deltaTime;
    while (this.spawnClock >= 0.9) {
      this.spawnClock -= 0.9;
      this.obstacles.push({ id: this.nextId++, x: (this.random() * 2 - 1) * 284, y: 680 });
    }
    for (const obstacle of this.obstacles) {
      obstacle.y -= 420 * deltaTime;
      if (Math.abs(obstacle.x - this.playerX) < (FIELD.playerWidth + FIELD.obstacleWidth) / 2
        && Math.abs(obstacle.y - FIELD.playerY) < (FIELD.playerHeight + FIELD.obstacleHeight) / 2) {
        this.state = 'game-over';
        return;
      }
    }
    const remaining = this.obstacles.filter(obstacle => obstacle.y >= -680);
    this.score += this.obstacles.length - remaining.length;
    this.obstacles = remaining;
  }
}
