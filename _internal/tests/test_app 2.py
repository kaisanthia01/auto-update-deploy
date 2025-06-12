import io
import urllib.request
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLocale
from PySide6.QtGui import QFontDatabase, QFont, QIcon
from ui.views.login_window import LoginWindow
from ui.views.main_window import MainWindow
import logging


# ตั้งค่ารองรับ UTF-8 สำหรับ Windows Terminal
class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        # ตรวจสอบ sys.stdout ก่อนใช้
        if sys.stdout and hasattr(sys.stdout, "buffer"):
            stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        super().__init__(stream)


# ใช้ UTF8StreamHandler แทน StreamHandler เดิม
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        UTF8StreamHandler(),  # ✅ รองรับ emoji และ Unicode เต็ม
        logging.FileHandler("MPS_Debug.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("MPS")

# กำหนดไฟล์เวอร์ชันในเครื่อง และ URL สำหรับตรวจสอบเวอร์ชันล่าสุด
LOCAL_VERSION_FILE = "version.txt"
REMOTE_VERSION_URL = "https://kaisanthia01.github.io/auto-update-deploy/version.txt"
AUTO_UPDATER_SCRIPT = "auto_updater.py"


# ฟังก์ชันสำหรับอ่านเวอร์ชันจากไฟล์ในเครื่อง
def get_local_version():
    """อ่านเวอร์ชันจากไฟล์ version.txt ในเครื่อง ถ้าไม่มีให้คืนค่า '0.0.0'"""
    try:
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"


# ฟังก์ชันสำหรับดาวน์โหลดเวอร์ชันล่าสุดจาก URL
def get_remote_version():
    """ดาวน์โหลดเวอร์ชันล่าสุดจาก URL และคืนค่าเป็นสตริง"""
    try:
        with urllib.request.urlopen(REMOTE_VERSION_URL) as response:
            return response.read().decode().strip()
    except Exception as e:
        logger.warning(f"ไม่สามารถเช็กเวอร์ชันออนไลน์ได้: {e}")
        return None


# ฟังก์ชันสำหรับเรียกสคริปต์ auto_updater.py เพื่อทำการอัปเดตโปรแกรม
def run_auto_updater():
    """เรียกสคริปต์ auto_updater.py เพื่อทำการอัปเดตโปรแกรม"""
    logger.info("เรียก auto_updater.py เพื่ออัปเดต")
    result = subprocess.run([sys.executable, AUTO_UPDATER_SCRIPT])
    return result.returncode == 0


# ฟังก์ชันหลักสำหรับรันโปรแกรม
def main():
    try:
        # อ่านเวอร์ชันทั้งสองฝั่ง
        local_ver = get_local_version()
        remote_ver = get_remote_version()

        logger.info(f"Local version: {local_ver}")
        logger.info(f"Remote version: {remote_ver}")

        # ถ้าไม่สามารถเช็กเวอร์ชันออนไลน์ได้ หรือเวอร์ชันตรงกัน
        if remote_ver is None or local_ver == remote_ver:
            logger.info("เวอร์ชันตรงกัน หรือไม่สามารถเช็กเวอร์ชันออนไลน์ได้ - เปิดโปรแกรมปกติ")
        else:
            # เวอร์ชันไม่ตรงกัน ต้องอัปเดตก่อนเปิดโปรแกรม
            logger.info("เวอร์ชันไม่ตรงกัน กำลังอัปเดต...")
            success = run_auto_updater()
            if success:
                logger.info("อัปเดตสำเร็จ ปิดโปรแกรมนี้และให้ auto_updater เปิดโปรแกรมใหม่แทน")
                local_ver = get_local_version()
                logger.info(f"เวอร์ชันใหม่: {local_ver}")
                sys.exit(0)  # ปิดโปรแกรมนี้เพื่อรอให้ auto_updater เปิดโปรแกรมใหม่
            else:
                logger.warning("อัปเดตไม่สำเร็จ เปิดโปรแกรมต่อไป")

        # สร้าง QApplication และตั้งค่าทั่วไป
        app = QApplication(sys.argv)
        app.setApplicationName(f"Meteorological Plotting System - v.{local_ver}")
        app.setOrganizationName("AWSS-MPS")
        app.setWindowIcon(QIcon("images/icons/logowxao-3.png"))

        # โหลดฟอนต์ภาษาไทย
        font_id = QFontDatabase.addApplicationFont(
            "fonts/Noto_Sans_Thai/static/NotoSansThai-Regular.ttf"
        )
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app.setFont(QFont(family))
            logger.info(f"Thai font loaded: {family}")
        else:
            logger.warning("Failed to load Thai font.")

        logger.info("System locale: %s", QLocale.system().name())

        # เปิดหน้าต่างล็อกอิน
        logger.info("Launching login window")
        login = LoginWindow(local_ver)
        login.show()

        # แสดงหน้าต่างหลัก
        # main = MainWindow("", local_ver)
        # main.show()

        # รัน event loop ของแอป
        sys.exit(app.exec())

    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดร้ายแรง")
        QMessageBox.critical(None, "Fatal Error", str(e))
        sys.exit(1)


# ฟังก์ชันหลักที่รันโปรแกรม
if __name__ == "__main__":
    main()
