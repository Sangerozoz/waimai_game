# COUNTY-REGION-1103 Implementation Plan

目标：独立Cocos整区图集浏览，保留原生A-v3与全县原坐标；PM负责新图与配准，开发不生成替代素材。

1. 从high-camera-city选择性复用assets场景/meta、settings、package及投影，不复制缓存/历史部署。新运行逻辑按AtlasModel（坐标/可信区域）、RegionStream（视口加载/资源释放）、CountyRegion（相机/接口）拆分。
2. 定义region-atlas.json，先向PM发送atlas-interface.json；原图锚点左上UV、统一尺度、显式sortOrder、可选重叠归属polygon。preview-only禁止路线/骑手，ready需实测证据。源city及蓝框只读。
3. 实现SHA校验、并发2个图片加载、视口外延迟3秒释放、加载失败明确状态、不复制补空白。相机全县范围平移/缩放/复位；整区背景固定排序，动态对象独立顶层，保留少量穿帮限制。
4. 提供window.countyRegion只读状态与setRoute/setRider接口；路线每个连续线段须完整在蓝框和ready区域归属覆盖内。默认没有自动行驶或编造路线。
5. 写prepare-runtime.py拷贝真实包与SHA清单；仅临时纳入A-v3 preview-only原生候选，不宣称配准/全县已完成。真实包到位后必要集中构建、部署独立county-region目录，旧预览不动。
6. 按用户权限不tests/typecheck/回归/浏览器；只做静态资料/SHA盘点及必要交付构建。报告分别记录源码、素材、构建、部署、体验状态，不提交。
