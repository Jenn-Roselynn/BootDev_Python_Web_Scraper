import requests
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
    # Try h1, fallback to h2
    h_tag = soup.find("h1")
    if not h_tag:
        h_tag = soup.find("h2")
    
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""

def normalize_url(url: str) -> str:

    parsed = urlparse(url)
    # Combine netloc and path
    full_path = f"{parsed.netloc}{parsed.path}"
    # Strip trailing slashes and return lowercase
    return full_path.strip("/").lower()

def get_urls_from_html(html: str, base_url: str) -> list[str]:
    """
    Extracts all internal URLs from a string of HTML.
    Resolves relative links against the base_url.
    """
    soup = BeautifulSoup(html, "html.parser")
    internal_urls = []
    base_domain = urlparse(base_url).netloc

    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        if href:
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == base_domain:
                internal_urls.append(full_url)

    return internal_urls

def crawl_page(base_url: str, current_url: str = None, pages: dict[str, PageData] = None) -> dict[str, PageData]:
    # 1. Initialize the shared dictionary on the first call
    if pages is None:
        pages = {}
    if current_url is None:
        current_url = base_url

    # 2. Domain Guard: Only crawl within the same root domain
    if urlparse(current_url).netloc != urlparse(base_url).netloc:
        return pages

    # 3. Normalization & Visited check
    normalized = normalize_url(current_url)
    if normalized in pages:
        return pages

    # 4. Fetch and Process
    print(f"Crawling: {current_url}")
    try:
        html = get_html(current_url)
        # Store the extracted data
        pages[normalized] = extract_page_data(html, current_url)
        
        # 5. Recursive Step: Crawl each link found on the page
        for link in pages[normalized]["outgoing_links"]:
            pages = crawl_page(base_url, link, pages)
            
    except Exception as e:
        print(f"Error crawling {current_url}: {e}")

    return pages

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Priority search: <main> then <p>
    main_tag = soup.find("main")
    if main_tag:
        p_tag = main_tag.find("p")
    else:
        p_tag = soup.find("p")
        
    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            images.append(urljoin(base_url, src))
    return images

def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }
    
def get_html(url: str) -> str:
    try:
        # 1. Fetch the webpage
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=10)
        
        # 2. Raise error for HTTP 400/500 codes
        response.raise_for_status()
        
        # 3. Check if content-type is text/html
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            raise Exception(f"Expected text/html, got {content_type}")
            
        # 4. Return the HTML
        return response.text
        
    except requests.exceptions.RequestException as e:
        # Handles network issues, timeouts, etc.
        raise Exception(f"Network error: {e}")

def main():
    print("starting crawl...")
    pages = crawl_page("https://wagslane.dev", {})

if __name__ == "__main__":
    main()