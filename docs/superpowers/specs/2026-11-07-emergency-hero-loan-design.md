# 旧软锁档的受限应急借车

2026-11-07。用户已明确选择“受限应急借车（推荐）”。本规格落实已选 A，不再请求同一选择；不实施 NPC 未完成合同取消。当前状态为设计冻结和实施开始，未表示功能已交付。

## 目标与来源

让已经合法陷入零余额、零额度、唯一旧车被 NPC 未付合同保留的档案，经玩家主动借用基础车，恢复真实亲送。旧合同、进度、报价、已结算收入和主角成长完整保留。新档的保留实车防线继续有效。

来源为 `docs/balance/2026-11-06-balance-round-01/pm/softlock-prevention-1107/recovery-options.md` 的 A，以及本线程用户明确选择。历史隔离夹具为 `pm/only-car-reproduction-1107.json` 的 `fixtures.signedZeroQuota`，不是用户档。该夹具旧批已推进 60000ms，尚余 45000/75000ms 两笔结算；亲送一次补 60000ms，故不能假设一单后必可还车。

## 玩家规则

1. 先用完整旧 reader 校验档案。主角未配车、无活动主角批次、额度为零、至少一辆永久车且每辆均由未付 NPC 合同占用、余额不足最便宜可买车辆时，才允许主动借用。未签约且可卸回的车、有空闲实车或有钱买车，继续正常操作。
2. 唯一应急车固定为基础 2 格、基础速度与车辆收益，沿用真实主角成长、普通报价、路线、时限、体力、食品风险及真实结算。领取本身不加钱、经验、体力、额度或广告权益；免费休息保持原规则。
3. 应急车不是永久资产，不写入 `state.vehicles`，不计车辆数量、付费车型、成长目标或资产节点，不可分配 NPC、升级、出售或重复领取。NPC 新签约保留实车检查始终只认永久车。
4. 旧 NPC 批次只消耗原有与真实亲送补入的额度。不得抢回旧批用车、改旧报价、提前结算或取消合同。仍没有可取回实车时，可继续亲送补额度，不按固定单量或时间收车。
5. 一旦至少一辆永久车不再被未付 NPC 合同保留，新应急配送批次不再可签；已经签约的主角批次可按原合同完整结束。不得在途中删除借车或改其报价。候选预览、手动接单及自动接单均遵守同一入口门禁。
6. 无主角在途批次时，由玩家明确选择可取回的实车并“取回并归还应急车”。在一个事务中卸下该实车的 NPC 未来配车、装备主角、将借车标记归还；不取消旧批，不修改其他车的配置。车辆又被保留时失败且原子不变。
7. 借车期间主角不能用普通卸装绕过归还流程；买车和正常成长仍自由。应急车历史身份在归还后继续可校验，防止已完成借车订单失去车辆来源。

## 领域与持久化

- Economy 拥有独立、版本化的借用记录及固定基础车效果解析。真实车集合仍是永久资产唯一来源。只在处理主角借车合同或显示时解析虚拟基础车，NPC 从不获得该车。
- Dispatch 是借还与批次门禁的聚合入口，借车资格同时检查 Economy 和 Fleet。UI 不重算资格、不直接改快照。
- 借用后的 Economy/Fleet/Dispatch 使用彼此一致的新容器版本，Game 使用新组合版本；旧 reader 应明确拒绝借车档。未借车的既有存档继续按原表示无损读取，不自动造车或切换资产。
- 新 reader 先执行所有旧合同、路线、食品、账目及合约对应关系验证，再进行已批准的显式新行为。旧 kg 合同的金额、载重、dueMs、部分支付及占车保留；新亲送继续 slots。
- 下调版本、混装容器、伪造借车身份或性能、借车进入永久资产/NPC、归还后仍有借车活动批次均拒读。未来或坏档不能覆盖唯一 slot。
- `V2RuntimeStore` 的唯一 slot、writer lease、epoch 和 expected bytes 不变。Runtime 命令仍走候选恢复、动作、完整校验、保存成功后才发布的事务。重复点击、重载、跨页、二写者和持久化失败都不得复制资产或结算。

## 接口冻结

PM采纳A只读接口建议，固定独立借用记录、明确合同来源与单调序号。主角实车 vehicleId 借用时仍为 null；新应急合同使用 vehicleRef={kind:"emergency",loanSequence,policyId:"hero-emergency-base-v1"}，不冒用真实 vehicleId。Economy 保存 heroEmergencyLoan={policyId,sequence,active}，归还后保留序号。首次借用原子升 Economy/Fleet/Dispatch 3、Game 7；未借旧档不改版本。跨层名称如下：

```ts
type EmergencyLoanStatus = Readonly<{
  phase: 'unavailable' | 'available' | 'borrowed' | 'returnable' | 'returned';
  sequence: number;
  loanSequence: number | null;
  returnVehicleIds: readonly string[];
  canStartBatch: boolean;
  reason: string;
}>;
// Dispatch 和 Runtime 都提供同一只读投影：
get emergencyLoanStatus(): EmergencyLoanStatus;
// 复用 Runtime.command() 的持久化事务：
{ type: 'borrowEmergencyVehicle'; expectedSequence: number }
{ type: 'returnEmergencyVehicle'; loanSequence: number; vehicleId: string }
```

借用 expectedSequence 必须与当前序号一致，归还 loanSequence 必须与活动序号一致；重复/陈旧命令拒绝。Runtime.command 对借还经 Game 行程边界包装后转 Dispatch，要求无活动主角批次、Route 为 idle/finished、Trip 无进行中动作。借还失败返回明确业务错误，状态/钱包/额度/合同均不变。资格投影读操作不得推进时钟或写存档；命令提交前用真实当前状态重新核对。

## UI

- 首页无主角批次的现有动作位置提供“应急借车”或“应急借用中 / 归还应急车”入口，进入主角配车页；订单大厅无车时也可进入，不让玩家停留在空列表。
- 主角配车页单独显示应急车与状态，不把它列入“已拥有车辆”列表或普通升级入口。
- 借车确认清楚说明“临时基础车 2 格；旧合同保留；需亲送补额度；实车可取回后归还”。借用和归还都由明确确认提交，取消弹窗无副作用。
- 可还车时，真实车辆条目提供“取回并归还”，显示当前 NPC 配车或旧批保留情况。旧批占车与主角在途时不可归还。
- 资格变化和旧批释放可在现有节流 UI 刷新周期更新；不移动已认可总体布局，不恢复首页已删的签约/速度/收益浮字。

## 验证门禁

- 先 RED 后 GREEN，使用原始合法终态 fixture；不重跑会覆盖原证据的生成器。
- 在真实 Game/Route 上完成借车、普通接单、行驶、主动取餐、ready 主动继续、逐单交付、真实补额度、旧批结算和取回实车归还；至少覆盖第一单仍不能释放车。
- 覆盖借车在途保存/重载、归还后历史报价恢复、重复借还、合法 kg 与 slots 旧批、部分已付、多 NPC 占车、0 体力免费休息；正常/未签/可卸/可买不误领。
- 覆盖 NPC/升级/资产计数防线，恢复实车后阻止下一批而允许当前批完整结束。
- 单 slot 拒读坏档/未来档、二写者/冲突/存储失败不发布未保存借车状态。
- 原 113 项默认回归、10/15 单精确预算和原已签合同保持；全量 typecheck、作者独立审查、Creator 实际构建与预览 HTTP 包身份通过后才部署。
- 本轮只使用隔离夹具/独立 headless，用户真实浏览器与存档不操作。不扩为长期二八、真机 FPS、广告 SDK 或整体 98% 验收。

## 写集与职责

同 checkout / env_e54zrbdgxt，固定 Codex / ccs-sanger/gpt-6.1-sol / max。A 负责 Economy/Fleet/Dispatch/Game/Runtime 接线及新领域测试；PM 负责 UI、新 UI/存储边界验证、规格清单、集成构建与服务；B 独立只读审查。修改前的 764 项输入及六源副本在 `pm/emergency-hero-loan-1107/`。不 fork/worktree，不 commit/push，不修改地图、参数表、旧证据、账号、连接或全局权限。
