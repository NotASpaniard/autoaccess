# AutoAccess - Bot tự động đăng ký tài khoản

Bot dùng Playwright (Python) tự động hóa luồng đăng ký tài khoản theo mô hình
Page Object Model.

## Luồng hoạt động

    Nhập link trang web
        -> Mở trang chủ
        -> Bấm nút "Đăng ký tài khoản" (mở form)
        -> Điền form (username, email, password, full_name)
        -> Giải captcha (gọi API Image-to-Text)
        -> Submit
        -> Nhận OTP (gọi API bên thứ ba) -> điền OTP -> Submit
        -> Kiểm tra thông báo thành công

## Cấu trúc thư mục

    main.py                     Điểm chạy chính (nhập link + lặp qua các account)
    config/config.py            Đọc cấu hình từ .env
    pages/base_page.py          Lớp cơ sở POM (navigate, fill, click...)
    pages/registration_page.py  Logic đăng ký + selector + giải captcha + OTP
    utils/data_loader.py        Đọc danh sách account từ data/accounts.json
    utils/api_client.py         Client gọi API giải Captcha và nhận OTP
    utils/helpers.py            Khởi tạo / đóng browser
    data/accounts.json          Danh sách tài khoản cần đăng ký
    tests/test_registration.py  Test pytest chạy luồng đăng ký
    mock_server/app.py          Website GIẢ để test (không dùng khi chạy thật)

## Cài đặt (chỉ làm 1 lần)

    py -m pip install -r requirements.txt
    py -m playwright install chromium

Ghi chú: nếu lệnh `python` không chạy trên máy, dùng `py` thay thế.

---

# HƯỚNG DẪN 1: Chạy trên WEB THẬT

## Bước 1 - Chỉnh dữ liệu tài khoản
Sửa `data/accounts.json`, mỗi tài khoản một object:

    [
      {
        "username": "taikhoan1",
        "email": "email1@gmail.com",
        "password": "MatKhau@123",
        "full_name": "Nguyen Van A"
      }
    ]

Bắt buộc: username, email, password. Tùy chọn: full_name.

## Bước 2 - Cấu hình API captcha / OTP trong file .env

    BASE_URL=https://trang-web-that.com
    OTP_API_URL=https://dich-vu-otp-that.com/receive
    CAPTCHA_API_URL=https://dich-vu-captcha-that.com/solve
    API_KEY=api_key_that_cua_ban

(Ví dụ dịch vụ thật: 2Captcha, Anti-Captcha cho captcha; dịch vụ SIM/Email OTP.)
Nếu cấu trúc response của dịch vụ khác, phải sửa lại `utils/api_client.py`
cho khớp (hiện đang đọc `data["otp"]` và `data["text"]`).

## Bước 3 - Chỉnh selector cho khớp web thật

Bot tự tìm ô nhập theo NHIỀU cách. Mỗi phần tử trong
`pages/registration_page.py` là một DANH SÁCH selector (candidates), xếp từ
cụ thể nhất -> tổng quát nhất. Bot thử lần lượt, cách nào khớp và hiện ra
trước thì dùng. Nhờ vậy khi web đổi giao diện (đổi class/id/thứ tự...), chỉ
cần còn ít nhất MỘT cách đúng là bot vẫn tìm ra ô.

Ví dụ ô email:

    EMAIL_INPUT = [
        "input[name='email']",         # ưu tiên 1: theo name
        "input[type='email']",         # ưu tiên 2: theo type
        "input[name*='email' i]",      # theo name gần đúng
        "input[id*='email' i]",        # theo id
        "input[autocomplete='email']",
        "input[placeholder*='mail' i]",# theo chữ gợi ý trong ô
    ]

Các phần tử cần khai báo:

    OPEN_REGISTER_BUTTON  Nút/link mở form đăng ký trên trang chủ
    USERNAME_INPUT        Ô nhập tên đăng nhập
    EMAIL_INPUT           Ô nhập email
    PASSWORD_INPUT        Ô nhập mật khẩu
    FULL_NAME_INPUT       Ô nhập họ tên
    CAPTCHA_IMAGE         Ảnh captcha
    CAPTCHA_INPUT         Ô nhập mã captcha
    SUBMIT_BUTTON         Nút submit
    OTP_INPUT             Ô nhập mã OTP
    SUCCESS_MESSAGE       Phần tử hiện khi đăng ký thành công

Cú pháp selector hỗ trợ:

    "input[name='email']"          CSS thường
    "input[type='email']"          theo type
    "input[id*='email' i]"         id chứa 'email' (i = không phân biệt hoa/thường)
    "[placeholder*='mail' i]"      theo placeholder
    "[aria-label*='OTP' i]"        theo nhãn trợ năng
    "button:has-text('Đăng ký')"   theo chữ hiển thị
    "text=Đăng ký"                 tìm theo đúng đoạn chữ

Khi web đổi giao diện mà bot báo "Khong tim thay phan tu...":
-> Mở F12 xem đặc điểm mới của ô đó (id, placeholder, type...) rồi THÊM MỘT
   dòng candidate mới vào đầu danh sách tương ứng. Không cần sửa logic.

Lưu ý:
- Đây là tìm theo quy tắc (heuristic), không phải AI hiểu ngữ nghĩa.
- Nếu trên trang có nhiều ô cùng loại (vd 2 ô password: mật khẩu + nhập lại),
  bot lấy ô ĐẦU TIÊN -> nên đặt selector cụ thể hơn cho trường hợp này.
- Bot tự bỏ qua bước captcha / OTP nếu trang không có các ô đó.

## Bước 4 - Chạy bot

    py main.py https://trang-web-that.com

Hoặc chạy rồi gõ link khi được hỏi:

    py main.py

Để xem browser chạy: đang để headless=False trong `utils/helpers.py` (mặc định).
Muốn chạy ẩn, đổi thành headless=True.

---

# HƯỚNG DẪN 2: Chạy trên WEB MOCK (để test / học)

Mock server là một website giả (có sẵn trang chủ + form + captcha + OTP)
để test bot mà không dùng web thật. `.env` đã trỏ sẵn về mock.

## Bước 1 - Bật mock server (cửa sổ 1)

    py mock_server/app.py

Server chạy tại http://127.0.0.1:5000

## Bước 2 - Chạy bot (cửa sổ 2)

    py main.py http://127.0.0.1:5000

Kết quả mong đợi trên màn hình:

    [INFO] Trang web muc tieu: http://127.0.0.1:5000
    [INFO] Da nap 2 tai khoan tu data/accounts.json
    Captcha solved: AH6DW
    Received OTP: 944780
    [OK] Dang ky thanh cong cho user: testuser123
    ...

Muốn tự xem giao diện: mở trình duyệt vào http://127.0.0.1:5000

## Chạy bằng pytest (tùy chọn)

    py -m pytest tests/ -v

## Khác nhau giữa MOCK và THẬT

    Thành phần            Mock (test)              Web thật
    Link web              127.0.0.1:5000           thay bằng link thật
    Selector              đã khớp sẵn mock         phải chỉnh theo web thật
    API captcha/OTP       mock trả sẵn             đổi sang dịch vụ thật + API key
    Luồng logic bot       giữ nguyên               giữ nguyên

---

## Lưu ý về bảo mật / pháp lý

- Hiện .env CHƯA có secret thật (chỉ là link localhost + key placeholder) nên
  đang được commit để mock chạy được ngay sau khi clone.
- Khi bạn thêm API KEY THẬT vào .env -> bỏ theo dõi ngay:
      git rm --cached .env
  rồi bỏ comment dòng `.env` trong .gitignore. Từ đó .env sẽ không lên git nữa.
- Tự động vượt captcha/OTP để tạo tài khoản hàng loạt trên web của người khác
  có thể vi phạm điều khoản dịch vụ. Chỉ dùng trên hệ thống bạn được phép
  (QA, kiểm thử hệ thống của chính bạn).
