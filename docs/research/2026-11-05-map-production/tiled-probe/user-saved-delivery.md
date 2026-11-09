# 用户保存地图接入结果

用户实际保存probe.tmj，41对象：9庭院楼组、26树、6灯。用户原文件字节已备份至runtime/source-maps/（按SHA命名）；转换只处理gui-saved.tmj副本，不回盖用户原文件。

[实际Cocos预览](http://127.0.0.1:4184/edited-viewer/) · [工程截图](cocos-user-edited.jpg) · [逐对象位置核对](engine-position-verification.json)

原部署JS仅允许两块，本隔离副本修改数量检查为至少一块，并为独立缓存改bundle/config版本名。保留Cocos引擎/原绘制器，没有用HTML替代工程画面。原样板/源码/正式地图/存档均未改。viewer-guard-patch.json记录修改前后；实际文件现位于edited-viewer/assets/main/index.probe41.js。

实际浏览器已显示并读取Cocos场景41节点，对比实际保存文件的物体尺寸、锚点和位置（含图层-13,-26偏移），最大误差约2.55e-8编辑器像素。4项转换测试通过。此为位置/尺寸闭环，不是美术/全图/游戏阶段测试通过。

未通过项：用户设置draworder:index，旧引擎仍按接地点排序，手动前后层级未同步。整体块内楼树不可拆开。截图可见摆放出原地面范围的对象旁仍为空底，原样板地面显示范围未扩大。本轮不擅自改用户布局/删重复对象。
