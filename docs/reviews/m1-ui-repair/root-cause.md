# 原始根因与复现

修前源码已按SHA保存至before，已有原生首页截图复制为home-before.png。隔离样板复制修前Web Mobile构建，在System.register导出MapSample时替换start：用真实地图数据建立全新内存OrderBook并调用真实rebuildLayout/openGarage/openMaps/openBills/openPhone。原start被截断，未构造CountySaveStore；禁止Storage全部读写，update和save为空。样板无真实配送、购买、计时或存档行为。

实际phone-before.png复现：PhoneFrame/AppHeader的PNG边缘压扁，宽接单按钮变成椭圆，宿主方板和PNG双重边框，关闭为文字；并非仅凭源码推断。其余页面修前截图同批保留。

1. box→paintBox在宿主画四层倒角，skin→cartoonChrome再叠带完整白蓝边PNG，没有隐藏宿主图形。
2. resizeCartoonChrome的虚拟画布虽然保证有效占地，但最终setScale(width/renderWidth,height/renderHeight)非等比，导致源圆角、边框厚度随着目标比例变形。原测试只校验占地，不能证明视觉正确。移除该运行入口，保留图集原文件供历史追溯。
3. 首页显式skin(bar,'button-blue')产生整条底座；图标48×1.25=60，标签y=-27落在图标外。定位宿主box另加方板。
4. tap只识别起止及7px拖动，没有视觉状态。新增行为用例对修前11通过/3失败，失败是缺少按压视觉/取消恢复。真实Node/Tween边界以引擎替身驱动生产tap，不检查源码字符串。
5. 通用dialog和phone的关闭都调用文字action；标题及手机几何使用不适合比例的PNG。

采用美术诊断与动画规格：按目标尺寸的原生圆角几何，单一Surface底层；复用插画，所有可点击视觉移入PressVisual，命中根不动，按下0.96、释放120ms恢复，取消/拖动/停用/销毁立即复位。遮罩不收缩。

## 短窄视口的第二处真实根因

修后初次360×560截图发现金额仍裁切。追查最终Cocos JS构建：字符串展开`[...this.money.string]`被loose转译成`[].concat(this.money.string)`，整个字符串只计一次宽度，导致计算仍用60号字、宽159、高94；源码层ES2020测试保留原语义，未暴露构建差异。改为`Array.from`逐字符计量，同时修正共用textHeight与昵称字宽。最终真实运行记录font=40、width=159、height=65、lineHeight=57，100.00单行完整；以最终截图为准，不以占地测试替代。

隔离存储监测发现每次启动引擎会尝试setItem('storage')探测支持度，已在Storage原型拦截并抛错，既未委托原方法，也未读写任何值。次数1表示被阻止的引擎探测，不能称为0次访问。fixture内未构建CountySaveStore。

独立测试指出地图署名Label原在触控根上，空PressVisual缩放不影响文字。已将其包装为MapAttribution命中根，Label置于子树，再由tap移至PressVisual；只针对可点击链接调整。
