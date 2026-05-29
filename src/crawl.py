import asyncio
import aiohttp
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
from urllib.parse import urljoin, urlparse

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.netloc}{parsed.path}".strip("/").lower()

def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    internal_urls = []
    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        if href:
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == base_domain:
                internal_urls.append(full_url)
    return internal_urls

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    p_tag = (soup.find("main") or soup).find("p")
    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [urljoin(base_url, img.get("src")) for img in soup.find_all("img") if img.get("src")]

def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }

class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int, max_pages: int):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session: aiohttp.ClientSession = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url: str) -> bool:
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.page_data:
                return False
            
            self.page_data[normalized_url] = None
            if len([p for p in self.page_data.values() if p is not None]) >= self.max_pages:
                self.should_stop = True
                for task in self.all_tasks:
                    if task != asyncio.current_task():
                        task.cancel()
            return True

    async def get_html(self, url: str) -> str:
        async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=10) as resp:
            resp.raise_for_status()
            if "text/html" not in resp.headers.get("Content-Type", ""):
                raise Exception("Not HTML")
            return await resp.text()

    async def crawl_page(self, current_url: str):
        if self.should_stop or urlparse(current_url).netloc != self.base_domain:
            return

        normalized = normalize_url(current_url)
        if not await self.add_page_visit(normalized):
            return

        print(f"Crawling: {current_url}")
        try:
            async with self.semaphore:
                html = await self.get_html(current_url)
            
            data = extract_page_data(html, current_url)
            
            async with self.lock:
                self.page_data[normalized] = data
                if len([p for p in self.page_data.values() if p is not None]) >= self.max_pages:
                    print("Reached maximum number of pages to crawl.")
                    self.should_stop = True
                    for task in self.all_tasks:
                        if task != asyncio.current_task():
                            task.cancel()
            
            tasks = []
            for link in data["outgoing_links"]:
                t = asyncio.create_task(self.crawl_page(link))
                self.all_tasks.add(t)
                tasks.append(t)
            
            if tasks:
                await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
        finally:
            task = asyncio.current_task()
            if task in self.all_tasks:
                self.all_tasks.remove(task)

    async def crawl(self):
        root_task = asyncio.create_task(self.crawl_page(self.base_url))
        self.all_tasks.add(root_task)
        await root_task
        return self.page_data

async def crawl_site_async(base_url: str, max_concurrency: int, max_pages: int):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()

if __name__ == "__main__":

    import sys

    async def main_async():
        if len(sys.argv) < 4:
            print("Usage: uv run main.py <base_url> <max_concurrency> <max_pages>")
            sys.exit(1)

        base_url = sys.argv[1]
        max_concurrency = int(sys.argv[2])
        max_pages = int(sys.argv[3])

        pages = await crawl_site_async(base_url, max_concurrency, max_pages)
        
        completed_pages = [data for data in pages.values() if data is not None]
        print(f"\nCrawl complete! Found {len(completed_pages)} pages.")
        for data in completed_pages:
            print(f"\nURL: {data['url']}")
            print(f"  Heading: {data['heading']}")
            print(f"  Outgoing Links found: {len(data['outgoing_links'])}")
            print(f"  Images found: {len(data['image_urls'])}")

    asyncio.run(main_async())