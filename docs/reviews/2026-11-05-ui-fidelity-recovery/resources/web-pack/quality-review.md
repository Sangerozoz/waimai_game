# 四类 UI Web 资源：独立代码质量审查

## 结论

**静态质量 FAIL（`passed=false`）：2 项条件性逻辑问题，未发现安全问题。**

不是资产清点不通过：当前 pack 的42来源/143 region、既有记录146别名与父 PM 清点吻合。问题出在**可选包缺项或语义校验失败后的会话恢复路径**；本轮未制造坏包或执行故障注入，不声称当前磁盘资源已损坏，更不把它们认定为远程缺图的共同根因。

- 独立审查：`thr_htnxptrv4w`，非作者；父 PM：`thr_axf6i4e89t`。
- checkout：`/Users/sanger/Documents/ChatGPT/taptap 2`，环境 `env_e54zrbdgxt`。
- 主目标完整读回：`UIArtResources.ts`、`V2ImageSkin.ts`、`CartoonArt.ts`。
- **只写本 Markdown 与 [quality-review.json](quality-review.json)。源码只读范围现交回 PM；不自行修代码。**

## 阻塞发现

### L01 · P2 · 缺映射的原图回退被当作最终成功帧

位置：

- `delivery-game/assets/scripts/map-sample/UIArtResources.ts:100-122`
- `delivery-game/assets/scripts/map-sample/CartoonArt.ts:131-138`

**触发条件：** 四类已 opt-in 的 Cartoon key；pack 顶层可解析且 version/sources 通过，但缺少原 resource 或其 pixelRect region；原图可加载。当前磁盘映射未发现此缺项，此处是用户要求覆盖的不完整包分支。

静态流程：

1. `retryWeb` 在 `UIArtResources.ts:101` 为 false。
2. `104-116` 的两个 `if` 未命中，不抛错，不改变标志。
3. `119-122` 返回合法原图，仍 `retryWeb=false`。
4. `CartoonArt.ts:136,138` 把它写进最终 `frames`，不是临时 `fallbackFrames`。
5. 以后同 key 在 `133` 直接返回，完全不再进入 Web 流程；即使索引后来恢复也没有重试机会。

**影响：** 不会因此必然占位，但原图回退粘住，违反“临时 fallback 不永久阻断后续 Web 重试”。

**最小建议：** 区分有意 `web:false` 与已 opt-in 后未找到衍生；后者也应带重试标记，只进入临时原图帧缓存。同时给不完整索引安排有界、身份保护的恢复路径，不做每帧无限重试。

### L02 · P2 · 语义校验失败的索引/纹理仍在成功缓存里

位置：

- `delivery-game/assets/scripts/map-sample/UIArtResources.ts:23-51`
- `delivery-game/assets/scripts/map-sample/UIArtResources.ts:71-84`
- `delivery-game/assets/scripts/map-sample/UIArtResources.ts:104-117`

**触发条件 A：** 引擎无错误地交回纹理，但尺寸与 `derived.size` 不一致。

- `cachedLoad:29,40` 和 `loadArtTexture:51` 已先成功缓存并 addRef。
- `loadArtRegion:112` 才拒绝尺寸；`117` 捕获后回原图。
- 原 `textures` Promise 仍 fulfilled，`43` 的 rejected-Promise 清理不会运行。
- 重新打开虽能绕过临时 `fallbackFrames`，但 `24` 又取同一个错误尺寸纹理，反复回退，不发生新的纹理加载。

**触发条件 B：** JSON 顶层合法，但所用 source 的 size/regions 或 region 字段不合法。

- `loadWebPack:77-84` 已把顶层合法的索引作为成功 Promise 保存。
- 下游 `104-110` 的内部结构访问/校验抛错由 `117` 捕获，不会使 `webPack` Promise 自身拒绝。
- 下次仍获得同一个坏索引，`83` 无机会清理。

**影响：** 当前请求仍能回原图，非永久占位；但语义失败没有进入失败缓存生命周期，同会话 Web 恢复无效。这不是 `resources.load` 无法取消导致的已知限制。

**最小建议：** 所需结构/尺寸验证纳入“成功”边界，再进入成功缓存和 retain；异常仅使匹配的 Promise/对象失效，并平衡坏纹理的引用。还需处理引擎的目标资产缓存：本机 Cocos 3.8.8 `cocos/asset/asset-manager/load.ts:109-111,155-161` 会复用成功 UUID，仅删应用 Map 再普通 `resources.load` 不足以保证重新获取。由 PM/原 owner 选择该目标的受控重载方式，不清全局资源、不改全局 downloader、不改原图/manifest 策略。

## 正常路径与重点核对

### 映射、比例与 alpha

- `UIArtResources.ts:86-89,104-114`：用原 resource + 原像素框查 region。归一化坐标按起点和终点分别 `Math.round` 后相减，与旧 Cartoon 规则一致，不把源裁切框用在缩小纹理上。
- 成功衍生返回 `[0,0,w,h]`；`V2ImageSkin.ts:49` 用衍生尺寸作 originalSize；`CartoonArt.ts:138` 保留源 originalSize 供 contain 布局。
- `UIArtResources.ts:113`：左右 inset 乘衍生宽/源框宽，上下 inset 乘衍生高/源框高；`V2ImageSkin.ts:47-59` 再验证并使用 SLICED。例 panel-glass `1620×570 → 1368×482`，60px 四边分别为横向 `50.6666667`、纵向 `50.7368421`，没有把横比率误用于纵轴。
- hero：`CartoonArt.ts:67` 与 `portraits.json` 的 `[340,0,360,360]` 一致；同指 `ui-v2/web/portraits-01c64dfa01b4`，292方形。两 loader 共享 `UIArtResources.ts:5,46-51` 的实际 `/texture` Promise，不按显示别名重复 retain。
- 读取既有生成逻辑 `generate-web-pack.py:169-182`：裁切中非全不透明 alpha 保留 RGBA/PNG，仅全不透明转 JPEG；hero 与 panel 的 meta 均保留 `hasAlpha:true`。父 PM 已完成的全量清点/目视不在本次重复执行；也不据此宣称渲染或零损失。

### SpriteFrame.rect / originalSize / CUSTOM / trim：没有凭名称判错

从项目 `package.json:6-7`、`temp/tsconfig.cocos.json`、`temp/declarations/cc.d.ts:2` 追到本机 **Creator 3.8.8** 声明与实现：

- `cocos/2d/components/sprite.ts:128-152,427-435,629-643`：CUSTOM 不自动以 frame 的原始/裁切尺寸改节点大小。
- 同文件 `459-474`：SIMPLE 且默认 `_isTrimmedMode=true`。
- `cocos/2d/assembler/sprite/simple.ts:141-174`：trim=true 时顶点覆盖整个 UITransform；只有 trim=false 才用 originalSize/trimmedBorder 计算几何缩进。
- `cocos/2d/assets/sprite-frame.ts:351-390,911-928`：originalSize 是修剪前尺寸，不是第二次纹理分辨率缩放开关；`1025-1133` 的普通 UV 来自 rect/texture，不扫描 alpha 自动裁边。

**因此当前不能把 Cartoon 的“大 originalSize、小 rect”直接报为二次缩小。**

纯算术例（没有执行 TS 或引擎）：D车源1536×1024、衍生1000×667，在500×350 contain框中由源 originalSize 算得节点500×333.333；默认 trim=true 时 simple 顶点仍500×333.333，不再乘1000/1536。hero 经 `V2ApprovedSkin.ts:68-75` 的 cover 在104×146 viewport内画146×146，再由已有 Mask裁两侧，非透明边被误裁。

**非阻塞 S01：** 建议显式锁定当前 SIMPLE/CUSTOM/trim=true 契约，或分开源布局尺寸与帧元数据；以后调用者若改 trim=false，会把原始分辨率差误当透明裁边。当前所查四类调用没有这样做。

### 生命周期、重试与缓存竞争

- `UIArtResources.ts:9-21`：settled 防止超时后晚回调重新 resolve/reject；不把回调直接绑到节点。
- `23-44`：同路径共享尝试；真实 load error/timeout 到最终失败会按 Promise 身份删除，旧失败不会驱逐较新条目。L02 是下游语义失败，不应与这个正常机制混淆。
- `V2ImageSkin.ts:29-30`、`UIArtResources.ts:82-83` 对各自真正拒绝的 Promise 同样做身份保护。原 manifest JSON 的成功格式检查保留；本轮没有扩大修改其策略。
- `V2ImageSkin.ts:40,44,62`、`CartoonArt.ts:147,151` 检查严格有效性。引擎 `cocos/core/data/object.ts:651-655` 的 strict 模式也排除本帧待销毁对象，而不排除仅隐藏的有效节点。
- 两 loader 都未保留旧 `activeInHierarchy===false` 丢弃成功结果分支；隐藏有效节点可赋图。fallback 只在成功后隐藏，失败保留。
- `CartoonArt.ts:133-138` 在异步完成后再查成功缓存；选择的缓存中也先查已有帧，同 key 并发不会无限创建 retain 帧。临时原图与衍生最多各保一帧/key；成功衍生优先。当前包含73个 opt-in Cartoon key，但这是静态上界而非实际已分配帧数。
- `V2ImageSkin.ts:35-38,49-59` 是每调用节点一帧、节点销毁时 destroy；不销毁共享纹理。未见由正常切页导致的无限常驻帧增长。
- `VehicleSideArt.ts:4-5`、`FoodImages.ts:6-10` 的 key/签名不变；`VehicleShowcase.ts:22-26` 仍走原 loader并处理失败文字。

### 时间边界：与代码缺陷分开

- 可选 pack：单次4000ms。
- Web纹理：3×4000ms +1000/2000ms 间隔 = **15000ms**。
- 若冷 pack 近4s才成功，再耗尽Web纹理尝试，进入原图前顺序等待可近 **19000ms**；不是把Web纹理序列改成19s。
- 原图或原 manifest：单条名义序列3×60000ms +1000/2000ms = **183000ms**。V2先加载原manifest再加载region，不能把单序列上界当整个页面完成时间。
- 底层 `resources.load` 无取消口、超时后的底层工作可能重叠、后台计时节流、所有尝试耗尽后当前节点不无限自动轮询：均保留为已知限制，不单独判本次 FAIL。

**非阻塞 S02：** 后续获准验证再分别记录pack/衍生/原图/绘制Timing，不把上述源码算术当用户带宽、首屏或成功显示证据。

### 地图完全旁路

`V2ImageSkin.ts:43` 对 maps manifest 明确 `web:false`；`CartoonArt.ts:129,134` 仅四类 UI key opt-in。原有世界top车/历史地图等 key 继续原路径。不制作、加工、修复、写入或向地图线派工。

## SHA 绑定与基线

初读及收口三个主目标 SHA 均与交付 README/image-inventory 记录一致：

| 主目标 | SHA-256 |
|---|---|
| UIArtResources.ts | `73e29316a757f4a37a2f47f188e8f558aa074aeb8270d7ce148cecab2ec9949f` |
| V2ImageSkin.ts | `e0a160ee04ecbe0374e6d65c5b453e0921f2be4c6fa4cdfb8e6e05c01559faca` |
| CartoonArt.ts | `5b59bb9d4c15fba335754f430641d228a20ea31023cf6385f333fba200d73e52` |

pack SHA：`fb8b62bfff79bb840f915cab6f977ccf37f1cb7e9ae0d116c40c56de3377de30`。

其余只读依赖与引擎 SHA 见 JSON。CartoonArt 的 git diff 已读；另两主目标为未跟踪文件，没有经 SHA 认证的紧邻旧版本，所以不把 HEAD 冒充紧邻基线。本结论审查当前字节，L01/L02 属当前可选包恢复路径，未声称此前版本所有问题都由本次引入。

## 权限、未验证与交回

未运行 tests/typecheck、任何TS/游戏函数、真实或合成存档、故障注入、Creator导入/构建、部署、浏览器或网络游戏操作。Python只做文件SHA、JSON与纯算术。本轮不因测试未获授权判FAIL；FAIL仅来自上述静态分支问题。

未改公共 ledger/plan/dispatch/baseline，未改源码、原manifest或资产，未新建子Agent/commit/push/worktree。**只读范围已释放给父 PM。** 由 PM 安排修复后的独立复审与统一集成，不能以本报告关闭用户缺图反馈，不能称实际显示、游戏通过或98%达标。
