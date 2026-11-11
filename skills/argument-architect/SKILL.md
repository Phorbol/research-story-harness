---
name: argument-architect
description: "根据科研材料建立可追溯主张、贡献边界、故事备选与图表段落计划，并协调学术论文起草和增量修订。用于从材料构建论文或维护论证；局部润色可直接使用 manuscript-editor。"
---

让作者明确目前能够说什么、为什么值得说、怎样让读者理解。核心状态由本技能附带的 Python harness 管理；学术判断由读取原始材料的作者/代理完成。

先读 [共享数据契约](references/contract.md)。使用状态或补丁时再读 [运行方法](references/runtime.md)。评估科学支持时读 [科学审阅](references/scientific-review.md)，按研究设计选读 [设计要求](references/study-design.md)。

## 任务路由

根据任务选择所需工作，不强制完整流水线：来源收集用 `$source-harvester`，范例分析用 `$paper-dissector`，政策/教材和偏好用 `$context-pack-builder`，起草与 polish/draft/restructure/adapt 用 `$manuscript-editor`，核查用 `$manuscript-auditor`。这六个技能随同一套件安装；不假定宿主支持自动代理调度。并行或委派按当前会话授权执行。

## 从研究材料建立论证

先检查真实数据、日志、脚本、图表和已有稿件，区分原始观察、派生量、推断和作者目标。关键结果建立 source → evidence → claim 的链接；可计算数字绑定对象、指标、数值、单位、人群、条件及分析版本。记录数据—脚本/参数—输出—图面板的路径，不把可追溯性当作研究设计正确的证明。

claim 写成可独立判断的命题，带 scope、warrant、assumptions、alternatives、evidence_ids。来源身份、内容抽取与主张支持分别判断。状态可为 supported、partial、contradicted、insufficient、unknown、not_assessed；旧判断受材料或依赖变化影响时显示 stale。没有材料时形成缺口清单、可填充大纲或有支持的局部段落，不编造结果。

围绕读者认识变化提出少量有实质区别的故事备选，比较各自需要哪些主张、已覆盖哪些证据、缺什么。数量按任务决定。相对最接近工作陈述具体差异与范围，不用未限定的“首个”“全面优于”掩盖检索或证据缺口。

用 plan 记录故事选择、图表/段落使用的主张与证据、每段的读者问题和下一步认识。需要贡献表达时，计划应包含具体方法/认识改变及其用途；把论文原贡献与此次重构、表格复算或故障测试的操作贡献分别表述。高风险段落再做句级规划；其他段落保留表达自由。计划不能把 unknown 自动变 supported。

## 写作与更新

编辑者提出候选文本；审阅者从实际正文反向提取命题，再回原始材料判断，避免只把台账与稿件互相核对。主张或证据变动时，运行 `impact` 和 `audit` 定位正文、图注和摘要；先重开科学判断，再接受文字补丁。

使用附带 CLI 时主稿为 `.academic/HEAD` 指向的检查点；候选通过 `propose`、`diff`、逐问题 `accept` 或 `reject` 处理。局部风格修改仍需保留因果方向、否定、比较对象、数值归属、范围和不确定性。不能用总体评分抵消严重错误。

## 实际保证

`python3 scripts/academic_harness.py capabilities` 显示代码已实现与未实现的能力。schema、版本、原文件漂移、单写入锁和补丁前置条件是程序检查；科学支持、正文命题抽取和具体问题是否解决仍依赖提交的审阅，不声称具有自动语义证明、工具权限隔离或已启用宿主 hooks。

做固定材料的组件对照时读 [对照评测](references/ablation.md)；汇总入口为 `scripts/ablation_eval.py`，不调用模型或产生科学标签。

停止于当前任务满足、需新数据/作者判断、收益耗尽或明确预算边界。首版预算只限制接受补丁数；需要 token/时间/费用上限时由宿主落实，不能假称已生效。交付时报告实际修改、检查结果及仍未解决的问题。
