# 待阶段集中验证用例（全部未执行）

前置：用户明确“阶段完成”并由PM授权。下列仅是未来用例，不在本线程创建/运行测试、故障注入或真实/合成存档。

## 日历与历史边界

- 单日本地时间：已有配车NPC和真实既有额度；每条新增npc_delivery的atMs仍等于原workAt，dayKey等于Runtime.dayKey(atMs)，今日/近七日计入该条，不改金额。
- 跨午夜：一次推进中让已有合同在本地D日23:59:59、D+1日00:00:00及之后分别到期。逐笔按各自workAt归D或D+1，不能统一归frameEnd日；同刻多NPC均用同日键。
- 离线跨日恢复：Runtime首次open在tick前重注入；只有额度允许的真实workAt有结算，恢复当天不获得全部历史钱，闲置/额度耗尽尾段仍无补收益。
- 月末/年末/有效闰日，以及支持夏令时的宿主时区：复用宿主本地年月日，与ledgerQuery使用同一口径，不假定一天恒定毫秒数或固定UTC偏移。
- 历史null记录：恢复后既有entry的id、amountCents、atMs、dayKey保持原值；unknownDate仍包含这些记录，累计/余额不因归日修复重记；仅后来新增条目有新日键。

## 非持久回调生命周期

- 独立新建Fleet/Dispatch未注入resolver：仍记录正确workAt且dayKey:null；即使外层ledgerContext有今天日键也不盗用。
- JSON恢复：Fleet Object.create路径明确置null，Dispatch新实例也为null；旧回调不进任何序列化载荷、不读回快照中的伪造callback字段。可信宿主显式重绑后新结算正常归日。
- Fleet.atomic连续调用：注入后先syncHeroCompletions/completeHeroDelivery，再多次advanceTo；嵌套草稿不会丢resolver。不得重放游标或补两次额度。
- Dispatch.transact连续调用：注入后经合法command/acceptBatch/tick等原事务，Fleet替换后再次tick仍持有同一策略；setter(null)后立即及后续事务均回到null，不残留旧回调。
- Runtime每次从committed恢复的候选、只读quoteCandidates草稿均在action前接线；报价不发布、不commit、不影响真实合同。

## 原子性、幂等与范围隔离

- resolver抛错、返回非法日期字符串：原实例的现金、账本、quota、nextBatchId、合同、lastAdvancedAt、heroEventCursor不应部分提交；没有吞错贴今天。验证失败后再次合法推进只入账一次。
- 同一帧/同一时间重复调用及时间倒退：不重复结算、不倒走高水位；同一可信resolver下，**没有新增主角补额度事件**的相同Fleet区间分段/整段推进应逐笔日期一致。此用例不代表Game帧内补额度缺口已修复。
- 保存失败或expected/epoch/写者失效：候选不得替换Runtime.live/committed；已有单slot不被本修复清理或新增备份。由授权存储测试确认具体失败边界，不能用源码顺序代替运行结果。
- 帧内NPC推进后接其他主角/购买账目：Fleet成功返回后还原原ledgerContext，不能把最后一条NPC的workAt/dayKey泄漏给外层动作；原合同金额/逐单幂等不变。
- 继续配送、前后台、广告暂停、30Hz合并门禁及已提交缓存仍按原路径；不借归日改Game/Route/Trip规则。

## 集中测试准备提示（本次未改测试）

只读发现`/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/tests/v2-trip-ui.test.cjs:23,67`的Runtime替身dispatch仅提供setLedgerContext，未来需同步新增setLedgerDayKeyResolver测试端口，并核对原夹具的committed前置。不得为了迁就替身而把产品Runtime的新setter改成可选调用或跳过日键接线。

现有Fleet/Dispatch测试尚未覆盖本次resolver生命周期；待授权后由PM安排测试owner增补。本清单不是测试结果，不关闭用户反馈或宣称98%。
