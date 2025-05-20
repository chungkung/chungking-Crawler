import time
import random
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from playwright.sync import sync_playwright

# 导入配置
from config import (
    BASE_URL, USER_AGENTS, MAX_WORKERS, CRAWL_DEPTH,
    REQUEST_TIMEOUT, CRAWL_DELAY, CONTENT_SELECTORS,
    USE_PLAYWRIGHT, PLAYWRIGHT_TIMEOUT, PROXY_POOL
)

visited_urls = set()

class WebCrawler:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.playwright = sync_playwright().start() if USE_PLAYWRIGHT else None

    def _get_proxy(self):
        if PROXY_POOL:
            return {'http': random.choice(PROXY_POOL), 'https': random.choice(PROXY_POOL)}
        return None

    def _fetch_with_requests(self, url):
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            response = requests.get(
                url, headers=headers, timeout=REQUEST_TIMEOUT,
                proxies=self._get_proxy()
            )
            response.raise_for_status()
            return (url, response.text)
        except Exception as e:
            print(f'请求失败 {url}: {str(e)}')
            return (url, None)

    def _fetch_with_playwright(self, url):
        browser = self.playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url, timeout=PLAYWRIGHT_TIMEOUT * 1000)
            html = page.content()
            return (url, html)
        except Exception as e:
            print(f'Playwright请求失败 {url}: {str(e)}')
            return (url, None)
        finally:
            browser.close()

    def fetch_page(self, url):
        time.sleep(CRAWL_DELAY)
        if USE_PLAYWRIGHT:
            return self._fetch_with_playwright(url)
        else:
            return self._fetch_with_requests(url)

    def extract_links(self, html, current_depth):
        if current_depth >= CRAWL_DEPTH:
            return []
        soup = BeautifulSoup(html, 'lxml')
        links = []
        for a_tag in soup.find_all('a', href=True):
            abs_url = urljoin(self.base_url, a_tag['href'])
            if abs_url not in visited_urls:
                visited_urls.add(abs_url)
                links.append(abs_url)
        return links

    def extract_content(self, html):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.select_one(CONTENT_SELECTORS['title']).text if CONTENT_SELECTORS['title'] else ''
        content = ' '.join([p.text for p in soup.select(CONTENT_SELECTORS['content'])]) if CONTENT_SELECTORS['content'] else ''
        return {'title': title, 'content': content}

if __name__ == '__main__':
    crawler = WebCrawler()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(crawler.fetch_page, BASE_URL)]
        for future in futures:
            url, html = future.result()
            if html:
                print(crawler.extract_content(html))
                links = crawler.extract_links(html, current_depth=1)
                print(f'提取到链接：{links}')