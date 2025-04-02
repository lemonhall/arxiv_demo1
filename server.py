from flask import Flask, jsonify, request, render_template_string
import main
import os
import glob
import re
import json

app = Flask(__name__)

# 存储最新的抓取结果
latest_result = None

@app.route('/api/crawl_latest_papers', methods=['POST'])
def crawl_latest_papers():
    """抓取arXiv CS.AI分类下的最新论文标题并保存为文件"""
    global latest_result
    try:
        # 调用主爬虫函数
        result = main.arxiv_dynamic_crawler()
        latest_result = result
        return jsonify({
            "success": True,
            "date": result["date"],
            "total_entries": result["total_entries"],
            "filename": result["filename"]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/get_latest_titles', methods=['POST'])
def get_latest_titles():
    """获取最近一次抓取的arXiv论文标题列表"""
    global latest_result
    
    # 获取请求参数
    data = request.json or {}
    limit = data.get('limit', None)
    if limit is not None:
        try:
            limit = int(limit)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "limit参数必须是整数"
            })
    
    # 如果内存中没有最新结果，尝试从文件中读取
    if latest_result is None:
        try:
            # 查找最新的文件
            files = glob.glob("arxiv_AI_*.txt")
            if not files:
                return jsonify({
                    "success": False,
                    "error": "没有找到已抓取的论文文件"
                })
                
            # 按修改时间排序文件
            latest_file = max(files, key=os.path.getmtime)
            
            # 从文件名提取信息
            date_match = re.search(r'arxiv_AI_(.+?)_\((\d+)entries\)', latest_file)
            if date_match:
                date = date_match.group(1)
                total_entries = int(date_match.group(2))
            else:
                date = "未知日期"
                total_entries = 0
                
            # 读取文件内容
            with open(latest_file, "r", encoding="utf-8") as f:
                titles = [line.strip() for line in f if line.strip()]
                
            latest_result = {
                "date": date,
                "total_entries": total_entries,
                "titles": titles,
                "filename": latest_file
            }
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"读取文件时出错: {str(e)}"
            })
    
    # 如果仍然没有结果，返回错误
    if latest_result is None:
        return jsonify({
            "success": False,
            "error": "没有可用的论文数据，请先调用抓取接口"
        })
    
    # 根据限制返回标题
    titles_to_return = latest_result["titles"]
    if limit is not None and limit > 0:
        titles_to_return = titles_to_return[:limit]
    
    return jsonify({
        "success": True,
        "date": latest_result["date"],
        "total_entries": latest_result["total_entries"],
        "titles_count": len(titles_to_return),
        "titles": titles_to_return
    })

# API接口文档页面
@app.route('/api', methods=['GET'])
def api_docs():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>arXiv AI论文爬虫API文档</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 30px; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            table { border-collapse: collapse; width: 100%; }
            th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            .endpoint { margin-bottom: 30px; }
            .method { font-weight: bold; color: #e97230; }
            .url { color: #008080; }
        </style>
    </head>
    <body>
        <h1>arXiv AI论文爬虫API文档</h1>
        <p>这是一个提供arXiv CS.AI论文抓取功能的简单API服务。</p>
        
        <h2>接口列表</h2>
        
        <div class="endpoint">
            <h3>1. 抓取最新arXiv论文</h3>
            <p>触发爬虫抓取最新的arXiv CS.AI论文标题并生成文件。</p>
            <p><span class="method">POST</span> <span class="url">/api/crawl_latest_papers</span></p>
            <h4>请求参数</h4>
            <p>无</p>
            <h4>响应示例</h4>
            <pre>{
  "success": true,
  "date": "2023-05-10",
  "total_entries": 50,
  "filename": "arxiv_AI_2023-05-10_(50entries).txt"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>2. 获取最新论文标题</h3>
            <p>获取最近一次抓取的arXiv CS.AI论文标题列表。</p>
            <p><span class="method">POST</span> <span class="url">/api/get_latest_titles</span></p>
            <h4>请求参数</h4>
            <table>
                <tr>
                    <th>参数名</th>
                    <th>类型</th>
                    <th>说明</th>
                    <th>是否必须</th>
                </tr>
                <tr>
                    <td>limit</td>
                    <td>整数</td>
                    <td>返回的标题数量上限</td>
                    <td>否</td>
                </tr>
            </table>
            <h4>请求示例</h4>
            <pre>{
  "limit": 10
}</pre>
            <h4>响应示例</h4>
            <pre>{
  "success": true,
  "date": "2023-05-10",
  "total_entries": 50,
  "titles_count": 10,
  "titles": ["标题1", "标题2", ...]
}</pre>
        </div>
        
        <h2>使用示例</h2>
        <h3>使用curl调用API</h3>
        <pre>curl -X POST http://localhost:5000/api/crawl_latest_papers</pre>
        <pre>curl -X POST -H "Content-Type: application/json" -d '{"limit": 5}' http://localhost:5000/api/get_latest_titles</pre>
        
        <h3>使用Python调用API</h3>
        <pre>import requests

# 抓取最新论文
response = requests.post('http://localhost:5000/api/crawl_latest_papers')
print(response.json())

# 获取最新论文标题
response = requests.post('http://localhost:5000/api/get_latest_titles', json={'limit': 5})
print(response.json())</pre>
    </body>
    </html>
    """
    return render_template_string(html)

# 添加一个简单的首页
@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>arXiv AI论文爬虫服务</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
            h1 { color: #333; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>arXiv AI论文爬虫服务</h1>
        <p>这是一个提供arXiv CS.AI论文抓取功能的API服务。</p>
        <p>详细API文档请访问: <a href="/api">/api</a></p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000) 