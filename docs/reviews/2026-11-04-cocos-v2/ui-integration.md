# V2现有Cocos入口与功能页接入（源码，未运行）

MapSample新增编辑器属性`v2Enabled=false`。false执行原start；true在旧writer acquire和CountySaveStore创建之前返回，新增V2GameBootstrap，再进入V2GameUI。没有改场景默认值。网页显式`?v2=1`与编辑器属性并列启用；无此query且属性false仍走旧start。浏览器读取以`typeof window`保护。入口仍需点击新建/恢复才打开存储。交付URL形式为`<现有map-sample入口>?v2=1`（已有query时用`&v2=1`），未构建/部署/打开页面，不声称该URL已可见。

Bootstrap明确提供“新建V2进度/恢复V2进度”。点击后才加载原city、prepareCity并创建/启用/配置Runtime，以独立V2组合key打开；没有自动读写或迁移旧key。新建遇到现有档由Store拒绝，不覆盖。默认没有真实广告SDK，界面标广告暂不可用，注入adapter抛错，绝不模拟成功。

真实调用链：

- 首页HUD从Runtime.snapshot.economy.state取金币、经验、人物与累计完成，不假造评价/体力。
- 骑手31位置双列可滚动卡，招募/培养分别调用hireRider/upgradeRider。已招募卡进入配车页，列真实车辆实例并调用assignVehicle/upgradeVehicle；无车人物不显示假车。
- 车辆上方当前车型属性/拥有数量/唯一购买，下方三列选择，buyVehicle真实扣款。配置来自二八V2_CONFIG；无资格门槛。
- 五图独立卡调用buyMap/selectMap。只改变经济图选择；实际背景复用原CityData/CityMap，并未生成五张新地图美术。
- 每次真实进入大厅调用enterLobby随机出现判定；普通候选由Runtime.normalCandidates原道路取送产生。连续滚动勾选，总重按真实车辆容量；确认acceptBatch，然后routeChoices/beginTrip；到店pickup，Runtime按真实道路时间和服务时间结算。UI定期同步routeSnapshot.position与当前leg到原CityMap。
- 账单只列真实Dispatch完成receipt与实际累计主角/NPC单数，不造今日/七日金额。

尚未完整：真实进入大厅的专送候选以独立报价卡展示，但广告授权流程/SDK未接，按钮明确禁用；主角体力/评价/风险/补给尚无V2模型，HUD不造数字；NPC经营没有可见路线；车辆/人物卡仍为基础文本交互，未复刻认可原图中的图片和细节；新UI固定720×1280，安全区/横屏/动态尺寸未校准。缺少逐日NPC金额账本，不能给出完整今日/近七日统计。新/恢复发生后没有重置现有档按钮。

依用户要求未运行tests/typecheck/build/游戏或真实存档；没有宣称编译、运行、视觉或体验验收通过。待阶段完成后重点验证：默认关闭分支不访问旧/新存储；入口点击前不启用Runtime；双写锁拒绝；新建不覆盖；新/恢复真实路线；招募/买车/配车/培养余额边界；多单取送/超重/取消已完成单保持收益；大厅进入概率与SDK缺失不发奖；地图选择不篡改道路；滚动与点选、节点销毁、安全区。

CityMap继续显示原OSM归属文字，点击回调调用`sys.openURL(https://www.openstreetmap.org/copyright)`，沿用旧入口链接。
