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
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (chưa sửa `system_prompt.md`, `tools.yaml`) | Baseline, chưa có giả thuyết — `v0+peb1c8179815b+te69bc53ed884` | n/a | case 0.65 (13/20) · routing 0.75 · args 0.65 · multiturn 1.0 | [`runs/v0_B_base_openrouter_20261110T184255677399.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T184255677399.json) |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

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
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

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
