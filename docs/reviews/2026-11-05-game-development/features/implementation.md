# 功能接入实施记录（2026-11-05）

最新U01优先修订：Runtime增加成功提交字节缓存及约30Hz普通时钟合并，保留逐事务校验与提交后发布；原文每帧成本描述为首轮诊断历史，详见[u01-runtime-hot-path.md](u01-runtime-hot-path.md)。源码已写，性能与行为未测，U01未结案。

本角色 thr_f2cxhbkw45，父PM thr_axf6i4e89t。所有结论限源码静态检查；未运行 tests/typecheck/回归/Creator/页面，未读改真实存档，未购买、接单、升级或清档，未commit/push。构建部署由父PM统一。用户最新“不允许重新开始”覆盖11-04重开文档与本任务旧条款中的玩家重开要求。

## 依据与输入

已读取 implementation-baseline.md 最新覆盖与长期规则、正式V1相关流程、2026-11-03-next-product-economy-revision-intake.md，以及 docs/reviews/2026-11-04-cocos-v2/ 下 runtime-implementation、single-slot-save、ui-integration、rewards-implementation、ledger-supply-ui-implementation 五份已存在文件。历史报告描述的是当时状态，本次依实际导出符号/调用者判断。新版经济以TS中的 frontloaded-2026-11-04-v3-hire-training-tail 为准，非intake旧候选。

## 实际修改

1. V2GameBootstrap：删除“清空进度重新开始”、二次确认及open(reset)分支。唯一动作开始/继续调用startOrContinue，在锁内有slot则restore、空slot才fresh。不把重开搬页；移除onRestartFailure接线。
2. V2RuntimeController：startOver/restart保留原签名兼容在途UI引用，但直接拒绝，不调用store、不清live、不换epoch、不保存。open类型去掉reset。原startNew已由store拒绝覆盖已有slot。
3. V2RuntimeStore：坏档/未来版本restore异常统一显示保留原档并停止载入，不再引导清空；锁冲突文案仅引导关闭其他页后继续。writable遇到writer失权、epoch改变或读取异常，冻结并记录原因；Runtime.ready传播到lastError，现有UI update可显示。
4. Runtime.requestAd：SDK同步抛错仍先持久化failed票据，但现在向调用方抛出错误，避免UI act把正常返回解释为成功；向SDK交只读冻结副本，保留原票据供失败收尾。未添加任何completed模拟器。
5. 生命周期：Runtime持有openingStore，Bootstrap持有preparation，onDestroy立即close。根因是此前仅在await结束后挂store，销毁发生在acquire等待期间无法关闭待完成实例。Store.acquire已有closed复查，阻止迟到取得锁后继续清理/打开。Bootstrap增加disposed检查，阻止迟到资源回调开局。

独占源码只修改 V2GameBootstrap.ts、V2RuntimeController.ts、V2RuntimeStore.ts。CountyV2Session与RewardSession核查后无需本轮改动。未改UI、domain、GameSession/RouteSession、MapSample、地图资产及公共基准。

## 实际可达链

MapSample.start显式v2Enabled或URL ?v2=1 → V2GameBootstrap → prepareCity(唯一map-sample/city) → Runtime.configure/enableV2 → startOrContinue → Store.open → V2GameSession.restore/fresh → tick/commit后发布live → V2GameUI.configure。

UI只读追踪：navigate真实切入大厅才enterLobby(新ID,Math.random,Math.random)，列表滚动/刷新不抽；主六页从snapshot与tripState读取。骑手hireRider/upgradeRider、配置assignVehicle/upgradeVehicle、商城buyVehicle、地图buyMap/selectMap，均经Runtime.command→Dispatch.command。补给supply/configureAutoSupply→GameSession→TripRules；普通组批quoteCandidates只克隆预览，acceptBatch事务提交后routeChoices/beginTrip，pickup及路线到达经GameSession结算；取消按钮cancelDelivery(pending[0])下游取消全部未完成，已完成账本保留。账单summarizeLedger只读查询，整批汇总筛真实order ID，不二次发钱。

Runtime.mutate对候选克隆推进旧资产时钟→执行命令→restore校验→commit→发布live。写失败不发布候选，store冻结。UI各操作act捕获同步错误；异步/逐帧错误由lastError刷新。忙碌限制由domain/Session负责，当前Dispatch在活动batch期间拒绝全部经济command，具体是否放宽交逻辑owner，不在运行适配层绕开。

CountyV2Session.migrate为历史显式兼容工具；scripts中无外部调用者，当前V2入口不使用它，不自动迁移、恢复或发迁移赠品。它的存在不代表运行接线。

## 存储与重开边界

唯一快照 delivery-county-single-slot-v1；epoch key只存并发世代元数据。Store.prepare/open仍按既有明确allowlist废弃旧游戏key，未使用localStorage.clear、前缀清空、backup或fallback。检查只读源码，本次没有实例化存储或运行清理。

已有slot：startNew拒绝、continue restore验证失败拒绝，原快照字节不覆盖；空slot：continue自然fresh并保存。未来组合/嵌套版本由restore拒绝；可能初始化缺失epoch，但不会覆盖坏slot。写入要求共享Web Lock、epoch一致、slot字节仍等于expected。旧标签失锁/失epoch/slot冲突不能回写；销毁释放锁并增加generation，广告迟到回调被ready/generation挡住。底层Store.reset/open(reset)仅留兼容，无Runtime玩家调用；未删除其防旧写者机制。

## 广告与自动权益的实际状态

RewardSession.enterLobby以appearanceRoll<0.8判一次真实大厅进入，价格100+floor(priceRoll*51)，100～150；pending/authorized权益保留但每次打开仍独立判定。requestAd只允许一张pending票据；special绑定候选，completed必须匹配ID/benefit/order/expiry且未过期。beginBatch专送只能一单，广告授权不直接发钱。重复/过期/不匹配回调不授权。

自动成功授600秒；Dispatch控制manual/auto，GameSession按许可时间真实推进路线/接普通批次；stop/resume及剩余秒保存在组合快照。后台、暂停、恢复首帧、pending广告期间不推进主角；NPC按独立经营时钟推进。规则源码已接，但UI没有requestAd/stopAutomation/resumeAutomation调用，专送卡仅“广告暂不可用”。Bootstrap的SDK.show明确抛错；真实SDK/凭据/平台奖励验证属于外部阻塞。不能宣称专送/广告自动可玩。

## 经济、地图与目标

TS配置ID与五图名确认：晴川县/云浦市/星澜城/曜川都会/海境港。购买链走新版报价/扣款；只检查运行接线，数值一致性由经济owner独立负责。只有一个CityData，买图/选图改变经济状态，不代表五张运行地图完成。queryProgressTargets是推荐目标，无奖励表/领取链，不添加赠品。

## 静态证据与局限

已用rg追scripts全域startOver/restart/reset与CountyV2Session、广告API调用者，并回读修改后的三个文件；报告JSON经解析与条目枚举检查。UI为并行owner在途文件：复查时其重开方法/按钮已移除，仅残留未使用onRestartFailure属性，不由本角色写入。未执行行为验证，不能称编译通过、功能通过、阶段完成或98%。具体逐项状态见feature-matrix.json；集中用例与阻塞见remaining.md。
