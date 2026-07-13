import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Cấu hình chung cho dự án."""
    BASE_URL = os.getenv("BASE_URL", "https://example.com")
    OTP_API_URL = os.getenv("OTP_API_URL", "https://thirdparty-otp.com/receive")
    CAPTCHA_API_URL = os.getenv("CAPTCHA_API_URL", "https://captcha-solver.com/solve")
    API_KEY = os.getenv("API_KEY", "your-api-key")
    TIMEOUT = 30000  # milliseconds