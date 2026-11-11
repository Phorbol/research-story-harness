# 来源与归属

Worakul, Laplaza, Das, Wodrich and Corminboeuf. *Microkinetic Molecular Volcano Plots for Enhanced Catalyst Selectivity and Activity Predictions*. ACS Catalysis 2024, 14, 9829–9839. DOI: https://doi.org/10.1021/acscatal.4c01175 。对象范围为 Fig.4 d–g。

原始作者数据：mikimo v1.0.1，2024-07-12，https://zenodo.org/records/12731466 ，归档目录 lcmd-epfl-mikimo-20cfc3a。`source/zenodo-record.json` 保留作者记录与 **CC BY 4.0** 许可字段。此包复制其 `examples/data/hf/vp/data_a.h5`、`vp/data_b.h5`、`data_tv_t.h5`、`data_tv_time.h5`，未重新计算模拟。

源数据映射：曲线采用 `/data/descr_all` 与 `/data/prod_conc_`，不采用 `prod_conc_pt_`；网格采用 `/data/xint`、条件向量和 `/data/grid`，排列是 product × descriptor × condition。CSV 是历史案例的作者数组导出，随包提供可复查的原始 H5 和提取程序。

绘图代码改自本项目 `cases/acs-volcano-transfer/production/final/generator/volcano_figure.py`。本次只去除历史路径依赖、提供配置和可重算比值注释、使用随 Matplotlib 分发的字体。不是作者原始绘图代码，也不把本次代码冒称由论文作者授权。历史本地代码未附独立许可证，此处不擅自添加许可。数据仍保留上游许可和作者归属；本包不附受独立版权约束的论文版面。

`source/historical-provenance.md` 是原制作过程记录，其历史相对路径仅供追溯，不是本例运行依赖。此记录与重复归档不构成独立科学证据。
