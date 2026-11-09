# B03 单件原生候选
内置 image_gen 单次生成；完整实际 prompt、参考路径与 SHA 见 provenance.json。原生逐字节拷贝，未旋转、镜像、拉斜或修改像素。仅运行派生图使用指定只读导出工具裁透明边与缩小。

- 原生：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/native/B03-001/B03-v1.png；[1254, 1254]，RGBA，1051920 字节。
- 运行：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/native/B03-001/B03-runtime-280.png；[166, 280]，RGBA，77690 字节。
- 原生 alpha extrema：[0, 255]；运行：[0, 255]。
- tool source 与归档 SHA 一致：de203e6c32ab3ccf281f5012a48d5a60ac7c86d52b9ab19090ad0f41b137b870。
- 运行 SHA：f4c6630617317157671b2b8535b215b9d770742678075e0b6884c8fbae52ef6e。
- 已实际打开两张 PNG：楼体完整、透明留边存在；竖向玻璃/石柱清楚。左侧墙面较空，原生轮廓少量浅色碎边。运行缩小后细窗格变软。
- 底边视觉估读约 -27° / +55°，非精确标定；墙竖边目视保持屏幕竖直，不能据此宣称精确配准。
- 候选未用户验收、未 Cocos 接入/遮挡验证，未跑游戏 tests/typecheck/回归。原生仅归档，不进运行包。

原生 alpha bbox 为 [0,41,1240,1213]，表明有游离低 alpha 碎点触达左画布边；主体本身留边完整。指定工具按主体连通域导出后运行 alpha bbox 为 [1,1,165,279]，未宣称原生整圈完全无碎点。
