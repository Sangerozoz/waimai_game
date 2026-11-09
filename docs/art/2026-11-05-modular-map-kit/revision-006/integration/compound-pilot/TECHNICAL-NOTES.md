# 源125：受限一场景两模块已实际入图

[同一viewer：复合院落与市场](http://127.0.0.1:4186/revision-006/viewer/?view=compound-market) · [实际全景](cocos-compound-market.jpg) · [门路细节](cocos-compound-detail.jpg)

旧市场、两新楼、共享院落/真门路及原道路已在同一Cocos画面中可见；两图是实际页面截图直接复制，未拼贴/生图。细节镜头自然裁到市场一角，全景保留整市场与新两楼。仅本scene比较，不是批量或美术/导航/用户/全县验收。

## 实际增量和保护

- 基线实际161静态/501面/81源，不回放producer的156旧快照。新增**源1、scene1、模块2、地面5**，整体成立后追加。当前163静态/506面。
- 当前**源集合并集82、源绑定scene所有者82、源绑定模块83**。原81个单模块来源只在内存视作legacy owners；明确compoundScenes注册只有本次1scene，两个模块都引用125仅计一个源。不是83源/经营地址，也不把163静态实例算作绑定楼数。
- 原161全部block字段、world frame、固定排序值、实际UI及相对顺序，原501面、所有Tiled既有层/对象/tiles/offset/index，旧镜头、D路径/source/POI/nav和市场生活层全部逐值保持。旧81个sourceIndex单数/数组记录原字段不回写。B12/B13/T05有限状态不扩，T04等hold不解除。
- 可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。新增独立group保留原sceneId/moduleIds/ground归属，不修复或重命名原ID。

## 可执行consumer与事务

入口[compound_import.py](../compound_import.py)，所有权与计数[compound_contract.py](../../../revision-009/pipeline/compound_contract.py)，形状文档[compound-schema.json](../../../revision-009/pipeline/compound-schema.json)。复用batch_prepare.Context的真实PPU/UV/图框/门坐标校验与现有neighborhood_export，不重写renderer；旧batch_prepare.py明确拒绝compound schema并指向本受限入口，不删除旧防重、不扁平化scene。

```sh
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py preflight
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py negative-probes
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py apply
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/verify_compound_pilot.py
```

以上已实际执行。现在重复apply会拒绝；preflight/negative-probes只针对原未导入基线，导入后拒绝重跑负例，防止把重复apply异常冒称schema证据。后续读取已合法的两模块会识别为同一个显式scene；source_accounting已对当前发布场景再次实际计算。

写入前检查受支持schema、scene/module/ground双向归属、源polygon/SHA、每源唯一scene、ID与旧绑定/预留排重、单次比例/脚线/真门和全局障碍；只对本source125载体豁免，同scene模块不互豁免。two modules/five surfaces任何一项失败均整scene拒绝，没删成单模块。

先在transaction-stage导出同一运行壳的临时副本，验证完整163/506/82与旧161/501，再用带before备份及日志的逐文件原子替换发布，异常恢复全部目标；不是声称文件系统具备跨文件原子操作，发布中断可运行`compound_import.py recover`按journal恢复。stage为导出证据，不是新工程/服务。transaction-journal状态committed，两模块/五面一起提交，原始source/候选不写。

第一次预导出发现旧north_region.patch每次重复插入已安装镜头筛选片段，被renderer字节不变门禁拦在发布前；live161/501 SHA保持。已只加已存在则跳过的判断，**当前renderer字节未改**；原失败stage/aborted-stage-evidence保留。现在重复export连scene/manifest/TMJ/HTML/renderer均字节稳定。

## 真实consumer负例（非游戏测试）

consumer-negative-preflight.json记录实际同一个preflight函数，对明确内存副本执行：重复模块ID、重复地面ID、缺module.sceneId、缺scene、scene漏列模块/孤儿、scene列不存在模块、跨scene复用源、旧数组源260、旧单数源630、旧绑定/预留1731冲突、独立预留114门禁、未知schema，共12类均拒绝。独立预留门禁的baseline仅在临时内存移除绑定以隔离该规则，绝未改生产绑定。每例失败前后主TMJ/scene/manifest SHA一致。

导入后又实际执行一次`apply`，重复应用被拒且163/506主文件SHA不变，证据duplicate-apply-rejection.json。不是调用审查模型或只写一组假结果；独审负例与本consumer证据分开。

## 脚线、单次比例与实际画面

B05@0.9、B01@1，原生PPU/UV不改；输入worldSize/anchor/footprint/entry已最终值，运行nodeScale全1，没有二乘0.9。每模块sceneId/sourceNativeSHA/真门/脚线均在Tiled属性、block和源绑定中可追溯。B01沿原人工[198,910]/[438,1229]/[1055,931]/[815,612]四点、25px候选不确定性，B05用原校准点与隐后角推断，绝非整图框充当精密脚线。母版/实际tool SHA与运行图SHA逐字节复核，native-foot-door-scale-check.json保留。

|模块|单次标量|实际world frame|实际UI像素（32px/单位）|实际nodeXY|静态值|
|---|---|---|---|---|---|
|B05|0.9|9.162777204×10.486393036|293.208871×335.564577|[227.8259344123397, -5744.888343066962]|128.888888889|
|B01|1|7.936234073×9.940515158|253.959490×318.096485|[-166.53612464825343, -5825.789208444775]|128.944444444|

完整原路605760963-0四节点数组/sourceNodeIds/width5/direction1逐值核原city；旧road字典不覆盖。当前95路/619完整节点引用保持，绘制只有限clip。两门各自接原路肩，未把门强压原POI或增加经营地址。

两模块实体间4.691031m，互相门路距对方实体最小4.445288m。B05距旧0587门路1.312391m、距市场P03脚点11.043372m；其屋顶在图像上遮了后方旧步道短段，实体脚线未侵入，实际未见市场主入口堵塞。这是可见残差，不是放宽地脚/误差无限许可。新两楼整sprite框均未叠旧sprite框，旧rank固定，新值插在128～129间。

5面按shared-court基底→有限garden→shared-walk→两条真门路排序，原路最后画。四块铺地连通，种植面仅邻接共享院、不盖门路/连接；G02是已有受控种植色块，不冒充新原生土纹。原source125几何保留：脚线有8.021㎡/13.400㎡外伸已独审，consumer再次核所有他源/空地，约19.47%源面积被新脚线覆盖是美术重组，非原楼等形重建，更非扩大经营土地所有权。

本consumer重新对最新161实体/501面（含市场五件脚点及8处新改面）、3524原source（仅125豁免）、9970原路、492水道/水polygon、蓝边、POI和同scene两模块/面全量复核。bbox只作距离下界剪枝。geometry-preflight.json逐件距离与自家首0.6m门槛有限例外保留；0.6m后自身脚线≥0.05m，其他实体不豁免。

## 节点、缓存和稳定SHA

真实__mapPreviewOrder/UI/Frame读回：163静态＋D/影子共165项，全部坐标/尺寸/scale/order核导出；旧161 UI相同。new-two-runtime-node-frame-check.json给新模块宽高/坐标、Frame index/file/SHA。最大位置浮点差约0.000001340投影像素。

运行仍30张≤280唯一PNG，2,425,880字节，新增图片0；实际30 images/28 nativeFrames/2 canvasFrames，重复file+SHA共享image/Frame。原生/25图/全城快照未进包。全景和细节各只激活一块≤2048有限地面；全景2048×1817、15面/1原路，不常驻新县图。未测FPS/实际内存。

736个只读输入/原生/规划/审查文件SHA保持，原city/source业务未改。详细验证：[final-verification.json](final-verification.json)。

- parentOriginalSHA256：`a5564388f2efb4afc55c8baa50e0f0607b1d0484ded6c2b05b6cc9abda6edb27`
- derivedSHA256：`bd304158193244a7e7d3c62247c318415c01fa503ebae0cfcd6eb2075def3896`
- baselineSceneSHA256：`e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7`
- baselineTiledSHA256：`5a4ee4e32ca61f88c81d97161469fa558fdfa75d1f8051ffaeef7c03badfee5c`
- finalSceneSHA256：`237252cf5858346686c707335f1a323c0d14261631ec6262b6d403bbfd94b5cc`
- finalTiledSHA256：`26eb9baad3f38a13570c5c23d4cadd5a5f4f4ef29f1c5a174436d3c566fd99e8`
- sourceCitySHA256：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

当前仍有B01重复、院内种植色块空白、少量软边和素材轴与原路角差；没有为了这些残差重生/变形或添新物。没有游戏tests/typecheck/回归/渲染矩阵/FPS/存档/业务/UI/经济/提交、新Agent/工程/服务。这是一次实际局部运行比较，未用户/导航/全县验收，也不授权后续全量多模块生产。
