隔离候选已完成并交回，生产未改。

- 两源候选：[Economy](/Users/sanger/Documents/ChatGPT/taptap%202/docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/stage/domain/V2EconomySession.ts)、[Fleet](/Users/sanger/Documents/ChatGPT/taptap%202/docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/stage/domain/V2FleetSession.ts)，SHA保持PM指定值。
- [最终测试](/Users/sanger/Documents/ChatGPT/taptap%202/docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/stage/tests/hero-car-reserve.test.cjs) ROOT已修正；SHA：`23819a18703548df6970b7e4db6e84227f1f208220bacd7896cdf830711dbf13`。
- 最终严格领域编译exit 0；GREEN **71/71**（新增18＋既有53）。原RED和两次GREEN日志均保留。
- 最终只读审计PASS：292项保护文件、A36输入无漂移，5个scratch全部清理。

[总收据](/Users/sanger/Documents/ChatGPT/taptap%202/docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/receipt.json)与[报告](/Users/sanger/Documents/ChatGPT/taptap%202/docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/report.md)已注明集成目标和PM补入PlaceCatalog编译入口的要求。

通过范围为防新增及历史兼容；已签零额度旧档仍未救援，完整默认回归与发布门禁待PM。作者停止编辑，写集交回。
