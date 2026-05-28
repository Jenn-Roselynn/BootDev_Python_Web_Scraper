import unittest
from src.crawl import (
    normalize_url, 
    get_heading_from_html, 
    get_first_paragraph_from_html,
    get_urls_from_html, 
    get_images_from_html
)

class TestCrawl(unittest.TestCase):
    # 1. Normalize URL Tests
    def test_normalize_url_strips_protocol(self):
        self.assertEqual(normalize_url("https://blog.boot.dev/path"), "blog.boot.dev/path")
        self.assertEqual(normalize_url("http://blog.boot.dev/path"), "blog.boot.dev/path")

    def test_normalize_url_strips_trailing_slash(self):
        self.assertEqual(normalize_url("https://blog.boot.dev/path/"), "blog.boot.dev/path")
        self.assertEqual(normalize_url("https://blog.boot.dev/path//"), "blog.boot.dev/path")

    def test_normalize_url_lowercase(self):
        self.assertEqual(normalize_url("https://BLOG.boot.dev/path"), "blog.boot.dev/path")

    # 2. Heading Tests
    def test_get_heading_basic(self):
        self.assertEqual(get_heading_from_html('<html><body><h1>Title</h1></body></html>'), "Title")
        
    def test_get_heading_fallback_h2(self):
        self.assertEqual(get_heading_from_html('<html><body><h2>Fallback</h2></body></html>'), "Fallback")
        
    def test_get_heading_none(self):
        self.assertEqual(get_heading_from_html('<html><body><p>No header here</p></body></html>'), "")

    # 3. Paragraph Tests
    def test_get_first_paragraph_main_priority(self):
        html = '<html><body><p>Outer</p><main><p>Main</p></main></body></html>'
        self.assertEqual(get_first_paragraph_from_html(html), "Main")
        
    def test_get_first_paragraph_no_main(self):
        html = '<html><body><p>Just a paragraph</p></body></html>'
        self.assertEqual(get_first_paragraph_from_html(html), "Just a paragraph")
        
    def test_get_first_paragraph_none(self):
        self.assertEqual(get_first_paragraph_from_html('<html><body><div>No p here</div></body></html>'), "")

    # 4. Link & Image Tests
    def test_get_urls_from_html_absolute(self):
        url = "https://crawler-test.com"
        html = '<html><body><a href="https://crawler-test.com">Boot.dev</a></body></html>'
        self.assertEqual(get_urls_from_html(html, url), ["https://crawler-test.com"])

    def test_get_urls_from_html_relative(self):
        url = "https://crawler-test.com"
        html = '<html><body><a href="/about">About</a></body></html>'
        self.assertEqual(get_urls_from_html(html, url), ["https://crawler-test.com/about"])

    def test_get_urls_from_html_multiple(self):
        url = "https://crawler-test.com"
        html = '<html><body><a href="/a">A</a><a href="/b">B</a></body></html>'
        self.assertEqual(get_urls_from_html(html, url), ["https://crawler-test.com/a", "https://crawler-test.com/b"])

    def test_get_images_from_html_relative(self):
        url = "https://crawler-test.com"
        html = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        self.assertEqual(get_images_from_html(html, url), ["https://crawler-test.com/logo.png"])

    def test_get_images_from_html_missing_attr(self):
        url = "https://crawler-test.com"
        html = '<html><body><img></body></html>'
        self.assertEqual(get_images_from_html(html, url), [])

    def test_get_images_from_html_multiple(self):
        url = "https://crawler-test.com"
        html = '<html><body><img src="1.png"><img src="2.png"></body></html>'
        self.assertEqual(get_images_from_html(html, url), ["https://crawler-test.com/1.png", "https://crawler-test.com/2.png"])

if __name__ == '__main__':
    unittest.main()