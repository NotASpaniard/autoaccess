from pages.base_page import BasePage
from playwright.sync_api import expect


class RegistrationPage(BasePage):
    """Page Object cho trang Đăng ký.

    Mỗi phần tử được khai báo bằng MỘT DANH SÁCH các cách tìm (candidates),
    xếp từ cụ thể nhất -> tổng quát nhất. Bot thử lần lượt, cách nào khớp
    trước thì dùng. Nhờ vậy khi web đổi giao diện (đổi class/id/thứ tự...),
    chỉ cần còn ít nhất một cách đúng là bot vẫn tìm ra ô nhập.

    Cú pháp selector hỗ trợ:
      "input[name='email']"        CSS thường
      "input[type='email']"        theo type
      "input[id*='email' i]"       id chứa 'email' (i = không phân biệt hoa thường)
      "[placeholder*='mail' i]"    theo placeholder
      "[aria-label*='OTP' i]"      theo nhãn trợ năng
      "button:has-text('Đăng ký')" theo chữ hiển thị
    """

    # ==================== LOCATORS (nhiều cách tìm mỗi ô) ====================
    USERNAME_INPUT = [
        "input[name='username']",
        "input[name*='user' i]",
        "input[id*='user' i]",
        "input[autocomplete='username']",
        "input[placeholder*='đăng nhập' i]",
        "input[placeholder*='username' i]",
    ]
    EMAIL_INPUT = [
        "input[name='email']",
        "input[type='email']",
        "input[name*='email' i]",
        "input[id*='email' i]",
        "input[autocomplete='email']",
        "input[placeholder*='mail' i]",
    ]
    PASSWORD_INPUT = [
        "input[name='password']",
        "input[type='password']",
        "input[name*='pass' i]",
        "input[id*='pass' i]",
        "input[placeholder*='mật khẩu' i]",
    ]
    FULL_NAME_INPUT = [
        "input[name='full_name']",
        "input[name='fullname']",
        "input[name*='name' i]:not([name*='user' i])",
        "input[id*='fullname' i]",
        "input[placeholder*='họ tên' i]",
        "input[placeholder*='họ và tên' i]",
    ]
    CAPTCHA_IMAGE = [
        "img.captcha",
        "img[src*='captcha' i]",
        "img[alt*='captcha' i]",
        "img[id*='captcha' i]",
    ]
    CAPTCHA_INPUT = [
        "input[name='captcha']",
        "input[name*='captcha' i]",
        "input[id*='captcha' i]",
        "input[placeholder*='captcha' i]",
        "input[placeholder*='mã xác nhận' i]",
    ]
    SUBMIT_BUTTON = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Đăng ký')",
        "button:has-text('Đăng kí')",
        "button:has-text('Xác nhận')",
        "button:has-text('Submit')",
        "button:has-text('Gửi')",
    ]
    OTP_INPUT = [
        "input[name='otp']",
        "input[name*='otp' i]",
        "input[name*='code' i]",
        "input[autocomplete='one-time-code']",
        "input[id*='otp' i]",
        "input[placeholder*='OTP' i]",
        "input[placeholder*='mã xác thực' i]",
    ]
    SUCCESS_MESSAGE = [
        ".success-message",
        ".alert-success",
        "[class*='success' i]",
        "text=thành công",
    ]
    ERROR_MESSAGE = [
        ".error-message",
        ".alert-danger",
        "[class*='error' i]",
    ]
    # Nút/link "Đăng ký tài khoản" trên trang chủ
    OPEN_REGISTER_BUTTON = [
        "#open-register",
        "a[href*='register' i]",
        "a[href*='signup' i]",
        "a[href*='dang-ky' i]",
        "button:has-text('Đăng ký')",
        "a:has-text('Đăng ký')",
        "text=Đăng ký",
    ]

    def open_registration_form(self):
        """Từ trang chủ, bấm nút 'Đăng ký tài khoản' để mở form.

        Nếu trang hiện tại đã là form đăng ký sẵn (không có nút riêng),
        bỏ qua bước bấm nút.
        """
        # Nếu form đã hiện sẵn thì không cần bấm nút mở.
        if self.smart_exists(self.USERNAME_INPUT, timeout=1500):
            return
        self.smart_click(self.OPEN_REGISTER_BUTTON)
        self.page.wait_for_load_state("networkidle")
        self.smart_locator(self.USERNAME_INPUT)   # chờ form hiện ra

    def register_user(self, account_data: dict, captcha_solver, otp_receiver):
        """
        Thực hiện toàn bộ luồng đăng ký một user.
        Luồng: Mở trang chủ → Bấm 'Đăng ký' → Điền form → Captcha → Submit → OTP.
        """
        # 0. Vào trang chủ của website (link do người dùng nhập)
        self.navigate()
        # 0b. Bấm nút mở form đăng ký
        self.open_registration_form()

        # 1. Điền thông tin tài khoản
        self.smart_fill(self.USERNAME_INPUT, account_data["username"])
        self.smart_fill(self.EMAIL_INPUT, account_data["email"])
        self.smart_fill(self.PASSWORD_INPUT, account_data["password"])
        if account_data.get("full_name") and self.smart_exists(self.FULL_NAME_INPUT, timeout=1500):
            self.smart_fill(self.FULL_NAME_INPUT, account_data["full_name"])

        # 2. Giải Captcha (nếu trang có captcha)
        if self.smart_exists(self.CAPTCHA_IMAGE, timeout=1500):
            captcha_text = self.solve_captcha(captcha_solver)
            self.smart_fill(self.CAPTCHA_INPUT, captcha_text)

        # 3. Submit form đăng ký
        self.smart_click(self.SUBMIT_BUTTON)
        self.page.wait_for_load_state("networkidle")

        # 4. Xử lý OTP (nếu trang yêu cầu OTP)
        if self.smart_exists(self.OTP_INPUT, timeout=3000):
            otp_code = self.get_otp(otp_receiver, account_data["email"])
            if otp_code:
                self.smart_fill(self.OTP_INPUT, otp_code)
                self.smart_click(self.SUBMIT_BUTTON)

        # 5. Kiểm tra kết quả
        expect(self.smart_locator(self.SUCCESS_MESSAGE)).to_be_visible(timeout=10000)
        print(f"[OK] Dang ky thanh cong cho user: {account_data['username']}")

    def solve_captcha(self, captcha_solver) -> str:
        """Chụp ảnh captcha và gọi API Image-to-Text."""
        captcha_element = self.smart_locator(self.CAPTCHA_IMAGE)
        captcha_img_path = "temp_captcha.png"
        captcha_element.screenshot(path=captcha_img_path)

        captcha_text = captcha_solver.solve_captcha(captcha_img_path)
        print(f"Captcha solved: {captcha_text}")
        return captcha_text

    def get_otp(self, otp_receiver, email: str) -> str:
        """Gọi API bên thứ ba nhận OTP."""
        otp_code = otp_receiver.get_otp(email)
        print(f"Received OTP: {otp_code}")
        return otp_code
