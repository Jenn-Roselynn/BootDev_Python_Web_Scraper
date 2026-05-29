# src/main.py
import sys
import asyncio
import json
from crawl import crawl_site_async # Changed from src.crawl to crawl

async def main_async():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)

    base_url = sys.argv[1]
    pages = await crawl_site_async(base_url)
    
    print(f"\nCrawl complete! Found {len(pages)} pages.")
    for data in pages.values():
        print(f"\nURL: {data['url']}")
        print(f"  Heading: {data['heading']}")
        print(f"  Outgoing Links found: {len(data['outgoing_links'])}")
        print(f"  Images found: {len(data['image_urls'])}")

    # Parked for future use:
    # with open("crawl_results.json", "w") as f: 
    #     json.dump(pages, f, indent=4) 
    # print("\nResults saved to crawl_results.json!")

if __name__ == "__main__":
    asyncio.run(main_async())