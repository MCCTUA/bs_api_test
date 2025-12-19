#!/usr/bin/env python3
"""
📋 BS Device Lister
แสดงรายการอุปกรณ์ทั้งหมด โดยใช้ Token อัตโนมัติจาก bs_auth.py
"""

import requests
import json
import sys

# ตรวจสอบว่ามีไฟล์ bs_auth.py อยู่หรือไม่
try:
    from bs_auth import BsAuthManager
except ImportError:
    print("❌ Error: ไม่พบไฟล์ bs_auth.py กรุณาวางไว้ในโฟลเดอร์เดียวกัน")
    sys.exit(1)

# ==================== CONFIG ====================
BS_API_URL = "http://open.smartbosun.com:8000"

# สร้าง Auth Manager
auth_manager = BsAuthManager()

def list_all_devices():
    print("\n" + "="*60)
    print("📋 BS IoT - Device List")
    print("="*60)
    
    # 1. ขอ Token (แบบไม่ต้อง Format ซ้ำ)
    access_token = auth_manager.get_valid_token()
    
    if not access_token:
        print("❌ ไม่สามารถขอ Token ได้")
        return

    url = f"{BS_API_URL}/api/v1/device"
    
    # Parameters ในการดึงข้อมูล
    params = {
        "model": "Device",
        "Device[with]": '["DeviceLocation"]', # ดึงข้อมูล Location มาด้วยถ้ามี
        "Device[page]": 1,
        "Device[page_size]": 50  # ดึงมา 50 ตัวแรก (ปรับเพิ่มได้)
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}", # ✅ ใช้ Token ตรงๆ
        "Content-Type": "application/json"
    }
    
    print(f"🔄 Connecting to Server...")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # ดึง list รายการอุปกรณ์ออกมา
            device_list = data.get("Device", {}).get("items", [])
            total_count = data.get("Device", {}).get("total", 0)
            
            print(f"✅ Success! Found {total_count} device(s).\n")
            print("-" * 60)
            
            # วนลูปแสดงข้อมูลทีละตัว
            if not device_list:
                print("   (No devices found)")
            
            for i, device in enumerate(device_list, 1):
                d_id = device.get('id', 'N/A')
                d_name = device.get('name', 'Unknown')
                d_clientid = device.get('clientid', 'N/A')
                d_online = device.get('online_status') # 1=Online, 2=Offline (เดาจาก log เก่า)
                
                # แปลงสถานะออนไลน์ให้ดูง่าย
                status_icon = "🟢 ONLINE " if str(d_online) == "2" else "🔴 OFFLINE"
                
                print(f"Device #{i}")
                print(f"   Name:     {d_name}")
                print(f"   ClientID: {d_clientid}")
                print(f"   ID:       {d_id}")
                print(f"   Status:   {status_icon} (Code: {d_online})")
                print("-" * 60)
                
        else:
            print(f"❌ Error {response.status_code}")
            print(f"   Message: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    list_all_devices()