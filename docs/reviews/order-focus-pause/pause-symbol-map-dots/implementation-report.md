# 暂停符号与地图密集圆点调整

**已实现，未测试，待阶段集中测试。** 根据用户两张截图及 PM 定位实施。未运行测试、typecheck、回归或渲染核验，未操作用户游戏页面/存档，未 commit/push。

## 暂停控件

`MapSample.ts` 原先在原生白色双竖杠之上加载 AU05 pause 图片，图片成功后隐藏原生符号；32×42 的图片框还会继承整钮 0.5 缩放，细暗条和金边不适用于当前小尺寸棕色底板。

现已移除该控件的 pause PNG 加载、覆盖和异步 fallback 切换，常显原生白色双竖杠。保留整钮 0.5、原位置、独立小热区，以及取餐后待配送/配送中可暂停的语义。AU05 原图及 pause 资源 key 仍作为库存保留。

## 地图圆点

`CityMap.ts` 构造函数按 operatingPOIs 创建的 `Place-*` 白环橙蓝圆点是密集标记来源。现移除该基础圆点的创建循环、poiDots 容器和同步遍历，默认地图不绘制这些圆点。当前订单的 `Pin-取`、`Pin-送` 继续走独立路径保留。

没有修改 pois、operatingPOIs、营业点数据、路线候选、路网和寻路；车辆、15 m 默认比例及总览 fit 保持。B3 点击加速和其他最新改动包含在此次基线与构建中，本次补丁只涉及上述两处绘制路径。

## 交付证据

一次必要构建：`npm run build:map --prefix delivery-game` 包装退出 0，`build.log` 于 2026-10-30 15:38:25 记录 Finished。4181 静态首页与当前主包 `assets/main/index.e9a2b.js` 均返回 HTTP 200，响应 SHA 与当前构建一致，见 `static-http.json`。静态请求未运行游戏。

`before/`、`before-sha.json` 保存修改前文件，`production.patch` 保存两处脚本差异，`final-source-sha.json`、`build-manifest.json`、`delivery.json` 保存最终源码与产物记录。实际小尺寸显示、路线选择画面和交互尚未测试，待阶段集中测试及用户体验验收。
