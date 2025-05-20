# FireCrawl 爬虫应用开发指南

[切换语言 / Switch Language]
- [中文 / Chinese](#chinese-version)
- [英文 / English](#english-version)

## 中文版本 / Chinese Version {#chinese-version}

## 项目概述
基于Python的通用网页爬虫工具，支持URL爬取、内容提取及简单数据存储，适用于小型网站数据采集场景。

## 技术栈
- 网络请求：requests（HTTP客户端）
- 内容解析：beautifulsoup4 + lxml（HTML/XML解析）
- 依赖管理：pip（通过requirements.txt管理）

## 架构模块
1. **网络请求模块**（`main.py`）：封装HTTP请求逻辑，支持超时控制（`REQUEST_TIMEOUT`）、随机User-Agent（`USER_AGENTS`）和并发爬取（`ThreadPoolExecutor`），处理网络异常并返回结构化结果。
2. **链接提取模块**（`main.py`）：使用BeautifulSoup解析HTML，提取所有超链接并转换为绝对路径，集成URL去重机制（`visited_urls`集合）避免重复爬取。
3. **配置模块**（`config.py`）：集中管理基础URL、User-Agent列表、并发线程数（`MAX_WORKERS`）、爬取延迟（`CRAWL_DELAY`）等参数，支持快速调整反爬策略。
4. **数据提取模块**（`main.py`）：基于配置的选择器（`CONTENT_SELECTORS`）提取页面标题、正文等核心内容，返回结构化数据（字典格式）。
5. **数据存储模块**（`storage.py`）：提供CSV和JSON两种存储方式，自动生成带时间戳的文件名，支持将爬取结果持久化到本地文件。

## 安装
通过pip安装：
```bash
pip install chungking
```

## 核心功能
### WebCrawler 类
用于网页爬取的核心类，初始化参数：
- `base_url`: 基础URL（可选，用于相对链接转换）

方法：
- `fetch_page(url)`: 异步获取页面内容，返回(url, html)
- `extract_links(html)`: 从HTML中提取链接列表
- `extract_content(html)`: 提取页面标题和正文内容

### API服务
安装后可启动API服务：
```bash
uvicorn chungking.api:app --host 0.0.0.0 --port 8000
```

## API端点说明
- `POST /scrape`: 爬取单个URL，返回markdown/html内容
  - 请求参数：`url`（目标URL）, `formats`（返回格式列表）
  - 响应示例：
    ```json
    {
      "success": true,
      "data": {
        "markdown": "# 页面标题\n\n正文内容",
        "html": "<html>...</html>",
        "metadata": {"title": "页面标题", "url": "https://example.com"}
      }
    }
    ```

- `POST /crawl`: 启动批量爬取任务
  - 请求参数：`url`（起始URL）, `limit`（最大链接数）, `max_depth`（最大深度）
  - 响应示例：{"success": true, "id": "crawl_12345", "url": "/crawl/crawl_12345"}

- `GET /crawl/{task_id}`: 检查爬取任务状态
  - 响应示例：{"status": "completed", "total": 10, "completed": 10, "data": [...]}


## 扩展功能说明
### 动态网页处理
集成Playwright支持JavaScript渲染页面，配置参数：`USE_PLAYWRIGHT`（布尔值，默认False），`PLAYWRIGHT_TIMEOUT`（超时时间，单位秒）。启用后自动处理动态加载内容。

### 代理池集成
添加代理IP池支持（基于`requests-proxy`），配置参数：`PROXY_POOL`（代理列表，格式：["http://ip:port", ...]），`PROXY_RETRY_TIMES`（代理失败重试次数）。请求时随机选择代理避免IP封禁。

### 深度爬取控制
实现爬取深度限制（`CRAWL_DEPTH`，默认3），防止无限递归。爬取时跟踪当前深度，超过限制后停止递归提取链接。

### 分布式爬取
集成Celery实现多节点协同爬取，配置参数：`CELERY_BROKER_URL`（消息队列地址），`CELERY_RESULT_BACKEND`（结果存储地址）。支持任务分发与结果汇总。

## 部署建议

## 开源协议 / Open Source License
本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。使用本项目时需遵守以下条款：
- 保留原项目的版权声明（包括本许可证和版权信息）。
- 不得将本项目用于非法或侵犯他人权益的用途。
- 本项目不提供任何形式的担保，作者对使用本项目导致的任何直接或间接损失不承担责任。

## 英文版本 / English Version {#english-version}

### Project Overview
A Python-based general-purpose web crawler tool that supports URL fetching, content extraction, and simple data storage, suitable for small website data collection scenarios.

### Tech Stack
- Network Requests: requests (HTTP client)
- Content Parsing: beautifulsoup4 + lxml (HTML/XML parsing)
- Dependency Management: pip (managed via requirements.txt)

### Architecture Modules
1. **Network Request Module** (`main.py`): Wraps HTTP request logic with timeout control (`REQUEST_TIMEOUT`), random User-Agent (`USER_AGENTS`), and concurrent crawling (`ThreadPoolExecutor`). Handles network exceptions and returns structured results.
2. **Link Extraction Module** (`main.py`): Uses BeautifulSoup to parse HTML, extracts all hyperlinks and converts them to absolute paths. Integrates URL deduplication mechanism (`visited_urls` set) to avoid repeated crawling.
3. **Configuration Module** (`config.py`): Centralizes management of base URL, User-Agent list, concurrent threads (`MAX_WORKERS`), crawl delay (`CRAWL_DELAY`), etc. Supports quick adjustment of anti-crawling strategies.
4. **Data Extraction Module** (`main.py`): Extracts core content like page titles and body based on configured selectors (`CONTENT_SELECTORS`), returns structured data (dictionary format).
5. **Data Storage Module** (`storage.py`): Provides CSV and JSON storage methods, auto-generates filenames with timestamps, supports persisting crawl results to local files.
- 本地测试：通过`python main.py`直接运行，观察控制台输出和生成的CSV/JSON文件
- 服务器部署：
   - 使用Docker打包（创建`Dockerfile`，基于Python镜像安装依赖）
   - 配置`systemd`服务实现开机自启动（示例：`/etc/systemd/system/crawler.service`）
   - 定时任务：通过`crontab`设置每日/每周执行（如`0 3 * * * /usr/bin/python3 /path/to/main.py`）
- 生产优化：
   - 集成日志系统（如`logging`模块）记录详细爬取日志
   - 使用监控工具（如Prometheus）监控爬取速率、失败率等指标