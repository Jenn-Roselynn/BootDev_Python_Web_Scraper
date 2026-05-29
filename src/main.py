import sys
import asyncio
from crawl import crawl_site_async

async def main_async():
    if len(sys.argv) < 4:
        print("Usage: uv run main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)

    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])

    pages = await crawl_site_async(base_url, max_concurrency, max_pages)
    
    # Filter out None values which act as placeholders during the crawl
    completed_pages = [data for data in pages.values() if data is not None]
    
    print(f"\nCrawl complete! Found {len(completed_pages)} pages.")
    for data in completed_pages:
        print(f"\nURL: {data['url']}")
        print(f"  Heading: {data['heading']}")
        print(f"  Outgoing Links found: {len(data['outgoing_links'])}")
        print(f"  Images found: {len(data['image_urls'])}")

if __name__ == "__main__":
    asyncio.run(main_async())