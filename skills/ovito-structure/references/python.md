# OVITO Python 与来源

## 官方工作流

```python
from ovito.io import import_file
from ovito.vis import Viewport, TachyonRenderer

pipeline = import_file("actual.extxyz")
data = pipeline.compute(0)
print(data.particles.count, data.cell)
pipeline.add_to_scene()
try:
    viewport = Viewport(type=Viewport.Type.Ortho,
                        camera_dir=(1, -1, -.65), camera_up=(0, 0, 1))
    viewport.zoom_all(size=(1600, 1200))
    viewport.fov *= 1.1
    viewport.render_image(filename="structure.png", size=(1600, 1200),
                          background=(1, 1, 1), crop=True,
                          renderer=TachyonRenderer(shadows=False,
                              ambient_occlusion=True,
                              ambient_occlusion_samples=40,
                              antialiasing_samples=12))
finally:
    pipeline.remove_from_scene()
```

这是通用模式，不承诺所有文件的类型、元素和键均被自动正确识别。对 LAMMPS 的数字 type 必须提供 type→元素/物种映射；不能用连续色标把无序类别暗示成数值顺序。不要在已有真实拓扑上重复用距离创建键。

本包的 CLI 进一步用 ASE 读取 CIF、XYZ/extxyz、POSCAR 等单帧文件，在统一场景中保留占据率，再用 OVITO 的 `DataCollection`、`Particles`、`SimulationCell` 与 `StaticSource` 构建 pipeline。这样避免在格式转换中丢掉 Ta/Cr 混合占据位点，也让源位点与显示周期像可追踪。

## 版本与参考

2026-10-23 实际读取并参考了：

- [OVITO 官方渲染教程](https://www.ovito.org/manual/python/introduction/rendering.html)
- [OVITO Python vis API](https://www.ovito.org/docs/current/python/modules/ovito_vis.html)
- [OVITO 数据模型](https://www.ovito.org/docs/current/python/modules/ovito_data.html)
- [ASE CIF 读取实现](https://docs.ase-lib.org/_modules/ase/io/cif.html)
- [ASE 周期邻接](https://docs.ase-lib.org/ase/neighborlist.html)
- [WuGroup 的 OVITO skill](https://github.com/WuGroup-XJTLU/cc-skills-ZhenghaoWu-Group/blob/main/plugins/ovito/skills/ovito/SKILL.md)，读取到的 blob 为 `4ba3582e4e5b145ab935a449ed9614cd80274db3`。

第三方 skill 贡献的是导入—修改—视图—渲染的组织与常见问题线索。本包未直接安装它，也没有照搬未经运行验证的格式、渲染器或参数结论。例如当前 OVITO 版本的图形后端和旧 OpenGL 示例不同；实际参数以本次安装的 3.16.0 运行结果和对应官方 API 为准。官方 current 页面会随版本更新，应核对本地版本，不把开发版参数写进固定版脚本。
