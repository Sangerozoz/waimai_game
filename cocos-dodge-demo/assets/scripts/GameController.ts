import { _decorator, Color, Component, Graphics, sys, UITransform } from 'cc';
import { GameSession } from './GameSession';
import { HUD } from './HUD';
import { ObstacleSpawner } from './ObstacleSpawner';
import { PlayerController } from './PlayerController';

const { ccclass } = _decorator;

@ccclass('GameController')
export class GameController extends Component {
  private game = new GameSession();
  private player!: PlayerController;
  private spawner!: ObstacleSpawner;
  private hud!: HUD;
  private best = 0;

  start(): void {
    const canvas = this.node.parent!;
    this.player = canvas.getChildByName('Player')!.getComponent(PlayerController)!;
    this.spawner = canvas.getChildByName('Obstacles')!.getComponent(ObstacleSpawner)!;
    this.hud = canvas.getChildByName('HUD')!.getComponent(HUD)!;
    this.hud.onRestartRequested = () => this.startGame();
    try { this.best = Number(sys.localStorage.getItem('cosmic-dodge-best')) || 0; } catch { this.best = 0; }
    this.hud.setBest(this.best);
    this.player.resetPosition();
    const background = canvas.getChildByName('Background')!;
    const transform = background.getComponent(UITransform) || background.addComponent(UITransform);
    transform.setContentSize(720, 1280);
    const g = background.addComponent(Graphics);
    g.fillColor = new Color(12, 18, 33);
    g.rect(-360, -640, 720, 1280);
    g.fill();
    g.strokeColor = new Color(35, 48, 67);
    g.lineWidth = 1;
    for (let x = -300; x <= 300; x += 60) { g.moveTo(x, -520); g.lineTo(x, 370); }
    for (let y = -520; y <= 370; y += 60) { g.moveTo(-332, y); g.lineTo(332, y); }
    g.stroke();
    g.strokeColor = new Color(66, 129, 125);
    g.moveTo(-332, -520); g.lineTo(332, -520); g.stroke();
  }

  startGame(): void {
    this.player.resetPosition();
    this.spawner.reset();
    this.game.start();
    this.hud.setScore(0);
    this.hud.showPlaying();
    this.player.inputEnabled = true;
  }

  update(deltaTime: number): void {
    if (!this.player || this.game.state !== 'playing') return;
    // Cap resumed-tab frames so obstacles cannot jump through the player.
    const dt = Math.min(deltaTime, 0.05);
    this.player.move(dt);
    this.game.setPlayerX(this.player.node.position.x);
    this.game.step(dt);
    this.spawner.sync(this.game.obstacles);
    this.hud.setScore(this.game.score);
    this.finishIfNeeded();
  }

  private finishIfNeeded(): void {
    if (this.game.state === 'game-over') {
      this.player.inputEnabled = false;
      this.best = Math.max(this.best, this.game.score);
      try { sys.localStorage.setItem('cosmic-dodge-best', String(this.best)); } catch { /* Storage may be unavailable in embedded browsers. */ }
      this.hud.setBest(this.best);
      this.hud.showGameOver(this.game.score);
    }
  }
}
