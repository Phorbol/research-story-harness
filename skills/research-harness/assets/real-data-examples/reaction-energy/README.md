# 局部反应能量 + 四个真实坐标 TS 结构范例

本例保留历史成熟组合图的完整 B 面板：四条初期路径、蓝色路径续接、四个真实坐标过渡态结构及 C–O 距离。**这是局部能量与结构组合范例，不是完整反应网络的缩略替代品。** 原网络 A 面板的分子图与反应拓扑不在此包中。

## 运行

安装 `requirements.txt`，然后从任意当前目录执行：

```sh
python /path/to/reaction-energy/run.py
python /path/to/reaction-energy/run.py --out /tmp/reaction-figure
```

默认输出 `output/reaction-energy.png`、`.pdf`、`.svg`。当前PDF宽171 mm、高112 mm：上方能量、下方四TS，按目标宽度重新分区；不是将原组合图裁剪后缩放。SVG/PDF 的曲线、文字和距离标注可编辑；原子结构是嵌入的透明高质量位图，不虚称矢量原子模型。

## 编辑入口

- `data/energy-values.csv` 是运行时数值来源：id、path、state、stage、G（eV）。保留行序和路径/状态身份；所有绘图纵坐标从此读取，TS数字注释也从此读取。图中标签的摆位仍在代码中，改能量后需实际查看以调整标注。
- `energy_panel.py`：四路径位置、颜色、线型、状态文字与成熟曲线布局。横轴是反应序列，不是时间或经采样的反应坐标。平滑线只是离散稳态能级间的视觉引导，不是连续PES计算。
- `config.json`：字体和导出dpi；`run.py`：结构插图位置及距离注释样式。
- `assets/refined_TS*.png` + `TS*-metadata.json`：真实坐标结构渲染及源原子像素位置；`vector-overlays.json` 给出距离原子对。
- `source/*.extxyz` + `structure-mapping.json`：四个作者原始坐标与SI页码、Str身份。结构PNG已经制作好，默认运行不需要OVITO。**本例不提供重新渲染三维结构的后端**；若换坐标，必须重新生成结构PNG及原子像素映射，不能只改距离数字。
- `data/energy-levels.json` 与 `late-energy-audit.json` 是历史推导/来源记录，不是第二套运行时能量输入；CSV改稿后它们仍表示原始来源值，不会自动更新。

## 必须保留的边界

473 K，以气相甘油G=0，采用SI Table S6的库/共吸附物约定。初期G与TS来自正反向势垒累加；只允许蓝色路线按其自身约定继续。其他三条线的空心终点表示后期状态映射未解决，不能直接补成同一闭合能量终点。不能宣称精确复现原 Fig.5B、所有路径热力学闭合或独立验证TS。

结构来自作者坐标（不是从图片猜测），但TS标签是既有案例依据路径与结构序列建立的映射。原子距离不证明键级或机理。源坐标绝对VASP能量不能替代473 K相对Gibbs能曲线。

来源、许可与修改范围见 `SOURCES.md`；运行与目视记录见 `VERIFICATION.md`。

## 统一文字入口与实际尺寸

`config.json` 的 `font_family`、`text_roles_pt`、`text_weights` 是本例文字样式的单一入口。`axis` 对应坐标标题，`tick` 对应刻度，`legend` 对应图例，`annotation`/`small` 对应科学状态注释，`panel` 对应面板字母；能量图另有 `distance`、`footnote`，条件图另有 `colorbar`。字号单位是pt；`scientific_text_semantics` 记录正体/数学斜体/加粗语义。数字、化学物种、单位使用正体，变量仅在数学公式中斜体；加粗服务于面板与指定身份，不表示统计显著性。

两例字体统一为DejaVu Sans；保留各自成熟版式的字号比例，并未把高密度能量图强行套成条件图同字号。本轮条件图轴7.8pt、刻度7.3pt；能量图分开路径与TS条带，状态7pt、轴8pt、图例/脚注7pt。按目标尺寸原生重排，不能整体缩小后沿用结论。调整字号后需要重新目视，程序不会自动解决碰撞。

2026-11-09样式修订：仅面板编号及科学身份承担粗体层级；详见 STYLE-REVISION.md。
