# Codex开发A接续：真实数值平衡模型

你是产品PM thr_78t2htdctw的开发A；迁移授权来自用户：不再使用Hermes，指定Codex模型6.1-sol（Sanger），max。实际配置必须为Provider codex / Model ccs-sanger/gpt-6.1-sol / max；不要切回Hermes、默认原生同名模型、astra、nested CLI或新子Agent。使用同env_e54zrbdgxt和当前checkout，不fork/worktree，不清理未提交。

先读取docs/team/handoffs/2026-11-07-codex-migration/handoff.md第0/1/3/5节与protected-artifacts.json；读baseline最新覆盖及当前source所需定义。它们是精简交接，不读取旧长聊天。旧A thr_j9izunn7qx已中断停止，**没有a目录模型产出**；95项测试/guard已完成，不重复修旧问题。PM当前探针已有quote/成长结果和3条未批准敏感性曲线，全部保留。

立即实际实施并运行当前数值平衡第一轮，不仅给计划：
- 唯一写集docs/balance/2026-11-06-balance-round-01/a/下模型脚本、baseline-results.json、events.csv、report.md和可选候选JSON；临时编译只用系统提供scratch。生产TS/JSON、测试代码、UI、地图、用户档只读，不构建/部署/commit/push。本批Accept Edits仅限此写集，交回由新PM收回，别用旧Hermes的_bb/legacy-mode参数。
- 导入实际当前Game/Economy/Route/Fleet函数，从合法新档100金币/2格和真实已赚资金出发，不用richGame/richEconomy/注余额/赠品/强开图。可先有界代表性运行场景并明确路程假设，再用既有游戏只读供给依赖扩展；不做地图生产/布局/边界，不找地图会话。
- 先前20/60分钟，至少4条投资路径：推荐小队优先、升级旧车优先、大容量车优先、先NPC及唯一旧车分配；常规/慢操作明确，慢只加阅读/点击停顿不改道路速度。优先无广告，真实SDK未接入不得模拟线上成功。
- 记录每单毛/净、单数/分钟、升级购车招募补给支出、首车/首NPC/3名均配车NPC时间、额度利用/停工与真实可接数量。保留推荐无额外消费的10单首车/15单首NPC预算；20分钟小队及二八需重算，不贴旧19.91/27.41。
- 当前PM实跑的风险：保护14→15边界354m从20→19.27、100m18.75、500m19.57；2km/4km同22.66。319车型过渡231不加格但0个三属性全不增。别把公式合法/平均单价当平衡；比较单位时间、容量利用与扩队回本；先NPC借唯一车/额度耗尽是否软锁必须用合法路径实际验证，不能脑推。
- 先给真实基线，再至多3项最小候选+同路径对照；生产价不变，不补贴/恢复资格/抬收藏尾价凑目标。旧已签合同与当前资产/金币/等级兼容另由PM串行设计。pm/candidate-curves.json仅候选，不直接批准或上线。
- 临时TS输出在scratch且精确清理自己创建的目录，保留原始命令/exit/sourceSHA/结果。不能跑通就报实际阻塞和已完成部分，不编造数据或无限审计。

此迁移初始任务允许你在上述模型目录持续做；PM只读接续验收同时进行，生产源码仍冻结。完成向父PM回事实和绝对路径，不给旧HermesPM派工。常规决定无需再问用户，重大体验取舍留明确对照给PM。
