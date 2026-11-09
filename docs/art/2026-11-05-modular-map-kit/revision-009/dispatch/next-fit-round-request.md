# 下一适配轮：先区分未处理、固定尺度失败和真实资源缺口

009县级清单已读回计数，原首批4实例SHA 9360a09116a099e6df54fd2848ee49bd3b39ab7c90d0b5273ba0bfb4089cc9e6已排接入，保持冻结，所有旧009规划文件/原city/00657实例与115面只读。你唯一新写集 /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/planning/fit-round-2/，不生图/游戏测试/typecheck/回归/业务/存档/提交。

父实际统计：蓝内1004 deferred中，325有screening，679无screening；325样例的约束是“unchanged-scale native footprint + positive-front door corridor bounded search”。所以不能用统一deferred标签声称全部已无解或都缺新图。下一轮输出按具体阶段/拒绝规则的统计，不用一句no fit吞掉原因。

先读父已追溯真实定义的 /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/source-entry-semantics.md 。MapPOI.node是导航/取送图节点，当前schema没有sourceBuildingId/门像素绑定；PlaceCatalog直接从连通road-node pool分配地址。保持原node/名称/路线不动，允许真实图门经合法侧院/步行面到路肩，再以设计关联指向原停靠node；不把图门强压到路中node，不新造导航边，不冒称原始楼-POI关联本来存在。若确有物理门约束证据就保留。

适配试算重点：
1. 扩到还没screen的源对象，按source方向/面积/旧认可landUse分层；先给一个跨住宅/商住的稳定可接入增量，不等全1008做完。优先真实业务停靠点附近地块，门语义按上面分层，不回到任意source8m邻近就认定楼门。
2. 新实例可评估合理单一正等比（如0.9/1/1.1试算是候选，不是用户硬新值）；原57、B01/T01认可基准不改，不把一栋压扁或缩到门比人还小来通过。通过/失败分规则留证。
3. 正面直通失败不等于无法接近，可用你此前已成功的有限侧院折线/1.5m通路，只避真实新本体、邻楼/路/水/原业务保护；自身被替换source轮廓不是另一个外部障碍。保持真正门像素，不能搜索把门移到透明中庭。预算有界、分批保存结果，不无限搜索。
4. 原source大长条/复合面可评估“一源载体→多个视觉模块/院落”的组合，不硬规定每个原楼只能一张PNG。必须符合原地块用途，明确clusterOfSource关系、候选足迹覆盖和余地用途、源数组/业务仍原样；不是把大工厂偷偷换成小住宅，也不能用多个sprite虚增源建筑完成数。无足够证据则defer不硬造。
5. 对实际40度高频路向，先给可复核的源road/node方向、原投影推导u/n/Z、一个或两个真实源址适配案例及现族失败证据，再建议最小必要一款紧凑低层住宅新原生朝向。不把世界角/屏幕角混用，不直接做27方向矩阵。北簇小住宅6x4缺口也要区分正缩/通道/体量/朝向究竟哪项不满足，才派生产。
6. 图与语义以实际为准：先前naturalPlants写tree-pitT02有误，现T02是无树池自然树，T01才树池；可以在合法自然语境合理复用T02，但不能宣称一树复制就是多种森林完成。需新植物只报真实缺口。

交fit-summary.json（screened/untested/accepted/rejected-by-rule）, second-expansion-batch.json（独立新稳定SHA，别动原4栋）, direction-native-contract.json（若真需要原生，给确切geometry/源址/25图局部参考，不先出图），简短REPORT。每个源Id唯一计数，assigned只是静态候选，不是rendered/用户验收。先增量返回能用的数据，不再只交全县大台账；源码只读证据缺时明确不确定，不为数量放宽道路/邻楼碰撞或三框规则。
