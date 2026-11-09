# V2车队经营源码接续（2026-11-04）

已新增正式纯逻辑 `delivery-game/assets/scripts/domain/V2FleetSession.ts` 和 `.meta`，扩展 `V2EconomySession.ts`。本模块不改地图、旧OrderBook或正式UI，不操作浏览器或真实存档。**未运行tests/typecheck/build/游戏；下面所有测试均待用户明确阶段完成后执行。**

## 已实现行为

- 车队在线/离线共用 `advanceTo(nowMs)`，传入绝对、安全整数毫秒。不读系统时间；重复区间不推进，系统时间倒退不降低高水位。无工作NPC不烧额度；额度为0停工，保留已接批进度，离线最多消耗离线前已有额度。
- 全队共享现实时间池，同时工作30人也只按一份实际毫秒扣。全队完成量0/60/240/700时容量15/20/25/30分钟；每个主角真实完成事件按该事件的完成后全队量补1/2/2/3分钟。上限成长不额外送满池；无NPC可先存池；NPC完成只增长完成量，不回补。
- 经济保存 `heroCompletionEvents:{id,teamCompletedAfter}[]`；车队保存消费游标及历史基线，恢复不把迁移前历史完成量重新补池。主角每单经经济去重，避免广告/手动/重载双补。
- NPC必须已招募且有唯一配车。以当前图整数重量分布1/2/3、1/2/3、1/3/5、1/3/6、1/3/6及组批机会2/3/5/7/10生成整数批次，总重不超容量。首单从可装分布选择，后续遇到过重候选停止。确定分布由保存的批次序号驱动，重载与推进分段不改变下一批；未引入不可重放的Math.random。
- 每批共享道路时间：`ceil(60000 × 地图距离系数 / 相对速度 × (1+0.25×(订单数−1)))`，地图距离系数1/1.1/1.25/1.45/1.6。每单独立服务 `ceil(30000 × (1−0.15×g))`，`g=((培养等级−1)/29)^0.65`；每个交付时点唯一结算，不按帧或容量直接乘收益。
- `registerFleetOrders(riderId, ids, integerWeights)`由经济验证资产、容量、合法身份与ID，内部生成NPC锁定合同；`settleFleetOrder(id)`只能结算已签合同，不接受外部金额。以图基础费×车辆收入×培养收入计价、分为整数分，无主角经验。错误或金额溢出通过草稿校验整体回滚。
- 切图、车辆改装、人物培养与配车变化不改已接批的报价和耗时；完成旧批后再用新配置。仍在旧批内的车辆禁止配给另一个人；同一人物换车后旧批继续用旧车完成，再接新配置。取消配车同样先完成已接批，之后停工。
- 主角经济新增 `acceptBatch([{id,kind,weightKg,specialCoins?}])`，按总重校验、支持普通多单与100–150整数金币独占专送。`completeDelivery(id)`任意顺序逐单结算，`cancelDelivery(id)`仅取消尚未完成单；批内报价锁住接单时参数。原 `acceptOrdinary`、`activeQuote`首未完、最近receipt重复回调接口保留，`activeQuotes`为全部未完。

## 对接与原子保存

```ts
const economy = new V2EconomySession();
const fleet = new V2FleetSession(economy, nowMs);
// 先把已有经营推进到真实完成时刻，再结算主角单，防新额度回溯使用。
fleet.advanceTo(completionAtMs);
fleet.completeHeroDelivery(orderId); // 同事务结算+逐事件补时
const combined = fleet.serialize();  // 同时含economy和fleet
const resumed = V2FleetSession.restore(combined);
```

若由Dispatch负责主角结算，先 `fleet.advanceTo(nowMs)`，然后 `economy.completeDelivery(id)`、`fleet.syncHeroCompletions()`，并由外层组合草稿一次提交。不能先离线结算主角再把新额度倒灌至旧时间段。多单同帧逐事件消费，不用帧末总数统一算补时。`restore(serialized, sharedEconomy)`只在两份经济快照完全一致时挂接同一个经济对象，方便Dispatch/Reward/车队共享钱包；`fleet.economy`保持引用，不另藏第二个钱包。车队 `advanceTo` 内部也按完整组合草稿验证后才提交经济与车队。

组合schema：`format:county-v2-fleet/version:1/configId`，`economy`为完整经济对象，`fleet`含quotaMs、lastAdvancedAt、heroEventCursor、heroCompletionsSeen、nextBatchId、batches。校验未付合同与经济合同一一相等、已付ID存在、累计重量、到期时间、进度、唯一车/人/批次以及有限整数时间。存储接入方必须一次保存组合快照，不分别保存两个时点的钱包和车队。

## 尚未接入与限制

本文件只说明可调用源码，**未接正式UI/正式路由、30条NPC可见路线、动画或存储端口**。道路/服务为版本化经济模型，尚未用真实路径、天气与餐损校准。确定性重量选择与规划推演的均匀随机采样并非同一统计序列，不能把之前二八曲线模拟时长宣称为本模块运行测得的时长。

ID/主角事件/结算列表会随历史增长，尚未做压缩；组合恢复校验属于数据一致性，不是抗恶意修改存档签名。外部不得直接用replaceFrom任意改资金，正常经营入账必须走已签合同。当前消费方法依旧在主角有未完单时暂停购买/配车；本次未扩展交易期间UI。

## 待执行用例

`delivery-game/tests/v2-fleet.test.cjs` 已写：无NPC存池与重复回调、共享秒数、额度耗尽保留进度、在线分段与离线同收益、时钟回退/重复区间、切图/升级/卸车锁旧价、整数容量、新批用新图、60/240/700边界无赠池、非有限时间/错配快照/伪造报价拒绝、主角多单乱序与取消、旧批车辆占用、迁移历史基线。

尚未加入他人负责的统一runner；接入代理应将本文件作为待执行测试注册，授权后再运行。没有任何“已通过”结论。
