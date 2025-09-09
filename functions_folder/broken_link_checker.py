# File: functions/broken_link_checker.py

from bs4 import BeautifulSoup

import requests
import aiohttp
import asyncio

async def check_link(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return url, response.status
    except Exception as e:
        return url, str(e)

async def validate_links(links):
    async with aiohttp.ClientSession() as session:
        tasks = [check_link(session, link) for link in links]
        return await asyncio.gather(*tasks)

def broken_link_checker(page_url):
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch page: {e}"}

    soup = BeautifulSoup(response.text, 'html.parser')
    raw_links = [a.get('href') for a in soup.find_all('a', href=True)]
    full_links = [requests.compat.urljoin(page_url, link) for link in raw_links]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(validate_links(full_links))

    broken = []
    valid = []
    for url, status in results:
        if isinstance(status, int) and status < 400:
            valid.append((url, status))
        else:
            broken.append((url, status))

    return {
        "page_url": page_url,
        "total_links": len(full_links),
        "valid_links": valid,
        "broken_links": broken
    }