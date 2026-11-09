# UI 图片资源链路修复报告

日期：2026-11-05。资源工程线程：thr_cqkytibciw；父 PM：thr_axf6i4e89t。
工作目录：`/Users/sanger/Documents/ChatGPT/taptap 2`，环境 env_e54zrbdgxt。

已交付源码修复，尚未构建、部署或在真实远程浏览器验证。用户缺图反馈有效；本报告不宣称远程问题全部解决、98%一致或用户验收。

## 结论与证据边界

已由源码证实的故障机制：

1. 原 `V2ImageSkin.loadManifest` 和 `loadTexture` 将 Promise 放入 Map，失败没有删除。因此 manifest 一次失败会使该 manifest 的后续所有调用持续拒绝；纹理一次失败会使使用同张 atlas 的所有图片持续占位，重新切页也不能恢复，直至刷新 JS 会话。这是条件成立即可确定的缺陷；没有远程控制台证据证明此次用户就是由首次超时触发。
2. 原 `CartoonArt.loadAtlas` 会删除失败缓存，但 `cartoonArt` 节点只请求一次。失败后当前节点没有自动恢复，catch 静默保留占位；只能依赖重建页面再试。
3. 原 `cartoonArt` 在成功回调中额外检查 `parent.activeInHierarchy===false` 并直接 return。暂时隐藏但仍有效的父节点会丢弃已经加载成功的图，随后恢复显示也不重新赋图。当前 V2 render 主要销毁重建节点，故该分支是否在本次用户路径触发仍待证实。
4. 两套资源加载器各有纹理缓存；共同引用的原主角图跨模块没有应用层共享。引擎本身还有缓存，因此不能仅据此断言发生重复网络下载。

首次缺图的唯一共同触发原因仍待证实。没有把“已修复失败恢复缺陷”等同于“已证实此次远程缺图的唯一原因”。

## 只读资源核验

机器可读明细见 [asset-audit.json](asset-audit.json)，包括 key、源文件绝对路径、PNG尺寸/字节/SHA、裁切框边界、构建入口、原生构建文件以及 HTTP 抽样。可用 [audit-assets.py](audit-assets.py) 重新执行只读库存及 HTTP 资源探测，不会启动游戏或操作存档。

| 类别 | 调用链和映射 | 独立纹理与源文件体积 | 结果 |
| --- | --- | --- | --- |
| 底栏及皮肤 | `V2ApprovedSkin.glyph → imageSkin → ui-v2/manifest`；四底栏 key 为 icon-riders/vehicles/maps/bills，共用 nav-icons-v1；其余属性图标另见 manifest | 整份 manifest 42 key，19纹理，16,146,724字节；其中包含面板/按钮，不能全算底栏 | 源图/纹理入口/原生文件齐全，矩形合法 |
| 骑手肖像 | NPC `portrait → imageSkin('npc-N', ..., 'portraits', 'cover')`；npc-1..30 对应5张 portrait-atlas。hero manifest 保留原图；实际 hero 走 `artCrop('avatar') → loadCartoonFrame` | 31身份、6纹理，15,513,807字节；audit另列legacy-avatar别名，所以行数32，非32人 | 源图/纹理入口/原生文件齐全，矩形合法 |
| 车辆 | `VehicleSideArt.vehicleSideArt → cartoonArt → loadCartoonFrame`，tier1..10 对应 side-d/d-plus/c/c-plus/b/b-plus/a/s/ss/sss | 10纹理，22,694,260字节 | 10档齐全；A档实际文件名为 `vV06-a-45`，库存存在，未擅自改名 |
| 地图卡 | `mapPreview → imageSkin(String(id), ..., 'maps', 'cover')`，id1..5 → map-preview-1..5-v1 | 5纹理，13,656,988字节 | 名称依次晴川县/云浦市/星澜城/曜川都会/海境港，矩形合法 |
| 菜图 | `FoodImages.foodImage → foodForOffer.imageIndex → cartoonFoodKey → cartoonArt` | 50 key共用5张原生批次，11,342,450字节 | 50 key的源图/纹理入口/原生文件齐全，归一化裁切换算后合法 |

所有上述原生构建 PNG 均与相应源 PNG 的 SHA 一致。每类抽取一张，通过 `http://127.0.0.1:4182/assets/resources/native/...png` 实际 GET，均200、image/png、响应 SHA 与源文件一致。此操作没有请求游戏入口，不写存档。三份manifest构建JSON也已实际GET，均200且内容与磁盘构建文件逐字节一致。

这只证明本机该文件可完整读取，不证明分享隧道、登录态、远程传输/解码/渲染正常。

原生 PNG 多为数 MB，全部车辆约22.7MB、地图卡约13.7MB。存在移动网络首次传输压力；未测用户带宽和浏览器解码耗时，不能把“大图”单独认定为此次唯一根因。没有生成衍生预览，也没有改 manifest；如父 PM 决定生成小图，需独立目录保留母版，并协调布局工程的 manifest 写集。

## 服务请求时序

来源：`bb terminal output term_xmiiqsyu84 --tail-bytes 240000 --json`，先解码 dataBase64，后仅筛选19:41～19:45。原始限定区间为 [request-evidence.txt](request-evidence.txt)，已在 asset-audit.json 映射 UUID 到源文件。未拷贝凭据或使用他人浏览器。

- 19:41:04：入口请求200。
- 19:41:37～38：原主角图 `rider-master-original` 的 import/native 已请求；不能说主角头像直到19:44才请求。
- 19:41:37～39：portrait-frame、按钮等请求。
- 19:42:01：一条 import JSON 请求。
- 19:44:58～59：旧首页地图纹理、底栏 atlas、HUD等 import 请求。
- 19:45:00～19：相应 native PNG 请求，包括 nav-icons-v1。
- 该区间64条记录全部200，没有同一路径的重复 GET。import JSON 与 native PNG 是资源不同阶段，不能当成重复下载。区间未观察到 NPC portrait-atlas 的请求；不能凭此断言这些 NPC 已成功或失败，因为没有页面导航事件。

服务的200日志不是浏览器完成时间；没有客户端 initiator、Timing、响应字节完成、Image解码/贴图事件，无法区分用户停留入口、开始按钮点击、单档准备等待、网络排队或传输耗时。`V2GameBootstrap` 在点击开始/继续且 runtime 准备后才建立 `V2GameUI`，此前不请求底栏是可能的正常顺序（只读审查，未修改 bootstrap）。因此“入口到晚请求相差数分钟”本身不能证明加载器堵塞。

## 实际改动

源码绝对路径：

- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/UIArtResources.ts`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/UIArtResources.ts.meta`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2ImageSkin.ts`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/CartoonArt.ts`

`FoodImages.ts` 和 `VehicleSideArt.ts` 无需修改，原签名和调用方式保持。新增模块名称已检查现有符号/依赖，无同名文件。依赖方向是两加载器共同依赖 UIArtResources；辅助模块只依赖 cc，不反向引用 UI 或业务。未更改其他地图、UI布局、manifest、原图、经济、存档、baseline或handoff。

具体行为：

- 两加载器按资源路径共享纹理 Promise；同一时刻同资源的正常调用复用一次加载流程，成功纹理 addRef 一次，保持会话内可复用。
- 每个加载流程最多3次尝试，间隔1s/2s，每次60s应用层截止；10s未完成记录 slow，失败记录 retry/failed（资源路径、次数、耗时、原错误），慢恢复或重试成功记录 ready。
- 最终失败删掉缓存，下一次打开页面可重新发起。当前尚在等待的节点自动跟随有限重试，不再必须先关页。
- V2 manifest Promise失败也清除，manifest缺件/拒绝状态及格式异常保留明确诊断；肖像名称读取不再完全静默吞异常。
- cartoonArt 只检查节点是否仍有效，允许给暂时隐藏节点提前赋图；销毁节点仍不写入。V2在manifest返回后也先检查节点，避免已销毁页面继续发起纹理请求。
- 节点发出 `ui-art-state` 的 loading/ready/failed（失败含错误）。保留原fallback且只在成功后隐藏，不伪装已加载，不改动态文字/点击行为。事件为诊断接口，当前UI未订阅；地图卡现有调用方没有失败文案，本次没有擅自改布局。
- 不全量预载，不改全局 downloader，也不加启动阻塞。

## 集成与未验证项

父 PM 建议步骤：

1. 读回这4个源码/metadata文件，确认其他工程没有同时改写；audit里的 sourceFixes 记录本次源文件SHA。报告目录另含 report.md、asset-audit.json、request-evidence.txt、audit-assets.py。
2. 在父 PM 独占流程中用 Creator 导入新增 TS/meta，进行必要构建并读回完整结果。本线程没有运行Creator、tests、typecheck、回归、部署或重启4182。
3. 部署后由独立新浏览器仅做已授权外观诊断，记录首屏/切页资源Timing与新日志，检查五类真实图是否出现、关闭页面时回调安全性。不得以本报告的本机HTTP结果代替远程验证，不发未达标预览给用户。
4. 若仍缺图，先关联具体 key 和 `[UI resource ...]` 路径，区分“未请求、请求未完成、失败后恢复、成功但未显示”。需要认证的分享页使用正规新会话登录流程；无cookie401不能绕过或复制凭据。

已知限制/风险：

- 60s是应用层截止，不是网络中断。Cocos `resources.load` 没有取消接口；晚到回调忽略，底层请求可能仍在进行。超时后重试可能与旧引擎任务重叠，最多3次应用层尝试；引擎自己的下载重试还可能发生，不能承诺线上完全没有重复传输。
- 若用户网络长时间不可用，约183s（不含浏览器暂停计时）后明确失败；最终失败不自动无限轮询，重新打开页面才开启新一轮。未在真实慢网/断网环境执行故障注入或阶段测试。
- 共享纹理按会话保留，切页不会主动释放；这延续旧CartoonArt的持有方式并覆盖V2，仍需父 PM 后续评估移动设备内存。未把所有大图提前加载。
- 本地引擎源码已核对：`bundle.ts` 的 resources.load 委托loadAny；`downloader.ts`有引擎重试；`download-file.ts`仅传入xhrTimeout时设置；DOM图像下载依赖load/error事件，没有本加载器可用的取消口。此处引用本机Creator 3.8.8源码，不推断全部线上设备行为。
- 缺少远程控制台/网络记录，首次全类缺失根因待证实；源码修复是否消除用户问题仍需父 PM 构建后的真实验证。未达到也未声称98%。
