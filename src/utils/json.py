from flask import jsonify, Response
import re, time, json

def process_character(put_data):
    try:
        messages = put_data.get("messages", [])
        temperature = put_data.get("temperature", 1)
        max_tokens = put_data.get("max_tokens", 300)
        
        if len(messages) >= 2 and messages[-1].get("role") == 'system' and messages[-2].get("role") == 'system':
            messages.pop(-2)
        
        formatted_messages = [f"{msg.get('role', '')}: {msg.get('content', '')}" for msg in messages]
        character_info = "\n\n".join(formatted_messages).replace("system: ", "")
        
        character_name_match = re.search(r'DATA1: "([^\"]*)"', character_info)
        user_name_match = re.search(r'DATA2: "([^\"]*)"', character_info)

        character_name = character_name_match.group(1) if character_name_match else 'Character'
        user_name = user_name_match.group(1) if user_name_match else 'User'
        
        character_info = re.sub(r"({{r1}}|\[r1\]|\(r1\))", "", character_info, flags=re.IGNORECASE)
        character_info = re.sub(r"({{search}}|\[search\])", "", character_info, flags=re.IGNORECASE)
        character_info = re.sub(r'DATA1: "([^"]*)"', "", character_info)
        character_info = re.sub(r'DATA2: "([^"]*)"', "", character_info)

        character_info = character_info.replace("assistant:", character_name + ":").replace("user:", user_name + ":")
        character_info = character_info.replace("{{temperature}}", str(temperature)).replace("{{max_tokens}}", str(max_tokens))
        
        character_info = re.sub(r'\n{3,}', '\n\n', character_info)
        character_info = f"[Important Information]\n{character_info}"
        
        return character_info.strip()
    except Exception as e:
        print(f"Error processing character info: {e}")
        return None

def get_streaming(put_data):
    try:
        return put_data.get("stream", False)
    except Exception:
        return False

def get_deepseek_deepthink(put_data):
    try:
        messages = put_data.get("messages", [])

        if len(messages) >= 2 and messages[-2].get("role") == 'user':
            content = messages[-2].get("content", "")
            
            if re.search(r"({{r1}}|\[r1\]|\(r1\))", content, re.IGNORECASE):
                return True
        
        return False
    except Exception:
        return False

def get_deepseek_search(put_data):
    try:
        messages = put_data.get("messages", [])

        if len(messages) >= 2 and messages[-2].get("role") == 'user':
            content = messages[-2].get("content", "")
            
            if re.search(r"({{search}}|\[search\])", content, re.IGNORECASE):
                return True
        
        return False
    except Exception:
        return False

def get_model():
    return jsonify({
        "object": "list",
        "data": [{
            "id": "rp-intense-2.0",
            "object": "model",
            "created": int(time.time() * 1000)
        }]
    })

def create_response(data, type):
    if type:
        return Response(create_response_streaming(data), content_type="text/event-stream")
    else:
        return create_response_jsonify(data)

def create_response_jsonify(data):
    return jsonify({
        "id": "chatcmpl-intenserp",
        "object": "chat.completion",
        "created": int(time.time() * 1000),
        "model": "rp-intense-2.0",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": data},
            "finish_reason": "stop"
        }]
    })

def create_response_streaming(chunk):
    return "data: " + json.dumps({
                    "id": "chatcmpl-intenserp",
                    "object": "chat.completion.chunk",
                    "created": int(time.time() * 1000),
                    "model": "rp-intense-2.0",
                    "choices": [{"index": 0, "delta": {"content": chunk}}]
                }) + "\n\n"