# Tiled → 现有 Cocos 小包探针

仅隔离工具验证，不是正式地图、美术验收或阶段游戏测试。原素材、Cocos源码、正式地图与存档未改。`probe.tmj` 是当前权威布局；`initial-map-snapshot.json` 只供比较，不能回盖手动文件。

从仓库根目录运行：

```sh
python3 docs/research/2026-11-05-map-production/tiled-probe/bridge.py prepare
# 已准备好的包不能再次prepare，命令会拒绝覆盖。
# 在 Tiled 打开 probe.tmj，编辑/保存为原生JSON地图 .tmj。
python3 docs/research/2026-11-05-map-production/tiled-probe/bridge.py import
python3 docs/research/2026-11-05-map-production/tiled-probe/bridge.py check
python3 docs/research/2026-11-05-map-production/tiled-probe/test_bridge.py
```

`import`/`check` 默认读 `probe.tmj`、写 `runtime/assets/`。可指定 `--map other.tmj --output <本目录内隔离目录>`；素材路径保持相对 `assets/`，建议地图保存在本目录。仅输出已有 HighCameraCity 所需 JSON/PNG，不含替代HTML，也不自动启动Cocos或正式游戏。由主任务复制既有 HighCameraCity 构建到隔离服务，将该构建的 `assets` 子目录替换为本包 `runtime/assets`。必须保留构建JS/引擎并实际截图后才能判断显示。原构建不应被覆盖。

AI在手动保存后追加一盏独立灯，不重新生成布局：

```sh
python3 docs/research/2026-11-05-map-production/tiled-probe/bridge.py append --asset P01 --x -1595 --y 72 --id ai-added-lamp-01
python3 docs/research/2026-11-05-map-production/tiled-probe/bridge.py import
```

地图采用有限正交屏幕坐标，不是等距格网。投影沿用高机位 `axisX/axisY`、62.5°、原世界原点；编辑器每投影单位16px，屏幕原点 `[896,896]`。Tiled图片对象锚点明确为 `bottomleft`，接地点为 `x + anchorU*width, y - (1-anchorV)*height`，再反投影回原世界米坐标。尺寸由 `nativeSize/nativePixelsPerUnit*16*scale` 得到。GUI修改尺寸后以实际宽高为准，`scale` 属性由导入器更新；只接受正均匀缩放，拒绝平面旋转、镜像、非均匀拉伸。

持久ID、自定义 `assetId/orientationVariant/scale/manualLocked` 保存在每个对象。GUI复制会复制持久ID，导入器为重复ID分配新ID并回存地图；首次原对象保留ID。`manualLocked` 是增量工作流元数据，Tiled的实际编辑锁使用图层锁。AI追加只新增对象，不修改现有对象；删除以地图中的对象缺席为准，不从初始JSON补回。

现有 Cocos viewer 的 `blocks` 没有实例缩放字段，因此导入按实例生成 `kind:block` 清单条目，`nativePixelsPerUnit = 原值 / scale`，素材文件字节不变；布局每个实例记录来源资产、持久ID、缩放和锁定属性。独立树T02、灯P01复用旧模块素材的原接地锚点，其绘制相机不同于62.5°，仅验证可编辑单件，不能当高机位美术达标。庭院块内楼/树仍是整体，不能逐件编辑。

原路作为锁定图片层显示。PNG由标准库按原节点/宽度投影生成平色参考，非新道路素材；Cocos仍以原路数组和原地面材质绘制，图面颜色无需像素一致。运行包保留原骑手双向、原路段及相机。编辑器当前无骑手静态对象，骑手在实际Cocos中展示。

`source-integrity.json` 记录8张原素材的来源/SHA，复制字节不变；`runtime/import-report.json` 记录当前地图SHA、逐对象位置/缩放/坐标往返、相对初始删除ID和道路逐值比较。三项自动测试覆盖非底边接地点与非单位缩放、手动移动/删除后追加保持、真实适配器导入时复制ID规范化与删除保留。合成保存测试不等于GUI证据。

截至工具准备：三项自动测试通过，初始4个可编辑对象往返最大误差为浮点量级，原路数组相等。Tiled真实GUI编辑/重开、Cocos实际显示与二者逐对象对照仍由主任务采证；这些证据齐备前不宣称闭环通过。
