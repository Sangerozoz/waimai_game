# 测试A：当前V2纯逻辑/数值/存储隔离回归

**最终实际结果：exit 0；TAP 95项、通过95、失败0、跳过0。** 包含ES2020 strict/noEmitOnError编译。不是静态绿、完整产品PASS、95个独立业务路径或98%视觉验收；TAP含父/子测试，不累加历次重跑总数。

- 权限：写前实际执行`bb thread options --self --json`，`_bb/legacy-mode.value=accept_edits`且`pendingValue=null`；未改权限配置。
- 仅生产修改：`V2EconomySession.ts:106` 增加`check(int(s.selectedMapId,1,5));`，没有`as number`、删门禁、改公式或扩写其他生产源。
- 前SHA：`6465c5580a3a0568ed28e0a6227c2c3b1db2f945625baebdacd299a69d615d37`；后SHA：`90b331aea0ecfb05cef239b09b08affc97402336273611eedafd96497fa694a8`。文本逆去这一行精确恢复前SHA。
- [机器结果与全部文件前后SHA](test-results.json)；[精确源码/测试diff](source-and-test.diff)；[最终完整输出](v2-suite-final-complete.log)。

## 根因和先失败后修

原生raw state是`Record<string,unknown>`；校验ownedMapIds每个元素是整数，不会把另一属性selectedMapId收窄成number。新增编译/校验回归先RED（exit1，原TS2345）；再加明确1..5整数检查，原owned成员/去重校验仍在。相同回归随后GREEN（exit0，合法初始/已购地图与未知/非整数/越界/未购地图，kg及slots两分支共5项）。新slots公共投影仍复用完整legacy门禁，没有另开宽松验证。原membership已间接排除非法成员，本次不伪称发现了“非法地图可购买”的运行漏洞。

PM原始失败日志[保持原样](../v2-suite-initial.log)，本线的[selected-map-red](selected-map-red.log)和首轮[V2旧套件50/60](v2-suite-before-fixture-update.log)也全部保留。新增大容量fixture第一次失败保留于[v2-suite-final-expanded.log](v2-suite-final-expanded.log)：10格车不保证容纳9个混合占格订单；改为从真实候选挑单格单，**未删`>8`断言、未改容量/自动策略**。最终实测fixture为10格、20候选、10个单格候选、承接10单。

## 实际命令与独立退出状态

所有下列命令cwd均为`delivery-game`，TMPDIR固定`/Users/sanger/.hermes/cache/scratch`。精确命令、每次完整TAP计数与日志SHA见JSON；临时编译输出由runner finally清理。

| 阶段 | exit | pass/tests | 真实输出 |
| --- | ---: | ---: | --- |
| selected-map-red | 1 | 0/1 | [selected-map-red.log](selected-map-red.log) |
| selected-map-green | 0 | 5/5 | [selected-map-green.log](selected-map-green.log) |
| v2-suite-before-fixture-update | 1 | 50/60 | [v2-suite-before-fixture-update.log](v2-suite-before-fixture-update.log) |
| v2-suite-fixtures-aligned | 0 | 69/69 | [v2-suite-fixtures-aligned.log](v2-suite-fixtures-aligned.log) |
| current-contract-first | 0 | 13/13 | [current-contract-first.log](current-contract-first.log) |
| current-contract-expanded | 0 | 17/17 | [current-contract-expanded.log](current-contract-expanded.log) |
| current-contract-complete | 0 | 21/21 | [current-contract-complete.log](current-contract-complete.log) |
| v2-suite-final | 0 | 90/90 | [v2-suite-final.log](v2-suite-final.log) |
| v2-suite-final-expanded | 1 | 93/94 | [v2-suite-final-expanded.log](v2-suite-final-expanded.log) |
| v2-suite-final-verified | 0 | 94/94 | [v2-suite-final-verified.log](v2-suite-final-verified.log) |
| v2-suite-final-complete | 0 | 95/95 | [v2-suite-final-complete.log](v2-suite-final-complete.log) |

最终默认执行11份测试文件。新增`product-regression-1106/current-contract.test.cjs`含26个顶层契约case；selectedMap回归另有父/子计数。没有用后续成功掩盖初次失败。

## 旧断言/fixture纠正，不回退产品规则

- `tests/v2-county-adapter.test.cjs`：旧OrderBook迁移成功并继续旧服务 → **退休迁移入口必须拒绝；原输入/旧Book不变，不创造V2钱包或旧资产**。依据：`docs/product/implementation-baseline.md:50-52`；`delivery-game/assets/scripts/domain/V2EconomySession.ts:96,131-132`。另用合法Game1空闲/真实Game4-Route2 kg在途fixture验证当前V2支持的兼容，不把退休游戏迁移与当前V2旧合同混淆。
- `tests/v2-economy.test.cjs`：第一次随意招npc-30仍按120金币的招募顺位价；npc-25=400000、旧培养满级4800 → **固定身份报价；推荐首NPC使用npc-1；legacy kg冻结表为npc-25=880000、满级1600；新slots全部30级另与11-06冻结JSON逐值校对**。依据：`delivery-game/assets/scripts/domain/V2RiderEconomy.ts:8-25`；`delivery-game/assets/scripts/domain/V2EconomyConfig.ts:257-259,754-755`；`docs/product/implementation-baseline.md:9,50`。失败不推进招募/不扣款、自由购买与去重仍执行；另有当前slots不加奖励的真实10/15单领域预算测试。
- `tests/v2-ledger-targets.test.cjs`：缺ledger时自动制造迁移期初余额 → **缺失ledger拒绝，合法空账本正对照保留**。依据：`docs/product/implementation-baseline.md:50-52`；`delivery-game/assets/scripts/domain/V2EconomySession.ts:130-132`。日期未知/分类记账/对账/重复消费/目标只读全部保留。
- `tests/v2-route.test.cjs`：取餐2秒结束立即开走并完成；新生产候选检查weightKg；任意自动帧都必须finished → **取完停ready，显式continue后续送；候选为1/2整数slots且同店只一次服务；自动可已在下一批中途**。依据：`docs/product/2026-11-02-delivery-game-product-v1.md:55-61`；`docs/product/2026-11-06-capacity-slots-upgrade-revision.md:14-19`；`delivery-game/assets/scripts/map-sample/V2GameSession.ts:90-136`。到达凭证、真实沿路、恢复、原位取消/不可达、自动完成数增长及权限制动仍执行；新增不同店不合并和600秒末段测试。
- `tests/v2-trip-rules.test.cjs`：公共restore后第一帧就补跑供给；把Game6改根版本1即视作合法旧档 → **恢复首帧只rebase，后帧实际推进；错配版本拒绝，另构造真实Route1/Dispatch1的Game1合法正对照**。依据：`docs/product/2026-11-02-delivery-game-product-v1.md:61,169`；`delivery-game/assets/scripts/map-sample/V2GameSession.ts:138-172`。零体力、费用/库存、动作状态、非法旧在途和未来版本仍执行。
- `tests/run-v2.cjs`：独立测试引用V2ProgressTargets却未把其列为编译根，导致MODULE_NOT_FOUND整文件失败 → **增加ProgressTargets与新Store回归所需RuntimeStore编译根，保留ES2020/strict/noEmitOnError原选项；自动收集本批独立回归并允许白名单聚焦运行**。依据：`delivery-game/tests/v2-ledger-targets.test.cjs:7`；`delivery-game/tests/run-v2.cjs:9-20`。没有排除默认旧测试或跳过失败case，不改项目tsconfig。

## 已实际覆盖

- selectedMapId: kg/slots两类合法初始及已购选图；undefined/null/bool/string/object/array/NaN/Infinity/负数/0/小数/越界/未购ID拒绝。
- 当前slots真实20/24金币保护预算：第10单购买首车、第15单招npc-1且旧车复用，无任务返利；完整30级/10车型/30骑手及地图表与冻结JSON/SHA一致，升级费按批准累计表正整数作差。
- ready/continue等待不补跑，同店组取餐2秒只扣一次，异店分组；原位取消与恢复权威腿/到达token；容量超载/伪造load/kg混入原子拒绝，有限稳定池实际返回20个候选并合法承接10个单格订单。
- U22: current Game草稿与正式同源可信heldMetres；14/15完成数边界；旧kg跨ordinal批整批保护、4005/4004单次取整对照；null/缺漏/额外/继承/__proto__输入和历史completed/cancelled metadata篡改拒绝。
- 旧kg在途保持报价/期限/draw/单位，下一批才slots/food3；kg及slots占车恢复拒绝hero/其他NPC复用，同时保留原骑手未来null/空闲车合法路径；slots已签NPC合同不因升级热换效果/费用。
- NPC zero quota粗帧0->60且第10秒完成对比0->10->60；重复/倒退不重补；主角/供给事件毫秒与固定UTC+8日键、NPC逐笔workAt跨午夜、同毫秒NPC旧due先于主角；主角暂停/后台/恢复边缘不冻NPC。
- planned补给真实耗时/收费而不走行程钟；活动供给仍耗游戏钟；食品3分类不新增draw且保留旧normal协议；快照/轻量tick/效果嵌套capacity修改隔离；自动600秒只扣实用时长，NPC推进至真实帧尾。
- 唯一slot内存adapter：已有档禁止new覆盖，坏档/未来版本保留不fresh，writer获取失败/epoch变化/外部字节变更/写前quota错误冻结；RewardSession既有10个回调/授权/过期/失败/去重测试实际运行。

## 边界与真实未覆盖

- 这是真实的纯V2 ES2020严格编译和Node领域/内存存储单元集成测试，不是静态GREEN。使用固定scratch临时编译输出，运行结束清理；不启动Cocos或浏览器，不接触真实用户slot。
- 运行了真实Game/Route/Trip/Dispatch/Fleet/Economy等领域函数。部分资金/时钟/兼容fixture由内存构造并经真实restore校验；fixture不得冒充正常玩家路径、真实地图供给或历史用户数据。
- 日期测试显式注入UTC+8本地日resolver；未覆盖任意时区/DST及物理设备系统日历。
- RewardSession的verified-token/arrival port和writer使用明确测试端口；没有真实广告SDK成功、浏览器Web Locks多标签、Cocos Runtime/发布链或网络失败端到端证据。
- Store失败case仅证明写前抛错adapter保留旧字节并冻结；不证明任意存储已写后再抛错可回滚物理字节，也不冒称直接执行了Cocos Runtime.commit->publish分支。
- 旧库存奖励case使用测试进程内目录替身并恢复；出厂空奖励表未改，真实任务领奖链仍不因此完成。
- 未跑tests/v2-trip-ui.test.cjs这份Cocos mock专项、全项目typecheck、Creator构建或浏览器；全项目lib/嵌套工程/MapSample问题由PM独占处理，B负责页面验证。
- 未覆盖真实CityData长期供给、五图、生产蓝框/素材、真实用户完整配送操作、FPS/卡顿profile、全30级实际经营平衡或98%视觉/用户验收。
- 没有commit/push、部署、新Agent、Codex/provider/权限配置修改。测试通过不自动关闭U01/U02或38条反馈；交回后停止本批写入，由PM恢复Default。

**仅本批：源码与测试已交回后停止写入，交还租约；由父PM恢复Default、处理全项目编译配置/MapSample和必要构建。线上包没有因这次测试自动更新。**
