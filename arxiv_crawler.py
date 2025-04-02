#!/usr/bin/env python
"""
独立的arXiv爬虫脚本，可以作为单独进程运行
"""
from playwright.sync_api import sync_playwright
import re
import time
from datetime import datetime
import sys

def arxiv_dynamic_crawler():
    with sync_playwright() as p:
        # ===== 浏览器配置 =====
        browser = p.chromium.launch(
            headless=True,  # 改为无头模式以提高稳定性
            channel="chrome",
            args=["--start-maximized"],
            slow_mo=500
        )
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # ===== 访问目标页面 =====
            print(f"🕒 {datetime.now().strftime('%H:%M:%S')} 访问arXiv...", file=sys.stderr)
            page.goto(
                "https://arxiv.org/list/cs.AI/recent?show=250",
                timeout=30000,
                wait_until="domcontentloaded"
            )

            # ===== 提取H3文本 =====
            h3_text = page.locator("dl#articles > h3").first.inner_text()
            print(f"🔍 原始文本: {h3_text}", file=sys.stderr)

            # ===== 提取日期部分 =====
            date_match = re.search(r'^([A-Za-z]{3},\s\d{1,2}\s[A-Za-z]{3}\s\d{4})', h3_text)
            if not date_match:
                raise Exception(f"无法从文本中提取日期: {h3_text}")
            
            arxiv_date_str = date_match.group(1)
            print(f"📅 arXiv发布日期: {arxiv_date_str}", file=sys.stderr)

            # 将arXiv日期转换为标准格式（如：2025-04-02）
            try:
                arxiv_date = datetime.strptime(arxiv_date_str, "%a, %d %b %Y")
                formatted_date = arxiv_date.strftime("%Y-%m-%d")
            except ValueError as e:
                print(f"⚠️ 日期格式转换失败，使用原始日期字符串: {str(e)}", file=sys.stderr)
                formatted_date = arxiv_date_str.replace(",", "").replace(" ", "_")

            # ===== 解析论文数量 =====
            count_match = re.search(r'showing (?:first )?\d+ of (\d+) entries', h3_text)
            if not count_match:
                raise Exception(f"无法解析论文数量信息")
            
            total_entries = int(count_match.group(1))
            print(f"📊 检测到 {total_entries} 篇当日论文", file=sys.stderr)

            # ===== 提取所有标题 =====
            title_elements = page.locator("dd div.list-title.mathjax")
            titles = [title.inner_text().replace("Title:", "").strip() 
                     for title in title_elements.all()]
            
            # ===== 结果验证 =====
            if len(titles) != total_entries:
                print(f"⚠️ 注意: 当前页面显示 {len(titles)} 篇论文（总数 {total_entries} 篇）", file=sys.stderr)
                if len(titles) < total_entries:
                    print("💡 建议: 修改URL中的show参数为更大值，如 ?show=500", file=sys.stderr)

            # ===== 保存结果 =====
            filename = f"arxiv_AI_{formatted_date}_({total_entries}entries).txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(titles[:total_entries]))
            print(f"💾 结果已保存到: {filename}", file=sys.stderr)
            
            # 输出机器可读的结果到标准输出
            import json
            result = {
                "date": formatted_date,
                "total_entries": total_entries,
                "titles": titles[:total_entries],
                "filename": filename
            }
            print(json.dumps(result))
            
            return 0

        except Exception as e:
            print(f"❌ 发生错误: {str(e)}", file=sys.stderr)
            page.screenshot(path="arxiv_error.png")
            # 输出错误信息到标准输出以便调用者处理
            import json
            print(json.dumps({"success": False, "error": str(e)}))
            return 1
        finally:
            time.sleep(2)
            context.close()
            browser.close()

if __name__ == "__main__":
    sys.exit(arxiv_dynamic_crawler()) 