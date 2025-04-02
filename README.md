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
