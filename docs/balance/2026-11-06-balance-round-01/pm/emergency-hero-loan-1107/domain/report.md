Task 1 的受限应急借车已实现并交回，等待 PM 集成及 B 独立审查。最终窄测为 **35/35、exit 0**：新增领域 17 项，原 hero-car-reserve 18 项。依据 `behavior-006.json` 与原始 `behavior-006.log`；最终五源和新测试与该次运行所记录的 SHA 逐项一致。当前没有领域测试失败。

工作目录为 `/Users/sanger/Documents/ChatGPT/taptap 2`，线程 `thr_gf8gehviua`、环境 `env_e54zrbdgxt`。沿本批指定 Codex / ccs-sanger/gpt-6.1-sol / max 接续，未改路由或权限，未派工、创建 worktree、commit、push。实现依据已冻结 spec 与 plan 的 Global Constraints / Task 1，接口原始收据 `interface-receipt.json` 保留；其中“implementation pending business RED”是早期接口签收状态，不是本报告的完成状态。

**最终行为与版本**

- Economy 保留独立 `heroEmergencyLoan={policyId:"hero-emergency-base-v1",sequence,active}`。借车始终不加入 `state.vehicles`，主角实车 `vehicleId` 保持 null；报价仅带 `vehicleRef={kind:"emergency",loanSequence,policyId}`，不含真实 `vehicleId`。
- 实际领取要求：主角无实车、无主角批次，Fleet 零额度且无待补事件，所有永久车均有未付 NPC 合同，现金小于当前最便宜合法购车报价。expectedSequence 与活动序号严格校验；失败不改变组合快照。
- 应急效果解析使用基础 starter 1 级，当前容量 2 格、车辆速度和收益因子均为 1；真实主角经验、接单时 xpMultiplier、路线、体力、食品风险和结算原规则保留。
- 首次成功借用原子升级 Economy/Fleet/Dispatch 至 3、Game 至 7。未借旧档保持原版本和表示；归还后保留记录及版本。新 reader 拒绝混装/下调/未来容器、伪造来源/性能、把应急来源塞入永久资产或 NPC 合同、归还后仍有活动借车合同。冻结旧 reader 对活动及已归还的 3/7 容器均拒读。
- 新批次门禁落在 Economy 接单入口，Game 普通/专送预览同步隐藏。可取回实车后，已签主角批次继续完整结算，未签新订单拒绝；归还只在空主角批次、Route idle/finished、Trip 无动作时通过 Game.command。Runtime.command 在现有 mutate 事务内转 Game.command。
- 归还在单事务中卸下目标车的 NPC 未来配车、装备主角、标记 inactive。仍有未付合同的实车拒还。钱包、额度、已签合同、已付收入和其他 NPC 批次保持。NPC 防新增仍只认永久实车，不将应急车当备用。

**真实终态与兼容输入的范围**

唯一自然可达终态仍是原 `pm/only-car-reproduction-1107.json` 中 `fixtures.signedZeroQuota`，只读取其当前原文件；未运行旧生成器。测试先确认恢复后字节表示相同，再通过 Game.command 主动借用，真实 acceptBatch / beginTrip / tick / pickup / continueTrip 完成配送。

首单仅补 60000ms 额度。真实帧尾消耗也计入：`quotaMs + (NPC elapsedMs - 60000) == 60000`；等待后旧批为 elapsedMs=120000、paidCount=1、额度 0，最后一单仍保留实车。下一主角两单批次在首单后释放实车，第二单合同保持并真实完成，随后主动归还，再完成一笔实车订单。没有按“一单即恢复”实现。

其他输入均标为隔离兼容 fixture，不能据此声称另有自然可达终态：

| 输入 | 产生方式与限制 |
| --- | --- |
| kg NPC 旧合同 | 克隆原 signedZeroQuota，仅将 NPC 载重表示/编号改成 kg-v1：两单各 1kg、容量 2kg，保留现金、额度、105000/135000 dueMs、elapsed60000、金额和主角历史；新亲送仍 slots。 |
| 多 NPC | 复用已保留 `historical-fixtures.json` 的 slots-v1/reservedOldCarAndConfiguredNewCar 中两个付费资产和两名 NPC；新增一个明确假设的旧 NPC 签约批并冻结零额度。不增加车辆、现金、账目收入或主角完成事件；不是当前防新增规则可新造出的终态。 |
| 零体力 | 原自然终态只改变 stamina=0 / blocked=true。借车不补体力，真实无单免费休息 20 秒后配送。 |
| 有剩余额度 | 将原 slots-v1/signedRemaining Fleet/Economy 保持原样放入空 Game 包装，验证借用拒绝；不是额外自然终态。 |

多 NPC 用例在第一辆实车真正释放时停止等待，明确断言另一 NPC 仍有未付合同，归还后其全部 Fleet 状态和账目保持。kg/slots 均经历第一笔支付、保存重载、第二笔支付和归还，每个旧订单收入只记账一次。

**验证与原始失败**

所有运行使用同一命令形式，传入下表的文件集合；每次独立保存 label.log 与 label.json，收据含实际命令、cwd、开始/结束时间、exit、输入 SHA、log SHA 与新增 scratch 残留。`run-check.py` 只包装现有测试 runner，未改旧 runner 或旧测试。

```sh
python3 docs/balance/2026-11-06-balance-round-01/pm/emergency-hero-loan-1107/domain/run-check.py LABEL product-regression-1106/emergency-hero-loan.test.cjs [product-regression-1106/hero-car-reserve.test.cjs]
```

| 原始 label | exit | TAP 结果 | 解释 |
| --- | --- | --- | --- |
| red-001 | 1 | 0/1 | 编译通过后的业务 RED：available 投影不存在。此后才写生产。 |
| green-attempt-001 | 1 | 无 TAP | 新 vehicleRef.policyId 的字面量推导导致编译错误，保留原日志；不计业务 RED。 |
| green-001 | 0 | 1/1 | 最小借用业务通过。 |
| behavior-002 | 1 | 7/8 | 测试遗漏真实帧尾已消耗的 286ms；修正额度守恒断言，未改生产计时。 |
| red-003 | 1 | 8/9 | 业务 RED：永久车辆可夹带应急来源标记。随后补车辆 validator 拒绝。 |
| green-003 | 0 | 27/27 | 当时的 9 个领域用例与旧 18 个用例通过。 |
| red-004 | 1 | 14/15 | 业务 RED：kg 已支付 NPC 历史报价未拒绝应急来源。随后补 Fleet 所有订单来源检查。 |
| green-004 | 0 | 33/33 | 15 个领域用例与旧 18 个通过。 |
| behavior-005 | 1 | 34/35 | 新预算用例误将 10/15 分成独立路径并误认招募价；修正为买首车后实际换车再配送的同一路径，生产价格不变。 |
| green-005 | 0 | 35/35 | 同路径预算及正额度拒借通过。 |
| behavior-006 | 0 | **35/35** | 最终代码和测试；加强逐阶段借还拒绝、新未签订单门禁、多 NPC 剩余合同和归还历史伪造拒读。 |

最终用例还覆盖：只读投影不写存档；重复/陈旧/非法序号和普通配车绕过均原子拒绝；正常/可卸/真实赚款可购车状态拒领；planned/travelling/pickup/service/ready 各阶段保存重载与借还拒绝；取回实车后新未签订单从 Game 和 Economy 两入口拒绝；完成/取消借车历史在归还后完整校验；永久资产和成长目标不计借车、NPC 不签新批、借车无可升级实例；无额度即不推进旧批；旧 kg/slots 防新增与预算测试保持。

真实 Game 的 10/15 路径从 100 金币开始，10 笔基础车亲送赚到 300 金币后按生产报价购买车型 1，余额 0；装备新车后再送 5 单共得 120 金币，正常招募 npc-1，余额 0，旧车可分给 NPC。全程无借车记录、无额外消费或 SDK 成功模拟。

**源指纹与写集**

唯一五源修改和新增测试如下，完整审查差分为 `source-changes.diff`，直接比较 PM 的 source-before 副本，未以 git HEAD 代替未提交基线。

| 文件 | 最终 SHA-256 |
| --- | --- |
| `delivery-game/assets/scripts/domain/V2EconomySession.ts` | `75e745549c67d3715ca7852538fb7da3cb46e0fc7161d87988eb940f9ee65fc3` |
| `delivery-game/assets/scripts/domain/V2FleetSession.ts` | `25bb29bbe67739022e1330865bf9c5a06557808c1e65fcc1f7bd4af07facc43e` |
| `delivery-game/assets/scripts/domain/V2DispatchSession.ts` | `77c2faba87e27b86c69bfe5841f015fa6dcc75dcc024e78bfe3a6bf1d5efedd0` |
| `delivery-game/assets/scripts/map-sample/V2GameSession.ts` | `6e8b1a0bcf17cb19d07d97a6257fc0e660744e1a7d8258210a00843935108019` |
| `delivery-game/assets/scripts/map-sample/V2RuntimeController.ts` | `bee518024daa35c2b18dd42d41a491beaf995290f36e90edf28b161c60b9aeb3` |
| `delivery-game/tests/product-regression-1106/emergency-hero-loan.test.cjs` | `2dcc5c5505fb5a5fa87121c87794d195a7a945aee53f5c90a674884e00fba1e7` |

`final-source-sha.json` 将上述 SHA 绑定到最终运行；`verification-index.json` 索引全部原日志与收据。`inputs-after-audit.json` 核对原 764 项输入：758 项一致、A 五源及 PM 的 V2GameUI 一源变化，0 缺失、0 未授权漂移。五源原副本 SHA 与 PM 初始清单、author-source-before 三方相同。旧测试、参数表、地图输入均在未变清单内。

原始两份 docs fixture 不在该 764 项清单中；本线程未写入它们，最终文件 SHA 已另列在 inputs-after-audit.json，供 PM 对其原证据核对，不能把这次最终采样冒充其事前 SHA 证明。未改第一轮 A/B 证据、长期模型或候选。

测试 runner 的领域/Game 依赖编译仅写系统 scratch，每次 finally 精确删除本次 mkdtemp 目录；全部运行收据的 newRunnerScratchRemaining 均为空。冻结旧 reader 的兼容断言仅用已有 TypeScript 在内存转译 source-before，没有运行旧复现模型或写编译目录。

**界限与交回**

本轮完成 Task 1 作者领域范围。完整默认回归、RuntimeController/UI 全量类型检查、Runtime 保存失败/二写者门禁、UI 行为、B 作者独立审查、Creator 构建及部署仍由 PM 负责；35/35 不能替代这些门禁或原 113 项完整回归。

有钱购车拒领用例来自真实赚款，但同时存在可取回车，未独立构造“全部实车仍被旧合同保留且余额充足”的新自然终态；代码中的最低购车价条件已经自审，仍将该独立现金边界列给 B/PM。自动接单通过现有 normalCandidates 与 Economy 共享门禁，经代码核对，本轮没有模拟广告 SDK 成功来启动自动权益。其他自然历史终态可达性、用户真实档、长期二八、在线广告 SDK、整体 98% 与真机性能不作本轮结论。

正式交回五个生产 TS、新领域测试及本 domain/ 写集。保留所有失败与兼容输入说明，之后停止编辑，供 PM 冻结最终输入并串行集成。
