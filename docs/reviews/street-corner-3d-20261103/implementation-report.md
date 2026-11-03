# 三维街角样板实施报告

2026-11-03，静态交付，等待隔离样板实际展示。目标与接口见 `docs/superpowers/specs/2026-11-03-street-corner-3d-design.md`。

- 独立工程 `delivery-game/street-corner-3d-project/` 单独启用 Cocos 3D 和 primitive，未修改主工程引擎配置。场景脚本消费指定 JSON 的 box、cylinder、sphere、mesh，按材质和投影/接收阴影属性合并网格，设置正交相机、标准材质、方向光、环境光和阴影贴图，并提供缩放/复位与加载错误提示。材质和光照的最终画面尚未实测。
- 按本机 Cocos 3.8.8 源码修正阴影接收枚举，避免大网格数组展开触发参数上限。位置、尺寸和取景来自输入数据；保留原坐标约定，不读取或改写订单、存档、地图数据。
- 独立 Cocos 构建日志 `/private/tmp/street-corner-3d-build-final.log` 显示 10:42:52 Finished，构建目录 `delivery-game/street-corner-3d-project/build/street-corner-3d/` 已生成并复制到 `delivery-game/build/map-sample/street-corner-3d/`。日志包含 `build-script` 子进程 SIGTERM 诊断，不能仅凭 Finished 认定运行成功。
- 旧县城样板源码及静态副本包含新入口链接；本机 127.0.0.1:4181 静态服务已启动，根目录为 `delivery-game/build/map-sample/`。
- 最终资产 `docs/art/2026-11-03-street-corner-3d/scene-design.json` 已原样复制到 `delivery-game/build/map-sample/street-corner-3d/scene-design.json`，两份 SHA256 均为 `15e36246b7c967af685941bfd55937e80bc0a7150a22c64dbf42dfa46427ec47`，部署文件 9,062,262 字节。资产报告 164 个组合 mesh、60,608 个三角形及 44 种材质；镜头 target `[6,6,3]`、position `[-52,68,83]`、正交半高 35。素材复制无需重建 Cocos。
- 入口 `http://127.0.0.1:4181/street-corner-3d/` 的静态 index 和素材文件已就位，4181 监听已确认，可供 PM 打开隔离美术样板；未在此会话打开或确认实际运行画面。
- 未运行正式游戏、游戏测试、typecheck、存档操作或渲染矩阵；视觉效果、光影、遮挡、性能与用户验收均未确认。隔离美术样板的单次展示由 PM 负责。

## 首次展示加载失败及修正（10:54）

PM 首次打开隔离样板看到 `Cannot read properties of undefined (reading 'localSetLayout')`，未看到场景；旧 catch 未输出堆栈。静态定位到 Cocos `SubModel.initialize` 对 `passes[0].localSetLayout` 的读取，同时此前构建的 internal 资源清单不包含以字符串动态创建的 `builtin-standard`。这表明缺失标准 effect/空 pass 是高可能原因，尚未从原始堆栈独立确认。

现将 Cocos 3.8.8 随附标准 effect 显式纳入独立工程 resources，并显式异步加载引用，检查材质 passes；先设置材质再设置网格，catch 记录 `[street-corner-3d]` 完整异常供诊断。独立构建脚本退出 0，日志 `/private/tmp/street-corner-3d-build-fix.log` 10:54:56 Finished，资源清单包含 `street-standard`，资源及场景数据已更新到 4181，场景 JSON SHA 与源一致。日志仍有 build-script 子进程 SIGTERM。未在本会话重新打开或确认错误消失；需 PM 刷新隔离样板作单次展示，若仍失败读取浏览器 console 的错误堆栈继续定位。

## 日光和阴影调整（11:01）

PM 已观察到首次隔离场景显示、`localSetLayout` 错误消失；反馈纯色低模感、玻璃偏暗、墙地偏灰、阴影偏硬。该反馈不构成视觉验收。

只修改独立 Cocos 脚本：方向光颜色改为微暖白 `(255,244,228)`，强度维持 65000；环境天空/地面颜色由偏冷调整为偏中性暖色；相机由默认 f/16 调至 f/14，约提高 0.4 档曝光。阴影贴图场景配置原有 2048×2048，之前运行时未显式设置 PCF，Cocos 源码普通质量默认 HARD；现明确设置 `SOFT_2X`（9 次采样），阴影距离 140 收至 100 米以集中覆盖样板。具体 GPU 阴影效果、边界或裁切风险未实测。相机视角、目标及半高仍来自场景 JSON，不擅自覆盖美术侧取景。

场景 `_useHDR=true`，tone mapping 为 DEFAULT；本轮不改变色调映射或使用大规模后处理。Cocos 3.8.8 中 `ENABLE_WEBGL_ANTIALIAS` 默认 true，WebGL 创建 swapchain 时请求抗锯齿，但浏览器/GPU 是否提供、渲染管线效果尚未知；未宣称锯齿问题已解决。纯色资产和玻璃的设计由美术任务另行处理，光照调整不能替代材质细节。

独立构建日志 `/private/tmp/street-corner-3d-build-lighting.log` 显示 11:01:33 Finished，进程退出 36，包含既有 `build-script` SIGTERM 诊断；构建产物已复制至 4181，保留当时现有 scene-design.json，SHA 仍为 `15e36246b7c967af685941bfd55937e80bc0a7150a22c64dbf42dfa46427ec47`，未覆盖美术侧在途文件。仅静态检查，未复看本轮光照画面、测试性能或代替用户验收。

## 第二版资产部署

美术任务已完成第二版 `scene-design.json`，已原样复制到 `delivery-game/build/map-sample/street-corner-3d/scene-design.json`；源文件和部署文件 SHA256 均为 `c94451f7435125fd6534062b555acf8a61e4ff0e8fea1682bd426d7b5dde102c`，部署文件 6,966,208 字节。资产任务报告 174 个组合 mesh、48,484 个三角形和 46 种材质；相机 target `[8,7,3]`、position `[-30,70,105]`、正交半高 31。该版覆盖上述早期资源 SHA 与镜头状态，保留已打包光照调整，无需重建。

4181 静态服务监听已确认。PM 已观察到第一版场景能显示；第二版尚待 PM 展示，不据静态部署声称视觉达标或用户验收。未执行正式游戏测试、typecheck 或存档操作。
