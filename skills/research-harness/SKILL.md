---
name: research-harness
description: 为科研论文写作与绘图建立或维护可执行本地项目，连接来源、主张、科学对象、视觉规格与正文，并执行渲染、定向修改及回归检查。适用于明确要求科研 harness 或跨稿件图表协作的任务。
---

# 科研项目 Harness

本 skill 提供共享项目契约和可运行工具。写作决策配合 `$academic-writing`，视觉决策配合 `$scientific-figure`；已有项目优先保留其格式和后端，不为一次小修另建系统。

首要任务是把用户希望表达的意义与材料能支持的逻辑共同打磨清楚，再编译成图形语言。版式、结构渲染和审美优化服务于这条逻辑；成图应能反读出同一个故事，而不是仅与参考图外观相似。

正式成图起稿前，将目标尺寸和依据绑定到具体用途（TOC／正文图／汇报）；工作画幅不能冒充刊载框。未知原图的历史尺寸不妨碍核查当前目标要求。按[制作循环](references/visual-production-cycle.md)处理信息取舍，可用[出版组件](references/publication-components.md)核对交付PDF尺寸；尺寸检查不判视觉通过。

## 作者还不知道画什么时

先读[材料归纳与故事共构](references/story-discovery.md)。以材料、困惑和读者认识变化启动，不要求作者先提供图型或完整故事。批量拆论文的证据链与图件职责，比较故事候选，再用草图与原话反馈逐步收敛。`story.json`保留来源观察、候选、面板/段落衔接及尚未决定的选择；宿主代理负责理解，`scripts/story.py`负责可检查的交接。

## 同一意图的不同表示

需要把研究故事用于论文图、正文和演示时，读[跨媒介叙事与变化检查](references/cross-representation.md)。沿用共同的 story/claims；明确请求本地 PPTX 时使用 `$ansatz-slide` 的固定版本实现，页面共享主张与证据，但按听众知识前提另行组织讲述顺序。外部研究源变化由 `scripts/representations.py` 提示复核，文件当前不等于语义或视觉通过。

用户直接给一篇论文要求汇报时，使用 ansatz-slide 的[论文入口](../ansatz-slide/reference/paper-to-deck.md)。由代理读取全文与关键图表、建立最小共享故事和来源定位，再制作整套汇报；不要求用户预先建立科研项目或逐页提纲。

用户指出“像demo、普通流程图、远不如原版”时，先读[用户反馈到制作动作](references/feedback-to-practice.md)，回到具体成图的失败层；该说明也覆盖完整汇报与TOC/Fig1的职责区分。

## 建立项目

将 `<skill>` 替换为本文件所在目录，使用可用的 Python 3.9+：

```bash
python3 <skill>/scripts/research.py init <project>
# 仅教学与验收：显式合成数据，不能混入真实研究
python3 <skill>/scripts/research.py init <project> --demo
```

当前有十二种后端：paired/table/energy/energy_network/methods/series/structure3d/catalyst_surface/toc/schematic/summary/recipe。schematic 不强制 dataset，用来源明确的概念场景；summary 要求数值和不确定性定义。新 toc 通过 scene_source_id 与 schematic 共用可编辑场景；原四块 toc 隔离为兼容案例。结构使用独立 `$ovito-structure`，依赖 `requirements-3d.txt`；Python 3.12、OVITO 3.16 的真实运行已验证。

`catalyst_surface` 面向有真实坐标的有序周期催化表面：登记 job 和所有状态文件，以共享相机渲染，保留基底周期像与单份吸附物，并在统一字体下叠加源原子标签和距离。它不要求 CSV，不负责确认反应机理或 TS。参数和独立/TOC 嵌入方法见项目契约；风格选择读 `$ovito-structure` 的催化表面参考。

复杂定量图可用项目自行编写并审阅的 `recipe`；它保留数据与对象绑定、字体审计及导出检查，不把任意 Python 执行当作科学验收。接口见[项目契约](references/contract.md)。

初始化生成本地 `AGENTS.md`、`research.json`、`scripts/research.py` 、高级后端、独立结构脚本、style profile 与参考/评估说明；不覆盖现有入口。真实项目先填研究问题与证据，空项目不是已验收项目。渲染依赖 Matplotlib；安装项目给出的 `requirements.txt` 到隔离环境，不修改全局 Python。

```bash
python3 scripts/research.py check research.json --out reports/check.json
python3 scripts/research.py map research.json --out reports/map.md
python3 scripts/research.py render research.json --out build
python3 scripts/research.py revise research.json operation.json
python3 scripts/research.py check research.json --export build
```

`check` 默认仅因已实现检查失败而返回非零。`--strict` 也因未知或未实现返回非零，适合明确要求完整验收的交付；它不赋予缺失检查任何能力。`render` 不等于科学、读图或出版验收。用户要求的成图应按实际刊载尺寸精修与查看，不以demo结案；原图忠实复现和改换图型的重新设计分别展示和验收。人工核验通过 `record-review` 绑定当前输入指纹，不得用代理自报充当独立盲读。

机制、状态与架构图需区分共同输出、竞争分支和循环恢复，并在实际图面追踪关系；科研汇报的新增图元需按约定保持最终载体可编辑。条件化方法见[关系图与编辑能力](references/relations-and-editability.md)。

新流程/网络/TOC 优先用对象锚点绑定实际箭头，使用分组、对齐和保比例资产；多路径能量图使用 energy_network。语法、参照边界与实际导出检查见[场景、版式与多路径能量图](references/scene-layout-energy.md)。

新图可选 `assets/publication-style-v2.json` 作为文字角色起点，按目标期刊和图件用途调整；不是通用字号规定。复杂配对图与局部能量差使用[可复用出版组件](references/publication-components.md)：物理尺寸分面、统一面板标题及源状态绑定的差值括号。机制图可嵌入 OVITO 渲染；真实坐标与经用户授权的 ASE 构造示意模型分别记录，不把材料插图当作定量证据。

## 按需阅读

- [首稿视觉决策与严格盲评](references/first-draft-and-blind-review.md)：复杂论文的TOC/Fig1/完整汇报先作主次取舍和不同构图；独立试验保留首次完整稿，并把实质返工与首交质量分开。
- [原生尺寸迁移的实际修正](references/native-size-transfer.md)：小字、公式层级、注释方向，以及主图与源任务重建分开验收的实际成图经验和边界。
- [真实数据与编辑入口范例](references/real-data-examples.md)：随包复制的条件地图、离散能量与真实TS；数据、代码、样式配置和来源俱全，区别可运行与视觉通过。
- [项目契约与命令](references/contract.md)：字段、四个关联结构、数据格式、修改类型及边界。
- [验收方法](references/evaluation.md)：分项检查、故障注入、五次连续修改、真实任务验收。
- [来源与设计依据](references/sources.md)：调研来源、已核查原文、未核查范围。
- `assets/patterns.json`：按科学任务、布局、风格三个索引检索的设计模式；这是本包的综合设计建议，不是实测最优结论。
- `assets/journal-profile.json`：目标媒介与出版政策模板；填写当时官方来源和核查日期后再用于投稿判断。

## 执行边界

数据和文献由用户资产或核实的来源提供；未知保持未知。现有验证器检查身份引用、来源文件、有限的图种约束、保留项和导出绑定；不证明统计推断、化学机理、因果或文字论证成立。遇到错误回到相应来源/语义/编码/渲染层，避免以反复美化替代诊断。自动检查报告和人工记录必须分别呈现。

实证验收样例：本包 `cases/mattergen` 保存公开论文来源、原始数据、参考图解析、写作、三种叙事、七张实图及五次连续修改。`reference-library.json` 是有界实图学习库，不等同于逐篇科学复现。字体审计覆盖真实文本属性；遮挡、符号语义、读者理解和出版要求分别报告。

用户要求复现参考图时，先对照实际原图，再核对对象/拓扑/字号与空间关系；`cases/visual-reproductions` 提供原图并排和源规格。程序通过不能替代成品的视觉验收，探索稿与原图驱动重建分别标记。

`assets/narrative-examples/index.json` 提供可编辑的流程、机理和结构示意模板。公共包泛化了项目名，并使用明确生成的定性景观资产；这些模板用于表达方式学习，不携带原用户研究结果，也不声明复现或普遍期刊规范。

复杂化学/能量/结构图及论文到汇报的实际制作，读[成图制作循环](references/visual-production-cycle.md)，使用源状态组件并检查最终导出。用户要求独立迁移验收时读[冻结与独立迁移](references/independent-transfer.md)，保留自主首交与外部辅助的区别。
