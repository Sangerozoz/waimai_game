# 订单专注与暂停开发交付

**已实现，未测试，待用户说“阶段完成”后集中测试。** 依据2026-10-30-order-focus-pause-design.md与任务执行；唯一生产脚本修改MapSample.ts。保留M2锁/保存/时钟、schema5以及新头像、D档车和金边按钮。未运行测试、typecheck、回归、浏览器渲染或独立复验；未操作用户游戏/存档，未commit/push。

## 实际交互

- 活动订单存在时navigation不创建底座或任何导航按钮（含中央订单）；正常接单并保存成功后重建进入专注界面，取餐前取消并保存成功后重建首页恢复底栏。完成结算finish清理后亦恢复。订单卡右上关闭已移除，重建时活动卡强制展开；大厅和其他弹窗关闭保留。
- 取消继续复用OrderBook业务守卫：planning/toPickup/awaitPickup可取消并保实际道路anchor，picking及之后拒绝。没有更改费用/存档/旧订单兼容规则。
- 有活动订单时在头像经验条下增加“暂停”按钮，独立留间距，采用公共次按钮。暂停先收口暂停前在线区间（已有pending则不修改），清空在线起点、重置ForegroundClock、取消定位动画，保存当前快照。
- “游戏已暂停”弹窗只有“继续游戏”和“退出游戏”，没有X或遮罩关闭；模态BlockInputEvents阻挡背后动作。暂停与入口门禁同时阻止业务act、行驶、服务、在线时长及自动阶段弹窗；引擎UI继续运行，存档失败重试可以处理。失败说明在暂停卡滚动区展示，不用会盖住按钮的大toast。
- 继续先提交或重试同一冻结快照，失败仍留暂停；成功清门禁，前台时钟重置并丢恢复首帧，不补暂停区间，随后恢复当前订单或原回执。
- 退出先save，成功才window.location.reload；失败保留暂停/待提交状态并可再次点击或由既有重试机制保存，自动重试成功本身不触发刷新。非Web宿主保守回到同一内存订单的继续入口。

## 读档与暂停边界

不新增保存字段、schema或sessionStorage标志。所有已有活动（包括旧profile、到达/结算态）在加载后第一帧之前设置entryGate，展示轻量“继续配送/继续游戏”入口；不会自动开跑/取餐/结算，明确点击继续并保存成功才恢复。退出后刷新与普通重开共用此入口，因此无需不受保护的退出标记；订单本身及精确elapsed/serviceElapsed仍由已有保存底座持久化。

paused/entryGate是独立内存交互状态，不把OrderBook.mode改成旧paused模式，避免旧档restore把paused转running而解除门禁。后台show不清门禁，resize重建最后恢复不可关闭暂停/继续入口；hide不记暂停在线区间。pending提交重试在暂停冻结检查之前运行，快照保持不变；操作禁止直到保存成功。未知未来档/未持写锁仍由原底座只读保护，继续/退出也必须save成功。

## 构建与证据

`npm run build:map --prefix delivery-game`实际包装退出0；build.log记录2026-10-30 13:52:55 Finished。构建到delivery-game/build/map-sample。4181静态服务首页HTTP200，响应index和本构建index的SHA记录static-http.json；仅静态HTTP，没有浏览器启动或存储访问。

before/与before-sha.json记录本轮改前基线（含全部前期未提交工作）；production.patch为差异，final-source-sha.json、build-manifest.json和delivery.json记录最终源码/构建指纹和退出码。接口/存档schema没有新增，暂停/继续、保存失败、后台/resize和旧活动读档入口实际行为均未测试，不能把构建完成写成体验验收通过。
