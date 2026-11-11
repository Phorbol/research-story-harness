# 有序催化表面的近景与连续状态

## 来源与适用范围

表面渲染器由作者提供的本地 `render_surface.py` 改编；原始研究坐标及参考图不随公开包分发。保留了金属显示半径、基底铺展、吸附物单份显示、共享相机及像素投影的主要方法；新增明确的组分身份、来源绑定、周期像身份和只读准备接口。原包的“已批准”“逐像素一致”是来源描述，不作为普遍验收结论。

这个入口适用于有序、具有面内 PBC 的扩展表面及保持原子顺序/晶胞一致的状态序列。有限团簇、多孔结构、混合占据和需要保留稀疏骨架的体系先用通用 `structure_render.py`。密排视觉不是所有材料的优化目标；不能为填满画面而修改坐标或删去反应位点。

## 先确定读图任务，再调材质

读者要追踪哪个原子、哪次接近或离开？先设 `request`、`focus_atoms`、`center_atoms` 与 `orient`，再以同一镜头比较状态。这里的 `break/form` 是作者给定的显示语义；输出距离与距离阈值棒不是成键、断键、能垒或 TS 的证明。`saddle` 等源文件名也不能代替计算验证。

“球小、很空”分为表示和构图两种问题：金属球间缝隙用显示半径处理，背景过多用相机 `half_height` 处理。把两项分开比较，避免靠放大画面声称球体改善。来源包的 CN12 金属半径表是显示预设，尚未在此独立核对物理半径数据库；不适合时用 `style.radii` 明确覆盖。缺表元素用半个基底近邻中位距离拟合，并在 metadata 中标明来源；这也不等于物理半径测量。

层次用克制的 AO、层间色阶与必要阴影表达。表面阴影导致脏线或伪孔洞时先减少直射/关闭投影，保留接触层次；勿先无限增加采样。吸附原子与金属分别调半径，H 不应消失，也不应遮住关键几何。底色是当前显示预设，可改成白色；实际论文须统一跨图元素颜色，不能依各面板元素丰度自动换色。

## 最小任务文件

路径相对于 job 文件；原子编号为源文件中从 0 开始的顺序。

```json
{
  "prefix": "surface",
  "states": [{"name": "IS", "path": "is.extxyz"}, {"name": "FS", "path": "fs.extxyz"}],
  "adsorbate_indices": [64, 65, 66, 67],
  "request": [[64, 65, "break"], [65, 66, "form"]],
  "center_atoms": [64, 66],
  "orient": [64, 66],
  "style": {"radii": {"Pt": 1.39, "H": 0.56}, "colors": {"Pt": [0.8, 0.83, 0.86]}},
  "scene": {"layers": 4, "keep_radius": 14},
  "camera": {"elevation": 50, "azimuth": 10, "half_height": 5.4, "target_up": 0.6, "size": [900, 720]},
  "renderer": {"engine": "tachyon", "ao_samples": 48, "aa_samples": 12, "ao_brightness": 0.8, "direct_light": 0.85, "shadows": true}
}
```

也可用源 `tags == adsorbate_tag`（默认 2）；多状态标签必须一致。没有身份时不要按“非金属就是吸附物”猜测氧化物。独立脚本的 `allow_element_inference` 只供明确请求的探索；harness 不接受它作为确定身份。氧化物/非金属基底的显示半径需另行确认，不套用吸附原子半径。

```bash
python <skill>/scripts/surface_render.py job.json --verify-only
python <skill>/scripts/surface_render.py job.json --preview
python <skill>/scripts/surface_render.py job.json --strip
```

Python `render_surface_job(..., verify_only=True, write_outputs=False)` 不写目录、图像或元数据，不载入 OVITO。正式图要实际渲染；本机 Tachyon 仍需宿主图形访问。当前实测为 OVITO 3.16.0。参见 [官方 Tachyon 接口](https://www.ovito.org/manual/python/modules/ovito_vis.html#ovito.vis.TachyonRenderer)，新版本 API 不能直接推定存在于旧环境。

## 保存和验收什么

- 来源坐标不变；MIC 展开和基底周期像是记录的显示变换，并非所有屏幕位置都等于原胞内位置。
- 基底才铺展周期像，吸附物只一份；每个显示原子保留源编号和晶格像，focus 投影绑定实际显示像。
- 相机由整个序列共同决定，不逐帧重新缩放。固定 `half_height`、方向、像素尺寸后才比较材质。
- 遮挡要看图；投影坐标不保证原子可见。被遮挡球的可见色块包围盒中心不等于球心，不能据此断言投影误差。
- `cutaway` 只在明确指定时启用，并报告透明的显示原子；稿件图注要披露。默认不做穿透。
- 位图提供球体/材质；文字、局部距离、图例通过 harness 做矢量叠加。字体、大小、字重和元素正体由统一 style profile 管理。

公开示例位于 `assets/synthetic-catalyst-example/`，全部坐标按规则构造，用于软件与显示变换测试，不代表计算得到的结构、反应路径或稳定态。真实研究须登记自己的坐标、身份和来源。

## 反应小分子近景的低高光样式

`assets/reactive-cu-display-fragment.json`是2026-11-06 AI-Cat四TS精修的**可选配置片段**，合入已有真实坐标job的style/renderer字段；不是完整job或通用物理半径。Cu/C/O/H显示半径1.23/0.40/0.44/0.23 Å、键宽0.16 Å及低高光有实际小尺寸改善证据。其他元素/支撑体必须重新选定，不应将Cu样式套到分子催化或氧化物。

OSPRay新增可选字段`material_type`、`standard_shininess`、`standard_specular_brightness`、`direct_light_angular_diameter`，及`refinement_iterations`/`samples_per_pixel`和对应`preview_iterations`/`preview_samples_per_pixel`；未给时保留旧行为。`transparent_background:true`允许透明底。以上材质字段来自本机OVITO3.16实际使用，不保证其他版本API；Tachyon不消费这些OSPRay参数。

先在相同物理显示尺度看反应原子对，分别调整相机、球径、键宽及高光；提高分辨率不能补救球体挡住关键键。连续状态保持同镜头，独立TS可不同取向但共享尺度并注明不可当轨迹比较。图中以实际投影端点叠加距离虚线；选与氧红/碳灰区分的颜色，短引线不能横穿反应骨架。取景裁掉边缘表面H与源坐标删除是两件事，都需如实记录；不得声称全场景原子都在图内可见。
