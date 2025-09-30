from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests

def crawl_site(start_url, max_pages=50, delay=1.0):
    visited = set()
    index = {}

    def is_internal(link):
        return urlparse(link).netloc == urlparse(start_url).netloc

    def crawl(url):
        if len(visited) >= max_pages or url in visited:
            return
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                visited.add(url)
                index[url] = response.text
                soup = BeautifulSoup(response.text, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    next_url = urljoin(url, a_tag['href'])
                    if is_internal(next_url):
                        crawl(next_url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    crawl(start_url)
    return index