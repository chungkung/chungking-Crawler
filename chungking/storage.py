import csv
import json
import sqlite3
from datetime import datetime

def save_to_csv(data_list, filename=None):
    """将数据列表保存为CSV文件"""
    if not filename:
        filename = f'crawl_data_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'content', 'url'])
        writer.writeheader()
        writer.writerows(data_list)
    print(f'数据已保存至 {filename}')


def save_to_json(data_list, filename=None):
    """将数据列表保存为JSON文件"""
    if not filename:
        filename = f'crawl_data_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)
    print(f'数据已保存至 {filename}')


class SQLiteStorage:
    def __init__(self, db_name='crawl_data.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                url TEXT UNIQUE,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_data(self, data):
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO crawl_data (title, content, url)
                VALUES (?, ?, ?)
            ''', (data['title'], data['content'], data['url']))
            self.conn.commit()
        except Exception as e:
            print(f'保存数据到SQLite失败: {e}')

if __name__ == '__main__':
    # 测试示例
    test_data = [{'title':'测试标题','content':'测试内容','url':'https://example.com'}]
    save_to_csv(test_data)
    save_to_json(test_data)