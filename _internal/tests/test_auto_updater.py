import os
import sys
import zipfile
import urllib.request
import shutil
import subprocess
import time
import logging

logger = logging.getLogger("CheckURLSurface")

# ตั้งค่ารองรับ UTF-8 สำหรับ Windows Terminal
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")

UPDATE_URL = "https://kaisanthia01.github.io/auto-update-deploy/version.txt"
ZIP_URL = "https://kaisanthia01.github.io/auto-update-deploy/update.zip"
APP_NAME = "app.exe"
ZIP_NAME = "update.zip"


def get_remote_version():
    with urllib.request.urlopen(UPDATE_URL) as response:
        return response.read().decode().strip()


def get_local_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"


def download_update():
    print("📥 Downloading update...")
    urllib.request.urlretrieve(ZIP_URL, ZIP_NAME)


def extract_update():
    print("📦 Extracting update...")
    with zipfile.ZipFile(ZIP_NAME, "r") as zip_ref:
        zip_ref.extractall(".")
    os.remove(ZIP_NAME)


def kill_app():
    print("🛑 Closing app...")
    os.system(f"taskkill /f /im {APP_NAME}")


def launch_app():
    print("🚀 Launching new version...")
    subprocess.Popen([APP_NAME])
    sys.exit()


def main():
    remote_version = get_remote_version()
    local_version = get_local_version()

    print(f"🔎 Local: {local_version} | Remote: {remote_version}")

    if remote_version != local_version:
        kill_app()
        time.sleep(1)
        download_update()
        extract_update()
        with open("version.txt", "w") as f:
            f.write(remote_version)
        launch_app()
    else:
        print("✅ Already up-to-date.")


if __name__ == "__main__":
    main()
