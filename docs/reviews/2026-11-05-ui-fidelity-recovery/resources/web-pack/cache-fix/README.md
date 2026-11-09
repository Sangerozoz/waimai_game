# Web 缓存恢复 L01/L02 修复候选交回

**状态：候选已落盘，等待父 PM 安排独立复审；修复者不出 PASS，不关闭 L01/L02、用户缺图或 98% 目标。**

- fixer：`thr_tviezvnwds`；父 PM：`thr_axf6i4e89t`；同 checkout / `env_e54zrbdgxt`。
- 实际只修改 `delivery-game/assets/scripts/map-sample/UIArtResources.ts`。`CartoonArt.ts` 已完整读取、保持本轮起始字节：现有 `retryWeb → fallbackFrames` 与重开路径足够，无需额外修改；`V2ImageSkin.ts` 完整读取、只读，未请求扩大写集。
- 写入证据仅本 `cache-fix/` 目录。不改图片、pack、原 manifest、maps、UI/Game/Runtime/经济/slot、父清单/plan/dispatch；不派新 Agent、不 commit/push。

## 交付与精确绑定

主源码 `delivery-game/assets/scripts/map-sample/UIArtResources.ts`：

- 修前 SHA-256：`73e29316a757f4a37a2f47f188e8f558aa074aeb8270d7ce148cecab2ec9949f`
- 候选 SHA-256：`a7c71f515644ec90ac6c71f05d7f05c543971acc9fd37c085dbdf27269bb92d4`
- 本轮前快照：[UIArtResources.before.ts.txt](UIArtResources.before.ts.txt)
- 精确增量：[candidate.diff](candidate.diff)。该文件源在 git 中原本未跟踪，不能用空 git diff 代替增量证据；CartoonArt 的 git modified 状态属于接手前已有改动，本轮未覆盖它。
- [修前静态反例](static-counterexamples.md)、[起始 SHA](source-before.json)、[候选/引擎 SHA 与未来用例](source-candidate.json)。

保持起始字节的源码：

- `delivery-game/assets/scripts/map-sample/CartoonArt.ts`：`5b59bb9d4c15fba335754f430641d228a20ea31023cf6385f333fba200d73e52`
- `delivery-game/assets/scripts/map-sample/V2ImageSkin.ts`：`e0a160ee04ecbe0374e6d65c5b453e0921f2be4c6fa4cdfb8e6e05c01559faca`

只读输入 SHA 保持：

- `delivery-game/assets/resources/ui-v2/web/pack.json`：`fb8b62bfff79bb840f915cab6f977ccf37f1cb7e9ae0d116c40c56de3377de30`
- `delivery-game/assets/resources/ui-v2/manifest.json`：`557df1a20e05328132e1efa8467944dbf4f4baffc2878a1c35e55b5cb3e06322`
- `delivery-game/assets/resources/ui-v2/portraits.json`：`fc35329f1f63cce69c55ea5668af0eebe86ff6962a2216a6e34e03637c2df826`
- 上轮 `quality-review.json`：`67d34f63fc97b1c50aecd2e283f0fac51d7fcf5d4e209a125501c568703cfcf5`，没有覆写原 FAIL。

## 静态反例对应改动

### L01：缺项不是有意原图旁路

`UIArtResources.ts:144-162` 现在先区分 `web:false` 与 opt-in：

1. `web:false` 完全跳过可选索引，返回最终原图 `retryWeb=false`。
2. opt-in 默认 `retryWeb=true`。仅成功取得、校验衍生纹理后才返回 false；source/region 缺项会抛到临时原图回退，不能再把原图放进最终 Cartoon frames。
3. 缺项会把**本次匹配的**索引 Promise 失效（`:101-104,149,153`）；后续页面重建可以重新请求索引，不永远复用旧 fulfilled 数据。
4. 增加按需刷新冷却：失效后 4s 内不再启动新 pack 请求，直接回退；超出冷却后仍必须有新调用才加载。没有轮询 timer、每帧刷新、同次调用递归重试；旧消费者不能重复延长新索引的冷却。

`CartoonArt.ts:131-139` 入口只查最终 `frames`，不提前查 `fallbackFrames`。临时原图按 key 最多保留一个帧，后续重开仍先尝试 region loader；成功衍生后进入最终帧缓存。保留该已有有限缓存，不加新帧表。

### L02：先语义有效，再成为应用成功缓存/retain

- `UIArtResources.ts:80-100,112-115`：遍历全部 source/region；验证对象而非数组、正安全整数尺寸、标准整数 rect 键及边界、限定衍生 resource 路径、同一路径预期尺寸一致性。全部通过才返回复制后的内部索引。结构异常使 pack Promise 自身 reject，从而退出应用缓存，而不是在外层消费时才发现错误。
- `:23-43,120-128`：尺寸检查从 `loadArtRegion` 下移到 `cachedLoad` 的 `validate → retain → return` 成功顺序。Map 中可以共享进行中的 Promise，但坏尺寸不能 fulfilled，更不会先 addRef。尺寸错误参与原有三次短重试，耗尽后按 Promise 身份删除。
- 衍生应用缓存键为实际路径加 `@宽x高`；实际请求仍是原 `resource + '/texture'`，没有虚构资源路径。不同索引若改变某一资源的预期尺寸，不会误用旧期望下的已成功纹理，也不驱逐仍合法持有的旧对象。
- 原 `loadArtTexture/loadArtJson`、原图和原 manifest 的策略保持；两个当前 region 消费者的衍生纹理统一走带预期尺寸的 `loadWebTexture`。

## CC 3.8.8 API 与 native 缓存证据

实际根目录：`/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/resources/3d/engine`。下列路径均相对此根，SHA 已放入 JSON。

- 项目 `temp/declarations/cc.d.ts:2` 引用该引擎的 `bin/.declarations/cc.d.ts`。后者 `30149-30160` 与 `cocos/asset/asset-manager/asset-manager.ts:552-568` 声明/实现支持 **request 对象 + options 开放字典 + completion**。本补丁不臆造 `IOptions` 或 `resources.load` reload 重载。
- 调用选为 `assetManager.loadAny({path,type,bundle:resources.name},{reloadAsset:true},done)`，仅用于可选 pack 和衍生纹理。正常成功继续由应用 Promise 缓存共享；每次新可选尝试才经该 API。
- `bundle.ts:248-250` 是原 resources.load 的路径/type/bundle 转发；`url-transformer.ts:49-55,93-112,146` 证明本次 request 对象仍解析相同 bundle/type 路径，且 options 合入每项。
- `preprocess.ts:33-62` 保留全局 `reloadAsset`；`load.ts:193-198` 把 `task.options` 传入依赖子任务。不是仅在根 request 的局部字段上设 reload。
- `load.ts:109-111,155-161` 的两个成功 UUID 快路都在 `!reloadAsset` 下，本次可以绕过。`Texture2D._deserialize`（`cocos/asset/assets/texture-2d.ts:320-333`）按 ImageAsset UUID 登记 mipmap 依赖；所以只重载根 Texture2D 而不考虑依赖是不够的，本补丁使用全局 options 递归重载。
- `ImageAsset._nativeAsset`（`image-asset.ts:555-565`）接收 native 数据并 reset；Texture2D 的 `:121-135` 从 ImageAsset 尺寸重建纹理。
- **原生数据缓存已核对**：`load.ts:126-137` 在成功 native parse 后移除该 id 的 `files/parsed`；`:232-238` 在成功 import/依赖加载后同样移除该 id 的临时缓存。因此本次指定的“完整引擎成功后才发现结构/尺寸错”对象，之后不会因同 UUID 的成功 ImageAsset/Texture2D 快路而永久卡在原对象；新 optional 尝试重载依赖，native 数据也重新经过加载管线。只删除应用 Map 而普通 resources.load 并不具备这一点。
- `utilities.ts:47-55` 的引擎请求临时 addRef 在清理时以 `decRef(false)` 平衡；`:129-181` 的依赖绑定/引用属于引擎自己管理。本补丁不调用它们。

### 不夸大 reload 的能力

`downloader.ts:401-419`、`parser.ts:278-286` 对临时文件/解析数据或**尚未结束的**同 id 请求可能复用/合并；`pack-manager.ts:248-262` 也会利用临时已拆包内容或进行中的包。`reloadAsset` 不是取消 API，不强制 HTTP 缓存失效，不保证服务器内容已经修复或网络一定恢复。成功后的临时缓存清除证据适用于本次 L02 成功对象反例，不扩称任意部分失败/在途情形都能取得新网络字节。

保留应用 `attempt` 的超时后晚回调忽略。底层引擎请求可能继续运行、更新自己的缓存；本补丁不能取消它，也不会谎称已经通过故障恢复测试。后续 optional 请求仍用 reload 绕过成功 UUID 缓存；若实际内容依然错误则继续有界回退，不伪造成功。

## 引用计数与并发

- 失败 pack 无应用 addRef；复制索引不保留 JsonAsset 所有权。后续重载不释放旧 JsonAsset 或任何全局资源。
- 尺寸错误/超时纹理没有取得应用那一次 addRef，因此**不补一个凭空 decRef**。尺寸通过才执行共享成功缓存的那一次 addRef，正常生命周期与此前一致。
- 旧合法纹理和帧继续保留；不同期望尺寸不销毁旧对象。不调用 releaseAsset/releaseAll、不清全局缓存、不手动 destroy 纹理、不递归释放 native 依赖。引擎重载自己的成功缓存与依赖引用仍由引擎处理；本轮没有运行内存或引用计数观测。
- 纹理失败清理保留 `cache.get(key)===pending`；索引失效也仅在 `webPack===pending` 时执行并设置冷却。旧失败不清新请求、不修改新请求的冷却。
- 晚回调在 `attempt` 的 settled guard 截止；不能进入 validate/retain 或替换页面。有效但隐藏节点仍可赋图；销毁保护仍为原 `isValid(...,true)`，没有改节点/交互逻辑。

## 已做的静态核对（不是执行验证）

- 完整阅读指定三份源码、原质量 FAIL JSON，追实际 CC 声明与实现；逐支追缺 source、缺 region、完整 JSON 内部结构错、尺寸错、并发旧失败和后续重开。
- 对**未修改**当前 pack 做离线 JSON 字段检查：42 sources / 143 regions / 143 unique derivative paths；与新增数据谓词无冲突。没有加载 TS 或图片、没有重复图片库存审计。146 别名沿用已有资料与源码；未重生成任何一项。
- 明确保留 sourceRect 端点 Math.round、原 resource/rect 映射、衍生全纹理 rect、inset 双轴缩放。`CartoonArt`/`V2ImageSkin` SHA 未变，未改 CUSTOM/default trim=true/originalSize 路径。
- 原图/原 manifest 名义序列 `3×60000 + 1000 + 2000 = 183000ms`；pack 单次 `4000ms`；Web 纹理 `3×4000 + 1000 + 2000 = 15000ms`；冷 pack+衍生最多名义 `19000ms`。均为配置算术，不是计时实测；冷却不等待 timer，当前请求直接回退，不恢复 183s 的可选前置等待。
- scoped `git diff --check` exit 0/无输出；由于 UIArtResources 原本未跟踪，另用修前快照做 `git diff --no-index --check`，exit 1、无空白诊断（两文件确实不同），并保存精确增量。没有把这当编译通过。
- patch 工具自动报告“项目 tsconfig 存在，per-file tsc skipped”；没有启动 tsc、LSP 编译或其他 typecheck。

## 未来用例与交回

JSON 中 F01–F12 全部标为 `not-run`：source 缺项、region 缺项、web:false、内部结构错、同路径尺寸冲突、成功坏尺寸、旧索引失败、新旧纹理晚回调、同源别名并发、隐藏/销毁、等待预算/无轮询、正常裁切/九宫格与 trim。需按父 PM 授权验证，不由 fixer 执行游戏场景或制造故障。

**未运行、未测试、未 typecheck、未构建、未部署、未操作浏览器、未故障注入、未造真实/合成档。没有宣称网络恢复、实际画面可见、当前资产损坏、缺图已清或 98% 达标。**

独占写范围在本候选交回后释放；父 PM 可把上述候选 SHA 与 diff 交给另一独立会话复审，原作者/本 fixer 均不把自己改动审为 PASS。
