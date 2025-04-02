from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import os
import glob
import re
import io
import sys
import asyncio
import json
import subprocess
import time
from datetime import datetime, date

# Ensure proper encoding for stdin/stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Initialize MCP server
mcp = FastMCP("arxiv_crawler")

# Store latest crawling result
latest_result = None

# Get absolute script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Debug log function
def log_debug(message):
    """Write debug message to log file"""
    with open(os.path.join(SCRIPT_DIR, "arxiv_server_debug.log"), "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

@mcp.tool()
async def check_latest_paper_info() -> Dict[str, Any]:
    """Check if there are already crawled arXiv papers for the current date.
    
    This tool checks if a paper file for today's date already exists.
    - If a file for today exists, it suggests using get_latest_titles.
    - If no file for today exists, it suggests using crawl_latest_papers.
    
    No web crawling is performed, only checking existing files.
    
    Returns information about the latest paper file and whether it's current.
    """
    try:
        # Get today's date
        today = date.today().strftime("%Y-%m-%d")
        
        # Log current directory and script directory
        cwd = os.getcwd()
        log_debug(f"Current working directory: {cwd}")
        log_debug(f"Script directory: {SCRIPT_DIR}")
        
        # Search in both current directory and script directory
        pattern = "arxiv_AI_*.txt"
        cwd_files = glob.glob(pattern)
        script_dir_files = glob.glob(os.path.join(SCRIPT_DIR, pattern))
        
        # Combine file lists and make paths absolute
        files = [os.path.abspath(f) for f in cwd_files]
        files.extend(script_dir_files)
        
        # Log found files
        log_debug(f"Found files: {files}")
        
        if not files:
            # Try a more aggressive search
            for root, dirs, found_files in os.walk(SCRIPT_DIR):
                for file in found_files:
                    if file.startswith("arxiv_AI_") and file.endswith(".txt"):
                        files.append(os.path.join(root, file))
            
            log_debug(f"After deeper search, found files: {files}")
            
            # If still no files, look specifically for today's file
            todays_file = os.path.join(SCRIPT_DIR, f"arxiv_AI_{today}_(140entries).txt")
            if os.path.exists(todays_file):
                files.append(todays_file)
                log_debug(f"Found today's file directly: {todays_file}")
        
        if not files:
            return {
                "success": False,
                "has_papers": False,
                "is_current": False,
                "today": today,
                "message": "No paper files found. You need to run crawl_latest_papers to get today's papers."
            }
            
        # Sort files by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        latest_file = files[0]
        log_debug(f"Selected latest file: {latest_file}")
        
        # Extract information from filename
        filename = os.path.basename(latest_file)
        date_match = re.search(r'arxiv_AI_(.+?)_\((\d+)entries\)', filename)
        if date_match:
            file_date = date_match.group(1)
            total_entries = int(date_match.group(2))
        else:
            file_date = "unknown_date"
            total_entries = 0
        
        log_debug(f"Extracted date: {file_date}, entries: {total_entries}")
        
        # Get file modification time
        file_time = os.path.getmtime(latest_file)
        file_modified = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_time))
        
        # Check if file is for today
        is_current = (file_date == today)
        log_debug(f"Is current: {is_current} (today: {today}, file_date: {file_date})")
        
        # Create appropriate message
        if is_current:
            message = f"Found {total_entries} papers from {file_date}, last updated on {file_modified}. This is today's data. Use get_latest_titles to read it."
        else:
            message = f"Found {total_entries} papers from {file_date}, last updated on {file_modified}. This is not today's data ({today}). Consider using crawl_latest_papers to get the latest papers."
        
        return {
            "success": True,
            "has_papers": True,
            "is_current": is_current,
            "today": today,
            "file_date": file_date,
            "total_entries": total_entries,
            "filename": latest_file,
            "file_modified": file_modified,
            "message": message
        }
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Exception in check_latest_paper_info: {error_msg}")
        return {
            "success": False,
            "has_papers": False,
            "is_current": False,
            "today": date.today().strftime("%Y-%m-%d"),
            "error": error_msg
        }

@mcp.tool()
async def crawl_latest_papers() -> Dict[str, Any]:
    """Fetch the latest arXiv CS.AI paper titles by crawling the website.
    
    This will launch a browser and fetch today's papers from arXiv.
    Use this when:
    - You need papers for today's date
    - There are no local files for today's date
    - You want to refresh the data for today
    
    Returns information about the crawling result, including date, paper count and filename
    """
    global latest_result
    try:
        # Run the crawler script as a separate process
        crawler_path = os.path.join(SCRIPT_DIR, "arxiv_crawler.py")
        log_debug(f"Running crawler: {crawler_path}")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, crawler_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode('utf-8').strip()
        stderr_text = stderr.decode('utf-8')
        
        log_debug(f"Crawler return code: {process.returncode}")
        log_debug(f"Crawler stderr: {stderr_text}")
        
        if process.returncode != 0 or not stdout_text:
            # Print the stderr output for debugging
            print(f"Crawler stderr: {stderr_text}", file=sys.stderr)
            return {
                "success": False,
                "error": "Error during crawler execution"
            }
        
        try:
            # Parse the JSON output from the crawler process
            result = json.loads(stdout_text)
            if "error" in result and not result.get("success", True):
                return {
                    "success": False,
                    "error": result["error"]
                }
                
            latest_result = result
            today = date.today().strftime("%Y-%m-%d")
            is_current = (result["date"] == today)
            
            # Create appropriate message
            if is_current:
                message = f"Successfully crawled {result['total_entries']} papers from {result['date']}. This is today's data."
            else:
                message = f"Successfully crawled {result['total_entries']} papers from {result['date']}. Note: The crawled data is not from today."
            
            return {
                "success": True,
                "date": result["date"],
                "total_entries": result["total_entries"],
                "filename": result["filename"],
                "is_current": is_current,
                "message": message
            }
        except json.JSONDecodeError:
            log_debug(f"Failed to parse JSON: {stdout_text}")
            print(f"Failed to parse JSON: {stdout_text}", file=sys.stderr)
            return {
                "success": False,
                "error": "Failed to parse crawler output"
            }
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Exception in crawl_latest_papers: {error_msg}")
        print(f"Exception in crawl_latest_papers: {error_msg}", file=sys.stderr)
        return {
            "success": False,
            "error": error_msg
        }

@mcp.tool()
async def get_latest_titles(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get the list of latest arXiv CS.AI paper titles from local files.
    
    This reads paper titles from already crawled local files.
    No web crawling is performed - it only reads existing data.
    
    Args:
        limit: Optional maximum number of titles to return
        
    Returns the list of paper titles from the most recent local file
    """
    global latest_result
    
    # If no latest result in memory, try to read from file
    if latest_result is None:
        try:
            # First check if today's file exists directly
            today = date.today().strftime("%Y-%m-%d")
            todays_file = os.path.join(SCRIPT_DIR, f"arxiv_AI_{today}_(140entries).txt")
            
            log_debug(f"Looking for today's file directly: {todays_file}")
            if os.path.exists(todays_file):
                files = [todays_file]
                log_debug(f"Found today's file: {todays_file}")
            else:
                # Search in both current directory and script directory
                pattern = "arxiv_AI_*.txt"
                cwd_files = glob.glob(pattern)
                script_dir_files = glob.glob(os.path.join(SCRIPT_DIR, pattern))
                
                # Combine file lists and make paths absolute
                files = [os.path.abspath(f) for f in cwd_files]
                files.extend(script_dir_files)
                
                log_debug(f"Found files: {files}")
                
                if not files:
                    # Try a more aggressive search
                    for root, dirs, found_files in os.walk(SCRIPT_DIR):
                        for file in found_files:
                            if file.startswith("arxiv_AI_") and file.endswith(".txt"):
                                files.append(os.path.join(root, file))
                    
                    log_debug(f"After deeper search, found files: {files}")
            
            if not files:
                return {
                    "success": False,
                    "error": "No crawled paper files found. Please run crawl_latest_papers first."
                }
                
            # Sort files by modification time (newest first)
            files.sort(key=os.path.getmtime, reverse=True)
            latest_file = files[0]
            log_debug(f"Selected latest file for reading: {latest_file}")
            
            # Extract information from filename
            filename = os.path.basename(latest_file)
            date_match = re.search(r'arxiv_AI_(.+?)_\((\d+)entries\)', filename)
            if date_match:
                file_date = date_match.group(1)
                total_entries = int(date_match.group(2))
            else:
                file_date = "unknown_date"
                total_entries = 0
                
            log_debug(f"Extracted date: {file_date}, entries: {total_entries}")
            
            # Read file content
            with open(latest_file, "r", encoding="utf-8") as f:
                titles = [line.strip() for line in f if line.strip()]
            
            log_debug(f"Read {len(titles)} titles from file")
                
            latest_result = {
                "date": file_date,
                "total_entries": total_entries,
                "titles": titles,
                "filename": latest_file
            }
        except Exception as e:
            error_msg = str(e)
            log_debug(f"Exception in get_latest_titles: {error_msg}")
            print(f"Exception in get_latest_titles: {error_msg}", file=sys.stderr)
            return {
                "success": False,
                "error": f"Error reading file: {error_msg}"
            }
    
    # If still no result, return error
    if latest_result is None:
        return {
            "success": False,
            "error": "No paper data available, please call crawl_latest_papers first"
        }
    
    # Return titles based on limit
    titles_to_return = latest_result["titles"]
    if limit is not None and limit > 0:
        titles_to_return = titles_to_return[:limit]
    
    # Check if data is for today
    today = date.today().strftime("%Y-%m-%d")
    is_current = (latest_result["date"] == today)
    
    # Create appropriate message
    if is_current:
        message = f"Retrieved {len(titles_to_return)} paper titles from {latest_result['date']}. This is today's data."
    else:
        message = f"Retrieved {len(titles_to_return)} paper titles from {latest_result['date']}. Note: This is not today's data ({today})."
    
    return {
        "success": True,
        "date": latest_result["date"],
        "total_entries": latest_result["total_entries"],
        "titles_count": len(titles_to_return),
        "titles": titles_to_return,
        "is_current": is_current,
        "message": message
    }

if __name__ == "__main__":
    # Create log file
    log_file = os.path.join(SCRIPT_DIR, "arxiv_server_debug.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Server started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Script directory: {SCRIPT_DIR}\n")
        f.write(f"Current working directory: {os.getcwd()}\n")
    
    # Run MCP server
    # Use stdio as transport method, which can be called by various MCP clients
    mcp.run(transport='stdio') 