# 本地 harness 使用

Python 3.9+，只使用标准库。以下 `HARNESS` 是完整脚本路径，例如安装后的 `~/.codex/skills/argument-architect/scripts/academic_harness.py`，`PROJECT` 是作者指定的研究项目目录。不要把包含空格的路径拆成多个参数。

```bash
HARNESS="$HOME/.codex/skills/argument-architect/scripts/academic_harness.py"
PROJECT="/absolute/path/to/research-project"
python3 "$HARNESS" --project "$PROJECT" init
python3 "$HARNESS" --project "$PROJECT" put source source.json
python3 "$HARNESS" --project "$PROJECT" put evidence evidence.json
python3 "$HARNESS" --project "$PROJECT" put claim claim.json
python3 "$HARNESS" --project "$PROJECT" assess claim-review.json
python3 "$HARNESS" --project "$PROJECT" put unit results.json
python3 "$HARNESS" --project "$PROJECT" review-unit results-review.json
python3 "$HARNESS" --project "$PROJECT" audit
```

`source.json` 等是宿主根据实际材料编写并提交的 JSON 文件，格式见 schemas。若用户没有提供目标目录，先在任务工作区创建项目，不把真实项目数据写入技能安装目录。

## 查阅与检查

```bash
python3 "$HARNESS" capabilities
python3 "$HARNESS" validate claim claim.json
python3 "$HARNESS" --project "$PROJECT" inspect C1
python3 "$HARNESS" --project "$PROJECT" deps UResults UCaption UAbstract
python3 "$HARNESS" --project "$PROJECT" impact S1
python3 "$HARNESS" --project "$PROJECT" review-template C1
python3 "$HARNESS" --project "$PROJECT" review-template UResults
python3 "$HARNESS" --project "$PROJECT" history
```

review-template 只生成带空理由和 unknown 检查项的待填写结构，不会生成肯定结论。阅读原始材料后再填写。unit-review 的 text_sha256 计算 UTF-8 文本字节；模板提供当前文本值，候选需用候选全文计算。保存候选、审阅与 diff 便于人工查看。

`audit` 成功返回 JSON 的退出码是 0，即便 final_export_ready=false；它表示检查执行成功。消费者必须读取状态，不能把退出码 0 当论文通过。输入无效、依赖过期或接受被阻止时退出码 2。`export --final` 不满足条件也以 2 退出并不写输出。

## 候选补丁

patch.schema.json 的 replacements 是完整 unit 对象，version 为当前版本 + 1。affected_units 与 replacements 的 ID 严格相等。base_revision 记录提案读取的全局版本；合并依据是完整依赖版本，不因无关事件使全部并发候选失效。

read_dependencies 从 `deps` 获得，覆盖 affected_units、issue_ids 以及新增引用的全部实体和传递上游。issue 必须 open；disputed 问题要先有作者决定，不能默默关闭。claim_delta 非空会被拒绝，先重开科学决策。

跨单元问题在 issue.affected_units 明确列出需同时修改的位置；程序要求补丁覆盖这些单元才能关闭该问题。该字段为兼容 0.1 历史记录保持可选；旧问题只有自由文本 location 时，覆盖检查仍依赖人工审阅。

```bash
python3 "$HARNESS" --project "$PROJECT" propose patch.json
python3 "$HARNESS" --project "$PROJECT" diff P1
python3 "$HARNESS" --project "$PROJECT" accept P1 --review patch-review.json
python3 "$HARNESS" --project "$PROJECT" reject P2 --reason "保留条件丢失，当前不接受"
```

accept 的 review 覆盖每个指定问题、每个候选单元与确切文本摘要，并提交未引入严重错误、保留正确内容和表达改善的依据。若任何一项不通过，内存中的部分改动不会提交；可把独立问题分成不同补丁分别验收。首次 draft 可直接登记为 unreviewed，后续不能用 put 覆盖文本绕过候选流程。

## 更新材料

1. 保存新的原材料版本；使用 `put source` 更新快照摘要和来源版本。未登记的文件改变会被 audit 发现。
2. 用 impact 查看依赖。重读并更新 evidence（必要时保留记录但重新确认其来源版本），以及受影响的 context/dissection/plan。
3. 更新并重新 assess claim；范围可能缩小、支持状态可能降低，不能为了通过检查维持旧结论。
4. 对 Results、图注、摘要和其他受影响位置提候选并重新审阅。导出新版本文件。

状态变化不会自动改写科学结论或替作者选故事。所有影响来自登记的依赖；未登记的事实和引用无法由版本图发现。

## 导出、检查点与停止

```bash
python3 "$HARNESS" --project "$PROJECT" export "$PROJECT/draft-v1.md"
python3 "$HARNESS" --project "$PROJECT" export "$PROJECT/manuscript-v2.md" --final
python3 "$HARNESS" --project "$PROJECT" stop --reason "需要新的实验数据"
python3 "$HARNESS" --project "$PROJECT" resume --reason "作者已提供新数据"
python3 "$HARNESS" --project "$PROJECT" budget --max-accepts 8 --reason "本轮最多接受八个补丁"
python3 "$HARNESS" --project "$PROJECT" restore-prose CHECKPOINT_FILENAME.json
```

盲审包可用 `export "$PROJECT/anonymous.md" --blind` 导出正文与单元类型，不带版本、unit ID、审阅状态及harness生成的HTML注释。它不要求最终通过，也不改变原状态；不能将它称为最终导出。优先使用该模式或结构化 unit.text，不要仅切除Markdown文件头后保留审阅注释。它不自动匿名化正文中的作者/条件信息、文件名、计划或来源；给评审前仍需按实验实际检查。

工作稿保留各单元检查标签；final 仅允许当前主张 supported/partial、正文审阅当前、数值绑定一致、无未解决的 major/critical 问题和原文件漂移。partial 需要审阅确认正文限制充分，代码本身不能证明。final 是本地导出状态，不能称作科学有效或可直接发表。

检查点在 `.academic/checkpoints/`，HEAD 原子替换是提交点；历史文件不覆盖。restore-prose 以新修订恢复已有单元的历史文本，保留当前证据/主张并使恢复文本待审。它不删除后来新增的单元、不撤销问题状态，也不回滚科研数据。

写入锁文件 `.academic/writer.lock` 含 PID；冲突立即停止，不盲目重试。不自动删除疑似遗留锁：确认没有运行中的写入者后才清理。断电级文件系统持久性、任意外部编辑/删除状态库、防篡改与跨主机锁不在保证范围。多个候选可串行提交，不实现工作进程调度。

默认本轮接受补丁上限为 20，可明确调整；只有已接受补丁计数。没有 token/费用/时间硬限制。重复回到此前已接受的文本会阻止自动接受，需要停止并记录作者决定。无改进、观点反复或需要新材料时，也由宿主停止；没有自动无限修订循环和重试机制。

## 面向读者的清洁导出

`export "$PROJECT/manuscript-clean.md" --final --clean` 先通过原有最终检查，再仅导出正文与单元类型，不带版本、审阅状态和unit ID。原科学正文不变；`--clean`只改变呈现，不改变审阅、来源或未解决问题。`--clean`也可用于工作稿；`--blind`保留原义。清洁不等于身份匿名化，正文中的作者信息和实验条件仍需按任务核查。
