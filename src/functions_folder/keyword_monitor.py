import requests
import json
import os
import argparse
import re
from datetime import datetime
from dotenv import load_dotenv
import logging
import os


from logger_config import get_custom_logger

from APP_loggerSetup import app_loggerSetup
from LOCAL_loggerSetup import local_loggerSetup

logger = app_loggerSetup()


def create_timestamped_folder(base_name="static/KM result"):
    now = datetime.now()
    formatted_time = now.strftime("%d-%b-%Y %I-%M %p").lstrip("0")
    folder_name = f"{base_name} {formatted_time}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def perform_google_search(keyword, api_key, cx_id, max_results=10):
    logger.info("\n" \
    "*********************************************\n"\
    "🔧 Logger initialized for keyword_monitor.py\n"\
    "*********************************************\n"
    )

    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx_id,
        "q": keyword,
        "num": max_results
    }
    try:
        response = requests.get(base_url, params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def loose_match(keyword, text):
    keyword_tokens = re.findall(r"\w+", keyword.lower())
    text = text.lower()
    return all(token in text for token in keyword_tokens)

def find_keyword_rank(keyword, search_results, use_tokenization=True):
    items = search_results.get("items", [])
    logger.info(f"\n🔍 Top 10 results for: {keyword}")
    for idx, item in enumerate(items):
        title = item.get("title", "")
        url = item.get("link", "")
        logger.info(f"{idx+1}. {title} → {url}")

    for idx, item in enumerate(items):
        title = item.get("title", "")
        url = item.get("link", "")
        snippet = item.get("snippet", "")

        if use_tokenization:
            match_found = (
                loose_match(keyword, title) or
                loose_match(keyword, url) or
                loose_match(keyword, snippet)
            )
        else:
            keyword_lower = keyword.lower()
            match_found = (
                keyword_lower in title.lower() or
                keyword_lower in url.lower() or
                keyword_lower in snippet.lower()
            )

        if match_found:
            return idx + 1, item
    return None, None

def save_json(data, folder_path, filename):
    full_path = os.path.join(folder_path, filename)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")

if __name__ == "__main__":
    load_dotenv()
    
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger=logging.getLogger("keyword_monitor")
    logger=local_loggerSetup(logger,script_name)
    
    parser = argparse.ArgumentParser(description="Keyword relevance scanner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--tokenize", dest="tokenize", action="store_true", help="Enable tokenization")
    group.add_argument("--no-tokenize", dest="tokenize", action="store_false", help="Disable tokenization")
    parser.set_defaults(tokenize=True)

    parser.add_argument("--keywords", type=str, nargs='*', default=None)
    args = parser.parse_args()

    test_keywords = args.keywords if args.keywords else ["SEO masterz"]
    test_api_key = os.getenv("GOOGLE_API_KEY", "your_api_key_here")
    test_cx_id = os.getenv("GOOGLE_CX_ID", "your_cx_id_here")

    folder = create_timestamped_folder()

    for keyword in test_keywords:
        search_data = perform_google_search(keyword, test_api_key, test_cx_id)
        rank, matched_result = find_keyword_rank(keyword, search_data, use_tokenization=args.tokenize)

        result_summary = {
            "keyword": keyword,
            "rank": rank if rank else "Not found",
            "matched_result": matched_result if matched_result else {},
            "timestamp": datetime.now().strftime("%d-%b-%Y %I-%M %p").lstrip("0")
        }

        safe_name = keyword.replace(" ", "_").lower()
        save_json(search_data, folder, f"{safe_name}_full_data.json")
        save_json(result_summary, folder, f"{safe_name}_result.json")

        logger.info(f"\n✅ Keyword: {keyword}")
        logger.info(f"   Rank: {result_summary['rank']}")
        logger.info(f"   Saved to folder: {folder}")