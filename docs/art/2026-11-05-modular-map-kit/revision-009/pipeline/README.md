# 009 批次准备器（数据阶段）

唯一写集为本目录。006 的现有 Cocos 引擎、57 静态实例、115 地面、全部镜头及 D 骑手内存演示均未修改。本轮没有新地图画面、没有运行游戏测试，也没有启动或暴露服务。未读取 009/planning 的在途方案。

## 已实际执行

`batch_prepare.py` 使用 Python 3 和既有 Pillow，只有 prepare / build-index / cache-window / audit，没有向主图 apply 或 init 命令。完整命令及退出结果见 execution-prepare.json、verification-results.json。以下命令在仓库根目录执行；prepare 已执行，重复同 batchId 或 batchIndex 会拒绝，不会重置输出。

```sh
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py prepare --batch-id demo-008-core --index 0 --plan docs/art/2026-11-05-modular-map-kit/revision-008/planning/next-district-plan.json --parent-sha a5412d65a4a9149051f98f43026b8d9e00d4b2e111d3c9366b998a2e4f230758 --demonstration-existing
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py prepare --batch-id demo-b07-wide --index 1 --plan docs/art/2026-11-05-modular-map-kit/revision-008/planning/b07-extension/b07-extension-plan.json --parent-sha 5e5c40725da225cb5fa45c129c0ab04951f76a9f562d519911f8acc44922fa76 --demonstration-existing
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py build-index --packages docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/demo-008-core docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/demo-b07-wide --output docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/batch-index.json
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py cache-window --package docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/batch-index.json --bounds -2395 -695 -2340 -625 --output docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/cache-core.json
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py cache-window --package docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/batch-index.json --bounds -2365 -795 -2305 -745 --previous docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/cache-core.json --output docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/cache-wide.json
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py audit --package docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/demo-008-core
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py audit --package docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/staging/demo-b07-wide
```

| staging包 | 转换实例 | 地面 | 完整原路记录 | 新增实例/面/路引用 | PNG引用 | 引用字节 |
|---|---:|---:|---:|---|---:|---:|
| demo-008-core | 13 | 17 | 23 | 0 / 0 / 0 | 10 | 787,728 |
| demo-b07-wide | 1 | 13 | 1 | 0 / 0 / 0 | 3 | 283,332 |

这些实例/地面已在57/115基线中，全部记为 already-present-identical。两包联合仅11张唯一PNG、879,180字节，长边最大280；材料图片跨包共享，3件P08共享同一SHA文件。staging/shared-assets 是按SHA存储的派生PNG，不包含原生母版、25区图或完整全城分析快照。

## 适配合同与产物

schema.json 记录输入形状；实际额外检查由脚本执行，不依赖 JSON Schema 库。输入可为008原有的扁平 buildings/fixtures/parkedVehicles/groundSurfaces/roads，或根 projection 加 districts 数组。每个实例必须给原始 persistentId、libraryAssetId、最终 anchorMap；建筑必须给真实原生 entryPixel 和 entryMap。root projection 必须与006完全相等。

- converted-plan.json 保留每件 sourceObject、地面原字段与原路完整节点；districtIndex 旁路保存 zoning/zone/landuse/landUse/site/selectedSite 等，不创建业务图或POI。原ID不改名。
- difference.json 单列父批准原文件SHA、当前基线scene/TMJ SHA、实际新增与已存在ID、逐件拒绝原因。转换文件自己的SHA在 prepare-report.json；不能用派生SHA冒充父批准原SHA。传入正确SHA仅验证字节，**父会话授权仍来自派发消息**，脚本不能自行批准新规划。
- increment.tmj 是可编辑的新增层集合，素材图路径指向共用CAS。此次为零差分，故两个新增对象层均为空；真实13件/1件转换证据在 converted-plan，完整旧图字节副本在 baseline-editable-map.tmj。副本仅用于保护对照，保留原相对资源路径；编辑现图仍用原006 TMJ，不能把此证据副本当新工程。
- baseline-scene.json、merged-scene-data.json 保留所有旧字段；本次两者语义完全相同。旧TMJ字节完全相同，含嵌套组偏移、位置、可见性、层/index顺序。新层从零组偏移开始，位置按现有896原点/16像素单位/底左锚点转换。之后手调位置与组偏移仍由现有006导出器处理；此工具不读取手调TMJ后覆盖主图。
- asset-manifest-additions.json 准备新增实例的现有manifest格式，世界框与裁边UV来自真实库，实例可以不同ID但按原file+SHA共享解码/Frame；本次无新增，数组为空。
- coordinate-report.json 给实际门点换算、完整道路计数、组偏移快照。基线25道路/178节点逐条与源city核对，008输入23/1条也逐值核nodes顺序、width、direction及可用sourceNodeIds。投影保持原值，仅未来绘制clip，不裁源节点。
- package-manifest.json 与 source-protection-before.json 支持 audit。protected-sources.json 保护本轮开始时全部006/integration与viewer及固定008输入/原city；最终核对见 verification-results.json 和 source-protection-final.json。

每件新实例从 asset-calibration 取真实原生PPU，禁止用运行manifest的 nativePixelsPerUnit=1 当标定。worldSizeUnits/anchorUV 必须与库的单一正缩放一致；B01/T01尺度锁定。旋转、镜像、冲突scaleX/scaleY、未知素材和hold逐件拒绝，无白盒回落；拒绝物的专属地面会剔除。无明确支持的对象局部offset/旋转拒绝，要求先给最终anchorMap。新实例ID与基线、同批、其他已暂存新增ID去重；已有ID发生位置/尺度变化拒绝。非示范模式不能重放旧实例。

门点原像素经真实PPU和既有投影逆变换，并与 entryMap 对照，同时检查原图该像素非全透明。B07必须为修正门11[704,609]。这不自动认证门的语义、隐藏脚线、导航或整块几何净空；规划候选的真实footprint/void仍原样保存供接入复看。V02用wheel-contact锚点，显式车身polygon必须落在原parkingSpace内，不推导交通AI。B09/B10/B11仍hold；其他有限比较资产的上下文与视觉门禁不因导出成功而解除。

## 区域引用与有限缓存候选

现有006真实代码按32投影像素/单位生成地面，单画布最长3072，三块画布常驻：3072×2725、3072×2725、2486×2205，合计22,224,030像素。仅RGBA8色面理论值88,896,120字节（约84.78MiB），若CPU canvas也保留则另有同量级。**这不是实测内存**，也不含深度、驱动、纹理、浏览器开销。

budget-policy.json 建议64×64m tile、2m裁切halo、名义12投影像素/单位、单边最多1536、最多8个resident（预取最多2），地面总像素最多8,388,608，RGBA8约32MiB，CPU canvas保留时另约32MiB。候选单tile1154×1024；8张名义尺寸略超预算时仅降低地面栅格密度，不改原生PPU、世界物体、镜头尺度。可见tile超过8直接报告blocked，不漏画可见tile。

实际联合索引6tile；core窗口4可见+2预取，7,090,176像素；wide窗口2可见+2预取，4,726,784像素，输出2个待evict引用。tile只是surface/object/road/assetKey引用；同对象跨tile索引不产生多份图片。原几何每包存一次，未来按clip渲染地面，不能生成跨县巨幅底图。

build-index 支持多个准备包按稳定tileID合并旁路引用；cache-window输出load/evict及需要acquire的共享PNG key（含铺地/道路材质）。本次索引覆盖这两份**已存在示范子集**，不是全57实例或全县的运行索引。未来实际接入需把已有区域引用与新批索引合并，按可见窗口连接当前006引擎；退出窗口应detach节点并释放无引用地面Frame/Texture，素材Frame按file+SHA做引用计数，不能每实例建纹理。

当前renderer未改，三画布机制仍在运行。尚未验证新分块渲染接缝、镜头切换、FPS或实际内存，也没有新显示/用户验收结论。

## 后续门禁

等待父会话派发新009稳定规划路径与明确批准SHA后，使用新batchId/index（从2开始）且不带 --demonstration-existing 准备真实差分。先核当前基线SHA；若主图已有合法增量，须更新适配基准而不能覆盖旧手调。逐件处理可用素材/门与地脚/蓝绿边界等具体证据，再由父授权接入同一006地图。此阶段的准备器不向主图写入，不能以文件落盘替代新街区真实Cocos截图。


## 已续接009第二批：当前74/164

上文57/115与两个008包是本准备阶段的历史示范。后续已获父批准，首批接到69/135、第二批再接到74/164，仍为同一006工程。准备器Context每次读取当前真实scene/TMJ/library，不冻结57；第二批expansion-009-round2/prepare-report已实际以69/135生成5/20差分，并按已缩world frame核单次0.9。实际接入另外9有限草地/门前面，见applied-009-round2.json及current-integration-reference.json。未来批必须以当前74/164及其后合法手调为准，不重放旧baseline文件。

历史staging包记录当时父SHA/派生SHA/基线SHA；原源保护audit在已授权主图接入后会发现基线文件变化，不能为过audit改写旧SHA或重置主图。准备包静态文件/CAS用package-manifest核对，接入后用applied记录和本批final-verification逐字段核原基线保护。


## 第三批数组源绑定：当前94/260

已按654ccb稳定父SHA，以实际74/164准备20源/20模块/96面并接到同一006，当前94/260。batch_prepare.py显式适配sourceIndices/sourcePolygonsMap，逐项核源city，保留root sourceMappings和多对多语义/sourceDataChanged=false，拒绝空源/长度不符/源polygon或SHA错配。比例仍核canonical×uniformScale一次，不按instance别名找canonical。applied-009-round3.json给实际尺寸/截图和保护证据；current-integration-reference.json指向当前基线。旧示范与先前准备包保留其历史SHA，不用其snapshot重置当前图。
