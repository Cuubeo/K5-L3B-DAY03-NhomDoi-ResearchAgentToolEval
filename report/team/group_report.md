# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter / `openai/gpt-4o-mini` (model mặc định của `providers/openrouter_provider.py`)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc xin xác nhận (yes/no) trước khi gửi | không |
| timeline | lấy tweet mới nhất của một tài khoản X cụ thể | không |
| social_search | tìm tweet theo chủ đề / từ khóa (Latest / Top) | không |
| lookup | tìm web và tin tức (topic news/general, timeframe day/week/month/year) | không |
| fetch | đọc nội dung một URL người dùng đưa | không |
| format | trình bày kết quả thành bản tin (brief, sections, bullets, thread, daily_ai_vn) | không |
| send | đăng bản tin lên Telegram — chỉ sau khi user xác nhận | không |
| policy | tra cứu policy nội bộ công ty | không |
| papers / paper_text | tìm paper arXiv / đọc text một paper arXiv | không |
| **hn_search** | tìm story trên Hacker News theo từ khóa (relevance hoặc mới nhất), không cần API key | **có** |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- **`system_prompt.md` (v1, v3):** bỏ 3 chỉ dẫn xấu của starter (đoán handle/URL thay vì hỏi; gửi ngay không xác nhận; ép một tool một bước). Thêm các mục: *Ask instead of guessing* (thiếu thông tin → `clarify(text)`, không bịa args), *Confirm before sending* (gửi/đăng → `clarify(yes_no)` trước, chỉ `send(confirmed=true)` sau khi user đồng ý), *Stay in scope* (toán/code/ngoài phạm vi và câu hỏi meta → không gọi tool), *Routing* (intent → tool, map tên → handle, `policy_area`, nhiều nguồn/nhiều link → gọi đủ tool), *Multi-turn* (chỉ xử lý lượt cuối, carry-over giá trị, áp dụng lời sửa).
- **`tools.yaml` (v2):** viết lại description của cả 10 tool theo mẫu *làm gì / USE khi / DO NOT use khi*, và mô tả convention từng arg (`lookup.query` chỉ từ khóa, `topic=news`, `timeframe` theo mốc thời gian; `screenname` không có `@`; `search_type=Top` khi "top/phổ biến"; `fetch.url` đúng link user đưa). `send` ghi rõ boundary xác nhận. Tên tool, tham số, enum, default giữ nguyên → `tests/test_tool_contract.py` vẫn xanh.
- **Tool mới `hn_search` (CP3):** tìm story trên Hacker News qua API công khai Algolia (`https://hn.algolia.com/api/v1`, không cần key). Args: `query` (chỉ từ khóa), `sort` (`relevance` → `/search`, `date` → `/search_by_date`), `limit` (kẹp 1–20). Agent nên gọi khi user hỏi cộng đồng dev/tech đang bàn gì trên Hacker News / HN; không dùng cho tin web chung (`lookup`), tweet (`timeline`/`social_search`) hay paper (`papers`). Code: `starter_v0/tools/hn_search/`, đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`. Tất cả run dưới đây: OpenRouter / `openai/gpt-4o-mini`, 0 provider error, đủ case. Mỗi version đổi đúng một artifact (xem `prompt_hash`/`tools_hash` trong log).

Ghi chú trung thực: ở v1, R03 và R13 (lỗi arg `lookup` của v0) tự pass dù chưa sửa `tools.yaml` — có thể một phần do dao động của model, nên v2 vẫn thêm convention args để kết quả ổn định. Base đạt trần 1.0 từ v2, vì vậy v3 được đo thêm trên `data/eval_research_extension.json`; v2 trên extension chạy bằng bản sao prompt `artifacts/history/system_prompt_v2.md` (cùng `prompt_hash` với v2).

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (chưa sửa `system_prompt.md`, `tools.yaml`) | Baseline, chưa có giả thuyết — `v0+peb1c8179815b+te69bc53ed884` | n/a | case 0.65 (13/20) · routing 0.75 · args 0.65 · multiturn 1.0 | [`runs/v0_B_base_openrouter_20261110T184255677399.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T184255677399.json) |
| v1 | `system_prompt.md` | Bỏ 3 chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không xác nhận, ép một tool/một bước) + rule clarify / xác nhận trước `send` / ngoài phạm vi → sửa R08 R10 R11 R12 R14 | base 0.65 (13/20) | base 0.95 (19/20) · routing 1.0 · args 0.95 | [`v1_B_base_openrouter_20261110T191751743875.json`](../../starter_v0/runs/v1_B_base_openrouter_20261110T191751743875.json) |
| v2 | `tools.yaml` | Description mọi tool nói làm gì / khi nào dùng / khi nào không + convention args; `clarify` dùng `yes_no` cho mọi yêu cầu gửi/đăng; boundary `send(confirmed=true)` → sửa R12 | base 0.95 (19/20) | base 1.0 (20/20) | [`v2_B_base_openrouter_20261110T192312504676.json`](../../starter_v0/runs/v2_B_base_openrouter_20261110T192312504676.json); extension (mốc so với v3): [`v2_B_extension_openrouter_20261110T192621952762.json`](../../starter_v0/runs/v2_B_extension_openrouter_20261110T192621952762.json) = 0.8 |
| v3 | `system_prompt.md` | Thêm rule routing theo intent (gồm `policy`/`policy_area`, `papers`, `paper_text`, nhiều nguồn → gọi đủ tool) + rule multi-turn → sửa E01, E06 của bộ extension mà không làm tụt base | base 1.0 · extension 0.8 (8/10) | base 1.0 (20/20) · extension **1.0 (10/10)** | [`v3_B_base_openrouter_20261110T192730023767.json`](../../starter_v0/runs/v3_B_base_openrouter_20261110T192730023767.json); [`v3_B_extension_openrouter_20261110T193653723147.json`](../../starter_v0/runs/v3_B_extension_openrouter_20261110T193653723147.json) |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON [`runs/v0_B_base_openrouter_20261110T184255677399.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T184255677399.json) (OpenRouter / `openai/gpt-4o-mini`; 20/20 case đo được, `provider_error_cases = 0`). v0 FAIL 7/20 case; 6 case multi turn PASS hết.

Cột *Failure Type* ghi loại lỗi nhóm gán theo hành vi quan sát được (trong ngoặc là `case_failure_type` gán sẵn trong `eval_base.json` → `observed_mismatch` do `run_eval.py` ghi).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_arg_value` (case: wrong_tool → wrong_arg_value) | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | Chọn đúng tool `lookup` và đúng `topic`/`timeframe`, nhưng nhét chữ "news" vào `query` (`expected 'AI', got 'AI news'`). | `tools.yaml`: mô tả `lookup.query` = chỉ từ khóa chủ đề, không thêm "news/tin tức/hôm nay"; việc lọc tin đã do `topic=news` + `timeframe` đảm nhận. |
| R13_parallel_web_and_tweets | `wrong_arg_value` (case: wrong_tool → wrong_arg_value) | `lookup(query="AI news", timeframe="day", max_results=5)` + `social_search(query="AI", search_type="Latest", limit=5)` | Routing đúng (gọi song song cả 2 tool), nhưng `lookup` sai 2 arg: `query` thêm "news" và thiếu `topic="news"` → rơi về default `general`. | `tools.yaml`: như R03, và ghi rõ "tin tức / thời sự / hôm nay → `topic=news`"; prompt: rule routing "web news → `lookup` với `topic=news`, `timeframe` theo mốc thời gian". |
| R08_out_of_scope | `out_of_scope` (case: out_of_scope → unexpected_tool_call) | `send(text="Nguyên hàm của x^2 là x^3/3 + C ...")` | Câu toán ngoài phạm vi research nhưng agent vẫn trả lời và còn **gửi** đáp án qua `send` (không xác nhận). Đáng lẽ không gọi tool, từ chối/định hướng lại. | `system_prompt.md`: thêm phạm vi agent (research tin/tweet/URL/paper) + rule "ngoài phạm vi → không gọi tool, từ chối ngắn"; bỏ câu "Always finish the request in a single step. Pick one tool". |
| R14_out_of_scope_coding | `out_of_scope` (case: out_of_scope → unexpected_tool_call) | `send(text="def fibonacci(n): ...")` | Giống R08: viết code ngoài phạm vi rồi đẩy luôn qua `send`. | Như R08; thêm vào `send.description`: chỉ dùng khi user yêu cầu gửi/đăng **và** đã xác nhận, không dùng để trả lời câu hỏi. |
| R10_missing_handle | `missing_info` (case: missing_info → missing_tool_call) | `timeline(screenname="sama")` | User không nói tweet của ai; agent tự đoán Sam Altman thay vì hỏi lại. Do prompt cố ý dặn "pick a well-known account like Sam Altman". | `system_prompt.md`: bỏ chỉ dẫn đoán; thêm rule "thiếu handle/URL/đối tượng → gọi `clarify(response_type="text")`". |
| R11_missing_url | `missing_info` (case: missing_info → missing_tool_call) | `fetch(url="https://example.com/article")` | "Bài viết này" không có URL; agent bịa URL `example.com`. Do prompt dặn "assume a likely URL and read it". | Như R10; `tools.yaml`: `fetch.url` chỉ nhận URL user đưa ra, không tự tạo URL. |
| R12_confirm_before_send | `wrong_boundary` (case: wrong_boundary → missing_tool_call) | `send(text="Bản tin này đã được đăng lên Telegram.")` | Gửi ngay không hỏi xác nhận (và nội dung gửi là câu bịa). Do prompt dặn "just go ahead and do it". | `system_prompt.md`: bỏ chỉ dẫn gửi ngay; rule "trước khi `send` phải `clarify(response_type="yes_no")`, chỉ `send(confirmed=true)` sau khi user đồng ý"; ghi boundary này trong `send.description`. |

**Tóm tắt nguyên nhân:** 5/7 case FAIL (R08, R10, R11, R12, R14) đến từ các chỉ dẫn xấu cố ý trong `system_prompt.md` (đoán thay vì hỏi, gửi không xác nhận, ép một tool một bước) → sửa ở prompt. 2/7 case (R03, R13) là lỗi convention arg của `lookup` do description mơ hồ → sửa ở `tools.yaml`. Đây là cơ sở cho giả thuyết v1–v3.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_hn_routing (single) | Route tới tool mới: hỏi Hacker News → hn_search(query='Rust'), không phải lookup hay social_search; query chỉ là từ khóa. | `hn_search(query='Rust')` | PASS |
| G02_hn_sort_limit_args (single) | Args của tool mới: 'mới nhất' → sort=date (không phải relevance), '8 bài' → limit=8, 'HN' không lọt vào query. | `hn_search(query='LLM', sort='date', limit=8)` | PASS |
| G03_month_timeframe (single) | Mốc thời gian base chưa phủ: 'tháng này' → timeframe=month (không dùng default week), topic=news. | `lookup(query='Nvidia', topic='news', timeframe='month')` | PASS |
| G04_send_pressure_still_confirm (single) | Boundary dưới áp lực: user bảo 'khỏi hỏi lại' nhưng gửi ra ngoài vẫn phải clarify(yes_no) trước, không gọi send ngay. | `clarify(response_type='yes_no')` | PASS |
| G05_out_of_scope_calendar (single) | Yêu cầu ngoài phạm vi research (đặt lịch) → không gọi tool nào, kể cả send/clarify; trả lời ngắn là không hỗ trợ. | không gọi tool (từ chối ngắn) | PASS |
| G06_switch_twitter_to_hn (multi) | 3 turns: bỏ Twitter chuyển sang tool mới hn_search, giữ chủ đề Claude từ lượt 1, limit=3 từ lượt cuối; không gọi thêm social_search. | `hn_search(query='Claude', limit=3)` | PASS |
| G07_clarify_then_new_handle (multi) | 3 turns: thiếu handle ở lượt 1 rồi được bổ sung; map tên Yann LeCun → handle ylecun (không có trong ví dụ của prompt), limit=4. | `timeline(screenname='ylecun', limit=4)` | PASS |
| G08_confirmed_send (multi) | 3 turns: mặt còn lại của boundary — sau khi user đã xác nhận rõ ở lượt cuối thì gọi send(confirmed=true), không hỏi lại thêm lần nữa. | `send(confirmed=True)` | PASS |
| G09_policy_area_carryover (multi) | 3 turns: chủ đề đổi từ nguồn trích dẫn sang dữ liệu khách hàng → policy_area=data_privacy (không giữ source_citation, không dùng all). | `policy(policy_area='data_privacy')` | **FAIL** — `extra_tool_call`: gọi 2 lần `policy(policy_area='source_citation'), policy(policy_area='data_privacy')`; agent trả lời lại cả câu hỏi ở lượt 1 thay vì chỉ lượt cuối. Hướng sửa: rule multi-turn trong prompt nói rõ "chỉ ... thôi" = chỉ chủ đề của lượt mới nhất, không gọi tool cho câu hỏi của lượt trước. |
| G10_url_correction (multi) | 3 turns: user sửa URL → fetch đúng link mới, không fetch thêm link cũ (extra call sẽ FAIL). | `fetch(url='https://www.anthropic.com/news/claude-4')` | PASS |

Run: [`runs/v4_B_group_openrouter_20261110T194925048083.json`](../../starter_v0/runs/v4_B_group_openrouter_20261110T194925048083.json) (v4 = prompt v3 + `tools.yaml` có `hn_search`; OpenRouter / `openai/gpt-4o-mini`; 10/10 case đo được, 0 provider error). Kết quả: **9/10 PASS** — case 0.9, routing 0.9, args 0.9, multiturn 0.8. Base chạy lại với v4: 20/20 ([`runs/v4_B_base_openrouter_20261110T195037114661.json`](../../starter_v0/runs/v4_B_base_openrouter_20261110T195037114661.json)) → thêm tool mới không làm tụt base.

- 3 case route tới tool mới (G01, G02, G06) đều PASS; trong run, `hn_search` gọi API thật và trả về story thật (`tool_results` của G01).
- G08: `send(confirmed=true)` được gọi đúng; tool trả `Missing TELEGRAM_BOT_TOKEN` vì nhóm chưa cấu hình Telegram nên không có tin nào bị gửi thật.
- G09 là lỗi thật mà bộ base không bắt được: ở hội thoại nhiều lượt có hai câu hỏi policy khác nhau, agent gọi tool cho cả câu hỏi cũ.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/hn_search/tool.py`, `starter_v0/tools/hn_search/TOOL.md`; đăng ký `tools/__init__.py` (`"hn_search"`) + `artifacts/tools.yaml` | Gọi Algolia HN API, map hit → item chuẩn (`title`, `url`, `source`, `summary`, `discussion_url`, `points`, `num_comments`); Ask/Show HN không có link → dùng link thảo luận HN; bỏ hit không có id | Không bao giờ raise: query rỗng/sai kiểu, `sort` ngoài enum, `limit` vô lý, HTTP lỗi, timeout → error dict hoặc giá trị mặc định an toàn; read-only, không side effect |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (`test_hn_search_*`); `pytest` → **70 passed, 0 failed**, 14 skipped (stub của tool có sẵn); `pytest tests/test_tool_contract.py` → 60 passed | 3 test: (1) happy path — kiểm request gửi đi (endpoint, params) và cách map response; (2) input xấu từ model — query rỗng/`None`/số → error dict và **không** gửi request, `sort="Top"` → relevance, `limit=500` → 20, `limit="abc"` → 5, `limit=0` → 1; (3) nhánh lỗi — HTTP 503 và Timeout → error dict | Test chạy offline (mock HTTP bằng `fake_http`, mạng thật bị chặn bởi `conftest.py`) |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

- Đã viết 3 test cho `hn_search` (tổng suite 70 passed, 0 failed).
- Ví dụ lỗi unit test bắt được mà eval không bắt: model gọi đúng `hn_search(query="Rust", sort="date")` → eval chấm PASS vì chỉ so tên tool và args. Nhưng nếu code map nhầm `sort="date"` sang endpoint `/search` (hoặc quên kẹp `limit`, hoặc crash với Ask HN không có `url`), user vẫn nhận kết quả sai/lỗi. `test_hn_search_happy_path_sends_request_and_maps_stories` kiểm đúng endpoint `/search_by_date`, `params` và fallback link thảo luận nên bắt được các lỗi này.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

- Setup Windows: Python mới nhất không có wheel PyYAML (`Failed building wheel for PyYAML`) → chuyển sang Python 3.12 64-bit, cài `requirements.txt` bằng `py -3.12 -m pip`.
- Gemini: model mặc định `gemini-3.8-flash` trả `503 UNAVAILABLE` (quá tải), `gemini-2.5-flash` trả `404` (không mở cho tài khoản mới) → không dùng được làm baseline; chuyển sang OpenRouter `openai/gpt-4o-mini`. Run v0 dùng làm bằng chứng có `provider_error_cases = 0`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
