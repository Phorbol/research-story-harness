---
name: context-pack-builder
description: "为学术论文构建可替换的期刊、研究设计、领域、体裁与作者上下文包，并将写作教材原则转成有条件的编辑策略。用于投稿适配和研究写作配置。"
---

建立有来源、有条件、有版本的上下文。先读 [共享数据契约](../argument-architect/references/contract.md)；按需读 [研究设计要求](../argument-architect/references/study-design.md) 和 [条件式编辑原则](../argument-architect/references/principles.md)。

## 五层上下文

分别建立 venue、study_design、domain、genre、author 的 context 记录。缺一层时明确缺失；可先用暂定画像继续局部工作，不虚构期刊要求或领域共识。

- venue：使用当前官方指南，注明文章类型、日期、适用条件、篇幅和声明要求。观察到的范文习惯不升级为政策。
- study_design：由实际研究设计决定论证责任；比较、机制、观察、理论、质性可以组合，不从期刊名或领域名推断设计成立。
- domain：术语、量纲、最近工作、竞争解释与边界。必要时按科学对象记录首选术语、合理变体、符号/单位和来源；同一简称有多个含义时在相应段落展开，不从五篇范文生成全领域禁词或固定替换表。科学事实仍进入具体主张的证据链。
- genre：段落任务、读者预设和常见组织路径；记录样本量和偏差，视为软性先验。
- author：当前项目已经接受的贡献边界、风格偏好和决策；不把一次局部改动推广成永久偏好。

## 教材原则

提取 purpose、trigger、diagnostic、operation、exception、invariants 六项。明确原则来自何种教材/资料及其条件；不要把未经阅读的书籍内容写成已核实引文。生成前只取与当前段落相关的少数原则，审阅时按实际问题扩大诊断。

## 产物与交接

遵循 context.schema.json，规则保留 source_id、basis、strength、condition；用 `put context` 登记依赖。corpus 和 pedagogy 规则不使用 must。样本扩大不会自行消除系统性标注偏差。

官方指南或作者决策更新后运行 `impact`，重新检查依赖的计划和正文。只要求润色时加载实际需要的层，不启动完整语料采集。
