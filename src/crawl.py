from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Try h1, fallback to h2
    h_tag = soup.find("h1")
    if not h_tag:
        h_tag = soup.find("h2")
    
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Priority search: <main> then <p>
    main_tag = soup.find("main")
    if main_tag:
        p_tag = main_tag.find("p")
    else:
        p_tag = soup.find("p")
        
    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""

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

def crawl_page(current_url: str, pages: dict[str, int]) -> dict[str, int]:
    normalized_url = normalize_url(current_url)
    if normalized_url in pages:
        return pages
    pages[normalized_url] = 1
    print(f"crawling {current_url}")

    return pages

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            images.append(urljoin(base_url, src))
    return images

def main():
    pass

if __name__ == "__main__":
    main()