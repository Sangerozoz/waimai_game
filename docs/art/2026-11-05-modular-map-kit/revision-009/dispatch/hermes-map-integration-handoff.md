# 地图接入Hermes接续：通道纠正后的唯一常用作者

用户明确：新开/后续执行会话使用Hermes → OpenAI API → GPT，不用Codex或独立Codex CLI。你应是`acp-hermes-agent`、`openai-api:gpt-6.1-sol`，不要自行改回Codex/OAuth、模型或账号配置。禁止GPT-6-astra。旧接入作者thr_8vs8ndqxxa已停止、自动重试队列清空，只保留来源；Provider无法原地替换，所以这次必要单会话迁移。今后地图接入/素材包优先复用你，不每个小修新会话。不fork/不读旧长聊天，不派子Agent。

## 目标与已完成状态
先地图资产包＋可编辑雏形，位置/大小/放置后续用户手调；原25拼图同时借用楼群关系、体量比例、城乡疏密，不只抽楼型。不要恢复逐场景精摆/几何95项审计，不以完整庭院卡交付。唯地图，产品业务/UI/数值不属于本线。
工程根：/Users/sanger/Documents/ChatGPT/taptap 2
kit根：docs/art/2026-11-05-modular-map-kit/
先读AGENTS最新几条、kit/BRIEF.md、delivery-kit/reference25/README.md。

现有物件不要重做：
- v1 ZIP已交并父核CRC/34唯一PNG，<=280，原主图实际163静态/506面；delivery-kit/v1/user-layout.tmj可能被用户手调，一律不写不重置。
- 旧Codex两次502后父已直接做完新delivery-kit/reference25/参考稿：reference-layout.tmj、index.html、cocos-reference25.jpg、actual-runtime.json、layout-changes.json。参考TR-33的大市场+小住宅前排+高低后排；实际Cocos读回172视觉节点/32引用PNG/nodeScale1，共享Frame。白铺地/留白仍粗、高楼接地未完善，非全县/精密配准/用户验收。已有截图不用再跑渲染矩阵。
- P11花箱/P12候车棚各一次真实原生已交，父核工具源逐字节/运行SHA并开图，已加入此新参考稿库和模板；metadata目录合计36图（含原有候选）。PNG长边<=280，母版不进包，来源保留。不要新生图或返工。
- delivery-kit/map-reference25-addon.zip已打包，需相邻解压的v1，刻意不重复打引擎；导出包装器会按需从v1复制壳。不得覆盖已有用户布局。工程中交互预览已在4186既有服务真正显示，不开新服务/暴露端口。

## 本次只做未完成的收尾，完成后保持此会话供后续接续
父已实际将v1+附件解包到：/Users/sanger/.hermes/cache/scratch/map-reference25-unpack-g077_u44/
已在其中首次执行`python3 export_reference_preview.py --map reference-layout.tmj --output preview-check`退出0，172实例/32PNG，原输入不写、道路数组保持。脚本产物在该临时目录，父后面的检查脚本只因算原city相对路径少一级报FileNotFound，并非导出错误。不要再重复地图制作/重建用户图。

只补正式交付记录`delivery-kit/reference25-delivery-verification.json`：读取实际已解包输出、真实runtime证据、ZIPCRC/文件引用/32PNG<=280、素材分类合计36且小物11；核原路数组和固定主源SHA、用户布局不写；记录ZIP真实字节/SHA、相邻v1依赖、GUI未拖/游戏未测/未用户验收。可以用一次便宜脚本完成，不逐源/负例/多轮截图。若现有ZIP/目录缺或引用确实坏，限定修附件元数据/工具，不动源地图或用户图；有阻塞如实报。

原city确切路径：/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/resources/map-sample/city.json，SHA536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20。
原scene：revision-006/viewer/assets/scene-layout.json，SHA237252cf5858346686c707335f1a323c0d14261631ec6262b6d403bbfd94b5cc。
原Tiled：revision-006/integration/neighborhood.tmj，SHA26eb9baad3f38a13570c5c23d4cadd5a5f4f4ef29f1c5a174436d3c566fd99e8。
v1 ZIP SHA5630062301297e76203fd3800833341603ad56d512c6d611518cffd99fe820da。
用户布局若和之前记录有差异，按用户手调保护，不恢复旧版。metadata/provenance保真实Codex原生产出处，不能把历史伪标为Hermes。

## 写集与权限
仅kit/delivery-kit/reference25/和新增reference25-delivery-verification.json；父本轮不再改此写集。v1/主scene/TMJ/原city/原生/25图/规划/其他产品线只读。只必要打包/导出可用性核对，不游戏tests/typecheck/回归/FPS、存档、提交、模型/账号/全局权限配置。只可本工作区必要编辑，敏感路径仍须授权；不要dont_ask/绕过审批。

交短报告：确切交付记录、可编辑稿/ZIP/实际截图路径，验证了什么、仍粗什么。不要复述整个历史或假称全县完成；然后等待下一份有界地图接续。
