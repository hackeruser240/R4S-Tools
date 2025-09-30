# serp_scraper.py — goes inside functions_folder/

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random
import logging
import json

# Setup dual-handler logger
logger = logging.getLogger("SERPLogger")
logger.setLevel(logging.INFO)
# File handler (overwrite mode)
file_handler = logging.FileHandler("results.txt", mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)
# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# Formatter
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %I:%M %p'
)
console_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%b-%Y %I:%M %p'
)
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)
# Attach handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_company_input():
    user_input = input("Enter a company name or URL to match: ").strip()
    
    if not user_input or user_input.isdigit():
        logger.error("Invalid input. Please enter a valid company name or URL.")
        return None
    
    return user_input

def find_match(results, query):
    query_lower = query.lower()
    is_url = "." in query_lower and "/" in query_lower  # crude URL check

    matches = []

    for idx, entry in enumerate(results):
        title = entry.get("title", "").lower()
        url = entry.get("url", "").lower()

        if is_url:
            if query_lower in url:
                matches.append((idx, entry))
        else:
            if query_lower in title or query_lower in url:
                matches.append((idx, entry))

    if matches:
        logger.info(f"✅ Match found for '{query}':")
        for i, match in matches:
            logger.info(f"The company ranked: {i+1}!")
            logger.info(json.dumps(match, indent=2))
    else:
        logger.info(f"❌ No match found for '{query}'.")

def scrape_serp(keyword, num_results=10):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.bing.com/',
        'Accept': 'text/html'
    }
    query = keyword.replace(" ", "+")
    url = f"https://www.bing.com/search?q={query}&setlang=en&cc=us&count=20"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

    except Exception as e:
        logging.error(f"Request failed: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "lxml")
    results = []

    blocks = soup.select("li.b_algo, div.b_algo")
    logger.info(f"Found {len(blocks)} result blocks")
    
    for result in soup.select("li.b_algo, div.b_algo"):
        # Try to find the <h2> inside .b_algoheader
        h2_tag = result.select_one(".b_algoheader h2")
        link_tag = result.select_one(".b_algoheader a[href]")

        # Fallback: if .b_algoheader is missing, try generic <h2> and <a>
        if not h2_tag:
            h2_tag = result.select_one("h2")
        if not link_tag:
            link_tag = h2_tag.select_one("a") if h2_tag else result.select_one("a[href]")

        # Snippet logic: prefer .b_caption p, fallback to any <p>
        snippet_tag = result.select_one(".b_caption p")
        if not snippet_tag:
            snippet_tag = result.select_one("p")

        # Extract clean text
        title_text = h2_tag.get_text(strip=True) if h2_tag else None
        url = link_tag.get("href") if link_tag else None
        snippet_text = snippet_tag.get_text(strip=True) if snippet_tag else ""
        raw_bytes = snippet_text.encode('latin1', errors='ignore')
        snippet_text = raw_bytes.decode('utf-8', errors='ignore')


        # Filter out junk titles (e.g. domain names mashed with URLs)
        if title_text and url and not any(domain in title_text.lower() for domain in ["https://", ".com", ".net", ".org"]):
            results.append({
                "title": title_text,
                "url": url,
                "snippet": snippet_text
            })


    time.sleep(random.uniform(1.5, 3.0))  # Anti-bot delay
    return results


if __name__ == "__main__":
    keyword = input("Enter keyword to scrape: ").strip()
    company_query = get_company_input()

    logger.info(f"Keyword: {keyword}")
    logger.info(f"Company to search for: {company_query}")    
    
    results = scrape_serp(keyword)
    logger.info(f"Number of search results: {len(results)}")
    logger.info(json.dumps(results, indent=2))

    if company_query:
        find_match(results, company_query)