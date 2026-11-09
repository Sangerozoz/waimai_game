# 第2次修后定向独立质量复审 · 当前结论

**静态 PASS（`passed=true`）：当前未解决的安全/逻辑发现均为空；L03 在本次增量中修复。** 这是针对本次缓存修复的定向源码结论，不是重复全量产品/SDK审查或实际显示验收。

- 当前 `UIArtResources.ts` SHA：`50fd03e67582a89bcfe145027f79e6660d15360f1d9888ae39fd5b0866f373bf`。
- 被复审的前版SHA：`a7c71f515644ec90ac6c71f05d7f05c543971acc9fd37c085dbdf27269bb92d4`；以原快照及candidate.diff在内存严格重建，SHA吻合。
- 精确diff只改 `loadArtRegion` 的映射消费段；函数之前全部字节相同，后续纹理/返回/原图逻辑不变。SDK调用与引擎SHA未变，复用下方历史中已追实的有边界证据，不重复整份缓存读取。
- 非作者复审线程仍为 `thr_htnxptrv4w`；父PM `thr_axf6i4e89t` 统一集成。仅更新本Markdown和 [quality-review.json](quality-review.json)。

## 当前增量与L03闭环（仅静态）

`UIArtResources.ts:148-157` 保留本次pending，统一以映射try覆盖source存在性、pixelRect、checkRect、region存在性。现在旧L03反例的裁切越界在154抛出，会进入157的 `invalidateWebPack(pending)`，再重抛到外层161，以163-166原图临时回退结束。后续调用不再永远命中该成功坏索引，而遵守原4s按需冷却刷新。

静态决策核对：

| 路径 | 当前源代码结果 |
|---|---|
| L03：结构合法但source尺寸容不下合法原裁切框 | 154失败→157按pending身份失效→161捕获→163-166原图 `retryWeb=true` |
| source/region缺项、pixelRect异常 | 同一150-157映射try处理；不漏早于lookup的异常 |
| 旧pending在新请求已建立后才尝试失效 | 101-104首先比较身份，不清新请求，也不写其冷却时间 |
| 同一pending已被其他消费者失效 | 已为null或另一pending，旧调用返回，不重复延长冷却 |
| 正常映射 | sourceRect在153赋值，derived在155赋值且156通过后才到158；rect/inset计算仍为原路径 |
| 变量赋值失败或缺项 | 内层catch在157无正常返回；不会以未赋值的sourceRect/derived抵达158。此为控制流审查，不是typecheck通过 |
| 普通Web纹理网络/尺寸失败 | loadWebTexture在158、位于映射try之外；仅进入外层161原图回退，不误失效索引或清全局缓存 |
| `web:false` | 跳过146整个可选分支，直接163-166原图，`retryWeb=false`；不触发pack冷却 |

新增代码没有资源释放、retain、timer、SDK或节点写入调用；成功缓存、reload、超时、晚回调和消费节点存活逻辑与a7c版保持。未发现本次增量的新安全/逻辑阻塞。非阻塞建议S01（后续获准集中观察GPU/native回收）仍保留，不声称运行内存已验证。

## 本轮证据和权限

- 完整读回当前167行源码及旧质量报告；按文本hunk精确重建a7c前版并核对SHA，再审唯一差异。没有执行TS或把原candidate.diff误认为50fd03的新diff。
- CartoonArt、V2ImageSkin、pack、manifest、portraits及原L01/L02两份FAIL报告SHA均未变；相关引擎文件SHA无漂移。当前报告JSON绑定新SHA，历史发现移出当前阻塞数组。
- 未测试/typecheck、执行游戏函数、触碰真实/合成存档、故障注入、Creator构建、部署、浏览器或地图工作；未改源码/资产/manifest/其他文档，不派Agent、不commit/push/worktree。
- 已到本缓存问题第2次fix-and-review；本复审不自行开启后续修复循环。**只读范围已释放给父PM。静态PASS不能用于关闭远程缺图或报98%。**

## 历史保留说明

下方完整保留a7c版L03原FAIL稿；其中“当前”、行号和未解决问题均绑定历史a7c版，不代表50fd03版仍有该错误。原稿SHA为 `a625353af389a373d3bc397698d1cc8fd6c60d0b2bce28d25e8c78a754eb2307`；旧JSON SHA为 `101ce7772ed60052a1a5fe79077bad2f6e24a9632d13d31f9ecf6d27ea7e9d27`，其原发现亦保存在新JSON的review_history。原web-pack的L01/L02 FAIL文件保持不动。

---

# L01/L02 修后独立质量复审

## 结论

**静态质量仍 FAIL（`passed=false`）：无安全发现，1 项残留逻辑问题 L03。**

本次确实修复了先前的主要缺陷：缺 source/region 不再把原图升级为最终成功帧；索引完整结构校验、纹理尺寸验证均移到应用成功边界之前；使用真实 Cocos API 定向绕过成功 UUID 缓存。但是另一个已检测出的映射异常分支没有让成功索引失效，故不能给整个恢复逻辑 PASS。

- 独立复审：`thr_htnxptrv4w`，非作者；复用本线程，不派新 Agent。
- 父 PM：`thr_axf6i4e89t`；同 checkout / `env_e54zrbdgxt`。
- 当前候选：`UIArtResources.ts` SHA `a7c71f515644ec90ac6c71f05d7f05c543971acc9fd37c085dbdf27269bb92d4`。
- 仅写本报告和 [quality-review.json](quality-review.json)。**源码只读范围交回 PM，不自行修改。**

## L03 · P2 · sourceRect 检查失败回退，但成功索引没有失效

位置：

- `delivery-game/assets/scripts/map-sample/UIArtResources.ts:80-99`
- `delivery-game/assets/scripts/map-sample/UIArtResources.ts:148-157`
- 实际消费者：`delivery-game/assets/scripts/map-sample/V2ImageSkin.ts:41-43`

### 触发条件与最小静态反例

可选索引的 source.size 结构合法，却小于该消费者的合法原图裁切框。例如真实 `manifest.json` 中：

- `icon-riders` → `ui-v2/nav-icons-v1`
- 原裁切框 `[144,147,384,378]`；右端528、下端525。

若不完整/错误的索引把该 source 写为尺寸500×500、regions为空对象，`validateWebPack` 会接受正安全整数尺寸和合法对象。这里仅描述分支，**没有制造/写入/执行这个坏包**。当前真实索引尺寸为1268×1241，不触发反例。

流程：

1. `validateWebPack:85-96` 接受该 source；`loadWebPack` Promise fulfilled 并缓存。
2. `loadArtRegion:149` 发现 source 存在，不失效。
3. `150-151` 按调用方原框执行 checkRect，因越界抛出；尚未走到 `153` 的“缺 region → 失效”。
4. `157` catch 回原图，但没有 `invalidateWebPack(pending)`。
5. 原图成功时仍正确返回 `retryWeb=true`；可以显示原图，不会错误创建最终 Cartoon 帧。
6. 以后重开又在 `loadWebPack:106` 得到同一个成功坏索引；每次在151失败，**不会进入4s失效冷却与后续定向刷新**。

**问题性质：** 不是永久占位，也不是当前磁盘资产错误证据。它是索引语义错误被下游发现后仍留在成功缓存的残留分支，与本次 L02 要消除的生命周期缺口同类。

**最小建议：** 将 Web 映射阶段 sourceRect/checkRect 失败也纳入对本次 pending 的身份保护失效，复用现有4s按需冷却后再回原图；不只处理 source/region 缺失。保留 `web:false` 旁路，不为所有纹理网络失败无差别清索引，更不能清全局资源。

## 已修好的路径：独立逐支核对

### L01：缺项回退与冷却

`UIArtResources.ts:144-162` 在 opt-in 时先设 `retryWeb=true`，只有成功取得并校验衍生才返回false。source/region缺项在149/153失效并回退，`CartoonArt.ts:131-139` 因而只放临时 fallbackFrames；重开入口133不查临时表，会重新进入 loader。

`101-118` 的身份/冷却逻辑正确：

- 仅 `webPack===pending` 才失效并设冷却；旧消费者不清新请求，也不继续延长冷却。
- 冷却4s内返回拒绝给外层回退，不等待4s timer。
- 超过冷却后必须有新调用，才启动单次4s pack请求；无轮询、无同次递归自重试。
- `web:false` 直接跳到159，不接触 pack/冷却，返回原图 `retryWeb=false`。

这修复了原 L01 的直接缺项路径，**不覆盖 L03 的提前检查异常**。

### L02：结构检查、复制索引及纹理尺寸

`80-99,112-117` 检查所有 source/region：对象非数组、正安全整数尺寸、标准整数 rect键、边界、受限资源路径、同衍生路径尺寸一致性。返回的是复制出的source/region/size数据，且字典使用null原型；不把引擎JsonAsset中部分检查过的可变结构直接发布。

`23-43,120-128` 的顺序为 **attempt → validate → retain → return**。尺寸错误参与原有三次短重试，耗尽后拒绝并按 Promise 身份清除。坏尺寸在应用层不 addRef，不再形成旧版 fulfilled 错纹理缓存。按 `path@宽x高` 共享成功，实际请求仍为正确 `/texture` 路径；尺寸预期不同不误用旧成功，也不销毁旧合法对象。

当前真实 pack 的离线JSON字段检查为42来源、143 region、143唯一衍生路径，未见与这些谓词冲突。未执行TS或故障注入，未重复图片生产/库存审计。

## Cocos 3.8.8 API、依赖与 native 缓存：独立查实现

项目声明shim仍指向本机 `/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/resources/3d/engine`。以下路径相对该根：

1. **调用形状和回调**：`bin/.declarations/cc.d.ts:30149-30160`、`cocos/asset/asset-manager/asset-manager.ts:552-568` 支持 request对象 + options字典 + completion；`utilities.ts:235-262` 将第三参数函数识别为completion；`186-195` 的单项结果为单个asset，不是数组。没有凭空使用 `resources.load` 的 reload重载。
2. **path/type/bundle**：`shared.ts:42-61` 定义 path请求；`url-transformer.ts:49-55,93-112,146` 用原bundle/type解析path并合并options，与原 `bundle.ts:248-250` 的路径语义一致。`instanceof JsonAsset/Texture2D` 进一步拒绝错类型结果。未运行typecheck，不能称编译通过。
3. **根与依赖UUID**：`preprocess.ts:33-62` 保留全局reload选项；`load.ts:193-198` 将同一task.options传递到依赖。`load.ts:109-111,155-161` 两个成功UUID快路都要求 `!reloadAsset`；本次设置能够绕过根及依赖成功资产缓存，不是只重取Texture2D根。
4. **纹理实际尺寸来源**：`texture-2d.ts:320-333` 登记ImageAsset UUID依赖；`image-asset.ts:555-565` 接受native数据并reset；`texture-2d.ts:121-135,177-183` 据ImageAsset重建纹理尺寸。故在完整成功但尺寸不符后再新发optional尝试，可以重走ImageAsset/native链。
5. **成功后的临时缓存**：`load.ts:126-137` 成功native解析清除该id的files/parsed；`232-238` 完成import/依赖后也清除该id。对本次原L02指定的完整成功对象，reload能避开成功UUID复用，并非仅删除应用Map后返回同一成功对象。
6. **边界不夸大**：`downloader.ts:401-419`、`parser.ts:278-286`、`pack-manager.ts:248-262` 仍可复用临时文件/解析或在途同id请求；`depend-util.ts:202-213` 对成功UUID依赖元数据也有复用。不能把reload说成取消、HTTP缓存失效、任意依赖图/后缀热更或服务器已修好的保证。此候选并未改变原资产UUID/依赖身份。

**API和完整成功对象的定向刷新主路径未发现额外阻塞；L03 则根本没有机会发起该刷新。**

## 并发、引用、晚回调与渲染保留

- `attempt:9-21` 的settled guard未改。超时后的晚回调不会进入该次validate/retain；引擎自己的在途工作及缓存仍可能继续，已知不可取消限制保留。
- `cachedLoad:40-43` 失败清除保留 `cache.get(key)===pending`；index失效也做身份保护。未见旧失败驱逐新请求。
- 原图临时结果与后发衍生结果竞争时，`CartoonArt.ts:135-138` 完成后再次优先检查最终帧，每key临时/成功帧各至多一张；补丁没有新增帧表或无限增帧循环。
- 同资源同期望尺寸仅共享流程成功时retain一次。坏尺寸/超时未取得应用那次addRef，不应凭空补decRef。代码没有releaseAll/releaseAsset/销毁共享纹理或清全局缓存。
- **非阻塞建议 S01：** 引擎 `utilities.ts:47-55,315-328` 及 `load.ts:181-202,244-250` 管理请求临时引用；`Asset.decRef(false)` 不请求释放，实际回收另由 `release-manager.ts:208-260` 决定。**本轮未证明重复强制重载的GPU/native内存零增长**，保留集中观测建议，不把缺少运行观测判FAIL。
- V2ImageSkin和CartoonArt的当前SHA未变，严格销毁保护/允许隐藏有效节点赋图保持；没有新增节点写入路径。CUSTOM/default trim=true/originalSize、端点取整、全衍生rect、inset双轴缩放均未改。

## 时间与排除范围

纯配置算术：pack单次4000ms；失效后按需冷却4000ms；Web纹理3×4000+1000+2000=15000ms；冷pack再Web纹理名义19000ms；原图/原manifest单序列183000ms。冷却直接回退，不叠成当前调用的额外等待。后台计时节流、引擎重试/在途合并与无法取消不包含在名义算术里。

原公开API/原图与manifest策略未改。地图及一切相关制作完全不在本线：没有加工/写地图资产、几何/边界/拼接，未向地图线派工。

## 版本绑定、实做检查与交回

- 修前快照SHA：`73e29316a757f4a37a2f47f188e8f558aa074aeb8270d7ce148cecab2ec9949f`，正是原FAIL审查版本。
- 当前候选SHA：`a7c71f515644ec90ac6c71f05d7f05c543971acc9fd37c085dbdf27269bb92d4`。
- candidate.diff SHA：`1a751a4de400eb5f946aa975aa3815c24f83b1c6cf598990487a31ebf9a4c3e8`；由修前与当前文本重新生成的diff与该文件完全一致，不用空git diff代替。
- CartoonArt/V2ImageSkin/pack/manifest/portraits五输入与交回记录一致；引擎记录SHA亦无漂移，详见JSON。
- 原 `web-pack/quality-review.json` SHA `67d34f63fc97b1c50aecd2e283f0fac51d7fcf5d4e209a125501c568703cfcf5`、原Markdown SHA `62641fa2880ccc2c68c6ebbf948786019220073b1d923f2e05f3c66fd9ad4e78`，均保留历史。

仅静态读取源码/真实SDK与现有文档/JSON，Python只做SHA、文本diff、现有JSON字段与纯算术。**未执行TS、tests/typecheck、游戏函数、真实/合成存档、故障注入、Creator导入/构建、部署或浏览器操作。** 未授权测试本身不是FAIL依据。

仅写本目录两份quality报告；未改源码/资产/manifest/其他文档，未新派子Agent/commit/push/worktree。**只读范围已释放给父PM。** L03修复及再复审由PM统一安排；不关闭用户缺图，不证明实际图片显示或98%达标。
