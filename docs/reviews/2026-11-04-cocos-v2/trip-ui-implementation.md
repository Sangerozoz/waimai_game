# 第四批主角行程 UI / Runtime 接入

本批仅写源码和待执行测试。未执行 tests、typecheck、build、游戏页面或真实存档操作；未声称验证通过。

## 实际调用链

- 首页 / 订单大厅 HUD → `runtime.tripState` → `V2GameSession.tripState`：体力、评价、天气、动作进度、零体力提示、余单期限。
- 原地补给 → `runtime.supply(kind)` → `mutate` 候选恢复、同步时间 → `session.supply(kind)` → 序列化校验、提交同一组合存档 → 发布 live。UI 不扣费、不修改体力、不另存动作。
- 水 1 金币 / 20 点 / 1 秒；面 3 金币 / 70 点 / 3 秒；免费休息有单 10 秒 / 20 点、无单 20 秒 / 满。显示封顶后的恢复量，满体力及已有动作时关闭补给按钮；业务层仍须校验。
- 自动付费明确开关、总预算 0 / 5 / 10 金币、品类水 / 面 → `runtime.configureAutoSupply(policy)` → 同一 `mutate` 事务。显示真实累计消费。默认由领域提供关闭政策，UI 不自动开启，不增加广告奖励。
- 非首页、选路、补给选择 → `runtime.setPaused(true)`；继续、出发、取餐、确认补给 → 首页 → `setPaused(false)`。补给确认后执行真实动作，不因保留选择面板而永久暂停。Runtime 仅传递暂停标志，NPC墙钟结算由组合 Session 继续。
- 地图位置始终来自 routeSnapshot.position；没有补给传送或重置路线。取消后回首页。

## 测试与限制

`delivery-game/tests/v2-trip-ui.test.cjs` 已编写：候选保存失败不发布、单次供给转发、满体力禁购、确认补给关闭面板、自动开关与分预算。独立测试通过 Cocos TypeScript 转译及模拟 Cocos 端口加载，不在默认 run-v2 列表中；待阶段完成明确授权后执行。

Bootstrap 现有显式 V2 新建 / 恢复和真实存档门禁保留，不需要新增隐式开启。六页配色、结构、地图路网和美术未改。完整高阶吃喝、库存选择、多余单滚动详情、正式路线风险细节、真实广告 SDK 与美术验收仍未完成；当前余单面板最多显示四条摘要。

## 回执与账目口径

已对齐 `V2DeliveryReceipt extends Partial<V2FinalSettlement>`：迟到秒数、餐损程度、评价变化、`baseIncomeCents` 原价、`incomeCents` 实收和两者差额。首页逐单反馈五秒内自动消失，不触发行程暂停；完成整批后显示该批真实回执收入合计。账单逐行保留同口径结果，另列 `tripState.supplySpentCents` 的全档补给累计。UI 只读展示，不再扣迟到、餐损、补给或重发结算。

当前补给字段为累计值，尚无每批补给起始快照，因此未把累计支出错误地从单批收入中扣成“净赚”。今日、近7日及完整分类 ledger 尚未完成，不虚构对应金额。默认测试 runner 未修改，Bootstrap 无需变更。
