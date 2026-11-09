# NPC 逐笔归日：独立代码质量审查

## 结论

**PASS（仅静态源码质量）**。未发现本次实现新增的安全阻塞、逻辑错误或实际漏注入路径。`security_concerns=[]`，`logic_errors=[]`。

审查者：`thr_ef9asz76ur`；父 PM：`thr_axf6i4e89t`；同环境：`env_e54zrbdgxt`。本结论依据独立读取源码，不以作者报告或父 PM 的规格 PASS 代替审查。

**未运行测试、typecheck、回归、构建、故障注入、游戏操作或合成/真实快照；未读写真实 slot。** 不代表 E05 全闭、实际账单验收或产品 UI 98% 达标。

## 范围与证据版本

完整读取三份候选：

| 源码 | SHA-256 |
| --- | --- |
| `delivery-game/assets/scripts/domain/V2FleetSession.ts` | `1e1ccd5242762260213f8744c3cddf4328bbe35b100a0fba779e4c9cd7facb3a` |
| `delivery-game/assets/scripts/domain/V2DispatchSession.ts` | `adbc39af0f133714df647a0e8df78789171efbec94468d227557001ddf422a6a` |
| `delivery-game/assets/scripts/map-sample/V2RuntimeController.ts` | `bb6dc40f960f5867b96bf9eeaad218d8d6a9d2aa648b53ce34aa0afcff892d81` |

依赖仅追到 `V2EconomySession.ts`、`V2Ledger.ts`、`V2GameSession.ts`、`V2RuntimeStore.ts`，完整内容已读取，依赖 SHA 记录在同目录 JSON。

三份候选目前均为 Git 未跟踪文件；针对这些路径的 `git diff` 和 `git ls-files --stage` 没有条目。**没有版本化前态，不将空 diff 当作无改动或完整差异证明。** 本审查绑定上述具体源码快照。

## 重点静态追踪

### 1. 多层恢复、atomic 与回调生命周期

- Fleet 新建时初始化 null：`delivery-game/assets/scripts/domain/V2FleetSession.ts:24`；`Object.create` 恢复分支也显式初始化 null：同文件 `:37–39`。
- Fleet `atomic` 的 `serialize → restore` 后立即复制原 resolver，再执行变更：同文件 `:56–58`。
- Dispatch 同名 setter 先交由 Fleet 校验/接收，再更新自己的非持久配置：`delivery-game/assets/scripts/domain/V2DispatchSession.ts:44`。非法非函数/非 null 入参在赋值前失败，不会形成两层配置不一致。
- Dispatch `transact` 每次恢复后、执行变更前重注入：同文件 `:49–52`；之后额外的 `syncHeroCompletions` 也经过 Fleet.atomic，配置继续被复制。
- Fleet.atomic 通过 `Economy.replaceFrom` 更新共享钱包内容，而非更换共享钱包对象：`delivery-game/assets/scripts/domain/V2FleetSession.ts:58`、`delivery-game/assets/scripts/domain/V2EconomySession.ts:98`。Dispatch 成功时成对替换草稿 economy/fleet：`delivery-game/assets/scripts/domain/V2DispatchSession.ts:53`。未发现换实例后回调丢失或钱包分叉。
- Dispatch 当前事务没有修改 resolver 的分支，所以父 Dispatch 保留的 resolver 与已提交 Fleet 的配置一致，不需要在成功提交时另从草稿回拷配置。

### 2. this 与替换实例的引用

Runtime 三处注入均使用 `atMs => this.dayKey(atMs)`：`delivery-game/assets/scripts/map-sample/V2RuntimeController.ts:90`、`:105`、`:135`。箭头函数保持控制器 this，不依赖调用它的 Fleet 草稿 this，也未捕获旧 Fleet/Economy。

Game.restore 的到达端口使用 `result.route` 属性读取：`delivery-game/assets/scripts/map-sample/V2GameSession.ts:98`；随后 route 的替换发生在 `:114`。该端口不是捕获替换前 route 对象，本次回调复制没有引入旧实例引用。

### 3. 跨午夜逐笔日键与旧 null 账目

触发链：

`Fleet.advanceTo → workAt=lastAdvancedAt → step=min(remaining, quotaMs, nextDue) → workAt+=step → setLedgerContext({nowMs:workAt, dayKey:resolver(workAt)}) → settleFleetOrder → appendLedger`。

证据：

- 原事件推进与 `nextDue` 截断位于 `delivery-game/assets/scripts/domain/V2FleetSession.ts:84–87`；日键解析与结算在 `:89–90`。
- 同一完成时点的多笔订单共享该步 workAt；跨午夜的不同到期步分别调用解析器。传给解析器的时点与账目 `nowMs` 是同一个值，没有改用 frameEnd、今天或 Date.now。
- Runtime 复用本地年月日规则：`delivery-game/assets/scripts/map-sample/V2RuntimeController.ts:42–44`。Ledger 的 UTC 日期构造只用于验证日键格式/实际日历日期（`delivery-game/assets/scripts/domain/V2Ledger.ts:13–18`），不是替换宿主的归日时区。
- Ledger 写入上下文并按 dayKey 聚合：`delivery-game/assets/scripts/domain/V2Ledger.ts:34–36`、`:43–45`。
- resolver 为 null 时仍写 dayKey=null；没有遍历修改历史 entries 的路径，老 null 账目不会被重新分日。

上述是静态控制流结论，不是已执行跨午夜或离线用例。

### 4. 失败原子性、上下文恢复及非法回调边界

- 成功推进结束后，Fleet 恢复推进前 ledgerContext：`delivery-game/assets/scripts/domain/V2FleetSession.ts:84`、`:93`。
- 回调抛错，或返回不能通过既有 LedgerContext 校验的值时，在草稿内抛出：`delivery-game/assets/scripts/domain/V2FleetSession.ts:89` → `delivery-game/assets/scripts/domain/V2EconomySession.ts:101` → `delivery-game/assets/scripts/domain/V2Ledger.ts:17–18`。
- Fleet 提交位于全部变更/校验之后（`V2FleetSession.ts:57–58`），Dispatch 提交亦在变更及校验之后（`V2DispatchSession.ts:52–54`）。因此中间某步失败不会将前面已结算的草稿订单、额度、时间高水位或临时上下文写回 live。
- Runtime 失败候选不会进入 commit/publish（`delivery-game/assets/scripts/map-sample/V2RuntimeController.ts:111–119`）。异常路径丢弃整个草稿即可，不缺少针对 live 的 finally 上下文恢复。
- setter 仅承诺接收函数或 null；返回值沿用 LedgerContext 校验，并未新增更严格的返回策略。运行时绕过类型后返回 null，既有 dayKey=null 规则仍会接受；这不影响 Runtime 注入的正常本地日键回调，也不应误报成新缺陷。
- 原子性不包含宿主回调主动修改外部对象的副作用；当前 Runtime 注入只进行日期计算，未见该副作用链。

### 5. 首次恢复离线结算与实际入口覆盖

- `open` 中 `store.open` 先纯恢复/校验；拿到 session 后先注入 resolver，再首次 tick：`delivery-game/assets/scripts/map-sample/V2RuntimeController.ts:85–92`。Domain 恢复/校验不提前推进 Fleet，所以恢复后的首笔离线 NPC 入账不会发生在注入之前。
- `mutate` 每次从 committed 恢复候选后立即注入，再同步时钟/执行 action：同文件 `:104–111`。
- `drive` 经 mutate，即使传入 `synchronizeClock=false`，仍先执行同一注入再由 action tick：同文件 `:198`。
- 只读报价使用独立 draft，在 `acceptBatch` 前注入，既不覆盖 live，也不 commit：同文件 `:132–139`。
- Dispatch 可推进 Fleet 的 `completeDelivery` 和 `tick` 均在重注入后的 transact 中运行：`delivery-game/assets/scripts/domain/V2DispatchSession.ts:88–95`、`:104–121`。其余会进入 Fleet.atomic 的同步路径亦有复制。
- Runtime 其他公开只读查询不执行 Fleet.advanceTo。所读范围内未发现新的实际漏注入入口。

### 6. 非持久配置与保存/门禁边界

- Fleet.serialize、Dispatch.snapshot、Game.serialize 都使用显式持久化结构：`delivery-game/assets/scripts/domain/V2FleetSession.ts:32`、`delivery-game/assets/scripts/domain/V2DispatchSession.ts:47`、`delivery-game/assets/scripts/map-sample/V2GameSession.ts:14`。resolver 不进入正式保存 JSON；未新增保存版本或持久化配置字段。
- 独立 restore 后 resolver 回到 null 是设计约定。Runtime 只用于验证的二次 restore 不推进（`delivery-game/assets/scripts/map-sample/V2RuntimeController.ts:113`），因此该验证实例不需要注入。
- 新增注入在候选侧，不跳过 Store 的写者、epoch、expected 检查：`delivery-game/assets/scripts/map-sample/V2RuntimeStore.ts:24–30`、`:87–94`。坏档原值仍在 restore 失败时保留：同文件 `:65–66`。
- open 仍先 commit 再发布（`V2RuntimeController.ts:94–96`）；mutate 仍先 restore 验证、必要的成功 commit，再发布（`:113–117`）。
- 当前源码保留 30Hz 合并门禁（`:196–198`）、continueTrip 的旧阶段同步及前台命令门禁（`:142–154`）。
- 当前 Fleet 仍通过 nextDue/workAt/quota、合同与 heroEventCursor 推进；本次静态结论没有替代“与缺失前态逐行比较”的证据。Game 帧内主角完成事件精确时点按任务声明属于既有未实现项，不判为本次新回归，也不声称本次已解决。

## 非阻塞准备项

**S01：后续阶段补齐 Runtime 测试替身接口。** 用户已明确既有替身缺少新 setter；三个实际调用点为 `V2RuntimeController.ts:90`、`:105`、`:135`。本次未读取/执行夹具，不将此写成已观测运行失败。阶段集中验证前由实现/集成方补齐，不要求本只读审查修改测试或提前执行。

## 限制与交付边界

1. 仅静态源码审查；全部运行检查按要求未执行，不造通过或失败。
2. 未获取三份未跟踪文件的版本化前态；结论仅绑定记录的 SHA，不覆盖后续改动。
3. 只写本目录 `quality-review.json`、`quality-review.md`；不修改源码、公共 ledger/dispatch/plan/baseline，不新建子 Agent，不执行 Git 写操作。
4. 不读取地图制作资料，不派地图任务，不将地图生产纳入本报告。
5. 采纳、修正、后续构建与验收由父 PM 负责；本报告不清用户反馈、不关闭 E05、不替代用户体验验收。
