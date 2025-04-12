import time, re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException, TimeoutException

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

def initialize_webdriver(browser="chrome"):
    try:
        if browser == "Chrome":
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

        elif browser == "Firefox":
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--start-maximized")
            firefox_options.add_argument("--disable-blink-features=AutomationControlled")
            firefox_options.set_preference("dom.webdriver.enabled", False)

            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)

        elif browser == "Edge":
            edge_options = EdgeOptions()
            edge_options.add_argument("--start-maximized")
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            edge_options.use_chromium = True

            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)

        else:
            return None
        
        driver.get("https://chat.deepseek.com/sign_in")
        return driver

    except Exception as e:
        print(f"Error starting Selenium: {e}")
        return None

def is_browser_open(driver):
    try:
        driver.title
        return True
    except WebDriverException:
        return False

def login_to_site(driver, email, password):
    try:
        if not email or not password:
            return
        
        wait = WebDriverWait(driver, 15)
        
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Log in')]")))
        
        email_input.send_keys(email)
        password_input.send_keys(password)
        login_button.click()
    except Exception as e:
        print(f"Error logging in: {e}")
        pass

def current_page(driver, url):
    try:
        current_url = driver.current_url
        return current_url.startswith(url) if current_url else False
    except Exception:
        return False

def close_sidebar(driver):
    try:
        sidebar = driver.find_element(By.CLASS_NAME, "dc04ec1d")
        
        if "a02af2e6" not in sidebar.get_attribute("class"):
            button = driver.find_element(By.CLASS_NAME, "ds-icon-button")
            button.click()
    except:
        pass

def new_chat(driver):
    try:
        button = driver.find_element(By.XPATH, "//div[contains(@class, '_217e214')]")
        button.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", button)
    except Exception as e:
        print(f"Error creating new chat: {e}")
        pass

def set_r1_state(driver, activate=False):
    try:
        button = driver.find_element(By.XPATH, "//div[@role='button' and contains(@class, '_3172d9f')]")
        style = button.get_attribute("style")
        
        if "rgba(77, 107, 254, 0.40)" in style:
            is_active = True
        elif "transparent" in style:
            is_active = False
        else:
            is_active = False
        
        if is_active != activate:
            button.click()
    except Exception as e:
        print(f"Error activating R1: {e}")
        pass

def reset_and_configure_chat(driver, r1):
    close_sidebar(driver)
    new_chat(driver)
    set_r1_state(driver, r1)

def send_chat_message(driver, input_message):
    try:
        wait = WebDriverWait(driver, 15)

        def attempt_send():
            chat_input = wait.until(EC.presence_of_element_located((By.ID, "chat-input")))
            for _ in range(3):
                chat_input.clear()
                driver.execute_script("arguments[0].value = arguments[1];", chat_input, input_message)
                chat_input.send_keys(" ")
                chat_input.send_keys(Keys.BACKSPACE)

                if chat_input.get_attribute("value") == input_message:
                    chat_input.send_keys(Keys.RETURN)
                    return True

                time.sleep(1)
            return False

        if attempt_send():
            return True

        driver.refresh()
        
        if attempt_send():
            return True

        return False
    except Exception as e:
        print(f"Error when pasting prompt: {e}")
        return False

def active_generate_response(driver):
    try:
        wait = WebDriverWait(driver, 10)
        return wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='button' and contains(@class, '_7436101')]//div[contains(@class, '_480132b')]"))
        )
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def is_response_generating(driver):
    try:
        button = driver.find_element(By.XPATH, "//div[@role='button' and contains(@class, '_7436101')]")
        return button.get_attribute("aria-disabled") != "true"
    except Exception:
        return False

def get_last_message(driver):
    try:
        messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'ds-markdown ds-markdown--block')]")
        
        if messages:
            last_message = messages[-1].get_attribute("innerHTML")
            last_message = re.sub(r"</?em>", "*", last_message)
            last_message = re.sub(r"</?strong>", "", last_message)
            last_message = re.sub(r"<p>", "", last_message)
            last_message = re.sub(r"</p>(?!$)", "\n\n", last_message)
            last_message = re.sub(r"</p>$", "", last_message)
            last_message = re.sub(r'\*{2,}', '*', last_message)
            last_message = re.sub(r'"{2,}', '"', last_message)
            last_message = re.sub(r'\*{2,}', '“', last_message)
            last_message = re.sub(r'\*{2,}', '”', last_message)
            return last_message
        else:
            return None
    
    except Exception as e:
        print(f"Error getting last response: {e}")
        return None

def closing_symbol(text):
    if not text:
        return ""
    
    text = text.strip()
    analysis_text = text.split("\n")[-1].strip()
    
    if re.search(r'(?:"\.?$|\*\.?$|”\.?$)', text):
        return ""

    current_symbol = None
    equal_chars = {
        '"': ['"'],
        '*': ['*'],
        '“': ['“', '”'],
        '”': ['“', '”']
        }
    opposite_chars = {
        '"': ['*', '“'],
        '*': ['"', '“'],
        '“': ['"', '*'],
        '”': ['"', '*']
        }
    
    for char in analysis_text:
        if not current_symbol:
            if char in equal_chars:
                current_symbol = char
        else:
            if char in equal_chars[current_symbol]:
                current_symbol = None
            elif char in opposite_chars[current_symbol]:
                current_symbol = char
    
    return current_symbol if current_symbol else ""