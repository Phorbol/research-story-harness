---
name: structure-cover
description: 将已有分子或有限材料坐标制作成自媒体封面、结构美图与缩略图；用同一科学对象分别进行 OVITO 或 Blender 渲染，保留可编辑场景与来源。用于传播视觉，不代替论文论证图、周期结构准备或化学结构推断。
---

# 科学结构封面

单个视觉主角即可启动，不要求创建完整 research harness。先确定对象与来源、封面用途和标题空间；未给文案时用明确标为示例的短标题，同时交付无字版。

## 直接制作

依赖：Python 的 ASE、NumPy、Pillow；OVITO 路线另需 ovito；Blender 路线用 Blender 自带 Python。示例实跑版本为 OVITO 3.16.0、Blender 4.5.0，非版本兼容承诺。

1. 读取真实坐标，或明确授权的理想模型/生成构象。保留全部源原子，不为构图删原子。小分子的连接来自化学拓扑；杆仅表达连接时注明未展示键级。没有坐标时不要从一张漂亮图片猜出实验结构。
2. 参考 `assets/particle-style.json`，使用 `scripts/make_scene.py structure.extxyz --style style.json --origin idealized --out scene.json`。它只处理有限、完整占据对象；周期、占据率、表面复制交给 `ovito-structure` 先准备。源坐标写入共享 scene，显示半径与相机另存。
3. 两种实际后端任选或对照：
   - `python scripts/render_ovito.py scene.json ovito.png`
   - `blender --background --python scripts/render_blender.py -- scene.json blender.png assets/satin-metal.json`
   最后的配方 JSON 可省略，省略保留此前 studio 起点；`materials/default_material/lights/world_strength` 控制实际材质和灯光，并随成图记录。不需要模型每次重写 Blender 脚本。`satin-metal.json` 在本次颗粒上较平衡，`metal-strip.json` 保留作高反射对照，不能视作普遍最佳。小分子可用 `molecule-editorial.json`。同题比较先共用 scene。Blender 输出 `.blend`；两者输出透明 PNG 与后端记录。
4. 调材质前先看结构轮廓与遮挡；分子基团/材料接触区是否能辨认。参看 [此次实跑发现](references/observed-tradeoffs.md)，不要把金属高光照搬到所有元素。
5. 用 `python scripts/compose_cover.py render.png cover.json --out cover` 独立组版。配置见 `assets/cover.json`；另有居中、双对象和方形三个例子。`subjects` 指定每个完整渲染与独立位置（第二张示例图 `aspirin.png` 需替换成已有输出）；文字可用 `anchor: mt` 居中与逐段 `font_path/font_family`。字体路径须选本机真实可用且覆盖实际字符的字体；检查化学式下标，不因中文能显示就认为所有字形可用。输出无字图、JPEG/PNG、可编辑文本 SVG 和缩略图。SVG 的字体需目标机器支持，实际排版可能随字体回退改变。
6. 同时查看大图和320px左右缩略图。小图看主角轮廓、标题和视觉噪声，大图看结构、遮挡、锯齿与材质。方形用途独立重排 `size` 和 `subject_box`，不要直接中心裁切丢掉主体。尺寸由使用情境决定，示例2400×1024并非平台API要求。

## 脚本边界

共同 scene 的 `positions/elements/tags/bonds/origin` 是科学对象；`radii/colors/camera/size` 是显示选择。脚本不推断晶相、吸附、化学键或光学常数。Blender 使用球与连接杆；不含轨道、电子密度或真实表面材质计算。原子没有被删除，不代表都未被遮挡。

`camera.halfheight` 是正交视口垂直半高；Blender 横向画幅的 ortho_scale 取 `2*halfheight*width/height`。比较时不能把两端数值同名就认作同一尺度。非z向上的相机需扩展 Blender 相机定向并实测；当前实跑使用 up=[0,0,1]。

若 macOS 沙盒报 `No MTLDevice` 或 Blender 初始化崩溃，保留错误并按宿主权限流程运行同一脚本；不要修改全局安全设置或悄悄换科学对象。

交付坐标/拓扑来源、scene、渲染脚本、`.blend`（使用Blender时）、透明图、封面配置和缩略图。保留实际发生的首稿与改稿；将材料美观判断与科学有效性分开，不宣称点击率或传播效果已验证。

Blender 是外部实际渲染器；本 skill 固化已运行的建场景、材质配方与组版代码。主题选择、配方适用性、取景与视觉验收仍由 agent 结合输入完成，不是一个已验证能自主产出优秀封面的固定模板。
