# v1交付

分类素材34张唯一PNG/2,818,111字节，全部长边≤280；建筑13、植物4、车辆与骑手4、灯具2、小物9、地材2。候选本体与待精校摆位分开，不以开发阶段实例上限锁用户。

当前163静态/506面初稿原样作为user-layout.tmj；34个.tx模板＋asset-palette.tmj均使用相对图片路径。export_user_preview.py支持移动、正等比大小、组偏移、可见性、新增和删除；保旧ID，模板用稳定Tiled对象ID生成视觉ID；复制原绑定对象只留copiedFrom，不新增经营/nav关系。原生canonical和原业务元数据只读，摆位不作严格碰撞阻拦、不自动挪回。

实际文件字段演示：B01移动＋等比1.15，P03模板新放ID671→user-object-671，同一Cocos实际164节点/30图片/共享Frame；见demonstration/cocos-edit-demo.jpg与actual-runtime.json。没有Tiled GUI拖动声明。preview-demo只是独立副本，最终用户user-layout与主图不改。

主图保护SHA、相对引用、图片尺寸/内容、164实际UI/坐标、单次scale、PNG共享已核。原主scene237252cf...、TMJ26eb9baa...保持。用户导出不依赖绝对city源或母版，可在解包目录用Python标准库脚本运行；页面需HTTP，当前使用既有4186，无新服务。

仍是可手调粗摆和候选素材，未全县/正式玩法/用户验收。无生图、游戏tests/typecheck/回归/FPS、存档或提交。
