# 构模后交互检查与快照预览

适用于已生成或修改结构、需要检查模型并决定下一步表达的任务。MatterViz 是可选的交互查看器和快照工具；使用已有 OVITO draft 也可完成预览。根据需要辨认的位点、周期关系和目标载体选择工具。

## 先保留结构身份

读取原结构的来源、单位、元素/占据率、晶胞/PBC、帧和弛豫状态。真实计算结构与理想示意模型分别标明。交互视图帮助发现重叠、孤立原子或遮挡；模型科学有效性与计算收敛仍回到相应证据。

优先直接打开原文件。调整显示选项时保留原始 cell/PBC；确需制作去除边界元数据的 XYZ 预览副本时，记录转换原因及被省略字段，核对元素顺序和笛卡尔坐标，原件继续作为结构权威。混合占据模型需核查各组分是否被正确呈现，不以主元素显示替代完整位点组成。

## 交互检查

已有 [MatterViz VS Code 扩展](https://marketplace.visualstudio.com/items?itemName=Janosh.matterviz)时，通过 `Open With… → MatterViz`打开所支持的结构文件；远程工作区需确认扩展运行在能读取该文件的一侧。也可使用 MatterViz 自己的交互应用。安装与格式支持以[官方仓库](https://github.com/janosh/matterviz)为准，RSH 不更改全局文件关联。

旋转、缩放并查看整体几何和目标位点；周期盒与自动推断的键/配位多面体都是影响解释的显示选择。推断的键不能作为真实成键或机理的证据。不同状态比较时记录显示差异，只有视觉一致性确已核对后才作并列判断。

## 复用官方快照 CLI

已验证入口为 MatterViz **v0.9.0** 的 `src/scripts/snapshot.mjs`，见[固定版本源码](https://github.com/janosh/matterviz/blob/v0.9.0/src/scripts/snapshot.mjs)。先按[固定依赖安装流程](matterviz-setup.md)准备独立 checkout、Node >=24、依赖和 Playwright Chromium。该版本原来的 Git main 依赖已出现不兼容，不能只固定 MatterViz tag 后直接安装；这些依赖不加入 RSH 的 Python 默认环境。

下面从 RSH 仓库根运行，`MATTERVIZ_ROOT`指向已准备的独立 checkout。两个输入是本包中明确标注的未弛豫理想模型，不是实验结构。

```bash
MATTERVIZ_ROOT=/path/to/matterviz
export PLAYWRIGHT_BROWSERS_PATH="$MATTERVIZ_ROOT/.playwright-browsers"
node "$MATTERVIZ_ROOT/src/scripts/snapshot.mjs" --help
node "$MATTERVIZ_ROOT/src/scripts/snapshot.mjs" \
  examples/supported-nanoparticles/models/illustrative-PdZn-ZnO.extxyz \
  examples/supported-nanoparticles/models/illustrative-PdCu-ZnO.extxyz \
  --out-dir work/matterviz-preview \
  --props skills/ovito-structure/assets/matterviz-preview.json \
  --width 1000 --height 800 --dpi 72 \
  > work-matterviz-preview.jsonl
```

[预览选项](../assets/matterviz-preview.json)使用白色背景并关闭推断键和配位多面体，便于检查原子几何；需要这些关系时按来源和任务显式开启。该文件是起点，不是出版配色规范。轨迹默认使用第0帧；检查其他状态时显式传 `--frame`并记录选择。CLI 输出目录应是新的，已有同名图片会被拒绝；保留旧结果再选择新目录即可。

无硬件 GPU 的受支持环境可按上游实现使用 `CI=1 node ...`选择软件 WebGPU adapter。本次 Linux smoke 使用该路径；依赖、浏览器或图形后端失败时检查原始错误，不将空白图作为成功。交互窗口、其他操作系统和新的 MatterViz 版本分别核验。

## 把预览变成一次具体检查

先提出本次需要回答的问题，例如“哪些位点属于颗粒，哪些属于载体，界面是否在当前投影中被遮挡”。在位点表中核对元素、坐标和源文件分组，再用属性着色或隐藏分组减少遮挡，从互补方向观察；将发现的问题定位到源位点，而非仅保存漂亮的快照。隐藏显示分组不等于删除原子，自动邻接不等于机理证据。

有限模型即使 PBC 全为 false，也可能带有较大的辅助晶胞；v0.9.0 的自动取景包含晶胞角点。优先调整显示边/面透明度及完整相机规格（方向、up、target、投影、视场），不要为改善构图删除原件的 cell/PBC。仅隐藏盒子也不保证自动取景会收紧。改变显示后重新看真实输出。

仓库中的[纳米颗粒检查案例](../../../examples/supported-nanoparticles/matterviz/README.md)保留默认/调整后图与位点表、tags 隔离截图，并列出已回答的问题和未验证能力。案例相机仅适用于那两个模型，不是通用预设；独立安装此 skill 时，案例仍可从[公开仓库](https://github.com/Phorbol/research-story-harness/tree/main/examples/supported-nanoparticles/matterviz)阅读。

## 检查实际输出并回到论文图

每个成功快照返回一行 JSON，含 `input`、`output`和 `sites`。核对返回路径、图像尺寸、实际可见元素与目标位点，以及当前帧/显示晶胞对应的 site 数。位点计数相符只是粗检查，不能证明占据率、周期关系或坐标解释全部正确。沿项目已有图源记录保留源版本、MatterViz 版本、实际命令/props和输出定位，核对输入文件未改变。

v0.9.0 快照只捕获 **3D canvas**：不含 DOM 图例、位点标签、面板及2D截面。打开实际 PNG 检查可读性；需要标注与版式时另行组版。此入口未实现 OVITO `render-spec`、共享相机、半径/颜色或原子像素投影的等价映射，也不进入 `structure3d` / `catalyst_surface`的生产缓存。

需要既有出版渲染和原子映射时，仍用同一原结构执行 [OVITO 渲染](rendering.md)或[催化表面流程](catalyst-surfaces.md)，再在论文实际尺寸核对。预览暴露的问题回写本项目结构或显示决定；改变科学模型时保留来源和作者决定。
