# 核心配送闭环A实施报告

状态：**指定源码已落盘，未测试，待用户明确“阶段完成”后集中测试。** 不代表真实用户档已经转换、游戏可玩验证通过、配送卡顿已解决或性能通过。

范围依据：`../cross-module-contract.md` 第1—5节及本批冻结契约。第6节NPC帧内时点不实施。本执行者只修改下列源码及本目录报告，保留其他dirty/untracked内容：

- `delivery-game/assets/scripts/map-sample/V2RouteSession.ts`
- `delivery-game/assets/scripts/map-sample/V2GameSession.ts`
- `delivery-game/assets/scripts/domain/V2TripRules.ts`

## API与接线契约

|接口|实际行为|
|---|---|
|`V2RouteSession.continueTrip():void`|只接受`ready`，仅变为`travelling`；重复提交及其他phase抛错。不改位置、钱、体力、期限或时间。Route不持有补给状态，补给门禁在Game。|
|`V2GameSession.continueTrip():void`|有补给action则拒绝，否则调用上述Route入口。自动控制也调用这个Game入口，不直接改phase。|
|`V2TripRules.pickupGroup(ids:string[]):boolean`|先检查数组非空、ID非空/唯一、成员全是真实未取未送订单，再检查体力。低于1点返回false并设blocked，不部分扣点、不部分标记；足够时一次扣1点并全组picked。|
|Route `advance` hooks新增`pickupGroup?:(ids:string[])=>boolean`|多成员pickup必须存在此hook；缺失抛错，绝不循环旧service。单成员仍调用旧`service(id,'pickup')`入口，Trip内部复用单成员pickupGroup；dropoff仍独立service。Game已接组hook。|
|Route只读`serviceBudget:{seconds:number;stamina:number}`|按实际Stop统计：`seconds=pickupStops*2+dropoffStops`，`stamina=pickupStops+dropoffStops`。供choices与Game预算共用，不是新增持久字段。|
|`assertDispatch(dispatch, routeSnapshot?)`可选校验参数|保留原三条Dispatch对应校验，允许Game对尚未转换的旧结构做组合预检；默认仍校验本Route。只读，不改变当前Route。|

PM最新告知Runtime/UI执行者B已交回continueTrip/ready/orderIds接线。Runtime `continueTrip()`须走原mutate的“同步旧时钟→命令→组合校验→同一slot commit→publish”。本执行者没有改Runtime、GameUI或Store，也没有运行验证B的接线；必要构建由PM统一。

## 快照字段与版本

|结构|本批值/变化|
|---|---|
|Route format|仍为`county-v2-route`|
|Route version|`2`|
|Route timeProfile|`road40-service2-1-grouped-v2`|
|Route stopPolicy|必填`'legacy-sequential'|'grouped'`，精确命名如左；新批固定grouped，旧批转换为legacy-sequential。|
|Stop|`{orderId:string,orderIds:string[],kind:'pickup'|'dropoff',node:string}`；`orderId`固定为首成员。dropoff必须只有一个成员。|
|Route phase|原phase加`ready`；`serviceCharged`在规范v2中为必填boolean。|
|Game|`county-v2-game`组合version `4`|
|TripState|仍version `2`，没有为合并或ready加快照字段。|
|Dispatch/Fleet/经济/Store|本批不改版本、不改配置、不扩大快照。|

## 新批规划与服务

1. 商家键仅在订单`pickupNode`与`pickupName`精确匹配当前可经营的真实`city.pois`项时成立；该配对必须唯一且名称非空。`this.places`直接来自原city.pois的既有边界/经营过滤，不是屏幕文案索引。重复配对有歧义、未知名称或伪造名称均不合并，也不做trim/别名猜测。
2. 按所选订单第一次出现的已证实商家建组，组内保持原订单顺序。每组一个pickup，随后按组内顺序逐单dropoff，再下一商家。未知身份订单各自单成员。不是全局最优排程。
3. `plan`在写Route前，对重排后每个实际有向段用原router检可达；Game仍先候选plan，再Dispatch.acceptBatch。整批容量仍由Dispatch按所选全部订单总重校验，不允许通过先卸货突破容量。
4. pickup确认将全组ID放入Route.picked；在serviceCharged门闩成功扣点之前，Trip仍全组未picked。这是可恢复的明确中间态。扣点成功只设一次门闩，服务总时长仍2现实秒/60游戏秒。每个dropoff仍单独1点、1现实秒/30游戏秒、独立arrival令牌与结算。
5. pickup服务完成立即清门闩、cursor移到下一站、legSeconds/serviceSeconds归零、进入ready，并从本次advance立即返回实际消耗秒数。即使本次还有余秒，Route也不代为继续；Game手动分支丢弃此尾段，不在下一帧追回。
6. ready.position取已到店anchor，而非下一leg。无补给动作的ready等待不调用travel/serviceTime，不增加主角gameSeconds/里程/体力/餐损。Dispatch.tick仍照常推进NPC，不设置全局暂停。主动补给自身原有耗时不属于空等，规则保持。
7. 自动控制在尚有本帧合法动作秒数时，经同一Game.continueTrip入口继续，再推进剩余时间。advance在余秒耗尽时不再自动确认pickup或扣下一服务点，避免权益精确到边界时多代点。暂停、后台、重载首帧和广告门禁沿用原逻辑。
8. dropoff服务后仍自动沿下一leg继续，没有新增顾客确认。取消ready保留商家anchor；取消travelling按当前leg真实边/elapsed取anchor，并覆盖零长度/恰好到腿末端的落点，避免回到前一anchor。

## 时间、体力与合同预算

- Route.choices与Game.routeChoices均使用serviceBudget实际服务Stop口径；天气/车速修正只作用于道路时长，不乘取送服务时长。
- 首15单候选接受预算和路线过滤使用同一个实际服务耗能口径，不再用`orders.length*2`估算服务点。
- 道路40游戏秒/现实秒、取餐2秒/60、每单送达1秒/30保持；没有修改速度参数、报价、奖励或原路。
- `fastest`仍给每单自己的必要一次取餐/一次送达时间，保留原`+90`游戏秒；Trip.begin仍为每单建立独立期限，不因分组合并重签合同或发额外奖励。
- 收入、经验、补额度、receipt与arrival去重仍走既有逐单链路。未改Dispatch/Fleet经济路径。

## 旧当前进度兼容执行路径

Game.restore按以下顺序执行，所有对象都只是内存候选，函数内无存储读写：

1. 校验Game format与版本及组合配对。旧Game v1/v2/v3只能带Route v1；Game v4只能带Route v2。未知未来版本拒绝。
2. 恢复Dispatch及其原经济/Fleet/reward完整校验；对原始Route结构做原Dispatch对应校验。v2/v3先恢复对应TripState并执行原组合总体校验：订单对应、picked/delivered、补给开放/在途休息、逐单结算对应均保留。旧pickup服务未扣点特例仍只针对原当前ID；旧缺失serviceCharged按原规则推断，源结构不先加orderIds、不先重排。
3. 之后调用Route.restore；v1进入独立`restoreLegacy`，先完整执行原v1校验：原profile/mapKey、订单、合法anchor/原道路边、phase/游标/计时、原orders.flatMap逐单Stop精确顺序、门闩、按router生成的完整legs JSON相等、picked顺序与原arrival令牌精确对应。
4. 只有上述全部通过，Route才改为v2/profile新标识、stopPolicy=legacy-sequential，并将原每个Stop加成单成员orderIds。其余原stops次序、cursor、legs、legSeconds、serviceSeconds、有效serviceCharged、picked、arrivals、tripId、nextId、origin/anchor及令牌保留。旧缺失门闩只沿用原restore已有推断；不重新扣服务、不重抽Trip、不改期限、不重发钱/经验/额度。
5. 原travelling仍停留在当前leg真实进度，不回退已出发腿；原进行中的pickup/dropoff服务按剩余服务时长继续。今后完成pickup才进ready。旧已规划/在途批不重排，下一新批plan才切grouped。
6. Game v1仍只接受无活跃batch、Route idle/finished的原范围，并保留原cancel处理；不补造缺失在途Trip。Game v2仍必须TripState v1并走其既有转换；v3/v4必须TripState v2。原v1/v2接受/拒绝边界没有借新Route扩大。
7. Game.restore最后才返回规范候选，由Runtime既有成功载入事务决定写回同一个slot。失败直接抛出，不提供清档、第二slot、备份档、废弃key读取或自动重开。未读写真实slot；实际事务持久化由Runtime owner负责核验。

## 新Route恢复门禁

- 按stopPolicy重建规范Stop列表逐字段/成员顺序比对。由此同时约束每ID恰好一次pickup成员/一次单成员dropoff、先取后送、组商家权威可证、稳定分组或严格旧逐单顺序，不接受任意站点排列。
- planned重新检查原路可达；已出发状态始终将输入legs完整JSON序列化，与独立router生成的期望值比对。
- ready要求cursor合法且大于0、前一站是已完成pickup、anchor在原商家无边偏移、legSeconds/serviceSeconds均0、serviceCharged=false。相应completed/picked列表及Game的全组Trip.picked校验必须同时匹配。
- pickup/service/travelling/finished各自校验计时与anchor；service非零进度必须已扣点。所有completed dropoff的arrival token仍精确按`arrival:<tripId>:<stopIndex>:<orderId>`验证。
- Game的“当前pickup已列Route.picked但未扣点”例外，对新组扩为全部成员，不能只比首ID；已扣点的组必须全部Trip.picked。

## 保留的安全/性能边界

- `prepare`的CityData WeakMap缓存、原有向路段拆run与POI过滤保持，未改源city/三框/道路。
- 期望legs缓存仍以真实PreparedMap/router实例隔离；只存router生成的字符串，不存输入legs。仍最多16项，单项key+value字符数不超过262144；超大项不缓存但仍完整比对。
- 本次仅让makeLegs/expectedLegsJSON可接收待校验origin/stops，以在转换前验证旧结构。缓存命中也不省略输入legs的完整JSON比对。
- CityData仍有“加载后不可变”前提；未增加新安全承诺，未进行性能测量。商家配对遇到重复POI保守不合并，是明确保守策略，不声称已有merchantId。

## 源码锚点

以下行号为本次编辑后的源码静读定位，不是测试证据：

|实现|锚点|
|---|---|
|Stop/Route v2字段|`V2RouteSession.ts:7–18`|
|权威商家、稳定规划、实际服务预算|`V2RouteSession.ts:63–76`|
|独立单单期限必要服务、plan前有向可达|`V2RouteSession.ts:87–95`|
|期望legs有界缓存与choices|`V2RouteSession.ts:96–115`|
|pickup/continue/服务门闩/ready/自动零余量边界|`V2RouteSession.ts:120–155`|
|位置与取消/原Dispatch对应校验|`V2RouteSession.ts:55`、`:157–167`|
|旧Route完整校验后转换|`V2RouteSession.ts:168–184`|
|新Route规范、ready与token恢复校验|`V2RouteSession.ts:185–225`|
|Game v4、预算、continue入口|`V2GameSession.ts:14`、`:22–33`|
|Game自动ready与组hook接线|`V2GameSession.ts:47–89`，重点`:83–85`|
|旧组合预检后进入Route转换|`V2GameSession.ts:91–117`|
|组原子预检/扣点、单成员与dropoff服务|`V2TripRules.ts:83–95`|
|服务游戏时间不变|`V2TripRules.ts:103`|

## 本轮证据、风险与交付边界

- 实际使用read_file/search_files读取邻接调用与定义，再用patch逐段编辑指定源码；未整文件覆盖其他人的工作。
- patch工具对TypeScript的自动检查返回**skipped：检测到项目tsconfig，跳过单文件tsc**。本轮没有语法检查通过或类型检查通过的结论，也没有另跑tsc绕开限制。
- 没有运行tests/typecheck/回归/游戏/存档/构建/部署，没有接单、购买、造档/清档、commit/push、worktree/stash或恢复其他改动。
- 旧档转换函数已实现但没有用任何真实档或合成档执行。旧在途位置/令牌不变、持久化失败保原档、自动末帧及性能都只能列入待集中案例，不记通过。
- Runtime/UI另一写集已据PM通知交回，仍由PM统一集成核对；本报告不替其运行结果背书。尚未完成与精确待跑案例见`remaining.md`。
## PM修复A-SPEC-01（定向复审中）

独立规格审查发现经营子集唯一不能证明完整来源配对唯一。PM仅修改merchantKey：同时要求非空名称、现有经营places中存在准确配对、只读权威来源同配对恰好一项，歧义保持singleton。新规划与恢复共用这一条件；不更改任何源数据、路由、道路、边界或地图制作素材。已向原规格审查者thr_xian3wmj7j发送并读回复审请求；不是修后通过或运行通过。

修后V2RouteSession.ts SHA-256：73d4daea391b506dd38f0fcd25fb04d9ae387e5aa07a148b42bf2699c7839a5e。
## PM修复A-QUALITY-01（独立复审中）

核心静态质量审查发现既有组合恢复遗漏：可以接受已扣点取送服务与未完成补给并行。PM仅在restore原有效charged推断之后增加同正常supply入口的互斥拒绝，不清action、不重置门闩或更改旧数据。旧缺门闩仍按原服务进度推断；未扣点服务补给、ready补给、无action已扣服务不因新条件被拒。已向thr_wy4wnu5fyr发送并读回定向复审请求，尚未修后通过/构建/运行。自动旧Array.includes库告警未用来扩改tsconfig或启动typecheck。

修后Game源码SHA-256：0101ac3eac40b82432d14c2bbb47dde4cdf8913fdb31ddb65fac362697c9af37。
