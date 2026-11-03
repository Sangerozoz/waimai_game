# 五区ABCDN数据更新交付（2026-11-03 20:31）

已实际将 `docs/art/2026-11-03-county-region-atlas/runtime-package-abcdn/` 接入 `delivery-game/county-region-project/runtime-data/`，并将准备后的数据原样复制到独立 `delivery-game/build/map-sample/county-region/assets/`。

- 本次5整区为A-v3/B-v4/N2/C-v3/D-v4，另含NE/SW独立骑手，共7张原图，拷入SHA全部匹配。5区PM批准的ready、全部registration/内部routeCoverage/ownership逐值原样保留，23条源道路fullnodes原样沿包；未扩张外端可信范围。
- 源atlas SHA：`2a1cbf583bb801ba2a8b744d401be14713c4b5e9fd1eed207d68f384cb89b386`。
- 运行atlas SHA：`dea955ff9f9e4ff006f4ffcee4fb13ad3388b3677b1c3487111b321c1c1723a0`。差异仅为已授权 `rider.initialMap=[-1596.7,96.27]`、`initialDirection=ne`，源包未改；integration-record保留source SHA与override。没有自动配送/演示路线，静态骑手仍由既有可信走廊/蓝框/原路检查放行，运行结果未观察。
- 相机沿包focusMap `[-1535,80]`、viewWidthUnits `450`。路缘重影、外端未可信范围及未制作B-N邻接单元均保留真实状态，无复制填空，不称全县完成或像素无缝。
- 更新前已完整备份ABN静态入口和runtime-data至 `delivery-game/county-region-project/deployment-backups/abn-before-abcdn-20261103-203147/`；此前AB/ABN证据保留。旧high-camera入口未写。
- 本次没有重编。静态SHA盘点确认既有源码、编译JS/HTML/CSS不变，部署runtime文件SHA与准备包一致。编译产物仍来自18:55:54 Finished构建。源city SHA仍为 `536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`。
- 全部源包、源码、override、运行数据和部署SHA见 `docs/reviews/county-region-20261103/abcdn-deployment-record.json`。
- 未做tests/typecheck/回归、HTTP/浏览器/游戏或存档访问，未碰Git。此次只称数据接入/静态部署更新，不声称运行实显或体验验收。成果提交由PM统一处理。
