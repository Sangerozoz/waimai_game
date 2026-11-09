# Codex产品PM接续：2026-11-07

## 0. 用户最新决定与强约束

用户明确：“现在在codex里面接入了模型，我们不使用hermes了；切换过去继续任务，保持进度要求不丢失”；指定 **6.1-sol（Sanger）、max**。已从真实模型目录核对：BB Provider=`codex`，模型精确ID=`ccs-sanger/gpt-6.1-sol`，reasoning=`max`。不要误选无Sanger的`gpt-6.1-sol`，不要用旧`acp-hermes-agent`/`openai-api:`前缀，不用GPT-6-astra及其变体。此条覆盖旧AGENTS/baseline里“仅Hermes、禁Codex”的产品线路由；不改账号、凭据、全局Provider或独立地图会话。

同checkout：`/Users/sanger/Documents/ChatGPT/taptap 2`；project=`proj_3sznws2gfk`；environment=`env_e54zrbdgxt`；host=`host_tr578kqahd`；branch=`codex/food-delivery`。禁止fork长历史/另建worktree/重建项目/清理dirty或untracked。已有大量地图/旧工程等他人改动，只保留；迁移不commit/push/删文件/动用户存档。

旧PM=`thr_axf6i4e89t`，旧开发A=`thr_j9izunn7qx`、B=`thr_tviezvnwds`，旧复审A/B=`thr_wy4wnu5fyr`/`thr_htnxptrv4w`，均是Hermes会话，只保留历史，不再续派。四会话已停并读回idle、parent通知off、agent队列已留档后清除；见old-workers-stopped.json、old-thread-queues.json。用户消息不删除、不归档整个会话。

## 1. 必须保留的目标和依据

- 本线负责产品、逻辑、规则、功能、数值、UI和非地图产品素材；**地图制作完全独立，无交叉派工**。不做地图素材/边界/拼接/路网生产，不加工地图插图做车场景，不找地图会话承担产品开发。不以地图未齐停止已明确产品工作。
- 原始认可8张效果图：`docs/art/2026-11-02-approved-ui-reference/`，用图本身＋后续明确改动指导实施；目标98%，但没有实际全页证据不得报达到。不要用整页原图充游戏，不把图片文件/静态PASS/构建当用户验收。
- 固定长期入口：`docs/product/implementation-baseline.md` 顶部最新覆盖；正式V1 `docs/product/2026-11-02-delivery-game-product-v1.md` 未被覆盖章节有效；新容量/费用见`docs/product/2026-11-06-capacity-slots-upgrade-revision.md`。
- 现数值是整数slots：初始2格，餐占1或2格；新表 `docs/balance/2026-11-06-capacity-slots-economy/parameters.json` 对应 `V2SlotEconomyConfig/Profiles`。完整30级/10车型/30人物测试过同源，不把旧kg/旧1600/1.5P当新规则。
- 唯一当前存档，**不允许玩家重开**；不清等级资产金币，不追溯重价旧已签合同。旧kg合同保留原表示/价格/效果，到批准的新接单边界才启用slots/食品新规则。坏档/未来版本拒绝且不覆盖；不建第二slot/备份。
- 买人物/车/地图钱够即可，不恢复等级/地图资格锁。地图卡显示“未解锁”只是文案，不加新购买前置。
- 主角靠亲送经验；NPC培养/车辆实例各自升级，一车一人且旧签约车辆不能借给其他演员。NPC在线/离线同有限额度、亲送实际完成补一次，不循环刷额度。
- 配送按正式V1第4节：沿路自动移动→到店主动取餐→同店一次服务→原地ready→主动继续→到顾客自动逐单交付；40游戏秒/现实秒、取2秒/60、送1秒/30。当前ready、合并、NPC帧内时点已经写好，不要照旧remaining重做。
- 专送为实际进大厅80%出现1候选、100～150且广告独占；600秒自动是可选权益。真实SDK未接入，不假成功，不据纯逻辑称线上可用。
- 用户最新“继续并测试一下”已授权**本批产品定向测试**：允许真实纯逻辑/数值/内存fixture、typecheck、独立headless真实UI操作；不读取/改写真实用户浏览器进度，不做地图阶段测试，不假存档/假广告来充真实流程。
- 用户允许PM管理常规权限，临时编辑能力只给实际开发A/B具体批次和写集，交回收回；审查只读。旧Hermes的`_bb/legacy-mode`选项不能机械搬到Codex，按Codex实际权限接口核对。不能full全局放开绕审批。

## 2. 反馈清单与已经实施的UI

唯一清单：`docs/reviews/2026-11-05-game-development/feedback-ledger.{json,md}`，当前40条；保留稳定ID/原话/证据。部分状态文本陈旧，应依据下列新证据校正，不重置全部任务，也不把单个测试PASS平均成全产品完成。

已写并有隔离画面：主角名称/小等级靠姓名、肖像下未招募、收益/取送省时统一、招募金额外置、四页大标题删除、首页NPC摘要替数量条、右上补给图标、固定首车→首NPC→首张付费图的半透明提示（无换任务）、列表保位、禁重开、×光学修正、订单pin删除/重量或占格随餐名/币图改符号、地图状态文案、账单币图删除，车辆独立原生场景与车型联动。用最新源和B截图核对，不套旧静态稿等待状态。

**仍held：万元近似取整规则**。用户举39,140→4万、42,170→4.5万、3,080,000→308万，仅表示层不改实际扣款。例子不等于统一普通四舍五入；近似需约/确认真实扣款。骑手旧静态稿 `.../rider-proposal-01/` 保留但后续已落实的排版不再整套held。

## 3. 已实际测试、不可抹掉的成果

根入口 `docs/reviews/2026-11-06-product-testing/`：
- A最终纯V2严格编译＋Node TAP **95/95，失败0、跳过0、exit0**，`a/test-results.json`、`a/report.md`、`a/v2-suite-final-complete.log`。PM读回原始日志SHA、核心/参数输入无漂移。含父/子计数，不是95条完整玩家路径。
- PM全产品typecheck **exit0**：`typecheck-post-ui-fix.log`。初始122条失败/只剩1条/最终通过全部历史保留。
- 资源适配13/13、内存存储适配15/15通过。mock/内存不是实际Cocos/远程/用户存档证据。
- A生产只加EconomySession selectedMapId范围守卫，SHA=`90b331aea0ecfb05cef239b09b08affc97402336273611eedafd96497fa694a8`；旧测试按当前规则纠正，不回退slots/ready/禁止旧游戏迁移等。精确diff已归档。

## 4. 最近真实阻塞与修复包（首要集成）

B在4198自己的全新headless，通过真实UI接单 `v2-road-268`。2格load/2格capacity条款都正常，但旧包把`[...batchLoads.values()]`编成`[].concat(iterator)`，planned页抛“配送容量单位或条款无效”，只剩HUD。**不是容量数据错误，不要删严格校验/改价格假修。**

PM只改 `V2GameUI.ts:700` 为 `loadSummary(Array.from(batchLoads.values()),capacity)`。
- 源SHA=`dd0054b6f15f1bca07c886217a8197796138a951223fb8bde935a23717bbe3c2`。
- 逆替换精确还原前SHA=`cea071606d173007ca8ce8acde05c74748e3243d2c4091390aedcdfcef550ed9`。
- Cocos真实构建 `delivery-game/build/v2-loadmap-fix-1106`，Finished/exit36；保留SIGTERM、版本诊断，不声称整个环境健康。
- `index.html` SHA=`0b6a467549a2717bb49a0644ecb96c9db44b2e2e6d2ca0590ffccfcc8f165927`。
- `assets/main/index.ab2ce.js` SHA=`fbd0ca86721c9f67e50a94be4c6b3c5db3cf1f26f8f27ded8db9415ab2166a4d`。
- 实际构建表达式回归：旧RED 4例3fail→新GREEN4/4，含slots单/多、历史kg、混单位拒绝；`batch-load-{red,green}.log`。
- 独立复审B窄修复PASS，PM重新核SHA：`planned-iterator-quality-dd0054.json`。只通过这个修复，不关U01/98%。

**B旧根report/test-results标题仍是RED检查点，不代表后续没做。** 必须读`b/20`到`b/41`真实文件：
- B20新JS执行路径/hash正确；原origin/原planned单正常续。
- B22真实路线/出发入口已显示。
- B25～31全真实UI：travelling→pickup停→手点取餐service→ready原地等→手点去配送→travelling→service→finished；100→120金币、已送0→1、batch清空，follow全程true。
- B29 ready位置与行程钟不变，122,982ms观察等待不是常规玩家操作输入。
- B36非零进度自然reload/继续：120金币、已送1、finished位置与follow保持。
- B38/39真实水补给：120→119；B40账单显示本单收入/补给；B41最后观测finished、119、已送1。
- `b/motion-analysis.json`及B32 raw记录：100ms投影采样、active窗rAF p95约16.7ms；不是每GPU帧/真机FPS/全部性能PASS。
- `b/browser-close-receipt.json`已核对该测试浏览器closed，用户桌面/tab/profile未动。**不要尝试继续已经关闭的旧session，不注入其存档重建假连续性。**
- 原RED、恢复RED、所有截图/trace保留。新B先整理这些已有证据成为最终report，不重做已通过整单；若需新增测试须新隔离上下文并标明。

服务最后核对：正式试玩4182/4196仍指向旧`build/v2-tick-follow-1106`，新修复只在内部4198。旧BB终端ID和当前进程可能在daemon重启后变动，现场核对。下一步应收尾B证据/门禁，再由新PM统一更新原试玩端口至已测修复包，读回HTTP/实际包身份；不改真实用户存档、不把已测候选说成已上线。相关收据`planned-iterator-fix-receipt.json`。

## 5. 数值平衡当前真正进度（正在接续的主任务）

`docs/balance/2026-11-06-balance-round-01/`已存在README和PM成果：
- `pm/audit-current.cjs`已真实临时严格编译调用生产领域函数，输出`current-probe-results.json`、`marginal-growth.csv`、`audit-current.log`、`report.md`。
- 已完成14→15单保护边界，旧车354m敏感性输入20→19.27，100m→18.75、500m→19.57；2km/4km同22.66。公式正确但有保护退出降价/单位收益体验风险，不是真实供给分布。
- 319个车型升级过渡，231不加格，但0个容量/速度/收益三项全不增；不能把不加格判成完全无价值。初始车1→2费20、收益+4%、速度+3%；到10级累计805/6格，NPC10级累计1015，来自新表与域函数/测试，不是长期回本实测。
- `pm/candidate-curves.json`仅敏感性对照：A base10000/slope1、B base9800/slope1、C base10000/slope0.5，D cap2000/分母10000；保护内不动。354m各21.33/20.92/20.96；C长端22.66不升原上限。**都未批准，不是生产参数，不能直接上线。**
- **旧A尚未产出`a/`模型/结果目录**：迁移前实际查不存在；旧A最新也回default未写。不要说这份20/60分钟模型已完成或成果丢失；已完成的是PM报价/成长探针。

新开发A接着真正实现并运行：从合法新档100/2格出发，不用richGame/改余额/赠品，当前真实Game/报价/扣费/Fleet规则，前20/60分钟至少4种投资策略（小队优先/旧车升级优先/容量车优先/先NPC与唯一旧车分配），常规/慢操作明确假设。保留推荐10单首车/15单首NPC预算；20分钟3NPC、二八要重算，不沿用旧19.91/27.41。记录毛/净、单量/分钟、支出、配车/额度/停工、实际容量可用。查保护降价、长短单每分钟、升级vs扩队回本、先NPC借唯一车导致额度耗尽占车软锁等，必须给合法路径实际结果，不脑推。只读现有游戏路由/数据作为运行依赖，不做任何地图生产/边界工作。

模型/候选只写`a/`，生产JSON/TS、旧合同/用户进度不改。最多先3个最小调整，要同路径前后对照和兼容设计，禁止补贴/恢复资格/抬收藏尾价凑目标。旧队列提示在old-thread-queues.json，PM已保存后删除，必须接到新A任务里。

## 6. 新Codex角色的交接纪律

新PM保持同checkout，先对照protected-artifacts.json核核心代码/参数/测试/原图指纹，读本文件、baseline顶部、feedback-ledger及所需原图，不重读整个旧长聊天。新A/B均父到新PM，仅Codex/Sanger/max；常规同方面复用，不再到处建角色。复审保持作者独立、优先1～2个复审会话，不与实现抢文件。PM独占构建/开发预览服务、全局基准/清单/交接。

初始新PM仅做接续校验，收到旧PM的`MIGRATION-READY`后立即持续推进，不等用户再说继续；A/B可先在各自模型/报告目录工作，不抢生产源。新角色ID映射、切换完成见roles.json和migration-state.json；只确认真实创建/启动与原始文件一致，模型接入如失败就报实际错误，不切回Hermes。

阶段声明精确：已派工/已写源码/独立静态通过/测试通过/构建/实际部署/用户体验分开。当前整体未98%/未全产品验收，真实广告SDK及其它未覆盖仍列限制。任何查到的旧文档状态与新证据冲突，保留历史并用新覆盖段校正，不制造重复未完成项或虚假完成。
