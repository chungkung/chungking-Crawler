from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from main import WebCrawler
from storage import SQLiteStorage

app = FastAPI(title="Chungking 自动爬取API", description="基于Firecrawl设计的通用网页爬取API服务")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化存储
storage = SQLiteStorage()

# 任务管理（示例使用内存存储，生产环境建议用Redis）
_crawl_tasks = {}

class ScrapeRequest(BaseModel):
    url: str
    formats: List[str] = ["markdown", "html"]

class ScrapeResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

class CrawlRequest(BaseModel):
    url: str
    limit: int = 10
    max_depth: int = 2

class CrawlResponse(BaseModel):
    success: bool
    id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

class CrawlStatusResponse(BaseModel):
    status: str  # 'pending', 'scraping', 'completed'
    total: Optional[int] = None
    completed: Optional[int] = None
    data: Optional[List[Dict]] = None
    next: Optional[str] = None

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest):
    try:
        crawler = WebCrawler(base_url=request.url)
        url, html = await crawler.fetch_page(request.url)
        if not html:
            return {"success": False, "error": "页面获取失败"}
        content = crawler.extract_content(html)
        storage.save_data({**content, "url": url})
        return {
            "success": True,
            "data": {
                "markdown": f"# {content['title']}\n\n{content['content']}",
                "html": html,
                "metadata": {"title": content['title'], "url": url}
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/crawl", response_model=CrawlResponse)
async def crawl_url(request: CrawlRequest):
    try:
        task_id = f"crawl_{asyncio.get_event_loop().time()}"
        _crawl_tasks[task_id] = {"status": "pending", "total": 0, "completed": 0, "data": []}

        async def crawl_worker():
            crawler = WebCrawler(base_url=request.url)
            initial_response = await crawler.fetch_page(request.url)
            if initial_response[1]:
                links = crawler.extract_links(initial_response[1])[:request.limit]
                _crawl_tasks[task_id]["total"] = len(links)
                for idx, link in enumerate(links):
                    url, html = await crawler.fetch_page(link)
                    if html:
                        content = crawler.extract_content(html)
                        storage.save_data({**content, "url": url})
                        _crawl_tasks[task_id]["data"].append({
                            "markdown": f"# {content['title']}\n\n{content['content']}",
                            "html": html,
                            "metadata": {"title": content['title'], "url": url}
                        })
                    _crawl_tasks[task_id]["completed"] = idx + 1
                    _crawl_tasks[task_id]["status"] = "scraping"
                _crawl_tasks[task_id]["status"] = "completed"

        asyncio.create_task(crawl_worker())
        return {
            "success": True,
            "id": task_id,
            "url": f"/crawl/{task_id}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/crawl/{task_id}", response_model=CrawlStatusResponse)
async def check_crawl_status(task_id: str):
    task = _crawl_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {
        "status": task["status"],
        "total": task["total"],
        "completed": task["completed"],
        "data": task["data"][:10],  # 示例返回前10条
        "next": f"/crawl/{task_id}?skip=10" if len(task["data"]) > 10 else None
    }

@app.get("/")
async def root():
    return {"message": "Chungking 自动爬取API服务已运行。可用端点：/scrape (POST), /crawl (POST), /crawl/{task_id} (GET)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)