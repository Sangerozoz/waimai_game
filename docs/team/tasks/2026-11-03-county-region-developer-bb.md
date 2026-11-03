# COUNTY-REGION-1103：地图开发接续

用户已明确满意REGION-A-v3，要求按其规划持续完成整张县城地图后再开始其他任务，授权自主创建Agent与新对话。你是本轮BB唯一业务代码/引擎集成负责人，PM为BB `thr_7w55f3h66f`。旧ChatGPT开发目前交接所报idle、R2停止；由于无法跨应用发送消息且用户已授权新对话，本次在同一checkout通过BB接续，不fork、不worktree。

## 目标与输入

先读AGENTS.md、docs/product/implementation-baseline.md、docs/team/handoffs/project-manager-current.mdsvg、development-current.md。新授权覆盖其中A-v3待审/只读待命的旧状态；原路、用户红蓝绿边界、布局、高机位62.5°、A-v3画风与独立骑手保持。现有认可high-camera-city与v1副本不能覆盖。

## 当前独占范围

你单独负责新增独立 `delivery-game/county-region-project/`（从现有Cocos高机位工程选择性复用源码/配置，不能复制library/temp等缓存）与 `delivery-game/scripts/build-county-region.sh`、独立预览 `delivery-game/build/map-sample/county-region/`、报告 `docs/reviews/county-region-20261103/`。共享assets/resources/map-sample/city.json、正式业务/存档、旧high-camera工程与部署均只读。PM与两名数据代理只写docs各自目录。

## 当前可立即执行

1. 阅读旧工程实现与现有区域数据，设计/实施整区图片加载、全县范围相机平移缩放、按视口延迟加载/释放、透明区域图排序与重叠归属、原路投影和独立骑手接口。不要用重复贴图/程序盒子或空占位填充冒充最终地图。
2. 把最小稳定的 `region-atlas.json` 接口及坐标/图片锚点需求写入 `docs/reviews/county-region-20261103/atlas-interface.json`，先给PM发消息。与即将产出的 `docs/art/2026-11-03-county-region-atlas/planning/`、`registration/` 读接口协作，不修改它们。
3. A-v3可纳入隔离预览的真实候选，但精确配准数据尚在制作，不把道路/骑手错位标成已完成；没有可信对应时仅把原生整区作为预览展示，路线层按已记录状态处理。不要任意单点平移或扭曲美术来伪造原路精确一致。
4. 区域图片包/配准/接缝由PM依次提供。先让显示层适配一个A，再实际接入B及更多，必要构建可做；尽量等真实整区包准备后集中构建，避免每次重编。

## 交付/验证权限

报告区分源码、资源接入、构建、部署和用户体验。用户未说阶段完成，不tests/typecheck/回归/渲染矩阵/浏览器自动化；必要交付构建可做，静态文件盘点与SHA记录可做。不开正式游戏，不读写存档，不commit/push/发布，不清理任何未提交工作。不要自行生图，PM统一内置imagegen。完成当前可做实现后向PM `bb thread tell thr_7w55f3h66f --message-file ...` 报告具体文件/接口/阻塞，勿空等；有独立可推进项继续。你的会话将持久保留，不新增重复开发。
