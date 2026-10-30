# 第一阶段收尾：应用重启接续记录

日期2026-10-28，Asia/Shanghai。用户要求先完成第一阶段，完成后一起验收：提供测试用例，用户验收功能并给优化建议。当前只执行第一阶段收尾，不进入第二阶段或广告SDK。

## 近期决定

- 用户已将Work/工作偏好里的「使用本地浏览器」由默认改为「开启」，并回复已开启；CUA重新连接和js_reset后仍报 Local browser use is disabled in Work settings。用户建议退出应用重新打开，以重新加载设置。本文件在退出前保存。
- 需要用户手动退出当前ChatGPT/Codex应用再重开，不能用绕过CUA的方式控制本应用，也不能伪称设置已生效。
- 重开后第一步CUA getState核对浏览器可用，再继续收尾任务。原用户游戏入口http://localhost:4179/，python3服务器PID69946，若重启后仍活着则复用；不清空该源的游戏存档。
- 技术基线是local-dispatch-v1：默认50m、缩放30–100m、10普通单滚动列表、真实道路全程≤10km、骑手连续取送、79项自动检查通过。图指纹/旧存档保护保留。

## 已落盘的新工作

1. `docs/superpowers/plans/2026-10-28-stage-one-handoff.md`：本轮收尾计划。
2. `delivery-game/scripts/fetch-map-details.py`：公开OSM建筑/水绿场景下载，4×4分区、最多2并发，完整XML+无remark才写入，已完整文件校验哈希后复用。默认https://overpass-api.de/api/interpreter；VK接口失败未纳入数据。系统curl正常校验证书；捆绑Python证书链失败，未关闭TLS校验。
3. `delivery-game/data/map-sample/details/tile-01.osm/.json/.query.txt` 已成功，820ways、8809nodes、884679字节。其余下载曾在exec会话49955中运行，重启后先检查文件，不假设后台下载仍存在。完整文件可复用，`python3 delivery-game/scripts/fetch-map-details.py`继续缺块；失败不影响已有片。
4. `delivery-game/scripts/import-map-details.py`：仅合并buildings/areas/waterways，不改nodes/roads/pois/labels，包含真实多边形/线裁剪与去重，拒绝缺节点或服务器remark数据；命令行基底/输出/源文件通配。
5. `delivery-game/tests/test_map_details.py`：4项导入行为检查，先失败后实现，目前通过。尚未将该Python检查加到npm test。脚本仅实现，尚未向运行city.json导入新数据。
6. 子代理`/root/stage_one_acceptance`独立写`docs/acceptance/2026-10-28-stage-one.md`及`delivery-game/acceptance/index.html`。两份文件已完整落盘（Markdown26452字节、HTML46084字节），接续时先读，勿覆盖或重做；脚本语法和最终界面验证待进行。验收预计24项，普通/条件/真机分开，localStorage仅自己的记录，支持反馈导出。验收新档入口约定http://localhost:4188/，根代理需启动独立HTTP服务；HTML构建后复制至build/map-sample/acceptance/index.html。

## 接下来要完成

- 取得缺失OSM细节分区，必要时合理缩小查询或重试；验证来源/许可/哈希。不能用虚构建筑伪装成真实。
- 运行原import-map-sample到临时base，再运行import-map-details到临时输出，确认nodes/roads/pois/labels与当前city.json完全一致，旧有效存档仍恢复，才替换运行city.json。保存覆盖统计与体量。当前只有旧697建筑/57areas/6waterways，外围未补齐。
- 按需要将farmland/residential新kind绘制为浅色地块；保持道路/骑手易读与有界600m细节缓存，不做无关重构。
- 完成验收HTML/Markdown并检查，给用户独立新档入口、正常存档入口和验收表链接；不得替用户勾通过。
- 补完实测：浏览器连续第二单送达、缩放按钮30/100m、重载50m定位真实骑手位置、10单滚动、长屏、最终error日志。此前部分证据见docs/reviews/local-dispatch，别重复宣称未完成项已通过。
- 运行完整自动检查/类型/Cocos构建，独立审查必要改动，保存构建哈希、截图、恢复快照，更新阶段状态为待用户验收。手机真机首屏/帧率/双指与系统后台由用户验收，未测不可伪填。

## 保护与恢复

已有`.merge-backups/2026-10-28/county-stage-one-v1.zip`、`local-dispatch-v1.zip`完整恢复点；本轮还会保存stage-one-handoff-wip.zip作为重启检查点。当前分支codex/food-delivery，很多源码原本未提交，不能reset/clean或混入旧躲避游戏。不要修改原Main.scene与DeliverySession.ts；保护哈希分别4b243a4bfdd6f6cdaf5db358c0405dd9ea4b971351028bee1b3aee84eb368166、a2ba218af00e1075cec9b9cf63528e09dcfbe6f56b8e19441dce0f9f6aac6f1c。

重启检查点已有完整细节分区：tile-00.osm, tile-01.osm, tile-02.osm, tile-03.osm, tile-04.osm。下载已请求停止，重启后重跑下载器复用完整片。
