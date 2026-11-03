# 二维街角六项审图修订

2026-11-03，用户在真实小样上明确六项问题，本目录保留新候选PNG/完整prompt/源路径/SHA/锚点与临街朝向。原已认可首页为视觉依据，旧engine-v3是修改前实际画面，不能标成合格母版。

规格：`docs/superpowers/specs/2026-11-03-modular-city-six-point-revision-design.md`；计划：`docs/superpowers/plans/2026-11-03-modular-city-six-point-revision.md`。

## 当前状态

**最新事实覆盖下方故障历史：** 内置生图已恢复，原缺7方向v2已全部生成并原生归档；现19张PNG，含9方向v1历史、8方向v2候选和2地表材质，源/完整prompt/SHA见generation-records.json与metadata/source-map.json。未生成最终runtime清单、未集成部署或实际查看新运行画面。用户正在讨论更高俯角与道路可见通道，故保留30°候选作来源，不自动覆盖预览；补图自动续办automation已删除，固定开发已通知。最新状态见metadata/work-state.json及地图方法目录high-camera-discussion.md。下文12图/持续失败/定时续办是本次恢复前历史。

**本轮停靠事实：** 显示层源码及独立编译产物已交，尚未集成/部署。Cocos日志Finished但退出36，SIGTERM/计时/网络诊断保留，不能称全检查通过；工程证据在`delivery-game/modular-city-project/revision-build-evidence/`，完整工程说明在`docs/reviews/modular-city-20261103/implementation-report.md`。旧4181部署68文件前后SHA一致，仍是修改前版本。12张原生图已归档；剩余7张机位v2连续连接失败，无新产物。

用户明确选择继续内置生图、服务恢复后补齐，不切API/CLI。已创建本聊天每15分钟自动续办“补齐街角建筑机位”（ID `automation`），故障不变时保持安静，恢复后补图/接入，完成后停用；接续事实以`metadata/work-state.json`为准。不要把未完成素材/集成写成可见交付。

- 固定开发MC-REV1-1103已接单，正在修改地面/树池/骑手/投影显示层。
- 新图扩充为三类楼各左右正门两个方向＋3张隐藏临街面的背面观察图＋入口砖/种植土草。`prompts/jobs.json`、`prompts/rear-jobs.json`保存完整提示词，使用内置image_gen；没有CLI/API替代、未脚本翻转/旋转/抠图。
- 新生成结果、标注与接入状态按实际到件更新；本段不是已产图/已接入声明。
- 不扩全县、不恢复3D、不改玩法/原地图/存档、不自动测试。Work设置禁用本地浏览器自动化，未看到新运行画面时明确如实报告。

## 用户原话

1. 建筑美观度不够
2. 地面贴图单一，不符合实际情况
3. 树木只有树本土，缺少树种植区域的土，草，围栏等。现在的树很生硬的放在地上
4. 建筑角度，建筑正面朝向有问题，比如最上方那个间距正门朝左，但是道路在他右侧，他等于把侧面靠着马路。
5. 骑手模型太小，至少要放大2倍。
6. 缺少光影，建筑，物体有遮挡关系但没有阴影

## 生产接口

首批11图及B12-E-v2机位修正样张已实际原生归档，来源/完整prompt/尺寸/SHA见`generation-records.json`。首批楼图实际俯角偏浅，留档但不因产图即选入；B12-E-v2已用原B01作机位参考重绘，其余选用方向的机位修订正在补齐。一次7图修订批次因生图连接失败没有产物，已保留错误与重试记录；不切换CLI/API。此状态不等于新图已完整接入或用户验收。

`revision-manifest.json`沿schemaVersion:1，assets字段兼容原Asset；楼体新增`frontage:{screenSide:'left'|'right',entranceUV:[u,v]}`与`heightMeters`、`groundPolygon`。UV原点为原图左上。B11餐饮、B12玻璃商办、B13商住；E门在画面右面、W门在左面。S03-entry/S04-soil为地表。新PNG原尺寸/比例保留，所有角点与高度是候选标注，不能用prompt代替实际视角判断。
