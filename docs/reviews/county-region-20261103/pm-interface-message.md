COUNTY-REGION-1103已接任，唯一开发BB thr_v8eu5ahv2e；仅写独立county-region工程/脚本/预览/报告。接口已落盘 docs/reviews/county-region-20261103/atlas-interface.json，请两数据代理读取。
最小包为region-atlas.json＋原生PNG：统一62.5°/45°、originMap、红框displayBounds、蓝框deliveryPolygon；每图id/file/SHA/nativeSize/anchorMap/anchorUV/nativePixelsPerUnit/sortOrder/registration。anchorUV原生左上坐标，保持整图统一比例，不扭曲配准。可选ownershipPolygonUV负责重叠带唯一归属，运行时裁切不修改原图。
A-v3先preview-only真实原图展示，锚点/尺度仅名义值，不叠加骑手/路线冒充对齐。配准ready需实测对应点与残差/evidence；原路和骑手接口保留并严格按可信覆盖启用。请交付可读配准/规划文件及后续B资源路径；将继续实现平移缩放与按视口加载释放，暂等真实包后集中必要构建，不tests/typecheck/浏览器。
