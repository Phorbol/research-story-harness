# 同一故事，论文图与 Slide 两种表示

已有 `brief.txt`、`story.json`、`research.json` 的用户意图、选择、claims 和证据是共享源。先确定读者认识要发生什么变化，再选载体；论文图允许并行比较和反复细读，幻灯片按讲述节奏逐页揭示。面板和页面是多对多关系，不要求一图一页。共享的是主张、证据和限定，讲述顺序则由听众的知识前提与当下问题决定；同一故事不等于同一叙述路线。复杂论文的贡献取舍、理解依赖及两项独立审查见 [论文到汇报](../../ansatz-slide/reference/paper-to-deck.md#复杂论文的听众路径)，不把某篇成功页序固定为通用模板。

明确请求本地 PPTX 或 ansatz 时用 `$ansatz-slide`；其固定版本 CLI 负责可编辑页面、文字测量、导出、局部修改与版本绑定审阅。沿用已有 scientific-figure 绘图后端，不能把整张论文图简单缩到一页后视作完成媒介转换。

## 跨媒介转换中应保留的语义

论文图可同时呈现跨指标比较；汇报可按任务问题、关键对照、验证边界逐步解释。转换后核查标题与轴方向是否一致、主张主语是否改变、数值的分母和条件是否仍可见。相同 claim ID 或数值不变并不保证表达含义一致。

独立检验时，制作代理仅接收材料、任务和冻结方法；盲读者先看实际成图及正常图注，再对照预期故事和来源。来源审计、程序检查、制作自查和独立阅读分别记录；相同模型的独立上下文不是独立专家。每条视觉批评应指向完整导出中的具体对象，重新查看后发现误判就撤回，不能为了服从评语修改正确内容。

## 外部研究状态的变化检查

上游 ansatz 的 `needsReview` 追踪自己的页面、素材和叙事状态，不能自动感知外部研究文件更新。以下小桥接补此缺口，**不做语义证明、不自动重画、不自动登记视觉通过**。

项目中写 `representation-map.json`，例如：

```json
{"representations":[
  {"id":"Figure1","medium":"figure","path":"build/Figure1.pdf","claim_ids":["C1"],"source_paths":["data/results.csv","recipe.py"]},
  {"id":"Talk","medium":"slides","path":"talk/talk.pptx","claim_ids":["C1"],"source_paths":["talk/claim-page-map.json","data/results.csv"]}
]}
```

`claim_ids` 必须已登记。`source_paths` 填该产物实际依赖的数据、页面与源脚本；路径相对项目目录，也可绝对。请勿漏掉只在图注中提及的外部数据。

```bash
python scripts/representations.py capture --project . --map representation-map.json --out reviews/representations.json
python scripts/representations.py check reviews/representations.json
```

`capture` 仅保存当前依赖字节；不能用它抹掉待复核项。共享 brief/story/research/map 任一变化，保守提示所有表示 `needs_review`；局部源或产物变化仅提示该表示。`check` 发生变化返回 1，当前返回 0；都不修改输入。不分析哪些文字在语义上受影响，代理据实际主张决定复核范围。新版本的视觉审阅另行保留，旧盲读哈希不应冒充新图的审阅。

## 吸收上游模式的边界

参考 [ansatz-slides 固定版本](https://github.com/ansatzX/ansatz-slides/tree/2c5669a795722d9da9bdba81572d45db35b5d3c9)：叙事为状态、限定修改范围、失败后保留内容、分离程序/语义/视觉责任、验收绑定版本。保留其唯一 CLI，不另写 PPTX 导出器。其 gate 描述不是自动语义裁判，常规失败回滚不是崩溃原子性；作者偏好、委派和固定风格不移作当前用户要求。

ACS Catalysis 火山图迁移另暴露了一个局部风险：slide里的“L → B”可能把“主要产物偏好改变”画成物种转化。涉及催化选择性时，明确写 preference/偏好变化，只有原材料支持化学转化时才用物种之间的反应箭头。图内曲线读数标记也须与独立实验/计算点区分。这是跨媒介措辞与图形关系的检查，不要求所有slide增加声明框。

## AI-Cat留出的具体制作证据

2026-11-06最终整图/TOC/Fig1/10页汇报已实际查看并定向独立复核。可确认的改善包括：源能级共享、四TS同尺度细球棍、结构与能峰互指、开圆边界、原生大字号开场页，以及网络重排后的局部修复；不能据此称无辅助迁移成功。宽屏版的节点间距、共物种标签和箭杆需独立重排，纯粘贴或拉宽失败。详见[制作循环](visual-production-cycle.md)；本例仍保留密集文字需近读、无纸样及未做原生PowerPoint/WPS检查的边界。
