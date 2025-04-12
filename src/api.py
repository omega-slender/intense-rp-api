import socket, time, threading, utils.selenium as selenium
from utils.json import process_character, get_model, create_response, create_response_jsonify, create_response_streaming
from flask import Flask, jsonify, request, Response
from gui import textbox_add, textbox_clear
from waitress import serve

app = Flask(__name__)
driver = None

config_show_ip = True
config_browser = None
config_password = None
config_email = None

last_response = 0
textbox = None

@app.route("/models", methods=["GET"])
def model():
    global driver
    if not driver:
        return jsonify({}), 503
    
    show_message("\n[color:purple]API CONNECTION:")
    
    try:
        show_message("[color:white]- [color:green]Successful connection.")
        return get_model()
    except Exception as e:
        show_message("[color:white]- [color:green]Error connecting.")
        print(f"Error connecting to API: {e}")
        return jsonify({}), 500

@app.route("/chat/completions", methods=["POST"])
def bot_response():
    try:
        data = request.get_json()
        if not data:
            print("Error: Empty data was received.")
            return jsonify({}), 503
        
        character_info, r1 = process_character(data)
        if not character_info:
            print("Error: Data could not be processed.")
            return jsonify({}), 503
        
        global driver
        if not driver:
            print("Error: Selenium is not active.")
            return jsonify({}), 503
        
        return generate_response(character_info, r1, data.get("stream", False))
    except Exception as e:
        print(f"Error receiving data: {e}")
        return jsonify({}), 500

def generate_response(character_info, r1, streaming):
    global driver, last_response
    
    last_response += 1
    current_message = last_response
    show_message(f"\n[color:purple]GENERATING RESPONSE {current_message}:")
    show_message("[color:white]- [color:green]Character data has been received.")
    
    try:
        if not selenium.current_page(driver, "https://chat.deepseek.com") or selenium.current_page(driver, "https://chat.deepseek.com/sign_in"):
            show_message("[color:white]- [color:red]You must be logged into DeepSeek.")
            return create_response("You must be logged into DeepSeek.", streaming)
        
        def interrupted():
            return current_message != last_response

        if interrupted():
            return create_response("", streaming)

        selenium.reset_and_configure_chat(driver, r1)
        show_message("[color:white]- [color:cyan]Chat reset and configured.")

        if interrupted():
            return create_response("", streaming)

        if not selenium.send_chat_message(driver, character_info):
            show_message("[color:white]- [color:red]Could not paste prompt.")
            return create_response("Could not paste prompt.", streaming)

        show_message("[color:white]- [color:green]Prompt pasted and sent.")

        if interrupted():
            return create_response("", streaming)

        if not selenium.active_generate_response(driver):
            show_message("[color:white]- [color:red]No response generated.")
            return create_response("No response generated.", streaming)

        if interrupted():
            return create_response("", streaming)
        
        show_message("[color:white]- [color:cyan]Awaiting response.")
        
        initial_text = ""
        last_text = ""
        start_time = time.time()

        if streaming:
            def streaming_response():
                nonlocal initial_text, last_text, start_time
                while selenium.is_response_generating(driver):
                    if interrupted():
                        yield create_response_streaming("")
                        return

                    if (time.time() - start_time > 180):
                        if last_text:
                            break
                        else:
                            yield create_response_streaming("Error receiving response.")
                            return
                    
                    new_text = selenium.get_last_message(driver)
                    if new_text and not initial_text:
                        initial_text = new_text

                    if new_text and new_text != last_text and new_text.startswith(initial_text):
                        diff = new_text[len(last_text):]
                        last_text = new_text
                        yield create_response_streaming(diff)
                
                response = selenium.closing_symbol(last_text) if last_text else "Error receiving response."
                yield create_response_streaming(response)
                show_message("[color:white]- [color:green]Completed.")
            
            return Response(streaming_response(), content_type="text/event-stream")
        else:
            def jsonify_response():
                nonlocal initial_text, last_text, start_time
                while selenium.is_response_generating(driver):
                    if interrupted():
                        return create_response_jsonify("")
                    
                    if (time.time() - start_time > 180):
                        if last_text:
                            break
                        else:
                            return create_response_jsonify("Error receiving response.")
                    
                    new_text = selenium.get_last_message(driver)
                    if new_text and not initial_text:
                        initial_text = new_text

                    if new_text and new_text.startswith(initial_text):
                        last_text = new_text
                
                response = (last_text + selenium.closing_symbol(last_text)) if last_text else "Error receiving response."
                show_message("[color:white]- [color:green]Completed.")
                return create_response_jsonify(response)
            
            return jsonify_response()
    except Exception as e:
        print(f"Error generating response: {e}")
        show_message("[color:white]- [color:red]Unknown error occurred.")
        return create_response("Error receiving response.", streaming)

def run_services():
    global driver, config_email, config_password, config_browser, config_show_ip
    driver = selenium.initialize_webdriver(config_browser)
    
    if driver:
        threading.Thread(target=monitor_driver, daemon=True).start()
        selenium.login_to_site(driver, config_email, config_password)
        
        clear_messages()
        show_message("[color:red]API IS NOW ACTIVE!")
        show_message("[color:cyan]WELCOME TO INTENSE RP API V2.0")
        show_message("[color:yellow]URL 1: [color:white]http://127.0.0.1:5000/")

        if config_show_ip:
            local_ip = socket.gethostbyname(socket.gethostname())
            show_message(f"[color:yellow]URL 2: [color:white]http://{local_ip}:5000/")
        
        serve(app, host="0.0.0.0", port=5000)
    else:
        clear_messages()
        show_message("[color:red]Selenium failed to start.")

def show_message(text):
    global textbox
    textbox_add(textbox, text)

def clear_messages():
    global textbox
    textbox_clear(textbox)

def assign_config(email, password, browser, show_api):
    global config_email, config_password, config_browser, config_show_ip
    config_email = email
    config_password = password
    config_browser = browser
    config_show_ip = show_api

def assign_textbox(object):
    global textbox
    textbox = object

def monitor_driver():
    global driver
    while True:
        time.sleep(3)
        if driver and not selenium.is_browser_open(driver):
            clear_messages()
            show_message("[color:red]Browser connection lost!")
            driver = None
            break

def close_selenium():
    global driver
    if driver:
        try:
            driver.quit()
            driver = None
        except Exception:
            pass