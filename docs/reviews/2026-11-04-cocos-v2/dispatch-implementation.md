# V2统一调度门面实现交接

新增 `delivery-game/assets/scripts/domain/V2DispatchSession.ts` 与.meta，以及待执行 `delivery-game/tests/v2-dispatch.test.cjs`。无cc或存储依赖；消费另一开发的V2EconomySession多单报价API、V2FleetSession和RewardSession，不修改地图/旧OrderBook。不是已完成正式场景接入或可玩验收。

## 统一业务入口

- `new V2DispatchSession(port, nowSeconds=0)`；`port.verifyArrival(order, arrivalToken):boolean`由真实地图配送适配器提供，必须是可重复、无副作用的验证，只有明确true才允许完成。模块不靠计时伪造到达。
- `acceptBatch([{id,kind:'ordinary'|'special',weightKg}])`：实际ID唯一，正有限重量，累计重量不得超过当前配车；普通单可多单；专送独占且须广告授权，价格取RewardSession不可由调用方随便传入。返回锁定的经济报价。
- `completeDelivery(id,arrivalToken,nowSeconds可选)`：逐单完成，支持任意顺序，历史已完成幂等返回原收据。经济完成链统一发一次金币/经验，并由Fleet.syncHeroCompletions消费真实主角事件补经营额度。传now时先推进旧额度到完成时刻，再补新额度，避免回溯经营；不传时用最近frame时刻。
- `cancelRemaining()/cancelBatch()`取消本批全部未完成订单；`cancelDelivery(id)`验证指定订单属于活批未完后同样取消全部余单，符合已确认V1批次取消语义。已完成收益/经验保留，未完成无奖；本会话历史取消ID不可重新接取。
- `command(discriminatedUnion)`支持buyVehicle/modelId、hireRider/riderId、assignVehicle/riderId/vehicleId、buyMap/mapId、selectMap/mapId、upgradeVehicle/vehicleId、upgradeRider/riderId，均在同组合事务内。活主角批次期间拒绝资产变化；NPC合同锁定由经济模块负责。
- `enterLobby`、`requestAd`、`resolveAd`透传奖励事务；真实SDK仍是接口。自动权益成功开始控制模式，`stopAutomation`保留剩余预算转手动，`resumeAutomation`有剩余预算且无专送批次才可恢复。
- `tick(frameSequence,nowSeconds,foreground,paused)`：绝对秒，Fleet转换`floor(seconds*1000)`；同frame同参数重复返回0推进，不重复扣权益；同frame不同参数拒绝。新frame系统时间倒退仅0推进且不降时间高水位。主角仅前后台连续前台非暂停区间扣时，后台/暂停、真实恢复首帧不追赶。广告待播冻结主角自动预算。600秒归零末帧截断返回`autoRunSeconds`并转manual，在途单保留，不能自动免费跑完余批。时间不会自动调用completeDelivery。
- `economyState`、`fleetState`返回克隆读模型；`snapshot()/serialize()`包含经济、车队、奖励、历史订单/报价/收据、活批次及帧计时。

## 事务与恢复

每次变更先恢复整体草稿，挂接同一经济引用到Fleet，执行动作及主角事件补额度，验证后统一交换内存状态。错误不提交半个经济/奖励/车队状态。Fleet恢复还核对自身内嵌经济与组合经济完全一致。Dispatch验证活批次订单集合、逐单剩余经济报价、累计容量、奖励批次身份/类型、专送定价、完成收据/入账ID、帧计数等。

`restore(serialized,port)`用于实际持久恢复，首tick重置主角时间差；工作内存事务克隆使用`restore(serialized,port,{preserveClock:true})`。`clockNeedsRebase`随快照保留，因此实际恢复后再克隆不会丢失待重置标志，也不会因每帧克隆永远不扣自动时长。Runtime开发已收到此契约。

调用端每次业务动作前应在同一候选事务先tick到当前时刻，再执行动作/保存，避免新NPC额度用于动作前时间。保存成功后必须把预tick的autoRunSeconds交真实路线port一次，不能扣时却丢弃推进；业务/保存失败则整候选不生效。Runtime代理正在实施此调用链。

## 待执行验证与边界

已编写容量/重复ID/虚假到达拒绝、逐单收据幂等、部分完成恢复、取消整批余单、专送权益/价格/独占、失败事务无半提交、后台暂停冻结、末帧截断、恢复不补跑、重复frame/倒退时钟、工作克隆保留时钟、主角补车队额度一次、组合经济不一致拒绝等行为用例。遵照阶段测试要求，未运行任何tests/typecheck/build/游戏/存档；仅静读源码，不能称验证通过。

尚无真实SDK或正式地图到达适配器。Fleet时长/订单供给属于经济规划模型，不冒充地图可见骑手实际路线。自动选单/路线推进由上层接入；本模块不生成地图订单、不自动宣称抵达。组合快照不含外部路线port的内部进度，保存后投递推进期间崩溃仍可能导致业务时长与地图位置不一致，需下一阶段路线事务令牌/联合持久化解决；本轮只保证模块组合业务状态原子，不声称跨引擎位置原子。真实旧档迁移、SDK信任与防作弊、长期历史压缩、自动补给授权、正式UI、集中游戏验证仍是后续工作。

待执行统一入口`node delivery-game/tests/run-v2.cjs`已纳入经济/适配/车队/调度/奖励，统一先严格编译依赖；奖励测试另用同一COCOS_CREATOR中的TypeScript隔离transpile模块。此入口未执行。运行控制器还须实际挂载场景，真实SDK/路线与体力、天气、餐损、迟到、自动补给预算风险未接，不能以经济报价直接宣称完整V1风险结算已实现。
