# P0轻量读取暂存候选：独立质量审查

**结论：静态PASS，`passed=true`；安全发现与逻辑错误列表均为空。** 只批准记录SHA的四文件共同替换候选，不代表已应用、可运行、性能改善或U01关闭。

审查者：`thr_wy4wnu5fyr`；父PM：`thr_axf6i4e89t`；环境：`env_e54zrbdgxt`。机读报告：[light-read-quality.json](light-read-quality.json)。本次没有覆盖旧核心质量报告。

## 候选与证据边界

候选根目录：[light-read-stage](light-read-stage/)；下列Route/Game/Runtime/UI行号均指该目录下`delivery-game/assets/scripts/map-sample/`对应暂存文件。将四份作为同一替换候选审查，依赖从原仓库读取；**没有把孤立暂存目录缺相对依赖副本的LSP提示当成工程错误**。

已独立读取补丁、四份候选的相关完整控制流和原UI.update，追踪原Point、routePosition及CityMap现有只读接口；没有仅采用作者报告或父PM规格PASS。

## 独立静态核对

### 1. progress与motion不泄露可变内态

- **Route `:15-16,55-61`**：progress每次生成只含`tripId/phase/cursor/serviceCharged/serviceSeconds`的新对象，不调用完整snapshot、JSON复制或position计算，不返回state、legs或Stop。
- motion调用一次既有position，再分配新外层对象和`[position[0],position[1]]`坐标对。消费者可修改返回对象/坐标，但没有内部数组别名可回写。
- 精准核对原仓库`RoadRouter.ts:59-69`：零segment回退确实会直接返回`route.points[0]`；新motion也会再复制，因此这一分支没有漏掉。`MapTypes.ts:1`的Point仍是原可写二元组，Readonly不是运行时freeze，不作冻结声明。
- 原`position/routeSnapshot`接口没有顺手修改；不声称其既有别名语义全部被修复。

### 2. Game与Runtime只更换读取，不更换业务

- **Game `:18,23-39,48-89`**：routeMotion直接委托Route.motion；候选tripId、phase、serviceCharged改读progress。accept/begin/continue之后都重新读phase，没有缓存旧批/旧阶段。自动补给短路、余秒、组扣点、到达回调与动作顺序保持。
- 删除Game新增getter并将progress标量读取在**内存中**逆变换成snapshot后，整个Game文本精确等于原源。这不是执行Game或模拟快照。
- **Runtime `:129-130`**只新增委托getter，读取最后成功发布live；不读时钟、不tick、不访问slot、不写状态。`mutate :101-117`原恢复→同步→动作→完整复验→必要提交→发布、生命周期与30Hz调度未变。

### 3. UI逐帧移动与完整成员读取分开

- **UI `:596-615`**：每次有效update先读motion并setRider，再经过0.5秒HUD门禁。没有逐帧无条件完整路线snapshot，也没有用插值、预估时间或改速代替权威位置。
- **`:602-611`**：仅`tripId:phase:cursor`变化时读取完整legs；不是把上一个批次的腿缓存给新批。begin时phase变化、服务后cursor/phase变化、取消清腿、新plan增加tripId，均保留路线更新触发。
- **`:619-630`**：pickupGroup仍在HUD门禁之后得到完整snapshot，不把缺少stops/orders的motion误传给完整成员消费者。服务标签、详情页等继续原接口。完整clone没有“全部消失”。
- 重新读取轻量motion与完整legs/成员之间没有新增await或跨帧缓存；已读setRider、HUD/状态刷新只同步更新显示或读状态，不显式推进Game。

### 4. 跟随、恢复与既有修复保留

- **UI `:601-611`**保持setRider、captureView→setRoutes→restoreView及原出发locate判定。原仓库`CityMap.ts:281-297,338-348`确认setRoutes会清follow、拖动会取消follow；候选没有新增每帧强制定位，也没有删除视图恢复。
- **Route `:69-81,103-118,175-233`**的商家键经营资格＋权威全集唯一、分组规则、旧Legacy完整门禁、可信期望legs缓存与完整输入legs比较原样保留。
- **Game `:14,17,92-119`**的序列化和恢复逐字未改，含`A-QUALITY-01`旧有效门闩推断及action/已扣服务互斥拒绝。版本、持久字段、服务/体力/收入经验、报价、旧Game1/2边界未变。

## 独立哈希与精确补丁重建

已自行重算四份原源、四份暂存候选及补丁SHA；均与清单一致。8个hunk按唯一精确上下文在内存重建，四份结果全部逐字匹配候选：Route 2、Game 3、Runtime 1、UI 2。**没有应用补丁或写回原源。**

共同逻辑路径为`delivery-game/assets/scripts/map-sample/`：

|文件|原SHA-256|候选SHA-256|
|---|---|---|
|V2RouteSession.ts|`73d4daea391b506dd38f0fcd25fb04d9ae387e5aa07a148b42bf2699c7839a5e`|`77cac10354e5f457f5553cc0c9b0b091345f583b54c18373aeff8a510a81f184`|
|V2GameSession.ts|`0101ac3eac40b82432d14c2bbb47dde4cdf8913fdb31ddb65fac362697c9af37`|`3d27e36b83e07f7235aa1aa6f51378a4abc3421bfa3003175464eedd34a6baf3`|
|V2RuntimeController.ts|`bb6dc40f960f5867b96bf9eeaad218d8d6a9d2aa648b53ce34aa0afcff892d81`|`725a4a6354712a960f854b80295d406049155e800cccc628eb97e19c2daff721`|
|V2GameUI.ts|`a33f933e5dc1e41827ac5cfbfaee1563d494d0acceae5fdaebec9321d10a1e96`|`cbcc769df60e8d5bfeeeb7d4c33ccb78faa12cbf8e271f9195950d8b6a97f210`|

补丁：[apply.v4a.patch](light-read-stage/apply.v4a.patch)，SHA `a4a70f3184d8c8f3b420826f8258963901e88a6a2a806f8e013e6b4e1dfb0af9`。

清单/父PM规格报告及所读依赖SHA详见JSON。交还前重算未发现所记版本漂移。**父PM应用前仍须重新核对四份原SHA及候选/补丁；任一不符就停止、重基和复审，不模糊套用或整份覆盖新改动。**

## 不随本次PASS解决的事项

- **剩余完整克隆成本：** Game serialize、Runtime候选恢复/复验/提交、UI路线键变化与HUD/详情读取仍在。此次仅改变指定调用策略，不是消除全部clone。未测FPS、耗时、GC或内存，不能称卡顿解决或关闭U01。
- **NPC真实帧内事件时点：** 候选Game `:44-49,86`仍沿原帧尾Dispatch及默认到达结算时刻，没有eventAt/offset改造。这是既有独立缺口，不计本候选新增回归，也不能以NPC日期归类PASS替代。
- **运行案例全部未执行：** 零长度腿坐标隔离、沿路/ready/取消位置、新批同phase/cursor换腿、拖动与跟随、HUD门禁前刷新、同店/自动余秒、Game1–4合法恢复及互斥坏组合、完整legs拒绝、事务失败不发布和唯一slot等，均等阶段授权。

## 权限与交还

仅源码/控制流/JSON/哈希/内存文本补丁核对；未运行tests/typecheck、TS或游戏函数、合成/真实档、故障注入、游戏页面、Creator、构建或部署。

只写`performance/light-read-quality.json`与本文件；未改原源、候选、补丁、清单、旧核心报告或其他文档，没有子Agent、commit/push。地图制作与任何相关生产加工不在本次范围，未派地图任务；CityMap/RoadRouter只追现有消费接口。

**只读范围已交还父PM。候选尚未应用，不自行集成或关闭反馈；静态PASS不代表功能、性能、构建部署、98%或用户验收。**
