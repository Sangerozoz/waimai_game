# V2 体力、补给、交付静态复核

2026-11-04。只读检查 `V2TripRules.ts`、`V2GameSession.ts`、`V2RouteSession.ts`、`V2EconomySession.ts`、`V2DispatchSession.ts`，并在 owner 落地修复后定向复读。两项确定问题已修并通过静态复核，本指定范围未再发现确定的严重缺陷。不执行测试、typecheck、构建、游戏或任何存档操作；本文不代表运行验收。

## 确定问题与最小修复

1. **P1，已修并静态复核：服务入口缺体力会令手动配送永久卡住。** 路线到达取送点后进入 `service`，规则在体力不足 1 时返回 false，路线保持 `service` 且 `serviceCharged=false`。原 `supply()` 拒绝所有 service，玩家无法恢复体力。已反馈 owner；当前改为只在 `serviceCharged=true` 时拒绝补给，未启动服务可以补给。未运行验证。
2. **P1，已修并静态复核：自动配送缺补给停止后仍消费广告自动时长。** 原 `V2GameSession.tick()` 先调用 `dispatch.tick()` 消费整段自动时长，随后才检查 blocked 与补给预算并 return，停住尾段也被扣除。已通知 owner 与 parent。当前 Dispatch 的 `deferAuto` 只提供本帧 allowance；Route 的所有正常/提前出口返回 `seconds-remaining`；Game 累加既有补给、新自动补给与实际路线动作的已用秒数，并在 finish 中调用 `consumeAutomaticProgress(used)`。因此既有 blocked/policy-off 状态用量为零，当帧途中停止只扣已走部分，完成批次也不扣未走尾段。Dispatch 仍正常前进 fleet 与 frame 时钟，不回退 NPC。实现保留 auto 控制状态以便补给后续行，停止期间不消费权益；此行为只经过静态复核。

## 重点链路结论

- **零体力道路截断**：`TripRules.travel()` 以剩余体力/本段成本返回 fraction；`RouteSession.advance()` 只增加实际比例的 legSeconds，fraction 小于 1 即 return。没有发现体力为零仍走完整段道路的静态路径。
- **跨帧与重复结算**：Game 使用 sequence 的严格递增条件，重复帧 seconds 为零；Route 使用持久化 `serviceCharged` 门闩，成功取送各扣一次，服务持续时间不重复扣点；Dispatch 对 completed 订单返回既有 receipt，经济状态也保存 settledOrderIds。未发现按帧多扣服务体力或重复入账路径。
- **补给动作恢复**：开始动作先经过经济 chargeSupply 扣费，trip 才登记 action；恢复只继续 elapsedSeconds，不重开动作、不重复扣费。Rules 校验 kind/cost/duration/gameSeconds/restore 的合法固定组合。取消配送期间已开启的途中休息动作原先会被 Game.restore 误拒绝，owner 已移除此误拒绝条件；当前动作保留原恢复量和时长，不升级为免费满恢复。此结论针对程序自然产生的状态，不把本地 JSON 校验当防篡改认证。
- **迟到、餐损与锁价**：Route 在每个 dropoff 到达事件即时调用 Game.completeDelivery；该刻取 outcome，后续行程不会追溯改变既有结果。Economy 以已接受 quote.incomeCents 为 base，统一 settleTripIncome 计算 final；Dispatch.restore 以同一 quote 重算并核对 base/final、保留率与评分变化。未发现报价随事后车辆、经验变化重算或后单拖累前单结算的静态路径。

## 已知边界

红灯、途中变天与食品 fragility 分类尚未接入，本轮不重复列缺陷。当前只评审实现链路，不宣称这些规则或完整产品规格已实现。初始评分修正由 owner 处理，不重复列项。
