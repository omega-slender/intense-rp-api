from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from seleniumbase import Driver
import re, time

def initialize_webdriver(custom_browser="chrome"):
    try:
        custom_browser = custom_browser.lower()
        
        if custom_browser == "chrome":
            driver = Driver(browser=custom_browser, uc=True)
        else:
            driver = Driver(browser=custom_browser)
        
        driver.open("https://chat.deepseek.com/sign_in")
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

def current_page(driver, url):
    try:
        current_url = driver.get_current_url()
        return current_url.startswith(url) if current_url else False
    except Exception:
        return False

def close_sidebar(driver):
    try:
        sidebar = driver.find_element(By.CLASS_NAME, "dc04ec1d")
        
        if "a02af2e6" not in sidebar.get_attribute("class"):
            button = driver.find_element(By.CLASS_NAME, "ds-icon-button")
            button.click()
    except Exception:
        pass

def new_chat(driver):
    try:
        button = driver.find_element(By.XPATH, "//div[contains(@class, '_217e214')]")
        button.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", button)
    except Exception:
        pass

def set_r1_state(driver, activate=False):
    try:
        button = driver.find_element(By.XPATH, "//div[@role='button' and contains(@class, '_3172d9f') and contains(., 'R1')]")
        style = button.get_attribute("style")
        is_active = "rgba(77, 107, 254, 0.40)" in style
        
        if is_active != activate:
            try:
                button.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", button)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error setting R1 button state: {e}")

def set_search_state(driver, activate=False):
    try:
        button = driver.find_element(By.XPATH, "//div[@role='button' and contains(@class, '_3172d9f') and not(contains(., 'R1'))]")
        style = button.get_attribute("style")
        is_active = "rgba(77, 107, 254, 0.40)" in style
        
        if is_active != activate:
            try:
                button.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", button)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error setting Search button state: {e}")

def reset_and_configure_chat(driver, r1, search):
    close_sidebar(driver)
    new_chat(driver)
    set_r1_state(driver, r1)
    set_search_state(driver, search)

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