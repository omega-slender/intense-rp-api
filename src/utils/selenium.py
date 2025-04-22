from seleniumbase import Driver

def initialize_webdriver(custom_browser="chrome", url=None):
    try:
        custom_browser = custom_browser.lower()
        chromium_arg = None
        
        if custom_browser in ["chrome", "edge"]:
            chromium_arg = f"--app={url}"

        driver = Driver(
            browser=custom_browser,
            chromium_arg=chromium_arg,
            uc=(custom_browser == "chrome")
        )

        if custom_browser in ["firefox", "safari"]:
            driver.get(url)

        return driver

    except Exception as e:
        print(f"Error starting Selenium: {e}")
        return None

def is_browser_open(driver):
    try:
        _ = driver.title
        return True
    except Exception:
        return False
    
def current_page(driver, url):
    try:
        return driver.get_current_url().startswith(url)
    except Exception:
        return False