# NEXT-B-UI-RESIDUAL-1106：账单币图与无效回退调用清理

**状态：两份源码已实际修改，等待父 PM 独立复审；不是独立 PASS、运行验收或 U38 关闭。**

开发 B：`thr_tviezvnwds`；父 PM：`thr_axf6i4e89t`；同 checkout / `env_e54zrbdgxt`。前两轮 ACP 拒写没有产生源码或本报告；本轮 PM 设置真实 ACP 临时选项后，正常 `patch` 工具已成功应用。没有使用终端绕过编辑批准，也没有改全局设置。

## 1. 唯一写集与前后 SHA-256

实际只修改以下两份源码，并新增本报告；没有其他文件写入。

### delivery-game/assets/scripts/map-sample/V2GameUI.ts

- 原始：`cbcc769df60e8d5bfeeeb7d4c33ccb78faa12cbf8e271f9195950d8b6a97f210`
- 候选：`1b70ff52c504c01fa1a790cf75d1d2ff087b9f510b208271c6fc4cb487533ef3`

### delivery-game/assets/scripts/map-sample/V2ApprovedSkin.ts

- 原始：`e3be2228f8ac59746fa412146b289b2c0a267fa18184fcf5859460f59f972e8e`
- 候选：`796a4111bc9c367672863351b4a93eb43031cd5e2fe83d303fe4979622dee4f0`

两份文件原本为 git 未跟踪源码，本轮在内存中保存获租起始完整文本，生成并阅读其精确文本增量；没有拿空 git diff 或 HEAD 充当本轮前版本。

### 冻结输入：起始与收口一致

- `delivery-game/assets/scripts/map-sample/UIArtResources.ts`：`50fd03e67582a89bcfe145027f79e6660d15360f1d9888ae39fd5b0866f373bf`
- `delivery-game/assets/scripts/map-sample/CartoonArt.ts`：`5b59bb9d4c15fba335754f430641d228a20ea31023cf6385f333fba200d73e52`
- `delivery-game/assets/scripts/map-sample/V2ImageSkin.ts`：`e0a160ee04ecbe0374e6d65c5b453e0921f2be4c6fa4cdfb8e6e05c01559faca`
- `delivery-game/assets/resources/ui-v2/manifest.json`：`557df1a20e05328132e1efa8467944dbf4f4baffc2878a1c35e55b5cb3e06322`
- `delivery-game/assets/resources/ui-v2/web/pack.json`：`fb8b62bfff79bb840f915cab6f977ccf37f1cb7e9ae0d116c40c56de3377de30`

没有改资源 API、加载策略、超时、缓存、裁切或所有权，没有改原图/衍生图/manifest/pack，没有重新清点或复制图片库存。

## 2. U38：账单全部币图调用路径

先追实际映射，而非只搜索 coin 字面：当前 `manifest.json:646-665` 的 `icon-income` 明确 `aliasOf: icon-coin-stack`，且 resource/rect 相同。旧 `bills-ready.jpg` 可见今日/累计配送收入左侧金币堆，与该调用链一致。截图来自父 PM 已有隔离核对；本轮没有打开游戏或取得新截图。

### 已改

- `V2GameUI.ts:461-468`：账单局部 metric 的 icon 允许 null；只有有图标时才调用 glyph。无图标时仅把该槽标题/金额居中，收回原币图留白；其他有图标槽仍保留原文字偏移和宽度。
- `:471-473`：今日配送收入显式传 null，不再调用 `income → icon-income → coin-stack`；补给支出/配送净赚仍用原 expense/profit 图片。
- `:492`：累计配送收入显式传 null；任务奖励仍为 `null + trophy`，显示“未记录”，不是假0；累计支出的 cart 图保留。
- `:202-211`：账单顶栏加号可达的共享钱包详情，在账单且非补给上下文不再画 coin，并仅调整被删图标题留白。其他页钱包仍画原 coin；金额标签和余额读取不改。

### 追查并保持

- 顶栏 `:106-108` 已有 `page !== '账单'` 的 coin 旁路，保持原字节。
- 七日收入图、合计、开局资金/余额、日期未知说明没有独立币图调用；其真实数据来源/计算不变。
- 累计支出明细保留 riders/expense/vehicles/wrench/maps 等非金币分类图；没有把这些图片或其他页面的金额一并删除。
- `coins()` 格式、deliveryCategories、账目筛选/求和、真实余额、日期口径、图表数值全部保持；仅把今日指标数组加上明确的 tuple 类型，以安全传入 null 图标。
- 主角里程、在线时长仍显示“未记录”；没有使用统计值或0代填未实现字段。

## 3. 无效回退调用：修调用方，不屏蔽日志

已完整阅读当前 CartoonArt registry、V2ApprovedSkin、V2ImageSkin 和当前 manifest；并检索 glyph/skinSurface 的相关调用及唯一另一皮肤消费者 V2GameBootstrap。没有新增权威存在性查询或修改 CartoonArt。

### nav-base

`V2ApprovedSkin.ts:23` 移除不存在的 nav-base 映射。NavigationBase 继续保留现有深色底板；其名称不会匹配 Navigation- 前缀，所以不再发不存在的皮肤请求。真正的 Navigation-*Face 仍正常加载已有 nav-tile/nav-selected，轮廓与裁切代码不变。

### button-disabled

`:43-47` 仅 enabled 按钮加载已有 button-orange/button-blue。当前 manifest 没有 button-disabled，因此禁用按钮保留已有灰色底板/文案与无 tap 绑定，不发该无效皮肤请求。启用按钮、正常 native 皮肤及已有失败可见底板不变；没有新画图片替代主图。

### clock / coin-stack

`:49-65`：

- clock 不再落入 Cartoon 原 key 透传，而使用临时“时”字回退；主图片仍是正常 `imageSkin(n,'icon-clock',...)`。
- coin-stack 的 Cartoon 临时图片显式映射到已注册 coin，主图片仍是原 `icon-coin-stack`；没有把其他页面的金币堆主图片换成单币。
- 其余当前图片回退使用调用方明确别名，目标为现有 recruit/vehicle/map/bills/coin/heart/target；未命中自有别名的 kind 不再盲目透传到 Cartoon。使用 own-property guard，避免继承属性被误当别名。
- 临时图片背后保留可见文字占位；Cartoon 图片成功才隐藏该占位，native 图片成功仍隐藏整个 fallback。两路图片失败时不会只剩空节点；没有新增粗绘图标、改原资源或改公开函数签名。
- `imageSkin(n,'icon-'+kind,...)` 原成功路径保持；未改变 console.warn、失败事件或诊断去重。未来真正无效的 native key 仍会报告，而不是被静默吞掉。

父 PM 的 `integration/private-visual-observations.json` 仅截获前200条 warning，是截断样本，不是全部总数。这些调用问题不等于当前 native 主图缺失，也不据此宣称修复了用户远程缺图。

## 4. 允许范围内的静态核对

本轮只进行了源码/JSON 定向 key 查找、文本差分、文件 SHA 和静态字符串比对；没有执行应用代码或游戏函数。

- 当前实际 glyph 调用（包括导航、车辆属性、账单指标/明细动态参数）对应的 native key 定向查询未发现缺项。
- 新明确 Cartoon fallback 目标与已读 registry 对照未发现未注册目标。
- 两个不存在的皮肤 key 字面调用已移除；没有修改或新增警告处理器。
- 起始和候选文本逐段比较：`render`、`refreshHUD`、骑手/状态、车辆配置/升级/车辆页/地图卡页、订单页、`update` 中 routeMotion/跟随/HUD 节流全部逐字相同。P0 更新和车型布局没有被本次账单修改覆盖；U23—U30 待确认新排版/万元近似没有实施。
- 本轮新增行未发现尾随空白；只读 SHA 无漂移。这些是静态观察，不是独立质量 PASS。

### 工具自动诊断边界

未主动启动 tests、tsc、typecheck、回归或构建。patch 工具报告 per-file tsc skipped；第一次成功 patch 还自动附带 LSP 静态诊断：V2ApprovedSkin 的 includes 和 padStart 缺目标 lib 支持。原始源码同样已有这两个操作（原 :56 和 :97），本轮未增加这些 API，也未为其扩大范围修改项目配置。没有将该回报当作编译通过或游戏验证，后续由父 PM 的统一复审/构建处理；本轮没有补跑诊断命令。

## 5. 未执行的后续用例与交回

以下均未运行：账单顶栏/今日/累计/明细币图实际移除、账单与其他页钱包差异、真实有账目时金额保持、未记录字段、冷加载/失败下的时钟与金币堆主图片和回退、导航底板与禁用按钮可见性/不可点、实际 warning 变化、P0 配送运动/跟随/HUD 与各页布局回归。

未游戏、未浏览器、未构建、未部署、未读写或制造存档，未招募/购买/接单，未 commit/push、新Agent、地图制作/加工/拼接/数据任务。没有关闭 U38、远程缺图或98%目标。

**两份源码候选与本报告交回父 PM，停止写入并释放写租约。父 PM 复用独立复审 B、统一必要构建，并恢复本线程 Mode=default；本批临时 Accept Edits 不跨批沿用。**
