from typing import Dict, Any
import os
import sys
import asyncio
import logging
import json
from datetime import date, datetime
import re
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

def log_debug(message):
    """Write debug message to log file"""
    logger.debug(message)

async def crawl_latest_papers(base_dir: str) -> dict:
    """Crawl the latest arXiv CS.AI papers.
    
    This will launch a browser and fetch today's papers from arXiv.
    Use this when:
    - You need papers for today's date
    - There are no local files for today's date
    - You want to refresh the data for today
    
    Returns information about the crawling result, including date, paper count and filename
    """
    try:
        log_debug("Starting crawler...")
        log_debug(f"Base directory: {base_dir}")
        
        # 获取今天的日期
        today = date.today().strftime("%Y-%m-%d")
        log_debug(f"Today's date: {today}")
        
        # 使用传入的基础目录
        user_data_dir = os.path.join(base_dir, "chrome_data")
        
        log_debug("Launching browser...")
        async with async_playwright() as p:
            # 使用持久化上下文
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=['--start-maximized'],
                slow_mo=500  # 添加延迟以提高稳定性
            )
            
            # 创建新页面
            page = await context.new_page()
            
            # 设置视口大小
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 设置页面加载超时
            page.set_default_timeout(30000)
            
            log_debug("Navigating to arXiv...")
            await page.goto(
                "https://arxiv.org/list/cs.AI/recent?show=250",
                wait_until="domcontentloaded"
            )
            
            # 提取H3文本
            h3_element = page.locator("dl#articles > h3").first
            h3_text = await h3_element.inner_text()
            log_debug(f"Raw text: {h3_text}")
            
            # 提取日期部分
            date_match = re.search(r'^([A-Za-z]{3},\s\d{1,2}\s[A-Za-z]{3}\s\d{4})', h3_text)
            if not date_match:
                raise Exception(f"Could not extract date from text: {h3_text}")
            
            arxiv_date_str = date_match.group(1)
            log_debug(f"arXiv date: {arxiv_date_str}")
            
            # 将arXiv日期转换为标准格式
            try:
                arxiv_date = datetime.strptime(arxiv_date_str, "%a, %d %b %Y")
                formatted_date = arxiv_date.strftime("%Y-%m-%d")
            except ValueError as e:
                log_debug(f"Date format conversion failed, using original string: {str(e)}")
                formatted_date = arxiv_date_str.replace(",", "").replace(" ", "_")
            
            # 解析论文数量
            count_match = re.search(r'showing (?:first )?\d+ of (\d+) entries', h3_text)
            if not count_match:
                raise Exception(f"Could not parse paper count")
            
            total_entries = int(count_match.group(1))
            log_debug(f"Found {total_entries} papers")
            
            # 提取标题
            log_debug("Extracting titles...")
            title_elements = page.locator("dd div.list-title.mathjax")
            titles = []
            for i in range(await title_elements.count()):
                title = await title_elements.nth(i).inner_text()
                titles.append(title.replace("Title:", "").strip())
            
            # 结果验证
            if len(titles) != total_entries:
                log_debug(f"Warning: Found {len(titles)} titles (expected {total_entries})")
                if len(titles) < total_entries:
                    log_debug("Suggestion: Increase show parameter in URL to ?show=500")
            
            # 保存结果
            filename = f"arxiv_AI_{formatted_date}_({total_entries}entries).txt"
            filepath = os.path.join(base_dir, filename)
            log_debug(f"Current working directory: {os.getcwd()}")
            log_debug(f"Script directory: {base_dir}")
            log_debug(f"Saving to file: {filepath}")
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(titles[:total_entries]))
            
            # 等待一段时间确保资源释放
            await asyncio.sleep(2)
            
            log_debug("Closing browser...")
            await context.close()
            
            # 返回结果
            result = {
                "success": True,
                "date": formatted_date,
                "total_entries": total_entries,
                "filename": filename,
                "message": f"Successfully crawled {len(titles)} papers"
            }
            
            log_debug(f"Returning result: {json.dumps(result)}")
            return result
            
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Error in crawl_latest_papers: {error_msg}")
        
        # 保存错误截图
        try:
            if 'page' in locals():
                await page.screenshot(path=os.path.join(base_dir, "arxiv_error.png"))
        except Exception as screenshot_error:
            log_debug(f"Failed to save error screenshot: {str(screenshot_error)}")
        
        return {
            "success": False,
            "message": error_msg,
            "error": error_msg
        } 