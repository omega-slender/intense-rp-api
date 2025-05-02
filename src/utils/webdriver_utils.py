from seleniumbase import Driver
from typing import Optional

# =============================================================================================================================
# Initialize SeleniumBase and open browser
# =============================================================================================================================

def initialize_webdriver(custom_browser: str = "chrome", url: Optional[str] = None) -> Optional[Driver]:
    try:
        browser = custom_browser.lower()
        chromium_arg = None
        
        if browser in ("chrome", "edge"):
            chromium_arg = f"--app={url}" if url else None

        driver = Driver(
            browser=browser,
            chromium_arg=chromium_arg,
            uc=(browser == "chrome"),
        )
        
        if browser in ("firefox", "safari") and url:
            driver.get(url)

        return driver

    except Exception as e:
        print(f"Error initializing Selenium driver: {e}")
        return None

# =============================================================================================================================
# SeleniumBase Utils
# =============================================================================================================================

def is_browser_open(driver: Driver) -> bool:
    try:
        _ = driver.title
        return True
    except Exception:
        return False

def current_page(driver: Driver, url: str) -> bool:
    try:
        return driver.get_current_url().startswith(url)
    except Exception:
        return False