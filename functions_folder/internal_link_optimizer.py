# internal_link_optimizer.py

from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

import argparse
import requests
import networkx as nx

def normalize_page_id(url: str) -> str:
    """Extract slug from URL or return slug as-is."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    return path.lower() or "home"

def extract_internal_links(root_url, max_links=10):
    """Fetch homepage and extract top-level internal links."""
    try:
        response = requests.get(root_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {root_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    base_domain = urlparse(root_url).netloc
    found = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(root_url, href)
        parsed = urlparse(full_url)

        if parsed.netloc == base_domain:
            slug = normalize_page_id(full_url)
            if slug and slug not in found:
                found.add(slug)
            if len(found) >= max_links:
                break

    return list(found)

def suggest_internal_links(pages, existing_links=None, top_n=3):
    """Suggest internal links based on graph centrality and clustering."""
    if existing_links is None:
        existing_links = []

    G = nx.Graph()
    G.add_nodes_from(pages)

    for src, dst in existing_links:
        G.add_edge(src, dst)

    centrality = nx.degree_centrality(G)
    clustering = nx.clustering(G)

    suggestions = {}
    for page in pages:
        neighbors = set(G.neighbors(page))
        candidates = set(pages) - neighbors - {page}
        ranked = sorted(
            candidates,
            key=lambda x: (centrality.get(x, 0), clustering.get(x, 0)),
            reverse=True
        )
        suggestions[page] = ranked[:top_n]

    return suggestions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Internal Link Optimizer")
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.seomasterz.com/",
        help="Root URL to analyze"
    )
    parser.add_argument(
        "--max_links",
        type=int,
        default=10,
        help="Maximum number of internal links to extract"
    )
    parser.add_argument(
        "--top_n",
        type=int,
        default=3,
        help="Number of suggestions per page"
    )

    args = parser.parse_args()
    print(f"🔍 Crawling homepage: {args.url}")
    slugs = extract_internal_links(args.url, max_links=args.max_links)

    if not slugs:
        print("No internal links found.")
    else:
        result = suggest_internal_links(slugs, top_n=args.top_n)
        print("\n📌 Suggested Internal Linking Strategy:\n")
        for i, (page, recs) in enumerate(result.items(), start=1):
            print(f"Suggestion {i}:\n")
            print(f"The page **{page}** should add internal links to the following pages:")
            for rec in recs:
                print(f"- {rec}")
            print()