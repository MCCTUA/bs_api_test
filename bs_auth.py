#!/usr/bin/env python3
"""
🔐 Bosun Auth Manager (Updated v2)
เพิ่มฟังก์ชัน get_token_with_expiry เพื่อรองรับการสร้าง Browser Token
"""

import requests
import json
import time
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# ==================== CONFIG ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
PRIVATE_KEY_PATH = os.path.join(CONFIG_DIR, "private_key.pem")
TOKEN_CACHE_FILE = os.path.join(CONFIG_DIR, "token_cache.json")

BOSUN_AUTH_URL = "http://open.smartbosun.com:8000/api/v1/access_token"
ENTERPRISE_ID = 51
APPID = "1hc9b214nt0debmj7jf51e18j0s4fj6h"

class BosunAuthManager:
    def __init__(self):
        self.enterprise_id = ENTERPRISE_ID
        self.appid = APPID
        self.private_key_path = PRIVATE_KEY_PATH
        self.token_file = TOKEN_CACHE_FILE
        
        if not os.path.exists(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR)
            except OSError:
                pass

    def _load_private_key(self):
        try:
            with open(self.private_key_path, 'rb') as f:
                return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
        except FileNotFoundError:
            raise Exception(f"❌ ไม่พบไฟล์ Private Key: {self.private_key_path}")

    def _generate_signature(self, timestamp, nonce):
        private_key = self._load_private_key()
        sig_string = f"appid={self.appid}&enterprise_id={self.enterprise_id}&nonce={nonce}&time={timestamp}"
        signature = private_key.sign(sig_string.encode(), padding.PKCS1v15(), hashes.SHA256())
        return signature.hex()

    def _request_new_token(self):
        print("🔄 Requesting new token from Server...")
        timestamp = int(time.time())
        nonce = f"nonce_{timestamp}"
        signature = self._generate_signature(timestamp, nonce)

        payload = {
            "enterprise_id": self.enterprise_id,
            "appid": self.appid,
            "time": timestamp,
            "nonce": nonce,
            "sig": signature
        }

        try:
            response = requests.post(BOSUN_AUTH_URL, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "access_token" in data["token"]:
                    token_data = {
                        "access_token": data["token"]["access_token"],
                        "expire_time": data["token"]["expire_time"],
                        "fetched_at": time.time()
                    }
                    with open(self.token_file, 'w') as f:
                        json.dump(token_data, f)
                    return token_data
            return None
        except Exception as e:
            print(f"❌ Network Error: {e}")
            return None

    def get_valid_token(self):
        # คืนค่าเฉพาะ Token string (เพื่อให้ bs_list.py / bs_reader.py เดิมใช้งานได้ไม่กระทบ)
        data = self.get_token_data()
        return data["access_token"] if data else None

    def get_token_data(self):
        # ✅ ฟังก์ชันใหม่: คืนค่าทั้ง Token และ Expire Time
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                
                # เช็ควันหมดอายุ
                expire_time = data.get("expire_time", 0)
                current_time = time.time()
                if expire_time > 2000000000: current_time *= 1000 # Handle MS timestamp
                
                if current_time < (expire_time - 300):
                    return data
            except:
                pass

        return self._request_new_token()