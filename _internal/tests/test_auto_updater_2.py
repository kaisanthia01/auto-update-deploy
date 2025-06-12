import sys
import os
import zipfile
import urllib.request
import subprocess
import logging
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QMessageBox,
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt, QCoreApplication
from PySide6.QtGui import QIcon, QFontDatabase, QFont

# ✅ CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # กำหนดไดเรกทอรีหลักของโปรแกรม
APP_NAME = "MeteorologicalPlottingSystem.exe"  # ชื่อไฟล์โปรแกรมหลัก
VERSION_FILE = "version.txt"  # ไฟล์เก็บเวอร์ชันปัจจุบัน
UPDATE_URL = "https://kaisanthia01.github.io/auto-update-deploy/version.txt"  # URL สำหรับตรวจสอบเวอร์ชันล่าสุด
ZIP_URL = "https://kaisanthia01.github.io/auto-update-deploy/update.zip"  # URL สำหรับดาวน์โหลดไฟล์ ZIP อัปเดต
ZIP_NAME = "update.zip"  # ชื่อไฟล์ ZIP ที่จะดาวน์โหลด
CHANGELOG_URL = "https://kaisanthia01.github.io/auto-update-deploy/changelog.txt"

# ✅ LOGGING
logging.basicConfig(
    filename="MPS_Update.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("AutoUpdater")


# ✅ VERSION FUNCTIONS
def get_remote_version():
    with urllib.request.urlopen(UPDATE_URL) as response:
        return response.read().decode().strip().replace("\ufeff", "")


# ✅ LOCAL VERSION FUNCTIONS
def get_local_version():
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"


# ✅ WRITE VERSION
def write_version(version):
    with open(VERSION_FILE, "w") as f:
        f.write(version)


# ✅ KILL APPLICATION
def kill_app():
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", APP_NAME],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"✅ ปิด {APP_NAME} เรียบร้อยแล้ว")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ ไม่พบ {APP_NAME} หรือปิดไม่สำเร็จ: {e.stderr.strip()}")


# ✅ EXTRACT AND UPDATE
def extract_update():
    with zipfile.ZipFile(ZIP_NAME, "r") as zip_ref:
        zip_ref.extractall(".")
    os.remove(ZIP_NAME)


# ✅ LAUNCH APPLICATION
def launch_app():
    if not os.path.exists(APP_NAME):
        logger.error(f"❌ ไม่พบไฟล์โปรแกรมหลัก: {APP_NAME}")
        QMessageBox.critical(None, "ผิดพลาด", f"ไม่พบไฟล์โปรแกรมหลัก:\n{APP_NAME}")
        return
    logger.info(f"🚀 Launching: {APP_NAME}")
    subprocess.Popen([APP_NAME])
    sys.exit(0)


# ✅ CHECK CHANGELOG
def load_changelog():
    try:
        with urllib.request.urlopen(CHANGELOG_URL) as r:
            return r.read().decode("utf-8").strip()
    except Exception as e:
        logger.warning(f"ไม่สามารถโหลด changelog: {e}")
        return "⚠️ ไม่สามารถโหลดรายละเอียดการเปลี่ยนแปลง"


# ✅ THREAD สำหรับโหลด
class DownloadThread(QThread):
    progress = Signal(int)
    status = Signal(str)
    done = Signal()
    error = Signal(str)

    def run(self):
        try:
            with urllib.request.urlopen(ZIP_URL) as response:
                total_size = int(response.getheader("Content-Length", 0))
                block_size = 8192
                downloaded = 0

                with open(ZIP_NAME, "wb") as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        f.write(buffer)
                        downloaded += len(buffer)
                        percent = int(downloaded * 100 / total_size)
                        self.progress.emit(percent)
                        self.status.emit(
                            f"📥 {downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB"
                        )

            self.done.emit()
        except Exception as e:
            self.error.emit(str(e))
            logger.exception("Download failed")


# ✅ GUI CLASS
class AutoUpdaterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Update - AWSS MPS")
        self.setFixedSize(400, 200)
        self.setWindowIcon(QIcon("images/icons/icon.ico"))

        # ✅ Load Thai font globally
        font_id = QFontDatabase.addApplicationFont(
            "fonts/Noto_Sans_Thai/static/NotoSansThai-Regular.ttf"
        )
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.setFont(QFont(family, 11))
            logger.info(f"Thai font loaded: {family}")
        else:
            logger.warning("Failed to load Thai font.")

        self.label = QLabel("🔍 กำลังตรวจสอบเวอร์ชัน...")
        self.label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.retry_btn = QPushButton("🔁 ลองใหม่")
        self.retry_btn.setVisible(False)
        self.retry_btn.clicked.connect(self.start_update)

        self.launch_btn = QPushButton("🚀 เปิดโปรแกรม")
        self.launch_btn.setVisible(False)
        self.launch_btn.clicked.connect(launch_app)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.retry_btn)
        layout.addWidget(self.launch_btn)
        self.setLayout(layout)

        QTimer.singleShot(500, self.check_version)

        self.setStyleSheet(
            """
                QWidget {
                    background-color: #2c3e50;  /* พื้นหลังหลัก */
                    font-family: 'Noto Sans Thai';
                    font-size: 14px;
                    color: #ecf0f1;
                }
            
                QLabel {
                    color: #ecf0f1;
                }
            
                QProgressBar {
                    background-color: #fff;  /* สีขาว */
                    color: #ecf0f1; /* ข้อความใน ProgressBar */
                    border: 1px solid #95a5a6;
                    border-radius: 6px;
                    text-align: center;
                    height: 20px;
                    font-family: 'Noto Sans Thai';
                    font-size: 14px;
                }
            
                QProgressBar::chunk {
                    background-color: #078f00;  /* เขียวอ่อน */
                    border-radius: 6px;
                }
            
                QPushButton {
                    background-color: #2980b9;  /* ปุ่มฟ้า */
                    color: white;
                    border: none;
                    padding: 8px 14px;
                    border-radius: 6px;
                }
            
                QPushButton:hover {
                    background-color: #3498db;
                }
            
                QPushButton:disabled {
                    background-color: #7f8c8d;
                    color: #ecf0f1;
                }
            
                QGroupBox {
                    border: 1px solid #95a5a6;
                    border-radius: 8px;
                    margin-top: 10px;
                }
            
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                    color: #ecf0f1;
                    font-weight: bold;
                }
            
                QComboBox, QSpinBox, QSlider, QCalendarWidget, QLineEdit {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 4px;
                }
            """
        )

        logger.info("AutoUpdater initialized")

    # ✅ CHECK VERSION
    def check_version(self):
        try:
            remote = get_remote_version()
            local = get_local_version()
            logger.info(f"Local: {local} | Remote: {remote}")
            if remote != local:
                changelog = load_changelog()
                reply = QMessageBox.question(
                    self,
                    f"พบเวอร์ชันใหม่ {remote}",
                    f"มีการเปลี่ยนแปลงดังนี้:\n\n{changelog}\n\nต้องการอัปเดตหรือไม่?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    self.start_update()
                else:
                    self.label.setText("❌ ผู้ใช้ยกเลิกการอัปเดต")
                    self.launch_btn.setVisible(True)
                    logger.error("❌ ผู้ใช้ยกเลิกการอัปเดต")

            else:
                self.label.setText("✅ โปรแกรมเป็นเวอร์ชันล่าสุด")
                self.launch_btn.setVisible(True)
                logger.info("✅ โปรแกรมเป็นเวอร์ชันล่าสุด")

        except Exception as e:
            self.label.setText(f"⚠️ ไม่สามารถตรวจสอบเวอร์ชัน: {e}")
            self.retry_btn.setVisible(True)
            logger.error(f"⚠️ ไม่สามารถตรวจสอบเวอร์ชัน: {e}")

    # ✅ START UPDATE
    def start_update(self):
        self.label.setText("📥 เริ่มดาวน์โหลดอัปเดต...")
        self.progress.setValue(0)
        self.retry_btn.setVisible(False)
        self.thread = DownloadThread()

        self.thread.progress.connect(self.progress.setValue)
        self.thread.status.connect(lambda text: self.label.setText(text))
        self.thread.done.connect(self.apply_update)
        self.thread.error.connect(self.download_failed)

        kill_app()
        self.thread.start()
        logger.info("📥 เริ่มดาวน์โหลดอัปเดต...")

    # ✅ APPLY UPDATE
    def apply_update(self):
        self.label.setText("📦 แตกไฟล์...")
        try:
            extract_update()
            write_version(get_remote_version())
            self.label.setText("✅ อัปเดตสำเร็จแล้ว")
            self.launch_btn.setVisible(True)  # ✅ กรณีใช้ปุ่ม

            logger.info("✅ อัปเดตสำเร็จแล้ว")
            QTimer.singleShot(500, launch_app)  # ✅ เปิดโปรแกรมหลักทันทีหลังอัปเดต

        except Exception as e:
            self.label.setText(f"❌ แตกไฟล์ล้มเหลว: {e}")
            self.retry_btn.setVisible(True)
            logger.exception(f"❌ แตกไฟล์ล้มเหลว: {e}")

    def download_failed(self, error):
        self.label.setText(f"❌ ดาวน์โหลดล้มเหลว: {error}")
        self.retry_btn.setVisible(True)
        logger.error(f"❌ ดาวน์โหลดล้มเหลว: {error}")


# ✅ SILENT MODE
def run_silent_mode():
    try:
        remote = get_remote_version()
        local = get_local_version()
        logger.info(f"(Silent) Local: {local} | Remote: {remote}")
        if remote != local:
            kill_app()
            with urllib.request.urlopen(ZIP_URL) as response, open(ZIP_NAME, "wb") as f:
                f.write(response.read())
            extract_update()
            write_version(remote)
            logger.info("✅ Silent update success")
        else:
            logger.info("✅ Already up-to-date (silent)")
        logger.info("🚀 Launching main app...")
        launch_app()
    except Exception as e:
        logger.exception("Silent update failed")
        sys.exit(1)


# ✅ MAIN
if __name__ == "__main__":
    # if "--silent" in sys.argv:
    #    app = QCoreApplication(sys.argv)
    #    run_silent_mode()
    # else:
    #    app = QApplication(sys.argv)
    #    window = AutoUpdaterWindow()
    #    window.show()
    #    sys.exit(app.exec())

    app = QApplication(sys.argv)
    window = AutoUpdaterWindow()
    window.show()
    sys.exit(app.exec())
