# 公开方法的借鉴与本项目的检验范围

2026-11-06 核查以下项目的一手说明，结合此前本地调研；这是方法比较，不是安装运行后的能力排名。没有统一跑分，也没有证据说本系统审美领先。引用的质量主张属于原项目，不自动成为我们的能力。

| 参考 | 实际读到的设计 | 对本项目的可迁移策略与边界 |
|---|---|---|
| [K-Dense scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md) | 先定义证据与媒介，强调诚实编码、冗余颜色、作用域内样式、实际交付文件检查；精确尺寸时避免无意紧裁剪 | 保持统一语义色与线型，按毫米组版并检查 PDF。其完整性要求与我们有重叠，不能宣称为独有特色。当前局部能量差仍需领域语义组件 |
| [K-Dense scientific-schematics](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/docs/skill-guides/scientific-schematics.md) | 由明确组件/关系形成位图草稿，保留有限迭代与自动评论，要求最终人工核查 | 可学习“先写关系和视觉层级，再看实际图”的闭环；本项目需要精确值及连续局部编辑时保留数据/矢量层，不把位图重存为 SVG 当成可编辑图 |
| [PaperBanana](https://github.com/dwzhu-pku/PaperBanana/blob/main/README.md)，其说明链接到 [PaperVizAgent](https://github.com/google-research/papervizagent) | 参考检索、内容规划、风格、生成、评论构成迭代；项目说明承认更复杂/多领域场景仍需改进 | 学习按任务检索范例和内容/风格分工。这里描述的是阶段职责，不要求为每阶段创建代理。我们额外需要从模糊意图协作形成逻辑，以及与源状态、正文相连的可编辑对象；未验证第三方是否缺少这些能力 |
| [SciVisAgentSkills](https://github.com/KuangshiAi/SciVisAgentSkills) | 将 ParaView、napari、VMD、TTK 的环境、无界面渲染与工具知识拆为独立技能 | 借鉴领域工具能力独立封装；OVITO 负责坐标/相机/表示，故事层决定其证据职责。只核查说明，不声称已运行上述工具；部署说明仍须按本机核对 |

本项目的重点是 **意图共构 → 证据和逻辑修订 → 图形语言选择 → 可编辑生成 → 从图反读故事与分层验收**。这是一种组合方向，不是“别人只会美化”的判断。故事发现不是靠增加字段自动获得的能力；实际交互、用户纠正和图的阅读结果才提供证据。

当前沉淀的强弱证据分别是：源绑定与局部修改有运行和回归证据；教材原则有一手依据；版式策略有同一案例的前后图；跨领域可迁移性与独立读者理解仍待继续真实案例验证。下一次案例应针对现存薄弱点选择，先声明希望改善的读者判断，再比较原图、忠实复现和重新设计；三者不混为一项成功。
