# revision-006 接入准备：11楼型实际运行库

继续你的地图接入职责。用户已认可005混合街段并授权继续，以25图多样建筑为参考。本轮B06～B11六件真实原生及280运行图已回齐，父会话已逐字节核source并看过运行对照；车辆v1被退回风格/角度修订，不准当可用车辆。

**写权限切换：上轮revision-005写权限结束，旧样板全只读。当前仅写**
`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/` 和同级`viewer/`。不写planning/native/references或公共文件，不改原city/路网/边界/业务/UI/经济/存档，不测试/typecheck/回归/提交，不生成新图或再建Agent。

## 立即可独立完成，不要等规划空转

1. 将005中已有B01～B05、T01/T02/T03、两侧向内灯与原D骑手的已导出校准/运行图只读复用；保持B01/T01认可尺度，不重新设计。六件新楼在`revision-006/native/B06-001`直到`B11-001`，各有`ID-v1.png`、`ID-runtime-280.png`、`.runtime.json`、provenance与REPORT，来源选择/几何辅助在`references/residential`、`civic-commercial`、`industry`。
2. 看真实新原图和运行图，读原生成图实际来源和源副本SHA。建统一11楼型资产校准库：实际底角/隐角/接地点手估明确标记，不拿prompt数字当实测。参考自己005脚本的正等比PPU/anchor/裁边worldSizeUnits方法。U形B07中庭透明，B08连拱顶市场、B09扇壳顶公共、B10锯齿厂房、B11坡顶作坊不要强按同一盒子处理。B11主要卷帘门在短向侧，后续必须按实际门位留可达侧院，不假装门在长向正中。
3. 输出真实精简运行资源目录和`asset-library.json`/`asset-calibration.json`/简短资源统计。运行每张长边<=280；只复制用到的派生图，原生母版不进包，按file+SHA共享image/Frame，不按实例各建纹理。源图与已认可样板SHA保持。列明每件候选世界足迹/高度比例和不确定性，遇明显姿态错误先标hold不强塞。
4. 将接入导出器扩展到本批库，复用005的路/地面多边形/静态index与group offsets/中心缩放/实际viewport fit能力；不要创建另一个纯素材展示项目或伪截图。初始化必须拒绝覆盖用户手调地图，旧005永远只读。

## 规划依赖与接入门禁

邻区规划线程thr_f9h46pp7kn正在修正原15候选中5处入口受原楼阻挡。**当前planning/next-neighborhood-plan.json尚不能直接标ready。不要轮询等文件或按旧15栋硬接。**先完成上述真实资产库/校准/可执行导出器，回报我库的可用项与源尺寸差异。规划完成的稳定版本由父会话另行通知再做最终三街段运行；若校准发现市场/U院等候选足迹显著大于规划，应列出具体差异给父会话，不缩小/拉斜掩盖或改源路。

旧源码/数据只读：`revision-005/integration/mixed_street.py`、005资产校准与运行包、006/planning/source-context.json、原完整`delivery-game/assets/resources/map-sample/city.json`及红蓝绿selection。真正运行前保留原道路节点/宽度/方向/projection逐值核对；车辆v2通过前仅保留原D骑手内存示范，不冒充交通多样性已完成。

## 此次回报

交实际落盘的资源库/校准/导出器路径和可运行的资源校验结果、唯一PNG字节/数量、原sourceSHA保持情况、待规划依赖/姿态与接地风险。不是只写方案。此阶段资源库完成不等于新街段显示/用户验收；不要把未运行的viewer说成已交街区。final简短中文自动回父会话。
