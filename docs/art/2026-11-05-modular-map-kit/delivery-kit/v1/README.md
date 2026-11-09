# 地图素材包＋可编辑初稿 v1

先交资产和可手调雏形，位置/大小/细小遮挡留给用户后调；不是全县、正式玩法或最终用户验收。原主图163静态/506面作为初稿保留，源道路/边界/水/POI/业务/存档未改。

## 3步使用

1. **看素材**：打开`catalog.html`。34张唯一运行PNG分建筑13、植物4、车辆与骑手4、灯具2、小物9、地材2。全部≤280。主用、可手调待画面确认、候选本体有争议分列；油箱/圆凳尚未入合适场景不等于素材坏。B12/B13/T05没有开发阶段1/2实例上限，允许用户新放；B09/B10/B11/T03不作为新增默认主用；163初稿已有两株历史T03比较实例按原样保留，不自动增放，保留候选供比较。B11-v2/T04不在本包。B13 clean是原同family派生，不是新楼型。
2. **用Tiled改**：打开`user-layout.tmj`，图片全部相对路径。已有对象可移动、隐藏/删除、调整等比大小，改变组偏移/层index。锁定宽高比，保持rotation=0、不镜像。从`templates/*.tx`模板浏览器拖入素材，或打开`asset-palette.tmj`复制装饰对象。也可以复制旧楼；新副本自动获得`user-object-<Tiled对象ID>`，导出记录`copiedFrom`，不会复制经营/POI/nav绑定。可用字符串属性`userVisualId`指定新视觉ID（须唯一）。已有ID保留；请勿手动重复Tiled数值object.id。canonical PPU/UV/PNG只读，实例正等比大小可调，B01/T01旧锁位不阻止用户编辑。
3. **保存→导出用户预览**：在v1目录执行：

   ```sh
   python3 export_user_preview.py --map user-layout.tmj --output preview-user
   ```

   在已有本项目服务打开`/delivery-kit/v1/preview-user/?view=user`。输出隔离在preview-user，绝不写回输入TMJ、原主图或只读preview。默认取复合院落近景；改远处时可追加`--focus-id ID1,ID2`聚焦指定视觉ID。保留旧预览镜头可用query查看其他区域。

此导出器随包携带标准库脚本与同一Cocos壳，不依赖本项目city.json或绝对原生路径；无需安装Python第三方库。但**Cocos页面须通过HTTP打开**，file://不支持浏览器fetch；当前已授权项目4186服务可直接用上述路径，本轮没有新增服务。离开项目后需用户自行提供静态HTTP服务。本包不含原生母版/25图/全城分析快照，metadata里原绝对路径仅来源追溯，页面与Tiled图片引用不依赖这些路径。

## 输出边界与编辑提示

- user-layout.tmj一旦存在，构建器拒绝常规重置；导出器从不写输入。请把用户布局另行备份，不运行旧开发init/apply来覆盖。
- 只支持供给的Tiled object/group图层、可见性/index/组偏移、有限数值、正等比sprite尺寸和多边形面。不支持旋转、镜像、非等比、tile刷图层/部分opacity；明确报错，不白盒兜底。
- 用户视觉实例全部是装饰。已有来源/POI/nav关系只作为冻结只读参考保存在base-scene，移动或复制图像不移动经营目标/停靠点或创建新业务绑定。原始道路、D演示路线/水/边界字段从冻结基线读取，不能通过TMJ改写业务源。
- 摆位/碰撞由用户决定，不自动挪回、不以精摆净距拦导出；预览不证明无碰撞或导航可达。场地种植仍有色块、同楼型重复及原生角度/软边/隐藏根风险；详见catalog中每件校准和状态。
- 原图框按实例宽高一次换成worldSizeUnits，运行nodeScale1，PNG缩到280不缩世界物体。相同file+SHA共享Image/Frame；用户预览仅复制实际引用PNG，素材库可包含未放入预览的资产。
- D骑手两方向只是原内存演示，不代表车辆AI/正式车型完成。V01/V02仍静态视觉候选。

## 实际演示

`demonstration/demo-layout.tmj`是单独副本：B01原对象保ID，editor anchor移动[32,-16]像素并等比放大1.15；模板新增P03长椅ID671，导出为user-object-671。运行入口`preview-demo/?view=user`；字段编辑＋导出演示，未声称Tiled GUI拖动。原user-layout.tmj和当前主图不作为演示输入修改。核验与实际截图见`demonstration/`。
