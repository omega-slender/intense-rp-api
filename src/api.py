from flask import Flask, jsonify, request, Response
from gui import textbox_add, textbox_clear
from waitress import serve

import utils.deepseek as deepseek
import utils.selenium as selenium
import socket, time, threading
import utils.json as json

app = Flask(__name__)

driver = None
last_driver = 0
last_response = 0

textbox = None

config = {
    "browser": "Chrome",
    "model": "DeepSeek",
    "show_ip": False,
    "models": {
        "deepseek": {
            "email": "",
            "password": "",
            "auto_login": False,
            "text_file": False,
            "deepthink": False,
            "search": False
        }
    }
}

# =============================================================================================================================
# Server
# =============================================================================================================================

@app.route("/models", methods=["GET"])
def model():
    global driver
    if not driver:
        return jsonify({}), 503
    
    show_message("\n[color:purple]API CONNECTION:")
    
    try:
        show_message("[color:white]- [color:green]Successful connection.")
        return json.get_model()
    except Exception as e:
        show_message("[color:white]- [color:green]Error connecting.")
        print(f"Error connecting to API: {e}")
        return jsonify({}), 500

@app.route("/chat/completions", methods=["POST"])
def bot_response():
    try:
        global driver, config

        data = request.get_json()
        if not data:
            print("Error: Empty data was received.")
            return jsonify({}), 503
        
        character_info = json.process_character(data)
        streaming = json.get_streaming(data)
        deepseek_deepthink = json.get_deepseek_deepthink(data)
        deepseek_search = json.get_deepseek_search(data)
        
        if not character_info:
            print("Error: Data could not be processed.")
            return jsonify({}), 503
        
        if not driver:
            print("Error: Selenium is not active.")
            return jsonify({}), 503
        
        if config["models"]["deepseek"]["deepthink"]:
            deepseek_deepthink = True

        if config["models"]["deepseek"]["search"]:
            deepseek_search = True
        
        return deepseek_response(
            character_info,
            streaming,
            deepseek_deepthink,
            deepseek_search,
            config["models"]["deepseek"]["text_file"]
        )
    except Exception as e:
        print(f"Error receiving data: {e}")
        return jsonify({}), 500

def deepseek_response(character_info, streaming, deepseek_deepthink, deepseek_search, deepseek_text_file):
    try:
        global driver, last_response

        last_response += 1
        current_message = last_response
        show_message(f"\n[color:purple]GENERATING RESPONSE {current_message}:")
        show_message("[color:white]- [color:green]Character data has been received.")

        if not selenium.current_page(driver, "https://chat.deepseek.com") or selenium.current_page(driver, "https://chat.deepseek.com/sign_in"):
            show_message("[color:white]- [color:red]You must be logged into DeepSeek.")
            return json.create_response("You must be logged into DeepSeek.", streaming)
        
        def interrupted():
            return current_message != last_response and driver is not None
        
        if interrupted():
            return json.create_response("", streaming)

        deepseek.configure_chat(driver, deepseek_deepthink, deepseek_search)
        show_message("[color:white]- [color:cyan]Chat reset and configured.")

        if interrupted():
            return json.create_response("", streaming)

        if not deepseek.send_chat_message(driver, character_info, deepseek_text_file):
            show_message("[color:white]- [color:red]Could not paste prompt.")
            return json.create_response("Could not paste prompt.", streaming)

        show_message("[color:white]- [color:green]Prompt pasted and sent.")

        if interrupted():
            return json.create_response("", streaming)

        if not deepseek.active_generate_response(driver):
            show_message("[color:white]- [color:red]No response generated.")
            return json.create_response("No response generated.", streaming)
        
        if interrupted():
            return json.create_response("", streaming)
        
        show_message("[color:white]- [color:cyan]Awaiting response.")
        
        initial_text = ""
        last_text = ""
        start_time = time.time()
        
        if streaming:
            def streaming_response():
                nonlocal initial_text, last_text, start_time
                while deepseek.is_response_generating(driver):
                    if interrupted():
                        yield json.create_response_streaming("")
                        return

                    if (time.time() - start_time > 180):
                        if last_text:
                            break
                        else:
                            yield json.create_response_streaming("Error receiving response.")
                            return
                    
                    new_text = deepseek.get_last_message(driver)
                    if new_text and not initial_text:
                        initial_text = new_text

                    if new_text and new_text != last_text and new_text.startswith(initial_text):
                        diff = new_text[len(last_text):]
                        last_text = new_text
                        yield json.create_response_streaming(diff)

                    time.sleep(0.5)
                
                response = deepseek.closing_symbol(last_text) if last_text else "Error receiving response."
                yield json.create_response_streaming(response)
                show_message("[color:white]- [color:green]Completed.")
            
            return Response(streaming_response(), content_type="text/event-stream")
        else:
            def jsonify_response():
                nonlocal initial_text, last_text, start_time
                while deepseek.is_response_generating(driver):
                    if interrupted():
                        return json.create_response_jsonify("")
                    
                    if (time.time() - start_time > 180):
                        if last_text:
                            break
                        else:
                            return json.create_response_jsonify("Error receiving response.")
                    
                    new_text = deepseek.get_last_message(driver)
                    if new_text and not initial_text:
                        initial_text = new_text

                    if new_text and new_text.startswith(initial_text):
                        last_text = new_text

                    time.sleep(0.5)
                
                response = (last_text + deepseek.closing_symbol(last_text)) if last_text else "Error receiving response."
                show_message("[color:white]- [color:green]Completed.")
                return json.create_response_jsonify(response)
            
            return jsonify_response()
    except Exception as e:
        print(f"Error generating response: {e}")
        show_message("[color:white]- [color:red]Unknown error occurred.")
        return json.create_response("Error receiving response.", streaming)

# =============================================================================================================================
# Selenium actions
# =============================================================================================================================

def run_services():
    try:
        global driver, config, last_driver, last_response
        
        last_response = 0
        last_driver += 1

        close_selenium()
        driver = selenium.initialize_webdriver(config["browser"], "https://chat.deepseek.com/sign_in")
        
        if driver:
            threading.Thread(target=monitor_driver, daemon=True).start()
            
            if config["models"]["deepseek"]["auto_login"]:
                deepseek.login(driver, config["models"]["deepseek"]["email"], config["models"]["deepseek"]["password"])
            
            clear_messages()
            show_message("[color:red]API IS NOW ACTIVE!")
            show_message("[color:cyan]WELCOME TO INTENSE RP API V2.0")
            show_message("[color:yellow]URL 1: [color:white]http://127.0.0.1:5000/")
            
            if config["show_ip"]:
                local_ip = socket.gethostbyname(socket.gethostname())
                show_message(f"[color:yellow]URL 2: [color:white]http://{local_ip}:5000/")
            
            serve(app, host="0.0.0.0", port=5000)
        else:
            clear_messages()
            show_message("[color:red]Selenium failed to start.")
    except Exception as e:
        print(f"Error starting Selenium: {e}")

def monitor_driver():
    global driver, last_driver
    current_driver = last_driver

    print("Starting browser detection.")
    while True:
        if current_driver != last_driver:
            print("Detection stopped by new session.")
            break
        
        if driver and not selenium.is_browser_open(driver):
            clear_messages()
            show_message("[color:red]Browser connection lost!")
            driver = None
            break

        time.sleep(2)

def close_selenium():
    try:
        global driver

        if driver:
            driver.quit()
            driver = None
    except Exception:
        pass

# =============================================================================================================================
# Textbox actions
# =============================================================================================================================

def show_message(text):
    global textbox
    textbox_add(textbox, text)

def clear_messages():
    global textbox
    textbox_clear(textbox)

# =============================================================================================================================
# Assign variables and objects
# =============================================================================================================================

def assign_config(dict):
    global config
    config = dict

def assign_textbox(object):
    global textbox
    textbox = object
