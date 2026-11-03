import { _decorator, Color, Component, EventKeyboard, EventMouse, EventTouch, Graphics, input, Input, KeyCode, UITransform, Vec3 } from 'cc';
import { FIELD } from './GameSession';
import { MINT } from './UI';

const { ccclass } = _decorator;

@ccclass('PlayerController')
export class PlayerController extends Component {
  inputEnabled = false;
  private keys = new Set<KeyCode>();
  private mouseHeld = false;

  onLoad(): void {
    const transform = this.node.getComponent(UITransform) || this.node.addComponent(UITransform);
    transform.setContentSize(FIELD.playerWidth, FIELD.playerHeight);
    const g = this.node.addComponent(Graphics);
    g.fillColor = MINT;
    g.roundRect(-32, -25, 64, 50, 14);
    g.fill();
    g.fillColor = new Color(98, 239, 200, 65);
    g.roundRect(-22, -41, 44, 7, 3);
    g.fill();
  }

  onEnable(): void {
    input.on(Input.EventType.KEY_DOWN, this.keyDown, this);
    input.on(Input.EventType.KEY_UP, this.keyUp, this);
    input.on(Input.EventType.TOUCH_START, this.touch, this);
    input.on(Input.EventType.TOUCH_MOVE, this.touch, this);
    input.on(Input.EventType.MOUSE_DOWN, this.mouseDown, this);
    input.on(Input.EventType.MOUSE_MOVE, this.mouseMove, this);
    input.on(Input.EventType.MOUSE_UP, this.mouseUp, this);
  }

  onDisable(): void {
    input.off(Input.EventType.KEY_DOWN, this.keyDown, this);
    input.off(Input.EventType.KEY_UP, this.keyUp, this);
    input.off(Input.EventType.TOUCH_START, this.touch, this);
    input.off(Input.EventType.TOUCH_MOVE, this.touch, this);
    input.off(Input.EventType.MOUSE_DOWN, this.mouseDown, this);
    input.off(Input.EventType.MOUSE_MOVE, this.mouseMove, this);
    input.off(Input.EventType.MOUSE_UP, this.mouseUp, this);
    this.keys.clear();
    this.mouseHeld = false;
  }

  move(deltaTime: number): void {
    if (!this.inputEnabled) return;
    const left = this.keys.has(KeyCode.ARROW_LEFT) || this.keys.has(KeyCode.KEY_A);
    const right = this.keys.has(KeyCode.ARROW_RIGHT) || this.keys.has(KeyCode.KEY_D);
    this.setTargetX(this.node.position.x + (Number(right) - Number(left)) * 680 * deltaTime);
  }

  setTargetX(x: number): void { this.node.setPosition(Math.max(-300, Math.min(300, x)), FIELD.playerY, 0); }
  resetPosition(): void { this.keys.clear(); this.mouseHeld = false; this.setTargetX(0); }
  private keyDown(event: EventKeyboard): void { this.keys.add(event.keyCode); }
  private keyUp(event: EventKeyboard): void { this.keys.delete(event.keyCode); }
  private touch(event: EventTouch): void {
    if (!this.inputEnabled) return;
    const p = event.getUILocation();
    const local = this.node.parent!.getComponent(UITransform)!.convertToNodeSpaceAR(new Vec3(p.x, p.y));
    this.setTargetX(local.x);
  }
  private mouseDown(event: EventMouse): void {
    if (event.getButton() !== EventMouse.BUTTON_LEFT) return;
    this.mouseHeld = true;
    this.mouseMove(event);
  }
  private mouseUp(): void { this.mouseHeld = false; }
  private mouseMove(event: EventMouse): void {
    if (!this.inputEnabled || !this.mouseHeld) return;
    const p = event.getUILocation();
    const local = this.node.parent!.getComponent(UITransform)!.convertToNodeSpaceAR(new Vec3(p.x, p.y));
    this.setTargetX(local.x);
  }
}
