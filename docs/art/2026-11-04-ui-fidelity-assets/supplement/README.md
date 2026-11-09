# UI缺件补充候选：12图标

仅本目录写入。内置 image_gen 生成，已实际打开四张认可参考及两张候选原图检查；未运行游戏、测试或构建。

- `attributes-atlas-v2.png`：speed、capacity、coin-stack、profit、trophy、cart，行优先3×2。
- `navigation-atlas-v1.png`：wrench、road、refresh、target、pickup-pin、delivery-pin，行优先3×2。两pin均为中性定位符号，不绑定额外业务含义。
- 两张实际原生均1536×1024 RGBA，每格512×512，非展示尺寸推断。12个独立rect与所引用PNG的SHA见 `manifest.json`；同图集六项共享文件SHA属于预期。
- 原始提示词见 `prompts.json` / `navigation-prompt.txt`；四参考SHA、原生来源路径见 `provenance.json`。v1保留历史，正式候选指向v2。

检查：12个主体均完整、无文字数字、未见主体串格。alpha≥128主体框全部在各格内部，实际宽231～339px，见 `inspection.json`。无PNG裁切、放大、程序绘图或alpha修复。

透明限制：原生alpha范围0～254；少量低alpha边缘延伸至格边，不能称严格零串色/干净alpha通过。工具RGB展示有明显彩色背景感，但大量对应像素alpha为0；仍按原生保留并标candidate，未认证最终合成效果。首版与修订版均保留，不继续无限重生。浅蓝白界面实装后若边缘影响可读性，再针对原生素材处理。

只补12件；既有19公共图、30NPC、5地图及前两轮manifest、源码、地图、存档均未在此任务修改。
