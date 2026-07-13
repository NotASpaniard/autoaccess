import requests
import time
from config.config import Config

class OTPReceiver:
    """Client gọi API nhận OTP từ bên thứ ba."""

    def get_otp(self, email: str, max_attempts: int = 10, delay: int = 5) -> str:
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{Config.OTP_API_URL}?email={email}",
                    headers={"Authorization": f"Bearer {Config.API_KEY}"},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                if otp := data.get("otp"):
                    return otp
            except requests.RequestException as e:
                print(f"OTP API error (attempt {attempt+1}): {e}")
            time.sleep(delay)
        raise TimeoutError(f"Không nhận được OTP cho {email}")


class CaptchaSolver:
    """Client giải Captcha Image-to-Text."""

    def solve_captcha(self, image_path: str) -> str:
        try:
            with open(image_path, "rb") as img_file:
                files = {"image": img_file}
                data = {"api_key": Config.API_KEY}
                response = requests.post(Config.CAPTCHA_API_URL, files=files, data=data, timeout=15)
                response.raise_for_status()
                return response.json().get("text", "").strip()
        except Exception as e:
            print(f"Captcha solver error: {e}")
            return ""