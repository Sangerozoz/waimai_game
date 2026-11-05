# 首组视角修订 · 当前交付

当前审阅入口 [前后对比](index.html)，原生四向 B01-F00-v3 / F90-v2 / F180-v2 / F270-v4，树复用旧 pilot/T01-v1 原字节，L01/L02保留。增加立面可见度是用户最新反馈，未将此图机位标为与道路投影精确一致。

- 来源与完整提示词：generation-records.json及 *prompt.txt；旧对话已生成四向，前三向已归档，第四向v2从原生输出恢复。v2/v3带灰光晕拒绝接入，v4重新从F00生成，仍有白彩杂边。
- Tiled当前文件：integration/revision.tmj。integration/pilot.tmj为先前候选，保留未覆盖。原41对象probe和上轮kit/integration/pilot均未改。
- 运行数据：integration/runtime/assets，派生viewer已同步至viewer/；可通过[4186独立入口](https://sanger--4186.getbb.app/revision-001/viewer/)访问。viewer不进Git，沿用原隔离引擎壳，未重新构建。本轮只核验HTTP、文件与坐标，没有新版本浏览器实显验收。
- 静态记录：integration/static-verification.json与source-integrity.json。7主对象、30隐藏组合实例，原生PNG副本SHA相同，锚点往返误差0。此结果不证明画风、机位、遮挡或游戏通过。
- integration/runtime与viewer是可重建导出，本次新导出替换了既有同名JSON，没有旧JSON备份；原Tiled地图和原生素材保留，可由对应地图重导。此项不等同覆盖用户地图。

## 仍需检查

白色和彩色轮廓边缘仍在；四向独立生图的机位与形体一致性未通过；新图与原路投影有差异。位置与缩放是人工视觉候选而非实测物理标定，未拉伸/旋转或迁就素材改原路。旧骑手沿用放大比例。手动层级同步、人工修改保护与两块不同完整街区仍未完成。先检查当前一组视角与组合，不能据此扩量或宣称绿框可交付。

## 接续实际观察

地图任务3（thr_girg7cdd6q）已实际打开4186对比页及Cocos，显示7对象，建筑相对旧放大骑手明显偏小，比例不通过。该对话返回的临时截图在本轮归档时已不可读取，未归档截图，不将其作为已有本地证据。原4185出现空响应，现用[4186新旧对比](https://sanger--4186.getbb.app/revision-001/)。下一轮比例诊断由该对话独占revision-002，不重复生图、不动此版本。
