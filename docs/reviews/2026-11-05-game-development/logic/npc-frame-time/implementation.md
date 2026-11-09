# NEXT-A-NPC-FRAME-1106 实施交接

实现者：开发A `thr_j9izunn7qx`；父PM `thr_axf6i4e89t`；环境 `env_e54zrbdgxt`。**三份源码已实际修改，仅完成作者静态核对，未执行测试，待父PM组织复审A；不自判独立PASS，不关闭反馈。** 本批没有构建、部署或操作游戏/存档。

## 1. 精确基线与前后 SHA-256

开工重新读取三源并校验SHA。Game/Route前态与 `performance/light-read-stage/` 同相对路径候选逐字匹配，没有恢复到P0之前的旧源。Dispatch修改前通过 `write_file` 保存了唯一真实文本基线 [dispatch-before.ts.txt](dispatch-before.ts.txt)，其字节与修改前原源一致；先前审批失败没有写入任何源码。

| 文件（均在 delivery-game/assets/scripts/ 下） | 修改前 SHA-256 | 修改后 SHA-256 |
| --- | --- | --- |
| map-sample/V2GameSession.ts | `3d27e36b83e07f7235aa1aa6f51378a4abc3421bfa3003175464eedd34a6baf3` | `90d6e5f4bb9e5322037c483d57dda65fb1c1f1473d4c406c34ef86b144610b16` |
| map-sample/V2RouteSession.ts | `77cac10354e5f457f5553cc0c9b0b091345f583b54c18373aeff8a510a81f184` | `7d4480870bcb128f729a0b6f2a130a590b6b4e45fea7dbc6e08d770e399a72c4` |
| domain/V2DispatchSession.ts | `adbc39af0f133714df647a0e8df78789171efbec94468d227557001ddf422a6a` | `2bb4abc56bd9987729d742844e5916b58c00698ff1eeeca26078d35427fbc00d` |

源改动行数（纯文本差异，不是测试）：Game +13/-8，Route +3/-2，Dispatch +12/-3。本次唯一文档产物为本报告及上述Dispatch基线；未生成第二套重复报告。

## 2. 接口与时序变更

- **Dispatch `:113-130`**：`tick` options新增可选 `deferFleet?:boolean`。未传或为false时仍按旧路径推进Fleet，旧frame/fingerprint/active/auto/高水位逻辑不改；只有Game显式选择延迟。
- **Dispatch `:96`**：新增 `advanceFleetTo(nowSeconds):void`，在原隔离事务中校验有限非负绝对秒、安全整数毫秒，按 `Math.floor(nowSeconds*1000)` 调原Fleet.advanceTo，不新建保存字段。
- **Route `:129,154-158`**：arrival第三参 `elapsedSeconds` 为该次advance实际消耗的现实秒数 `seconds-remaining`，在交付服务完成、令牌加入后回调。包含真实travel fraction和服务秒数；不使用gameSeconds/40，也不从frameEnd倒贴。其余Route逻辑不变。
- **Game `:45-56,62-95`**：调用Dispatch.tick时使用 `{deferAuto:true,deferFleet:true}`，帧前 `before.frame.nowSeconds` 是 `wallStart`。每次Route.advance前捕获此前已消耗补给/路线秒数 `offset=used`，交付时显式传 `eventAt=wallStart+offset+elapsedSeconds`。Game.completeDelivery新增可选时间参数，原两参调用仍使用当前frame高水位。
- **Game `:65-79`**：在自动补给选择/支付、下一批选单/签约等动作前，先把NPC推进到 `actionAt=wallStart+used`，再读取余额并执行动作；不会先拿帧尾NPC收入供帧中购买。补给结束后的offset包含其真实动作耗时。
- **Game `:56-57,95`**：所有正常退出统一finish，先把NPC推进到 `frameEnd=max(wallStart,nowSeconds)`；仅按原used/allowance规则扣实际自动动作秒数。主角idle、pickup/ready等待、无车、零体力阻塞、广告、暂停、后台、恢复首帧或自动权限尾段均不省略NPC尾段。没有把异常路径放入finally补推进；异常交给Runtime丢弃整个候选。

## 3. 每笔交付、归日及作用域

Dispatch.completeDelivery `:97-104` 保留原重复收据提前返回和权威到达校验。对新交付依次：

1. 在Dispatch隔离draft中按eventAt的**绝对floor毫秒**推进旧NPC额度，原Fleet逐笔workAt/nextDue结算照旧；同毫秒原due先于主角结算。
2. 临时使用该事件毫秒写主角账目，结算主角、关已完成批次。原Dispatch.transact末尾仍按hero事件游标同步一次额度并验证；新额度只能供eventAt后续段使用，不回填帧起。
3. 后续到达/经济动作继续按实际offset处理；finish才推进NPC剩余墙钟区间。各段都floor绝对时刻，不把分段秒数各自取整后累计。

Dispatch新增同步作用域 `withLedgerTime<T>(nowSeconds,action):T`（`:44-49`）：从同一个事件毫秒调用现有Runtime注入的本地日期resolver；无resolver写未知dayKey，不推断时区。保存原ledgerContext，使用try/finally在**当前**economy owner恢复它，避免嵌套transact替换economy后恢复到旧实例。

主角结算在Dispatch隔离draft内进入此作用域；Game手动补给 `:37-40` 和自动补给 `:70` 都按实际动作时刻进入作用域，chargeSupply仍走原事务、价格与库存/付费门禁。作用域结束恢复帧上下文，未改Runtime原注入方式。没有新增持久字段/版本，也未迁移历史null日期账目。

## 4. 静态保留检查与失败边界

仅运行了Python字节/SHA/文本差异检查，没有导入或执行TS游戏代码：

- Game完整restore（包括A-QUALITY-01）、serialize及补给入口之前的原接口逐字不变。
- Route逆去本次arrival签名/回调/一行注释后，字节精确恢复修改前SHA；P0 progress/motion/position、merchantKey经营资格与唯一配对、分组/ready、legacy和权威legs全量验证均未改。
- Dispatch完整validate/restore、snapshot/serialize、transact及resolver再注入段逐字不变。把新增deferFleet类型/条件去掉后，tick主体精确等于旧版；默认调用不改变Fleet推进行为。
- Fleet/Trip/Runtime/Economy/Ledger/Reward六份只读依赖的收尾SHA与前态记录一致。Fleet原workAt、同步游标、restore/atomic再注入均保留。UI/ApprovedSkin由开发B并行，本线未写其文件，也不把B的变化归为本线差异。
- Runtime原候选恢复→注入resolver/context→tick/action→完整验证→一次commit→publish不变。新增事件结算、日期resolver调用、NPC推进若抛异常，都发生在未发布Game候选内；本线没有新增storage调用或半帧提交。该结论为源代码边界核对，不是故障注入证明。
- 重复frame仍受原fingerprint门禁和零主角秒约束；重复交付仍先返回原收据，原heroEventCursor负责幂等补额度。倒退帧使用原高水位零主角推进，Fleet既有 `nowMs<=lastAdvancedAt` 不倒走。恢复时不新增补跑或迁移规则。

## 5. 留待阶段集中验证的案例（全部未执行）

1. 固定同一真实交付日程：0→60且主角第10秒完成，对比0→10→60；比较NPC额度/批次/游标、逐笔账目/时间、主角收据和自动剩余，排除额外手动点击/ready操作导致的不同日程。
2. 零额度到eventAt补充：不能在eventAt之前经营；多笔主角完成及跨阶段额度上限仍只按各自真实事件同步一次。
3. 跨本地午夜/月界交付、自动/手动购买补给：主角/补给账目用各自事件floor毫秒与resolver日期，NPC仍逐笔workAt，作用域结束恢复帧context；旧null条目保持。
4. NPC旧due与主角同毫秒：先旧NPC、后主角及额度同步；同毫秒多交付不能重复推进、补额度或回写旧时段。
5. pickup/ready等待、idle、无车、零体力、无可用补给、暂停/后台/广告等待/恢复首帧，以及补给恰好占满帧：主角按原规则冻结/耗时，NPC仍到真实帧尾。
6. 帧中余额不足而帧尾NPC将入账：早发生的自动补给不能借未来钱；下一批合同使用该动作真实时刻之前已发生的状态。
7. 重复frame、冲突fingerprint、倒退时钟及回到原高水位：不重送/重奖/重补，不倒走或重复计算NPC。
8. 自动600秒末段、分数秒/部分体力travel、同帧补给→ready→继续→交付/跨批：只扣实际动作秒数，权限耗尽不把尾段改成人工自动推进，NPC尾段仍完整。
9. resolver抛错/非法日期、结算失败、保存失败：不发布半帧；嵌套作用域与成功交易后context恢复；原合法legacy恢复和非法legs/互斥组合拒绝。

## 6. 限制与租约交还

未运行tests/typecheck/回归/ts-node、TS游戏函数、故障注入、游戏浏览器、Creator构建、真实或合成存档及业务操作；没有commit/push、新Agent或地图任务。编辑工具自动返回既有includes/flatMap库目标相关LSP诊断，per-file tsc明确skipped；未为消除诊断运行编译器、改tsconfig或扩写集。未测量性能/帧率，不宣称功能通过或卡顿清除。

**本批完成交接后停止写入，交还Game/Route/Dispatch写租约；临时Accept Edits仅本批有效，由父PM恢复Mode=default，后续不沿用。复审与必要构建归父PM安排。**
