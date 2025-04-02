from playwright.sync_api import sync_playwright
import re
import time
from datetime import datetime

def arxiv_dynamic_crawler():
    with sync_playwright() as p:
        # ===== 浏览器配置 =====
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--start-maximized"],
            slow_mo=500
        )
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # ===== 访问目标页面 =====
            print(f"🕒 {datetime.now().strftime('%H:%M:%S')} 访问arXiv...")
            page.goto(
                "https://arxiv.org/list/cs.AI/recent?show=250",
                timeout=30000,
                wait_until="domcontentloaded"
            )

            # ===== 提取H3文本 =====
            h3_text = page.locator("dl#articles > h3").first.inner_text()
            print(f"🔍 原始文本: {h3_text}")

            # ===== 提取日期部分 =====
            date_match = re.search(r'^([A-Za-z]{3},\s\d{1,2}\s[A-Za-z]{3}\s\d{4})', h3_text)
            if not date_match:
                raise Exception(f"无法从文本中提取日期: {h3_text}")
            
            arxiv_date_str = date_match.group(1)
            print(f"📅 arXiv发布日期: {arxiv_date_str}")

            # 将arXiv日期转换为标准格式（如：2025-04-02）
            try:
                arxiv_date = datetime.strptime(arxiv_date_str, "%a, %d %b %Y")
                formatted_date = arxiv_date.strftime("%Y-%m-%d")
            except ValueError as e:
                print(f"⚠️ 日期格式转换失败，使用原始日期字符串: {str(e)}")
                formatted_date = arxiv_date_str.replace(",", "").replace(" ", "_")

            # ===== 解析论文数量 =====
            count_match = re.search(r'showing (?:first )?\d+ of (\d+) entries', h3_text)
            if not count_match:
                raise Exception(f"无法解析论文数量信息")
            
            total_entries = int(count_match.group(1))
            print(f"📊 检测到 {total_entries} 篇当日论文")

            # ===== 提取所有标题 =====
            title_elements = page.locator("dd div.list-title.mathjax")
            titles = [title.inner_text().replace("Title:", "").strip() 
                     for title in title_elements.all()]
            
            # ===== 结果验证 =====
            if len(titles) != total_entries:
                print(f"⚠️ 注意: 当前页面显示 {len(titles)} 篇论文（总数 {total_entries} 篇）")
                if len(titles) < total_entries:
                    print("💡 建议: 修改URL中的show参数为更大值，如 ?show=500")

            # ===== 保存结果 =====
            filename = f"arxiv_AI_{formatted_date}_({total_entries}entries).txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(titles[:total_entries]))
            print(f"💾 结果已保存到: {filename}")
            
            return {
                "date": formatted_date,
                "total_entries": total_entries,
                "titles": titles,
                "filename": filename
            }

        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            page.screenshot(path="arxiv_error.png")
            raise
        finally:
            time.sleep(2)
            context.close()
            browser.close()

if __name__ == "__main__":
    print("🚀 arXiv动态数量爬虫启动")
    print("="*50)
    start_time = time.time()
    
    try:
        results = arxiv_dynamic_crawler()
        print("\n" + "="*50)
        print(f"⏱️ 总耗时: {time.time() - start_time:.2f}秒")
        print(f"📅 发布日期: {results['date']}")
        print(f"📊 总计获取论文数: {results['total_entries']}篇")
        print(f"💾 保存文件名: {results['filename']}")
    except Exception as e:
        print("\n" + "="*50)
        print(f"⚠️ 执行失败: {str(e)}")
        print("💡 调试建议:")
        print("1. 检查截图 arxiv_error.png")
        print("2. 手动访问页面确认日期格式")
        print("3. 检查网络连接")
