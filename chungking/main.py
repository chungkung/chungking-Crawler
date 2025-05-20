import requests
from bs4 import BeautifulSoup
import logging
from playwright.async_api import async_playwright
import asyncio

logging.basicConfig(
    filename='crawler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.visited_urls = set()  # URL去重集合

    async def fetch_page(self, url):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                content = await page.content()
                await browser.close()
                return (url, content)
        except Exception as e:
            logging.error(f'请求错误 {url}: {e}')
            return (url, None)

    def crawl_concurrently(self, urls, max_workers=5):
        """使用线程池并发爬取多个URL"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.fetch_page, urls))
        return results

    def extract_links(self, html):
        soup = BeautifulSoup(html, 'lxml')
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            if link.startswith('/'):
                link = self.base_url + link
            links.append(link)
        return links

    def extract_content(self, html):
        """提取页面核心内容（示例：标题和正文）"""
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('h1').text.strip() if soup.find('h1') else '无标题'
        content = ''.join([p.text for p in soup.find_all('p')[:5]]) if soup.find_all('p') else '无正文'
        return {'title': title, 'content': content}

import concurrent.futures

if __name__ == '__main__':
    crawler = WebCrawler('https://example.com')
    # 初始页面爬取
    initial_response = crawler.fetch_page('https://example.com')
    if initial_response[1]:  # 第二个元素是页面内容
        # 提取并去重链接
        extracted_links = crawler.extract_links(initial_response[1])
        new_links = [link for link in extracted_links if link not in crawler.visited_urls]
        crawler.visited_urls.update(new_links)
        print(f'获取到 {len(new_links)} 个新链接，开始并发爬取...')

        # 并发爬取前20个新链接
        crawl_results = crawler.crawl_concurrently(new_links[:20])

        # 处理并发结果
        for url, html in crawl_results:
            if html:
                content = crawler.extract_content(html)
                print(f'\n爬取成功 {url}:')
                print(f'标题: {content["title"]}')
                print(f'正文摘要: {content["content"][:200]}...')
            else:
                print(f'跳过无效链接 {url}')