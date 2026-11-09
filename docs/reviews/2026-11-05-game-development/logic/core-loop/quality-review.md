# 核心配送闭环独立代码质量审查

**最新结论：`passed=true`，A-QUALITY-01修后定向独立质量静态复审PASS。** 当前安全/逻辑阻塞列表均为空。未发现本次修复误拒正常合法旧状态或造成其他规格影响；这不是运行通过或24项规格全量复验。

审查者：`thr_wy4wnu5fyr`；父PM：`thr_axf6i4e89t`；环境：`env_e54zrbdgxt`。机读结果见 [quality-review.json](quality-review.json)。

## 修后定向复审：断言与合法路径

当前源码 `delivery-game/assets/scripts/map-sample/V2GameSession.ts:105-107`保留原旧门闩推断，在其后新增“有action且处于已扣点service则抛错”。错误为“取送服务与补给动作不能同时进行”。它只拒绝组合，不清action/门闩，不推进动作、变更时间、发收入或操作slot。

从源码静态核对以下分支，**全部未执行游戏或快照**：

|分支|定向静态结论|
|---|---|
|新旧版本rest/购买/库存action与已扣服务冲突|只要先通过原Trip门禁，新增`:107`不区分kind/source，统一拒绝；取餐/送达、服务起点/半程均适用。|
|旧Game2/3缺serviceCharged，serviceSeconds>0|`:105`仍推断为已扣；有action拒绝，无action继续原校验。没有将undefined统一当false。|
|旧Game2/3缺门闩且serviceSeconds=0|有效charged=false，新断言不拒绝；仍由原picked/Route等检查决定能否恢复，未补造已扣状态。|
|无action的已扣服务，包括体力为0|第一项即短路；原门闩/计时保留，继续原恢复链，后续服务仍可只完成余时而不二扣。|
|未扣点低体力service与合法补给|charged=false使新断言短路；serviceSeconds仍须按原门禁为0，当前pickup组未扣点picked特例仍在`:108-109`，原rest量/购买开放检查在`:110-111`。|
|Game4 ready加合法补给|phase不是service使新断言短路；Route`:208`继续检查商家anchor、零计时和未扣门闩。旧Game1/2/3仍不支持ready。|
|旧版本与库存边界|Game1无Trip分支未改。Game2必须Trip1，迁移仍只认water/noodles/rest，非rest来源按原规则规范成purchase，不新增库存语义。Game3/4 Trip2库存仍先过grant/数量门禁；当前奖励表为空，不称已有合法库存档或运行通过。|
|未来/错配/畸形门闩|原版本门禁不变，新断言不会放行先前拒绝的结构；Route2缺boolean门闩仍由原Route门禁拒绝。|

恢复其余链仍为原Trip检查、全组picked/delivered对应、rest/开放/结算对应以及原Legacy完整Route校验后singleton转换（当前Game`:102-118`，Route`:172-183,189-223`）。新增断言位于组合恢复，不改变正常命令、tick或持久化字段。

### 精确增量与新SHA

- 当前Game SHA：`0101ac3eac40b82432d14c2bbb47dde4cdf8913fdb31ddb65fac362697c9af37`。
- **只在内存中**从当前源码移除新增注释和互斥断言两行，重算SHA精确恢复初审Game的`2ff12cb7cb96d334d54c76ee68bd2db711e7ea21264585ef9b02c0480c78ecac`，确认没有其他Game变化。没有写回源码或执行游戏代码。
- Route/Trip仍分别为`73d4daea391b506dd38f0fcd25fb04d9ae387e5aa07a148b42bf2699c7839a5e`、`6ede7a45eed46a1875e187d1f728e045f44db82de6f7d83a685131d9e6093c16`。已记录依赖SHA与初审一致；未追审并行UI/资源线。
- 前置`review-round2/spec.json`仍绑定旧Game及原24项证据；本轮不改它、不称当前全量规格复验。初审质量证据按原SHA保留，当前只补两行增量的独立质量复审。
- NPC日期线核心文件不变，但其旧报告Game依赖SHA不能自动套到新Game；父PM最终集成可引用本次定向复审补充新Game绑定，不能称旧7文件hash审核覆盖当前全部集成。

**尚未解决：NPC按真实帧内主角事件补额度、完整routeSnapshot克隆。** 两项仍按原独立缺口保留，不因本次PASS关闭。

只更新两份quality报告；没有改源码、tsconfig或其他线报告，没有执行tests/typecheck/includes额外诊断、游戏、存档、故障注入、构建或部署。A-QUALITY-01仅完成修后静态复审，所有运行案例仍等阶段授权。**本轮只读范围已交还父PM**，未关闭任何用户反馈，不代填功能、性能、98%或用户验收。

---

## 原初审FAIL历史（以下保留原SHA、反例和行号）

**原结论：`passed=false`（仅静态）。** 安全发现为空；有一项组合恢复逻辑问题 **A-QUALITY-01 / P2**。这是精准对照旧恢复分支确认的**既有遗漏，不是本次分组/ready新增回归**。它仍位于本次核心质量审查范围，不能因为先前规格PASS而跳过。该历史发现已由上方修后定向静态复审处理；以下不是当前仍未解决的阻塞。

原Game第106行及之后的证据在当前文件后移2行；Game第105行及之前、Route/Trip行号未变。原历史“修复后须复审”等措辞保留作当时记录，当前状态以上方与JSON为准。

## A-QUALITY-01：恢复允许补给与已扣点服务同时在途

### 源码位置

- `delivery-game/assets/scripts/map-sample/V2GameSession.ts:36-38`：正常补给入口在 `phase=service && serviceCharged` 时明确拒绝启动补给。
- 同文件 `:62-65`：自动补给也排除已扣点服务。
- 同文件 `:103-110`：组合恢复检查了订单对应、picked/delivered、在途rest恢复量、非rest开放与结算对应，**未检查补给action与已扣点服务互斥**。
- `delivery-game/assets/scripts/domain/V2TripRules.ts:121-124`：只验证补给动作本身合法，不知道Route是否已有已扣点服务。
- `delivery-game/assets/scripts/map-sample/V2RouteSession.ts:198,215-216`：只验证服务门闩与进度，不知道Trip.action。
- `delivery-game/assets/scripts/map-sample/V2RuntimeController.ts:104-117`：提交前复验仍用同一Game.restore，因此不能补上组合断言。

### 最小静态反例（未执行，未制造快照）

1. 其余部分都是可通过校验的Game4/Route2/Trip2在途取餐服务状态：`phase=service`、`serviceCharged=true`、`serviceSeconds`在0与2之间；当前组Route与Trip全部picked，Dispatch仍pending。
2. Trip体力是低于100的合法值，同时携带在途免费休息action：`kind/source=rest`、`elapsedSeconds=0`、`durationSeconds=10`、`gameSeconds=600`、`restore=20`、`costCents=0`。其余订单、legs、账本等保持原合法对应。
3. Trip.restore接受该动作；Game的已扣点组picked对应仍成立；在途rest检查只要求恢复20点，本例满足；Route校验不读取action，因而整个组合可被接受。
4. 正常Game.supply入口却禁止这个组合。恢复后Game.tick `:59`先推进补给，再处理原服务，接受了正常状态机不允许产生的重叠动作。

**影响边界：** 这是坏组合可被恢复的正确性问题，不是已证明发生过的用户坏档；不声称产生了重复收入、服务二扣或外部攻击。

### 最小修法

由源码owner在组合恢复的原版本校验链中补上：**有Trip.action时，拒绝Route处于已扣点service。** 旧版本有效门闩继续使用现有推断，不能把缺失值一概当false。保留原Legacy完整校验及Game1/2各自边界；不清除action、不重置门闩、不补跑、不重签订单、不清档或新增slot来“修复”坏档。

本审查未改源码。修复后需另一位非修复者复审实际新SHA；运行案例仍等阶段授权。

### 为什么不称本次新增回归

发现上述遗漏后，才精准读取前审已登记的旧Game恢复分支：

- 历史文件：`delivery-game/temp/programming/packer-driver/targets/editor/chunks/8a/8a2aa821425f85b7718846c89d02831cc644a3b5.js.map`
- 仅输出embedded `V2GameSession.ts:89-100`，其中 `:95-99`同样没有动作互斥检查。
- 文件SHA：`fdfa98138194431d1b6b832096081a5a1e6462c9dd4ee1b03ab8edb2f62e3054`
- embedded source SHA：`41a0d0348a5ceb24dbbad657bf939955fd4d41ff73b66f63e4cdfb9b7a573309`

没有遍历Creator缓存或读取完整旧构建包，没有执行历史代码。该证据只能确定旧分支也遗漏，不能冒称运行验证。

## 其他静态追踪结果

下列是控制流核对，不是运行通过：

- **身份及分组：** Route `:63-75,90-94,196-197`重新核对了修后A-SPEC-01。商家键同时要求经营配对存在、权威`city.pois`全集唯一及名称非空；歧义为singleton。新批按首次商家及组内原序排程，旧批保留legacy-sequential。
- **整批容量及合法段：** Game `:22-30`、Route `:90-96`、Dispatch `:76-85,132-134`仍按全批重量门禁；重排后每段查询现有只读router，不修改地图。
- **组原子扣点及门闩：** Trip `:83-95`在扣点前完整检查成员；Route `:121,142-151`的组服务只扣一次、服务2秒，送达仍每客1秒/1点。Game `:105-107`未扣点picked特例覆盖全组。
- **逐单收入/经验及凭证：** Route `:149,157,220-223`、Game `:43-45`、Dispatch `:88-95`、Economy `:151-154`保留逐单令牌、receipt及已完成重试去重；没有把共享取餐改成共享交付结算。
- **ready及继续：** Route `:55,122,150-151`保留商家anchor、归零计时和门闩；Game `:33,54-60,83-87`及Runtime `:151-155`限制补给action，先同步等待区间再继续，不把ready空等补跑到下一腿。
- **自动余秒及跨批：** Game `:52-88`只在正余秒循环，Route `:125-127`在耗尽前不再代点；补给动作先消耗合法秒，实际推进秒数统一扣权益。没有运行浮点端点、跨批次数或粗细帧案例。
- **取消及中断：** Route `:158-160`从实际当前leg进度重建anchor，ready保商家位置；Game/Dispatch不回滚已结算收入经验。暂停、后台、广告及恢复首帧沿Game `:48-54`、Dispatch `:104-119,139-144`与Runtime门禁截断主角时间。
- **兼容及缓存：** Game `:91-115`先原结构组合校验，再调用Route旧完整门禁并singleton转换；新旧版本配对及旧门闩推断没有借用新组接受边界。Route `:97-111,172-225`只缓存router生成的完整期望字符串，命中仍完整比较输入legs，不以输入legs种缓存。
- **安全静读：** 所读主链未定位凭据、动态执行、命令/SQL/路径注入、网络外传或后门。结构校验不是本地档防篡改认证，空安全发现不等于安全认证。

除A-QUALITY-01外，未定位其他可确认的本范围阻塞；不将这种静态覆盖称作形式化完整性证明。

## 明示保留的两个既有独立缺口

这两项按任务边界单列，不计作本次新增回归，也不宣称已解决：

1. **NPC真实帧内事件时点/补额度：** Game `:43-48,85`仍先Dispatch.tick到帧尾，然后arrival使用默认帧尾时刻。额度为0且主角在粗帧中途完成时，粗帧与拆帧可在后续经营时长上不同。Fleet逐笔workAt归日与此是两件事；NPC日期线质量PASS不覆盖Game主链。最小方向仍是已留档契约第6节的eventAt/offset串行接线。
2. **完整Route快照克隆：** Game `:17,62,69,76,81,83`与Route `:19,53`仍复制完整state/legs；Runtime `:129`透传该 getter。期望legs缓存不等于每帧克隆消失。轻量只读进度接口应由现有Runtime/性能owner另行处理，不能删除持久化完整legs校验。未测帧率或耗时。

## 源码绑定

三主目标在审查开始及报告前重算均一致，且精确匹配前置规格报告最新SHA：

|文件|SHA-256|
|---|---|
|`delivery-game/assets/scripts/map-sample/V2RouteSession.ts`|`73d4daea391b506dd38f0fcd25fb04d9ae387e5aa07a148b42bf2699c7839a5e`|
|`delivery-game/assets/scripts/map-sample/V2GameSession.ts`|`2ff12cb7cb96d334d54c76ee68bd2db711e7ea21264585ef9b02c0480c78ecac`|
|`delivery-game/assets/scripts/domain/V2TripRules.ts`|`6ede7a45eed46a1875e187d1f728e045f44db82de6f7d83a685131d9e6093c16`|

前置`review-round2/spec.json` SHA为`9d1c3781f388c93746b472ad68280fdea63eefe45d852c0f3f8061881e70f827`。已读依赖完整SHA见JSON；报告前未发现所记录依赖SHA漂移。并行UI不纳入本结论。

## 权限与交还

- **仅源码静读、控制流推演及哈希/报告格式核对。** 未运行tests/typecheck/回归、游戏函数、合成或真实快照、故障注入、游戏页面、用户slot、Creator、构建或部署。FAIL来自静态组合反例，不来自禁止执行。
- 没有编辑任何源码、其他文档或公共进度，没有新子Agent、commit、push；只写本目录`quality-review.json`与`quality-review.md`。
- 地图制作及全部相关生产加工完全排除；只追现有路由API，不改道路、POI、地图数据或边界，不派地图任务。其他UI/资源线独立。
- **只读范围已交还父PM。** 不自行修复或关闭反馈。修复/新SHA复审由父PM安排；功能、性能、构建部署、98%视觉及用户验收均不由本报告代填。
