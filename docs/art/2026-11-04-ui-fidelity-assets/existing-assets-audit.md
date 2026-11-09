# 现有素材盘点（2026-11-04）

本文件为文件/来源盘点与已查看样本判断，不是全量美术验收。

- 导航/公共皮肤：V2ApprovedSkin.ts当前直接用Graphics画头盔、车、定位、账单、圆钮、边框，已明确进入图片替换队列。现有cartoon/ui-icons图集不是本轮认可八图的导航样式，不能因存在就称可复用。
- 人物：existing-20261031/P02-lead-original.png、P04-npc-a-original.png、P05-npc-b-original.png和au01/rider-master-original.png均1024×1536 RGBA；P01-weather/P03-operator是其他用途，不可冒充两位新增骑手。profile-master全身图已实看：橙外套男性身份源，不等于31人肖像库。现V2头像仅主角+2 NPC图片，其余编号头盔占位，不能称31人齐备。后续人物必须先绑定真实业务ID；原图后期名册示例不自动改正式名册。
- 车辆：CartoonArt注册10个展示key（side-d/side-d-plus/side-c/side-c-plus/side-b/side-b-plus/side-a/side-s/side-ss/side-sss）；除初始vehicle-sheet外，vehicles-20261031已有9档45度图与俯视图。文件存在不等于符合认可参考；逐项对车身朝向、占画比例、颜色和透明边。新业务不显示字母等级。
- 食物：CartoonArt有50个foodKeys和5张批量原图的独立rect，FoodImages已接引用。先复用，逐图只补不合格项。V2当前食品画面按订单ID映射，不是权威订单食物字段，不把视觉优化当数据已补齐。
- 地图图卡：已有M01–M05-display-original，可加载但不能直接作为本轮高还原通过素材。已实看M01：暖黄江南河道远景，与认可04-maps-v1.png的明亮现代街道正景差别大，建议五图作为独立UI预览插图重新制作；不涉及导航地图扩展。
- 字体：本次resources/map-sample目录未检出ttf/otf。当前系统字与原图粗黑字重可能不同，开发需核对现有工程字体可用来源；不可仅换图片后忽略字号、字重、行距。

下一步顺序：公共皮肤→布局叠图→31人身份表→五张图卡→有缺口的车/食品。用户目标98%尚未测得。
