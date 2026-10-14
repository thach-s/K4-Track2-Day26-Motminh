# Phòng thủ của Đậu Văn Thạch — 2A202602592

- `gateway.py`: nhận Command, trả Decision; không thực thi tool và không I/O.
- `policy.py`: kiểm tra tool/scope/learner/audience/token/card, lease, lệnh ghi,
  mask, replica và ngân sách. Rewrite slides.search sang slides.query; giới hạn
  query mặc định 2 hàng; giữ credit cho các vòng sau.
- `strategy.py`: helper ngân sách và routing. Drift không tự chứng minh replica
  nào mới hơn; `pick_replica(..., fresher=...)` dùng tín hiệu freshness cụ thể.
- `guardrails.py`: kiểm tra grounding, injection, redaction theo private source,
  phương trình Decimal và đối chiếu số với source texts.
- `prompt.md`: quy trình trả lời có căn cứ, đủ ask.require, không làm theo chỉ thị
  nhúng và nêu bất đồng giữa các nguồn.
- `telemetry.py`: ghi thông tin riêng cho đội; không phải chứng cứ trọng tài.
- `test_defense.py`: regression test bằng thư viện chuẩn.
- `TEAMMATES.md`: bản sao thông tin thành viên để được đóng vào bundle.

Gateway chỉ nhận MCP/A2A/DISCOVER; ANSWER đi qua đường riêng của harness.
Các guardrails trên câu trả lời không tự động chặn ANSWER. Prompt yêu cầu model
thực hiện cùng các kiểm tra; caller có thể gọi thư viện guardrails khi tự lắp câu
trả lời. Scanner chỉ là heuristic, không phải chứng minh một nguồn an toàn.

Callback `note_provenance`/`note_card` nhận kết quả trusted từ caller khi caller
hỗ trợ chúng. Một lệnh ghi không có provenance matching của vòng hiện tại sẽ bị
từ chối. Không tự tạo etag, token hay quyền truy cập để vượt qua kiểm tra.

Đọc [LAB_RUN.md](LAB_RUN.md) để thiết lập, chạy kiểm tra, spar và nộp bài.
