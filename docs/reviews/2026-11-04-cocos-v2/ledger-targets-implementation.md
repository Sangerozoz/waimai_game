# 第五批：真实分类账与成长目标查询（未测试）

依据长期implementation-baseline、V1第10/11节及最新frontloaded曲线实现。沿现有V2源码追加，不修改旧CountySaveStore、道路、游戏实际存档或业务参数。

新增V2Ledger、V2ProgressTargets及meta。Economy保存整数分账本：显式opening余额＋所有实际现金流＝当前cashCents；恢复验证该恒等式，损坏账本拒绝加载。现金流分类包含主角普通/专送、NPC逐单、旧在途真实结算，以及购车、招募、改装、培养、开图、付费补给。逐单ID为order:订单编号，重复配送不会再记账；普通消费使用持久递增序号，补给可传transactionId使重试去重并拒绝金额/详情冲突。零费用配车/选图/休息不伪造支出。库存使用不调用扣款，领取不发第二笔钱，没有10%额外金币奖励。

旧V2没有ledger时，将当时实际cashCents记为migration opening，时间和日键均未知，不根据已完成单数重造历史收入。新档opening source=initial，开局100金币只算期初、不算经营收入。CountyV2Session迁移原档同样以实际余额开账，保留原始checkpoint；迁移前在途单实际结算后追加legacy_delivery。账目仅存在新组合快照，不写实际用户存档。

外部注入Economy/Dispatch.setLedgerContext({nowMs,dayKey})，上下文随工作克隆保存。日键为宿主提供的YYYY-MM-DD（或null），不由订单ID/加载日期猜测。Fleet按共享工作时间逐步映射真实due atMs记录每单，但当前没有历史时区解析器，NPC日键为null，归入unknownDate，明确不将离线全部收入算登录今日。推进后还原外部命令上下文。下一阶段可以在宿主可靠提供历史时区转换后补足日统计；不能回填假日期。

summarizeLedger(ledger,{todayDayKey,recentDayKeys})提供今日、近7日、累计和日期未知四组；每组含incomeCents、expenseCents（正数）、netCents及byCategory（收入正/支出负）。opening单独显示；Economy.ledgerSummary另给expectedCashCents/currentCashCents/balanced核对。累计范围是本账本记账以来，不声称迁移前全历史。

queryProgressTargets(state)是无副作用数据查询：首辆新车300、首NPC120、3名已配车NPC小队（20分钟是设计目标）、至少4图/24NPC/前8车型、30NPC。返回真实费用/差额/进度/前往页；够钱只可前往，不自动消费、不因建议产生资格限制、不发奖励。小队需实际配车才完成；24NPC等是数量目标而非强制体验顺序。

待执行测试v2-ledger-targets.test.cjs覆盖期初迁移、分类、重复订单/补给、日期隔离、恒等式拒绝漂移和目标只读。旧economy/fleet的富余额测试准备同步opening余额，未放松生产校验。按用户阶段规则，本批没有运行tests/typecheck/build/游戏或读取写入实际存档；静态源码检查不等于编译或体验验证。Runtime/UI接入由同批代理负责。
