"""doubao2api QR 登录：生成二维码 → 等待扫码 → 保存 .doubao_session.json"""
from doubao2api.qr_login import QRLogin
import time, json

qr = QRLogin()
result = {"done": False}

def on_status(status, msg):
    print(f"STATUS {status}: {msg}", flush=True)

def on_done(r):
    result["done"] = True
    result["r"] = r
    print(f"DONE status={r.status} sessionid={'YES' if r.sessionid else 'NO'} cookies={len(r.cookies)}", flush=True)

qr.start(on_status=on_status, on_done=on_done)
time.sleep(4)
if qr.qrcode_data:
    with open("qr_code.png", "wb") as f:
        f.write(qr.qrcode_data)
    print("QR_SAVED qr_code.png", flush=True)
else:
    print("NO_QRCODE", flush=True)

deadline = time.time() + 150
while time.time() < deadline and not result["done"]:
    time.sleep(2)

if result["done"]:
    r = result["r"]
    if r.cookies and r.sessionid:
        data = {"cookies": r.cookies, "params": r.device_params}
        with open(".doubao_session.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("SESSION_SAVED", flush=True)
    else:
        print("LOGIN_INCOMPLETE", r.status, r.error, flush=True)
else:
    print("TIMEOUT", flush=True)
