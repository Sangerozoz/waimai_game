# AU05 补充功能图标接入

**已实现，未测试，待用户说“阶段完成”后集中测试。** 本轮未运行测试、typecheck、游戏操作或渲染核验；未触碰用户存档，未 commit/push。

## 接入范围

- 原图 `docs/art/user-deliveries/2026-10-30-au05/supplementary-icons-original.png` 原样复制到 `delivery-game/assets/resources/map-sample/anime/au05/`。两份 SHA-256 相同，见 `asset-sha.json`。六个图标沿用原图、按独立边界裁切，像素坐标见 `crop-rectangles.json`。
- 招募：底栏已有禁用入口接入新图，保留灰度及既有 1.725 倍菜单图标比例，不添加点击能力。
- 定位：地图现有定位入口接入新图，`locateAnimated()` 回调、15 m 默认比例与缩放逻辑未改。
- 关闭：通用 `closeButton` 接入新红叉，沿用原点击回调。活动卡片和暂停界面原本无 X，本轮没有新增。
- 暂停：配送阶段已有暂停钮接入新图，整钮仍只缩放一次至 0.5，原生双竖线保留为图片加载失败时的回退。图片以始终活跃的 `identity` 节点发起加载，之后挂到暂停钮下；这样按钮在非配送阶段隐藏时也可完成加载，并继续继承按钮的显隐与缩放。独立点击区及暂停条件未改。
- 背包与确认图标已注册为可用裁切映射；当前项目没有可见的对应调用入口，因此未新增按钮或业务。

AU03 的其余图标、车辆素材和 50 款餐品目录没有在本任务中修改；新餐品图片仍未交付。

## 构建与静态服务

最终一次 `npm run build:map --prefix delivery-game` 包装命令退出码为 0，`build.log` 记录 2026-10-30 14:56:09 `Finished`。此前一次构建后发现隐藏阶段可能阻止暂停图加载，已调整源码并重新完成最终构建；此前日志留存于 `build-before-hidden-phase-load-adjustment.log`，不作为最终交付。4181 静态服务的 `index.html` 和当前主包均 HTTP 200，响应 SHA-256 与构建产物一致，见 `static-http.json`。静态请求没有运行游戏。

前一工作模型曾返回 `Selected model is at capacity`，本次从已落盘源码和最终构建继续收尾；容量失败本身不计作交付或验证。`before/` 与 `before-sha.json` 是修改前基线，`production.patch` 仅含本次三个脚本的差异；`final-source-sha.json`、`build-manifest.json`、`delivery.json` 记录最终文件与交付状态。

六个图标的实际视觉尺寸、灰度效果、交互点击和配送阶段切换均未做体验验收，待阶段集中测试与用户体验验收。
