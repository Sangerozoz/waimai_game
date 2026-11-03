# COUNTY-REGION-1103 开发接续交付

当前最新静态数据为12区（5 ready＋7 preview-only），未重编；以 `progress12-delivery.md` 与 `progress12-deployment-record.json` 为准。下列五区/ABN/AB/A-only均为历史交付。

最新数据部署为A/B/C/D/N五整区（源码/编译产物不变），见 `abcdn-delivery.md` 与 `abcdn-deployment-record.json`。以下ABN/AB/A-only均保留为过程历史。

最新数据部署已扩为A/B/N2三整区（源码不变、未重编），见 `abn-delivery.md` 与 `abn-deployment-record.json`。以下AB/A-only均保留为过程历史。

## 当前执行尺度与接续入口（最新）

用户最新尺度见 `docs/art/2026-11-03-county-region-atlas/user-tolerance-20261103.md`：一两块地砖量级的小错位接受，不换算新的固定像素/米数门槛，不按全图最大残差统一返工；仅修明显覆盖遮挡且影响使用的问题。原路、蓝框、内部可信走廊继续约束运行对象，ownership只管理图片绘制。当前源码没有美术残差数值验收门槛，无需为本次尺度说明重编。

当前已交付为A-v3/B-v4独立包；本报告下方A-only/源码待构建段落为保留的过程历史，当前证据以 `ab-final-delivery.md`、`ab-final-deployment-record.json` 为准。下一完整包为PM组装中的北邻N2及C3/D4，收到后集中必要接入，不从在制图片目录私自拼装ready包。未运行页面或阶段测试，未代填全县验收。GitHub进度由PM统一维护索引与提交；开发不执行Git写入。


开发BB `thr_v8eu5ahv2e`，PM `thr_7w55f3h66f`，2026-11-03。最新用户授权覆盖旧A-v3待审和只读待命；用户认可美术不等于原路配准/接缝/全县交付完成。

## 当前真实状态

- **源码**：新增独立 `delivery-game/county-region-project/`，只选择性复用旧Cocos场景、meta、settings、package配置及Projection；没有复制library/temp/build历史缓存。旧high-camera工程和部署未写。
- **实现**：AtlasModel负责同源投影、蓝框/可信覆盖及原路中心线约束；RegionStream负责SHA/原生尺寸、透明整区排序、可选ownershipPolygonUV运行时裁切、视口加载和离屏释放；CountyRegion负责县域相机平移、滚轮/双指缩放、复位和独立路线/骑手入口。
- **资源**：原生REGION-A-v3 SHA `4e266eb23f4d165828fabc6c51ab0334a5d38db02a411ac84008f52ea949911e`，及旧高机位NE/SW独立骑手原生候选。骑手仅存为资源，不默认显示/自动行驶。A已采用registration代理的实测anchorUV `[0.48955335130218147,0.5109103188566978]` 和7.134580079506779 px/m，未旋转、扭曲或改源路。
- **配准**：保持代理 `preview-only`。三个内路口拟合最大11.4325px；所有观察最大47.687px，中高置信观察最大42.3299px。测量不是全路网精确标定，默认路线/骑手隐藏。未把图片像素与理论底稿比例直接等同。
- **构建**：首次沙箱启动Abort134（空日志）；正常macOS应用环境18:31:21构建日志显示Finished，Cocos原始36、包装0，保留build-script SIGTERM诊断。日志在工程build-evidence。不是测试通过。
- **部署**：实际静态文件复制至 `delivery-game/build/map-sample/county-region/`。A最新实测JSON作为纯数据更新复制，无额外编译。没有请求HTTP/打开浏览器/检查运行画面，不能称已实显。
- **未做**：tests、typecheck、回归、渲染矩阵、浏览器自动化、正式游戏/存档访问、commit/push/发布、清理现有改动。用户未触发阶段集中测试。

## 数据接口与交接

接口 `atlas-interface.json` 已通过bb thread tell送PM。数据代理的planning和registration目录只读。读取了planning/atlas-plan.json的1056区域源坐标分区、B/C/D底稿及registration-A.json/region-A-runtime-entry.json。

PM交付目录须包含region-atlas.json及其中相对路径指向的原生图片，运行：

```sh
python3 delivery-game/county-region-project/tools/prepare-runtime.py <PM完整包目录>
delivery-game/scripts/build-county-region.sh --deploy
```

只有Cocos源码/配置变化才需要重编。仅新图/atlas数据变化时，prepare-runtime后把runtime-data原样复制到独立county-region/assets即可。保留旧版本和SHA记录，不覆盖high-camera-city或v1。

浏览器内提供 `window.countyRegion.setRoute([[mapX,mapY],...])`、`setRider([mapX,mapY], 'ne'|'sw')`、`clearRider()`、`getStatus()`；没有游戏/存档连接。路线连续段必须完全落在蓝框和ready归属覆盖内，且每段落在已提供原道路中心线段上（2cm浮点容差）。ready必须显式提供分散不共线的实测点、残差和证据路径；当前A不满足可放行状态。接口拒绝时返回具体reason。骑手方向未提供则拒绝，不镜像/旋转替代。

## 限制与后续依赖

1. B及更多原生图尚未接入；不能宣称整县完成。没有素材的位置保留空背景，绝不重复A或程序盒子补景。
2. 每次最多2个加载；离屏3秒释放节点、SpriteFrame、Texture2D和ImageAsset。视口按距离保留最近24区域（含原生图范围），概览时若覆盖更多区域需缩近或由PM另供真实全县概览LOD；目前没有制作/宣称LOD完成。短时间切换视口会保留离屏缓冲，瞬时总驻留可能大于24。
3. 重叠按sortOrder（相同则id）稳定排序；ownershipPolygonUV由PM提供时仅运行时裁切，原图字节保留。没有互补归属polygon和实际B图，不能称已无缝。
4. 整区背景独立于动态顶层，不实现逐栋深度遮挡；保留用户允许少量穿帮的边界。没有自由旋转、逐栋拆建或动态光照。
5. 下一可推进输入为B原生图、配准条目、相邻接头/重叠带归属。源city SHA持续记录且未修改，经营蓝框没有扩大到红框。


## 后续源码更新：独立可信行驶走廊（未构建）

按PM新指令新增 `region.registration.routeCoverageMapPolygon`（可选原地图米坐标多边形）。PM将status标为ready后，路线与骑手仅在可信走廊与蓝框交集内放行；原道路中心线约束仍保留。连续线段在所有可信走廊边界处分割检查，不只检查端点。多个ready区域走廊允许联合覆盖。

该polygon独立于ownershipPolygonUV：不裁切、不缩小、不变形原图，不因边缘未可用而隐藏整个区域。未提供或null时兼容原有ownership覆盖规则；preview-only即使提供走廊也不放行。源码只校验结构、坐标及证据，不新增像素残差验收阈值；可用内路口与边缘暂不启用的取舍由PM按人工测量设置。

本次只改AtlasModel.ts、接口与报告；未写ready、未修改runtime-data或既有部署，未构建/tests/typecheck/运行/浏览器。等待首A/B实际修缝包后集中必要构建。B-v2原生图片及B配准由PM/数据代理负责，本次未抢写。Git index/commit/push由PM独占，本开发未操作。

## A/B实际包已集中构建（覆盖前述源码待构建状态）

PM提供runtime-package-ab后，已接入A-v3/B-v4与独立骑手，原样保留其ready、内部routeCoverage及互补ownership；已于18:55:54生成Finished证据、包装0并复制独立county-region静态部署。指定骑手点作为静态配置，运行时仍必须经既有门检查，无自动路线或存档连接。未HTTP/浏览器/测试/运行验收。具体当前交付和源码/包/部署SHA见 `ab-final-delivery.md` 与 `ab-final-deployment-record.json`；旧记录保留历史。
