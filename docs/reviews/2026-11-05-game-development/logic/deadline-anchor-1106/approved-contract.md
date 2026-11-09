# 期限锚点最小修正：PM冻结规格

依据正式V1第49行“期限从出发建立并保存”、第57/59行的三类时间分离，采用开发A DEADLINE-ANCHOR-CONTRACT-1106 的最小方案A，作为本轮产品收口的限定实现澄清，而非重新设定价格或奖励。

## 冻结决策

1. Route.phase==='planned' 尚未出发。已确认补给/休息仍耗原本现实动作时长，按原价格/库存/active分类恢复；但这些后续动作的名义游戏秒不加入尚未启动的配送行程钟。仅planning选择/阅读冻结和确认动作现实耗时不是同一件事。
2. 已出发的 travelling/pickup/service/ready 等状态完全保留原补给计时，尤其ready只是已出发后等待，不等于未出发。无单流程保持原默认行为。
3. deadlineGameSeconds已有相对预算D保持不变，不在beginTrip、restore、ETA或详情里重建；新批G=0预写预算、出发后才推进G是可接受的等价表示，不新增绝对钟表字段。
4. 对旧planned且已有G0>0：G0/D/动作elapsed/价格/库存/已付价值全部保留，不回滚已用游戏秒、不延长旧期限、不补偿历史结果；仅停止今后planned补给再增加G。旧有效已出发合同、位置、服务和凭证都不变。这是前瞻修正，不宣称完全追溯修复旧进度。
5. 允许精确加法签名 V2TripRules.advanceSupply(seconds:number,advanceTripClock:boolean=true):number；参数在任何变更前验证为boolean，原单参数调用维持true行为。仅条件控制this.s.gameSeconds增长，不变更action的nominal gameSeconds/现实elapsed/恢复/余秒/费用/库存。
6. Game.tick唯一调用改为 this.trip.advanceSupply(seconds,this.route.progress.phase!=='planned')；真实used、自动授权消费、wallStart/offset、NPC逐笔推进、同帧自动在补给后出发均保留。该同帧补给发生时planned，随后真正道路部分正常计G。

写集仅domain/V2TripRules.ts、map-sample/V2GameSession.ts及专属logic/deadline-anchor-1106报告。不得修改Route/Game查询DTO、Runtime/UI/存档schema/报价/参数/地图。原Game4/Route2/Trip2版本和所有恢复验证不弱化，不读写真实或合成档。

该规格是PM根据既定目标作出的最小实施选择；源码尚未写，不等于独立审查/行为通过。独立复审与后续必要构建单独进行；不把本增量混入已经生成的v2-product-eta-1106历史候选。
