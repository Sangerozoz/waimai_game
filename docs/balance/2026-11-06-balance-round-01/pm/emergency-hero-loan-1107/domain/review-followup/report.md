本轮仅补后端复审提出的 Important 自动完整路径与 Minor 现金独立门槛覆盖。两份获准测试新增 4 个用例，必要窄测 **32/32、exit 0**：领域 20 项、Runtime 12 项。五个生产源与原冻结 SHA 完全相同，旧证据和原 fixture 保持；交由 B/PM 核销原门禁，本作者不代独立审查裁定集成 PASS。

执行前已核 `backend-review-request.json` 的五源和两测试 SHA，阅读现实现的 RewardSession、Dispatch/Game 自动循环及 Runtime.open/mutate/update。建议对应的是原覆盖缺口，本轮无生产缺陷修复，也没有回退冻结源来制造 RED。测试与收据直接读取当前未提交文件，不以 git HEAD 代替基线。没有执行全量回归、typecheck、构建、部署、UI/浏览器或真实档操作，未改连接、路由或权限。

**Important：真实 Runtime 自动闭环**

新增入口 `delivery-game/tests/product-regression-1106/emergency-loan-runtime.test.cjs:183`。仅 Cocos 生命周期与 storage/writer 是测试端口；真实 RuntimeController 源在内存加载，Game/Route/Reward/RuntimeStore、公开命令、单 slot 保存和 open 均为现实现。

权益输入来源：克隆唯一原 signedZeroQuota 隔离 fixture，经真实公开 `dispatch.requestAd('auto', null, ...)` / `resolveAd(ticket, 'completed', ...)` 生成已完成权益事件，再用 `stopAutomation()` 保留 600 秒已有权益。该事件是明确的隔离测试输入，不是线上 SDK 成功证据；未直接设置 autoRemainingSeconds 或 control，Runtime ads 端口始终在被调用时抛错。

之后全程使用 Runtime.command / resumeAutomation / stopAutomation / update / setPaused / startOrContinue / onDestroy；不通过私有 live 或直接结算驱动配送。自动实际选择并签单、开始行驶后关闭实例，以同一个 memory slot 真正 open 新实例，模拟离线 30 秒。open 保留原路线位置、Trip、批次、所有已签报价、主角完成数和权益剩余量，主角没有离线补跑。实际恢复自动后完成真实配送。

第一单仅补 60 秒；明确暂停主角 60 秒，旧 NPC 批推进至 elapsed120000 / paidCount1、额度 0，实车仍被最后一单保留。恢复自动真实完成第二单后，用正常暂停等待把 NPC 剩余 work 推至释放前 250ms，再恢复行驶。实车释放时 `v2-road-270` / `v2-road-588` 两单批次仍完整存在，其中一单尚 pending；报价逐项不变。该批由自动完整结束，原 batch 两单均 completed，订单总数不增。

保留 auto 控制及余下权益继续 update 30 秒，主角完成数、订单总数和权益均不变，没有自动新批。显式 Runtime 归还后，主角装备 starter-1、NPC 未来配车卸下、账目和余额不变；原有 auto 权益实际签下实车批 `v2-road-43` / `v2-road-81`，并完成一笔真实实车配送。这里同时验证实际动作和公开状态，不止检查 auto 字段。

以下时间为隔离 Runtime 时钟减去 1800000000 秒；原始诊断见 attempt-01.log，按原日志解析的事件见 auto-events.json。

| 原始事件 | 相对秒 | Route | loan | 主角/NPC已完成数 | 当前 batch |
| --- | --- | --- | --- | --- | --- |
| auto-signed-and-moving-before-open | 0.25 | travelling | borrowed | 1 / 0 | v2-road-40 |
| actual-open-preserved-in-flight-auto | 30.25 | travelling | borrowed | 1 / 0 | v2-road-40 |
| first-auto-delivery-refilled-only-sixty-seconds | 36.5 | travelling | borrowed | 2 / 0 | v2-road-270,v2-road-588 |
| old-batch-partially-paid-still-reserved | 96.5 | travelling | borrowed | 2 / 1 | v2-road-270,v2-road-588 |
| real-car-released-during-current-auto-batch | 118.125 | travelling | returnable | 3 / 2 | v2-road-270,v2-road-588 |
| auto-remained-blocked-before-explicit-return | 152.875 | finished | returnable | 4 / 2 | 空 |
| explicit-runtime-return | 152.875 | finished | returned | 4 / 2 | 空 |
| owned-car-auto-batch-started | 153.125 | travelling | returned | 4 / 2 | v2-road-43,v2-road-81 |
| owned-car-auto-delivery-completed | 158.625 | travelling | returned | 5 / 2 | v2-road-43,v2-road-81 |

**Minor：仅现金不同的独立边界**

新增入口 `emergency-hero-loan.test.cjs:124`，三个用例自 `:129` 起。每例均克隆原终态，仅修改现金及维持账本守恒所必需的 opening.balanceCents，并同步重复保存的 Economy 副本。将这两个货币字段归一回原值后，完整 Game 结构必须与原 fixture 深相等；因此未改变车辆占用、未付合同、额度、事件 cursor、主角配车、Route/Trip 或任一其他资格。

这些是合成兼容输入，账本 opening 的差值不是游戏内收入/赠款，也不代表额外自然可达终态。原文件保持只读。

| 现金（分） | 与当前最低购车价30000分关系 | 实际结果 |
| --- | --- | --- |
| 29999 | 不足1分 | available；主动借用成功，现金/账目/车辆数组保持，重载通过。 |
| 30000 | 恰好 | unavailable；以“余额足够购车”原因原子拒领，随后生产 buyVehicle(1) 正常扣30000分、余0。 |
| 30001 | 更高 | 同一现金原因原子拒领，正常购车后余1分。 |

三例均独立验证没有可取回实车、零额度、无主角批次、hero.vehicleId=null、无 Trip 动作。拒领不再被“有闲置实车”等其他条件掩盖。

**原始命令与完整性**

```sh
python3 docs/balance/2026-11-06-balance-round-01/pm/emergency-hero-loan-1107/domain/review-followup/run-check.py attempt-01 product-regression-1106/emergency-hero-loan.test.cjs product-regression-1106/emergency-loan-runtime.test.cjs
```

实际下发 Node 命令保存在 attempt-01.json。唯一测试运行从 2026-11-07T04:16:22.583197+00:00 至 04:16:37.083332+00:00，exit0、32 pass / 0 fail。没有覆盖原 behavior-006 或 runtime-integration-07，也没有重跑整批。run-v2 只在系统 scratch 编译所需依赖并 finally 精确删除本次目录，newRunnerScratchRemaining=[]；RuntimeController 的测试转译只在内存。

一次只读发现命令因 zsh 未匹配 *auto* glob 而 exit1，原命令和错误保留于 discovery-command-failure-01.json；随后改用明确存在的只读路径，没有运行失败的测试或权限/原生连接变更。

两份测试最终 SHA：

- emergency-hero-loan.test.cjs：`45d4723fe90f0cf4ae809c11b9da79612ba5c0011feffdfddd63a872f7a41a99`
- emergency-loan-runtime.test.cjs：`47221c855c390760a03d8e325c7d85d55310fbee825f8e19de3af3d9eaffe039`

五源全部沿用 backend-review-request 的 SHA，见 final-source-sha.json。每次运行前后记录五源与两测试指纹，7 项运行中稳定；另核共 35 项旧文件（原 domain 证据、runtime-integration-07 原日志/收据及两个原 fixture），0 变化。test-changes.diff 只比较执行前测试副本与当前测试，旧日志/旧基准未改写。

本轮只交回两测试和本 review-followup/ 新证据。原自然终态仍只有 signedZeroQuota；现金边界与权益事件的合成属性明示。线上广告 SDK、浏览器表现、完整回归与部署均不作本轮新增结论。完成后停止编辑，等待具体复审反馈。
