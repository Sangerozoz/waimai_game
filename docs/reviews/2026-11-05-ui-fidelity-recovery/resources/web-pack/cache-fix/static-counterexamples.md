# L01/L02 修前静态反例与最小改法

状态：只描述源码条件分支；没有执行、注入故障或修改资产。修复者不出 PASS，父 PM 另派独立复审。

- L01/source 缺项：已 opt-in 的 Cartoon key → 顶层合法 pack.sources 无该 resource → retryWeb 仍 false → CartoonArt.frames 永久保存原图。改为 opt-in 默认临时 fallback，只有成功衍生才能 false；web:false 不进入 pack，仍是最终原图。
- L01/region 缺项：source 合法但无 pixelRect 键 → 同上。将当前索引 Promise 按身份失效，并设 4s 的按需刷新冷却；没有定时轮询，同一调用不递归重试索引，后续页面重建才可能加载新索引。
- L02/结构错：JsonAsset 成功但 source.size/regions/region 结构错 → 原 webPack 已 fulfilled，外围 catch 不会删它。改为完整遍历结构、整数尺寸/合法 rect/衍生路径、同一衍生路径预期尺寸一致性验证后，才让 pack Promise fulfilled；使用经过复制的内部索引。
- L02/尺寸错：Texture2D 成功但尺寸不符 → 原 cachedLoad 已 addRef，fulfilled Promise 不删。改为在 cachedLoad 的成功 retain 之前验证尺寸；只有通过才 retain/fulfilled。衍生缓存键含预期尺寸，避免新索引不同期望误用旧成功对象。
- 并发旧失败：旧索引消费者在新索引启动后才发现缺项，不得清除新 Promise；旧纹理拒绝也不得清除新条目。所有失效均匹配 Promise 身份。
- 后续重开：临时 fallback 仅进入现有有限 fallbackFrames；该表不在 loadCartoonFrame 入口截断，重开会继续进入 region loader。合法 web:false 原图仍进入 frames。CartoonArt 无需行为改动。

## CC 3.8.8 已读证据与重载选择

引擎根：/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/resources/3d/engine

- 项目 temp/declarations/cc.d.ts:2 指向实际引擎 bin/.declarations/cc.d.ts；loadAny 的 options 是开放字典，未发明 AssetManager.IOptions。
- bin/.declarations/cc.d.ts:30149-30160 与 cocos/asset/asset-manager/asset-manager.ts:552-568 提供 request 对象 + options + completion 重载。
- url-transformer.ts:49-55,93-112,146：{path,type,bundle} 从同一 resources 路径解析 UUID；全局 reloadAsset 合入 item.options。
- preprocess.ts:33-62；load.ts:193-198：reloadAsset 作为 task.options 递归传给依赖；不是只给根 Texture2D 的局部 request 字段。
- load.ts:109-111,155-161：普通成功 UUID 缓存命中；reloadAsset:true 绕过这两支。Texture2D 的 ImageAsset 依赖也绕过成功 UUID 缓存，native 请求继续经 packManager/downloader/parser。
- load.ts:126-137,232-238：成功原生依赖和 import 都移除其 files/parsed 临时项。因此在本次“引擎完整成功后、应用语义校验失败”的条件下，后续定向 reload 不会永久复用同 UUID 的旧 ImageAsset/native 对象。
- downloader.ts:401-419、parser.ts:278-286 仍可能复用临时缓存或进行中的传输/解析；reload 不是网络取消或强制 HTTP cache bypass。保留晚回调忽略，不伪称故障/网络恢复实测；损坏服务器内容、HTTP 缓存和未结束引擎请求仍可能导致再次 fallback。
- 不调用 releaseAsset/releaseAll、不删除全局资产表、不销毁对象，不改变 downloader 全局策略。坏纹理没有应用 addRef，故不凭空 decRef；成功对象保持原生命周期 retain。引擎自己完整加载时的依赖引用由引擎管理。

原图及原 manifest 的 3×60s、可选 pack 单次 4s、衍生纹理 3×4s + 1s/2s 不变；本轮不改 CUSTOM/trim/originalSize/rect/九宫格或节点生命周期路径。
