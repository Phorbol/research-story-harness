# 本轮来源与范围

目标论文：Worakul, Laplaza, Das, Wodrich and Corminboeuf, *Microkinetic Molecular Volcano Plots for Enhanced Catalyst Selectivity and Activity Predictions*, ACS Catalysis 2024, 14, 9829–9839. [DOI](https://doi.org/10.1021/acscatal.4c01175)。本轮只重设计 Fig.4d–g 的定量论证；没有重画原 Fig.4a–c 的反应与机理。

- `article.pdf`：EPFL 官方机构存档的出版排版稿。[来源](https://infoscience.epfl.ch/server/api/core/bitstreams/025e1484-6c09-4453-a933-a831bdb1e189/content)。原图尺寸从第5页嵌入图像的实际放置矩形读取，宽148.15996mm，高160.02000mm，见 `../reference/publication-size.json`。只裁出 d–g 时不放大至新宽度。
- `zenodo-v1.0.1/lcmd-epfl-mikimo-20cfc3a/`：作者软件2024-07-12存档v1.0.1，[记录12731466](https://zenodo.org/records/12731466)。原始API记录和zip均保留。
- `repository/lcmd-epfl-mikimo-1809a6d/`：[作者仓库](https://github.com/lcmd-epfl/mikimo) 2026-04-24提交1809a6d13143107d8bd163f23dc8fa1106323c43。它比论文晚，故另取2024存档。四个本次使用的H5文件逐字节一致；这证明版本一致性，不构成第二组独立科学证据。
- `supplement.pdf`：ACS Figshare官方补充材料，article26053671，file47110062，[下载来源](https://ndownloader.figshare.com/files/47110062)。S1展示不确定性方法及近等选择性区的限制；S4涉及280–400K自由能校正。当前图没有重画S1区间，不得声称区间不存在。

## 从源数值到本图

两张曲线使用 `examples/data/hf/vp/data_a.h5`、`data_b.h5` 的 `descr_all` 与 `prod_conc_`，不是 `prod_conc_pt_`。源文件已经包含作者的处理；本轮没有重新求解微观动力学，也没有重新获得未经处理的模拟输出。温度/时间图使用 `data_tv_t.h5` / `data_tv_time.h5`，网格维度为产物、descriptor、condition。时间数组是log10秒，显示为小时的对数坐标并不改变底层格点。

比值色阶为log10([L]/[B])，显示截在±2；这不是产率、活性或置信度。两浓度均零的格点是未定义，保留灰色；单一零按无穷比值饱和着色。原作者温度图的notebook会对NaN填值；本次不填，因此灰色局部与原图有意不同，不能称逐像素忠实复现。

源曲线完整域−40…20有负值插值伪影，原刊图和本图的显示域−30…20内无该问题；没有将负值偷偷截为零。`../review/source-check.json`保留独立核对的比值和范围。在温度图可见域x∈[−30,20]、T∈[280,400]内，有76个双零和4个仅L为零的格点；计数不包括域外数据。

等浓度线是模型中心预测的等值线，不是经统计验证的可靠选择边界。S1指出近50:50的细微选择性不可靠；当前成图没有提供不确定性区间。实际催化研究的可用性仍需独立验证。
