import os
import re
import subprocess

def get_device_ids():
    """Lấy danh sách device_id từ adb devices"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        print("ADB RAW OUTPUT:", repr(result.stdout))  # Debug output
        lines = result.stdout.strip().split('\n')
        device_ids = []
        for line in lines[1:]:
            if line.strip() and '\tdevice' in line:
                device_ids.append(line.split('\t')[0])
        return device_ids
    except Exception as e:
        print("ADB ERROR:", e)
        return []

def get_cookie_and_token(device_id):
    try:
        cookie_file = f"Cookie{device_id}.txt"
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
        # Copy file từ thiết bị Android về máy tính
        # Copy file đúng đường dẫn đã xác nhận trên LDPlayer
        subprocess.run(f"adb -s {device_id} shell su -c 'cp /data/data/com.facebook.lite/files/PropertiesStore_v02 /sdcard/Cookie_{device_id}'", shell=True)
        subprocess.run(f'adb -s {device_id} pull /sdcard/Cookie_{device_id} {cookie_file}', shell=True)
        with open(cookie_file, "rb") as f:
            text16 = f.read()
        text16 = text16.decode("utf-8", errors="ignore")
        # Lấy access token
        token_match = re.search(r"EAA[a-zA-Z0-9]+", text16)
        token = token_match.group(0) if token_match else ""
        # Lấy cookie
        name_matches = re.findall(r'"name":"(.*?)"', text16)
        value_matches = re.findall(r'"value":"(.*?)"', text16)
        if len(name_matches) <= 1 or len(value_matches) == 0:
            return "Không tìm thấy dữ liệu hợp lệ."
        cookie_dict = {}
        for i in range(1, len(name_matches)):
            if i - 1 < len(value_matches):
                cookie_dict[name_matches[i]] = value_matches[i - 1]
        cookie_header = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        c_user_match = re.search(r"c_user=(.*?);", cookie_header)
        c_user = c_user_match.group(1) if c_user_match else ""
        return f"{cookie_header}|{token}|{c_user}"
    except Exception as e:
        return str(e)
devices1 = get_device_ids()
print(devices1)
for id_device in devices1:
    kqua = get_cookie_and_token(id_device)
    if '|' in kqua:
        cookie, token, user = kqua.split('|', 2)
        print(f"id_device: {id_device}")
        print(f"cookie: {cookie}")
        print(f"token: {token}")
        print(f"user: {user}")
        print("_________")
    else:
        print(f"Device: {id_device} => {kqua}")