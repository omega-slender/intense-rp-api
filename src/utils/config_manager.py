from cryptography.fernet import Fernet
import json, os

class EncryptedConfigManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.key_path = os.path.join(self.base_path, "secret.key")
        self.config_path = os.path.join(self.base_path, "config.enc")

    def generate_key(self):
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)
    
    def load_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as key_file:
                return key_file.read()
        return None

    def save_config(self, config):
        os.makedirs(self.base_path, exist_ok=True)
        
        key = self.load_key()
        if not key:
            self.generate_key()
            key = self.load_key()

        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(json.dumps(config).encode())

        with open(self.config_path, "wb") as config_file:
            config_file.write(encrypted_data)
    
    def load_config(self, original):
        key = self.load_key()
        if not key or not os.path.exists(self.config_path):
            return original
        
        cipher = Fernet(key)
        try:
            with open(self.config_path, "rb") as config_file:
                encrypted_data = config_file.read()
            decrypted = json.loads(cipher.decrypt(encrypted_data).decode())
            
            if isinstance(decrypted, dict):
                config = {}
                for k in original:
                    if isinstance(original[k], dict):
                        config[k] = {}
                        for subk in original[k]:
                            config[k][subk] = decrypted.get(k, {}).get(subk, original[k][subk])
                    else:
                        config[k] = decrypted.get(k, original[k])
                return config
            else:
                return original
        
        except Exception:
            return original