# ayon-katana

AYON Host Addon for **Foundry Katana**（目标版本：**Katana 9.0v2**，平台：**Windows**）。

该仓库目标是提供 Katana 的 AYON 集成（启动注入 + Host 注册 + Publish/Submit 工作流），使你可以在 Katana 内通过 AYON Publisher 提交（publish）当前 `.katana` 文件。

## 主要思路（与 Foundry 机制对齐）

- 通过环境变量 `KATANA_RESOURCES` 注入本 addon 的 Katana 资源目录（其中包含 `Startup/init.py`、`Shelves` 等）  
- Katana 会在 `KATANA_RESOURCES` 下的 `Startup/init.py` 执行启动脚本（见 Foundry 文档）
- 启动脚本调用 `ayon_core.pipeline.install_host()` 注册 `KatanaHost`
- 为支持 **AYON OpenUSD Resolver**：将 `PXR_PLUGINPATH_NAME` 的路径同步到 `FNPXR_PLUGINPATH`（Katana 的 namespaced USD 使用 `FNPXR_PLUGINPATH`）

## 开发与测试（建议）

1. 将本仓库作为 AYON 的 dev addon 使用（或打包后安装到 bundle）
2. 从 AYON Launcher 在某个 Project/Task 上下文启动 Katana
3. 在 Katana 内运行 AYON Publisher（后续会通过 Shelf 提供入口）

> 备注：本仓库不包含 Katana 本体，所以无法在此环境内直接运行 Katana 做端到端验证；实现方式参考了 Katana 官方开发文档中的资源/启动机制。

## 提交类型（逐步对齐 Houdini 体验）

目前支持/规划中的“提交（publish）”类型：

- **Katana Workfile**：当前 `.katana` 文件（与 Houdini/Maya 的 workfile publish 类似）
- **USD 导出**：自动从 `UsdLayerExport` / `UsdExport` 节点检测导出路径并生成发布实例
- **Lookfile**：自动从 `LookFileBake` 节点检测 `saveTo` 输出并生成发布实例（通常为 `.klf` 或输出目录）

> 注意：USD/Lookfile 这两类实例依赖你在 Katana 里先把文件导出到磁盘（否则发布时会报“输出文件不存在”）。

### 一键 Publish（自动触发写盘）

已增加“发布前自动触发导出”的逻辑：

- 对 `LookFileBake` 实例：尝试触发节点上的 **Write Look File**（脚本按钮）
- 对 `UsdLayerExport` / `UsdExport` 实例：尝试触发节点上的 **Export/Write**（脚本按钮）

如果你现场节点的按钮参数名与默认不一致，会导致无法触发；把节点参数截图发我，我会针对 Katana 9.0v2 做精确适配。

## 目录结构

- `package.py` - AYON addon 元信息
- `server/` - server-side addon 定义（settings schema 等）
- `client/ayon_katana/` - client-side（Host 集成、Katana 启动资源、publish/create 插件等）
