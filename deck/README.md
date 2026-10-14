# Bộ bài Đậu Văn Thạch — 2A202602592

14 lá: 10 attack và 4 blank. Cân bằng 4 MCP, 2 gateway, 4 A2A;
9 lớp tấn công khác nhau. Lineup chơi 10 attack, không lặp.

Điều chỉnh từ starter:
- atk_04 hỏi source_of trên Claim đã có trong starter blank, để lookup research
  trực tiếp gặp bề mặt poison_row thay vì một câu define_term đi qua glossary.
- atk_07 và atk_10 kích hoạt từ call_index >= 1, sớm hơn starter.
- Lineup mới: schema_bomb → poisoned_result → forged_card → drift → shadow →
  faithless_peer → identity/aud → replica_flip → header_spoof → identity/act.
  Các đòn về ghi và identity/act được đặt ở cuối khi round_scale cao hơn.
- Giữ các anchor/path_id từ starter; không tự đặt anchor khi chưa có corpus.

defense_event phản ánh cơ chế phòng thủ: denial cho identity/shadow/header,
registry.pinned cho drift, guardrail.refused cho poison, gateway.budget_held
cho schema_bomb và a2a.crosschecked cho faithless_peer. Không đổi mọi cơ chế
thành denial chỉ để đạt proxy của validator.

Đã validate trên corpus df8c55dabb35: PASS, 0 failing checks, 5 warnings.
Đã chạy spar seed 1 với rookie, operator và adversary.
WARN về lethality proxy cần đọc theo giới hạn của validate_deck.py; green trên
fixture không thay thế validation bằng corpus thật.
