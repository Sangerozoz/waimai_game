# 模块化地图首组候选：恢复交付

2026-11-05，原执行对话 thr_f494gzcxn2 在交付末尾连续遇到 Account Pooler → ChatGPT 502，原生成与隔离接入文件仍在。根PM恢复交付，没有重新生图，也没有重置用户保存的41对象地图。

- 审阅入口：index.html（七张当前候选原图、Cocos入口、来源选型）。
- 已归档：商铺B01四向、T01树池一体树、L01/L02单灯；另保留两个已拒历史版本，总九张原生文件。完整提示词与SHA见pilot/及generation-records.json。
- 已有独立Tiled：integration/pilot.tmj，组合默认隐藏、对象可拆分。操作与导入说明见integration/README.md。
- 已有Cocos副本：viewer/，源自原隔离查看器。子对话日志记录曾实际显示，本轮仅核验HTTP和文件一致，不冒充新的浏览器验收。
- 本轮核验：九张原图SHA与记录相符、11资源×3副本SHA相符、Tiled图片路径存在、4185/viewer/返回200。见recovery-record.json；这些不是游戏测试。

## 当前缺陷与下一步

B01原生轮廓可见白边、彩色杂边；四方向独立生成，比例/形体/透视一致性未通过。树、灯与人物比例需要实看核查，旧骑手沿用放大尺度，不能作为比例基准。Tiled手动层级与人工修改保护尚未完成。先交当前一组检查，修明确缺陷后才扩余下建筑；不宣称两块完整街区或绿框已完成。

后续接续从本文件、BRIEF.md、generation-records.json和integration/README.md读取即可，勿重读旧长对话或重复生已归档素材。源city、25张认可原图、原41对象Tiled文件、业务/存档均未在此次恢复中写入。viewer为可重建部署副本，不纳入Git；Git保留原生图、Tiled及完整运行数据。
