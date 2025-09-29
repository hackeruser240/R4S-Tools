# File: functions_folder/keyword_monitor.py

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

def create_timestamped_folder(base_name="static/KM result"):
    now = datetime.now()
    formatted_time = now.strftime("%d-%b-%Y %I-%M %p").lstrip("0")  # e.g. 27-Sep-2025 1-25 AM
    folder_name = f"{base_name} {formatted_time}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def perform_google_search(keyword, api_key, cx_id, max_results=10):
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

def find_keyword_rank(keyword, search_results):
    keyword_lower = keyword.lower()
    items = search_results.get("items", [])
    for idx, item in enumerate(items):
        title = item.get("title", "").lower()
        url = item.get("link", "").lower()
        snippet = item.get("snippet", "").lower()

        if keyword_lower in title or keyword_lower in url or keyword_lower in snippet:
            return idx + 1, item  # 1-based rank
    return None, None  # No match found

def save_json(data, folder_path, filename):
    full_path = os.path.join(folder_path, filename)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

# ✅ Local test block
if __name__ == "__main__":
    load_dotenv()
    test_keywords = ["seo tools", "SEO optimization"]
    test_api_key = os.getenv('GOOGLE_API_KEY')
    test_cx_id = os.getenv('GOOGLE_CX_ID')

    folder = create_timestamped_folder()

    for keyword in test_keywords:
        search_data = perform_google_search(keyword, test_api_key, test_cx_id)
        rank, matched_result = find_keyword_rank(keyword, search_data)

        result_summary = {
            "keyword": keyword,
            "rank": rank if rank else "Not found",
            "matched_result": matched_result if matched_result else "No match found",
            "timestamp": datetime.now().strftime("%d-%b-%Y %I-%M %p").lstrip("0")
        }

        safe_name = keyword.strip().replace(" ", "_").lower()
        save_json(search_data, folder, f"{safe_name}_full_data.json")
        save_json(result_summary, folder, f"{safe_name}_result.json")

        print(f"✅ Keyword: {keyword}")
        print(f"   Rank: {result_summary['rank']}")
        print(f"   Saved to folder: {folder}\n")