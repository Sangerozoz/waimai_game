# B08 原生候选实交

- 原生绝对路径：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/native/B08-001/B08-v1.png。实际1536×1024 RGBA，2368142字节，alpha [0,254]。
- 工具原文件：/Users/sanger/.codex/generated_images/01a1ac1c-02e8-76f0-b1d9-82f4dab00260/exec-7808ae0c-2dac-4462-9ca2-c378cfa3349e.png。
- 源/逐字节副本SHA256一致：`b8623ecacd109a5c614eb144faa48c48d8249b8b1b48e829a2c1b2cde9513285`。
- 运行图：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/native/B08-001/B08-runtime-280.png。280×197 RGBA，92845字节，SHA256 `b8eb785226980b1bbbd931ff28f83ebbf8df9fa39a4683c66efa4db370223005`。
- 内置image_gen仅调用一次；原生不进运行包。共用只读工具导出.runtime.json，原文件SHA保持。完整实际prompt、参考SHA、源图号/region/version/box及理由在provenance.json。

- Actual native tool preview and exported runtime PNG opened. Complete building; runtime shows clear transparent margin, no bound trees/road/courtyard.
- Preview gradient has alpha=0 at six sampled outside positions; not evidence of an opaque backdrop. Very low-alpha detached pixels exist beyond main building. Exporter trims to major component plus margin; raw source unchanged.
- Native alpha maximum is 254, not 255; full-opacity texture behavior not verified.
- Frontage visually approximately -28 to -30 degrees; wall verticals visually upright. Estimate only, not precise registration.
- Cocos anchor, final scale, compositing/occlusion and user acceptance unverified.
- Market silhouette retains multi-barrel roof spans and repeated public entries; more roof segments/annexes than planned three bays.
- Glazing/interior is warm gold and may read as lit; no user acceptance claimed.

未重试/扩量，未操作业务/UI/经济/车辆参数/存档/道路边界，未跑游戏tests/typecheck/回归，未commit/push。
