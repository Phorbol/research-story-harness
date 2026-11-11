# 条件选择性图：两条产物曲线 + 温度/时间条件图

这是从已有成熟四面板成图提取的独立可编辑范例。使用作者存档 H5 的真实计算数组，不使用合成数字。读者可以比较温度改变时线性/支化产物浓度及等选择性边界。

## 运行

在此目录建立 Python 环境并安装 `requirements.txt`，随后运行：

```sh
python /path/to/condition-map/run.py
# 可选输出位置（默认写入范例自身 output/）
python /path/to/condition-map/run.py --out /tmp/condition-figure
```

可从任意当前目录执行。无需历史案例、仓库脚本、网络或外部资产。交付包含 `output/condition-map.png`、`.pdf`、`.svg`。SVG 保留文字和曲线，热图是嵌入栅格；PDF 是固定 148.16 × 126 mm。字体默认 DejaVu Sans，以 Matplotlib 自带字体减少跨机差异。

## 编辑入口

- `data/data_a.csv`、`data_b.csv`：descriptor、L/B 浓度（M）；上排两个温度，均为24 h。
- `data/data_tv_t.csv`：descriptor × 温度 K，按 descriptor 外层、condition 内层排序。
- `data/data_tv_time.csv`：condition 是 log10(秒)，显示轴换算为小时而不改变格点。
- `config.json`：尺寸、颜色、字体、标题、L1/L2/L3参考线与输出分辨率；第二项参考线用于曲线比值标记。若替换实验/条件，必须同步更新标题和 `figure.py` 的轴及横线条件。
- `figure.py`：成熟四面板版式、等值线和坐标范围。替换 CSV 时必须保持完整规则网格及列名；这不是通用任意表格绘图器。
- `extract_source.py`：安装 `requirements-source.txt` 后，可从本包 `source/*.h5` 重建 CSV；此操作覆盖编辑过的 CSV，应先另存改稿。

## 科学边界

色标为 log10(L/B)，显示截在 ±2。双零灰色，单零按极限比饱和着色。等浓度线为模型中心预测，不是可靠性/显著性边界。没有重新求解微观动力学，也未重画不确定性区间；不能用本图替代模型或实验验证。保留显示域 −30…20，完整源域 −40…20 的负浓度插值伪影没有被静默修正。

原图 d–g 被重排成四面板，未包括原 Fig.4 a–c 的化学机理。来源、许可和本地处理见 `SOURCES.md`；实际目视及迁移测试见 `VERIFICATION.md`。

## 统一文字入口与实际尺寸

`config.json` 的 `font_family`、`text_roles_pt`、`text_weights` 是本例文字样式的单一入口。`axis` 对应坐标标题，`tick` 对应刻度，`legend` 对应图例，`annotation`/`small` 对应科学状态注释，`panel` 对应面板字母；能量图另有 `distance`、`footnote`，条件图另有 `colorbar`。字号单位是pt；`scientific_text_semantics` 记录正体/数学斜体/加粗语义。数字、化学物种、单位使用正体，变量仅在数学公式中斜体；加粗服务于面板与指定身份，不表示统计显著性。

两例字体统一为DejaVu Sans；保留各自成熟版式的字号比例，并未把高密度能量图强行套成条件图同字号。条件图轴7.8pt、刻度7.3pt；能量图分开路径与TS条带，状态7pt、轴8pt、图例/脚注7pt。按目标尺寸原生重排，不能整体缩小后沿用结论。调整字号后需要重新目视，程序不会自动解决碰撞。

2026-11-09样式修订：仅面板编号及科学身份承担粗体层级；详见 STYLE-REVISION.md。
