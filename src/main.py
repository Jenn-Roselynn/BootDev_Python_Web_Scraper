import sys
import asyncio
from crawl import crawl_site_async
from json_report import write_json_report

async def main_async():
    if len(sys.argv) < 4:
        print("Usage: uv run main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)

    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])

    print(f"Starting crawl of: {base_url}")
    pages = await crawl_site_async(base_url, max_concurrency, max_pages)
    
    # Filter out None values
    completed_pages = {k: v for k, v in pages.items() if v is not None}
    
    # Write the JSON report
    write_json_report(completed_pages)
    
    print(f"Crawl complete! Found {len(completed_pages)} pages.")

if __name__ == "__main__":
    asyncio.run(main_async())