# 场景、版式与多路径能量图

用于流程/反应网络/TOC 的关系编辑，以及同参照的离散多路径能量图。先确定科学对象和读者任务，再使用这些组件；它们不会自动选择故事或证明机理。

图面关系的设计与最终载体的编辑能力先读[关系图与可编辑表达](relations-and-editability.md)。以下锚点语法只保证端点如何定位，不保证科学语义或视觉效果。

## 一个场景承担不同传播用途

新 TOC 使用 `kind: "toc", mapping: {scene_source_id: "SceneSource"}`，与 schematic 共用场景、字体和物理尺寸。不要把主流程图直接缩成 TOC；TOC 提炼主要研究动作与贡献，主图保留必要的研究决策。旧 blocks/linear/evidence_hub/comparison 路由仅是兼容的 MatterGen 案例，隔离在 legacy_mattergen_toc.py，不能套到新研究。

场景 `schema_version:2`、`canvas:[宽,高]`，推荐单位 mm；y 向上。原有图元及科学身份不变。

```json
{
  "layout": {"groups": [{"box": [5,10,80,20], "direction":"row", "gap":10,
                         "weights":[1,1], "children":["input","process"]}]},
  "objects": [
    {"id":"input","type":"rect","semantic_id":"Input"},
    {"id":"process","type":"rect","semantic_id":"Process"},
    {"id":"input-label","type":"text","semantic_id":"Input","text":"Inputs",
     "anchor":{"object":"input","port":"center"},"role":"body"}
  ],
  "connections":[{"id":"feed","from":"input","to":"process","meaning":"data_flow",
                  "basis":"conceptual","draw":{"from_port":"east","to_port":"west"}}]
}
```

这是局部语法示例，还需已有的来源、track、geometry_basis、scope_note 和 canvas 字段。分组可用 `parent` 对象与 `padding` 代替 box；按声明顺序解嵌套分组。column 从上到下，row 从左到右。一个对象只能加入一个分组。

文字 anchor 可加 offset；图片/矩形可用 anchor、size、self_port。图片 `fit:"contain"` 保留原比例。港口名为 north/south/east/west/center 与四个角。draw 可加 color_role、lw、head、linestyle、connectionstyle，或给 `via:[[x,y],...]` 明确通道。通道点保持绝对坐标，改布局后须复查通道；端点始终由源/目标对象解析。不提供通用自动避障或最优布局保证。

`narrative-map.json` 保存解析后的实际几何及连接身份。`layout.json` 报告文字框交叠、页面外文字和箭头与文字框交叉。检查的是可见路径和文字边界候选，不是阅读理解、材料遮挡或审美认证。文字过密先减去次要内容或重排，不自动缩字。实际 PDF 的栏宽与正文上下文仍要查看。

## energy_network

每个状态一行，稳定 ID 与 entity 对应。共享中间体只保留一个 ID、一组数值和进度位置。dataset 需 reference、energy_type、conditions、uncertainty；没有误差时声明来源未报告，不补误差条。mapping：

```json
{"value":"energy","x":"step","state_kind":"kind","label":"label",
 "paths":[{"id":"routeA","label":"Route A","states":["R","IA","P"]},
          {"id":"routeB","label":"Route B","states":["R","IB","P"]}]}
```

kind 列为 intermediate / transition_state。paths 的相邻边必须与 figure.relation_ids 的 transformation 精确对应；entity_ids 与所选 CSV 状态一致。选取论文子集时保存独立派生 CSV 和选择原因，不静默丢弃原始数据。所有路径要求共同参照和同一种能量；不同条件/催化剂的局部零点须分面或另图，不能合成全局路径。循环先明确展开为可追溯的状态实例；本后端不自动处理循环展开。

visual 支持 label_states、state_label_offsets（pt）、show_values、value_format、platform_half_width、legend_location、y_limits。位置轴只表示离散反应进度。平台高度绑定数据，直连接线只是视觉引导；未报告的 TS 不画峰，不从中间体高低推出活化能或速率控制步骤。PDF/SVG/PNG 与 data-map.json 同时导出。

## 连续修改

修改节点位置优先改分组/锚点；不要另画一条看似正确的箭头而保留错误关系。标题内容与颜色变化属于 interpretive，字号与采样密度仍为 presentation。分类只按字段保守路由，文字是否改变科学主张仍需核对源材料。JSON 修改历史不备份外部 scene 文件；为场景修订保留版本文件，再更新 source.path。

新材料验收保留首稿和每轮修改，分别检查示意与定量。技能冻结后允许修改项目场景/数据选择/样式，但任何核心程序补丁都要标记为迁移失败后修复，不能混入一次成功的冻结测试。已有作者反馈不能由代理编造；探索候选可由代理临时选择做测试，明确不等于作者定稿。
