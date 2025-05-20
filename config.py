# 爬虫配置文件
BASE_URL = 'https://example.com'
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
]  # 随机User-Agent列表
MAX_WORKERS = 5  # 并发线程数
CRAWL_DEPTH = 2  # 爬取深度（待后续实现）
USE_PLAYWRIGHT = False  # 是否使用Playwright处理动态网页
PLAYWRIGHT_TIMEOUT = 30  # Playwright超时时间（秒）
PROXY_POOL = []  # 代理IP池列表，格式：["http://ip:port", ...]
PROXY_RETRY_TIMES = 3  # 代理失败重试次数
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Celery消息队列地址
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Celery结果存储地址
CRAWL_DELAY = 1  # 爬取间隔（秒）
CONTENT_SELECTORS = {
    'title': 'h1',  # 标题选择器
    'content': 'p'   # 正文选择器
}