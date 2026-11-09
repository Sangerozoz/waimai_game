# 固定人物价与培养修订 v2

权威参数是上级`parameters.json`，配置ID为`frontloaded-2026-11-04-v3-hire-training-tail`。旧v1参数/源码副本/推演结果见上级`archive/pre-hire-training-correction-v1/`。

本目录是独立参数规划，不运行或测试游戏：`python run_model.py`。`corrected_model.py`保留旧规划模型的明确假设，更新固定ID价、小幅固有收入、培养费用/效果、车辆费用；`planning-results.json`为完整事件/购买路径，`arithmetic.json`为同地图稳态算术。不要直接执行旧v1的rebalance.py重新生成参数。

初版修订为27.05%；经末6收藏价明确授权统一2.2倍校准，当前正常手动前三人19.91分，24人+4图+8车292.37分，占30人1485.60分的19.68%。对照自动19.16%、混合19.12%，慢操作前三人仍需27.41分。`revision-record.json`记录最终表与结果，`tail-search*.json`保留候选搜索。详见`docs/reviews/2026-11-04-cocos-v2/hire-training-correction.md`。模型不覆盖实际路线、运行确定性订单和用户操作差异，不是游戏测试报告。
