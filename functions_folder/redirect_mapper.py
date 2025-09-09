# File: functions_folder/redirect_mapper.py

import httpx
import networkx as nx

def redirect_mapper(start_url, max_redirects=10, timeout=10):
    graph = nx.DiGraph()
    visited = set()
    current_url = start_url
    chain = []

    try:
        for _ in range(max_redirects):
            if current_url in visited:
                graph.add_edge(current_url, current_url)
                return {
                    "redirect_chain": chain,
                    "loop_detected": True,
                    "final_url": current_url,
                    "graph": graph
                }

            visited.add(current_url)
            response = httpx.get(current_url, follow_redirects=False, timeout=timeout)

            if response.status_code in (301, 302, 303, 307, 308):
                next_url = response.headers.get("location")
                if not next_url:
                    break
                next_url = httpx.URL(next_url, base=current_url).resolve().human_repr()
                graph.add_edge(current_url, next_url)
                chain.append((current_url, response.status_code))
                current_url = next_url
            else:
                chain.append((current_url, response.status_code))
                break

        return {
            "redirect_chain": chain,
            "loop_detected": False,
            "final_url": current_url,
            "graph": graph
        }

    except Exception as e:
        return {"error": f"Redirect mapping failed: {e}"}
    

if __name__ == "__main__":
    result=redirect_mapper("https://www.seomasterz.com/")
    print(result)