# 首页街区样板生产素材

任务 HOME-STREET-1101，2026-11-01。用户已认可首页概念并授权开始制作，允许在真实道路之外的空地补非交互房屋、院落和绿化。实施计划见 ../../superpowers/plans/2026-11-01-home-map-street-sample.md。

本目录保存实际生成原件副本、完整提示词和生产几何底稿。七张新素材通过内置imagegen生成，参考已接受的 ../home-map-concept/home-map-screen-v1.png；不是从概念图裁切成图。原始服务输出留在 /Users/sanger/.codex/generated_images/01a1915b-62c5-7b93-95de-bece15a1d48d/，不删除。图像实际规格、alpha内容框、SHA与复用候选以 manifest.json、asset-handoff.md 为准。既有T01–T03不重复制作，适用边界见 existing-assets.md。

|项目原件|服务原件文件名|世界尺寸起点|
|---|---|---|
|HG01-asphalt.png|exec-7e4e8349-fbb3-48f3-83b6-f1cf3fb0be12.png|12×12m材质|
|HG02-sidewalk.png|exec-112c7ddb-f5c0-4af9-b9cb-378dad589bef.png|6×6m材质|
|HG03-grass.png|exec-9d3f45a3-79bd-44e5-894d-59561c56340a.png|8×8m材质|
|HG04-water.png|exec-51c3a559-7671-470b-88d2-0e4a622d4fc0.png|16×16m材质|
|HB01-flat-roof.png|exec-3a283c4d-0240-466e-9977-fdd46b267cbd.png|8×8m材质|
|HE01-tree-green.png|exec-e8342aa2-1b8b-4404-ae4c-0b0c42415a23.png|绿树冠径约6m|
|HE02-tree-warm.png|exec-6d147c55-55e8-4ada-97ec-a5db0d1d73f5.png|花树冠径约5m|

以上尺寸为制作候选，树木按alpha主体而非透明画布缩放。材质世界坐标连续铺设；路缘、标线、地块与屋面遮罩由引擎按真实几何绘制。对边无缝、重复效果、实际引擎显示尚未验证，不将提示词中的目标写成已验证事实。光源统一左上，勿以镜像翻转制造变化而使光向颠倒。

当前状态：七张资源已实际产出、交固定开发并接入；T01–T03完整模块也已用于筛选后的空地补景。最终试玩构建13:43:02 Finished，实施范围与限制见`../../reviews/home-map-street-sample-20261101/implementation-report.md`，PM交付记录见`../../team/reports/2026-11-01-home-map-street-sample-pm-delivery.md`。生产图片已查看，未进行游戏测试、typecheck、回归、渲染复验或用户体验验收，不读取/修改用户存档。用户尚未说阶段完成，样板不等于全县逐栋精修完成。

