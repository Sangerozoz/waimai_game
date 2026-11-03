# 完整暂停控件缩小修正

**已实现，未测试，待阶段集中测试。** 仅修改MapSample.ts暂停控件创建与头像下定位，保留其他UI尺寸、取餐后可见阶段、实际冻结及取消配送语义。未运行测试/typecheck/渲染复验或回归，未操作用户游戏/存档，未commit/push。

根因：上轮只给PauseSymbol子节点scale0.5，底板/金边仍按原完整按钮绘制，未满足用户整体缩小的要求。

本次取消PauseSymbol局部scale，使其回到原局部几何；改为完整Button-暂停节点scale(0.5,0.5,1)，使底板、金边、Ⅱ的宽高统一为上次缩符号之前的0.5倍，Ⅱ不会叠乘变0.25。没有另留原尺寸可见底板。

头像经验条下按缩小后的控件与32 CSS像素小热区重新计算中心，横向仍对齐头像中心；热区为子节点PauseHitTarget，无绘制，仅负责点击，随暂停节点stage显隐。热区相对屏幕至少32 CSS像素，按其上沿在经验条下留12设计单位，避免伸到经验条或头像上。按钮底板实际视觉尺寸仍为0.5，不用热区撑大背景。UI按键原有点击守卫和阶段谓词未修改。

交付命令npm run build:map --prefix delivery-game包装退出0，build.log记录实际Finished。构建目录delivery-game/build/map-sample。4181静态index/主包HTTP200且SHA匹配本次产物，见static-http.json；仅HTTP，没有浏览器游戏操作。

before/和before-sha.json为真实改前MapSample基线；production.patch为最小差异，final-source-sha.json/build-manifest.json/delivery.json为最终源码、构建指纹和命令结果。实际视觉尺寸、热区及页面体验未渲染复验，不套用历史验证结果。
