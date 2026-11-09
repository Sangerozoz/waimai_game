# 主角可恢复车辆防线 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. User preference overrides fresh workers: reuse B as author and PM as independent reviewer, same checkout.

**Goal:** 新NPC配车与签批始终保留主角可恢复车辆，保持合法历史档可读及旧批原语义。

**Architecture:** Economy提供只读布尔查询并在拟议NPC配车与两个合同注册入口检查。Fleet在签新批前使用同一查询，已有批照常推进；restore不增加该新动作约束。

**Tech Stack:** TypeScript、Cocos既有TypeScript编译器、Node原生test；只用隔离内存fixture。

## Global Constraints

- 精确规格：`docs/superpowers/specs/2026-11-07-hero-car-reserve-design.md`。
- B写集：`docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/`；生产、A输入和旧证据只读；不构建产品/部署/开浏览器/读用户档。
- Provider `codex` / Model `ccs-sanger/gpt-6.1-sol` / reasoning `max`；不改路由或权限。
- 使用同checkout，不fork/worktree/commit/push；只清理自己创建的scratch。
- 正确RED先于候选实现；不改价格、额度、旧合同或存档校验来使测试通过。

## Task 1: 隔离候选的完整TDD交付

**Files:**
- Create under B写集：`stage/domain/V2EconomySession.ts`、`stage/domain/V2FleetSession.ts`（原源码的精确基线副本，在RED后才编辑）。
- Create：`stage/tests/hero-car-reserve.test.cjs`、`run-stage.cjs`、`report.md`、`receipt.json`、RED/GREEN原始日志。
- Read：两个生产源、`delivery-game/tests/product-regression-1106/helpers.cjs`、现有fleet/current-contract测试。
- Read historic fixture：`docs/balance/2026-11-06-balance-round-01/pm/only-car-reproduction-1107.json` 的 `fixtures.beforeNPCSigning` 与 `fixtures.signedZeroQuota`；它们来自实际公开动作，不制造余额/额度。

**Interfaces:**
- Consumes: `V2EconomySession.assignVehicle(riderId:string,vehicleId:string|null):void`、`registerFleetOrders(riderId:string,ids:string[],weights:number[]):V2FleetQuote[]`、`registerSlotFleetOrders(riderId:string,ids:readonly string[]):V2FleetQuote[]`、`V2FleetSession.advanceTo(nowMs:number):void`。
- Produces: `V2EconomySession.hasRecoverableHeroVehicle:boolean`，返回脱离私有状态的标量；拒绝文案“请为主角保留一辆可用车辆”。两个方法原有签名不变。

- [x] **Step 1: 写真实行为RED并先运行。** 最小缺陷用例可直接使用公开Economy方法；另加一个Game/Dispatch路径证明实际入口拒绝。

```javascript
test('one earned delivery cannot surrender the last recoverable hero car',()=>{
 const e=new V2EconomySession('slots-v1'),id='reserve-first';
 e.acceptSlotBatch([{id,kind:'ordinary'}],{[id]:{deliveryMetres:100}});
 assert.equal(e.completeDelivery(id).incomeCents,2000);
 e.hireRider('npc-1');assert.equal(e.state.cashCents,0);
 e.assignVehicle('hero',null);const before=e.serialize();
 assert.throws(()=>e.assignVehicle('npc-1','starter-1'),/请为主角保留一辆可用车辆/);
 assert.equal(e.serialize(),before);
 e.assignVehicle('hero','starter-1');assert.equal(e.state.riders[0].vehicleId,'starter-1');
});
```

Runner先编译原生产依赖到自建scratch，使用 `MAP_ROUTER_MODULE=<scratch>/map-sample/RoadRouter.js` 运行测试；RED应是 `Missing expected exception` 等业务断言失败，不是缺模块或编译错误。记录实际命令、退出码、sourceSHA、scratch清理。

- [x] **Step 2: 增加恢复和旧批边界用例。** 用已保存的合法历史fixture恢复，分别检查未签批危险状态不再自动签约、NPC卸车后主角可归还，以及已签零额度终态仍逐字节往返。对带剩余额度的已签旧批，使用公开动作产生的历史夹具；有必要可用RED阶段未修改代码生成并保存，不能更改快照余额/额度冒称合法路径。覆盖kg与slots注册入口、旧批车排除、真正第二车允许、10/15预算和旧占车约束。

- [x] **Step 3: RED正确后编写最小候选。** 只改stage两个TS：车辆可恢复集合由NPC当前占用与未付合同排除；NPC非空配车在拟议状态检查；注册入口检查；Fleet新签批前跳过危险状态。恢复校验与旧批推进保持。不要把主角卸车直接禁止，也不要把单纯现金足够当作备用车。

- [x] **Step 4: 运行GREEN和相关回归。** `run-stage.cjs`叠加候选至临时脚本树后编译真实依赖并运行新增测试、现有 `v2-economy.test.cjs`、`v2-fleet.test.cjs`、`v2-dispatch.test.cjs` 和 `product-regression-1106/current-contract.test.cjs`。编译严格、noEmitOnError。若旧测试与新规则冲突，说明具体差异，不能盲目改旧测试放宽。不跑原B浏览器整单。

- [x] **Step 5: 交付可审查结果。** `receipt.json`记录候选两个源、测试、runner、基线源的SHA，RED/GREEN准确计数/退出码，前后生产与36输入无漂移、fixture来源与清理结果。说明已软锁终态仍未救援，停止本写集编辑。

## Task 2: PM独立门禁与串行集成

- [x] PM核对spec覆盖、实际RED原因、候选差分、既有批与恢复语义；以候选runner复现最少必要的GREEN。不以作者文字替代实际结果。
- [x] 等A长期模型完成输入读取/运行并交回，同步记录真实结果或失败；只有36项基线仍匹配时才集成候选。
- [x] PM仅复制候选两个TS及新测试到 `delivery-game/tests/product-regression-1106/hero-car-reserve.test.cjs`，并为 `run-v2.cjs` 增加 `map-sample/PlaceCatalog.ts` 编译入口；原224保护清单不改，另建批准的三份旧文件前后SHA收据。运行 `node delivery-game/tests/run-v2.cjs` 和项目既有typecheck命令，记录命令/exit与实际覆盖。
- [x] 如门禁通过，PM按现有构建方法单独构建候选并核HTTP产物身份，再更新试玩；没有新运行画面时不报浏览器验收或98%。更新E09为防新增结果与旧档救援分别开放，用户反馈正式关闭数不变。

## 11-07执行结果

B候选交回、A独立审查、PM精确集成及默认113/113、typecheck0、Creator36/Finished和双端HTTP门禁已完成。完整证据：`docs/balance/2026-11-06-balance-round-01/pm/softlock-prevention-1107/report.md`。只完成防新增；旧已签零额度档救援、全产品及98%仍开放。
