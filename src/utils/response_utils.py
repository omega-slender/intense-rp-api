from flask import jsonify, Response
import re, time, json

__version__ = "2.0.0"

# =============================================================================================================================
# Character Processing
# =============================================================================================================================

def process_character(put_data: dict) -> str | None:
    try:
        messages = put_data.get("messages", [])
        temperature = put_data.get("temperature", 1)
        max_tokens = put_data.get("max_tokens", 300)

        if len(messages) >= 2 and messages[-1].get("role") == "system" and messages[-2].get("role") == "system":
            messages.pop(-2)

        formatted_messages = [f"{msg.get('role', '')}: {msg.get('content', '')}" for msg in messages]
        character_info = "\n\n".join(formatted_messages)

        character_name_match = re.search(r'DATA1:\s*"([^"]*)"', character_info)
        user_name_match = re.search(r'DATA2:\s*"([^"]*)"', character_info)

        character_name = character_name_match.group(1) if character_name_match else "Character"
        user_name = user_name_match.group(1) if user_name_match else "User"

        character_info = re.sub(r"({{r1}}|\[r1\]|\(r1\))", "", character_info, flags=re.IGNORECASE)
        character_info = re.sub(r"({{search}}|\[search\])", "", character_info, flags=re.IGNORECASE)
        character_info = re.sub(r'DATA1:\s*"[^"]*"', "", character_info)
        character_info = re.sub(r'DATA2:\s*"[^"]*"', "", character_info)
        
        character_info = character_info.replace("system: ", "")
        character_info = character_info.replace("assistant:", f"{character_name}:")
        character_info = character_info.replace("user:", f"{user_name}:")
        
        character_info = character_info.replace("{{temperature}}", str(temperature))
        character_info = character_info.replace("{{max_tokens}}", str(max_tokens))
    
        character_info = re.sub(r"\n{3,}", "\n\n", character_info)

        return f"[Important Information]\n{character_info.strip()}"
    except Exception as e:
        print(f"Error processing character info: {e}")
        return None

# =============================================================================================================================
# Response Settings
# =============================================================================================================================

def get_streaming(put_data: dict) -> bool:
    return bool(put_data.get("stream", False))

# =============================================================================================================================
# DeepSeek Settings
# =============================================================================================================================

def _has_marker_in_user_message(messages: list, marker_pattern: str) -> bool:
    if len(messages) >= 2 and messages[-2].get("role") == "user":
        content = messages[-2].get("content", "")
        return re.search(marker_pattern, content, re.IGNORECASE) is not None
    return False

def get_deepseek_deepthink(put_data: dict) -> bool:
    return _has_marker_in_user_message(put_data.get("messages", []), r"({{r1}}|\[r1\]|\(r1\))")

def get_deepseek_search(put_data: dict) -> bool:
    return _has_marker_in_user_message(put_data.get("messages", []), r"({{search}}|\[search\])")

# =============================================================================================================================
# AI Model
# =============================================================================================================================

def get_model() -> Response:
    global __version__
    return jsonify({
        "object": "list",
        "data": [{
            "id": f"rp-intense-{__version__}",
            "object": "model",
            "created": int(time.time() * 1000)
        }]
    })

# =============================================================================================================================
# Response System
# =============================================================================================================================

def create_response_jsonify(text: str) -> Response:
    global __version__
    return jsonify({
        "id": "chatcmpl-intenserp",
        "object": "chat.completion",
        "created": int(time.time() * 1000),
        "model": f"rp-intense-{__version__}",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": text},
            "finish_reason": "stop"
        }]
    })

def create_response_streaming(text: str) -> str:
    global __version__
    return "data: " + json.dumps({
                    "id": "chatcmpl-intenserp",
                    "object": "chat.completion.chunk",
                    "created": int(time.time() * 1000),
                    "model": f"rp-intense-{__version__}",
                    "choices": [{"index": 0, "delta": {"content": text}}]
                }) + "\n\n"

def create_response(text: str, streaming: bool) -> Response:
    if streaming:
        return Response(create_response_streaming(text), content_type="text/event-stream")
    
    return create_response_jsonify(text)