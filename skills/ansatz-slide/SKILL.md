---
name: ansatz-slide
description: 用户要求将论文 PDF、研究材料或已有科研故事做成汇报时，制作完整可编辑学术 PPTX，也支持现有汇报的修改与核查。用固定版本 ansatz-slide CLI 执行，保留证据与结论边界；无需用户先准备逐页提纲，不用于仅阅读或摘要论文。
---

# 科研叙事的幻灯片表示

本技能基于 ansatzX/ansatz-slides MIT 版本，归属与提交见 [provenance.json](provenance.json)。随目录携带唯一 Python CLI 实现；不复制第二套导出器。上游原始入口保留在 [reference/upstream-SKILL.md](reference/upstream-SKILL.md) 供版本比较（原目录及链接说明见 [归档说明](reference/upstream-archive.md)），其中上游作者的用户偏好、唯一风格、全文重读与委派要求不自动成为当前用户要求。

## 共用意图和证据

**直接给论文也可启动。** 用户说“把这篇论文做成汇报”，读取[论文到完整汇报](reference/paper-to-deck.md)，自行提取问题、论证、关键图表与限制，再创建讲述计划和成品；不要求用户先提供 story、claims、页纲或另装论文专用技能。已有科研项目则沿用其共享状态；没有项目时在本次输出目录建立最小来源／叙事记录，不另建互相冲突的事实体系。

先读当前科研项目的 brief、story、claims、数据来源与用户已有决策。图、正文和 slide 共享研究问题、主张、证据与限定，但论文论证次序和汇报的听众理解次序分别设计。页面可拆合、重排和改变信息密度；依据用途选择侧重点并记录省略，不另立冲突的中心结论或独立事实台账。保留已有 claim/source ID，在页面备注和投影映射中标明关联。

若 story 尚未落地，以已有明确用户 brief 为依据，标记投影状态，不把模型的提议写成用户批准。回写共享意图属于研究项目的明确修改，不由排版程序自动执行。跨表示冲突先解释证据与语义，再调整表示。

用户要求复杂论文的完整汇报时，交付应覆盖问题、方法必要性、关键证据、解释和结论边界，而非仅做几页风格样张。按听众阅读距离重组论文图：保留状态/路径/主张身份，必要时分步揭示；不要整图缩贴后仍沿用论文小字号。TOC、Fig1概览和方法图有不同任务，不复用一串箭头充当三种成品。已收到的成图质量否定须延续到对应页面，不能以故事可复述、导出成功或页面数覆盖；具体失败与纠偏见同套 `research-harness/references/feedback-to-practice.md`，没有该包时仍执行本段要求。

`deck brief` 接收 purpose、audience、centralClaim、sections；section.sources 是页面文件名，不是论文证据。`deck outline` 的 evidence 是说明性字符串，不验证科学支持。外部源/claims 的链接和新鲜度要保存在科研项目的投影映射；上游只跟踪自己的页面、素材和意图状态。

## 执行

完整复杂汇报的首稿采用同套harness的[首稿视觉决策与严格盲评](../research-harness/references/first-draft-and-blind-review.md)：先选择主次和讲述节奏；需要试页时选择论文实际存在的代表性读者任务，再扩成完整deck，不强制机制页或数据页；保留首次完整稿与自主自修。独立审阅按整套页序和实际PPTX渲染判断，不能把可读但未解决的视觉缺陷标成ready。

1. 读 [reference/harness-integration.md](reference/harness-integration.md)，确认共用意图、当前使用的证据和主张范围。
2. 按需要读 [reference/production.md](reference/production.md) 的环境、文件、最小示例，以及 [reference/production/cli.md](reference/production/cli.md) 的实际操作。技术字段见 [reference/technical.md](reference/technical.md)。上游的阅读方法、固定样式和LaTeX偏好是可选参考；当前任务和现有期刊/幻灯片设计优先。
3. 目录内用 `uv sync --frozen` 建隔离环境，再 `uv run --frozen python scripts/ansatz_slide.py --help`。Python >=3.11、PyYAML 6.0.3；受检导出需要 LibreOffice、Poppler 和可用字体，不改全局配置。
4. 从共享研究叙事生成页面候选、brief/outline及来源映射；按[论文入口](reference/paper-to-deck.md#把讲述计划变成可试讲的源稿)先试讲困难转折，把结果条件与实际口述、图面绑定。多页先 `deck preflight`，再 `deck import-pages`；修改用 `deck open` 返回的计划和 `deck revise`。按返回证据修复，不用 skip 参数绕过未通过检查。
5. 每页显示支持主张所需的单位、限定和文献定位。报告数值、模拟、示意明确区分；缺失值不补零。数值必须来自可追溯数据，不能凭论文图片估造。
6. 用户要求可编辑时，按[图示制作](reference/production/figures.md#最终ppt内的编辑能力)选择原生对象或明确的源编辑入口，不把随附SVG或PNG冒称PPT内已分层。检查实际 PPTX 渲染图；只有真实观察后才 `deck review ... --status reviewed --note ...`。导出成功、图片存在、历史测试通过都不是当前稿件视觉或科学通过。

## 各类保证的边界

- 程序：字段、资源、几何、版本与修改范围、实际文字容纳、渲染/包结构。
- 语义：模型/作者判断主张支持、前后推进、当前任务适用性和用户要求；CLI不会认证其正确性。
- 视觉：实际打开最终输出，判断字体替代、裁切、层次、可读性。记录引擎及仍有的限制。

源文件变化可能使 needsReview 变为真；它只表示复核需求。用户要求的归属由调用者提供，不是身份认证。事务提供常规失败回滚，不保证进程崩溃时多文件原子性。保留上游错误和修复记录，不通过删减科学内容换取几何通过。

交付 PPTX、源页面/素材、共享叙事投影映射与实测范围。正式全局安装由当前任务约定决定；准备目录本身不等于已安装或已在宿主发现。

复杂科研网络从论文转宽屏时，按[成图制作循环](../research-harness/references/visual-production-cycle.md)重新分配节点与标签，保留源身份。原生文字、曲线图片和结构资产须在最终PPTX渲染中一起复核；独立测试不得以主代理辅助精修冒充自主完成。
