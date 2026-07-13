from playwright.sync_api import sync_playwright

def create_browser(headless=False):
    """Khởi tạo browser, context, page."""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    return playwright, browser, context, page


def close_browser(playwright, browser):
    browser.close()
    playwright.stop()