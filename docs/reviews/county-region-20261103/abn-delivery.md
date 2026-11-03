# ABN 数据更新交付（2026-11-03）

已实际接入 `docs/art/2026-11-03-county-region-atlas/runtime-package-abn/`，将准备后的runtime-data原样复制至独立 `delivery-game/build/map-sample/county-region/assets/`。不重编源码，保留18:55:54的既有编译产物。本次为静态文件交付，没有请求页面或实际运行展示。

- 3整区：A-v3、B-v4、北A相邻N2（`R-+00--01-v2.png`）；加NE/SW独立骑手共5张原生图，全部SHA与PM包匹配。PM的3区ready状态、全部registration/evidence/实测点/残差、自然ownership原样保留；A/B既有routeCoverage逐值不变。未自行纳入C/D或提升其他候选状态。
- 源atlas SHA：`a198bc113267cc32dd3f9e862e135cb5bf1977bf6767bdef5aa460d3d03ccaa0`。
- runtime atlas SHA：`c3824cc40935539d0098f171376f0c152c39a6ff6d8e6547595a54a4b79b8757`；差异仅为已授权静态骑手override `[-1596.7,96.27] / ne`，记录于runtime-data/integration-record.json。骑手仍按原路/蓝框/内部可信走廊门判断，不自动配送、不添加演示路线。
- 相机沿PM包：focusMap `[-1535,30]`、viewWidthUnits `390`。B-N暗三角为未制作邻接单元，继续留空，没有复制图填充；不称全县完成或像素无缝。
- 上次完整静态部署和runtime-data先备份至 `delivery-game/county-region-project/deployment-backups/ab-before-abn-20261103-202537/`；旧high-camera-city及v1入口未写，历史交付证据保留。
- 本次文件盘点确认：PM包5图SHA、所有部署runtime文件SHA一致；已有源码与编译JS/HTML/CSS SHA不变。源city SHA仍为 `536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`。
- 完整包/运行数据/部署清单及SHA：`docs/reviews/county-region-20261103/abn-deployment-record.json`。最新记录覆盖此前AB-only当前状态，前次构建证据仍作为编译产物来源。
- 未执行构建、tests/typecheck/回归、HTTP/浏览器/游戏、存档访问或Git写入。静态骑手是否实际显示及运行reason未观察，不能代填用户体验验收；Git进度提交由PM处理。
