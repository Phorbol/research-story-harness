# 在线成品展厅

公开网址：[Research Story Harness · 从结构到故事](https://research-story-harness-gallery.inwardchart4.chatgpt.site)。网站无需登录，托管在 Sites；GitHub 保存页面源和可复现构建入口。

## 页面内容与编辑

- `structure-covers.html`：成品与对照、来源说明、编辑和下载链接。
- `showcase.css`：桌面网格、手机逐张展示与排版。
- `showcase.js`：RFdiffusion 精选页切换、20 页预览。
- `build_site.py`：只读取本仓库已有的公开素材，输出独立静态网站；不读取用户目录或外部稿件。

在仓库根目录执行：

```bash
python -m pip install Pillow
python docs/build_site.py --out build/site
python -m http.server 8080 --directory build/site
```

打开 `http://localhost:8080`。可将 `build/site` 部署到静态网站托管；HTML 本身引用构建后的 `assets/`、`style.css`、`app.js`，不要直接打开未经构建的源文件。更换域名时同步更新 HTML 的 `og:image` 绝对地址与 README 链接。

## 来源与表示边界

封面素材来自 `examples/structure-covers`；OVITO 图来自理想颗粒示例。材质对照按原图三列边界拆成三张，所有结构像素保留；桌面并排、手机逐张，完整原图仍可打开。网页压缩了部分 PNG 为 WebP，未改变坐标、数据或图面内容。

RFdiffusion 的 20 页为已有最终稿预览，不是新生成的 slides，也不冒充前后版本。论文素材 CC BY 4.0，裁切、中文讲解与重排的说明保留在页面及原示例。TOC 两版来自同一公开数据案例。具体出处与许可见 [第三方说明](../THIRD_PARTY_NOTICES.md)。网站未包含内部论文、字体二进制或 Blender 安装文件。

## 本轮浏览器核对（2026-11-19）

在本地预览及正式 HTTPS 站点实际打开：桌面 1440 × 1000、手机视口 390 × 844。修复了首屏成品过于靠后、手机三列材质图缩得过小、代码区造成 10 像素横向溢出。修订后手机文档宽度为 390 像素，检查的可见图片均加载；精选 slide 切换、全部 20 页展开与原图打开可用。

这属于桌面浏览器手机视口验证，不是实体手机或微信内置浏览器兼容性认证；网页布局检查也不等于科学成图达到发表标准或传播效果经过实验验证。
