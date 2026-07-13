import sys
from config.config import Config
from utils.helpers import create_browser, close_browser
from pages.registration_page import RegistrationPage
from utils.data_loader import load_accounts
from utils.api_client import OTPReceiver, CaptchaSolver


def get_website_url() -> str:
    """Lay link trang web can dang ky.

    Uu tien:  1) tham so dong lenh:  python main.py <link> [file_du_lieu]
              2) nhap tay khi duoc hoi
              3) mac dinh tu .env (Config.BASE_URL)
    """
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()

    try:
        entered = input(f"Nhap link trang web [{Config.BASE_URL}]: ").strip()
    except EOFError:
        entered = ""
    return entered or Config.BASE_URL


def get_data_file() -> str:
    """Lay duong dan file du lieu tai khoan (JSON/CSV/Excel/Word).

    Uu tien:  1) tham so dong lenh thu 2:  python main.py <link> <file>
              2) nhap tay khi duoc hoi
              3) mac dinh data/accounts.json (tra ve None)
    """
    if len(sys.argv) > 2 and sys.argv[2].strip():
        return sys.argv[2].strip()

    try:
        entered = input("Nhap duong dan file du lieu (Enter = data/accounts.json): ").strip()
    except EOFError:
        entered = ""
    # Bo dau nhay neu keo tha file vao terminal
    return entered.strip('"').strip("'") or None


def main():
    website = get_website_url()
    Config.BASE_URL = website          # dat lai link web cho toan bo bot
    print(f"[INFO] Trang web muc tieu: {website}")

    data_file = get_data_file()

    playwright, browser, context, page = create_browser()
    succeeded = []   # danh sach username thanh cong
    failed = []      # danh sach (username, ly_do) that bai
    try:
        accounts = load_accounts(data_file)
        total = len(accounts)
        nguon = data_file or "data/accounts.json"
        print(f"[INFO] Da nap {total} tai khoan tu {nguon}")

        reg_page = RegistrationPage(page)
        otp_receiver = OTPReceiver()
        captcha_solver = CaptchaSolver()

        for i, account in enumerate(accounts, start=1):
            username = account.get("username", f"#{i}")
            print(f"\n[{i}/{total}] Dang xu ly: {username}")
            try:
                reg_page.register_user(account, captcha_solver, otp_receiver)
                succeeded.append(username)
            except Exception as e:
                # Ghi lai loi va chay tiep tai khoan ke tiep (khong dung ca batch)
                reason = f"{type(e).__name__}: {str(e).splitlines()[0]}"
                failed.append((username, reason))
                print(f"[LOI] Tai khoan '{username}' that bai -> {reason}")
    finally:
        close_browser(playwright, browser)
        print_summary(succeeded, failed)


def print_summary(succeeded, failed):
    """In thong ke ket qua cuoi cung."""
    total = len(succeeded) + len(failed)
    print("\n" + "=" * 50)
    print("KET QUA DANG KY")
    print("=" * 50)
    print(f"Tong so tai khoan : {total}")
    print(f"Thanh cong        : {len(succeeded)}")
    print(f"That bai          : {len(failed)}")

    if succeeded:
        print("\nDanh sach thanh cong:")
        for u in succeeded:
            print(f"  [OK]  {u}")

    if failed:
        print("\nDanh sach that bai (username - ly do):")
        for username, reason in failed:
            print(f"  [LOI] {username} - {reason}")
    print("=" * 50)


if __name__ == "__main__":
    main()
