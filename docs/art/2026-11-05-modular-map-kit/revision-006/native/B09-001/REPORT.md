# B09 原生候选实交

- 原生绝对路径：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/native/B09-001/B09-v1.png。实际1536×1024 RGBA，2227193字节，alpha [0,254]。
- 工具原文件：/Users/sanger/.codex/generated_images/01a1ac1c-02e8-76f0-b1d9-82f4dab00260/exec-fac5724b-96d4-4fbb-b7fc-094b31920095.png。
- 源/逐字节副本SHA256一致：`f1d00032f2351f98a79369b53e95d0acea81bd45cd181ed95f2821de5b1cb768`。
- 运行图：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/native/B09-001/B09-runtime-280.png。280×195 RGBA，91594字节，SHA256 `fc06f1c5b450cd4633841e10822e97bbe60c85d1a76dc1ba983196f07e68acdd`。
- 内置image_gen仅调用一次；原生不进运行包。共用只读工具导出.runtime.json，原文件SHA保持。完整实际prompt、参考SHA、源图号/region/version/box及理由在provenance.json。

- Actual native tool preview and exported runtime PNG opened. Complete building; runtime shows clear transparent margin, no bound trees/road/courtyard.
- Preview gradient has alpha=0 at six sampled outside positions; not evidence of an opaque backdrop. Very low-alpha detached pixels exist beyond main building. Exporter trims to major component plus margin; raw source unchanged.
- Native alpha maximum is 254, not 255; full-opacity texture behavior not verified.
- Frontage visually approximately -28 to -30 degrees; wall verticals visually upright. Estimate only, not precise registration.
- Cocos anchor, final scale, compositing/occlusion and user acceptance unverified.
- Distinct fan-shell ribbed roof and curved glazed foyer retained, with low support wings; source identity differs from B04 flat pavilion.
- Fine shell ribs soften at 280px; exact curved mass geometry and ground footprint not calibrated.

未重试/扩量，未操作业务/UI/经济/车辆参数/存档/道路边界，未跑游戏tests/typecheck/回归，未commit/push。
