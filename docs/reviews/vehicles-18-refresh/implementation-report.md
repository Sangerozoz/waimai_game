# 18 张载具原图接入

状态：已接入并构建，未测试，待阶段集中测试和用户体验验收。PM解除逐图透明边等待条件，按用户交付原图接入。

D+、C、C+、B、B+、A、S、SS、SSS各顶视及45度展示按manifest的tier和resourceKey注册；A展示原文件名vV06-a-45.png保留。18原件复制到resources，source-sha.json记录每项原件与导入件SHA，均一致；未改色、清理或重绘。B按交付深棕黑原样使用。D保留既有图与地图80×128显示框。

MapVehicle通过现有loadCartoonFrame加载各档顶视，D+至SSS全画幅按宽高等比装入80×128；保留顶视朝向修正、异步请求序号及节点销毁保护。VehicleSideArt按tier选择侧45键，沿用cartoonArt等比适配及节点生命周期保护。原图完整透明画布保留，不做不确定的裁框；边缘光晕、留白及真实小尺寸可读性留待验收。既有县城逻辑仍只开放D和D+；更高档资源可映射不代表可购买或解锁，数值和存档规则未改。

before、changes.patch和source-sha.json记录真实改前及资源指纹；build-manifest.json记录最终构建文件SHA。两次构建：初次完成后调整D档继续保留原显示框，最终11:06:41 Finished、包装退出0；日志保留build-script SIGTERM诊断，不能据包装结果推断所有子进程无异常。4181静态HTTP 200，index SHA一致。

未运行测试、typecheck、渲染或回归，未操作用户游戏或存档，未commit/push。所有图片作为当前候选，未声明透明边、光晕及用户观感通过。
