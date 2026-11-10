"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest
import requests

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

hn_search = TOOL_FUNCTIONS["hn_search"]

HN_HITS = {"hits": [
    {"objectID": "101", "title": "Rust 2.0 released", "url": "https://blog.rust-lang.org/2026/rust-2",
     "points": 512, "num_comments": 230, "author": "steve", "created_at": "2026-11-10T08:00:00Z"},
    {"objectID": "102", "title": "Ask HN: Is Rust worth learning?", "url": None,
     "points": 40, "num_comments": 88, "author": "newbie", "created_at": "2026-11-09T10:00:00Z"},
    {"title": "hit without id is skipped", "url": "https://example.com/x"},
]}


def test_hn_search_happy_path_sends_request_and_maps_stories(fake_http) -> None:
    calls = fake_http(FakeResponse(HN_HITS))

    result = hn_search(query="Rust", sort="date", limit=3)

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"] == {"query": "Rust", "tags": "story", "hitsPerPage": 3}
    assert "error" not in result
    assert [item["title"] for item in result["items"]] == ["Rust 2.0 released", "Ask HN: Is Rust worth learning?"]
    first, ask_hn = result["items"]
    assert first["url"] == "https://blog.rust-lang.org/2026/rust-2"
    assert first["source"] == "blog.rust-lang.org"
    assert first["discussion_url"] == "https://news.ycombinator.com/item?id=101"
    assert first["summary"] == "512 points · 230 comments · by steve"
    # Ask HN has no external link -> falls back to the HN discussion page
    assert ask_hn["url"] == "https://news.ycombinator.com/item?id=102"
    assert ask_hn["source"] == "news.ycombinator.com"


def test_hn_search_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse(HN_HITS))

    # Empty / whitespace / wrong-type query -> error dict, and no HTTP request is made.
    for bad_query in ["", "   ", None, 123]:
        result = hn_search(query=bad_query)
        assert result["tool"] == "hn_search"
        assert result["error"] == "ValueError"
    assert calls == []

    # Out-of-enum sort falls back to relevance; out-of-range / non-numeric limit is clamped.
    hn_search(query="LLM", sort="Top", limit=500)
    hn_search(query="LLM", sort=None, limit="abc")
    hn_search(query="LLM", limit=0)
    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"]["hitsPerPage"] == 20
    assert calls[1]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[1]["params"]["hitsPerPage"] == 5
    assert calls[2]["params"]["hitsPerPage"] == 1


def test_hn_search_failure_returns_error_dict(fake_http) -> None:
    # HTTP error from the API -> error dict, does not raise.
    fake_http(FakeResponse({}, status_code=503))
    result = hn_search(query="Rust")
    assert result == {"tool": "hn_search", "error": "HTTPError", "message": "HTTP 503"}

    # Network failure (timeout) -> error dict, does not raise.
    fake_http(requests.Timeout("read timed out"))
    result = hn_search(query="Rust")
    assert result["tool"] == "hn_search"
    assert result["error"] == "Timeout"
    assert "timed out" in result["message"]
