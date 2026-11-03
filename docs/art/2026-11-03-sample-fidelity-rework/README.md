# 首块样板重做：用户拒绝后的修正入口

**最新：v2真实工程外观仍被用户明确拒绝。** [第二轮对比与方法追问](method-review-feedback.json)已归档，当前密度增加与贴图/几何小修不能代表画风改善已被接受。PM已停止继续此Canvas路径的补丁/全县扩张，正在评估正式资产和显示生产方法；见[独立技术判断](../../reviews/county-rendering-method-20261103/independent-assessment.md)。下方v2/材质均仅历史实际产出，不再作为达标依据。

2026-11-03。用户明确：仍有大片未布置空地，不能只处理成绿地，需要更多建筑、不要太多绿地；工程画风/颜色与概念稿毫无关系。此前将铺草/重复小窗计为完成的解释已被覆盖。

| 输入/产出 | 状态 |
| --- | --- |
| [被拒工程图](user-rejected-engine.png)、[用户重申目标](user-target-concept.png)、[原话与SHA](user-feedback.json) | 原样归档，旧工程外观明确被拒；目标仍为已认可概念 |
| [样板密度v2](density/README.md)、[工程JSON](density/sample-scene-layout-v2.json) | 110栋新增商住，真实足迹约4.10万m²，占预先剩余可布置地面52.56%；绿地约1580.5m²，占该地面2.03%。源134楼/59路/水系/两入口等数组逐值不变 |
| [材质包](materials/README.md)、[清单](materials/manifest.json) | SF01首层玻璃、SF02上层墙窗、RF01干净屋顶已实际齐备并交开发；按真实面分格，不整栋拉伸 |
| [规格](../../superpowers/specs/2026-11-03-sample-fidelity-rework-design.md)、[执行计划](../../superpowers/plans/2026-11-03-sample-fidelity-rework.md) | 默认街区近景、建筑/道路/光影同步重做，不靠缩放藏空地，不只换色 |

开发当前在独立样板实现v2和新显示模块，报告位于[重做实施记录](../../reviews/county-sample-fidelity-20261103/implementation-report.md)。输入产出存在不等于最终视觉已达标，当前未通过用户验收；未运行游戏测试、浏览器或独立渲染复验。

旧样板、全县扩展和外围数据留作历史与回退；本轮先收好首块，不把被拒的密度/外观继续铺全县。原始city.json、路网、水系、原建筑足迹、用户外边界、已认可UI和存档保持。`built-block`分区为引用，`renderGround:false`须跳过填地；真正残余地面按多环evenodd。铺地口径与实际未完成项见[density摘要](density/density-summary.json)，不能把所有铺地都误说成小广场或以一棵树计为地块填满。
