import uvicorn
import threading
import time
import subprocess
import os
import sys

def log_error(message):
    with open("error_log.txt", "a") as f:
        f.write(f"[{time.ctime()}] {message}\n")

def start_server():
    try:
        from main import app
        # log_config=None taake windowed mode mein crash na ho
        uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)
    except Exception as e:
        log_error(f"SERVER CRASHED: {str(e)}")

if __name__ == "__main__":
    # Windows compatibility fix
    if sys.stdout is None: sys.stdout = open(os.devnull, "w")
    if sys.stderr is None: sys.stderr = open(os.devnull, "w")

    # 1. Backend Start Karo
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # 2. Server ko warm-up honay ka waqt do (10 seconds)
    time.sleep(10)

    # 3. Chrome Launch Logic (App Mode + Camera Allow)
    url = "http://127.0.0.1:8000"
    
    # Chrome ko Cerostio ke liye ek alag profile ke sath kholna
    # Is se camera permissions save ho jayengi
    user_data = os.path.join(os.environ['LOCALAPPDATA'], 'CerostioAppProfile')
    
    chrome_cmd = f'start chrome --app="{url}" --user-data-dir="{user_data}" --unsafely-treat-insecure-origin-as-secure="{url}" --no-first-run --no-default-browser-check'

    try:
        subprocess.Popen(chrome_cmd, shell=True)
    except Exception as e:
        log_error(f"Chrome launch failed: {e}")
        # Fallback to Edge agar Chrome na ho
        os.system(f'start msedge --app="{url}"')

    # Backend ko chalta rehne do
    while True:
        time.sleep(10)