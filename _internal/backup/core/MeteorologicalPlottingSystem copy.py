# === Meteorological Plotting System (MPS) ===
# Meteorological Plotting System (MPS) - โปรแกรมวาดกราฟข้อมูลอุตุนิยมวิทยา
import os
import sys
import io
import logging

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLocale
from PySide6.QtGui import QIcon, QFontDatabase, QFont

# === import คลาสที่จำเป็นจากระบบภายใน ===
from ui.views.login_window import LoginWindow
from ui.views.main_window import MainWindow


# === ตัวจัดการ Logging ที่รองรับ UTF-8 และ Emoji ===
class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        try:
            if sys.stdout and hasattr(sys.stdout, "buffer"):
                stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        except Exception:
            stream = None
        super().__init__(stream)


# === ตั้งค่าระบบ Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        UTF8StreamHandler(),  # แสดง log บนหน้าจอ (รองรับ Unicode)
        logging.FileHandler("MPS_Debug.log", encoding="utf-8"),  # บันทึก log ลงไฟล์
    ],
)
logger = logging.getLogger("MPS")


# === จุดเริ่มต้นของโปรแกรมหลัก ===
def main():
    try:
        # สร้างแอปพลิเคชันหลัก
        app = QApplication(sys.argv)
        app.setApplicationName("Meteorological Plotting System")  # ชื่อโปรแกรม
        app.setOrganizationName("AWSS-MPS")  # ชื่อองค์กร
        app.setWindowIcon(QIcon("app.ico"))  # ไอคอนของแอป

        # กำหนด path สำหรับโหลดฟอนต์ภาษาไทย
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(
            base_dir,
            "fonts",
            "Noto_Sans_Thai",
            "static",
            "NotoSansThai-Regular.ttf",
        )

        # โหลดฟอนต์ภาษาไทยแบบกำหนดเอง
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app.setFont(QFont(font_family))  # ตั้งค่าเป็นฟอนต์หลัก
            logger.info(f"✅ โหลดฟอนต์ภาษาไทยสำเร็จ: {font_family}")
        else:
            logger.warning("⚠️ ไม่สามารถโหลดฟอนต์ภาษาไทยได้")

        # แสดง locale ของระบบ
        logger.info(f"🌐 Locale ของระบบ: {QLocale.system().name()}")

        # สร้างและแสดงหน้าต่างล็อกอิน
        #logger.info("🚪 กำลังเปิดหน้าต่างล็อกอิน")
        #login = LoginWindow()
        #login.show()
        
        main = MainWindow()
        main.show()

        # เริ่มลูปของแอปพลิเคชัน
        sys.exit(app.exec())

    except Exception as e:
        # แสดงกล่องแจ้งข้อผิดพลาดหากเกิดข้อผิดพลาดร้ายแรง
        logger.exception("💥 เกิดข้อผิดพลาดร้ายแรง")
        QMessageBox.critical(None, "ข้อผิดพลาดร้ายแรง", str(e))
        sys.exit(1)


# === เรียกใช้งานฟังก์ชันหลักเมื่อรันไฟล์นี้โดยตรง ===
if __name__ == "__main__":
    main()
