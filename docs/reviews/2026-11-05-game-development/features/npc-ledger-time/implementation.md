# NPC逐笔账目归日：源码实现报告

状态：**候选修复已实现，仅静态追踪；未测试、未构建、未部署、未操作存档，E05不关闭。**

执行线程：thr_sxu96cizgd；父PM：thr_axf6i4e89t。仅产品运行逻辑，无地图制作输入或产出，不派地图任务。

## 独占改动文件（绝对路径）

- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/domain/V2FleetSession.ts`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/domain/V2DispatchSession.ts`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2RuntimeController.ts`

本目录仅新增本报告、`future-cases.md`、`source-sha256.txt`。未写Game/Route/TripRules/UI/EconomyConfig/Ledger/Store或公共baseline、plan、反馈清单、dispatch；未commit/push、清理或回滚其他工作。

## 根因与实际修复

1. 原Fleet.advanceTo已经按nextDue推进workAt，但给Economy的每次账目上下文固定`dayKey:null`。Ledger只按dayKey过滤今日/近七日，故这些NPC账目只入累计/日期未知。
2. Fleet新增`setLedgerDayKeyResolver(resolver:((atMs:number)=>string)|null):void`（`:23–30`）。回调仅存在实例内，不进入V2FleetState、Snapshot或serialize的显式载荷。无回调保持null，不从外层frame日期、订单ID、UTC常量或系统当前日期猜日键。
3. Fleet.advanceTo在原有`workAt+=step`之后，以**同一个workAt**调用resolver并设置`{nowMs:workAt,dayKey:...}`，再执行原settleFleetOrder（`:82–93`）。同一时刻到期的各订单共享该时刻；跨午夜的不同workAt分别归日。保留原nextDue、step、quota、高水位、合同、订单ID、游标和完成结算顺序；循环结束恢复原账目上下文。
4. Fleet.restore使用Object.create，绕过字段初始化，故显式将resolver置null（`:33–39`）。Fleet.atomic从JSON恢复草稿后、执行change前复制原实例的resolver（`:56–58`）。回调抛错或返回非法日键仍由原事务/账目校验拒绝，不新增吞错或造日期兜底。
5. Dispatch新增同名setter，先转发Fleet再保留回调（`:36–44`）；每个transact草稿恢复后、change前重新注入（`:49–54`），防止Fleet被替换后丢回调。原公开方法参数和restore签名均不变；直接restore后的会话默认无resolver，须由可信宿主重绑。
6. Runtime继续使用原`dayKey(atMs)`的本地年月日口径（`:42–48`）。在open取得新建/恢复会话后`:90`、每次mutate恢复候选后`:105`、只读报价草稿恢复后`:135`重注入`atMs=>this.dayKey(atMs)`；所有可能推进NPC的tick/action均在注入之后。最终校验用的discarded restore不推进、不发布，无需注入。

## 静态保护检查与边界

- 追踪链：Runtime注入 → Dispatch.transact重绑 → Fleet.atomic重绑 → workAt解析 → Economy.settleFleetOrder → record/appendLedger → Ledger.dayKey筛选。定义、调用和序列化载荷均已只读核对，未执行该链。
- Fleet/Dispatch没有新增Date.now、宿主时间读取、固定时区或日期推断。Runtime不增加nowSeconds采样，只把事件毫秒传给已有dayKey。
- Runtime.mutate保留restore校验 → 必要commit → 更新committed/live顺序（`:112–117`），未改唯一写者、expected/epoch、30Hz门禁、continueTrip或foreground门禁。
- setter只改变非持久配置；不扫描、迁移、补写既有null日期账目。之后新增的真实结算（包括恢复后的离线补结算）按其workAt归日，原null历史继续留unknownDate。
- 不改持久版本/字段、经济配置`frontloaded-2026-11-04-v3-hire-training-tail`或唯一slot `delivery-county-single-slot-v1`，不清档、不新增资格门槛。
- **Game帧内主角完成/补额度时点仍有已知独立缺口。** 本批只修现有NPC workAt到日键的映射，不修长短帧事件时序，不宣称E03或完整E05解决。

## 证据与未验证项

- 实际修改由patch工具产生；中断后重新读取三文件，确认Fleet/Dispatch已落盘、Runtime尚未改，再仅补Runtime三个注入点，没有整体覆盖或回滚。
- 三个源文件均为既有untracked文件；git diff不会列出内部差异，因此不能把空diff当无改动。源码行位和`source-sha256.txt`用于本次候选定位。
- SHA由`shasum -a 256`实际读取上述三文件生成；不代表功能测试或编译通过。
- 未主动运行tests/typecheck/回归/故障注入/合成或真实存档/Creator构建/预览。编辑工具自动返回过`Array.includes`库级LSP告警，定位在原有未修改表达式；未据此变更tsconfig或扩范围，不能视为编译结果。
- 后续阶段集中用例及现有Runtime测试夹具新增setter接线需求见`future-cases.md`。当前无源码实施阻塞；构建、运行归日和保存失败行为仍待PM获准统一验证。4182旧v2-preview不含本次交付，旧v2-candidate也不是新源码证据。
