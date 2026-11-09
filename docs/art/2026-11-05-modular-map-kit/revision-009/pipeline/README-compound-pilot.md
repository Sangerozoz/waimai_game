# 受限复合场景入口

只支持父批准a5564388...的009compound-source0125-court：源125、两个模块、五面。当前consumer为006/integration/compound_import.py，复用batch_prepare.Context的原生图框/PPU/门坐标校验，复用同一neighborhood_export与renderer。旧batch_prepare.py明确拒绝scene-compound-static-v1并指向独立入口，不删除旧防重或扁平化scene。

```sh
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py preflight
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py negative-probes
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py apply
```

preflight和负例读取当前发布数据、在内存中验证；负例不是生产包/游戏测试，只写自己的证据报告。apply再次预检，预先完整导出到006/integration/compound-pilot/transaction-stage，验证两楼/五面和旧161/501，再以带备份/日志的逐文件原子替换发布；异常恢复原所有目标文件，未完成日志须先recover。事务stage只是短期导出证据，不是新工程或服务。

source_accounting仅临时归一化旧sourceIndex/sourcePolygonMap与数组记录；已发布明确sceneId必须在compoundScenes注册且moduleIds齐全。同一显式scene模块共享源只计一次，跨scene/旧绑定/预留继续拒绝。旧81记录逐值保留。pilot发布后应uniqueSourceCount82/sourceOwningSceneCount82/sourceBoundModuleCount83，而不是len(visualReplacements)当源数。静态实例163/地面506是另一个计数维度，不是经营地址。

不自动支持其他复合scene或批量生产；新候选/新SHA/新基线需父批准并独立重核。B12/B13/T05准入不扩，原city/POI/nav不改。
