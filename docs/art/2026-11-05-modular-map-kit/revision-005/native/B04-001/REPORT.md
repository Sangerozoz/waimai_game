# B04 原生展馆候选

- 内置 image_gen 一次输出，原生源逐字节复制；未旋转、镜像、拉斜或放大。完整实际prompt、参考绝对路径及SHA见 provenance.json。
- 原生：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/native/B04-001/B04-v1.png，1254×1254 RGBA，1338867字节，alpha extrema [0, 255]。
- 来源：/Users/sanger/.codex/generated_images/01a1ac1c-02e8-76f0-b1d9-82f4dab00260/exec-d87fbe9d-decc-4404-9823-82fe48a73648.png
- 来源/副本SHA256一致：`1b838b31b5950739d0c38e5a37e3fb1b904031bf9a1ac5b77cdce3fdb970adef`。
- 运行：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/native/B04-001/B04-runtime-280.png，280×263 RGBA，99335字节，alpha extrema [0, 255]；SHA256 `245ae915e10a2612947786cc5b4e14eb8da13b4cdf8735b2a3f6fa97de95d40e`。
- 使用共用只读导出器裁透明边并缩小，元数据为 B04-runtime-280.runtime.json；原生不进运行包。

已实际查看原生工具输出及打开运行PNG：主体、低翼、入口完整，透明边保留，无标签/院落/树/道路。玻璃部分偏暖金，不能证明是完全无灯；280像素下石缝和天窗格细节弱化。底边及屋顶长边目测约-30°、短边约+54°，墙体目测竖直；仅估读，未精确标定，与目标轴仍可能有残差。无树灯接地点。

状态：候选，未用户验收、未Cocos接入；最终锚点/遮挡/尺度由父会话处理。未运行游戏tests/typecheck/回归，未操作业务/UI/经济/存档/原city/道路/水系/Tiled，未commit/push。
