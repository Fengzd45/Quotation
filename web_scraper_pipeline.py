import sqlite3
import requests
from bs4 import BeautifulSoup
import os
import json
import datetime

# 1. 模拟浏览器请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def init_db():
    """初始化数据库表结构"""
    conn = sqlite3.connect('nursery_quotes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quote_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT,
            quote_number TEXT,
            quote_date TEXT,
            category TEXT,
            ordered INTEGER,
            botanical_name TEXT,
            size TEXT,
            net_price REAL,
            extension REAL,
            file_source TEXT,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def run_web_scraper():
    """网络爬虫核心逻辑"""
    print("🚀 [爬虫引擎] 开始抓取 Art's Nursery 供应商数据...")
    init_db()
    
    # 模拟抓取到的测试样本数据（实际运行时请替换为您的具体抓取解析逻辑）
    sample_data = [
        ("Art's Nursery (Website)", "WEB_SCRAPE", "2026-07-17", "Grass", 0, "Miscanthus sinensis", "#1 Gallon", 22.33, 0.0, "https://www.artsnursery.com/catalog"),
        ("Art's Nursery (Website)", "WEB_SCRAPE", "2026-07-17", "Shrub", 0, "Hydrangea macrophylla", "#2 Gallon", 40.00, 0.0, "https://www.artsnursery.com/catalog"),
        ("Art's Nursery (Website)", "WEB_SCRAPE", "2026-07-17", "Tree", 0, "Acer palmatum 'Bloodgood' (Red Maple)", "#5 Gallon", 95.50, 0.0, "https://www.artsnursery.com/catalog")
    ]
    
    conn = sqlite3.connect('nursery_quotes.db')
    cursor = conn.cursor()
    
    for item in sample_data:
        cursor.execute('''
            INSERT INTO quote_items (supplier, quote_number, quote_date, category, ordered, botanical_name, size, net_price, extension, file_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', item)
        
    conn.commit()
    conn.close()
    print(f"✅ [爬虫引擎] 成功向数据库写入 {len(sample_data)} 条网络报价。")

def sync_db_to_json():
    """【核心升级】从数据库抽取最新数据，完全覆写同步到 quotes.json 供前端看板使用"""
    db_file = 'nursery_quotes.db'
    json_file = 'quotes.json'
    
    print("🔄 [数据对齐] 启动双轨同步：SQLite -> quotes.json ...")
    
    if not os.path.exists(db_file):
        print("⚠️ [数据对齐] 未找到数据库文件，取消 JSON 同步。")
        return

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # 让结果集以字典字典形式返回
    cursor = conn.cursor()
    
    try:
        # 按时间倒序拉取所有历史及最新报价数据
        cursor.execute("SELECT * FROM quote_items ORDER BY rowid DESC")
        rows = cursor.fetchall()
        
        json_ready_data = []
        for row in rows:
            item = dict(row)
            # 确保每一条记录在前端都有时间展示
            if 'imported_at' not in item or not item['imported_at']:
                item['imported_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            json_ready_data.append(item)
            
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_ready_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ [数据对齐] 成功！已同步 {len(json_ready_data)} 条高精度数据至前端 JSON 缓存。")
    except Exception as e:
        print(f"❌ [数据对齐] 同步失败，发生异常: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_web_scraper()   # 1. 运行爬虫写入数据库
    sync_db_to_json()   # 2. 将最新的数据库状态广播到 JSON 文件
