# 多面板与源绑定能量差

`scripts/publication_components.py` 可用于 `recipe` 后端。`research.py init` 会复制它；旧项目需显式更新此依赖。组件只处理声明的内容和版式，不自动判断故事、参照是否可比或审美是否达标。

```python
from publication_components import panel_grid, panel_heading, energy_difference
axes, frames_mm = panel_grid(fig, ax, rows=1, cols=2,
    margins_mm=[15, 8, 18, 25], gap_mm=[13, 0])
panel_heading(axes[0], 'a', 'Catalyst A', bind=bind, prefix='A')
result = energy_difference(axes[0], source_states, {
    'from': 'A-intermediate', 'to': 'A-TS', 'semantic': 'activation',
    'unit': 'eV', 'x': 2.55, 'label_xy': [4.4, 2.65], 'color': '#087C86'
}, edges=declared_edges, bind=bind, prefix='A:water')
```

`panel_grid` 按上到下、左到右返回坐标轴；边距顺序为左、右、上、下，间距为水平、垂直。可指定正的行/列权重。框是绘图区，文字需另留空间。跨面板比较时显式设定相同轴范围，不能仅因等宽就称为可比。使用正式非交互导出后端，并从生成 PDF 核对实际尺寸；桌面窗口可能取整像素。

`energy_difference` 的 states 是 ID→源行映射，默认字段为 energy/step/kind；可用参数更名。差值从两个源值相减，单位必须显式提供。activation 要求终点为 transition_state 且存在声明的相邻边；desorption 表示脱附态的能量差，不要求或制造 TS；difference 仅表示普通态差。若存在温度、参照、单位或方法差异，调用前先解决，组件不会替你验证物理可比性。

括号两端绑定源能量；虚引导线指向源横坐标；标签位置可以调整而不得改变高度。返回源状态、精确能量、差值及实际导出图元 ID，可保存到对象映射。SVG 标识绑定可见的箭头对象，不绑定不会导出的空注释容器。

选择标签位置要看实际空间：不要挡住 TS、平台、其他注释或面板标题。双栏差值不必机械地放同一位置；保持字号、颜色和表示方式一致比牺牲可读性更重要。连线是离散状态间的导引，不是连续 PES。自动检查几何和身份后仍应分别查看示意图与数据图的目标尺寸导出。

在曲线与热图组合图中，把轴标签、共享色标、特殊值图例作为独立的排版区域预留空间，不把说明文字临时塞到横轴与色标之间。ACS 火山图首版实际出现了这类撞字；改正时固定原刊宽度，调整中央间距和图区宽度，不能仅把所有文字缩小。原尺寸并排须保留参考图在PDF中的放置缩放；只裁出局部面板时不擅自放大成整图宽度。屏幕缩放不可充当纸面物理尺寸，提供PDF和比例尺。字号/留白的具体数值仍按本图判断，不推广本案例参数为通用模板。

## 离散驻点能级：显式状态、导引与未重建尾段

`stationary_energy_path` 提取自 AI-Cat 精修中实际使用的短平台、无超调 smoothstep 导引和空心终点做法；不复用该案例的能级数组、反应物名称、路径位置或标签。适用于来源只提供离散驻点能量、希望用导引帮助读者跟随顺序的图；连续扫描 PES 应使用实际采样数据另行绘制。

```python
from publication_components import stationary_energy_path
# 教学数据，不代表任何真实反应。state ID 在源表和对象映射中保持一致。
states = {
    'initial': {'energy': 0.0, 'x': 0., 'kind': 'minimum'},
    'reported-ts': {'energy': 1.2, 'x': 1., 'kind': 'transition_state'},
    'intermediate': {'energy': -0.4, 'x': 2., 'kind': 'minimum'},
    'unresolved': {'energy': None, 'x': 3., 'kind': 'state'},
    'later': {'energy': -0.8, 'x': 4., 'kind': 'minimum'},
}
order = list(states)
edges = [('initial', 'reported-ts'), ('reported-ts', 'intermediate'),
         ('intermediate', 'unresolved'), ('unresolved', 'later')]
result = stationary_energy_path(ax, states, order=order, unit='eV',
    edges=edges, plateau_width=.16, guide='smoothstep',
    open_endpoints=['intermediate'], bind=bind, prefix='route-A')
# 同一组源能级用于 slide：只改横向布局；平台宽度也以 x 数据单位定义。
# result = stationary_energy_path(slide_ax, states, order=order, unit='eV',
#     positions=dict(zip(order, [0., 1.5, 3., 4., 5.])), edges=edges,
#     open_endpoints=['intermediate'], prefix='route-A-slide')
```

`order` 明确需保留的状态及其顺序，状态必须具有 energy/x/kind（字段名可由参数更改）。`kind` 只允许 `minimum`、`intermediate`、`transition_state`、`state`，由调用者按来源声明；组件不从形状猜测或补造 TS。`unit` 必填；若源行另有 `unit`，必须一致。不同参照、温度、理论方法仍须在调用前核实。`positions` 完整覆盖此顺序的横坐标，用于纸面/幻灯片等媒介的独立排版；横坐标不是距离、时间或已知反应坐标，须据实标轴。源能级不随布局变动。

只有 `edges` 中显式给出的相邻状态对才有导引，默认为空；没有边就只画能级。`energy=None` 保留缺失状态记录但不画假能级；涉及它的边断开，不允许用跨过此状态的边偷偷连通。省略的状态无法由组件自动发现，因此不得为了连通图形而从 `order` 删除缺失状态。`guide=None` 只画能级，`linear` 使用直线，`smoothstep` 使用端点间的凸组合，保持端点精确且不产生区间外能量或额外极值；平滑形状仅为视觉导引，不是拟合出的 PES，也不是新证据。

`plateau_width` 为平台全宽，可为统一非负数或 ID→宽度映射；默认给 minimum/intermediate 画短平台，设为 0 可取消。`plateau_kinds` 可显式更改；宽度不得让相邻已声明边的平台重叠。`open_endpoints` 在明确未重建的有限末端画空心锚点，不延伸出虚构尾段；它必须没有通往另一有限状态的已声明出边。未标空心的末端也不自动意味着完整反应已结束。

返回 `source_states`、带原能级/类型/实际 x/单位/缺失标记的 `states`、实际绘制的 `segments`、`open_endpoints` 和 `artist_ids`。每个图元都有 SVG gid，`bind` 可同时登记 recipe 的对象映射；状态记录也带各自的图元 ID。调用者应把结果保存到项目映射，并分别核查源值与目标物理尺寸成图；数值不变量通过不等于视觉验收。

## 保持物理尺寸的独立导出

先明确最终尺寸的用途与来源，再传 `save_publication(fig, prefix, target_mm=(80,40))`；该可选参数会在写文件前拒绝不匹配的工作画幅，不自动缩小内容。80×40mm是本次Chemical Science TOC的已核实目标，不是所有图的默认值。旧调用行为保持不变。

已有PDF或其他后端输出可用 `audit_publication_size(pdf_path, (80,40))`（需PyMuPDF）。它返回实际页面毫米数、是否匹配/容纳于目标、等比拟合系数及可提取文字的原始/缩放点数；不修改文件，不判定美观或可读性。矢量转曲与栅格内文字不在提取范围，不能把未提取当作没有小字。应继续实际打开目标框内的图件。尺寸相符只是前提，不能用这个报告替代视觉验收。

`save_publication(fig, prefix, dpi=600)` 导出 `prefix.pdf/.svg/.png`，返回各文件路径。它显式关闭 tight crop，连全局 `savefig.bbox='tight'` 设置也不会改变页面尺寸，并对 PDF 中的栅格化图元应用导出 DPI。调用前先设置 `figsize`、排版和字体；组件不改变字体策略。现有 `research.py render` 已接受 visual 的 `export_dpi`，recipe 通过该入口导出时应设置该值，无需在 recipe 内重复保存；此函数供独立绘图脚本使用。

AI-Cat 精修曾出现 PDF 嵌图约 100 ppi，故验证必须看输出：PDF 页面物理尺寸与 `figsize` 一致，`pdfimages -list` 中相关嵌图达到指定分辨率。600 dpi 是此接口的默认导出值，不是所有期刊的统一要求；源位图本身不足时提高 DPI 不会增加真实细节，`interpolation='none'` 等保留原像素的方式也可能保留较低嵌图分辨率。此组件不能自动修复源图细节或证明出版达标。

## 新起稿的文字角色配置

`assets/publication-style-v2.json` 是可选的原生尺寸工作配置，复制到本地项目后以 style_profile 指向它；旧style-profile.json保持兼容。它区分面板字母、科学身份、正常标题、轴/刻度/说明与变量，采用常规字重标题，避免所有层级都靠粗体。字号不是期刊通用规定：目标期刊要求优先，并对照实际成图调整布局。混排的变量/单位/化学式仍按scientific-figure规则处理，不能给整句套italic。

2026-11-09实际重排中，能量路径与四TS由插图占据曲线空白改为两个配对面板；旧153.90×82.38mm工作裁剪改为官方Chemical Science双栏171mm宽、112mm内容高，主要文字7–8pt。条件图保持148.16×126mm并重新分配两排间距。它们支持“为文字层级重新分配版面”的制作动作；不支持任意大图直接缩小、所有图固定7pt或每张图都必须上下两层。原生对照须分别放置前后PDF，不能为了同宽预览暗中缩旧版/新版。
