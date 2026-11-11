# 来源与设计依据

2026-11-06 的补充比较见[公开 harness 的借鉴与边界](harness-comparison.md)；教材到具体改图的条件化原则见 scientific-figure 的 `references/design-principles.md`。以下早期调研状态保留历史日期，不代表这些来源之后从未读取。

本包依据用户提供的《通用科研可视化 Harness 设计与验证方案》文本实现第一版。原文提及的 23 页 docx 与 34 项完整来源未附在当前任务中，因此本包没有声称读取该文档或核查全部来源，也未复刻任何第三方 skill 代码。

## 本次直接核查（2026-10-23）

- [Munzner, A Nested Model for Visualization Design and Validation](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/)：作者页面摘要直接区分领域、任务抽象、视觉编码和算法四层。本包用它区分错误归因；不将其论文主张当成本包实现的验证结果。
- [Wilke, Fundamentals of Data Visualization](https://clauswilke.com/dataviz/)：核查作者书籍入口，作为按需查阅的数据可视化依据；本包不复制书稿或据入口声称已核查所有章节。
- [Jambor et al., Creating clear and informative image-based figures for scientific publications](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3001161)：原文摘要/介绍支持图像的对象、尺度、标注、颜色解释和可读性关注。它针对图像图件，不足以证明跨领域通用系统有效。本次没有确认用户调研中“该文提供问题—面板目的规划表”的具体归属，因此不把这点作为该文的已核实结论。
- [Whitesides’ Group: Writing a Paper](https://www.gmwgroup.harvard.edu/publications/whitesides-group-writing-paper)：核查作者组的出版信息入口；写作流程是对用户调研的综合实现，不宣称此次逐页复核全文。

## 综合设计建议

主张—证据—图件—正文关联、科学对象/关系与视觉规格分开、类型化修改、分项状态与合成回归来自用户调研的设计建议，并由本包实现相应软件机制。模式卡是设计种子，不是从真实参考论文测量所得；提取具体论文时应填图号、图注、正文定位和字段级 measured/observed/inferred/unknown。

## 保留为待核查扩展

nature-figure、K-Dense、PaperBanana 系列、AutoFigure-Edit、Crafter、GenGA、SciVisAgentSkills 及调研列出的新 benchmark 均未在此次做统一运行比较。本包不承诺兼容其内部接口、复刻其能力，或具有文献声称的性能。

`journal-profile.json` 中 ACS、Elsevier、Springer Nature、Nature 制作页面仅为原调研给出的官方查询入口。未填现行许可、日期或通用字号；投稿时按目标期刊、图件用途和工具作用核查，再填写适用条件及披露。

## v2 实证扩展（2026-10-23）

- [MatterGen Nature 期刊版](https://www.nature.com/articles/s41586-025-08628-5)、官方补充 PDF 与 Europe PMC PMC11922738 全文实际取得；查看 Fig1/6，核实 SI D.10.8/FigD12 的 nm/mN。原文为 CC BY4.0；数据依公开包 CDLA-Permissive2.0。
- [MatterGen 公开数据](https://github.com/microsoft/mattergen/tree/main/data-release)：本案例使用两份真实 CIF 与原始 XRD/压痕文件，保留实际来源摘要与仓库版本。不是重新训练/合成/性质拟合。
- [arXiv v2](https://arxiv.org/abs/2312.03687v2) 实际取得并查看 Fig1。与 Nature 是同一研究的版本关系，不能算独立科学证据；早期版本没有期刊最终实验 Fig6。
- 多期刊参考卡（位于同级 scientific-figure skill 的 assets/reference-library.json；项目初始化不复制整个库）：16 条版本记录，12 条指定实图已查看，4 条尚未取得。记录任务/布局/风格、观察与推断、访问状态；JPCL 补充条目为公开作者预印本，并非期刊终稿版式。
- 独立 OVITO skill 依据实际3.16环境与官方 API 编写，参考其他公开 skill 仅用于发现使用场景，未盲复制其版本/渲染器假设。官方来源与 Python 用例见该 skill 的 references/python.md。

当前已实现七类渲染，不代表七类全部科学推断均自动验证。参考库不是代表性期刊抽样，也没有跨论文统一审美效果或生产力实验。
