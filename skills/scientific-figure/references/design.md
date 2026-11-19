# 视觉论证与参考解析

## 从读者判断开始

把“做散点图”改写成具体任务：比较同条件处理前后的个体变化，识别离群与不一致；把“材料机制图”改写成具体对象、物质转化或数据依赖，以及证据等级。

复杂图先比较结构不同的草图：按过程、对照、尺度，或观察/解释/验证组织。记录选择依据与否决理由；换配色不算新构图。候选数量是任务和成本选择，不设通用投票次数或三轮硬限制。

每个面板记录：问题、对象 ID、读者任务、证据角色、来源、不可推断项、与其他面板的关系、图注职责。保持必要科学细节；不能通过删掉控制、尺度或结构身份取得“更简洁”的效果。

## 参考论文：六层解析

输入尽量含图/面板、图注、正文引用段和必要方法。缺任何内容时逐字段标记未知。解析六层：科学对象、关系类型、论证角色、视觉编码、布局、表面风格。

每项记录 `value / origin (measured|observed|inferred|unknown) / locator / confidence`。PDF 字号路径可测量不等于轴标题语义已知；转曲、栅格化、裁剪与透明混合限制可恢复程度。只见位图不能承诺精确字体和原始矢量结构。

### Make the reference analysis an actual production input

For a task-matched reference, bind the existing six layers to visible regions: which scientific object supports which reader judgment, using shape, adjacency, shared scale, repeated identity or arrows? Distinguish overview, physical evidence, quantitative transformation and conditional policy. Keep observed visual facts separate from interpretations of their role. Hand this existing-field record and the original image to production; do not compile every scientific noun/verb into a uniform workflow node.

Boxes are appropriate for operations and decisions, not a mandatory representation for the whole figure. Preserve specific molecular transformations, spatial apparatus and measurement-to-criterion objects. Cross-region dependencies can use repeated identity, adjacency or overview-to-detail mapping; drawing every dependency as a page-spanning wire can make the same logic harder to read. In mixed apparatus/data diagrams, route a feedback edge from the object that actually carries its information: a model update from a measured-data object, liquid transfer from a vessel port, and instrument control from a controller. Distinguish those relation types visually; a convenient geometric attachment can imply the wrong scientific relation. When feedback labels are crowded, recover space from lower-priority explanation and reserve a local return lane before increasing type size; review the resulting whole page rather than treating a font threshold as acceptance. When a redesign is tidier but more abstract, locate where an object that performed a reader task became prose before changing colours or generating more layouts.

Keep a suggested implementation separate from the original delivery target. A method overview can visibly end with extraction/reporting; a quantitative result panel is needed only when its reader task requires that evidence. Do not promote a reviewer's optional panel suggestion into a new acceptance requirement. If a coordinator supplies source dissection, record this content assistance; a simultaneous model/host change does not identify the cause of any improvement.

### 把明确选定的原图区域变成素材

整页解析仍用 `scripts/reference_intake.py paper.pdf --pages 3 --out inspection`。已有目标区域时用同一入口的 `--regions regions.json --out assets`；JSON是列表，例如：

```json
[{"id":"comparison","page":3,"rect_pt":[40,60,280,200],"target_px":[600,350]}]
```

`page`是PDF一基页码，`rect_pt`是页面左上原点的PDF点坐标，不能直接填截图像素。`target_px`可省略；填写时表示最终渲染里分给该素材的像素区域。工具输出原裁片、带红框及周边内容的`-context.png`、等比放入目标框的`-target.png`，`regions.json`保存实际图像框。它只读原PDF，不自动紧裁白边或补画缺失对象。

把目标对象、关联标签/数值、坐标/图例作为完整表达单元，在上下文图上看清边界外是什么，再看目标尺寸是否仍能比较。区域不合适就修改同一个矩形定义，不在已裁图片上继续猜坐标。`text_crossing_crop_edge`仅提示可提取文字跨边；没有提示不能证明结构、位图文字或路径完整。所有输出保持`unassessed`，最终仍需看实际整页。

## 设计模式卡

卡片包括：任务、输入、组织原则、必须保持、可替换、禁用条件、已知失败、论文/图号/图注/正文依据和解析状态。学习“列对齐帮助结构与性能配对”，不是只抄“蓝绿色圆角框”。

分别索引 `task_tags / layout_tags / style_tags`；先匹配任务和布局，再按领域、媒介和偏好选风格。统计习惯时按任务和图种分层，考虑同论文/作者重复；常见不等于正确。高水平期刊图可以是负例。

## 不同绘制方式的选择与整图协调

当同一对象反复被简化为错误的形态类别（例如软组织变成枝条或独立薄片），先检查表示方式是否限制了形态，不再只增加轮廓线。以来源可见的主轮廓、连接、体量和细部层级比较实际对象产出；工具名、三维可编辑或生成图的精细纹理都不能代替这个判断。只有用途允许概念表示时，才考虑生成式插画；实测结构、定量形态与显微证据仍须用真实材料。

已有认可对象与新素材不协调时，保留认可的形态，调整同角色对象的色温、阴影、边缘与细节密度；跨角色不必同等写实。动物身份可由概念插画承载，组织—细胞—核的解释仍可用简洁矢量。先看色调是否足够，再决定是否需改轮廓或明暗；不为统一画风给细胞添加无依据的显微纹理，也不把好的主体降成简陋图标。

对象先看形态，再放回目标毫米框看整体主次。替换或转动资产后，按可见轮廓重新核对采样圈、引线和位置语义，不能沿用旧坐标即视为正确；透明像素检查只能找空背景，不能判断解剖。记录位图内部不可逐对象编辑的边界，保留原始资产和生成提示；整图重建使用已保存资产，不假定再次生成像素一致。两条验收均通过后才采用，单例效果不升级为统一后端。实图比较的有效动作和失败边界见[反馈到制作动作](../../research-harness/references/feedback-to-practice.md)。

## 修改与读图

先判断改动是否改变了图的职责。对大幅改稿，沿用上文已有的读者任务、证据角色与对象字段，把原图与拟替换部分放在同一目标尺寸看：原来能追踪的条件、选择、返回和终点，在新图哪里可见？将具体丢失项绑定到当前输出；不能仅凭新素材有真实来源，就把替换记为纯美化。方法图中的一次测量曲线可以解释数据如何进入决策，而一张最终结果曲线通常不能代替决策过程；是否保留由用户的图件任务决定，不设统一禁用图型。

外部自由绘图脚本同样需要这次对照。现有 `revise` 对已登记字段的变更分类，无法检查绕过项目状态的任意 Python 输出；必须对实际成图记录职责是否保持。若构图困难导致关键关系被结果展示取代，先重做同职责的表达，再比较美观，而不是把这种变化降格为字号/配色修正。纯呈现修改检查标签、绑定与可读性；轴、归一化、裁剪、透明度、相机、排序等影响解释，重查公平比较和可见性；数据/分析修改追踪所有下游。

科学核验读取源数据与规格。盲读只给最终图与目标上下文，问：对象/条件是什么、差异多大、误差是什么、箭头是什么、支持和不支持哪些结论。记录读者实际回答、身份/工具、是否独立及版本。无人进行盲读时结果是未知，不是自动通过。
