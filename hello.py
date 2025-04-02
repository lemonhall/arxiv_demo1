from playwright.sync_api import sync_playwright
import random
import time
from datetime import datetime

def arxiv_standard_crawler():
    with sync_playwright() as p:
        # ===== 浏览器配置 =====
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=[
                "--start-maximized",
                f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 125)}.0.0.0 Safari/537.36"
            ],
            slow_mo=500
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )

        # ===== 资源过滤 =====
        def route_interceptor(route):
            if any(ext in route.request.url for ext in [".jpg", ".png", ".gif"]):
                route.abort()
            else:
                route.continue_()
        context.route("**/*", route_interceptor)

        page = context.new_page()

        try:
            # ===== 访问页面 =====
            print(f"🕒 {datetime.now().strftime('%H:%M:%S')} 访问arXiv...")
            page.goto(
                "https://arxiv.org/list/cs.AI/recent?skip=0&show=250",
                timeout=30000,
                wait_until="domcontentloaded"
            )
            
            # ===== 等待加载 =====
            title_selector = "dd div.list-title.mathjax"
            for _ in range(3):
                if page.locator(title_selector).count() > 0:
                    break
                time.sleep(2)
                page.mouse.wheel(0, 500)
            else:
                raise Exception("元素加载超时")

            # ===== 数据提取 =====
            print("📊 提取数据中...")
            titles = page.locator(title_selector).all_inner_texts()
            titles = [t.replace("Title:", "").strip() for t in titles]
            
            # ===== 优化结果显示 =====
            print(f"\n✅ 成功获取 {len(titles)} 篇论文")
            print("最新完整标题：")
            for i, title in enumerate(titles[:50], 1):
                print(f"{i}. {title}")  # 完整显示标题
                
                # 如果需要保存到文件（含完整标题）
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                with open(f"arxiv_full_titles_{timestamp}.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(titles))
                    
            return titles

        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            page.screenshot(path="arxiv_error.png")
            raise
        finally:
            time.sleep(2)
            context.close()
            browser.close()

if __name__ == "__main__":
    print("🚀 arXiv爬虫启动（完整标题版）")
    start_time = time.time()
    try:
        results = arxiv_standard_crawler()
        print(f"⏱️ 总耗时: {time.time() - start_time:.2f}秒")
    except Exception as e:
        print(f"⚠️ 执行失败: {str(e)}")
