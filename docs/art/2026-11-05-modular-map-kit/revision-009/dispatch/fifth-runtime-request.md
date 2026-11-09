# 第五批v2增量接入：保护当前146/466，不回放143快照

继续你现有地图接入角色，不新建工程。父已实际看native-low/shrub图并核当前发布scene SHA 64e00ad3a2d6654858233fe623d4fba1b81754bdc8b47f4d4676d6851ce51a5c：146静态/466面/71源绑定。新增B12源1731、B13源1383及T05已经存在，必须连同life-street/第四批全保，仍仅有限比较，不趁本批扩大新三类准入。T04继续hold。若你又有合法增量，按最新实际发布基线核对，不重置任何快照。

唯一输入：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/planning/fit-round-5/fifth-expansion-batch-v2.json
父批准原SHA256：f2d391dccd4efb32ea0d1868db8f53abbdecf8df3772f617f6bf79ba3a0bf5e1
同目录import-contract.json必须读。首版e9ec文件仅历史，不能接入/改写。v2为10源/10场景/10模块/31面，市场4、住宅6、两个140m邻区，六种既有准入楼型。不是全县完成。

父已独立核：v2楼体/门/尺寸/道路与v1完全相同；其余29面不变，只删1423的source-court/entrance-apron两面换partial-inner-court一面。新面面积12平方米，四角位于真实8点U实体的凹空腔，距实体约1.9143m，连接009r5-src-1423-walk-0。不要填满void、把U框当实心楼或回用旧假门。10楼worldSizeUnits均canonical×uniformScale一次，entryPixel按原PPU/anchor回投影到entryMap误差0；nodeScale1，uniformScale仅来源，不再乘0.9/1.1。原source polygon和6条完整原路节点/width/direction逐项一致，10源不与原69或预留1731/1383重合。源索引[260,261,262,264,1359,1363,1364,1377,1423,1738]。

执行前仍须对**最新146及其后**实际地脚/旧466面/新低楼与灌木/原source障碍/蓝边水/业务节点/同批重新核对。只豁免本source carrier，不移动或删除旧物，不改旧地面/镜头/D路径/源绑定。个别冲突只排除该新增候选及专属面，记录原因，不强凑10、不挡其他安全项。父查69旧绑定时需兼容sourceIndex单数及sourceIndices数组，不漏旧源；现在应计入新增1731/1383共71，不能把源地址数与静态实例数混同。

沿原独占写集006/integration、viewer、009/pipeline，规划/native/其他线只读；新批group增量进同一Tiled与Cocos，不init/不换scene快照。只引用<=280运行PNG，保file+SHA共享Frame、有限区域地面，原生/25图/全城分析快照不打包。道路完整数组只读，绘制可有限clip，不新增业务/导航/交通AI。

本轮优先交能看见相邻关系的市场邻区及住宅邻区近景，最多两张，不给跨两区的巨空远景或10张单楼矩阵。确认新旧楼、庭院/前场和门路实际可见；密度与地面仍不足就如实标注，不以节点数代替场景丰富。保存原输入SHA/派生SHA/真实最新基线、逐项入拒、旧数据保护、实际节点尺寸/Frame/PNG预算及稳定最终scene/TMJ SHA。不得写已用户验收/全县完成。无生图/游戏tests/typecheck/回归/FPS/存档/新服务/提交。不要等其他原生或新规划才能继续本批。
