# ORDER-EXPERIENCE 开发交付

2026-10-29，当前local checkout。生产代码已冻结，精确改动见production.patch，11份修改/新增文件指纹见final-source-sha.json。以PM最终spec为准；未扩M2。

## 实际改动

- 中央红圆112→145.6，字体44→57.2，所有绘制层同比放大；稳定触控根与安全区横向反缩放保持正圆。无单“抢单”，有单“订单”，菜单保留；有单车辆可查看、升级按钮与既有业务层继续限制。
- 手机增加后层接触阴影、深色侧层、反光、侧键，状态栏/信号/电池/刘海/标题由同一连续蓝顶覆盖；正面内容不透视、不拉伸PNG。
- 大厅按期限、菜品份数、整单重量、真实取送地点、全程km、实际备注、配送费、操作排列；普通黄“抢单”、转单绿“接受转单”。金额统一为feeCents基础配送费，不把估算收益当承诺。
- 新单source由ID稳定hash约20%转单、CC-1为direct；不增加RNG调用。quantity与door备注生成时保存；旧字段缺省不回填，份数仅严格后缀解析，不明则显示未提供。可选字段校验拒绝未知来源、非法份数、超过300字/非字符串备注。schema仍1/2/3、catalog4、保存键不变。
- 候选与accept共用合法路线集合计算期限，保持原最终截止公式；旧活动预览直接使用已冻结deadline，不对历史端点重新套新限制。路线按实际points去重，不造三条。
- 已接卡头期限，详情后实际路线全部纵向滚动；唯一固定“去取餐”调用既有depart。卡底与红圆实际最高边实测均12CSS。卡高度调整为max(440, action+340)，为自动规划、骑手与控件留出地图区域，同时保证路线卡能完整滚动到固定按钮上方。
- 关闭订单卡只改orderCardOpen；中央找回原单。弹窗往返保留卡/选线/滚动/镜头，resize保留UI状态；前台到达不替换正在查看的账单/地图，返回可处理交付。done回执X仍finish+save后干净首页，继续接单仍清理后开大厅。
- 自动规划取所有候选的全部真实points包围中心，允许scale<.6，真实比例尺；预留HUD、骑手及取送标记外延、下方站点/定位。取送pin在骑手上层，车型不缩小。显式选线加粗高亮并重新fit；显示重建不重置riderPose。autoFit与低scale边界模式分离，拖图后重开/resize保留实际scale/offset；手动缩放仍.6–6，定位平滑回2（30m）。

## 验证证据

| 检查 | 结果 |
| --- | --- |
| npm test --prefix delivery-game | 退出0；27+173+18+4=222通过 |
| npm run typecheck --prefix delivery-game | 退出0 |
| npm run build:map --prefix delivery-game | 包装退出0；23:18:58 Finished |
| Cocos子进程诊断 | build.log保留code:null / SIGTERM；不能描述为原始引擎零异常 |
| browser-check | CLI退出0；720×1280、360×560、安全区三组；全点投影、骑手/取送pin边界、菜单间距通过 |
| browser-states | CLI退出0；26条真实Cocos内存状态记录，含真实绿按钮接单、拖动不误接、重复点击、收起找回、弹窗往返、手动pan重开/resize、低scale定位、途中/到达/结算X |

红绿：red.log锁定尺寸/蓝顶失败，route-red.log锁定长路线全点失败，manual-camera-red.log锁定拖图后恢复误fit失败；最终回归通过。模块测试替换引擎边界，真实图与状态用独立Cocos Web构建补齐，不将二者混称。

真实样板在4190，生产MapSample.start/update/save在创建存档仓库前被截断，使用新内存OrderBook，Storage全拦。记录到引擎setItem('storage')探针被拦，不能称零访问；未访问/操作4181用户游戏和存档。fixture和build的66个文件逐字节匹配（index仅加fixture脚本）。

41张图与源/构建/fixture/SHA：screenshot-sha.json、final-source-sha.json、build-manifest.json、fixture-sha.json。浏览器原始测量见browser-check-evidence.json、browser-states-evidence.json及对应脚本/log；汇总见verification.json。最后核源SHA未变。

## 交接边界

美术已在art-review.md记录终检通过；该报告有当时截图SHA。本次冻结版本浏览器刷新后部分PNG的SHA与其记录不同（home两图相同），详见verification.json的artReviewCurrentHashes；不将旧SHA冒充此次逐图终检，不修改美术原报告。由PM判断是否需看当前图。

开发自检已完成；PM安排的独立测试闭环、真机FPS/触感与用户体验验收未代填。未修改用户存档、未开始M2、未提交或清理工作区。后续生产修改请以前述冻结SHA为起点，避免覆盖其他在途工作。
