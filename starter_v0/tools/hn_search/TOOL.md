---
name: hn_search
track: core
kind: live_api
provider: Hacker News (Algolia HN Search API)
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hn_search

Tìm các story trên **Hacker News** theo từ khóa qua API công khai `https://hn.algolia.com/api/v1` (không cần API key).

- `sort="relevance"` → endpoint `/search` (liên quan nhất); `sort="date"` → `/search_by_date` (mới nhất).
- `limit` được kẹp trong khoảng 1–20; giá trị không phải số → mặc định 5.
- Mỗi item có `title`, `url` (link bài gốc; nếu là Ask/Show HN không có link thì dùng link thảo luận), `source`, `summary` (points · comments · author), `discussion_url`, `points`, `num_comments`, `created_at`.

**Khi agent nên gọi:** người dùng muốn biết cộng đồng dev/tech đang bàn gì trên Hacker News (vd. "Trên Hacker News đang nói gì về Rust?", "top bài HN về LLM").
**Không dùng:** tin tức web chung (→ `lookup`), tweet (→ `timeline` / `social_search`), paper (→ `papers`).

**Guardrail:** không bao giờ raise — query rỗng/sai kiểu, lỗi mạng, HTTP lỗi đều trả về error dict `{"tool", "error", "message"}`.
