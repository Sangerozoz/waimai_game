# 受限应急借车 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 合法旧软锁档经主动借车和真实配送恢复，并安全取回实车归还；不制造永久资产或改旧合同。

**Architecture:** Economy 独立记录借用来源，Dispatch 聚合借还和新批次门禁，Game 保留真实路线与体力结算。Runtime 复用现有唯一 slot 事务；UI 只读领域资格并通过真实命令提交。

**Tech Stack:** TypeScript、Cocos Creator 3.8.8、Node node:test、现有单 slot Storage/Writer ports。

## Global Constraints

- 规格 `docs/superpowers/specs/2026-11-07-emergency-hero-loan-design.md` 已落实用户所选 A，不再次询问执行方式。
- 同 checkout、env_e54zrbdgxt，Codex / ccs-sanger/gpt-6.1-sol / max；复用 A/B，不 fork/worktree，不 commit/push，不改模型、凭据、连接或全局权限。
- 应急车固定基础 2 格、基础性能；不进入 state.vehicles，不算永久资产，不给 NPC、不升级、不复制。
- 领取不补钱/经验/体力/额度/广告，旧 NPC 合同只由真实亲送完成事件补额度继续推进；免费休息不变。
- 可取回实车后阻止下一应急批次，当前主角批次完整结束后明确取回并归还。
- 旧 kg、slots、部分已付报价和合法终态保持；旧 reader 拒读新借车状态，坏档/未来档不覆盖。
- 不操作用户真实浏览器或存档，不重跑原整单/长期模型，不修改参数表、地图和旧验证证据。
- 原 113 项及 10/15 单精确预算保持，新测试放入新文件。PM 独占基准/清单、集成构建与预览服务；B 独立审查。

## 任务与写集

### Task 1: 借用状态、合同兼容与真实恢复闭环（A）

**Files:**
- Modify: `delivery-game/assets/scripts/domain/V2EconomySession.ts`
- Modify: `delivery-game/assets/scripts/domain/V2FleetSession.ts`
- Modify: `delivery-game/assets/scripts/domain/V2DispatchSession.ts`
- Modify: `delivery-game/assets/scripts/map-sample/V2GameSession.ts`
- Modify: `delivery-game/assets/scripts/map-sample/V2RuntimeController.ts`
- Create: `delivery-game/tests/product-regression-1106/emergency-hero-loan.test.cjs`
- Evidence: `docs/balance/2026-11-06-balance-round-01/pm/emergency-hero-loan-1107/domain/`

**Interfaces:**
- Consume: `only-car-reproduction-1107.json` 的原始 `fixtures.signedZeroQuota`，`prepareCity(city.json)`，现有 Game/Route/Dispatch 公开动作和 `V2RuntimeStore`。
- Produce: Dispatch 与 Runtime 的 `emergencyLoanStatus`，字段为 phase、sequence、loanSequence、returnVehicleIds、canStartBatch、reason；command 新增 `borrowEmergencyVehicle {expectedSequence}` 与 `returnEmergencyVehicle {loanSequence,vehicleId}`。

- [x] **Step 1: 最小业务 RED**。按真实旧 fixture 恢复 Game，预期资格 available，使用真实 command 借车；借后车辆数组和余额/额度/账表不变，正常候选可读。测试以业务断言失败开始，不能用 TS 编译失败代替。

```js
const g=V2GameSession.restore(city,JSON.stringify(pm.fixtures.signedZeroQuota),{preserveClock:true});
assert.equal(g.dispatch.emergencyLoanStatus?.phase,'available');
const before=g.snapshot();
g.dispatch.command({type:'borrowEmergencyVehicle',expectedSequence:0});
assert.deepEqual(g.dispatch.economyState.vehicles,before.economy.state.vehicles);
assert.equal(g.dispatch.economyState.cashCents,0);
assert.equal(g.dispatch.fleetState.quotaMs,0);
assert.ok(g.normalCandidates().length>0);
```

- [x] **Step 2: 运行并归档 RED**。

```sh
node delivery-game/tests/run-v2.cjs product-regression-1106/emergency-hero-loan.test.cjs
```

预期业务断言 available/借用动作缺失失败。记录命令、exit 和原日志，不覆盖后续日志。

- [x] **Step 3: 实现最小借还聚合**。独立借用记录、只限主角的基础车解析、保留已归还记录以校验历史报价；升级新容器且不改未借旧档表示。借用资格核真实 Fleet 额度，归还在事务内卸指定 NPC 未来配车、装回实车、标记归还。

```ts
case 'borrowEmergencyVehicle':
  return d.borrowEmergencyVehicle(command.expectedSequence);
case 'returnEmergencyVehicle':
  d.returnEmergencyVehicle(command.loanSequence,command.vehicleId);
  break;
```

这里两方法由 Dispatch 聚合拥有；不得公开注入钱包/额度或跳过原 validator。数据字段固定为 heroEmergencyLoan={policyId:"hero-emergency-base-v1",sequence,active}；应急报价 vehicleRef={kind:"emergency",loanSequence,policyId} 不带 vehicleId。首次借用升 Economy/Fleet/Dispatch 3、Game 7，归还不降版；未借旧档原表示保留。接口收据记入 domain/interface-receipt.json，供 UI 和审查绑定。

- [x] **Step 4: 补充行为 RED 并实现**。逐项覆盖：资格拒绝与原子性、真实 Game 完成配送补额度、第一单仍不足、实车释放前继续/释放后新批拒绝/当前批完整结束、kg+slots 部分已付、多 NPC、0体力免费休息、借用中各批次阶段重载、归还后完成/取消历史报价重载与下一实车批次、NPC/升级/成长计数隔离。所有新动作错误保留 state/合同/账目原子不变。

```js
// 第一单完成后最多补60秒；原批次最后一单还需75秒。
finishOneRealDelivery(g);
assert.equal(g.dispatch.emergencyLoanStatus.phase,'borrowed');
assert.ok(g.dispatch.economyState.fleetQuotes.length>0);
// 继续真实亲送与旧批推进；release期间已经签的主角批次不得被撤销。
assert.equal(V2GameSession.restore(city,g.serialize()).snapshot().economy.state.vehicles.length,1);
```

`finishOneRealDelivery` 为测试内 helper，只使用 acceptBatch、beginTrip、tick、pickup、continueTrip，不直调内部结算或改字段。

- [x] **Step 5: GREEN 与自审**。运行新领域文件及既有 hero-car-reserve 文件，核对原始 fixture、参数、其他源/测试 SHA。最终报告列精确写集、容器版本、RED/GREEN数量、未覆盖及已交回写集；不自报构建或用户验收。

### Task 2: 明确借还 UI 与保存失败边界（PM，Task 1 接口冻结后）

**Files:**
- Modify: `delivery-game/assets/scripts/map-sample/V2GameUI.ts`
- Create: `delivery-game/tests/product-regression-1106/emergency-loan-runtime.test.cjs`
- Create: `delivery-game/tests/emergency-loan-ui.test.cjs`
- Evidence: `pm/emergency-hero-loan-1107/ui/`

**Interfaces:** Consume Task 1 的领域投影及 Runtime.command；Produce 真实确认动作、主角借车独立显示、真实车条目取回归还、节流状态刷新。

- [x] **Step 1: RED**。新 UI 测试实例化真实 V2GameUI，收集组件层外部绘制/点击端口；断言 available 入口、取消不提交、确认只提交一次借用；returnable 时只有无旧合同的实车能触发取回并归还。Runtime 测试使用真实 Game 和 Store、内存 storage/writer，验证借/还保存失败及二写者不发布候选，不 mock 被测事务。

```js
assert.equal(runtime.emergencyLoanStatus.phase,'available');
const before=runtime.snapshot;
failNextPrimaryWrite();
assert.throws(()=>runtime.command({type:'borrowEmergencyVehicle',expectedSequence:0}),/storage/);
assert.deepEqual(runtime.snapshot,before);
assert.equal(storage.getItem(SLOT),beforeBytes);
```

- [x] **Step 2: UI 实现**。首页无主角批次原动作区域进入主角配车页；配车页独立借用说明与确认弹窗。真实车列表保留原数量，借用中真实车按钮变为“取回并归还”，提交 `{type:'returnEmergencyVehicle',loanSequence,vehicleId}`。借车不进入普通车升级列表。订单大厅在无候选/等待归还时给配车入口。借还弹窗取消无状态改变，重复确认不重复提交。

```ts
this.runtime.command({type:'borrowEmergencyVehicle',expectedSequence:0});
this.runtime.command({type:'returnEmergencyVehicle',loanSequence,vehicleId});
```

- [x] **Step 3: 资格变化刷新与 GREEN**。在现有 .5 秒刷新中观察 loan status 的 phase/候选实车/在途状态变化，更新按钮而不每帧重建页面；已有贷款历史 returned 不能继续显示“领取”。完成 UI/runtime 行为 GREEN 后归档 diff 与 SHA。

### Task 3: 独立完整审查（B）

**Files:** 只读 Task 1+2 的原始 source-before、副本差分、规格、接口收据和 RED/GREEN 证据；审查结果仅写本任务独占 review 目录或在消息中回报由 PM 保存。

- [x] **Step 1:** PM 冻结源码/测试 SHA 和逐文件 diff，将完整包交 B。规格符合性、代码质量分别裁定；重点审查历史报价来源、旧 kg/slots 容器匹配、批次边界、归还原子性、保存失败与二写者。
- [x] **Step 2:** Critical/Important 逐项给原作者修复，新增回归先RED后GREEN；B只复核变化和关联门禁。无独立 PASS 不部署。

### Task 4: PM 验证、构建与预览身份

**Files:** 只写 `pm/emergency-hero-loan-1107/` 门禁/报告、权威进度清单和独立新 build 输出。

- [x] **Step 1: 默认回归与 typecheck**。顺序执行并保存完整命令、exit、TAP数量及源hash；旧113行为全部保持。

```sh
node delivery-game/tests/run-v2.cjs
node --test delivery-game/tests/emergency-loan-ui.test.cjs
node delivery-game/scripts/typecheck.cjs
```

- [x] **Step 2: Creator**。使用前批已验证构建配置，只改 name/outputName 为 `v2-emergency-hero-loan-1107`。构建前后输入SHA相同，留原失败/诊断/成功日志；Finished 和实际输出存在才算通过。
- [x] **Step 3: 独立新 headless 定向借还**。仅以原始合法终态 fixture 在新隔离上下文核对入口、借车确认、真实配送/ready、reload和归还；标注 fixture 的来源与范围，不当用户档或新全流程证据。保存截图、事件和包身份，关闭上下文。
- [x] **Step 4: 预览部署**。PM 只更新原4182/4196静态服务到已过门禁的新包，读回新终端ID；逐端 index 与所有14 JS SHA 匹配。保留旧 build 作为源码/输出历史，不修改真实用户存档。
- [x] **Step 5: 同步收口**。更新 E09 与当前进度、test-results-current、handoff、implementation-baseline；借车已实现/已验证/已部署分清。旧防新增收据不改为新基准，记录本批批准的源变化。用户选择A、原B证据、长期两个终点未到及整体98%未验收保持。


2026-11-07执行收口：Task1/2/3/4的实施、审查、默认145/145、UI11/11、typecheck0、Creator36/721输入稳定和双端30项HTTP核对已完成。补审新增自动Runtime完整路径及现金29999/30000/30001分独立边界，32/32；五源保持原冻结SHA。详见 `docs/balance/2026-11-06-balance-round-01/pm/emergency-hero-loan-1107/report.md`。

Task4 Step3执行例外：原始源码终态在Creator包中被原mapKey门禁拒读，失败与原slot字节保留。经三层几何SHA和完整已签腿验证、B独立递归核对，只在另隔离origin使用`route.mapKey`运输适配副本完成真实UI流程，不改生产路由、地图、资金、额度或合同。该步骤的勾选表示定向UI验证与边界记录完成，**不代表原自然终态跨包直接恢复通过**。此兼容边界仍BLOCKED，未做生产迁移机制；此前公开包与新包524份resources逐字节相同。
