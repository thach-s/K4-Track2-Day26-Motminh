# Công tố từ trace L1

Entry point giữ nguyên: `prosecute(trace, answer, card) -> dict`.
Đồng bộ, không I/O/network; tối đa 4 claims, mỗi family tối đa một claim.
Mỗi claim gồm cls, evidence, expected, observed và argument tối đa 400 ký tự.

`detectors.py` bổ sung các detector dựa trên evidence hiện có cho 13 lớp;
`prosecute.py` giữ detector enforcement_failure, tổng cộng 14 lớp có heuristic.
Đã kiểm tra trên 40 fixture: precision 1.000, recall 0.824, false_claim_rate 0.000.
Đây là kết quả local; không bảo đảm điểm thi trên seed và trace mới.

Các lớp stale_read, hallucination và non_responsive chưa tự động cáo buộc:
trace không luôn có provenance/freshness hoặc đủ nghĩa để chứng minh chúng.
Không đọc truth.json, không dùng fixture labels trong đường prosecute.
Các lớp semantic khác cũng chỉ cáo buộc khi có dấu hiệu cụ thể; trọng tài live
vẫn quyết định kết quả adjudication.

Evidence gồm event của lệnh/kết quả/câu trả lời thực tế, có thể bổ sung
answer.span:N và anchor refs. Các near-miss được đối chiếu với đúng sự kiện,
không lấy một event có hình dạng tương tự ở đầu trace làm bằng chứng.

```bash
.venv/bin/python -m eval.prosecute
.venv/bin/python -m unittest eval.test_detectors -v
```

Chỉ sử dụng AI để phát triển trước giải; theo RULES.md, không đưa trace đối thủ
trong tournament cho AI assistant làm công tố.
