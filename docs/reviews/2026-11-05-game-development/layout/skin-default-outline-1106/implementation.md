# 普通玻璃卡默认描边：单条件实施交回

**状态：源码已实际修改，待父 PM 独立复审及外观核对；不自行判 PASS。**

唯一源码：`delivery-game/assets/scripts/map-sample/V2ApprovedSkin.ts:25`。

- before SHA-256：`796a4111bc9c367672863351b4a93eb43031cd5e2fe83d303fe4979622dee4f0`
- after SHA-256：`9e7e6914f8f5a7c0d8e5dba4045237fca0385d98af12d52676352221bcfd3f09`
- 原条件：`key==='panel-glass'||key==='bill-metric'`
- 新条件：`key==='bill-metric'||(key==='panel-glass'&&stroke!==UI.line)`

静态字节逆替换重建 before 的 SHA 精确匹配 PM 冻结版本；再次正向替换等于当前全部源码字节，证明只有这一处条件变化，其余语句/分支/代码不变。实际完整单行 diff 见 [implementation.json](implementation.json) 的 `exactDiff`。

## 覆盖与保留

- 普通 `panel-glass && stroke===UI.line`：成功后不再创建额外 GlassEdge，使用原位图轮廓。
- `panel-glass && stroke!==UI.line`：仍创建，包括橙色选中语义轮廓；原描边语句、颜色及线宽不变。
- `bill-metric`：任何 stroke 均维持原 GlassEdge；其他皮肤原本不创建的分支不变。
- fallback Graphics 成功隐藏/失败可见、SkinViewport 与8单位Mask/alpha、九宫格/inset/热区、加载/重试/诊断全部保持。

没有修改 GameUI/ImageSkin/ArtResources/CartoonArt、manifest/PNG、车辆场景或地图、开发A的逻辑/Runtime/数值域，也没有夹带骑手排版或万单位规则；没有重复生图。

## 验证边界

仅做精确字节差分、SHA与JSON序列化核对。未运行 tests/typecheck/TS/回归/Creator/浏览器/游戏/业务/存档，未构建、部署、commit/push或派子Agent。

patch 工具自动报告 per-file tsc skipped，并自动附带 includes(:57)/padStart(:104) 的目标lib诊断。这两个API在前态已经存在，唯一条件变化不涉及它们；本轮不扩配置、不补跑诊断，不声称编译通过。

真实去线观感、其他尺寸/透明填充、选中态/bill-metric及失败/晚完成/销毁行为均未运行验证。碎边/缺角不因此全部解释，G04圆盘细环仍 unknown；没有宣称视觉通过或98%。

**源码及两份报告交回父PM，释放写租约并停止写入；PM安排独立复审/构建及复原本批模式，临时权限不跨批继承。**
