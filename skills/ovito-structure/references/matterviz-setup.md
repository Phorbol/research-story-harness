# MatterViz v0.9.0：独立快照环境

只有需要源码快照 CLI 或本地交互应用时才准备此环境。已有可用的 MatterViz 查看器/VS Code 扩展可以直接检查文件；不需要为了打开一个结构而安装整套源码开发依赖。RSH 默认 Python 环境不安装这些依赖。

## 已固定的组合

- MatterViz v0.9.0，commit `6d3fbfc9f17581a7a6733dbf6558f190ef83aac6`。
- **npm 发布包** `svelte-widgets@1.11.0`，gitHead `29a64aa5cd8e18867fee9b469882b1a0715f8b5a`。
- pnpm 11.5.0（与上游 `packageManager` 一致）；[配套 lockfile](../assets/matterviz-v0.9.0.pnpm-lock.yaml) 固定本次依赖解析。
- Node >=24；本次维护者复跑使用 macOS 26.6 arm64 / Node 26.8.2 / Playwright 1.65.1。

为什么需要这一步：MatterViz v0.9.0 原 package.json 指向 `github:janosh/svelte-widgets#main`。2026-11-17 的新安装先遇到 pnpm Git 构建授权，再遇到该分支缺少 `storage`、`csv`、`download` 等导出的构建失败。只固定 MatterViz tag 不够。不要全局允许所有依赖执行构建；这里改用已验证的 npm 发布包。包内版本号相同也不代表 Git main 与 npm 发布包内容相同。

## 准备新 checkout

以下在 **RSH 仓库根**运行，需要 Git、Node 和 npm。目标目录必须尚不存在，以免覆盖现有工作。npm/pnpm 缓存可以复用；这不应复用旧 node_modules 或 dist 来代替安装验证。

```sh
RSH_ROOT="$PWD"
MATTERVIZ_ROOT="$RSH_ROOT/work/matterviz-v0.9.0"
git clone --depth 1 --branch v0.9.0 https://github.com/janosh/matterviz.git "$MATTERVIZ_ROOT"
git -C "$MATTERVIZ_ROOT" rev-parse HEAD
# 应为 6d3fbfc9f17581a7a6733dbf6558f190ef83aac6；不同则先核对版本。

(
  set -e
  cd "$MATTERVIZ_ROOT" || exit 1
  node --input-type=module -e '
    import fs from "node:fs";
    const p = JSON.parse(fs.readFileSync("package.json", "utf8"));
    p.dependencies["svelte-widgets"] = "1.11.0";
    fs.writeFileSync("package.json", JSON.stringify(p, null, 2) + "\n");
  '
  cp "$RSH_ROOT/skills/ovito-structure/assets/matterviz-v0.9.0.pnpm-lock.yaml" pnpm-lock.yaml
  npx --yes pnpm@11.5.0 install --frozen-lockfile
) || exit 1
export PLAYWRIGHT_BROWSERS_PATH="$MATTERVIZ_ROOT/.playwright-browsers"
node "$MATTERVIZ_ROOT/node_modules/@playwright/test/cli.js" install chromium
node "$MATTERVIZ_ROOT/src/scripts/snapshot.mjs" --help
```

检查安装退出状态与原始日志，成功后才继续。浏览器下载目录需要可写。新 shell 中重新设置 `MATTERVIZ_ROOT` 和 `PLAYWRIGHT_BROWSERS_PATH`；后者必须与安装浏览器时相同。不要只复制 `snapshot.mjs`，它依赖完整 checkout、前端构建配置和依赖。

需要共享包缓存时，可给 install 增加 `--store-dir /absolute/path/to/cache`。lockfile 不是所有平台可用的承诺；不同系统的浏览器共享库、图形驱动和新的 Node 版本分别核验。Linux 首次运行缺少 Chromium 共享库时，按 Playwright 官方系统依赖说明处理，不套用他人机器上的库路径。无 GPU 环境可以尝试上游支持的 `CI=1` 软件 WebGPU 模式；空白输出不能算成功。

## 运行和更新

回到[快照与交互检查](post-model-visualization.md)执行原始结构快照。要运行本地交互应用，在 MatterViz 目录执行：

```sh
node_modules/.bin/vp dev --host 127.0.0.1
```

打开终端给出的本地地址及 `/structure` 页面，可拖入原始文件。此环境的本地 package.json 改动是兼容性固定，不是更改科学模型。升级 MatterViz 时，在另一个 checkout 更新版本与 lockfile，并复核输入字段、实际输出和目标检查动作；不要把这份旧 lockfile 覆盖到新版本。
