from typing import Dict, Any, List
import requests
import os
import json

def get_base_url():
    # Allow overriding via env, default to internal docker service
    return os.getenv("TRENDRADAR_API_URL", "http://trend-radar-mcp:3333")

def get_news(ticker: str, start_date: str = None, end_date: str = None, *args, **kwargs) -> str:
    """
    Fetches news from TrendRadar API.
    Since TrendRadar is topic/keyword based, use ticker as query.
    """
    base_url = get_base_url()
    url = f"{base_url}/api/news/search"

    # Simple cleanup for TW stocks
    query = ticker.replace(".TW", "").replace(".TWO", "")

    # If ticker is numeric (Taiwan stock), try matching
    if query.isdigit():
        if query == "2330": query = "台積電"
        elif query == "2317": query = "鴻海"
        elif query == "2454": query = "聯發科"

    params = {
        "query": query,
        "limit": kwargs.get("limit", 20)
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Format the data to string as required by TradingAgents usually
        # Or return dict if supported. AlphaVantage returns dict or str.
        # Let's return formatted string for LLM consumption

        # data is likely a list of news items or a dict with "results"
        # Based on TrendRadar api.py, it calls search_news_unified which returns a list of results inside "results" key or directly list

        news_items = []
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        if isinstance(data, list):
            for item in data:
                title = item.get("title", "")
                platform = item.get("platform", "")
                date_str = item.get("timestamp", "")
                url = item.get("url", "")
                news_items.append(f"[{date_str}] {platform}: {title} ({url})")

        return "\n".join(news_items) if news_items else "No news found."

    except Exception as e:
        print(f"Error fetching news from TrendRadar: {e}")
        return f"Error fetching news: {str(e)}"

def get_global_news(*args, **kwargs) -> str:
    """
    Fetches latest hot news (global context).
    Accepts arbitrary args to match interface signature.
    """
    base_url = get_base_url()
    url = f"{base_url}/api/news/latest"

    try:
        response = requests.get(url, params={"limit": kwargs.get("limit", 20)}, timeout=10)
        response.raise_for_status()
        data = response.json()

        news_items = []
        # data is list of news or dict with "news"
        if isinstance(data, dict) and "news" in data:
             data = data["news"]

        if isinstance(data, list):
            for item in data:
                title = item.get("title", "")
                platform = item.get("platform", "")
                date_str = item.get("timestamp", "")
                news_items.append(f"[{date_str}] {platform}: {title}")

        return "\n".join(news_items) if news_items else "No global news found."

    except Exception as e:
        print(f"Error fetching global news from TrendRadar: {e}")
        return f"Error fetching global news: {str(e)}"
