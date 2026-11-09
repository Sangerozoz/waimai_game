# 道路裁切与编辑器参考修复

用户截图指出编辑器道路延伸完整，游戏却到建筑中途结束，且中线不同。确认旧ground()以68×66m world bounds裁切，而Tiled1792屏幕画布未作该裁切；编辑器原底图还是平色参考。道路节点和宽度未变，问题是显示范围/样式不一致。

导入器现由编辑器画布四角逆投影扩展runtime bounds（世界轴向bbox），不改roads、物体、相机。实际Cocos已显示延长道路，截图cocos-road-bounds-fixed.jpg。将真实Cocos地面Sprite内部canvas按原点896/896及16:32比例导出为1792×1792的original-roads.png供同一Tiled文件引用；包括原沥青/人行道/虚线。旧平色参考另存original-roads-before-material-fix.png。probe.tmj用户文件未动。

此次为局部显示修复，手动index层级仍未同步。原文件/素材/正式地图/存档均保留。编辑器若未自动重载图片，可保存后关图重开；本次桌面控制出现AX cannotComplete/无运行应用错误，未声称已重新打开Tiled。
