# 固定材料的组件对照

只在需要评价组件收益时使用，不给普通局部写作增加实验流程。

先冻结任务、来源读取范围、模型配置、各格调用和篇幅预算、评分规则；规划 on/off 必须说明是有无显式外部计划，不能称关闭内部思考。范例 on/off 说明候选库、真实检索方式、排除自身、选择理由以及原文/释义区别。相同调用数和正文长度不是相同隐藏 token 或费用；记录宿主实际上能落实的约束。

每格用新写作上下文，不向无模块组泄露计划或范例；保留一次原始输出和违约记录，不通过重试择优。若整体加载技能会向无规划组泄露规划要求，可做明确披露的指令级组件实验；不能称为整套技能的端到端效果试验。

匿名包从结构化 unit.text 或 `export --blind` 构建，不从带审阅标签的工作稿裁去标题后直接使用；检查残留HTML状态注释。发现泄漏保留污染记录，只重跑受影响评审，不改原科学正文或实验组输出。

评审只看匿名正文、必要任务场景、可定位原材料和冻结 rubric，不看计划、历史得分或条件映射。两份独立评审及原稿冻结后再解码、核查分歧和改技能。隔离上下文不是文件权限隔离；同模型评审仍可能共享盲点。科学误写去重，贡献缺失和可选细节分开。保留原评分，作者复核另列，不悄悄覆盖。

```bash
python3 /absolute/path/to/argument-architect/scripts/ablation_eval.py experiment.json
```

输入对象包含 cells 和 reviews。每个 cell 有 draft_id、paper_id、argument_plan (0/1)、retrieved_example (0/1)、material_sha256、model、budget。每位 reviewer 有 reviewer_id 和覆盖全部稿件的 ratings：draft_id、scientific_issues、contribution_score、qualification_score。评分为 0..4 整数；每项问题包含独立 error_key、severity (minor/major/critical)、draft_quote、source_locator、reason，建议另存 suggested_fix、理由和缺失项。去重是标注者的工作，程序仅拒绝重复 error_key。

脚本拒绝不完整/重复的2×2、同篇材料标识不一致、跨格模型/预算描述不一致、缺失/重复评审和无效评分。它只检查申报配置，不证明真正执行一致。保存正文、计划、来源选择器和映射另供核查；哈希绑定身份，不验证科学有效性。

对每篇先平均评审评分，再算规划主效应 ((10−00)+(11−01))/2，范例主效应 ((01−00)+(11−10))/2，交互 11−10−01+00；按论文平均。00、01、10、11先规划后范例。错误率越低越好，贡献/限定分越高越好。评审重复评分不是独立论文，旧稿若任务/篇幅不同，单列审阅，不能作组件基线。

报告逐篇结果与分歧。全组未检出错误或评分触顶意味着检验分辨力不足；不能宣称没有错误、两个模块等效或模块无效。小样本、单次生成、已发表材料及可能训练重叠的结果只用于定位失败模式。修复后行为收益需要新材料、新种子或独立前向检验，不能用同批评分验证修复本身。

## 来源交接、校准与版本比较

写手可用的事实材料（含Methods、原始CSV和派生计算记录）应完整交给评审；写作计划、条件映射和过程说明另存。以写作输入生成required来源清单，评审输入生成available清单，用 `scripts/review_handoff.py manifest.json` 检查source_id/sha256覆盖及版本一致。它只核对申报来源，不证明读取、实际工具权限或科学支持。Methods漏交时先补材料，不把评审者没有依据归为作者误写。

用 source-derived gold 与科学上正确的对照校准识错；可加入仅文风不佳的正确对照，检查是否把保守或不流畅当科学错误。金标准先回原材料独立核对，评分门槛先设定。`scripts/calibration_eval.py input.json` 接受gold、reviews、matches：gold每稿有draft_id与errors（每个gold_id唯一）；reviews为reviewer_id/ratings，每条含draft_id/scientific_issues；matches由核对者提交reviewer_id、draft_id、issue_index和gold_id。该脚本拒绝重复或错位匹配，报告precision/recall/specificity，零分母为null；不自动判断文本是否命中金标准。合成错例上的检出率不代表自然稿件表现。

评审上下文改变后，先前校准不能证明当前上下文有效；可在正式匿名包混入少量已知正确/错误控制项，仅用于检查当前审阅过程，排除于写作效果统计。已有控制项的重复使用不是新的独立校准证据。

验证修复收益时，两版本使用同一批新材料；不能把旧的完整材料结果与新的杂乱材料结果直接相减。`scripts/paired_eval.py input.json` 接受cells、reviews和明确的version_order（基线、候选）；跨版本同篇同格的材料、模型、预算必须一致。每版本仍须完整2×2，评审覆盖全部稿件；控制项先单列，不能混入论文效果。除原科学/贡献/限定指标，还读取domain_register_score、terminology_consistency_score（0..4）和unnecessary_defensive_clauses（带原句、理由的标注列表）。保留方向：误写与冗余防御越少越好，贡献/表达评分越高越好，不用合成总分抵消科学错误。

评测取材配方可以指定某篇的页码、数据列和筛选条件；这些研究fixture不属于通用引擎的科学判定。运行时不按论文身份/结果值给支持结论，也不从五例提炼全领域禁词。未见材料与作者真实项目的行为仍需另外验证。
