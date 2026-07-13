import pytest
from pages.registration_page import RegistrationPage
from utils.data_loader import load_accounts
from utils.api_client import OTPReceiver, CaptchaSolver
from utils.helpers import create_browser, close_browser

@pytest.fixture(scope="function")
def setup_browser():
    playwright, browser, context, page = create_browser(headless=False)
    yield page
    close_browser(playwright, browser)


def test_user_registration(setup_browser):
    """Kiểm thử luồng đăng ký nhiều user."""
    page = setup_browser
    accounts = load_accounts()
    otp_receiver = OTPReceiver()
    captcha_solver = CaptchaSolver()

    reg_page = RegistrationPage(page)

    for account in accounts:
        reg_page.register_user(account, captcha_solver, otp_receiver)