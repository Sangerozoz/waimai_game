# 原Important的专项只读回审

复用 `thr_978x3n893w`；同checkout、原provider/model/max与只读边界不变。请仅针对你上次指出的屋顶遮挡问题及对应修复复核，不重复整套美术/旧保护源审查，也不另建会话。禁止改文件或运行写入型builder/verifier/导出，允许读取脚本和图片、在内存独立计算；不运行游戏、tests/typecheck/FPS或操作存档。

先读 `OCCLUSION-FIX.md`、`verification/occlusion-evidence.json`，可对照 `history/before-occlusion-fix/` 中的旧构建器/验证器和原图。母图、裁界和拼接像素未改。

请核对：

1. `build_pair_evidence.py`、`W/actual-graph.json`、`E/actual-graph.json`、`actual-pair-graph.json`：`W-h-0-2` 明确禁导航、是屋顶遮挡推定；35边结构图与34边可导航子图分开。12个完整街坊保留，结构图12面、可导航图11面；`actual-blocks.json` 中B-05-04北边推定有披露。
2. 主路径3158.369316876853px，排除W-h-1-2后的新绕行3973.6525698173054px；两条都排除屋顶边。请独立重算并看新南侧绕行是否仍有同类可见路面问题。
3. `verify_pair.py` 独立Bellman-Ford及逐边路径检查是否真的拒绝禁导航边；`verification/test_occlusion.py` 有4项只读回归，旧失败/新通过原输出保留。静态报告566项通过；不要把脚本本身几何通过当可见沥青语义通过。
4. 三份 `tiled/*.tmj` 里可导航/推定独立分层、推定默认隐藏及属性正确，全部顶点/名称/属性往返不回退；`viewer-template.html`/`index.html` 默认道路层34条，打开推定也不影响路径。

主会话已重新执行官方Tiled六命令/六导出（`verification/tiled-cli-v2/`）和浏览器10桌面+2手机检查（`verification/browser-display-checks-v2.json`，五截图、原始结果），会话已关闭。你可检查记录，但请明确不代证未亲自执行的CLI/浏览器。

请回复是否原Important已消除、任何新Critical/Important/Minor及证据。分别给“独立证据可展示”和“普通地图生产/整城验收”结论。用户尚未审两张美术，米制覆盖/最终图数仍未知，无正式游戏测试授权。
