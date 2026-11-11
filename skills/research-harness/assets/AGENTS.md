# 科研写作与绘图项目

入口为 research.json；契约与覆盖范围见 harness-docs/contract.md，验收方法见 harness-docs/evaluation.md。先读现有输入与脚本，再改受影响的主张、语义、图件、图注和正文。

- 使用稳定来源/数据/主张/实体/关系/图件/段落 ID。来源、证据状态、科学语义与视觉表达分开；缺失不补零，假设不写成实证，示意线不冒充连续计算。
- 修改记录声明 presentation / interpretive / data、allowed_change 与 must_preserve。使用 scripts/research.py revise 可保留先前保护项并生成源规格检查点；原始输入单独保留。
- 期刊与媒介要求配置在 journal-profile.json。投稿前按具体用途和工具作用核对当时官方规则；unknown 不等于许可。
- 自动检查：python3 scripts/research.py check research.json。渲染：python3 scripts/research.py render research.json --out build。导出绑定：python3 scripts/research.py check research.json --export build。
- 报告 passed / failed / unknown / not_implemented；自动通过不等于科学正确或可读。不要用自报替代盲读。合成示例必须保持醒目标注。
- 图、图注、正文和来源一起交付。首次完成或新的故障证据出现时做相应验证，不为一次局部编辑反复运行所有验收。
