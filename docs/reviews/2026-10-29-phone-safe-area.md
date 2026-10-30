> 样式已被后续[白色圆角悬浮卡片](2026-10-29-floating-profile.md)替换，本文保留安全区技术及历史渐变记录。

# 顶部黑色渐变与iPhone安全区修订

2026-10-29。已按用户要求完成技术修改，真实iPhone观感待用户复验。原试玩 http://localhost:4181/ 。

## 实际变化

- 顶部黄色信息底改黑色向下透明渐变，头像/昵称/等级/余额/评价改浅色，地图延伸在渐变后面。
- 用设备非对称安全区避开刘海、灵动岛、摄像头与底部手势条。头像/文字下移，底部五入口、配送面板和定位同步上移；底栏无背景，抢单仍为黄色大字。
- 弹窗与抢单手机页按安全可用高度/宽度缩放、居中；比例尺、版权避开上下及左右安全边缘。站点仍在地图右上侧。
- 项目自己的web-mobile模板启用viewport-fit=cover，沿用Cocos CSS env安全边距；原生/普通网页读sys.getSafeAreaRect(false)。确认GameDiv被Cocos实际+90度旋转时，先映射物理边缘，再计算SHOW_ALL比例和黑边，避免横屏留白落错方向或重复留白。
- 重建、方向/可视窗口变化、恢复前台时重算必要布局，保持打开弹窗与行程；不添加状态文案。

## 检查

184项通过：domain27 + map135 + store18 + Python4；类型检查、Cocos最终构建通过。新9项行为检查涵盖黑色渐变端点、顶部/底部节点边界、重建不叠加留白、打开账单保持、配送面板/定位、侧边异形屏、大厅短视窗、超出游戏的黑边/无效读数、旋转的左右刘海方向及真实CityMap比例尺/版权节点。

修前red.log有4项失败；独立审查又发现旋转轴向P2、地图边栏信息P3，review-red.log有2项真实失败复现。已修复，独立复核135项通过，无剩余问题；见phone-safe-area/independent-review.md。代码测试不是手机实际测量。

未改派单/食物配置、现金/经验/车辆、配送时间/结算、存档/账单规则；对照基线核心文件SHA与餐图/资源SHA一致。没有读取、注入、清理用户浏览器存档，也未自动操作页面。验收表仅更新A01/A24预期，原结果键与历史记录保持。

## 证据与验收

phone-safe-area/ 下保存baseline.json、before/、red.log、review-red.log、tests.log、typecheck.log、build.log、independent-review.md、build-manifest.json。原M1食物修订的175项为历史检查；本次含新增安全区检查共184项。

用户只需在实际iPhone正常竖屏确认顶部信息、底部五按钮可见可点；转向/返回前台后再确认，大厅和账单能关闭。无需清档或重新攒钱，未测手机不代标通过。当前为M1界面追加修订，M2玩法尚未开始。

实现依据：[WebKit安全区](https://webkit.org/blog/7929/designing-websites-for-iphone-x/)、[Cocos 3.8自定义构建模板](https://docs.cocos.com/creator/3.8/manual/zh/editor/publish/custom-project-build-template.html)，并核对本机Cocos 3.8.8源码中的sys.getSafeAreaRect、view._convertToUISpace及web screen-adapter旋转行为。
