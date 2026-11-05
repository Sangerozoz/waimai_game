# 首组视角修订：隔离数据接入候选

本目录的 `revision.tmj` 独立于旧 integration/pilot.tmj 和用户 tiled-probe/probe.tmj。首次用 `python3 build_integration.py prepare`，已有地图则拒绝重置；手动保存 Tiled 后用 `python3 build_integration.py import` 更新 runtime/assets 与 ../viewer/assets，不覆盖地图。viewer 是旧 Cocos 隔离壳的字节副本，目标地址 `/revision-001/viewer/`，未运行构建或打开页面。

四向建筑采用新原生图，树直接复制 pilot/T01-v1.png，灯保留旧版。原生尺寸、SHA、anchorUV 在 assets/asset-manifest.json 和 Tiled 内嵌图集中记录。所有PNG字节原样保留，不裁切、不变形、不转图或镜像。

calibration.json 中可见底角只用于手估地面中心；不同机位不按旧16×11m强行拟合。楼体采用主要墙身竖直高度与共同8单位高度参考的候选正数等比尺度，非实测物理尺寸。树175px/投影单位仅为保留完整树高/树干的人工视觉候选，不强套6m或2.6m树池。灯沿旧候选尺度。保持原道路62.5°/45°投影，不为素材改源路。

主图7独立对象；隐藏组保留两条世界轴方向的三树、三单灯和九双臂灯，可拆编辑。组合默认不导出；显示对应组再 import。导出保留正数等比缩放/组偏移，拒绝平面旋转、镜像和非等比变形。运行按 sortMap 深度排序，Tiled 手动层级尚未同步。

局限：新图机位仍与源路投影不同，白边/彩边仍在，人物仍沿用旧放大比例，四向身份和接地比例需实看，人工锚点/缩放均未验收。source-integrity.json 与 runtime/import-report.json 只核验文件SHA和坐标数学，不证明美术、透明边、运行效果或游戏验收。未开浏览器/游戏，未tests/typecheck/构建，未动业务或存档。
