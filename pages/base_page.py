from urllib.parse import urljoin
from playwright.sync_api import Page
from config.config import Config

class BasePage:
    """Base class cho tất cả Page Objects - chứa các phương thức chung."""

    def __init__(self, page: Page):
        self.page = page
        self.base_url = Config.BASE_URL

    def navigate(self, url: str = None):
        """Điều hướng đến URL và chờ load xong.

        - url=None  -> đi tới base_url
        - url tuyệt đối (http...) -> dùng nguyên
        - url dạng path ("/register") -> ghép với base_url
        """
        if not url:
            target_url = self.base_url
        elif url.startswith("http"):
            target_url = url
        else:
            target_url = urljoin(self.base_url.rstrip("/") + "/", url.lstrip("/"))
        self.page.goto(target_url, timeout=Config.TIMEOUT)
        self.page.wait_for_load_state("networkidle")

    def wait_for_element(self, selector: str, timeout: int = Config.TIMEOUT):
        return self.page.wait_for_selector(selector, timeout=timeout)

    def fill_field(self, selector: str, value: str):
        self.page.fill(selector, value)

    def click(self, selector: str):
        self.page.click(selector)

    def get_text(self, selector: str) -> str:
        return self.page.inner_text(selector)

    # ==================== TÌM PHẦN TỬ "THÔNG MINH" ====================
    # Mỗi phần tử được mô tả bằng NHIỀU cách tìm (candidates). Bot thử lần
    # lượt, cái nào xuất hiện/hiển thị trước thì dùng -> chịu được việc web
    # đổi giao diện, miễn là còn ít nhất một cách đúng.

    def smart_locator(self, candidates, timeout: int = None, require_visible: bool = True):
        """Trả về locator đầu tiên khớp một trong các 'candidates'.

        candidates: list các selector (CSS, text=..., placeholder=..., v.v.)
        Chờ tối đa `timeout` ms để ít nhất một candidate xuất hiện.
        """
        if isinstance(candidates, str):
            candidates = [candidates]
        timeout = timeout if timeout is not None else Config.TIMEOUT

        # Gộp tất cả candidate thành một locator "hoặc" (or_) rồi chờ hiện ra.
        combined = None
        for sel in candidates:
            loc = self.page.locator(sel)
            combined = loc if combined is None else combined.or_(loc)

        if combined is None:
            raise LookupError("Danh sach selector rong.")

        target = combined.first
        state = "visible" if require_visible else "attached"
        try:
            target.wait_for(state=state, timeout=timeout)
        except Exception:
            raise LookupError(
                f"Khong tim thay phan tu nao khop (thu {len(candidates)} cach): {candidates}"
            )
        return target

    def smart_fill(self, candidates, value: str, timeout: int = None):
        """Tìm ô nhập theo nhiều cách rồi điền giá trị."""
        self.smart_locator(candidates, timeout=timeout).fill(value)

    def smart_click(self, candidates, timeout: int = None):
        """Tìm nút/link theo nhiều cách rồi bấm."""
        self.smart_locator(candidates, timeout=timeout).click()

    def smart_exists(self, candidates, timeout: int = 3000) -> bool:
        """Kiểm tra nhanh xem có phần tử nào khớp không (không ném lỗi)."""
        try:
            self.smart_locator(candidates, timeout=timeout)
            return True
        except LookupError:
            return False