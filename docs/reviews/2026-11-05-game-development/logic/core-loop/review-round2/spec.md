# 核心配送闭环A：独立规格审查（round2）

**修后结论：`passed=true`，当前本范围规格阻塞为空。** PM最小修复A-SPEC-01后，已只读定向复审商家身份、plannedStops、新计划及新恢复校验共用链，未发现新规格阻塞。原初审 `passed=false`、原反例及24项逐条证据保留如下，不能把历史fail抹掉或把修后静态通过当作运行通过、独立质量审查通过、用户问题关闭或98%验收。

审查线程：`thr_xian3wmj7j`；父PM：`thr_axf6i4e89t`。机器可读明细、逐条证据、SHA及待执行案例见 [spec.json](./spec.json)。

## 范围与证据等级

- 只审冻结契约第1—5节：产品配送状态、同店合并、ready/continue、当前进度结构兼容。
- 主目标三文件全篇静读；沿Runtime/UI/Dispatch/Economy/Fleet既有接口追调用。没有修改源码。
- 原 `implementation.md` 仅当作者自报；判断依据为实际源码，不借作者“已实现”结论背书。
- 额外读取现存Creator缓存的旧TS `sourcesContent`，并对照旧v2-candidate中的Game3/Route1编译恢复分支，以核对原校验，而不是凭报告猜旧逻辑。**旧构建只用于历史代码比对，不是新A源码构建，也未执行。**
- 没有运行tests、typecheck、回归、故障注入、游戏函数、真实或合成存档、Creator构建、部署；没有读用户slot、接单、购买、清档、新增slot、commit/push或派子Agent。
- 依父PM最新范围纠正，地图制作是独立工作线：没有生产/加工地图资源、拼接配准、修改建筑道路街段或数据边界，没有向地图会话派工，也不把地图进度列为本产品规格门禁。既有router仅作只读依赖。

## 初审历史阻塞项 A-SPEC-01（P2，修后已静态复审消除）

**本节是初审原发现及当时行号，初审结论为 `passed=false`；以下反例和建议保留作历史，不是修后仍存在的阻塞。**

### 位置

主文件绝对路径：

`/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2RouteSession.ts`

- `:37–38`：`places` 已先经过 `operatingPOIs` 等经营过滤。
- `:63–68`：`merchantKey` 用 `this.places.filter(node + name).length===1` 证明身份唯一。
- `:72–74`：该键直接决定是否合并pickup。
- `:195–196`：新恢复校验也用同一个 `plannedStops` 作为规范列表，继承同一缺口。

### 静态反例（没有制造或执行快照）

1. 权威 `city.pois` 有两条完全相同的 `node=N, name=A`，另有可经营顾客 `M/B`。
2. `operatingPOIs` 只保留其中一条 `N/A` 和顾客 `M/B`，另一条重复 `N/A` 不在经营索引中。
3. 经过 `prepare`，`this.places` 中 `N/A` 恰好只有一条。两个不同ID的新订单均从 `N/A` 取餐时，`merchantKey` 返回同一键，规划合并为一次pickup。
4. 冻结要求是**权威 `city.pois` 配对唯一**。此时全集配对不唯一，应各自singleton；过滤后的“唯一”不能替代该证明。

影响是歧义商家仍可合并，取餐服务次数与服务预算相应少于冻结保守规则；恢复校验也接受该分组。**没有检查当前地图是否实际存在这组数据，不声称用户已经遇到这个反例。** 这属于产品商家身份判定，不是要求地图线修复数据。

### 最小建议

经营资格仍沿现有 `places`，身份唯一性另对只读 `this.city.pois` 全集核对 `node + 规范name` 恰好一项；不唯一就返回 `null`、保守singleton。不要改POI、经营索引、router、道路或边界来消除反例。

若PM原意是“只在经营子集内唯一”，须先明确修改冻结规格口径；当前审查不静默把全集要求缩成子集要求。审查者没有代修源码。

## PM修后定向复审：A-SPEC-01通过

实际只读复核修后 `V2RouteSession.ts:63–75,90–94,186–227`，没有依据PM自报直接改判。证据及静态分支推演：

- `:66–68`：同一 `matches` 精确比较node和规范name，保留非空名门禁，且同时要求 `this.places.some(matches)` 与 `this.city.pois.filter(matches).length===1`。经营资格与权威全集唯一性不再混为一个条件。
- 原反例中全集重复，即使经营子集只剩一项，全集计数仍不为1，商家键为null。全集唯一但只有非经营配对时，经营存在条件为false；空名同样不能出键。
- `:71–75`：null键不读写 `known`，每单各建组，不能因两个null而合并；只有合法相同node+name键才复用组。既有首次出现顺序和组内顺序不变。
- `:90–94`：新 `plan` 仍直接调用同一个 `plannedStops`；没有另一个宽松身份入口。
- `:196–197`：新恢复继续重建同一个规范Stop列表，并比对长度、orderId/kind/node及orderIds顺序。若输入仍把歧义订单合为多成员pickup，会与singleton规范列表不符而拒绝。
- `:72`：legacy-sequential在调用merchantKey前直接返回singleton，旧在途逐单顺序和旧恢复边界未被此修复扩大或重排。

为确认其余证据可以沿用，另做了**只读源码文本/哈希比较**：将修后merchantKey及注释在内存中替换回初审已读原文本，完整Route源码SHA精确恢复初审的 `3d4be4ecde9c8308d7aba15ec53e68a0a8c6d8c1481be53e63c7de256b9a8855`。因此相较初审只有该局部变化；Game/Trip当前SHA也与初审完全相同。没有写回源码、制造存档、导入或执行游戏代码。

**证据行号约定：** 除本复审段与2.1更新证据外，下方矩阵保留初审24项的原始行号。Route旧第69行起在修后整体后移1行；Game/Trip行号不变。初审SHA与修后SHA分开保存于JSON的 `reviewHistory` / `sourceSHA.primary`，并行依赖证据仍绑定初审已读版本，不扩审其他工作线。

## requirements：逐条静态对照

“满足”以下均指**源码中有明确对应分支**，不是已运行或已测试。路径简称 `Route`=`V2RouteSession.ts`，`Game`=`V2GameSession.ts`，`Trip`=`domain/V2TripRules.ts`；绝对路径见后文及JSON。

### 1. 状态、版本与时间

- **1.1 满足**：Route2含 `orderIds` / `stopPolicy` / `ready`，Game序列化为4；TripState仍2。证据：Route `:7–18,51`，Game `:14,92–94,102`，Trip `:17–24`。
- **1.2 满足**：沿用道路40倍率与原车速/天气修正，取餐2现实秒、逐单交付1现实秒；服务时间以每现实秒30游戏秒累积。未因合并改报价或重签期限。证据：Route `:87,129,147`，Trip `:37,103`，Game `:27–30,85`。

### 2. 合并、顺序、预算与逐单合同

- **2.1 修后满足**：初审全集/子集唯一性缺口见历史A-SPEC-01；当前同时要求经营配对存在、权威全集唯一、规范名称非空。歧义或只有非经营配对保持singleton；新规划/新恢复共用门禁。修后证据：Route `:63–75,90–94,196–197`，仅静态复审。
- **2.2 满足**：`groups`保存商家首次出现顺序，组内保存原订单顺序；每组pickup后逐单dropoff。Route `:69–75`。
- **2.3 满足**：`plan`在写状态前逐个实际Stop重验有向可达；Game先候选plan，再Dispatch按全批总重比较实际容量。Route `:89–95`，Game `:24,28`，Dispatch `:76–85,132–134`。
- **2.4 满足**：`pickupGroup`先检查非空/唯一/真实未取未送成员，再检查体力；足够才单次扣1并全组picked。多成员hook缺失拒绝，不循环旧service多扣。Trip `:83–95`，Route `:120,141–147`，Game `:85`。
- **2.5 满足**：每个dropoff保持单成员、独立1点/1秒、独立Stop token；Game按单outcome交付，Dispatch收据幂等，Economy按单入账和增加经验。Route `:74,148,156`，Game `:43–45`，Dispatch `:88–95`，Economy `:151–154`。
- **2.6 满足**：`serviceBudget`统计实际pickup/dropoff Stop；choices、首15单接单预算、路线预算共用该口径。Route `:76,112–115`，Game `:26,30`。
- **2.7 满足**：单单 `fastest` 保留自身必要服务 `+90`，Trip仍给每单建独立期限。Route `:87`，Game `:27`，Trip `:33–37`。

### 3. ready、继续与恢复体力

- **3.1 满足**：取餐服务结束清两计时和门闩、cursor前移、立即ready并返回，anchor仍为到店商家；ready.position读anchor。Route `:55,139,147–150,207`。
- **3.2 满足**：manual ready不在Game可推进phase中，等待不调用travel/serviceTime；Dispatch仍先推进NPC现实经营。Runtime在continue命令前同步旧时钟，空等不传给下一leg。Game `:47–54,69,83–87`，Runtime `mutate`/`continueTrip`，Dispatch `tick`。第6节精确时点不在此结论内。
- **3.3 满足**：Game拒绝补给action，Route只接受ready，函数只写 `phase='travelling'`；下一leg起点仍为该店。重复调用不再是ready而拒绝。Game `:33`，Route `:121`。
- **3.4 满足**：auto ready调用同一个Game.continueTrip；Game只在seconds>0循环，Route先检查remaining，服务完成恰好无余秒时不多代点。实际used扣权益，不把auto末帧尾段转手动。Game `:52–60,83–87`，Route `:124–127,149–150`。
- **3.5 满足**：顾客到达直接service，完成发token并逐单结算，之后travelling；没有新增顾客确认。Route `:139,148–151`。
- **3.6 满足**：Game及当前UI只对已扣点service锁补给，未扣点低体力服务能免费休息；已扣点服务可在体力0时完成剩余服务时间，不再扣点。Game `:36–38,59–67`，Trip `:66–98`，Route `:141–147`，UI `:211–245,273–283`。仅核对入口静态可达，未实际点页面。

### 4. 当前进度兼容与拒绝边界

- **4.1 满足**：Game在Route升级前，对原结构做Dispatch/Trip组合校验；restoreLegacy完整保留旧Route门禁后才构造singleton。已实际比对旧缓存TS和旧构建恢复分支。Game `:91–114`，Route `:168–183`。
- **4.2 满足**：转换只改Route结构标识/policy及 `orderIds`，原旧序、cursor、legs、anchor、计时、picked/arrivals保留；缺失门闩沿旧推断。恢复不调用begin、completeDelivery或服务扣点，不重抽Trip或补造奖励。Route `:171–183`，Game `:98–115`。
- **4.3 满足**：旧批 `legacy-sequential` 不重排，已travelling不撤回；之后完成pickup才ready；下一新plan才固定grouped。Route `:71,89–93,149–150,182`。
- **4.4 满足**：新旧legs始终完整序列化输入并与router生成的期望比对；缓存只接受makeLegs输出，不从输入legs种值，缓存命中也不跳过完整比较。Route `:95–110,179,203–204`。
- **4.5 修后满足**：未来/错配版本拒绝，Game1仍仅无活批且idle/finished，Game2必须TripState1/Route1，Game3必须TripState2/Route1，Game4必须TripState2/Route2；无新在途补造。原关联A-SPEC-01已静态复审消除，新组结构恢复共用修后身份证明。原版本边界证据保留：Game `:92–105,114–115`，Route `:185–222`；修后共用链见 `:196–197`。

### 5. 时钟、取消与组合完整性

- **5.1 满足**：新旧foreground/paused、clockNeedsRebase及广告门禁共同限制active；seconds<=0在补给推进之前退出；后台/恢复首帧只重基准。Game `:48–59`，Dispatch `:107–119,139–144`，Runtime生命周期入口。
- **5.2 满足**：ready取消留anchor；travelling根据当前edge/elapsed取真实anchor，腿末或无段时有当前目标节点默认值；Dispatch取消全部未完单，已结算收入经验不撤回。Route `:157–160`，Game `:42`，Dispatch `:96–101`，Trip `:106–107`。
- **5.3 满足**：未扣点pickup特例对新组逐成员 `orderIds.includes`，旧批保原singleton例外；Route.picked重建亦按全组，已扣点后必须Trip全组picked。Game `:105–107`，Route `:120,219–221`。
- **5.4 满足**：ready要求前站pickup/原店anchor/两计时0/门闩false；finished要求末端cursor/末站anchor；完整重建completed前缀的picked和 `arrival:<tripId>:<StopIndex>:<orderId>`，并交叉核对Trip/Dispatch。Route `:195–222`，Game `:99–110`。

## sourceSHA与历史校验依据

工作根目录：`/Users/sanger/Documents/ChatGPT/taptap 2`。以下为修后定向复审最新三目标绝对路径及SHA-256；Game/Trip与初审相同，Route仅有前述局部修复，初审SHA另存JSON历史：

- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2RouteSession.ts`
  - `73d4daea391b506dd38f0fcd25fb04d9ae387e5aa07a148b42bf2699c7839a5e`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2GameSession.ts`
  - `2ff12cb7cb96d334d54c76ee68bd2db711e7ea21264585ef9b02c0480c78ecac`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/domain/V2TripRules.ts`
  - `6ede7a45eed46a1875e187d1f728e045f44db82de6f7d83a685131d9e6093c16`

完整依赖SHA及历史代码文件SHA在JSON。旧恢复门禁来源：

- `delivery-game/temp/programming/packer-driver/targets/editor/chunks/4a/4aac077890d7a9171c6a9e27cfc8c63703e38531.js.map` 的Route原TS `sourcesContent:140–151`。
- `delivery-game/temp/programming/packer-driver/targets/editor/chunks/8a/8a2aa821425f85b7718846c89d02831cc644a3b5.js.map` 的Game原TS `sourcesContent:89–100`。
- `delivery-game/build/v2-candidate/assets/main/index.22b1d.js:105,117` 的旧Game3/Route1恢复分支作交叉比对，未执行旧候选。

初审期间Runtime/Dispatch有其他工作线更新日历解析器接线，当时已重读相关接口并记录后读SHA；初审交还前UI又有后续改动。JSON中的依赖SHA保留初审实际已读版本，本轮仅定向复审A-SPEC-01，没有追审其他owner后续写入。**修后结论绑定本节最新三目标SHA，不为其他owner后续改动背书。** 初审已读UI `:597` 有 `tripId+phase+cursor` 的routeViewKey，不重复把前次已修项归给A。

## deferredCases：没有执行的后续项

- 同店身份/顺序/容量/有向跨站不可达及A-SPEC-01全集重复、仅非经营配对反例；组预算与单单期限。该缺口修后定向静态复审已完成，这些运行案例仍全部未执行。
- 体力0/不足1/恰好1、全组原子拒绝、未扣点与已扣半程恢复、免费补给后继续及不重扣。
- ready长尾截断、空等后继续、重复继续、补给action门禁、顾客逐单交付和NPC独立推进。
- 自动权益精确结束于到店、ready、dropoff和跨批边界，不多代点、不消费未走尾段。
- 旧Game3/Route1所有自然阶段转换保持在途状态与已得钱经验；Game1/2、未来/错配/坏结构拒绝；没有用档执行。
- ready/finished/token非法字段、缓存命中仍完整比legs；唯一slot提交失败及并发writer候选不发布。仅列待授权案例，没有故障注入。
- 后台/暂停/恢复首帧、道路边中/腿末/零长度腿/ready取消及真实补给UI可达性。
- **第6节NPC帧内时点仍是本审查Game源码的既有未实施项，不算A新回归，不称已解决。** 不因它否决本次第1—5节；本次不代做它的实现或独立质量审查。
- 类型/构建/性能/运行验证、部署与用户验收均未进行，待PM统一阶段权限；地图制作及边界不属本产品工作线门禁。

## 交还PM

本轮仅更新本目录 `spec.json` 和 `spec.md`，保留原fail历史并登记修后静态pass、最新三目标SHA及原24项证据。源码修复由父PM完成，审查者没有修改源码、公共baseline/plan/反馈清单/dispatch或任何资源。**A-SPEC-01修后定向规格复审完成，本范围无剩余规格阻塞，只读范围再次释放给PM。** 后续独立质量审查由父PM另派；不能把本报告当运行通过或用户反馈结案。
