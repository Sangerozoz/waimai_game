# 经济领域交付（2026-11-05）

本次实际源码仅修改 `delivery-game/assets/scripts/domain/V2ProgressTargets.ts`。按最新派工优先补目标查询，未抢UI、未修改参数JSON、未改其他owner文件。使用系统性排错和完成前验证的证据原则；用户禁止执行游戏/tests/typecheck优先，所有结论限源码静态与独立算术。

## 首张付费地图

新增稳定id `first-paid-map`，位于 `first-car`、`first-npc` 之后，原API、字段和五项长期指标保留。完成条件为配置中非初始且 `price>0` 的地图ID实际存在于 `ownedMapIds`；不是 `ownedMapIds.length>=1`，不看当前选中图，不要求先买便宜图。初始晴川县不计完成。报价取全部未购付费图最低价×100，没有候选时null；余额差额、可前往状态沿用原add逻辑。完成后即使仍有其他未购付费图，`canGo=false`，`shortfallCents=0`，UI应按completed过滤。

首页UI由thr_uevwv32vnh接入：固定 `first-car → first-npc → first-paid-map`，只显示首个未完成、全部完成收起；无换任务。领域不购买、不发奖励、不强制消费。父PM已澄清“不奖励”仅是不新增未确认奖励，不能取消此前已确认规则；本次不删旧规则，也不往空奖励表填数据。

已通过 `bb thread tell` 告知父PM thr_axf6i4e89t 与UI owner稳定id及口径。

## 当前参数与报价静态核对

权威为 `frontloaded-2026-11-04-v3-hire-training-tail`。已读长期基准、hire-training-correction、parameters.json、hire-training-v2/README及六个领域模块。未采用旧frontloaded-curve叙述。

独立脚本 `python3 docs/reviews/2026-11-05-game-development/economy/audit_parameters.py` 只解析TS中的JSON字面量和权威JSON，不执行TS，不导入游戏。实际输出：

- 配置深相等true，629个标量；外部V2_CONFIG_ID与configId一致。
- 30级培养及10车型×30级累计公式差异0；前三NPC120/130/170、末6收藏价格保留当前表。
- 培养29次相邻累计差之和160000分；收入满级1.6倍、固定服务耗时减25%。
- 10车型累计升级费用分别为450/900/1500/2700/4500/7500/12000/18000/120000/240000金币，均为1.5P。
- 免费旧车基数150，满级225金币；前5级累计0/2/5/11/17金币，未改变。
- 起始100＋10×20＝300，首车扣300后0；5×24＝120，首NPC扣120后0。限不买补给、不提前升级、普通单/初始地图/按推荐买首车；不是强制资格。

完整结果和源码SHA见 `parameter-consistency.json`。独立首图场景覆盖仅[1]、余额够/不足、先买第5图、全部图已购；这些是独立逻辑推算，未运行目标函数。

## 调用链静态证据

- `riderHireQuote(id)`取固定ID价，`hireRider`同报价扣款；UI骑手卡调用同函数。没有按hireCount决定购买价格或招募资格。
- `vehicleUpgradeQuote` / `riderUpgradeQuote`均取相邻累计费用差×100；实际升级和UI详情直接使用同报价。主角金币培养被拒绝，主角每交付+10经验；NPC等级独立金币培养。
- 购车、招人、买图只有ID/余额/已拥有检查及主角配送期间暂禁资产交易，无等级/地图/招募顺位资格。购车每次新实例ID，分配拒绝同车多人，旧NPC批次锁定身份、车/人等级与收入，结算不追溯新升级。
- `transact`、主角/NPC接单与结算、取消均先clone、校验再替换；异常不发布草稿。余额与账本逐项合计一致由validateLedger校验。主角最后一笔重试返回lastReceipt，较旧重试拒绝；NPC重复结算返回0，均不二次加钱。重复招同ID/买同图拒绝；重复买同款车是独立合法实例，并非幂等键。
- 补给6项价格/恢复/耗时与V1第6节一致，GameSession从catalog报价，TripRules在扣款前校验开放/库存/满体力，库存不扣现金；最高已购图保留低阶补给。空奖励表拒绝未知rewardId，不恢复消费返10%。
- 账本dayKey由宿主输入并校验日期，不从订单ID猜。NPC Fleet暂显式dayKey:null，累计与未知日期计入，今日/近7天不计，详见remaining。

以上为静态路径审阅，不证明运行原子性/幂等性或用户体验已经通过。

## 验证边界

只运行Python独立算术、JSON解析、rg/sed等源码检查。脚本首跑根路径层级写错导致FileNotFoundError，改为parents[4]后成功产证；未触碰游戏。未运行tests/typecheck/回归/Creator构建、未开游戏、未购买/招募/升级/接单、未读改用户档、未commit/push。当前多项经济源码为既有untracked文件，不清理或改其归属。本报告不宣称已平衡、阶段完成或验收。
