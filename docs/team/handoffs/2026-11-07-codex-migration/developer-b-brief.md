# Codex开发B接续：已有真实测试证据收口与产品UI

你是新产品PM thr_4xmqy6fzdm的开发B。用户最新路由Codex / ccs-sanger/gpt-6.1-sol（Sanger）/ max，不再用Hermes、默认同名模型、astra、nested CLI/新子Agent。当前同env_e54zrbdgxt、同checkout；不fork/worktree，不清理dirty/untracked或重复生图。

先读docs/team/handoffs/2026-11-07-codex-migration/handoff.md第0/1/2/3/4/6节，再读所需实际原始JSON/图片。旧B thr_tviezvnwds已中断停止，浏览器已经closed，不重新接管那个session，不造其存档或假连续性。旧根report/test-results还是RED检查点，但B20～41已经在磁盘，**不可因此误报新包没走过配送或重复做已通过步骤**。

首个可交付任务立即做：
1. 逐个读B20/21/22新包身份与原planned单恢复；B25～31真实UI整单、B29原地ready与时钟停住、B32帧观测、B33拖动/34定位、B35/36非零自然reload、B37～40真实1金币水与账单、B41最后119金币/已送1；查看对应截图并核SHA。可读motion-analysis和browser-close-receipt，不把投影采样/rAF当物理设备FPS。
2. 写**新的最终补充收据**到docs/reviews/2026-11-06-product-testing/b/codex-handoff/（独占写集）；不覆盖RED原始文件，不修改旧原始records。给新PM一个结构化JSON：realPassCases、limits、source/buildHashes、normalSaveContinuity、goldenEvidenceFiles、remainingUserIssues、publishGateRecommendation。尽量复用现数据，不先重跑整套。
3. 原阻塞是构建Map.values展开被loose转换，PM只改Array.from；当前源dd0054...、修复main ab2ce SHAfbd0ca...，原helper/LoadRules未弱化；实际产物回归4/4、独立窄复审PASS，见planned-iterator-*.json。你不能以此说全部U01/98%完成。
4. 现场不直接更新服务。最后已知正式4182/4196旧tick-follow，新修复在4198；新PM统一核门禁/发布/读回。不要操作用户真实浏览器进度。新测试需要PM具体指令后开你自己的新隔离headless，已有session已closed。
5. 后续复用你做明确产品UI/非地图素材，由PM给具体写集。当前初始不写任何生产TS/资源manifest/价格表，不修改地图。万元近似算法仍held，已落实主角/等级/状态/招募外价/标题等不再整套等确认；不用旧静态稿重做。
6. 现有车辆独立原生场景/图集/Web包均有成果，不调用地图插图裁切充产品场景，不换引擎/画风，不整页原图充游戏。SDK未接不假广告成功。原始8张认可图仍是视觉依据且98%未通过。

当前Accept Edits仅给报告补充目录与授权scratch，不全局full；不同于Hermes native模式参数，交回后父PM恢复相应Default。测试授权本批产品有效，但这一步以证据收口为主，不再增加购买/接单/重开测试。完成向新PM回实际收据路径/核对结果，不给旧HermesPM继续派工。不要仅发收到/等待，立即完成边界内的证据接续。
