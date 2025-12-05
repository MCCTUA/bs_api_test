#!/usr/bin/env python3
"""
🚀 Bosun IoT Controller - Stable Version 
"""

import requests
import json
import sys

# ==================== CONFIGURATION ====================
# Token จาก Browser
# Server B (Control ON/OFF): ใช้ Token แบบ User Session (Browser) ซึ่งระบบ Enterprise API ยังไม่เปิดให้ใช้
# สถานะ: เราจึงต้องไป "แอบ" Copy Token นี้มาจาก Browser เพื่อมาใส่ใน Code

LONG_LIVED_TOKEN = "NTN8MWhjOWIyMThtdzBkZXB3bjhidjIzbzNhMDBjMThlejN8MTc2NDg5OTQ2Mw=="

MQTT_API_URL = "https://light.smartbosun.com/api/mqtt"
PROJECT_ID = 51
DEVICE_CLIENTID = "860549070313080"

def send_command(cmd_code, d_data, description=""):
    print("\n" + "="*60)
    print(f"💡 Command: {description}")
    print("="*60)
    
    url = f"{MQTT_API_URL}?project_id={PROJECT_ID}"
    
    # Headers เลียนแบบ Browser (The Winning Formula)
    headers = {
        "Authorization": f"Bearer {LONG_LIVED_TOKEN}",
        "Content-Type": "application/json",
        "Referer": "https://light.smartbosun.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }
    
    payload = {
        "msgs": [{
            "topic": f"BS_Sev/{DEVICE_CLIENTID}",
            "qos": 0,
            "retained": False,
            "payload": {"CMD": cmd_code, "D": d_data}
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! สั่งงานสำเร็จ")
            return True
        elif response.status_code == 401:
            print(f"❌ 401 Unauthorized: Token อาจจะหมดอายุ (เช็คหลัง Nov 2025)")
            return False
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

# ==================== MAIN ====================

def send_turn_on():
    # Checksum AE28 (Brightness 100%)
    d_data = "860549070313080011000630001020064AE28"
    send_command(20, d_data, "Turn On")

def send_turn_off():
    # Checksum AFC3
    d_data = "860549070313080011000630001020000AFC3"
    send_command(21, d_data, "Turn Off")

# เพิ่มฟังก์ชันนี้ลงใน bs_controller_stable.py

def send_refresh():
    print("\n" + "="*60)
    print("🔄 Sending Force Refresh Command...")
    print("="*60)
    
    # 📌 Payload สำหรับ Refresh (แกะจาก WebSocket ของคุณ)
    # CMD: 21 (เหมือน Turn Off แต่ไส้ในคือคำสั่ง Read)
    # Data Breakdown:
    # 860549070313080  (Device ID)
    # 01               (Unit ID)
    # 03               (Func Code: Read)
    # 0044             (Start Address: Current/Voltage area)
    # 0048             (Length: อ่านยาวๆ เพื่อกวาดทุกค่า)
    # 05E9             (Checksum CRC16)
    
    cmd_code = 21 
    d_data = "86054907031308001030044004805E9"
    
    success = send_command(cmd_code, d_data, "Force Refresh (Read Status)")
    
    if success:
        print("⏳ รอสัก 3-5 วินาที เพื่อให้ค่าอัปเดต...")


    print("\n🚀 Bosun Controller (Stable 2025)")
    print(f"   Target: {DEVICE_CLIENTID}")
    
    while True:
        print("\n👇 Menu:")
        print("1. [ON]  Turn On")
        print("2. [OFF] Turn Off")
        print("3. [X]   Exit")
        
        choice = input("Select: ").strip()
        
        if choice == "1": send_turn_on()
        elif choice == "2": send_turn_off()
        elif choice == "3": break

def main():
    print("\n🚀 Bosun Controller (Stable 2025)")
    print(f"   Target: {DEVICE_CLIENTID}")
    
    while True:
        print("\n👇 Menu:")
        print("1. [ON]  Turn On")
        print("2. [OFF] Turn Off")
        print("3. [REF] Force Refresh (Update Status)")  # <--- เพิ่มเมนูนี้
        print("4. [X]   Exit")
        
        choice = input("Select: ").strip()
        
        if choice == "1": send_turn_on()
        elif choice == "2": send_turn_off()
        elif choice == "3": send_refresh()  # <--- เรียกใช้ฟังก์ชัน
        elif choice == "4": break

if __name__ == "__main__":
    main()