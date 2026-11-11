# 项目契约与命令（v2，schema_version 仍为 1）

## 四个关联结构

`research.json` 是可编辑的源规格；CSV、结构、图像、稿件和文献仍在独立文件中。

| 结构 | JSON 集合 | 含义 |
|---|---|---|
| 来源与分析 | sources、datasets | 数据来自哪里、记录身份、单位、条件、转换 |
| 论证 | claims、sections | 证据支持哪些主张、限制与正文位置 |
| 科学语义 | entities、relations | 对象身份、关系类型与证据依据 |
| 视觉场景 | figures | 任务、图注、科学绑定与 visual 呈现规格 |

所有集合中的 ID 是唯一字符串，格式 `[A-Za-z][A-Za-z0-9_-]*`；跨集合用字段名区分命名空间。数据行身份可含其他字符，但应保持稳定。`map` 由主张反查图件与正文，避免人工维护两个易分叉的方向。

## 核心字段

导入论文附件、网络档案或绘图代码的数据时，先用其数据字典确认字段的科学含义，不能由列名或视觉样式推断。例如本轮公开反应网络的 `final_conc` 实为有效自由能，`final_conc_percent` 才是比例，边宽还做了截断；另一来源工作簿的 SEM 与正文 CI 标签冲突。将原字段、解释来源、转换与冲突保留在现有 dataset/source 记录中，显示字段不自动当物理量。来源已更正时逐系列处理，不凭旧代码键批量改标签。

- 根：`schema_version: 1`，`revision: 0`，`project: {title, question, synthetic}`，七个集合，`protected: []`，`reviews: []`，`history: []`；可填 `journal_profile: "journal-profile.json"`。
- source：`id, kind (file|literature|synthetic), path`；文献可改用 `citation, locator`。`verified` 是来源内容核验的记录，不等于文件存在；合成源必须配 `project.synthetic: true`。
- dataset：`id, source_id, path, row_key, columns, units, conditions, transforms`。UTF-8 CSV，`columns` 将列名映射为 `string|number`；数值单位显式写出，无量纲用 `dimensionless`。空白是缺失，NaN/Inf 拒绝。重复/缺失行 ID 拒绝。除已实现的 `xrd_uniform_grid` 适配器外，`transforms` 非空会标记分析重现尚未实现；已有分析应保存独立脚本与来源记录。
- entity：`id, label, kind, source_ids`；实际分子/材料应另保留 `identity` 和结构资产定位，内置工具不会验证化学身份。
- relation：`id, from, to, type, basis, source_ids`。`type` 为 `data_flow|temporal|transformation|contact|contains|comparison|hypothesized_causality`；`basis` 为 `observed|computed|hypothesis|unknown`。不要以一种箭头偷换关系。
- claim：`id, text, status, evidence_ids, scope, limitations, alternatives`。证据可指 source 或 dataset；`supported` 至少有一个来源，验证器仅确认连接，不能证明来源足以支持结论。
- section：`id, title, path, claim_ids, figure_ids, citation_ids`；路径指实际稿件文件。正文内容、引文真伪和数值表达仍需核验，自动工具只验引用 ID 和文件存在。
- figure：`id, kind, dataset_id, claim_ids, entity_ids, relation_ids, reader_question, reader_task, evidence_role, cannot_infer, invariants, caption, representation, mapping, visual`。`representation` 为 `quantitative|schematic|mixed`；`visual` 至少含正数 `width_mm,height_mm,font_size`，可加 `title,colors,y_limits`。colors 是后端使用的色值列表；跨图语义色命名由项目约定维护，不由后端自动证明一致。

所有资产使用项目内相对路径。外部源可引用文献定位或复制到项目并注明来源，初始化/渲染不会遍历其他目录。检查器不是通用 JSON Schema 实现：已实现的字段检查见实际报告，额外领域字段允许保存但不因此得到验证。

## 内置 mapping

| kind | mapping | 已实现约束及限制 |
|---|---|---|
| paired | `before,after,labels` | 一行一个配对 ID；两列同单位；缺失配对拒绝；不做统计检验/误差区间 |
| table | `columns,denominator,missing_label,formats` | 单元格对应源行列；formats 可按数值列给 Python 格式（如 `.2f`）；缺失保留；分母是显式文字，不自动核实样本排除逻辑 |
| energy | `value,order` | row_key 为状态 ID，全部绑定 entity；dataset 有 reference；relations 精确覆盖单一路径相邻边；该旧后端无多路径/三维势能面；多路径用 energy_network |
| methods | 可选 `topology_source_id` | visual.nodes 是 `entity_id: [x,y]`，0–1 坐标；relation 端点必须可见；若源 JSON 有 nodes 列表与 edges 端点对列表则核对拓扑；不自动推断流程或排版 |

能量图只有离散平台与示意连接线。方法图显示关系类型标签，假设/未知依据为虚线。每个导出的 SVG 以 `figure:cell:row:column`、`figure:state:entity`、`figure:edge:relation` 等 ID 绑定科学对象；manifest 保存 ID 清单、图件/主张映射、输入指纹及导出摘要。SVG 文本保留为文本，PDF 使用嵌入 TrueType 字体。外部编辑后摘要改变会报错；其内容无法自动回写科学规格。

## 修改操作

```json
{
  "type": "presentation",
  "reason": "Improve label readability without changing measurements",
  "allowed_change": ["/figures/0/visual/font_size"],
  "changes": [{"path": "/figures/0/visual/font_size", "value": 10}],
  "must_preserve": ["/datasets", "/entities", "/relations", "/figures/0/mapping"]
}
```

`presentation` 为 font_size/export_dpi；标题内容和颜色需重新审阅解释，属于 `interpretive`；轴、尺寸、布局节点等其他 visual 修改是 `interpretive`；来源/数据/关系/主张/图注/稿件索引等为 `data`。操作类型至少达到所有修改中的最高影响级别；例如 data 可原子同步单位、轴标签、图注，interpretive 可附带纯呈现修正；presentation 不能掩盖数据修改。这里的 `data` 表示需要重新追踪科学内容的修改，不表示每次都改原始数据。

只修改已存在字段，allowed_change 是确切 JSON pointer。must_preserve 从修改前的真实值建立持久保护项，后续修改也要保持；原子结构/原始数值可通过保护相应规格及来源路径保留，但外部直接改写 CSV 不会被 JSON pointer 自动阻止，应结合输入指纹和来源版本管理。验证失败不写回；成功保存 `.research-history/revision-NNNN.json` 和新规格。检查点保存旧规格与操作，不备份外部改写的数据文件，不宣称完整回滚系统。新增数据版本应写新文件，再改 dataset.path，保留旧文件。

对保护项确需改变时，先说明科学变更及受影响产物，按用户已授权范围明确更新项目保护项；不要在 revise 操作中绕过保护。JSON 列表调序会影响位置 pointer，因此对象重排要人工确认保护项，日常用 visual 布局表达顺序，保持集合身份稳定。

## 命令结果与人工核验

`check` 返回 0 表示没有 `failed`，并不表示全部完成；1 表示有失败（或 strict 下有未知/未实现）；2 表示输入/运行环境错误。JSON 报告保留每项状态、对象和原因。`automated_checks_passed` 仅指自动检查无失败；`checks_passed` 也考虑已记录的人工失败。`fully_verified` 仅当所有项 passed；当前自动科学推断未实现，所以不会因漂亮图或人工声明变成 fully_verified。

`render --out build` 生成每图 SVG/PDF/PNG、`source-spec.json`、`captions.md`、`manifest.json`、`validation.json`。输入指纹覆盖规格、sources/datasets/sections 的文件与配置的期刊/style profile 、story_plan 及项目 scripts/*.py；用于发现导出或人工记录过期，不提供内容真伪保证。导出目录内旧文件不自动删除；manifest 指定本次有效交付文件。

人工评估须先保存实际记录（问题、回答/观察、评估者、版本和结论）：

```json
{
  "category": "reader",
  "status": "passed",
  "reviewer": "实际读者或工具标识",
  "independent": true,
  "record_path": "reviews/reader-notes.md"
}
```

```bash
python3 scripts/research.py record-review research.json review-record.json
```

category 为 scientific/reader/layout/publication。记录绑定当前输入与记录文件摘要；输入或记录内容改变即过期/未知。reader 非独立评估即使写 passed 也报告 unknown；工具不能核实填写者的身份，不能把这种记录包装为独立事实。尚未做的评估不生成虚假通过文件。

## v2 后端与实际导出

- `structure3d`：mapping 引用结构 source_id，repeat/selection/occupancy_mode/bonds/element_colors/radius_scale/must_show_sites/elements，visual.views 指定 name/projection/direction/up/margin。真实格式参照案例 research.json。保留 scene.json 的源位点、占据率、周期像、相机和 OVITO 版本。自动检查不能判断遮挡。
- `series`：mapping.series 含 id/x/y/label；按源采集顺序绘制。缺失策略只对 x/y 同时空白生效，单侧缺失拒绝。data-map.json 保留源行和显示顺序。
- `toc`：mapping.layout 为 linear/evidence_hub/comparison；四个 blocks 的 role 为 design/ordered/mixed/evidence，须绑定 claim_ids，结构块引用 structure_figure_id，测量块引用 data_figure_ids。显式 boundary 保留结论边界。现有结构固定四块，其他主题需扩展 renderer，不能伪装通用自动组版。

项目 `style_profile` 指向字体及角色配置。实际字体、大小、字重、斜体和颜色写入每图 typography.json；未安装字体报错，不静默替换。数学语义和外部编辑文字仍需核对。

render 另外保存 generator/*.py、实际输入文件摘要、每图 scene/data-map/typography 文件和 manifest。位图结构嵌入 SVG，标签保留矢量文字。缓存按结构内容、参数、视角、像素、质量及软件版本判断复用，`.structure-cache` 不作为交付证据。程序修改会使旧导出失效；验证当前版本后才能更新交付。

## v3：分开的示意与定量入口

新增 `schematic` 和 `summary`，共九种后端。

`schematic.mapping.scene_source_id` 指向项目内 JSON 场景 source。场景声明 `track: explanatory`、canvas、provenance.locator、geometry_basis、scope_note、objects 和 connections；**不需要 dataset_id**。primitive 包括 text/rect/ellipse/polygon/path/line/arrow/image/sphere，各有稳定 id 与 semantic_id；连接保存端点、meaning、basis。图片仍需登记来源，程序着色球体是可修改场景对象，不是作者原始坐标。场景可承载流程/机理示意/结构表达/TOC，不强制四块。

`summary` 必须绑定 dataset。mapping 给 label/value，可给 error、xscale、format；dataset.uncertainty 声明 SD/SE/CI 或计数不适用。当前提供区间点图或对数计数点线图，不执行统计推断。未知误差不能自动补零，混合单位不能据此直接排名。

文本审计保留科学对象原有 gid、语义颜色，并检查非 MathText 字符在解析字体中的覆盖。MathText 字体设置单独指定；其完整语义/字体组合仍需查看真实导出。关闭 Matplotlib 图片合并以保留多个独立 raster 对象 ID。每张 schematic 的 layout.json 报告实际文本边界相交；零相交不等于零遮挡，更不证明图件美观。

`cases/visual-reproductions` 的 `fidelity-research.json` 与 `fidelity/` 是本次原图驱动对照；早期探索稿不计作标准复现。原四块 toc 后端保留为 MatterGen 特定组版，不能当通用 TOC 限制。来源、正文/图注、定量计算与视觉对照分别报告，未知仍保持未知。


### 可选的呈现参数

summary 的 mapping.geometry 可选 bar（竖向零基线柱形，visual.ylabel 必填）或默认区间点图。bar 的 visual.y_limits 为可选显式范围，visual.edgecolor 为边线色。仍绑定 value/label 和可选 error；不确定性定义属于 dataset，不能通过换几何改变。

schematic 材质层的字段见 scientific-figure/references/reconstruction.md；物种/位点/结构的语义身份与材质参数分开。先修改 JSON，再 render；不能只编辑发布 PNG 后沿用旧 manifest。


## v5：材料讨论与定量自定义

可选根字段 `story_plan: "story.json"` 连接来源观察、不同故事候选、读者动作、面板与段落任务。作者未选择不导致探索项目失败；它保留为 unknown，不能宣称已完成共识。`story.py` 检查依赖、源快照漂移、材料可用性及声明的选择一致性；语义理解由宿主完成。详见 [story-discovery.md](story-discovery.md)。

第十种后端 `recipe` 用于固定后端不能表达的定量图，需绑定 dataset_id，并在 mapping.recipe_source_id 指向已审阅、由项目编写的本地 `.py` source。该模块提供：

```python
def render_figure(spec, project, root, fig, ax, bind, load_data):
    # 用 load_data(dataset, root) 读取显式数据。
    # 用 bind(artist, stable_object_id) 绑定主要数据对象，保留 ax 有效。
    # 可自行设置 GridSpec、多面板、色标和坐标，但不能删除主 ax。
    ...
```

程序可执行本机 Python，**没有运行沙箱**；不要直接执行下载论文的未知代码。只读入已核实数据，渲染逻辑按项目科学问题编写和审阅。数据转换、统计口径、物理限定、绘图对象绑定及图注需分别核对。recipe_semantics 始终保留人工审阅需求，自动导出/字体检查不认证科学结论。两个实际例子在 `cases/story-discovery/scripts/force_heatmap.py` 和 `spin_identity.py`。

`recipe` 未配置 `visual.title` 时，由 recipe 自行安排标题；宿主不再用内部 figure ID 补写或覆盖标题。显式配置 `visual.title` 仍设置主 axes 的左标题。合成项目始终保留 `SYNTHETIC DEMO` 标记：无显式标题时在主 axes 现有左标题前加标记，若左标题为空则只显示标记。其他后端的默认标题行为不变。

可选 `figure.visual.export_dpi` 为正数，配置PNG及嵌入位图的导出采样；不填写保留旧180dpi预览行为。当前论文成图案例显式用600dpi，PDF/SVG保留原生文字与几何；位图对象的源分辨率仍是上限。DPI修改归presentation，不改数据/布局/物理尺寸。分辨率不等于视觉或投稿合格。


## 已排版示意场景的物理画布

`figure.visual.layout_mode: "exact_canvas"` 是显式选项：关闭 constrained layout，并把主 axes 设为 `[0,0,1,1]`。用于场景已负责所有页内留白的 schematic；默认行为不改变。有轴数据图若选择此项，作者必须自己留刻度、轴标签等空间。`width_mm/height_mm` 决定 PDF 页面大小；输出后核对实际页面尺寸与标签基线，600dpi 或无文字包围框相交不能代替这一步。

schematic text 支持 `va: "baseline"` 和 `rotation_mode: "anchor"`；后者默认仍为 `default`。路径、线和边界的虚线可由 JSON 表达为 `[offset, [dash, gap, ...]]`，渲染时转换为 Matplotlib 接受的序列。它保留可复算绘制参数，不评价源图的科学关系或美观度。原图驱动几何测量与新论文独立叙事设计应分开报告。


### 项目内的角色字体与转曲导出

角色 token 可选 `font_family` 与 `font_file`。后者是项目内相对路径，渲染时用受约束的 project root 解析；把字体资源也登记到 sources，才能纳入输入版本。渲染和字体审计都使用实际文件与角色的预期属性，不需要安装系统字体。默认仍沿用 profile.font_family，不改变旧项目。

`visual.text_export: "outline"` 导出 SVG 字形路径及 PDF Type3 字形，适用于已经取得可用字形且需要稳定外观的重建。标签文本仍在场景 JSON 中编辑，SVG 中不再是可直接改字的 text。源 PDF 的字体子集只覆盖部分字符，不能拿来排新稿任意文字；新稿应另选覆盖完整、可用的字体。字体审计仍核对实际标签缺字，不能只检查文件存在。Matplotlib 可能对稀疏子集的行高探针 l/p 提示缺字；应区分探针与真实标签，并查看最终基线与字形。


## 有序催化表面后端 `catalyst_surface`

初始化将 `surface_backend.py` 和独立 `surface_render.py` 一起复制进项目 scripts；后续出图不依赖用户全局 skill 路径。ASE/NumPy/OVITO 使用现有 `requirements-3d.txt`。job 与所有状态坐标分别登记为 project.sources 中的本地文件。吸附物身份来自 tags 或 adsorbate_indices；不接受非金属猜测。状态须保留同一原子顺序、晶胞和 PBC。

```json
{
  "id": "SurfaceStates", "kind": "catalyst_surface", "representation": "mixed",
  "mapping": {"job_source_id": "SSurfaceJob", "states": ["IS", "FS"], "atom_labels": {"65": "H"}},
  "visual": {"width_mm": 90, "height_mm": 62, "font_size": 7.3,
    "layout_mode": "exact_canvas", "export_dpi": 600,
    "state_titles": {"IS": "Initial", "FS": "Final"},
    "atom_label_offsets_px": {"65": [20, -65]}, "show_distances": true,
    "note": "Periodic substrate display; source coordinates retained"}
}
```

另需填写通常的 claim_ids、reader_task、caption 等语义字段。标签编号必须在 job.focus_atoms 或 request 中。style-profile 的 subtitle/note/structure_label 控制实际字体。semantic_colors.element 作为项目统一元素色，job.style.colors 显式设置优先。位图渲染像素由 job.camera.size 决定；export_dpi 不会增加源位图细节。180 mm 四联图使用每帧 900×720 的例子，面板图像约 44 mm 宽，源采样约 520 ppi；按实际刊载宽度复查。

`check` 的准备过程不写图像或渲染缓存。`render` 按 job、坐标、渲染器代码、OVITO 版本和有效颜色缓存 `.surface-cache`；输出 `.surface.json` 保留有效设置、来源、半径、相机、显示像、focus 投影、局部 MIC 距离和显式透明处理。缓存是重渲染优化，不是视觉合格标记。surface_visibility 仍未知：看图确认遮挡、投影与科学含义。

旧四块 TOC 的结构块可令 structure_figure_id 引用 catalyst_surface，并用 surface_state 指定状态；默认首状态。其余 TOC 语义/版式限制保持原样。新主题优先用 schematic 做有明确故事的图形摘要，不把表面状态列表当作完整 agent 叙事。

## 场景与多路径扩展（2026-11-06）

新 toc 的 mapping.scene_source_id 走通用场景；四块旧模板单独保留兼容。场景分组、对象端口、渲染路径核查与 energy_network 的完整接口见 [scene-layout-energy.md](scene-layout-energy.md)。新版 init 会复制 scene_layout.py、energy_network.py 和兼容模块。已有项目不自动升级，先保留历史再按需迁移。
