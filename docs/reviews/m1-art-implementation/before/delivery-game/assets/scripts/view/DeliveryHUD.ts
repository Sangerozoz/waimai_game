import { Graphics, Label, Node } from 'cc';
import type { Order, RouteId, RoutePreview, SessionState } from '../domain/GameConfig';
import { button, color, money, node, Palette, panel, text } from './Widgets';
import { PLACE_NAMES } from './TownMap';

interface Actions {
  accept(orderId: string): void;
  depart(route: RouteId): void;
  continue(): void;
}

export class DeliveryHUD {
  private readonly content: Node;
  private readonly cash: Label;
  private readonly rating: Label;
  private readonly level: Label;
  private readonly saved: Label;
  private progress: Graphics | null = null;
  private timer: Label | null = null;
  private storageAvailable = true;

  constructor(parent: Node, private readonly actions: Actions) {
    panel(parent, 'Background', 0, 0, 720, 1280, Palette.page, 0);
    const badge = panel(parent, 'County', -230, 594, 190, 34, Palette.lightGreen, 16);
    text(badge, '县城 · 起步配送站', 0, 0, 15, Palette.green, 176, 'center', true);
    text(parent, '送外卖', -165, 544, 42, Palette.ink, 320, 'left', true);
    text(parent, '把每一单，稳稳送到。', 163, 538, 18, Palette.muted, 300, 'right');
    this.cash = this.stat(parent, -224, '钱包余额', '¥100.00', Palette.green);
    this.rating = this.stat(parent, 0, '顾客评价', '80 / 100', Palette.ink);
    this.level = this.stat(parent, 224, '经验等级', 'Lv.1', Palette.ink);
    this.content = node(parent, 'FlowContent');
    this.saved = text(parent, '进度自动保存在本机', 0, -603, 15, Palette.muted, 650, 'center');
  }

  render(state: SessionState, routes: RoutePreview[]): void {
    this.cash.string = `¥${money(state.player.cashCents)}`;
    this.rating.string = `${state.player.rating} / 100`;
    this.level.string = `Lv.${state.player.level} · ${state.player.experience} EXP`;
    for (const child of [...this.content.children]) child.destroy();
    this.content.removeAllChildren();
    this.progress = null;
    this.timer = null;
    if (state.phase === 'orders') this.orders(state);
    else if (state.phase === 'routes') this.routes(state, routes);
    else if (state.phase === 'delivering') this.delivering(state);
    else if (state.phase === 'result') this.result(state);
    this.updateSavedLabel();
  }

  tick(state: SessionState): void {
    if (!this.progress || !this.timer || !state.activeRoute) return;
    const elapsed = Math.min(state.elapsedSeconds, state.activeRoute.durationSeconds);
    const fraction = elapsed / state.activeRoute.durationSeconds;
    this.progress.clear();
    this.progress.fillColor = color(Palette.green);
    if (fraction > 0) {
      this.progress.roundRect(-270, -7, Math.max(14, 540 * fraction), 14, 7);
      this.progress.fill();
    }
    this.timer.string = `${elapsed.toFixed(1)} / ${state.activeRoute.durationSeconds.toFixed(1)} 秒`;
  }

  setStorageAvailable(available: boolean): void {
    this.storageAvailable = available;
    this.updateSavedLabel();
  }

  showError(message: string): void {
    this.saved.string = message;
    this.saved.color = color(Palette.red);
  }

  private updateSavedLabel(): void {
    this.saved.string = this.storageAvailable ? '进度自动保存在本机' : '本机存档不可用，请保持页面开启';
    this.saved.color = color(this.storageAvailable ? Palette.muted : Palette.red);
  }

  private stat(parent: Node, x: number, title: string, value: string, fill: string): Label {
    const card = panel(parent, 'PlayerStat', x, 464, 208, 86, '#FFFDF7', 17, Palette.border);
    text(card, title, 0, 22, 15, Palette.muted, 178, 'center');
    return text(card, value, 0, -11, 26, fill, 180, 'center', true);
  }

  private heading(title: string, subtitle: string): void {
    text(this.content, title, 0, 52, 28, Palette.ink, 650, 'left', true);
    text(this.content, subtitle, 0, 15, 16, Palette.muted, 650);
  }

  private orders(state: SessionState): void {
    this.heading(state.tutorialComplete ? '挑一单，出发吧' : '先把第一单送到',
      state.tutorialComplete ? 'D 级车 · 箱体 5 公斤 · 基础金额还将计算配送加成' : '点击接单，再从系统提供的道路里选一条出发');
    state.orders.forEach((order, index) => this.orderCard(order, -56 - index * 100));
    if (!state.tutorialComplete) {
      const note = panel(this.content, 'FirstOrderNote', 0, -216, 656, 108, Palette.lightGreen, 18);
      text(note, '一单就能学会', 0, 22, 22, Palette.green, 600, 'center', true);
      text(note, '选路看时间和风险，送达后就能领到本单收入。', 0, -16, 17, Palette.green, 610, 'center');
    }
    text(this.content, `已完成 ${state.player.completedOrders} 单 · 选道路本身不会扣评价`, 0, -556, 16, Palette.muted, 650, 'center');
  }

  private orderCard(order: Order, y: number): void {
    const card = panel(this.content, `Order-${order.id}`, 0, y, 656, 88, Palette.paper, 18, Palette.border);
    const urgent = order.type === 'urgent';
    const accent = panel(card, 'OrderIcon', -293, 0, 42, 48, urgent ? Palette.lightGold : Palette.lightGreen, 11);
    text(accent, urgent ? '急' : '餐', 0, 0, 22, urgent ? Palette.gold : Palette.green, 36, 'center', true);
    text(card, order.foodName, -102, 19, 21, Palette.ink, 310, 'left', true);
    const fragility = order.fragility === 'fragile' ? '易碎' : order.fragility === 'durable' ? '耐造' : '普通餐品';
    text(card, `${fragility} · ${order.weightKg}kg · ${order.deadlineSeconds}秒内送达`, -90, -15, 14, Palette.muted, 334);
    text(card, `¥${money(order.basePriceCents)}`, 162, 10, 23, urgent ? Palette.gold : Palette.green, 130, 'center', true);
    text(card, urgent ? '加急配送' : '普通配送', 162, -20, 13, Palette.muted, 124, 'center');
    button(card, '接单', 273, 0, 84, 50, () => this.actions.accept(order.id));
  }

  private routes(state: SessionState, routes: RoutePreview[]): void {
    const order = state.activeOrder!;
    this.heading('这单，选哪条路？', `${order.foodName} → ${PLACE_NAMES[order.destinationIndex % PLACE_NAMES.length]} · ${order.deadlineSeconds}秒内送达`);
    for (let index = 0; index < routes.length; index++) {
      const route = routes[index];
      const card = panel(this.content, `Route-${route.id}`, 0, -76 - index * 145, 656, 128, Palette.paper, 18, Palette.border);
      const routeColor = route.id === 'fast' ? Palette.gold : route.id === 'main' ? Palette.blue : Palette.green;
      panel(card, 'RouteMark', -312, 0, 6, 76, routeColor, 3);
      text(card, route.name, -130, 35, 25, Palette.ink, 350, 'left', true);
      text(card, `${route.durationSeconds.toFixed(1)} 秒 · 餐损风险 ${Math.round(route.damageChance * 100)}%`, -100, -4, 18, Palette.muted, 410);
      text(card, route.lateSeconds > 0 ? `预计晚到 ${route.lateSeconds.toFixed(1)} 秒，超时会影响评价` : '预计准时送达', -85, -39, 15,
        route.lateSeconds > 0 ? Palette.red : Palette.green, 440);
      button(card, '走这条', 252, 7, 118, 56, () => this.actions.depart(route.id), routeColor);
    }
    text(this.content, '点击路线即可出发 · 选路时不计时', 0, -556, 17, Palette.muted, 650, 'center');
  }

  private delivering(state: SessionState): void {
    const order = state.activeOrder!;
    const route = state.activeRoute!;
    this.heading('骑手正在路上', `目的地：${PLACE_NAMES[order.destinationIndex % PLACE_NAMES.length]} · ${route.name}`);
    const card = panel(this.content, 'DeliveryProgress', 0, -166, 656, 302, Palette.paper, 22, Palette.border);
    text(card, '这一单，正在认真送达', 0, 94, 27, Palette.ink, 600, 'center', true);
    this.timer = text(card, '', 0, 34, 34, Palette.green, 590, 'center', true);
    panel(card, 'ProgressTrack', 0, -30, 540, 14, Palette.lightGreen, 7);
    this.progress = node(card, 'ProgressFill', 0, -30).addComponent(Graphics);
    text(card, route.lateSeconds > 0 ? `预计晚到 ${route.lateSeconds.toFixed(1)} 秒，仍可完成订单` : '预计准时 · 到达后自动结算', 0, -91, 18,
      route.lateSeconds > 0 ? Palette.red : Palette.muted, 590, 'center');
    text(this.content, '离开页面会保存进度，回来后继续配送', 0, -396, 17, Palette.muted, 650, 'center');
    this.tick(state);
  }

  private result(state: SessionState): void {
    const receipt = state.receipt!;
    const clean = receipt.damage === 'none' && receipt.lateSeconds === 0;
    this.heading(clean ? '稳稳送到了！' : '订单已送达', '钱、评价和经验已经结算，本单进度已保存');
    const card = panel(this.content, 'Receipt', 0, -221, 656, 444, Palette.paper, 22, Palette.border);
    text(card, '本单收入', 0, 177, 17, Palette.muted, 590, 'center');
    text(card, `+ ¥${money(receipt.incomeCents)}`, 0, 112, 55, Palette.green, 590, 'center', true);
    panel(card, 'Divider', 0, 52, 568, 2, Palette.border, 0);
    const change = receipt.ratingDelta > 0 ? `+${receipt.ratingDelta}` : String(receipt.ratingDelta);
    text(card, `评价 ${change}     经验 +${receipt.experienceGained}     完成第 ${receipt.completedOrders} 单`, 0, 18, 20, Palette.ink, 590, 'center');
    receipt.summary.slice(0, 3).forEach((line, index) => text(card, line, 0, -40 - index * 32, 18, Palette.muted, 568, 'center'));
    button(card, '继续接单', 0, -164, 566, 64, () => this.actions.continue());
    text(this.content, state.tutorialComplete ? '下一单已经在等你' : '操作就这么简单，接下来由你挑单', 0, -510, 17, Palette.muted, 650, 'center');
  }
}
