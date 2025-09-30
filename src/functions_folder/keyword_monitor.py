# File: functions_folder/keyword_monitor.py
# This file uses Google Search API

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

def create_timestamped_folder(base_name="static/KM result"):
    now = datetime.now()
    formatted_time = now.strftime("%d-%b-%Y %I-%M %p")  # e.g. 27-Sep-2025 01-25 AM
    folder_name = f"{base_name} {formatted_time}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def sanitize_filename(keyword):
    return keyword.strip().replace(" ", "_")

def save_json(data, folder_path, filename):
    full_path = os.path.join(folder_path, filename)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def track_keyword_rankings(keywords, api_key, cx_id, max_results=10):
    base_url = "https://www.googleapis.com/customsearch/v1"
    output = {}
    full_data = {}

    for keyword in keywords:
        params = {
            "key": api_key,
            "cx": cx_id,
            "q": keyword,
            "num": max_results
        }

        try:
            response = requests.get(base_url, params=params)
            full_data[keyword] = response.json()
            top_result = full_data[keyword].get("items", [{}])[0]

            output[keyword] = {
                "rank": 1,
                "title": top_result.get("title", "N/A"),
                "url": top_result.get("link", "N/A"),
                "snippet": top_result.get("snippet", "N/A"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            output[keyword] = {"error": str(e)}
            full_data[keyword] = {"error": str(e)}

    return output, full_data

# ✅ Local test block
if __name__ == "__main__":
    test_keywords = ["website boosting"]

    load_dotenv()
    test_api_key = os.getenv("GOOGLE_API_KEY")
    test_cx_id = os.getenv("GOOGLE_CX_ID")

    output, full_data = track_keyword_rankings(test_keywords, test_api_key, test_cx_id)
    folder = create_timestamped_folder()

    for keyword in test_keywords:
        safe_name = sanitize_filename(keyword)
        save_json(full_data.get(keyword, {}), folder, f"{safe_name}_full_data.json")
        save_json(output.get(keyword, {}), folder, f"{safe_name}_result.json")

    print(f"✅ Results saved in folder: {folder}")