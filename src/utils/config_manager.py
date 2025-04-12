from cryptography.fernet import Fernet
import json, os

def get_key_path(base_path):
    return os.path.join(base_path, "secret.key")

def get_config_path(base_path):
    return os.path.join(base_path, "config.enc")

def generate_key(base_path):
    key_path = get_key_path(base_path)
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        os.makedirs(base_path, exist_ok=True)
        with open(key_path, "wb") as key_file:
            key_file.write(key)

def load_key(base_path):
    key_path = get_key_path(base_path)
    if os.path.exists(key_path):
        with open(key_path, "rb") as key_file:
            return key_file.read()
    return None

def save_config(base_path, email, password, browser, show_ip=True, show_console=False):
    key = load_key(base_path)
    if not key:
        generate_key(base_path)
        key = load_key(base_path)

    cipher = Fernet(key)
    data = {
        "email": email,
        "password": password,
        "browser": browser,
        "show_ip": show_ip,
        "show_console": show_console
    }
    encrypted_data = cipher.encrypt(json.dumps(data).encode())

    os.makedirs(base_path, exist_ok=True)
    config_path = get_config_path(base_path)
    with open(config_path, "wb") as config_file:
        config_file.write(encrypted_data)

def load_config(base_path):
    key = load_key(base_path)
    config_path = get_config_path(base_path)
    if not key or not os.path.exists(config_path):
        return None, None, "Chrome", True, False

    cipher = Fernet(key)
    with open(config_path, "rb") as config_file:
        encrypted_data = config_file.read()

    try:
        decrypted_data = json.loads(cipher.decrypt(encrypted_data).decode())
        return (
            decrypted_data.get("email"),
            decrypted_data.get("password"),
            decrypted_data.get("browser", "Chrome"),
            decrypted_data.get("show_ip", True),
            decrypted_data.get("show_console", False)
        )
    except:
        return None, None, "Chrome", True, False