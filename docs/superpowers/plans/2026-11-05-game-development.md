# 完整游戏开发接续 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 承接用户明确补充的游戏逻辑、经济数值和功能开发，并与正在执行的UI/资源还原统一集成，而非把产品开发缩成UI修图。

**Architecture:** 保留现有Cocos工程、原路网、新版经济与唯一slot。业务拆为逻辑状态、经济账本、运行接入三条不重叠写集；各owner先追已确认规则和实际调用链再修明确缺陷。UI/资源原有角色继续，PM独占跨模块协调、必要构建/部署及最终审查。

**Tech Stack:** Cocos Creator 3.8.8、TypeScript领域状态与Runtime适配、版本化参数JSON、已有独立规划模型。

## 11-06当前批次：NPC真实事件时点＋UI遗留清理

前批P0轻量读取已合入四源并精确匹配独立审查候选，资源缓存L01/L02/L03当前定向质量PASS。`v2-product-candidate`已生成，Finished日志及进程退出36诊断保留；143衍生纹理路径/原文件字节已进入产物。PM在隔离4187只切六页、滚动留图，未执行游戏业务或操作用户档，4182仍旧包。构建/外观证据见`integration/product-candidate-build-integrity.json`，不是性能、阶段测试或98%通过。

- **开发A复用thr_j9izunn7qx：** 本轮批准`logic/cross-module-contract.md`第6节。唯一源码写集为V2GameSession.ts、V2RouteSession.ts、domain/V2DispatchSession.ts；Fleet/Runtime/Trip/UI只读。新增默认false的deferFleet选项和advanceFleetTo，Route arrival第三参数传真实消耗秒数；Game按真实eventAt串行推进NPC旧额度、主角完成/补额度，再推进余段。补给购买等帧内经济动作同样用真实时点，临时ledgerContext恢复；沿用既有日期resolver，不新增持久字段/版本，不回填旧null日期。所有退出路径都推进NPC到帧尾，候选一次发布。保留P0轻量读、ready/分组、旧兼容和所有校验。输出一份`logic/npc-frame-time/implementation.md`，Dispatch修改前留一份非运行源文本基线，以便对照未跟踪源码。
- **开发B复用thr_tviezvnwds：** 唯一源码写集为V2GameUI.ts、V2ApprovedSkin.ts。U38除金额旁小币图外，今日/累计收入metric的income分类图仍是金币堆，须清除账单页所有币图别名但保留其他非币图标/真实账目。修nav-base、button-disabled不存在及clock/coin-stack未知Cartoon回退请求的调用原因，不只隐藏warning，不替换正常主图片、不重做资源或改版。输出一份`layout/ui-residual-cleanup.md`。
- **边界：** 两写集不重叠；不新建会话、不派地图生产/加工/拼接/数据任务。U23—U30骑手稿及近似金额仍待用户确认，B不得夹带实现。测试/typecheck/回归/业务操作及造档仍禁止；必要构建只由PM执行。各作者交回后由PM规格核对，再复用独立复审A/B，不以自审代替。

下文角色与批次为历史记录，本节覆盖其会话和当前写租约。

## 范围与权威

- 用户两次明确工作不只是UI，还包括游戏逻辑、游戏数值、功能开发；自主组织授权沿用。
- 当前参数唯一主版本：`frontloaded-2026-11-04-v3-hire-training-tail`，依据 `docs/balance/2026-11-04-frontloaded-economy/parameters.json`、`docs/reviews/2026-11-04-cocos-v2/hire-training-correction.md` 和实际TS配置。旧候选按招募顺位、旧培养/尾价、旧购买资格不可恢复。
- 正式V1未被新明确规则覆盖的流程继续有效；最新用户原话及 `implementation-baseline.md` 新覆盖段优先。旧文档的“未开发”不自动等于当前仍缺。
- 地图会话 `thr_2qc9rtsa9r` **只负责既有地图工作**。不再向其派UI/产品/逻辑/数值/开发协调任务；这里独立承担游戏工作。地图未就绪仍列全产品阻塞，但不改地图会话的目标或写集。
- 已明确首页两块悬浮文字删除，由UI owner落实；保留实际结算和账本。不是删除功能或通过改订单状态隐藏。

## 角色与写集

### A. 游戏逻辑owner（新短会话，Sol/high）
写集：map-sample/V2GameSession.ts、V2RouteSession.ts；domain/V2DispatchSession.ts、V2FleetSession.ts、V2TripRules.ts。

任务依序：
1. 建立规则→实际符号→缺口矩阵；静态追主循环/状态边界，禁止只写盘点便报完成。
2. 修容量组批、原路/到达、取送服务、逐单唯一入账与整批无重复、取消全部未完成单等已证实缺陷。
3. 修体力/动作/补给、暂停恢复、自动批次、NPC有限额度与冻结合同的逻辑问题；不更改经济报价或对外SDK。
4. 输出logic/implementation.md、requirements-matrix.json、remaining.md，公开接口或快照需变更先交PM协调。

### B. 经济数值owner（新短会话，Sol/high）
写集：domain/V2EconomyConfig.ts、V2EconomySession.ts、V2RiderEconomy.ts、V2Ledger.ts、V2ProgressTargets.ts、V2SupplyCatalog.ts；参数JSON只读，必要修正先报PM。

任务依序：
1. 对照当前JSON/TS/报价与扣费调用，查版本/ID/整数分精度/取整一致性。
2. 固定ID招募、培养1600/满级+60%与减服务25%、车辆1.5P/旧车150基数，任意钱够购买；只修明确实现不一致，不另调平衡以凑目标。
3. 购买/升级/结算原子性、余额账本对账、库存与现金来源、目标不冒充奖励，逐项追真实接口。
4. 独立算术可运行并保存真实结果，不运行游戏测试。模型20分钟小队/二八只标设计证据，慢操作27.41分仍是已知限制。
5. 输出economy/implementation.md、parameter-consistency.json、remaining.md。

### C. 功能接入owner（新短会话，Sol/high）
写集：map-sample/V2RuntimeController.ts、V2RuntimeStore.ts、V2GameBootstrap.ts、CountyV2Session.ts；rewards-v2/RewardSession.ts。

任务依序：
1. 从?v2=1入口追到可达能力，不以有按钮/有类当完成功能。
2. 修命令/忙碌态/错误反馈/前后台/保存写者生命周期、唯一slot与重开防旧标签页回写的明确缺陷。
3. 专送80%大厅口径/广告独占/失败不发权、600秒自动权益/停止恢复/回调去重；实际SDK未配置列外部阻塞，绝不模拟成功。
4. UI接线只读，需要新增入口给UI owner精确请求，不抢UI写集；MapSample现有dirty禁止擅改。
5. 输出features/implementation.md、feature-matrix.json、remaining.md。

### D. 已在执行的视觉链路
- 资源owner thr_cqkytibciw已交源码修复和报告，父PM已读回报告/UIArtResources；仍未构建/部署/远程证实，不记G0通过。
- UI owner thr_uevwv32vnh继续六页还原并已移除首页两块浮字及纯展示刷新；实际账本/订单详情保持。
- 独立视觉规格审查 thr_m4huheeu3r继续8原图差异单。

### E. PM/集成/复审
当前thr_axf6i4e89t。各owner只写自身文件及专属报告；不改公共baseline/handoff，不并发Creator构建。所有角色同env_e54zrbdgxt、Sol/high、不fork/worktree/新子代理/GPT-6-astra，不自动commit/push，保留全部未提交。

## 集成与验收

1. 各owner交已写源码与真实证据；PM读回具体目标，先规格一致性审查，后独立代码质量审查。未通过退回owner，不靠自审代替。
2. 三业务owner维持当前公共API和快照版本；跨边界变更不“顺手改”，由PM明确串行实施。
3. 原路/三框/唯一slot/新版参数不因视觉还原被改；五个购买记录不当作五张运行地图完成。
4. 代码存在、独立规划算术、必要构建、外观可见、行为通过、用户体验分别记录。逻辑/数值/功能不能用UI的98%指标替代验收，须逐条满足规则及正确性。
5. 用户仍未说“阶段完成”：过程不运行tests/typecheck/回归，不购买/升级/接单/清档、不造存档。可写待集中case，PM必要构建和授权外观核对不等于游戏测试。
6. 业务与UI/资源均稳定后PM统一必要构建/部署；真实SDK、完整首页地图、未确认奖励等仍未解决时如实列阻塞，不声明全产品完成。

实际角色和进度另记 `docs/reviews/2026-11-05-game-development/dispatch.json`。本计划开始执行，不是阶段完成或新版验收。

## 当前续推批次：核心取餐闭环（PM已批准实施）

**最新执行覆盖：** 核心A/B已经交回源码，当前不是两个旧执行者仍在运行。已实际新建四个同checkout、父通知auto的BB工作线：`thr_xian3wmj7j`只读核心规格审查；`thr_sxu96cizgd`独占Fleet/Dispatch/Runtime修逐笔NPC账单归日；`thr_rddariqvsa`独占GameUI/ApprovedSkin及独立产品车辆展示素材；`thr_rhp4ifmpzk`独占图片加载辅助与四类非地图资源Web包。四条线范围纠正均已发送并读回。资源与UI源码不重叠，审查只读；主方案/清单/构建部署归PM。

**产品/地图严格分线：** 本线不派地图制作/素材加工/拼接配准/建筑道路/地图数据边界，不向地图会话派工；车辆背景不得取地图插图裁切合成，Web包排除maps.json/map-preview/mapPreview及其他地图素材。地图引用维持原状，任何本轮越界衍生隔离不合入。旧段提到的地图缺口不再转为产品任务，两线独立推进与验收。不得因此重写已交回的核心代码或停止其他获准产品工作。

本批实际交付是可构建的同店合并取餐、取餐后原地等待和手动继续链路，不再停留于接口建议。批准logic/cross-module-contract.md第1—5节；NPC事件时点、蓝框、逐单报价等后续串行处理，不随本批擅改。现有六个BB专项会话首轮已回idle，改用两个精简Hermes执行上下文，避免重启已发生502的长会话；不fork、不建worktree、不引入新模型。

### 任务A：Route/Trip/Game状态与当前进度兼容

- 独占V2RouteSession.ts、V2GameSession.ts、domain/V2TripRules.ts，以及logic/core-loop/下实施报告。
- 新Route v2/Game v4；pickup Stop含orderIds、保留orderId；只对权威商家身份相同的新批次合并，一次2秒服务/1点体力，逐客送达仍独立。
- 取餐服务完成进入ready，人物停在该商家；continueTrip只做ready→travelling，等待不补跑，不消耗行程时间。自动经过同一入口，许可余额规则不变。
- 保留容量、已签合同与期限、原路和服务数值；choices/起步体力预算按实际服务Stop计数。
- 旧Route v1先用原校验，旧Game v3组合校验保持，再转单成员Stop；在途顺序、位置、进度、凭证和收入不变。新快照显式区分legacy-sequential/grouped计划策略，防止旧在途与新分组校验混淆；旧Game v1/v2的既有接受/拒绝边界不扩大。
- 禁止Runtime/UI/Dispatch/Fleet/经济/地图写入；不碰用户slot，不运行tests/typecheck/回归/构建/游戏，不commit/push。

### 任务B：Runtime/UI接线和明确标题删除

- 独占V2RuntimeController.ts、V2GameUI.ts，以及features/core-loop/下实施报告。
- Runtime.continueTrip走原mutate事务：先同步旧时钟、调用Game.continueTrip、完整校验、成功保存后发布。保留原唯一写者与失败保护，不能直接改Route字段。
- UI ready显示去下一站/去配送、pickup仍到店取餐，service不可重复；共享取餐显示真实商家和该组件数；不在UI推进人物/cursor。
- 删除骑手/车辆/地图/账单顶部标题（用户已明确要求，PM单独批准，不必等待整套骑手稿）；订单大厅标题和首页HUD保留。
- 骑手新卡排版与万元近似金额规则依然等待用户确认，不夹带实施；不写A的三个源文件，不构建/部署/测试或操作存档。

### PM集成与两阶段审查

- 两任务按上述固定接口可并行准备，PM等两写集交回后统一构建；不把中间未齐源码当可用包。
- PM先逐项规格审查，再独立代码质量审查；重要缺陷先修，不带病上线。必要Creator构建和非消费外观核对可做，阶段集中行为测试仍未获授权。
- U01/U02/E02的相关子项进入实施，但性能、主循环和原存档兼容均不能在没有对应证据时关闭；38条反馈依然保留未结案。
