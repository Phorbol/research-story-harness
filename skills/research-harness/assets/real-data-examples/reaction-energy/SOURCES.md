# 来源、许可与推导

Pei-Lin Kang, Yun-Fei Shi, Cheng Shang, Zhi-Pan Liu. *Artificial intelligence pathway search to resolve catalytic glycerol hydrogenolysis selectivity*. Chemical Science 2022, 13, 8148–8160. DOI: https://doi.org/10.1039/D2SC02107B 。范围：Fig.5B的局部路径表达与SI Table S6（S17）能量推导，四结构对应原Fig.5的TS1–TS4。

原作者文章XML许可：Creative Commons Attribution-NonCommercial 3.0，https://creativecommons.org/licenses/by-nc/3.0/ 。原文permissions片段保留于 `source/article-permissions.xml`，copyright The Royal Society of Chemistry (2022)。数据与结构归属于上述作者；此包不替上游改发许可，非商业限制仍保留。

坐标来自作者补充文件 SC-013-D2SC02107B-s002.pdf：https://www.rsc.org/suppdata/d2/sc/d2sc02107b/d2sc02107b2.pdf 。原子坐标、晶胞和原子序号保留在四个extxyz中；源页码与身份在 `source/structure-mapping.json`。

| 本例结构 | 作者路径/Str | 0-based C–O原子对 | 坐标距离/Å |
|---|---|---|---|
| TS1 | path1 Str6 | 11–14 | 1.884 |
| TS2 | path2 Str6 | 10–13 | 2.009 |
| TS3 | path4 Str4 | 10–13 | 2.286 |
| TS4 | path3 Str4 | 11–14 | 2.560 |

能量CSV与 `energy-levels.json`、`late-energy-audit.json` 复制自本地 `cases/aicat-network-transfer/production/reconstruction`，后者保留S6行号和推导、后期路径不闭合的问题。G(next)=G(current)+Ga_forward−Ga_reverse；G(TS)=G(current)+Ga_forward。数据不是从曲线图像数字化。

代码改自同目录 `energy_panel.py` 和 `build_composite.py` 的B面板/四TS部分。仅改为包内路径、CSV驱动数值及TS数字标签、移除网络并裁出原B物理区域，面板字母改A。结构PNG与像素映射复制自本项目 `production/structure-assets/refined-four-ts/final`，保持原制作的视角和裁切，未重新渲染或优化坐标。

本项目独立编写的绘图代码采用 Apache-2.0，不是论文作者代码；论文来源数据、坐标和图像继续保留 CC BY-NC 3.0。`source/historical-structure-notes.md` 为原制作说明，其中其他未随包提供的资产仅作历史背景，不是运行依赖。
