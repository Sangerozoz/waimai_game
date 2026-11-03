# 二维素材拼装街角首批

2026-11-03。用户提出素材库如积木搭建城市，PM说明固定斜俯视透明图、独立路网、地面锚点与遮挡后，用户明确“那我们开始吧”。本轮实际制作首批资产并拼装可浏览小样，不再延展三维程序建筑；已认可画风、蓝色程度、原路网与经营规则不变。Kenney例图只参考资产组合形式，不继承其低模画风。

## 范围

3栋完整独立建筑（橙棚餐饮、窄玻璃沿街楼、普通商住楼）、2种地面树（优先复用符合风格的原HT01一棵并新生一种）、一组道路/人行道美术材质、街灯；已有D骑手方向帧与车辆候选复用。所有新增raster由内置image_gen制作，不用程序盒子或SVG替代。参考 `docs/art/2026-11-03-sample-fidelity-rework/user-target-v2-concept.png`，每次生图明确参考角色及保留画风，真实透明alpha，原生输出保留。

固定斜俯视正交近似，地面两主轴约屏幕±30度，竖线竖直，所有资产统一；光从左上照亮，投影朝右后，不能烘整片大灰背景。建筑完整基底和顶点不裁切、不附带道路/周围地块，图内不画角色/UI/无意义文字。暖白/浅暖黄墙、适量蓝灰玻璃、橙棚，屋顶无树。主图在透明画布内留边，不能把母版切成透视碎片铺墙。

## 文件与数据接口

资产根 `docs/art/2026-11-03-modular-city-assets/`，原始生成文件按 `B01-cafe.png`、`B02-glass.png`、`B03-residential.png`、`T02-tree.png`、`S01-paving.png`、`S02-asphalt.png`、`P01-streetlamp.png` 的ID归档；已有资源另记录来源不覆盖。每次prompt以同ID.txt保存，来源/图像SHA/alpha候选以JSON记录。

`asset-manifest.json` schemaVersion:1，projection:{axisX:[.8660254,.5],axisY:[-.8660254,.5],vertical:[0,-1],pixelsPerMeter:32}，assets数组。asset字段 id、file（相对根）、kind（building/tree/prop/material/rider）、nativeSize:[w,h]、anchor:[u,v]（原图0..1，地面落点）、groundPolygon:[[u,v]...]（底部占地投影，素材类可空）、footprintMeters:[width,depth]、displayWidthMeters:number、facing:string、source:{tool,originalPath,sha256}、notes:string[]。像素尺寸/锚点须读真实输出再定，不用猜测填最终字段。PNG原生alpha保留；实际查看确认前不称验收。

`sample-layout.json` schemaVersion:1、origin:{x:-1580,y:75}、source:{path,sha256,roadIds,buildingReferenceIndices}、projection引用manifest、placements:[{id,assetId,map:[x,y],scale?:number,layer?:number,groundFootprint?:number[][]}]、roads:[{id,width,nodes:[[x,y],...]}]、bounds、rider:{assetId,map:[x,y],direction}。原路网只读，两条主路149397380-0/149397519-0及相关原路为底稿；美术摆放不能压道路/覆盖河道，原源楼143/144/145作为地块参考，不把素材强拉成任意原多边形。若素材完整占地与源楼不吻合，只在合法地块内选择/统一缩放，不能移动道路适应图片。

## 实施与显示

固定开发负责独立Cocos2D Sprite样板：新目录 `delivery-game/modular-city-project/`，构建到现有4181服务 `modular-city/`。数据与PNG置于该入口assets/；相机拖动和有限缩放/复位，画面占主体。不设计新产品HUD或技术面板。先搭图片框架，不等所有美术齐；未就绪资产不以盒子代画。若Cocos环境妨碍必要展示须报告具体fallback，不默默改引擎。

道路路缘用沿原线的精确地面几何配生成材质，与整栋图片同风格；不是再生成方盒建筑。地面、建筑角色前后顺序分开，按地面脚点排序。骑手沿一小段源路来回仅展示遮挡（内存演示，无接单/存档/正式游戏）。若仍有遮挡限制明确记录。地图图像不无限放大。

PM负责生图/完整性/锚点来源/实际组合画面与归档。禁止测试/typecheck/回归/正式游戏与存档访问；必要构建和本轮隔离美术样板展示允许，不宣称阶段测试或用户验收。保存全部dirty、旧图与工程，不提交/发布/安装新依赖。常规实现无需重复问用户。
