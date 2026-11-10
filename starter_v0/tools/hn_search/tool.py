from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err

HN_API = "https://hn.algolia.com/api/v1"
SORT_ENDPOINTS = {"relevance": "search", "date": "search_by_date"}
MAX_LIMIT = 20


def _clamp_limit(limit: Any) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return 5
    return max(1, min(value, MAX_LIMIT))


def _story_item(hit: dict[str, Any]) -> dict[str, Any]:
    story_id = hit.get("objectID") or hit.get("story_id")
    discussion = f"https://news.ycombinator.com/item?id={story_id}" if story_id else ""
    url = hit.get("url") or discussion
    return {
        "title": hit.get("title") or hit.get("story_title") or "",
        "url": url,
        "source": domain(url) if hit.get("url") else "news.ycombinator.com",
        "summary": f"{hit.get('points') or 0} points · {hit.get('num_comments') or 0} comments · by {hit.get('author') or 'unknown'}",
        "discussion_url": discussion,
        "points": hit.get("points") or 0,
        "num_comments": hit.get("num_comments") or 0,
        "created_at": hit.get("created_at"),
    }


def search_hacker_news(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories via the public Algolia HN API (no API key needed).

    Never raises: bad input or network/HTTP failures come back as an error dict.
    """
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query must be a non-empty string")
        sort_key = (sort or "relevance").strip().lower() if isinstance(sort, str) else "relevance"
        if sort_key not in SORT_ENDPOINTS:
            sort_key = "relevance"
        hits_per_page = _clamp_limit(limit)
        response = requests.get(
            f"{HN_API}/{SORT_ENDPOINTS[sort_key]}",
            params={"query": query, "tags": "story", "hitsPerPage": hits_per_page},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        hits = response.json().get("hits", []) or []
        items = [_story_item(hit) for hit in hits if hit.get("objectID") or hit.get("story_id")]
        return {"tool": "hn_search", "query": query, "sort": sort_key, "items": items[:hits_per_page]}
    except Exception as exc:
        return err("hn_search", exc)
