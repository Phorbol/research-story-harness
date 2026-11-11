# 拆解标注规范

先确认文本快照和源版本；精拆只覆盖当前有价值的部分。全文/章节/图表可先用单元级概括，逐步加深。当前 dissection schema 的 span 始终指向可检查的抽取文本；宏观解释也给出代表原文位置，不虚构全文覆盖。

## 必要区别

- 作者明确说“结果支持 M”：explicit 作者立场；是否科学上足以排除 N 另行评价。
- “这一句可能为下一段铺垫”：inferred 修辞分析，不存成作者声明。
- roles 可多选；observation、interpretation、qualification、motivation、comparison 等由任务决定，不把词表当普适分类学。
- propositions 是该单元表达的命题；support_relation 描述分析者当前判断，未判断用 not_assessed。
- unresolved 保存替代解释未排除、证据不可见、标签分歧和解析缺失。

## 原文位置

document_sha256 是文本文件字节的 SHA-256，仅用于绑定版本。start/end 用 Python Unicode 字符索引，而非 UTF-8 字节或 PDF 坐标。必须满足 `text[start:end] == quote`；locator 另外保存 section、page、paragraph 或 figure。页码无法确定时不编。

```python
from hashlib import sha256
from pathlib import Path
raw = Path('research/paper.txt').read_bytes()
text = raw.decode('utf-8')
quote = '需要标注的实际原文'
start = text.index(quote)  # 多次出现时选择并说明实际位置
span = {'document_sha256': sha256(raw).hexdigest(),
        'start': start, 'end': start + len(quote), 'quote': quote}
```

runtime 会拒绝新标注的引文/区间错配；来源更新后保留历史标注并标 stale，不能直接作为当前画像。跨页抽取、公式和图注仍需回原页检查。统计画像注明样本选择和标注方式；频率不能自动生成写作硬规定。
