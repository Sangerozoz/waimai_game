# M1-HUD-FINAL 开发交付

2026-10-29。本轮源码已稳定冻结，仅修改生产MapSample.ts、SampleUI.ts，精确哈希见final-source-sha.json。独立验收期间不作无关改动；等待固定测试及美术复核，不代填用户真机验收。

## 七项映射与根因

1. **显式定位恢复默认。** 原按钮调用city.locate()默认resetZoom=false，只恢复跟随、不恢复缩放。red.log新增实际MapSample回调回归复现undefined!=true；另真实CityMap回归验证overview100m→locate(true)实际scale2/30m、骑手当前位置居中、之后移动继续跟随及原视野边界。修复仅把显式用户按钮改为locate(true)，没有改世界限制、路网或旧起点。
2. **底栏上圆下直。** 新topOnlyBar在现有单Surface立体材质上，将底影、外沿、白边和黄色各层底部填成直角矩形，覆盖底边与手势区，不只改最外层。上角保留圆润过渡。
3. **红圆抢单。** 移除中心bag，原生多层同心红圆、深红底厚度、暖白环和左上柔光；白色44号粗体“抢单”配深红描边，100宽标签占112圆宽约89%。MainNavigation有横向安全区缩放，中心slot以逆向x scale抵消，根与视觉均实际正圆，PressVisual仍只压内层、命中根不动。
4. **左下站点。** positionStation统一安排idle左下-416Y，active时按配送面板顶部+110上移；半宽按当前active图像或标签取大，安全区+12CSS左距。异步SIZE/ACTIVE、页头update/save/rebuild仍走同一入口，灰度禁用保持；站点在比例尺/署名与菜单上方，不加动作。
5. **胶囊内边距和立体爱心。** 图标40、边距14、图标/数字间14，尾部14；爱心按饱满双瓣轮廓叠深红底缘、红/粉/浅粉多层渐进色与椭圆高光，不再平色白点。
6. **按内容hug的数字胶囊。** 不再固定三列比例；字体max(24,ceil(body×.8))，金额评分同号同粗同lineHeight且较旧body小。Array.from逐字符宽度估算，按原完整十进制文本加图标/内距算胶囊宽；超可用宽限制后换行，若两个胶囊不能并列则评分下移。保留两位小数，不缩成万亿单位。真实图覆盖100.00、10000000.00、100000000.00、1000000000.00及实际整数分上限90071992547409.91。
7. **无昵称的头像/下置经验条。** 删除昵称和身份板；等比头像成功宽87.359、失败占位宽84，经验轨道及填充基准跟随该实际显示宽，SIZE/ACTIVE切换重新布局。头像透明左边补偿2设计像素，实际可见左距约12CSS。经验文字只保留短Lv.等级，居中28号，真实阈值进度仍由experienceProgress驱动；不再把完整长经验串塞入条内。

## 验证与证据

- tests.log：npm test退出0，27核心+158地图+18存储+4Python地图数据=207通过、0失败。
- typecheck.log：npm run typecheck退出0。
- build.log：npm run build:map包装脚本退出0，最终21:45:43 map-sample Finished；保留build-script子进程SIGTERM/code null诊断，不称零异常。Cocos原始进程退出码未单独捕获；原包装允许0或36。
- red.log：新增显式定位回调修前失败；现实际CityMap与按钮回调两个回归通过。头部旧昵称/固定三列测试按本轮新要求替换为实际经验等宽、无昵称、完整大金额/hug增长检查；保留账单、存档、结算与安全区等原行为回归。
- render-measurements.log：真实生产组件标准/短屏、安全区、多级金额及失败回退，加载完成后首次测量在手动update前。头像成功87.359与XP87.359，失败占位84与XP84，后续更新一致；数字字体24或28、金额/评分相同。中心有效112×112，在安全区缩放后仍相等。无昵称。
- 同日志实际事件发给FollowRider：before scale0.6/100m；after scale2/30m、follow=true、rider[-1540.46,-129.99]、project[0,0]；配locate-before/after截图。
- layout-measurements.log补充内容胶囊实际边界、长数字增长、图像左距和真实XP40/50进度0.8。
- gallery.html及screenshots：标准720×1280、360×560、安全区、千万/亿/十亿/最大值、头像失败、定位前后。screenshot-sha.json固定最终批次；home-before为本轮前卡通HUD快照。

## 冻结与权限

before/baseline.json保留本轮前两份源码，production.patch为精确差异，final-source-sha.json为验收版本。未修改业务订单、经济、时钟或存档源文件；前轮结算退出/灰禁用/按压/滚动/缓存/车辆影子继续由原回归覆盖。没有开M2、没有新增生图。

内存fixture端口4186、独立hudfinal浏览器session；覆盖start/update/save，不创建CountySaveStore，不操作用户4181页或个人存档。大金额/经验、安全区和纹理失败只在fixture内存构造。Storage方法全部拦截，Cocos的setItem('storage')支持度探测每页一次被抛错阻止，不能说零访问。定位的原生事件在隔离样板发出，不是自动点击用户页。

待固定测试独立核对边距/圆形/大金额/异步及美术体积；真机系统手势、多指、完整长期业务及用户审美仍未代验收。

## 冻结后最终核证

PM提示计数后，已对冻结SHA重新执行完整npm test，工具返回退出0。实际Node各组27/158/18均fail0，Python4项OK，共207；red地图组160到现158是原昵称/固定三列3项由新紧凑头像/hug1项取代（净减2），不是遗漏新增定位用例。新增真实CityMap默认30m及MapSample显式定位回调均在当前完整组内。verification.json固定本次结果，生产SHA与冻结文件仍一致。

美术终检art-review.md已确认所查看的两张截图红圆/大字/心形体积/底栏下角/左下站点成立；该文件保留其实际查看的截图SHA，不扩称所有视口均由美术验收。固定测试角色当前独立验证仍以其后续报告为准。
