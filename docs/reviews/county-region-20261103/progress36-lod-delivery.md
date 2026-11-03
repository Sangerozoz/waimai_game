# 36区＋概览LOD静态交付

已接入 `docs/art/2026-11-03-county-region-atlas/runtime-package-progress36/`，完成一次必要Cocos构建并更新独立 `delivery-game/build/map-sample/county-region/`。5 ready＋31 preview-only和静态骑手[-1596.7,96.27]/ne保持；PM调整的preview排序沿包保留，五区ready条目逐值不变。原路fullnodes逐值核对，38张原生PNG SHA匹配，未修美术或更改原图字节。

- 派生概览：`delivery-game/county-region-project/runtime-data/derived/overview.png`，2048×1871 RGBA，SHA `da0a79446052f5ac2c58a9f1d19ea9f253abbe705f1461224ece3212e3243f35`。由全部36张真实整区原图按统一投影/比例、sortOrder、ownership合成，未制作处透明。只属显示派生纹理，不进入regions或任何可信路线范围。
- 远景完整概览单独显示；近景视口含缓冲所需区数≤24且全部加载齐后，整组切换到原图。超过24或加载未齐/失败仍显示完整概览；两层互斥，不将局部原图压在扁平概览上，不靠无限提高原图常驻量。原生常驻＋在途≤24、并发≤2；概览单张最大默认2048，脚本可设64..4096，未来可扩展分页提升大图细节。
- 每源id/file/SHA/anchor/统一比例/sortOrder/ownership及投影bounds：`runtime-data/derived/overview-record.json`；生成器SHA/Pillow版本同存。接口更新：`docs/reviews/county-region-20261103/atlas-interface.json`。源atlas SHA及runtime override链路见integration-record与本次部署记录。
- 20区完整备份：`delivery-game/county-region-project/deployment-backups/progress20-before-progress36-lod-20261103-234550/`；旧入口和历史证据保留。
- 必要构建日志：`delivery-game/county-region-project/build-evidence/build-20261103-234632.log`，23:46:41 Finished，Cocos36/包装0，保留build-script SIGTERM诊断。完整源/LOD/runtime/部署SHA：`docs/reviews/county-region-20261103/progress36-deployment-record.json`。
- 未tests/typecheck/回归/HTTP/浏览器/游戏/存档/Git；只记录源码实现、派生打包、Finished和静态部署，不称运行切换/画面/骑手已经验收。概览缩采样边缘与浏览器原图裁切可能有细小差异，未制作区域与明显遮挡仍待整县后处理，整县未完成。

可重复准备与构建（仅在获准需要构建时执行第二步）：

```sh
python3 delivery-game/county-region-project/tools/prepare-runtime.py docs/art/2026-11-03-county-region-atlas/runtime-package-progress36 --static-rider-map -1596.7 96.27 --static-rider-direction ne --overview-max-size 2048
delivery-game/scripts/build-county-region.sh --deploy
```

今后>24区数据包经prepare-runtime会自动从全包重建概览和证据，无源码变化时只复制runtime-data至独立入口assets，不重编。
