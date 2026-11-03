# 高斜俯视完整地块：原路街角生产包

**最新用户确认：** 当前效果“基本满意”，建筑可以稍高/稍大，其他没有问题。[原话与使用边界](user-review.md)、[确认版本/SHA](approval.json)。当前画面作为后续制作依据，首样9/10.5m不再是全图硬上限；没有新的精确高度指令。新大楼版本尚未制作，原生v1保留。以下未用户验收说明为反馈前时点；未游戏测试仍有效。

**当前实际交付：** [新独立入口](http://127.0.0.1:4181/high-camera-city/)已部署，页面/清单/六图HEAD200，旧入口保留。源码/构建/HTTP证据见[开发报告](../../reviews/high-camera-20261103/implementation-report.md)，状态与限制见[PM交付](../../team/reports/2026-11-03-high-camera-city-pm-delivery.md)。未实际查看新运行画面、未游戏测试或用户验收；下文在制/待部署是生产过程描述。

用户已授权开工；两块完整地块、四栋低楼和独立NE/SW骑手，固定开发负责新Cocos2D入口`/high-camera-city/`。旧展示保留。四张原生1254×1254 RGBA实际齐备，已交固定开发正式集成/必要构建/独立部署；部署状态见开发报告，不以素材齐备冒充运行完成。未游戏测试/用户美术验收。

- `scene-layout.json`：三条原路完整节点/原宽/原方向、62.5°正交基、候选地块/楼墙/隐藏入口与原路示范路线。原城市数据不改。
- `metadata/make-guides.py`与`guides/`：由原路计算的结构参考，不是最终运行程序楼体；不操作任何已有图片像素。
- `HC-P-WEST-v1.png`/`HC-P-EAST-v1.png`：两块原生整景；西侧临街正门和入口砖，东侧可见背面无假公共门，内部含庭院、种植池、围栏与固定阴影。
- `HC-R-NE-v1.png`/`HC-R-SW-v1.png`：原生两方向D骑手，橙头盔/衣/箱、圆灯；不是平面翻转或旋转图。
- `asset-manifest.json`/`generation-records.json`由实际新图及`metadata/manual-annotations.json`手工控制点产生。全prompt在`prompts/`，原生源及SHA在metadata/*-source.json。均保留原始字节。
- 沿临街两点只求统一比例/平移，nativePPU西40.0611、东39.9648；其他地面角点最大残差约2.23/1.20投影单位，东侧上临街角是隐藏估计。后角/墙高/退距不能称精确图像测量通过。NE画中轮轴约34°，略偏原道路28.5°，两方向有独立绘画差异。未用镜像/平面旋转/拉伸/脚本改像素掩盖。

已确认画风与用户区域参考见相邻map-production-method-review、approved-ui-reference；HC01仅构图/画风参考，不能作为原路对齐底图。全程不tests/typecheck/回归/渲染矩阵/存档/commit/push/发布。Work浏览器禁用时只做获准HTTP和交付证据核对。
