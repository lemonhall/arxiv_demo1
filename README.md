# arXiv AI论文爬虫工具

这是一个基于MCP（Message Channel Protocol）的arXiv论文爬虫工具，专门用于获取最新的人工智能（CS.AI）领域的论文标题，并支持论文的主题归类与趋势分析。

## 功能特点

- 自动抓取arXiv CS.AI分类下的最新论文标题
- 基于日期的智能缓存机制，避免重复抓取
- 详细的日志记录系统，便于问题诊断
- 支持论文主题分类和趋势分析
- MCP服务器接口，支持多种客户端调用

## 技术实现

### 项目结构
```
.
├── README.md
├── requirements.txt
├── arxiv_server.py      # MCP服务器主程序
├── tools/               # 工具函数目录
│   ├── crawler.py       # 爬虫实现
│   ├── paper_info.py    # 文件信息检查
│   └── titles.py        # 标题获取功能
└── chrome_data/         # 浏览器数据目录（不纳入版本控制）
```

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动服务器

```bash
python arxiv_server.py
```

### MCP服务器接口

服务器提供三个主要工具函数：

1. `check_latest_paper_info_tool`
   - 检查是否存在当天的论文数据
   - 只在基础目录中搜索文件
   - 返回数据状态信息，包括：
     * 是否存在论文数据
     * 数据是否为当天的
     * 文件修改时间
     * 论文数量等信息

2. `crawl_latest_papers_tool`
   - 启动浏览器抓取最新论文
   - 自动保存抓取结果到文件
   - 返回抓取状态和结果信息

3. `get_latest_titles_tool`
   - 从本地文件读取已抓取的论文标题
   - 返回所有标题数据
   - 智能判断数据时效性

### 推荐使用流程

1. 首先调用 `check_latest_paper_info_tool`
   - 如果返回 `is_current=true`，说明已有当天数据
   - 如果返回 `is_current=false`，需要抓取新数据

2. 根据检查结果：
   - 如果需要新数据，调用 `crawl_latest_papers_tool`
   - 如果已有当天数据，直接调用 `get_latest_titles_tool`

### 调试支持

- 服务器运行时会自动创建日志文件（如 `arxiv_server0.log`）
- 日志记录包括：
  * 服务器启动时间
  * 工作目录信息
  * 文件搜索结果
  * 错误信息等

## 典型使用案例

### 获取并分析最新论文趋势

这是一个典型的使用场景：获取最新的论文，根据主题归类，统计每个主题下的论文数量，分析研究趋势。

1. 首先检查是否有当天数据
2. 如果没有，抓取最新数据
3. 获取所有论文标题
4. 根据关键词对论文进行主题分类
5. 统计每个主题的论文数量
6. 分析研究热点和趋势变化

### 客户端配置示例

在Cherry Studio或其他MCP客户端中，可以使用如下配置：

```json
{
  "arxiv_crawler": {
    "name": "arxiv_crawler",
    "description": "抓取最新的arxiv关于人工智能的论文标题，存入文件；并可随时读取",
    "isActive": true,
    "command": "python",
    "args": [
      "E:/development/arxiv_demo1/arxiv_server.py"
    ],
    "env": {
      "PYTHONIOENCODING": "utf-8"
    }
  }
}
```

### 提示词示例

获取最新论文并分析趋势的提示词示例：

```
获取一下最新的论文，并且根据主题归类后，并统计每个主题下的论文数量，判断一下简要的趋势
```

## 注意事项

1. 文件命名格式：`arxiv_AI_YYYY-MM-DD_(数量)entries.txt`
2. 服务器会在基础目录中查找文件，不再进行递归搜索
3. 所有操作都会记录到日志文件中，便于问题排查
4. 日志文件和chrome_data目录不纳入版本控制

## 错误处理

- 如果遇到文件无法找到的问题：
  1. 检查日志文件中的搜索路径信息
  2. 确认文件命名是否符合规范
  3. 验证文件权限是否正确

- 如果需要强制更新数据：
  1. 直接调用 `crawl_latest_papers_tool`
  2. 新数据会自动覆盖同日期的旧文件


## 调用链

    调用链图 (基于日志时间顺序):

    2025-04-02 19:42:54.421
    ├─ [DEBUG] 初始化基础目录和设置
    │   ├─ Base directory: E:\development\arxiv_demo1
    │   └─ Current working directory: D:\Program Files\Cherry Studio

    2025-04-02 19:42:54.423
    ├─ [DEBUG] 初始化FastMCP服务器
    │   ├─ 注册ListToolsRequest处理器
    │   ├─ 注册CallToolRequest处理器
    │   ├─ 注册ListResourcesRequest处理器
    │   ├─ 注册ReadResourceRequest处理器
    │   ├─ 注册PromptListRequest处理器
    │   └─ 注册GetPromptRequest处理器

    2025-04-02 19:42:54.441
    ├─ [DEBUG] 收到InitializedNotification消息

    2025-04-02 19:42:54.442
    ├─ [INFO] 处理ListToolsRequest请求
    │   └─ [DEBUG] 分发并响应ListToolsRequest

    2025-04-02 19:42:54.631
    ├─ [INFO] 处理PingRequest请求
    │   └─ [DEBUG] 分发并响应PingRequest

    2025-04-02 19:42:54.729
    ├─ [INFO] 处理PingRequest请求
    │   └─ [DEBUG] 分发并响应PingRequest

    2025-04-02 19:43:02.128
    ├─ [INFO] 处理PingRequest请求
    │   └─ [DEBUG] 分发并响应PingRequest

    2025-04-02 19:43:03.874
    ├─ [INFO] 处理PingRequest请求
    │   └─ [DEBUG] 分发并响应PingRequest

    2025-04-02 19:43:03.880
    ├─ [INFO] 处理CallToolRequest请求
    │   └─ [DEBUG] 分发CallToolRequest
    │       └─ [DEBUG] tools.paper_info执行
    │           ├─ 检查论文信息
    │           ├─ 验证文件路径
    │           ├─ 分析arxiv_AI_2025-04-02_(140entries).txt
    │           └─ 返回结果

    2025-04-02 19:43:05.743
    ├─ [INFO] 处理PingRequest请求
    │   └─ [DEBUG] 分发并响应PingRequest

    2025-04-02 19:43:05.745
    ├─ [INFO] 处理CallToolRequest请求
    │   └─ [DEBUG] 分发CallToolRequest
    │       └─ [DEBUG] tools.titles执行
    │           ├─ 获取最新标题
    │           └─ 分析arxiv_AI_2025-04-02_(140entries).txt


## mcp服务器配置之：npx

这些MCP服务器配置中使用的`npx`命令和包名（如`@amap/amap-maps-mcp-server`）实际上指向的是**npm（Node Package Manager）注册表**中的公开包，而非直接使用GitHub仓库地址。以下是关键点的解释：

---

### 1. **为什么用`npx`？**
   - `npx`是Node.js自带的工具，主要用于**直接运行npm包中的命令**，无需先全局安装包。
   - 如果本地未安装目标包，`npx`会自动从npm仓库下载并临时执行（完成后可清理缓存），非常适合快速运行一次性或工具类脚本。

---

### 2. **`-y`参数的作用**
   - `-y`是`npx`的选项，表示**自动确认安装**（等同于`--yes`）。
   - 当包未安装时，`npx`默认会提示“是否安装？”，加`-y`可跳过确认直接安装。

---

### 3. **包名的含义（如`@amap/amap-maps-mcp-server`）**
   - **`@scope/package-name`**：这是npm的命名规范，`@scope`表示包所属的组织（如`@amap`是高德地图的官方组织），`package-name`是具体包名。
   - **这些包本质上是发布在npm注册表上的公开模块**，类似于Python的PyPI或Rust的Crates.io。虽然它们的源代码可能托管在GitHub（或其他平台），但用户通过`npm`或`npx`安装时，实际从npm服务器下载编译后的代码。

---

### 4. **与GitHub的区别**
   - **直接使用GitHub仓库**：若包未发布到npm，通常需要通过类似`npx github:user/repo`的语法指定GitHub地址。
   - **当前配置的包**：如`@amap/amap-maps-mcp-server`、`@playwright/mcp`等，均为**已发布到npm的官方包**，开发者无需关心源码位置，只需通过包名调用。

---

### 5. **配置示例解析（以高德地图MCP服务器为例）**
   ```json
   "command": "npx",
   "args": [
     "-y",
     "@amap/amap-maps-mcp-server"
   ]
   ```
   - **等效命令行**：
     ```bash
     npx -y @amap/amap-maps-mcp-server
     ```
   - **行为**：自动安装并运行`@amap/amap-maps-mcp-server`包，无需手动操作。

---

### 6. **为什么看不到`.js`文件路径？**
   - npm包的入口文件已在`package.json`中定义。通过`npx`运行时，会自动找到入口脚本（如`bin`字段指定的文件），用户无需关心具体路径。

---

### 总结
这些配置利用了npm生态的便捷性：通过`npx`直接调用远程包，省去手动下载、安装的步骤。所有包均来自**npm官方仓库**，而非直接关联GitHub。若包未发布到npm但托管在GitHub，需显式指定仓库地址（如`npx github:user/repo`）。


## uvx风格的mcp-server

在 Cherry Studio 中发布自定义的 Python MCP 服务器需遵循标准化流程。首先需通过 create-mcp-server 工具生成符合 MCP 协议规范的项目框架，该工具会自动创建必要的目录结构和配置文件，确保服务接口与协议兼容6。建议使用 uvx 打包工具进行依赖管理和构建，该工具能显著提升 Python 依赖解析效率，生成符合 PEP 621 标准的 pyproject.toml 文件46。

发布至 PyPI 时需注意三点技术细节：1. 在 setup.py 中明确声明 entry_points，将主模块注册为控制台脚本，使安装后可直接通过 mcp-server-<yourname> 命令调用5；2. 添加 mcp-server 分类标识符，便于 Cherry Studio 自动识别服务类型5；3. 对需要访问本地系统资源的服务类型（如文件操作类），必须在元数据中声明 requires-system-access 字段3。

用户安装后，需在 Cherry Studio 的 MCP 管理界面配置以下参数：服务类型选择 STDIO，命令格式应包含完整的模块调用路径，例如 uvx mcp-server-<yourname> 或 python -m your_module13。若涉及环境变量配置（如 API 密钥），需在高级设置中声明 env 字段，并通过 export 指令指导用户配置系统环境变量3。

建议在文档中提供标准化测试用例，推荐使用 @modelcontextprotocol/inspector 工具包进行协议兼容性验证，该工具可检查服务响应格式是否符合 MCP 协议的 JSON Schema 规范56。对于需要持久化运行的服务，应提供 systemd 或 launchd 的守护进程配置文件模板9。

