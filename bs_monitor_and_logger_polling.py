#!/usr/bin/env python3
"""
📡 BOSUN SMART LOGGER & MONITOR
- Option 1: Force Refresh (Active) -> สั่งให้อัปเดตแล้วบันทึก
- Option 2: Passive Monitor -> อ่านค่าเฉยๆ เพื่อดูพฤติกรรม Server
- บันทึกข้อมูลลงไฟล์ CSV (bosun_data.csv) ทุกครั้ง
"""

import time
import sys
import os
import requests
import json
import csv
from datetime import datetime

# Import bs_decoder
try:
    import bs_decoder as decoder
except ImportError:
    print("❌ Error: ไม่พบไฟล์ bs_decoder.py")
    sys.exit(1)

# ==================== CONFIG ====================
POLL_INTERVAL = 600   # รอบการทำงาน (วินาที) - ค่าเดิม 600 (10 นาที)
LOG_FILENAME = "bosun_data.csv"
CLEAR_SCREEN = True 

#หาตำแหน่งไฟล์ Script ปัจจุบัน
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#กำหนดชื่อโฟลเดอร์ปลายทาง
LOG_DIR = os.path.join(BASE_DIR, "log_test")
# สร้างโฟลเดอร์ log_test ถ้ายังไม่มี (สำคัญมาก! ไม่งั้นจะ Error หา Path ไม่เจอ)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
# กำหนดไฟล์ให้อยู่ในโฟลเดอร์นั้น
LOG_FILENAME = os.path.join(LOG_DIR, "bosun_data.csv")

# -----------------------------------------------------    


# 🔑 Token สำหรับสั่ง Refresh (ต้องคอยอัปเดตถ้าหมดอายุ)
# ใส่ Token ใหม่ที่คุณได้มาล่าสุดตรงนี้
BROWSER_TOKEN = "NTN8MWhjOWIyMTdtMDBkZWs4amRtd2dsNnBzMDBvZTE1cTJ8MTc2NDMyMzY1NA=="

MQTT_API_URL = "https://light.smartbosun.com/api/mqtt"
PROJECT_ID = 51
TARGET_DEVICE_ID = "860549070313080"

# ==================== FUNCTIONS ====================

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def send_force_refresh():
    """ส่งคำสั่ง Refresh"""
    cmd_code = 21 
    d_data = "86054907031308001030044004805E9"
    
    url = f"{MQTT_API_URL}?project_id={PROJECT_ID}"
    headers = {
        "Authorization": f"Bearer {BROWSER_TOKEN}",
        "Content-Type": "application/json",
        "Referer": "https://light.smartbosun.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)"
    }
    
    payload = {
        "msgs": [{
            "topic": f"BS_Sev/{TARGET_DEVICE_ID}",
            "qos": 0,
            "retained": False,
            "payload": {"CMD": cmd_code, "D": d_data}
        }]
    }
    
    try:
        requests.post(url, headers=headers, json=payload, timeout=5)
        return True
    except:
        return False

def save_to_log(data_dict, mode_name):
    """บันทึกข้อมูลลง CSV"""
    file_exists = os.path.isfile(LOG_FILENAME)
    
    # กำหนดลำดับ Column
    fieldnames = ['timestamp', 'mode', 'status', 'power_w', 'voltage', 'current_a', 
                  'frequency', 'power_factor', 'energy_kwh', 'temperature', 
                  'humidity', 'brightness', 'light_intensity', 'tilt_sensitivity']
    
    # เตรียมข้อมูล
    row = data_dict.copy()
    row['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row['mode'] = mode_name
    
    # คำนวณ Status ง่ายๆ เพื่อบันทึก
    p = row.get('power_w', 0)
    row['status'] = 'ON' if p > 5 else 'OFF'

    try:
        with open(LOG_FILENAME, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # เขียน Header ถ้าไฟล์ยังไม่มี
            if not file_exists:
                writer.writeheader()
            
            # กรองเฉพาะ Key ที่เราต้องการบันทึก (ป้องกัน error ถ้า decoder ส่ง key เกินมา)
            filtered_row = {k: row.get(k, '') for k in fieldnames}
            writer.writerow(filtered_row)
            return True
    except Exception as e:
        print(f"❌ Log Error: {e}")
        return False

# ==================== MAIN ====================

def main():
    print("\n🚀 BOSUN SMART LOGGER")
    print("="*30)
    print("1. Force Refresh Mode (กระตุ้นให้อัปเดต)")
    print("2. Passive Mode (อ่านอย่างเดียว - ดูพฤติกรรม Server)")
    print("="*30)
    
    mode_input = input("👉 Select Mode (1 or 2): ").strip()
    
    if mode_input == "1":
        mode_name = "Active(Refresh)"
        print("\n✅ Selected: Force Refresh Mode")
    elif mode_input == "2":
        mode_name = "Passive(Read)"
        print("\n✅ Selected: Passive Monitor Mode")
    else:
        print("❌ Invalid selection")
        return

    print(f"   Target: {TARGET_DEVICE_ID}")
    print(f"   Log File: {LOG_FILENAME}")
    print(f"   Interval: {POLL_INTERVAL} seconds")
    time.sleep(2)
    
    last_data_str = ""
    
    try:
        while True:
            if CLEAR_SCREEN:
                clear()
                print(f"📡 MONITORING [{mode_name}] - {datetime.now().strftime('%H:%M:%S')}")
                print("="*80)
            
            # --- STEP 1: POKE (เฉพาะโหมด 1) ---
            if mode_input == "1":
                if CLEAR_SCREEN: print("🔄 Poking device (Force Refresh)...", end="\r")
                send_force_refresh()
                # รอให้ Server อัปเดตค่า (ถ้า Active)
                time.sleep(3)
            
            # --- STEP 2: READ (อ่านข้อมูล) ---
            if CLEAR_SCREEN: print("📥 Reading data...                   ", end="\r")
            
            try:
                device = decoder.get_device_data()
            except AttributeError:
                 pass # Handle legacy decoder

            if device:
                hex_data = decoder.extract_hex(device)
                
                if hex_data:
                    current_data_str = hex_data[6:]
                    
                    # ถอดรหัส
                    results = decoder.decode_final(hex_data)
                    
                    # --- STEP 3: LOGGING ---
                    save_to_log(results, mode_name)
                    
                    if CLEAR_SCREEN:
                        # แสดงผลหน้าจอ
                        print(f"{'Parameter':<20} {'Value':<15} {'Unit':<10}")
                        print("-" * 60)
                        
                        units = {
                            'current_a': 'A', 'voltage': 'V', 'power_w': 'W', 
                            'energy_kwh': 'kWh', 'frequency': 'Hz', 'power_factor': 'PF',
                            'temperature': '°C', 'humidity': '%', 'brightness': '%',
                            'light_intensity': 'Lux', 'tilt_sensitivity': ''
                        }
                        
                        for key, val in results.items():
                            unit = units.get(key, '')
                            if isinstance(val, float): val_str = f"{val:.2f}"
                            else: val_str = str(val)
                            print(f"{key.replace('_',' ').title():<20} {val_str:<15} {unit:<10}")

                        power = results.get('power_w', 0)
                        status_text = "🟢 ON" if power > 5 else "🔴 OFF"
                        print("-" * 60)
                        print(f"💡 STATUS: {status_text} (Power: {power} W)")
                        print(f"💾 Log saved to {LOG_FILENAME}")
                        
                        if last_data_str and current_data_str != last_data_str:
                            print("\n⚡ CHANGE DETECTED! (Values updated)")
                        elif mode_input == "2":
                            print("\n💤 No change (Passive mode waiting for server update...)")
                        
                        last_data_str = current_data_str
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Data logged. Power: {results.get('power_w')} W")
            
            # --- STEP 4: SLEEP ---
            # ถ้าเป็น Passive Mode อาจจะไม่ต้อง Sleep นานเท่า Active ก็ได้ (แล้วแต่ Config)
            # แต่เพื่อความง่าย ใช้ Interval เดียวกัน
            if CLEAR_SCREEN: print(f"waiting {POLL_INTERVAL}s...", end="\r")
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring Stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()