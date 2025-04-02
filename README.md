# arXiv AI论文爬虫

这是一个自动爬取arXiv计算机科学人工智能(CS.AI)分类下最新论文标题的工具，并提供MCP服务器接口供客户端调用。

## 功能特点

- 自动访问arXiv CS.AI最新论文页面
- 提取当天发布的AI论文标题
- 将结果保存为易于分析的文本文件
- 支持大量论文批量抓取（可配置）
- 自动处理日期格式，方便归档
- 提供MCP服务器接口，方便各种客户端调用（如Cursor、Cline、Claude Desktop等）
- 智能基于日期的缓存机制，避免重复爬取

## 技术实现

- 使用Playwright自动化浏览器操作
- 采用正则表达式提取日期和论文数量信息
- 支持错误处理和截图调试
- 基于MCP协议实现服务器接口
- 使用子进程分离同步爬虫和异步MCP服务器
- 基于日期的智能缓存机制

## 项目结构

- `arxiv_crawler.py`: 独立的爬虫脚本，负责实际的爬取工作
- `arxiv_server.py`: MCP服务器，提供工具接口给客户端调用
- `requirements.txt`: 项目依赖

## 安装依赖

### 安装Python依赖

1. 使用pip安装所有依赖:

```bash
pip install -r requirements.txt
playwright install chromium
```

## 使用方法

### 直接运行爬虫

1. 安装依赖（参见上方"安装依赖"部分）

2. 运行爬虫：

```bash
python arxiv_crawler.py
```

3. 查看结果：
运行完成后，程序将在当前目录生成形如`arxiv_AI_YYYY-MM-DD_(N_entries).txt`的文件，包含所有抓取的论文标题。

### 启动MCP服务器

1. 安装依赖（参见上方"安装依赖"部分）

2. 启动MCP服务器：

```bash
python arxiv_server.py
```

3. 服务器将以stdio模式运行，可以直接被MCP客户端调用

## MCP服务器接口说明

服务器提供三个主要工具函数：

### 1. check_latest_paper_info

检查是否有已爬取的论文文件，特别是检查是否有今天日期的数据文件。

```
功能: 检查本地是否有今天日期的论文文件
参数: 无
返回: 
{
  "success": true,
  "has_papers": true,
  "is_current": true,  // 表示是否是今天的数据
  "today": "2023-05-10",
  "file_date": "2023-05-10",
  "total_entries": 50,
  "filename": "arxiv_AI_2023-05-10_(50entries).txt",
  "file_modified": "2023-05-10 15:30:45",
  "message": "Found 50 papers from 2023-05-10, last updated on 2023-05-10 15:30:45. This is today's data. Use get_latest_titles to read it."
}
```

如果不是今天的数据，会建议使用`crawl_latest_papers`获取最新数据。

### 2. crawl_latest_papers

触发爬虫抓取最新的arXiv CS.AI论文标题并生成文件。这将启动浏览器并从arXiv网站获取今天的数据。

```
功能: 抓取今天的arXiv论文（需要网络连接，会启动浏览器）
参数: 无
返回: 
{
  "success": true,
  "date": "2023-05-10",
  "total_entries": 50,
  "filename": "arxiv_AI_2023-05-10_(50entries).txt",
  "is_current": true,
  "message": "Successfully crawled 50 papers from 2023-05-10. This is today's data."
}
```

### 3. get_latest_titles

从本地文件读取最近一次抓取的arXiv CS.AI论文标题列表。不会进行网络爬取，只读取已有数据。

```
功能: 获取最新论文标题（从本地文件读取，不进行网络爬取）
参数: 
{
  "limit": 10  // 可选，限制返回标题数量
}
返回:
{
  "success": true,
  "date": "2023-05-10",
  "total_entries": 50,
  "titles_count": 10,
  "titles": ["标题1", "标题2", ...],
  "is_current": true,
  "message": "Retrieved 10 paper titles from 2023-05-10. This is today's data."
}
```

## 推荐使用流程

当客户端请求"最新的arxiv的人工智能论文"时，建议按照以下流程使用工具：

1. 首先调用 `check_latest_paper_info` 检查是否已有**今天日期**的论文数据
   - 查看返回的 `is_current` 字段，确认数据是否是今天的
   
2. 根据检查结果选择接下来的操作：
   - 如果 `is_current` 为 `true`，说明已有今天的数据，直接调用 `get_latest_titles` 获取论文标题
   - 如果 `is_current` 为 `false` 或没有数据，调用 `crawl_latest_papers` 获取今天的最新数据

这种基于日期的缓存策略可以避免在同一天内多次爬取相同的数据，提高效率。

## 在MCP客户端中使用

### Cursor

1. 打开设置 -> MCP → Add new MCP server
2. 类型选择 command
3. 名称可自定义（如"arxiv_crawler"）
4. 执行命令设置为：
   ```
   python /绝对路径/到项目目录/arxiv_server.py
   ```

   例如Windows系统上：
   ```
   python E:/development/arxiv_demo1/arxiv_server.py
   ```

### Cline

在配置文件中添加：

```json
{
    "mcpServers": {
        "arxiv_crawler": {
            "command": "python",
            "args": [
                "E:/development/arxiv_demo1/arxiv_server.py"
            ]
        }
    }
}
```

### Claude Desktop

与Cursor类似的配置方式，或添加以下配置：

```json
{
    "modelTools": {
        "servers": [
            {
                "name": "arxiv_crawler",
                "type": "command",
                "command": "python",
                "args": ["E:/development/arxiv_demo1/arxiv_server.py"]
            }
        ]
    }
}
```

### 其他支持MCP的客户端

可以参考以下通用配置格式：

```json
{
    "name": "arxiv_crawler",
    "type": "command",
    "command": "python",
    "args": ["E:/development/arxiv_demo1/arxiv_server.py"]
}
```

请根据您的实际项目路径替换上述示例中的路径。

## 架构说明

为了解决Playwright同步API与asyncio的兼容性问题，本项目采用了以下架构：

1. `arxiv_crawler.py` - 一个完全独立的爬虫脚本，使用Playwright的同步API
2. `arxiv_server.py` - MCP服务器，使用asyncio，通过子进程调用爬虫脚本

这种分离架构可以确保Playwright的同步API不会在asyncio事件循环中运行，从而避免冲突。

## 常见问题解决

### 安装依赖时出错

- 如果MCP安装失败，请确保使用的是Python 3.8+：
  ```bash
  python --version
  pip install mcp
  ```

- 如果Playwright安装失败，可以尝试：
  ```bash
  pip uninstall playwright
  pip install playwright
  playwright install chromium
  ```

### 运行时出错

- 如果看到 "Playwright Sync API inside asyncio loop" 错误，请确保使用的是最新版本的代码，该版本已通过分离架构解决了这个问题。

- 如果客户端显示乱码，请检查系统的字符编码设置，确保使用UTF-8编码。

### 功能问题

- 如果客户端同时调用了爬虫和读取标题的API，这可能是因为客户端没有正确理解基于日期的缓存策略。请参考上方的"推荐使用流程"部分。

## 注意事项

- 爬虫脚本现在默认使用无头模式，提高了稳定性
- 如需抓取更多论文，可修改arxiv_crawler.py中URL的`show`参数
- 如遇到错误，程序会自动保存错误截图以便调试
- MCP服务器使用stdio作为传输方式，适合与Cursor等客户端集成
- 系统使用基于日期的缓存策略，同一天内只需爬取一次，之后可直接读取缓存
