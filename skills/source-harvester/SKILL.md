---
name: source-harvester
description: "为学术论文检索或整理科学证据、范文、投稿规范和写作教材，记录用途、版本、原文位置及未覆盖范围。用于论文证据与范例收集；不用于普通网页检索。"
---

按用途建立可回查的来源集合。先读 [共享数据契约](../argument-architect/references/contract.md)，检索时再读 [检索方法](references/retrieval.md)。

## 输入与任务边界

使用已有研究问题、拟支持的主张、目标期刊/文章类型或具体表达难题。只给期刊和主题也能启动规范和范例检索；不要因此编造项目结果。先查看已提供文件与可用连接工具，不要求用户重复提供可读取的信息。

## 工作方式

- 把检索意图标为 scientific_evidence / rhetorical_example / venue_policy / pedagogical_principle / author_preference；同一来源可有多个用途。范文身份本身不能支持项目科学主张。
- 科学证据围绕最接近工作、竞争解释、反证和适用范围检索。范文优先匹配论证处境，再匹配主题和期刊。投稿要求查当期官方指南，区分 must、should、typically 和适用条件。
- 记录实际执行的查询、平台、日期、纳入理由、访问范围和未覆盖部分。仅摘要可用时如实登记，不声称已读全文。不绕过获取限制。
- 用 DOI、规范化标题、作者/年份和版本关系去重；预印本与期刊版保留对应关系和实质差别，不把两版当两份独立证据。
- 在用户项目内保留可检查的原文/抽取文本快照；公式、图表或关键图注回到原页检查。工具无法解析时保留 unavailable/unchecked，继续产出来源清单与缺口。

## 产物与交接

写入 source.schema.json 对应记录，用 `put source` 登记版本；查询日志与覆盖说明可另存项目的 `research/search-log.json`。需要结构化结果时再建立 evidence，标注真实数据、脚本、参数及输出位置。每次科学支持判断针对具体 claim 单独完成。

明确 URL 的公开文件可用附带 `scripts/fetch_source.py URL --output FILE --expected pdf|html|csv|text|json` 获取。HTTP 200、扩展名或落盘本身不说明取得正文：先核对文件类型，再核对标题/DOI、版本与内容覆盖。工具只执行前一项；遇到 HTML 验证页保留未获取状态，不登记为已核查 PDF。

来源或抽取快照变化后，先运行 `impact` 和 `audit`，将受影响证据、主张、正文交给重新核查。不要只更新参考文献条目后沿用旧核验。局部任务达到用途即停止，不设置固定全文篇数门槛。
