# Chạy lab COLOSSEUM

Thành viên: Đậu Văn Thạch — 2A202602592.
Chạy các lệnh dưới đây tại thư mục gốc repository.

## 1. Kiểm tra ngay trên máy hiện tại

Môi trường `.venv` Python 3.12 và pytest đã được tạo. Không cần API key.

```bash
cd "/home/thach2207/VIN AI K20/K4-Track2-Day26-Motminh"
make test
.venv/bin/python -m unittest agent.test_defense eval.test_detectors -v
.venv/bin/python -m eval.prosecute
```

Bộ test công khai trước khi cài corpus: 4608 passed, 7 skipped trên Python 3.12.
Sau khi cài corpus: 4608 passed, 7 skipped; cùng bộ test công khai.
20 regression test bổ sung đã qua. Prosecutor: 40 fixtures, precision 100%,
recall 82.4%, không false/rejected/unproven claims. Các con số trên là local.
Các test skip bao gồm kiểm tra cần corpus thật hoặc platform sandbox tương ứng.

## 2. Lấy corpus trước khi validate/spar/nộp

Corpus đã được cài và kiểm tra checksum tại `kit/world/df8c55dabb35/`.
Doctor/validate đã PASS, 0 lỗi và 5 WARN về lethality proxy.
Các trận spar seed 1 đã chạy thành công với cả ba bot.

Nếu cần cài lại trên máy khác, xin phụ trách artifact
`colosseum-world-df8c55dabb35.zip`, hoặc tải từ Releases khi tài khoản GitHub
có quyền truy cập repo. Không lấy truth.json của giám khảo.

Nếu có GitHub CLI và quyền truy cập release:

```bash
gh auth login
gh release download world-df8c55dabb35 --repo thach-s/K4-Track2-Day26-Motminh --pattern '*.zip'
gh release download world-df8c55dabb35 --repo thach-s/K4-Track2-Day26-Motminh --pattern '*.sha256'
sha256sum -c colosseum-world-df8c55dabb35.zip.sha256
unzip colosseum-world-df8c55dabb35.zip
```

Nếu phụ trách gửi ZIP trực tiếp, giải nén tại thư mục gốc với `unzip` như trên;
kiểm tra checksum nếu có file checksum. Cấu trúc cần có:

```text
kit/world/df8c55dabb35/manifest.json
kit/world/df8c55dabb35/pages.jsonl
```

Nếu release không tồn tại hoặc bị 404, cần phụ trách cấp đúng artifact/quyền;
không tạo fixture giả trong kit/world để vượt qua doctor.

## 3. Validate và luyện đấu

```bash
make doctor
make validate
make spar BOT=rookie AS=all
make spar BOT=operator AS=defender
make spar BOT=operator AS=prosecutor
make spar BOT=adversary AS=all
make ui
```

`make doctor`/`make validate`/`make spar` cần corpus. Đọc cả WARN của validator.
Spar dùng kế hoạch và câu trả lời scripted; điểm spar không xác nhận prompt
hay guardrails đã được chạy trên mọi câu trả lời. Không sửa kit/bots/fixtures.

## 4. Nộp bài

```bash
make test
.venv/bin/python -m unittest agent.test_defense eval.test_detectors -v
make validate
make submit TEAM=DauVanThach-2A202602592
```

Bundle: `submissions/DauVanThach-2A202602592.bundle`.
Tên đội ở trên là tên mặc định theo thông tin thành viên; thay TEAM nếu phụ
trách quy định tên khác. File teammates.md ở root vẫn được giữ; bản sao trong
agent/ cũng được bundle vì kit.submit chỉ đóng gói agent/deck/eval.

## 5. Thiết lập lại trên máy khác

Cần Python 3.12 và uv trên PATH. Theo Makefile gốc:

```bash
make install
```

Nếu có Python 3.12 nhưng chưa có uv, có thể tạo môi trường trực tiếp:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install pytest
```

Không dùng make qualify; target đó đã bị bỏ. agent/ và deck/ khóa ở đầu phiên;
eval/ có thể tiếp tục chỉnh theo luật. Không đưa trace đối thủ trong giải cho AI.
