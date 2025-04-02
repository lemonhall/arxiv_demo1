from typing import Dict, Any
import os
import glob
import re
from datetime import date
import logging

logger = logging.getLogger(__name__)

def log_debug(message):
    """Write debug message to log file"""
    logger.debug(message)

async def get_latest_titles(base_dir: str) -> dict:
    """Get the latest arXiv CS.AI paper titles from the local file.
    
    This will read the most recent file containing paper titles.
    Use this when:
    - You want to get the titles from the most recent crawl
    - You don't need to fetch new data
    
    Returns the list of paper titles from the most recent crawl
    """
    try:
        log_debug("Getting latest titles...")
        log_debug(f"Base directory: {base_dir}")
        
        # 获取当前工作目录
        current_dir = os.getcwd()
        log_debug(f"Current working directory: {current_dir}")
        
        # 搜索最新的文件
        pattern = os.path.join(base_dir, "arxiv_AI_*.txt")
        all_files = glob.glob(pattern)
        log_debug(f"Found files: {all_files}")
        
        if not all_files:
            return {
                "success": False,
                "message": "No paper files found",
                "error": "No paper files found"
            }
        
        # 按修改时间排序
        latest_file = max(all_files, key=os.path.getmtime)
        log_debug(f"Latest file: {latest_file}")
        
        # 读取文件内容
        with open(latest_file, "r", encoding="utf-8") as f:
            titles = [line.strip() for line in f if line.strip()]
        
        # 提取日期和条目数
        match = re.search(r'arxiv_AI_(\d{4}-\d{2}-\d{2})_\((\d+)entries\)\.txt', latest_file)
        if not match:
            return {
                "success": False,
                "message": "Invalid filename format",
                "error": "Invalid filename format"
            }
        
        file_date = match.group(1)
        total_entries = int(match.group(2))
        
        return {
            "success": True,
            "message": f"Successfully retrieved {len(titles)} titles",
            "data": {
                "date": file_date,
                "total_entries": total_entries,
                "filename": os.path.basename(latest_file),
                "titles": titles
            }
        }
        
    except Exception as e:
        log_debug(f"Error in get_latest_titles: {str(e)}")
        return {
            "success": False,
            "message": "Failed to get titles",
            "error": str(e)
        } 