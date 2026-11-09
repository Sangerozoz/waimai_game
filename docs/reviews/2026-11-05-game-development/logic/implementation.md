# 游戏逻辑实际开发交付

日期：2026-11-05。负责人线程 thr_tdwjukd785，父PM thr_axf6i4e89t。状态：源码已写、静态追踪；所有行为未运行验证，不是阶段完成。

## 权威与读取

先读AGENTS及implementation-baseline最新覆盖；本轮按正式V1第3–9、12节和11-03需求登记解释流程，报价/培养/唯一slot以baseline最新覆盖为准。先枚举确认dispatch-implementation、route-integration、trip-rules-implementation、core-static-review、trip-static-review五文件存在，再检查对应实现。规则→符号→缺口矩阵在requirements-matrix.json，写代码前已登记根因与待执行case。

旧广告pending超时、自动成功与专送交错、service未扣体力时不能补给、blocked仍扣自动权益均已有后续源码处理；六补给、库存、批次成本冻结也已实现。不恢复旧迁档、旧购买资格或旧参数待办。

## 本次源码改动

1. `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2GameSession.ts:46`：tick改为跨动作/批次的许可秒数推进循环。原来单次route.advance完成一批即返回，即使本帧还有许可秒数，下一批也要等下一帧，运行效率依赖帧划分。现在自动完成普通批后沿合法容量/原路规则继续组下一批；缺体力有明确补给授权时消费实际补给动作，无授权停止；统计实际使用秒数并封顶本帧许可。自动余额归零后仍不把同帧余时转手动行驶。
2. 同文件`:78`：已接受的planned普通批次在自动控制下使用既有routeChoices/beginTrip启动。原来自动只处理idle/finished，新权益或恢复自动碰到planned时永久无进展。专送manual约束由Dispatch原实现继续执行；不请求或模拟广告。
3. 同文件`:18`、`:60`、`:82`：统一检查已配车辆与可推进阶段。原来空闲卸车后每次tick仍计算effects，抛“主角未配车”使候选事务回滚，连NPC推进也不能提交。现在空闲tick无需主角效果，无车自动不启动批次，保留权益；normalCandidates返回[]，specialCandidate返回null。既有补给动作仍可完成；无配车不能接单出发。
4. `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2RouteSession.ts:76`：choices从总距离扣除origin有向边已走部分。原来取消后实际从边中途续走，但展示距离、体力预测、首15单组合门槛计入整条起始边；现与fastest和实际legSeconds起点统一。道路、宽度、方向、连通和任何边界未修改。

## 原链路静态追踪结果

- Dispatch.acceptBatch逐ID核对、总重<=实际容量，无固定3单数量门槛；活批拒绝追加。Route每单先取后送；pickup主动进入服务，dropoff服务产生trip/order/stop绑定凭证后立即结算。
- Dispatch完成收据和经济settledOrderIds双重幂等；Trip.delivered保存评价，重复交付取原收据，批次结束无第二次金币/经验发放。
- cancelDelivery验证活批未完ID并取消全部余单；Route保留有向边位置，Trip冻结已发生成本。已送收据/收入/经验及已补额度不撤回，未完不补。
- travel返回真实耗尽比例；serviceCharged门闩阻止重入重复耗能；补给action先扣一次并保存进度，恢复只继续动作。后台、暂停及恢复首tick冻结主角行程，不补跑。
- Fleet在线/离线共用advanceTo高水位和quotaMs；消耗全队时间不乘人数，NPC完成不补额度。syncDraft按heroCompletionEvents游标补一次。NPC收入/速度/服务减时读取冻结合同；本次未改经济参数和合同公式。
- 迟到、累积餐损在真实到达时计算；Dispatch从锁定base和outcome核对final，逐单已结算后不追溯。红灯等缺口见remaining。

## 接口影响及验证边界

只写上述两个源码文件及logic报告。未改公开方法签名、快照format/version/字段，未写其他owner文件；无车候选查询的行为变为空结果。没有新增模块或meta。现有snapshot恢复及Runtime候选保存机制继续使用原入口。

仅静读/搜索源码、读取静态city JSON结构、查看自身文本；未运行tests/typecheck/回归/Creator构建/服务/真实游戏或读改用户存档。remaining登记的case均待阶段集中执行；不能称通过。未commit/push，保留其他dirty/untracked。

## 风险与PM协调

一次长tick可串多批，因此每帧克隆/全历史校验成本增加；600秒许可限制自动推进，但长期性能未测。NPC与主角的帧内事件顺序仍有确定缺口；不宣称主循环整体或分帧不变性已完成。原路蓝框及四张运行地图、SDK等边界见remaining；父PM已收两次事实消息。

## U01优先续修：恢复时重复重算整批路由

父PM收到Runtime owner线索后明确要求优先修复。已静态核实：Route.restore的travelling/pickup/service/finished分支原先每次`JSON.stringify(route.makeLegs(preference))`，makeLegs逐Stop调用有向RoadRouter.find；Runtime每帧候选恢复与提交前恢复验证会重复触发。首次四项修改保留。

本轮新增源码：`V2RouteSession.ts:19`扩PreparedMap私有缓存，`:82`新增expectedLegsJSON，`:148`恢复比较改用权威expected字符串。缓存每个实际PreparedMap/router独立，不以存档mapKey摘要作缓存身份；key是完整origin/stops/preference JSON，值只能是当前router实际makeLegs输出的JSON。缓存miss仍完整计算；所有恢复无论来源均将输入legs完整序列化并逐字比较权威期望，原结构/anchor/cursor/进度/凭证/组合校验不删。缓存不会从输入legs填值，也不共享可变legs数组。

边界：LRU最多16项，每项key+expected≤262144字符，超限只计算验证不缓存；CityData释放后由现有WeakMap释放整组。沿用已有immutable loaded CityData契约；不同城市对象/几何替换的新对象各自生成router和缓存，即使弱mapKey碰撞也不共享缓存。本轮没有新增对同一CityData对象原地编辑路网的支持；当前prepare本来即缓存该对象，原地改源几何会违反现有契约，调用方应更换CityData对象。此限制已明确报PM，未用弱摘要替代权威校验。

未改Runtime/UI/CityMap/速度/计时/快照版本。静态可确认重复缓存命中不再执行makeLegs；仍有JSON序列化、进度验证、跨模块克隆及首次/新计划寻路成本，未性能实测，不能声明卡顿/跳站已消除。

下一步跨owner契约见cross-module-contract.md：ready/continueTrip、同店服务组、当前唯一slot v3→提议v4的保守结构升级、deferFleet及真实elapsedSeconds事件偏移。除本段缓存外，这些契约均未写入实现。
