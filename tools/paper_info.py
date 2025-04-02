from typing import Dict, Any
import os
import glob
import re
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

def log_debug(message):
    """Write debug message to log file"""
    logger.debug(message)

async def check_latest_paper_info(base_dir: str) -> dict:
    """Check if there are already crawled arXiv papers for today's date.
    
    This will look for files matching the pattern arxiv_AI_YYYY-MM-DD_(140entries).txt
    and check if any are from today.
    
    Returns information about whether papers are available and if they are current
    """
    try:
        log_debug("========== 开始检查论文信息 ==========")
        log_debug(f"基础目录: {base_dir}")
        log_debug(f"基础目录是否存在: {os.path.exists(base_dir)}")
        log_debug(f"当前工作目录: {os.getcwd()}")
        log_debug(f"当前工作目录内容: {os.listdir('.')}")
        
        if os.path.exists(base_dir):
            log_debug(f"基础目录内容: {os.listdir(base_dir)}")
        
        # 获取今天的日期
        today = datetime.now().strftime("%Y-%m-%d")
        log_debug(f"今天的日期: {today}")
        
        # 详细记录搜索路径
        base_pattern = os.path.join(base_dir, "arxiv_AI_*.txt")
        log_debug(f"在基础目录搜索模式: {base_pattern}")
        
        # 只在BASE_DIR中搜索文件，不递归
        all_files = glob.glob(base_pattern)
        log_debug(f"基础目录找到的文件: {all_files}")
        
        for file_path in all_files:
            try:
                full_path = os.path.abspath(file_path)
                mtime = os.path.getmtime(full_path)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                size = os.path.getsize(full_path)
                exists = os.path.exists(full_path)
                log_debug(f"文件详情: 路径={full_path}, 大小={size}字节, 修改时间={mtime_str}, 存在={exists}")
            except Exception as e:
                log_debug(f"获取文件详情失败: {file_path}, 错误: {str(e)}")
        
        if not all_files:
            log_debug("未找到任何文件，返回空结果")
            return {
                "success": True,
                "has_papers": False,
                "is_current": False,
                "message": f"No papers found for {today}",
                "data": None
            }
        
        # 按修改时间排序
        latest_file = max(all_files, key=os.path.getmtime)
        log_debug(f"最新的文件: {latest_file}")
        log_debug(f"文件修改时间: {datetime.fromtimestamp(os.path.getmtime(latest_file))}")
        log_debug(f"文件大小: {os.path.getsize(latest_file)} 字节")
        
        # 提取日期和条目数
        match = re.search(r'arxiv_AI_(\d{4}-\d{2}-\d{2})_\((\d+)entries\)\.txt', latest_file)
        if not match:
            log_debug(f"文件名格式无效: {latest_file}")
            return {
                "success": True,
                "has_papers": True,
                "is_current": False,
                "message": "Found papers but date format is invalid"
            }
        
        file_date = match.group(1)
        total_entries = int(match.group(2))
        log_debug(f"从文件名中提取的日期: {file_date}")
        log_debug(f"从文件名中提取的条目数: {total_entries}")
        
        # 检查是否是今天的文件
        is_current = file_date == today
        log_debug(f"是否是今天的文件: {is_current}")
        
        # 读取文件内容的前几行
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                first_lines = [next(f) for _ in range(3)]
                log_debug(f"文件内容前几行: {first_lines}")
        except Exception as e:
            log_debug(f"读取文件内容失败: {str(e)}")
        
        log_debug("========== 检查完成，返回结果 ==========")
        return {
            "success": True,
            "has_papers": True,
            "is_current": is_current,
            "message": f"Found {total_entries} papers from {file_date}",
            "data": {
                "date": file_date,
                "total_entries": total_entries,
                "filename": os.path.basename(latest_file)
            }
        }
        
    except Exception as e:
        log_debug(f"Error in check_latest_paper_info: {str(e)}")
        return {
            "success": False,
            "message": "Failed to check paper info",
            "error": str(e)
        } 