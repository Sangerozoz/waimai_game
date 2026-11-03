# A/B首批实际包最终必要构建/静态部署

开发BB `thr_v8eu5ahv2e`，PM `thr_7w55f3h66f`；2026-11-03 18:55。

- 来源包：`docs/art/2026-11-03-county-region-atlas/runtime-package-ab/`。原生A-v3、B-v4、NE/SW独立骑手4图；只有PM显式ready的A/B，未纳入C/D或修改任何preview-only为ready。
- 原生A SHA：`4e266eb23f4d165828fabc6c51ab0334a5d38db02a411ac84008f52ea949911e`；B-v4 SHA：`779b49f6a307094e8a71b1503fc19566dfecee229534af4851bc71326ac2c9dd`。文件拷入时按PM包记录校验SHA，未编辑原图像素。
- A/B registration、routeCoverageMapPolygon和互补ownership全部原样接入；62.5°/45°、蓝框、原路保持。路线门使用独立可信走廊，不因边缘残差否定可用内路；原图按ownership显示。保留边缘漂移及纹理差异，不称全县/像素无缝。
- 静态骑手配置：独立runtime atlas增加 `rider.initialMap=[-1596.7,96.27]`、`initialDirection=ne`。不修改PM源包；integration-record记录源atlas SHA与本地override。启动时经过既有蓝框/ready走廊/原路中心线校验，再加载原生骑手并静态显示；拒绝则保留reason到getStatus().initialRiderStatus及状态栏，不另找位置，不自动配送。没有自动演示路线。
- 新增prepare-runtime参数 `--static-rider-map X Y --static-rider-direction ne`，将明确授权的静态初始位置作为可记录override；未配置则沿用默认无骑手。没有正式业务或存档连接。
- 必要构建：`delivery-game/scripts/build-county-region.sh --deploy` 正常macOS应用环境18:55:44运行，日志18:55:54显示Finished，Cocos原始36、包装0；保留build-script SIGTERM诊断。日志：`delivery-game/county-region-project/build-evidence/build-20261103-185544.log`。
- 静态部署：`delivery-game/build/map-sample/county-region/` 已复制新编译产物及真实A/B runtime-data，旧county-region已按脚本备份到工程deployment-backups。旧high-camera-city及v1、源city/正式业务/用户存档均未写，未碰Git索引、commit或push。
- 证据：同目录 `ab-final-deployment-record.json` 完整列出PM包SHA、runtime override、源码SHA与部署文件SHA。之前deployment-record和route-coverage-source-record保留为历史状态，本轮新记录覆盖“源码未构建/A-only”的当前状态。
- 未执行：HTTP请求、浏览器/页面操作、运行截图、tests/typecheck/回归/渲染矩阵或用户体验验收。因此只称包已接入、构建Finished、静态部署已复制；不称骑手已经实显或地图已游戏测试。

重做同一必要构建的数据准备命令：

```sh
python3 delivery-game/county-region-project/tools/prepare-runtime.py docs/art/2026-11-03-county-region-atlas/runtime-package-ab --static-rider-map -1596.7 96.27 --static-rider-direction ne
```
