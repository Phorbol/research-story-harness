# 共享数据契约

六个技能共用 `argument-architect/scripts/academic_harness.py`。以该文件所在目录解析 scripts 与 schemas，不根据当前工作目录猜路径。六个技能需一起安装；普通语言润色可不用状态库，不能把未登记核查的文字说成已验证。

## 三种表示与实体

1. 来源/计算：source → evidence。source 保留用途、身份确认和抽取状态、文本快照、来源位置及覆盖范围；evidence 保留定位、观察与可选的结构化结果、数据/脚本/参数/输出路径。
2. 论证：evidence → claim。claim 带命题、范围、推理依据、假设与替代解释；语义支持审阅独立记录并绑定依赖版本。
3. 表达：context + claim → plan → unit。故事/段落计划回答读者问题；unit 保存实际 Results、图注、摘要等文本与关联主张。dissection 保存范例多层标注；issue 保存具体问题、依据及完成条件。

数据格式见 [schemas 目录](../schemas/)，每类独立 JSON Schema。输入 `put` 时 version 可省略，由 runtime 管理；所有实体 ID 在项目中全局唯一。字段拼错或多余字段会被拒绝。没有独立科学实体的网页信息不要强行变成 evidence。

## 状态的含义

| 状态 | 使用条件 |
|---|---|
| supported | 阅读原材料后，认为材料支持当前范围和强度；所有提交的语义检查为 pass |
| partial | 支持一部分，需要明确保留限制；正文审阅需确认限定充分 |
| contradicted | 已检查材料与主张冲突 |
| insufficient | 已检查，但不足以支撑当前命题强度 |
| unknown | 当前没有足够材料或能力判断 |
| not_assessed | 尚未评价 |
| stale | 原判断依赖变化，不能直接复用；不等于命题已被反驳 |

`stale` 为派生状态，不能直接通过 assess 提交。原始文件未经登记直接变动也会使下游失效。evidence/context/dissection/plan 的登记依赖会被比较；先更新上游记录，再重新评价科学主张。重评 claim 会增加其版本，让依赖正文重新打开。

## 来源用途与检查层次

source.purposes 可多选 scientific_evidence、rhetorical_example、venue_policy、pedagogical_principle、author_preference。同一来源多个用途不意味着不同用途已同时核实。

identity_status=confirmed 是提交者的身份核查记录；extraction_status=checked 表示提交者已检查内容抽取。harness 要求 checked 有本地快照，检查字节漂移；不能独立核实原始出版身份、OCR 正确性或实验真实性。

本地 artifact 是项目内相对路径，不能逃逸到项目外。对 PDF 可保存抽取文本快照，locator 仍回到原 PDF 的页码、图表和版本；抽取工具与页面检查由宿主完成。缺失来源可以登记空 artifact，但不能作为 supported 的完整依据。

## 数字的三层保证

- `value_found`：断言数值与关联记录中的标量相同，仅表示找到相同数值。
- `record_matched`：subject / metric / value / unit / population / conditions / analysis_version 七字段完全匹配。conditions 按集合比较；不自动转换单位、舍入或容差。
- `supported`：提交的科学语义审阅认为当前证据支持该命题。代码不能从前两项推出第三项。

assertions 每项引用一个 evidence_id 和完整 record；定性证据可省 record，claim/unit 的 assertions 可为空。record 不完整的独立比较结果为 unknown，不能据此默认匹配。派生值或单位转换应另建 evidence，并写明计算与上游来源；不要为通过检查悄悄改原始数值。

scope 和 assumptions 的完整性、自然语言与 assertions 是否一致，仍由从原材料开始的审阅负责。正文少登记一个命题，程序无法自动识别；unit-review 的 extracted_propositions 是审阅者提取结果，不能代替独立校准。

## 修改与失效

新建正文可 `put unit`；已存在正文内容只能走候选补丁。改变科学命题用 `put claim` 后 `assess`，再构造正文候选；patch.claim_delta 必须为空。补丁声明完整 read_dependencies，既含文本版本也含传递的证据/主张/上下文版本。无文本冲突但依赖已变，仍不能接受。

正文反向提取实际命题，检查相对计划的新增事实、必要内容遗漏、限定丢失和范围扩大。语料统计、期刊均值、自动 reviewer 分数不能替代这些判断。局部模式不强迫建立完整全稿状态。
