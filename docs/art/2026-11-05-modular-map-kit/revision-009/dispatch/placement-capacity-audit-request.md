# 独立只读审查：相邻源址容量为什么很低

上轮树木制作权限已结束。现在复用你做**独立审查，不是美术生产/规划实现**；你未写过当前规划/接入代码，保持作者独立。不要生图、不要创建其他Agent。唯一写集：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/review/placement-capacity-audit/。其余全只读，不改任何门禁/共享脚本/原city/业务/UI/经济/存档，不游戏tests/typecheck/回归/FPS/浏览器/服务/提交。

用户要求整县地图、多样完整场景，原路/水/红蓝绿/业务与nav不改。允许参考认可25图做纯美术地块规划，不新增经营地址；小误差接受，明显遮挡要修。当前同一006已实际显示156静态/497面、81源映射；不少图仍大片空白。第五规划限定两个140m邻区，旧可行池仅10新源；另外45源实际替代试算大多失败。不能直接判定算法有bug，也不能用继续挑远处大地块掩盖卡点。

## 已完成只读输入
- revision-009/planning/fit-round-5/REPORT.md、joint-fit-summary.json、local-fit-progress.json、joint-clearance-evidence.json，以及plan_fifth.py/assemble_fifth.py/refine_b07_court.py/finalize_fifth.py。追到它们引用的fit-round-3/4和共用geometry函数定义，按需读，不整段历史重扫。
- 重现第五拒绝时使用**同一已完成143基线**：revision-009/baselines/visible143/（scene/TMJ/library/calibration/manifest），这是静态审计输入，不是重置现图。shared renderer正继续场地艺术整理，别读取/轮询在写viewer当本次冻结基线。
- 第四/第五实际图和报告在revision-006/integration/batch-009-r4、batch-009-r5。原source数据delivery-game/assets/resources/map-sample/city.json，只读；源buildings是polygon，不要捏造不存在的原楼业务/门位绑定。红蓝绿selection只读。

## 要回答的具体问题
1. 程序统计45源的**源级**最先/全部拒绝类别，并单列尝试级计数，不能把上千asset@scale/approach失败当上千源。区分otherSourceMetres/道路水/POI真实安全、原1.5m门路、旧sprite保守包络、旧地面关系、用途未知/主观programme-context等。给真实source id与代码path:line。
2. 抽最多5个有代表性的失败源，读实际多边形和调用链，用只读输入在自己目录做最小静态反例/算例。证明规则真的检查什么：是别的原楼实体、合法门路/车道，还是普通草坪/铺装重叠/接边被作为实体。后者也可能是合理的编辑权限边界而不是bug，要区分“范围受限”和“几何错误”。不要先放宽全部障碍、豁免未画出的原楼或把屋顶billboard当精密脚线。
3. 检查unknown landuse/programme拒绝来自原数据/用户硬约束还是本线手工候选分类；用户已授权的纯视觉功能规划与新增业务是两回事。没有源语义不能伪造事实，但也不能未经论证把一切美术规划当新增经营。仅报告证据和需PM判定边界，不自行解禁。
4. 查一源多模块/多源一景的合同与实际入口：当前是否被“一源恰一楼”的实现或去重策略限制？对现有大载体“多视觉楼＋同一源集合、无新POI”应怎样表达才不灌水源数/破坏旧绑定？只提具体最小候选，不实现，不以强塞多楼作为预定正确答案。
5. 明确结论：真实空间/未覆盖源限制、缺少合适体量或路向、错误/过保守的判定、源用途假设、编辑权限限制，各有什么证据。若未发现错误也直说。最多给两项最值得下一步验证的改进建议和风险，不建大重构计划/新朝向矩阵。

只运行自己的小型静态几何/计数脚本，不执行会回写原报告的规划脚本；如需导入先读副作用并禁止bytecode，或在审查目录独立实现必要纯函数。冻结输入前后SHA保护。交REPORT.md＋机器可复核分类JSON＋少量反例数据/脚本，所有总数Python汇总，未跑游戏测试明确。先给根因与证据，不提交实现补丁、不声称密度已提高。
