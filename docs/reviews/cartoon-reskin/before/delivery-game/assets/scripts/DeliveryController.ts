import { _decorator, Component, Game, game, sys } from 'cc';
import { DeliverySession } from './domain/DeliverySession';
import type { RouteId, SessionState } from './domain/GameConfig';
import { DeliveryHUD } from './view/DeliveryHUD';
import { TownMap } from './view/TownMap';

const { ccclass } = _decorator;
const SAVE_KEY = 'delivery-game-save-v1';

@ccclass('DeliveryController')
export class DeliveryController extends Component {
  private session!: DeliverySession;
  private hud!: DeliveryHUD;
  private town!: TownMap;
  private paused = false;
  private lastSavedSecond = -1;
  private storageAvailable = true;
  private recoveryMessage = '';

  start(): void {
    this.session = this.load();
    const canvas = this.node.parent!;
    this.hud = new DeliveryHUD(canvas, {
      accept: id => this.act(() => this.session.acceptOrder(id)),
      depart: route => this.depart(route),
      continue: () => this.act(() => this.session.returnToOrders()),
    });
    this.town = new TownMap(canvas);
    game.on(Game.EVENT_HIDE, this.onHide, this);
    game.on(Game.EVENT_SHOW, this.onShow, this);
    if (this.session.getState().phase === 'arrived') this.session.settle();
    this.render();
    if (this.recoveryMessage) this.hud.showError(this.recoveryMessage);
  }

  update(deltaTime: number): void {
    if (!this.session || this.paused) return;
    let state = this.session.getState();
    if (state.phase !== 'delivering') return;
    this.session.advance(Math.min(Math.max(deltaTime, 0), 0.1));
    state = this.session.getState();
    this.hud.tick(state);
    this.updateMap(state);
    const currentSecond = Math.floor(state.elapsedSeconds);
    if (currentSecond !== this.lastSavedSecond) {
      this.lastSavedSecond = currentSecond;
      this.save();
    }
    if (state.phase === 'arrived') {
      this.session.settle();
      this.save();
      this.render();
    }
  }

  onDestroy(): void {
    game.off(Game.EVENT_HIDE, this.onHide, this);
    game.off(Game.EVENT_SHOW, this.onShow, this);
  }

  private depart(route: RouteId): void {
    this.lastSavedSecond = -1;
    this.act(() => this.session.depart(route));
  }

  private act(action: () => void): void {
    try {
      action();
      this.save();
      this.render();
    } catch (error) {
      this.hud.showError(error instanceof Error ? error.message : '操作未完成，请重试');
    }
  }

  private render(): void {
    const state = this.session.getState();
    this.hud.render(state, state.phase === 'routes' ? this.session.previewRoutes() : []);
    this.hud.setStorageAvailable(this.storageAvailable);
    if (state.activeOrder) this.town.setDestination(state.activeOrder.destinationIndex, state.activeRoute?.id || null);
    else this.town.reset();
    this.updateMap(state);
  }

  private updateMap(state: SessionState): void {
    if (state.activeRoute) this.town.setProgress(state.elapsedSeconds / state.activeRoute.durationSeconds);
  }

  private save(): void {
    try {
      sys.localStorage.setItem(SAVE_KEY, this.session.serialize());
      this.storageAvailable = true;
    } catch {
      this.storageAvailable = false;
    }
    this.hud?.setStorageAvailable(this.storageAvailable);
  }

  private load(): DeliverySession {
    let raw: string | null = null;
    try {
      raw = sys.localStorage.getItem(SAVE_KEY);
    } catch {
      this.storageAvailable = false;
    }
    if (!raw) return new DeliverySession();
    try {
      return DeliverySession.restore(raw);
    } catch {
      // Preserve the original bytes before offering a fresh playable session.
      try { sys.localStorage.setItem(`${SAVE_KEY}-recovery`, raw); } catch { this.storageAvailable = false; }
      this.recoveryMessage = '原存档无法读取，已保留备份；本次从新进度开始';
      return new DeliverySession();
    }
  }

  private onHide(): void {
    this.paused = true;
    this.save();
  }

  private onShow(): void {
    this.paused = false;
    this.lastSavedSecond = -1;
  }
}
