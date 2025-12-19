#!/usr/bin/env python3
"""
✅ BS DECODER (v13) - SAVED AS bs_decoder.py
ต้องบันทึกไฟล์นี้ในชื่อ "bs_decoder.py" เท่านั้น
"""

import requests
import json
import sys
from datetime import datetime

# ตรวจสอบไฟล์ bs_auth
try:
    from bs_auth import BsAuthManager
except ImportError:
    print("❌ Error: ไม่พบไฟล์ bs_auth.py")
    sys.exit(1)

# ==================== CONFIG ====================
BS_API_URL = "http://open.smartbosun.com:8000"
TARGET_CLIENTID = "860549070312868" # <-- ตัวแปรสำคัญที่ Poller เรียกใช้
auth_manager = BsAuthManager()

# ==================== MAPPING CONFIG ====================
FINAL_OFFSETS = {
    'current_a': {'position': 4, 'length': 2, 'divisor': 100, 'unit': 'A', 'desc': 'Current'},
    'voltage': {'position': 20, 'length': 2, 'divisor': 10, 'unit': 'V', 'desc': 'Voltage'},
    'frequency': {'position': 28, 'length': 2, 'divisor': 100, 'unit': 'Hz', 'desc': 'Frequency'},
    'power_w': {'position': 36, 'length': 2, 'divisor': 100, 'unit': 'W', 'desc': 'Active Power'},
    'power_factor': {'position': 100, 'length': 2, 'divisor': 100, 'unit': 'PF', 'desc': 'Power Factor'},
    'energy_kwh': {'position': 60, 'length': 2, 'divisor': 1000, 'unit': 'kWh', 'desc': 'Energy Consumption'},
    'light_intensity': {'position': 72, 'length': 2, 'divisor': 1, 'unit': 'Lux', 'desc': 'Light Intensity'},
    'brightness': {'position': 120, 'length': 4, 'divisor': 1, 'unit': '%', 'desc': 'Brightness'},
    'temperature': {'position': 264, 'length': 2, 'divisor': 100, 'unit': '°C', 'desc': 'Temperature'},
    'humidity': {'position': 268, 'length': 2, 'divisor': 100, 'unit': '%', 'desc': 'Humidity'},
    'tilt_sensitivity': {'position': 104, 'length': 2, 'divisor': 1, 'unit': '', 'desc': 'Tilt Sensitivity'}
}

def get_device_data():
    token = auth_manager.get_valid_token()
    if not token: return None

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BS_API_URL}/api/v1/device"
    params = {"model": "Device", "Device[page_size]": 10}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for d in data.get("Device", {}).get("items", []):
                if d.get('clientid') == TARGET_CLIENTID:
                    return d
    except Exception as e:
        print(f"Error: {e}")
    return None

def extract_hex(device):
    pt = device.get('param_table', {})
    if isinstance(pt, str): pt = json.loads(pt)
    for v in pt.values():
        val = v.get('D', '') if isinstance(v, dict) else v
        if len(val) > 50: return val
    return None

def decode_final(hex_str):
    payload = hex_str[6:]
    results = {}
    for key, cfg in FINAL_OFFSETS.items():
        try:
            pos = cfg['position']
            length = cfg['length'] * 2 
            chunk = payload[pos : pos + length]
            if not chunk: continue
            raw_val = int(chunk, 16)
            final_val = raw_val / cfg['divisor']
            results[key] = final_val
        except: pass
    return results