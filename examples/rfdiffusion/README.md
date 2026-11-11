# RFdiffusion · 完整中文文献汇报

20页，16:9；18页主讲加2页备份。基于 Watson, Juergens, Bennett et al. 的公开论文 *De novo design of protein structure and function with RFdiffusion*, Nature 620 (2023), DOI [10.1038/s41586-023-06415-8](https://doi.org/10.1038/s41586-023-06415-8)。这是一套已有最终汇报的公开整理，不是为了展示重新编造的研究结果。

## 查看与编辑

- [可编辑 PPTX](RFdiffusion.pptx) · [完整 PDF](RFdiffusion.pdf)
- [逐页中文讲稿](speaker-notes.md) · [来源与限定](source-map.md)
- `slides/01.png`–`20.png` 为该最终PPTX经LibreOffice转换、Poppler渲染的原有预览。
- `pptx.yaml` 和其中列出的20个 `.page.yaml` 是最终权威页面源。`media/` 只含这些源文件实际引用的37个图片；`asset-map.json` 保留对应定位与裁切记录。
- `data/motif-benchmark.csv` 保留补充信息Table10的25行数据。

新增标题、正文、注释、流程节点、箭头与汇总图表为PPT原生对象。蛋白结构、显微图和作者测量曲线为裁切PNG，可移动、缩放或裁切，不能在PPT内逐原子或逐数据点编辑。保持这一区别，不将“包含图片源文件”称为原图科学对象完全可编辑。

## 科学范围

这是公开论文的文献汇报，不是作者项目的新结果或对RFdiffusion模型的重新训练/复算。正文与SI Table10的RFjoint汇总存在不同口径；第9页按可复核表格合并得17/25，同时保留正文19/25的差异说明。RFdiffusion为23/25，Hallucination为15/25；按所测变体逐任务取最大值用于汇总，不代表单一配置同时达到每行最好结果。p53命中分母的来源差异也保留在讲稿与来源映射中。

## 重建

在本仓库根目录、已安装根requirements的Python环境运行（若本目录改名，相应调整路径）：

```bash
python skills/ansatz-slide/scripts/ansatz_slide.py validate examples/rfdiffusion/pptx.yaml
python skills/ansatz-slide/scripts/ansatz_slide.py deck preflight examples/rfdiffusion --offline
python skills/ansatz-slide/scripts/ansatz_slide.py export examples/rfdiffusion/pptx.yaml --offline -o work/RFdiffusion-rebuilt.pptx
```

原稿使用Arial和Arial Unicode MS；字体二进制不分发，需自行安装或显式替换并重新检查排版。原预览是在LibreOffice/Poppler生成；未声称在Microsoft PowerPoint或WPS逐页验证。导出成功只证明相应程序检查通过。

## 许可与公开范围

论文图像和选取的数据按原文 **CC BY 4.0** 保留归属、许可链接及改编说明：[权限原文](source/article-permissions.txt) · [来源链接](source/README.md) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。处理包括原图裁切、重新组版、中文讲解和带明确口径的数据汇总；不暗示原作者认可本汇报。新增讲稿、页面组织和代码没有被本文件重新授予统一开源许可。

不包含完整原论文/SI PDF、历史冻结工具、生产日志、审阅聊天、私人论文或本机路径。PPTX包含20页与20页正常讲者备注；98个XML/关系文件（含docProps、customXml）、页面源、讲稿、来源映射及PDF文本/元数据经过针对性个人路径和内部项目名扫描，未命中。扫描不证明所有未知敏感信息都不存在；本包内容来源限定为上述公开论文。
