#!/usr/bin/env python
from mcp.server import FastMCP
import logging
import os
import sys
from tools.crawler import crawl_latest_papers
from tools.paper_info import check_latest_paper_info
from tools.titles import get_latest_titles

# 定义基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 清除可能存在的处理器
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'arxiv_server0.log'), mode='w', encoding='utf-8'),  # 使用写入模式，每次启动都是新日志
        logging.StreamHandler()  # 输出到控制台
    ]
)
logger = logging.getLogger(__name__)

def log_debug(message):
    """Write debug message to log file and print to console"""
    logger.debug(message)  # 使用debug级别，确保正确显示
    # 同时直接打印到控制台，确保可见
    sys.stdout.write(f"DEBUG: {message}\n")
    sys.stdout.flush()

# 记录基本环境信息
log_debug(f"Base directory: {BASE_DIR}")
log_debug(f"Current working directory: {os.getcwd()}")
if os.path.exists(BASE_DIR):
    log_debug(f"Base directory contents: {os.listdir(BASE_DIR)}")
else:
    log_debug("Base directory does not exist")

# 创建MCP服务器
mcp = FastMCP()

@mcp.tool()
async def crawl_latest_papers_tool() -> dict:
    """Fetch the latest arXiv CS.AI paper titles by crawling the website.
    
    This will launch a browser and fetch today's papers from arXiv.
    Use this when:
    - You need papers for today's date
    - There are no local files for today's date
    - You want to refresh the data for today
    
    Returns information about the crawling result, including date, paper count and filename
    """
    return await crawl_latest_papers(BASE_DIR)

@mcp.tool()
async def check_latest_paper_info_tool() -> dict:
    """Check if there are already crawled arXiv papers for today's date.
    
    This will look for files matching the pattern arxiv_AI_YYYY-MM-DD_(140entries).txt
    and check if any are from today.
    
    Returns information about whether papers are available and if they are current
    """
    return await check_latest_paper_info(BASE_DIR)

@mcp.tool()
async def get_latest_titles_tool() -> dict:
    """Get the latest arXiv CS.AI paper titles from the local file.
    
    This will read the most recent file containing paper titles.
    Use this when:
    - You want to get the titles from the most recent crawl
    - You don't need to fetch new data
    
    Returns the list of paper titles from the most recent crawl
    """
    return await get_latest_titles(BASE_DIR)

if __name__ == "__main__":
    log_debug("Starting MCP server...")
    mcp.run(transport='stdio') 