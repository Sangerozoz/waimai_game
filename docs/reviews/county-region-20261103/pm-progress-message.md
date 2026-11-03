源码已落盘 county-region-project/assets/scripts/{AtlasModel,RegionStream,CountyRegion}.ts，独立场景/settings/配置仅选择性复用，未复制缓存。支持整区原图/SHA、排序、ownershipPolygonUV运行时裁切、平移/双指缩放、视口两并发加载/3秒延迟释放；目前限制最近24区域同时显示，避免整县概览把1056图全部载入显存，概览LOD待真实包/PM方案，绝不用重复图填空。
A-v3已原生拷入runtime-data（preview-only，名义6.36796875 px/m，未标定）；NE/SW独立骑手候选也原生复用，默认隐藏。window.countyRegion接口setRoute/setRider仅对ready覆盖、蓝框内、原道路中心线开放；未引入业务/存档/自动演示。
planning/atlas-plan.json已读，B/C/D结构可消费；registration目前只有measurement-grid，尚无可启用实际配准。下一步待真实图/配准包集中构建，当前尚未构建/部署/运行/测试。若近期图包仍需生产，我会先完成包准备/接入脚本与静态记录，不空等。
