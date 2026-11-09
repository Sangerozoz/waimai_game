# T02-free 单株候选交付

仅一次内置 image_gen 原生生成，原生文件逐字节复制，未修改原图。所有交付位于 /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/native/T02-free-001。

- 原生：T02-free-v1.png，1254×1254 RGBA，651393 字节，alpha 0–255。
- 运行：T02-free-runtime-280.png，139×280 RGBA，53828 字节，alpha (0, 255)。共用只读工具裁透明边并等比缩小，非新原生图。
- 原生 source/copy SHA256：d05e3ee4dc5edd1bddb397065810c7c56eb0afb823d6c6a06d10f37e2d48e310，逐字节一致，导出后再次核验一致。
- 运行 SHA256：3ab77c4885b44ba2f8574448f0851662ea0dbbcfa37132d02a52cd253a0ecf0c，再次核验一致。
- 完整实际 prompt、工具源绝对路径、四张参考绝对路径及 SHA 见 provenance.json；裁边和缩放记录见 T02-free-runtime-280.runtime.json。

实际打开运行 PNG 目视：单株窄冠，完整冠/干/根均在画内，无树池和混凝土边，无大片草地。树干竖直，左上亮右侧暗，树冠有叶簇顶面与侧部层次；但整体仍偏直立侧视，高俯视程度不够明确，不能判为62.5°机位通过。叶边局部黄绿细边，280下枝叶细节有合并；未对原生做去边修饰。

接地点估读：运行图根部中央约(68,267)，仅目视估读、非精确标定；自然根团没有可据以校验街段角度的直线底角。父级接入时需复核透视和锚点。候选未用户验收，未Cocos/Tiled接入，未游戏tests/typecheck/回归，未测近景或设备性能。无业务/UI/经济/存档改动，无commit/push。
