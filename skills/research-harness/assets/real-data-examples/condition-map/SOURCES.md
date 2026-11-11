# 来源与归属

Worakul, Laplaza, Das, Wodrich and Corminboeuf. *Microkinetic Molecular Volcano Plots for Enhanced Catalyst Selectivity and Activity Predictions*. ACS Catalysis 2024, 14, 9829–9839. DOI: https://doi.org/10.1021/acscatal.4c01175 。对象范围为 Fig.4 d–g。

原始作者数据：mikimo v1.0.1，2024-07-12，https://zenodo.org/records/12731466 ，归档目录 lcmd-epfl-mikimo-20cfc3a。`source/zenodo-record.json` 保留作者记录与 **CC BY 4.0** 许可字段。此包复制其 `examples/data/hf/vp/data_a.h5`、`vp/data_b.h5`、`data_tv_t.h5`、`data_tv_time.h5`，未重新计算模拟。

源数据映射：曲线采用 `/data/descr_all` 与 `/data/prod_conc_`，不采用 `prod_conc_pt_`；网格采用 `/data/xint`、条件向量和 `/data/grid`，排列是 product × descriptor × condition。CSV 是作者数组的导出，随包提供可复查的原始 H5 和提取程序。

`figure.py`、`run.py` 与配置是本项目为这些公开数组编写的再表达，采用根目录 Apache-2.0；并非论文作者的原始绘图程序。作者数据保留 CC BY 4.0、来源版本与归属。使用随 Matplotlib 分发的字体；不包含原论文版面。

`source/historical-provenance.md` 记录数据版本与处理范围；其中作者仓库路径用于定位上游数据，不是本例的运行依赖。此记录与重复归档不构成独立科学证据。
