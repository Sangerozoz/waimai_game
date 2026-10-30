# 结算弹窗蒙层：60% 黑色

2026-10-28，仅修改 SampleUI 的颜色解析及 MapSample.dialog 蒙层行、移除不用的 UIOpacity 导入。

- 根因：`col()` 固定返回 alpha 255；原蒙层使用褐黑色 `#302B20`，再设置节点 UIOpacity 180。
- 修改：`col()` 支持 `#RRGGBBAA`，六位颜色仍默认 alpha 255。蒙层直接用 `#00000099`（RGBA 0,0,0,153；153/255=60%），移除其 UIOpacity，弹窗卡片仍为不透明白色。
- 输入：保留全屏层与卡片的 BlockInputEvents，以及点击蒙层关闭弹窗。
- 定向验证：`node --test delivery-game/tests/modal-shade.test.cjs`。测试用 Cocos 边界替身加载、执行实际 SampleUI 与 MapSample.dialog；没有用字符串匹配替代行为测试。
- RED：修改前 3 项测试中 2 项失败，分别得到 alpha 255（应153）、蒙层 RGBA 48/43/32/255（应0/0/0/153）；输入行为测试通过。
- GREEN：修改后 3/3 通过、0 失败。`git diff --check` 退出0。
- 范围：没有运行浏览器、构建、全量测试，没有修改存档。实际页面由用户验收；此验证仅覆盖代码逻辑、颜色数值与旧六位颜色兼容。
