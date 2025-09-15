# internal_link_optimizer.py

import networkx as nx

def suggest_internal_links(pages, links, top_n=5):
    """
    Suggest internal links based on graph centrality and clustering.

    Args:
        pages (list): List of page names (nodes).
        links (list of tuples): Existing internal links (edges).
        top_n (int): Number of suggested links per page.

    Returns:
        dict: Suggested links {page: [recommended_pages]}
    """
    G = nx.Graph()
    G.add_nodes_from(pages)
    G.add_edges_from(links)

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

# 🔧 Local test block
if __name__ == "__main__":
    test_pages = ["home", "about", "contact", "blog", "faq"]
    test_links = [("home", "about"), ("home", "contact"), ("blog", "faq")]
    result = suggest_internal_links(test_pages, test_links, top_n=3)
    for page, recs in result.items():
        print(f"{page}: {', '.join(recs)}")