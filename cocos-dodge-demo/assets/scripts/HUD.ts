import { _decorator, Color, Component, Label, Node } from 'cc';
import { box, INK, MINT, MUTED, text } from './UI';

const { ccclass } = _decorator;

@ccclass('HUD')
export class HUD extends Component {
  onRestartRequested: (() => void) | null = null;
  private scoreLabel!: Label;
  private bestLabel!: Label;
  private overlay!: Node;
  private titleLabel!: Label;
  private detailLabel!: Label;
  private buttonLabel!: Label;

  onLoad(): void {
    text(this.node, 'Eyebrow', 'C O S M I C   D O D G E', 20, 0, 567, MINT);
    this.scoreLabel = text(this.node, 'ScoreLabel', '0', 70, 0, 495);
    this.bestLabel = text(this.node, 'BestLabel', 'BEST  0', 19, 0, 430, MUTED);
    text(this.node, 'Controls', '← → / A D  ·  拖动左右躲避', 21, 0, -570, MUTED);
    this.overlay = box(this.node, 'GameOverlay', 590, 390, new Color(24, 35, 54, 252), 0, 10, 26);
    this.titleLabel = text(this.overlay, 'Title', '星际闪避', 48, 0, 108);
    this.detailLabel = text(this.overlay, 'Detail', '躲开红色障碍，每避开一个 +1 分', 22, 0, 30, MUTED);
    const button = box(this.overlay, 'RestartButton', 430, 76, MINT, 0, -82, 18);
    this.buttonLabel = text(button, 'ButtonLabel', '开始游戏', 28, 0, 0, new Color(13, 28, 32));
    button.on(Node.EventType.TOUCH_END, this.requestStart, this);
  }

  setScore(score: number): void { this.scoreLabel.string = String(score); }
  setBest(best: number): void { this.bestLabel.string = `BEST  ${best}`; }
  showPlaying(): void { this.overlay.active = false; }
  showGameOver(score: number): void {
    this.titleLabel.string = '下次躲得更远';
    this.titleLabel.color = INK;
    this.detailLabel.string = `本次躲过 ${score} 个障碍`;
    this.buttonLabel.string = '再来一次';
    this.overlay.active = true;
  }
  private requestStart(): void { this.onRestartRequested?.(); }
}
