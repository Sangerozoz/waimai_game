# COMPACT-HANDOFF 独立核心核验（最终核心指纹收口）

日期：2026-10-30。当前结论：16组checkpoint核心核验保持有效；唯一变动的CountySaveStore定向续验2组通过。最终manifest与本次核心输入相符，P1关闭。本结论仅覆盖核心，不代言UI或用户体验验收。

## 执行

- 亲跑命令：`node docs/reviews/m1-compact-handoff/fresh-core-audit.cjs > docs/reviews/m1-compact-handoff/fresh-core-audit.log 2>&1`。
- 修复后原15组退出0；补核旧活动取消后最终退出码0，约0.21秒；输出 `RESULT 16 passed, 0 failed []`。
- 自写断言，transpileModule加载本轮当前/before真实核心模块；未执行开发tests、全npm test、UI或构建。
- 81节点、200米间隔直线小图，双向/单向代表反例；全部新建内存对象。未访问4181、任何浏览器页、用户存档或Storage。
- 写入仅fresh-core-audit.cjs/.log/.md。未改生产或开发测试，没有派子代理。

## P1历史与关闭证据

[P1，当前checkpoint已关闭] 初次核验发现：单行途中取消后刷新生成候选仍忽略真实origin。

1. 合成图road r为单向0→1→…→80，随机种子19；接CC-2（商家node4）。
2. depart→advance(.05)→cancel；停靠锚点为 `{road:r,from:0,to:1,fraction:0.15000000000000002}`。
3. refreshFree生成CC-14（from0,to23）；其真实normalRoute为null。此点不能逆单行返回商家0，故该新单不能合法接取。
4. 当时list已正确将不可达旧池候选标available=false且不整体抛错；当时问题存在于新刷新生成，不能把它当旧池保留的合理禁用。
5. 对应runner用例 `one-way refresh generation includes true origin, so every emitted offer is genuinely legal`；已把具体步骤发PM，未直接修生产。

修复后：同一输入刷新得到CC-14 from4→26，全部10个新候选都可从anchor合法出发，available=true、真实总距离与preview相同；可载重候选accept后期限与preview一致且起点无跳变。旧失败OrderBook SHA为 `1eec02f39a5612dde4ec9edd871b35b921cf9b411c64b4dead0952797a000a44`；当前SHA见下。

## 已通过范围

- 大dt分别截断到awaitPickup、awaitDeliveryStart；必须手动pickup/deliver，不越过人工边界；重复depart不重抽结果，非法pickup/deliver与取餐后cancel拒绝；完成重复settle不重复奖励。
- 服务0/1秒可恢复，2秒到awaitDeliveryStart；零取餐距离仍待确认，等待与服务不增加实际displaySeconds或晚到惩罚。
- schema4阶段/版本/mode/elapsed/服务时间/damage/receipt/坏anchor各类篡改拒绝，合法中途和完成快照恢复。
- planning/toPickup/awaitPickup取消保持钱包、账单、原10候选内容/ID/顺序、刷新额度与RNG；真实位置以1e-8容差保留及恢复。
- 下一单从真实anchor出发，origin剩余metres/seconds纳入路线总计；正向与反向prefix行至一半再次取消，真实位置连续，无新增虚拟node。
- 搬至node36后旧池某单10600米，list保持原ID且禁用超限单；单行旧池不可达候选不导致整体大厅失败。
- anchor校验拒绝逆单行、不相邻road、缺失road及非法fraction；真实单行点仅前向出口，不能找回node0的路线。
- before生产模块真实生成schema3 idle/routes/running/arrived/done：经济、期限、回执、候选和保存状态保持；原活动无handoff，继续自动配送；旧done门口false保留。
- ZIP真实v2十态fixture：相对本轮before恢复结果，玩家/姿态/时钟/回执保持，running不增加手动边界；构造v1三十候选经真实before校验的迁移与当前结果相同。
- 补核实际before v3及真实v2 running/paused旧活动：取餐前cancel保持精确点、钱包/账单/候选/额度与RNG；升级为schema4 anchor保存可恢复，再接可用新单仍从原点出发。v2示例反向r:23→22 fraction=.7352941176470589。
- 未来primary version5/99：CountySaveStore禁止保存，原字节不变，0次setItem。
- 72组评价20/80/100 × 四档餐损 × 准时/晚到 × 无需求/door false/door true：当前settlement完整结果与before相同；I0−lateImpact−damageImpact=真实整数分收入；报价及分解不变更输入，MAX钱包不溢出、不创建真实新钱包。

## 边界与SHA

- 最终清单SHA：`4c25a6f804928307a9c1f76afe609d57225d0f502f171547d6b1fd800d43342a`；核对本次运行时加载的15个当前模块，8项列于manifest且全部匹配，14项相对16组checkpoint未变。MapTypes为类型擦除文件，单独仅核当前与manifest一致。
- 日志SOURCE_SHA256记录本次加载当前/before模块。关键当前输入：
- `OrderBook.ts`：`f3b08c1cd876361eef71009b3a316fac55d6ec7711c95d0542de82bf02e816b2`
- `ManualHandoff.ts`：`2f6c02332fb52fe8e3c75cfaf260149ce93a6d5cf1d4532f9c72145ee3d31a95`
- `RiderAnchor.ts`：`08205207aa146b0d2d2bf5784e20ef8a559f574180a8f00c3756e5087fd16d65`
- `CountySnapshot.ts`：`23971114c1c0790d11e7c3ceb5faa8385a30757441fdf90585c8171c8c8c279f`
- `CountyRules.ts`：`6bf9548f2e733c82ef799da0e50a6be17d2abd5d04cca4a0ac73c23f5a63ec13`
- `CountySaveStore.ts`：`f6edf05a4125dc87586c228813320aada6b0432aadcd37f2aa2da2017d796d11`
- schema1为构造的合法历史形状，并非当年原始实存；v2使用真实baseline fixture；v3实际由本轮before模块生成。
- 旧arrived在纯OrderBook.restore仍保留arrived，未在本任务声称自动结算；UI启动/入口按true继续的真实触达由固定测试专责。
- 未测真实大图候选排序/时限的全量分布、手工事件主动呈现、保存失败UI提交栅栏、真机帧率或用户触感；本轮小图刷新已发现并复验origin遗漏修复，不重复批量大图寻路。
- 前一轮两项脚本误报已修：完成助手起点固定假设、端点1e-13浮点严格相等；均仅改审核runner，初次唯一产品失败为上述真实反例，现已保留断言并通过。

## 最终变动续验

- 仅CountySaveStore相对checkpoint变化：新增未来备份保护；其余核心字节相同，未重复原16整套。亲跑 `node docs/reviews/m1-compact-handoff/fresh-core-audit.cjs 'future '`，退出0，约0.24秒，2/2通过；追加日志保留原16/16记录。
- 续验primary version5/99原字节与0写保护，以及backup version5/99在primary缺失/损坏四种组合的保护；保存返回false，primary/backup原字节保持，仅允许保留损坏primary副本。
- 本次加载但未列于最终manifest的原有依赖：`delivery-game/assets/scripts/map-sample/DeliveryClock.ts`, `delivery-game/assets/scripts/domain/GameConfig.ts`, `delivery-game/assets/scripts/map-sample/CountyConfig.ts`, `delivery-game/assets/scripts/map-sample/DeliveryLedger.ts`, `delivery-game/assets/scripts/map-sample/CityExtent.ts`, `delivery-game/assets/scripts/map-sample/FoodCatalog.ts`, `delivery-game/assets/scripts/map-sample/OrderPresentation.ts`；各自相对checkpoint字节未变，SHA详见日志FINAL_FINGERPRINT。
- 核验没有读取UI状态、图或引擎构建结果；MapSample最后提示键/回执高度变化不在本核心结论内。未来若manifest/核心再变，须按记录续核。
