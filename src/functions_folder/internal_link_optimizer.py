# internal_link_optimizer.py

from bs4 import BeautifulSoup
import requests
import networkx as nx
import argparse

from functions_folder.APP_loggerSetup import app_loggerSetup
from functions_folder.LOCAL_loggerSetup import local_loggerSetup

logger = app_loggerSetup()

def normalize_page_id(url):
    path = requests.utils.urlparse(url).path.strip('/')
    return path.lower() if path else 'home'

def extract_internal_links(root_url, max_links=20):
    try:
        response = requests.get(root_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return [], f"Error fetching root URL: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')
    anchors = soup.find_all('a', href=True)
    internal_links = set()

    for a in anchors:
        href = a['href']
        if href.startswith('/'):
            full_url = root_url.rstrip('/') + href
        elif href.startswith(root_url):
            full_url = href
        else:
            continue

        slug = normalize_page_id(full_url)
        internal_links.add(slug)
        if len(internal_links) >= max_links:
            break

    return list(internal_links), None

def fetch_page_title(url, slug):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if slug == "home":
            return "Homepage"
        return title_tag.text.strip() if title_tag else "Untitled"
    except Exception:
        return "Homepage" if slug == "home" else "Title not available"

def suggest_internal_links(pages, root_url, existing_links=None, top_n=3):
    G = nx.Graph()
    G.add_nodes_from(pages)

    if existing_links:
        for src, dst in existing_links:
            if src in pages and dst in pages:
                G.add_edge(src, dst)

    centrality = nx.degree_centrality(G)
    clustering = nx.clustering(G)

    slug_to_title = {}
    for slug in pages:
        full_url = f"{root_url.rstrip('/')}/{slug}"
        slug_to_title[slug] = fetch_page_title(full_url, slug)

    suggestions_output = []
    for idx, page in enumerate(pages, start=1):
        suggestions = []
        for candidate in pages:
            if candidate != page and not G.has_edge(page, candidate):
                score = centrality.get(candidate, 0) + clustering.get(candidate, 0)
                suggestions.append((candidate, score))

        suggestions.sort(key=lambda x: x[1], reverse=True)
        top_suggestions = [s[0] for s in suggestions[:top_n]]

        source_title = slug_to_title.get(page, page)
        target_titles = [slug_to_title.get(slug, slug) for slug in top_suggestions]

        suggestions_output.append({
            "index": idx,
            "source": source_title,
            "targets": target_titles
        })

    return suggestions_output

if __name__ == "__main__":
    logger=local_loggerSetup(use_filename=__file__)
    parser = argparse.ArgumentParser(description="Internal Link Optimizer")
    parser.add_argument('--url', default="https://www.seomasterz.com/", help='Root URL to analyze')
    parser.add_argument('--max_links', type=int, default=8, help='Max internal links to extract')
    parser.add_argument('--top_n', type=int, default=3, help='Number of link suggestions per page')
    args = parser.parse_args()

    logger.info(f"🔍 Crawling homepage: {args.url}")
    pages, error = extract_internal_links(args.url, args.max_links)

    if error:
        logger.info(error)
    elif not pages:
        logger.info("No internal links found.")
    else:
        suggestions = suggest_internal_links(pages, args.url, top_n=args.top_n)
        logger.info("\n📌 Suggested Internal Linking Strategy:\n")
        for item in suggestions:
            logger.info(f"Suggestion {item['index']}:")
            logger.info(f"The page {item['source']} should add internal links to the following pages:")
            for target in item['targets']:
                logger.info(f"- {target}")