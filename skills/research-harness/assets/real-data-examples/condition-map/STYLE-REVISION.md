# 条件选择性图：同尺寸文字精修候选

本分支对来源 DOI 10.1021/acscatal.4c01175、Fig.4 d–g 的既有四面板再表达做呈现修改。原始范例的 `config.json`、代码和 `output/` 未改。`before/` 是原输出的逐字节副本；`source/` 保留独立可运行的新候选；`after/` 是当前导出。

## 读者任务与改变

先比较298.15 K和353.15 K、24 h时两种产物的浓度，再通过温度/时间地图定位等选择性边界及L1/L2/L3参考条件。读者应能关联温度图两条横切线与上排曲线，不能从该图推断误差范围、统计显著性或新的模型验证。

画布保持148.16 × 126 mm，未先扩大再缩小。刻度6.6→7.3 pt、参考标签6.6→7.4 pt、比值及科学说明6.8→7.5 pt、坐标标题7.2→7.8 pt。标题7.7→8 pt，图例7.5→8 pt，面板字母保持9 pt。仅面板字母加粗；L2不再额外加粗。两排间距略增，底部说明略下移，为更大的文字留出空间。

温度图横线原标注a/b改为“panel a / panel b”，明确是跨面板索引。曾试完整温度文字，但实际PDF中与L3竖线相交，已撤销该候选；精确温度仍在上方对应面板标题中。当前图中未增加新的科学主张。

## 实际查看记录

已打开原PNG、新PNG及最新Poppler PDF预览；最后还打开96 dpi的原生尺寸并排预览。观察到：新刻度和参考标签更易辨识；标题、坐标和状态标注有清晰层级；移除L2的粗体后，重点由曲线颜色和浓度标记承担；panel a/b标注完整落在L3右侧的地图区域，未被竖线穿过；上下两排及底部解释文字仍有间隔。曲线、等选择性轮廓、灰色0/0区及源网格颗粒均保留。

这是同一制作代理的有界目视记录，不是独立盲读或纸样验收；屏幕96 dpi仅近似物理阅读尺度。当前尺寸由已有范例及本次任务指定，不称期刊官方尺寸。

## 验证与交付

`verification.json`记录：数据CSV和before副本逐字节相同，所有浓度曲线/参考线/横切线的数值相同，两幅热图数组和mask相同，轴范围/刻度相同，原色彩与参考点不变；仅面板字母加粗；实际文字对象最小基础字号7.3 pt；文字均在画布内。PDF页面复核为148.160 × 126.000 mm。数学上下标在PDF中有更小字号，这是既有数学排版，不等于基础文本字号。

- `after/condition-map.pdf`：独立原生尺寸候选，另有PNG和SVG。
- `before-after-native.pdf`：左右各148.16 × 126 mm，无缩放；整页320.32 × 150 mm。打印请用100%，不用适合页面。
- `before-after-96dpi.png`：由上述PDF渲染的屏幕近似对照。
- `source/config.json`：供冻结新profile的候选；字号、字重、分面位置和切片标注集中在此。
- `verify_and_compare.py`：可重跑的针对性验证及1:1 PDF拼版。

命令（项目已有绘图环境）：

```sh
work/v2/render-venv/bin/python outputs/research-workbench/examples/condition-map/typography-refinement/source/run.py --out outputs/research-workbench/examples/condition-map/typography-refinement/after
work/v2/render-venv/bin/python outputs/research-workbench/examples/condition-map/typography-refinement/verify_and_compare.py
```

两命令均成功；9项针对性检查全部通过。完整上游来源与数据边界沿用 `../SOURCES.md`、`../source-data-check.json`。未重新求解动力学。0/0未定义、单零极限饱和、log10(L/B)显示截断至±2等语义保持不变。未做新论文迁移或中央skills修改。

环境备注：原生并排预览的Poppler命令返回0并生成完整PNG，但系统字体缓存配置产生警告；已实际打开结果确认两张图和标题均完整。此警告没有被计作字体检查通过；实际嵌入字体与字号另由PDF解析核实。工作目录没有Git元数据，因此不报告Git差异状态；本轮只写入typography-refinement，原输出逐字节对照通过。
