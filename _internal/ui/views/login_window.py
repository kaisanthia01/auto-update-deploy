import io
import os
import sys
import logging
import subprocess
import urllib

from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import Qt, QUrl, QTimer, Slot, QObject, Signal
from PySide6.QtGui import QColor

# === import คลาสที่จำเป็นจากระบบภายใน ===
from core.auth_service import AuthService
from core.splash_sequence_manager import SplashSequenceManager
from ui.views.main_window import MainWindow
from ui.views.splash_window import SplashBridge, SplashWindow

# === ตั้งค่าชื่อ logger สำหรับหน้าต่าง Login ===
logger = logging.getLogger("LoginWindow")

# === กำหนดค่าคงที่สำหรับเวอร์ชันและการอัปเดต ===
LOCAL_VERSION_FILE = "version.txt"  # ชื่อไฟล์เวอร์ชันในเครื่อง
REMOTE_VERSION_URL = "https://kaisanthia01.github.io/auto-update-deploy/version.txt"  # URL สำหรับตรวจสอบเวอร์ชันล่าสุด
AUTO_UPDATER_SCRIPT = "auto_updater.exe"  # ไฟล์ .exe สำหรับอัปเดตโปรแกรม
APP_NAME = "auto_updater.exe"  # ใช้สำหรับเช็กและ kill โปรแกรมอัปเดตหากยังเปิดอยู่

# === คลาสหน้าต่างล็อกอินหลัก เชื่อมต่อ QML และตรวจสอบเวอร์ชัน ===
class LoginWindow(QMainWindow):
    versionLoader = Signal(str)  # 🔔 ส่งสัญญาณเวอร์ชันให้ QML
    versionUpdate = Signal(bool)  # 🔔 แจ้งว่าโปรแกรมต้องอัปเดตหรือไม่

    def __init__(self):
        super().__init__()

        # === ตั้งค่าหน้าต่างหลัก ===
        self.setFixedSize(380, 420)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # === โหลด QML ลง QQuickWidget ===
        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setClearColor(QColor(0, 0, 0, 0))
        self.setCentralWidget(self.view)

        # === เชื่อม context ระหว่าง Python ↔ QML ===
        self.handler = LoginHandler(self)
        ctx = self.view.rootContext()
        ctx.setContextProperty("loginHandler", self.handler)
        ctx.setContextProperty("loginWindow", self)
        ctx.setContextProperty("splashWindow", self)

        qml_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../ui/qml/LoginWindow.qml")
        )
        self.view.setSource(QUrl.fromLocalFile(qml_path))
        logger.info(f"📄 โหลด QML จาก: {qml_path}")

        if self.view.status() != QQuickWidget.Ready:
            logger.error("❌ โหลด QML ไม่สำเร็จ")
            for err in self.view.errors():
                logger.error("QML Error: %s", err.toString())
            QMessageBox.critical(self, "QML Load Error", "ไม่สามารถโหลดหน้าล็อกอินได้")
            self.close()

        # === ตรวจสอบเวอร์ชันและส่งข้อมูลให้ QML ===
        local_ver = get_local_version()
        remote_ver = get_remote_version()

        logger.info(f"🔍 Local version: {local_ver}")
        logger.info(f"🌐 Remote version: {remote_ver}")

        if remote_ver is None or local_ver == remote_ver:
            logger.info("✅ เวอร์ชันตรงกัน หรือไม่สามารถเช็กออนไลน์ได้")
            self.versionUpdate.emit(False)
        else:
            logger.info("⬆️ พบเวอร์ชันใหม่ ต้องอัปเดต")
            self.versionUpdate.emit(True)

        self.versionLoader.emit(local_ver)
        self.vName = local_ver

        # === ปิด auto_updater.exe หากยังเปิดอยู่ ===
        #kill_app()

    # === เมาส์ลากหน้าต่างได้ ===
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and hasattr(self, "_drag_pos"):
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    # === ไปยัง Splash และ MainWindow หลังล็อกอินสำเร็จ ===
    def goto_main(self):
        logger.info("🧊 เปิดหน้าต่าง SplashWindow")
        splash_qml = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "qml/SplashWindow.qml")
        )
        self.splash_bridge = SplashBridge()
        self.splash = SplashWindow(splash_qml, self.splash_bridge)
        self.splash.show()
        self.hide()

        QTimer.singleShot(1200, self._load_main)

    def _load_main(self):
        self.sequence = SplashSequenceManager(self.splash_bridge)
        self.sequence.add_step("🚀 Preparing UI...", 1000)
        self.sequence.add_step(
            "📡 Connecting to Meteorological Plotting System...", 1000
        )
        self.sequence.add_step("🔄 Fetching Data...", 1000)
        self.sequence.add_step("✅ Almost Ready...", 1000)
        self.sequence.start(on_done=self._show_main)

    def _show_main(self):
        logger.info("✅ เปิด MainWindow")
        self.main = MainWindow(self.splash_bridge, self.vName)
        self.sequence.add_step("🚀 Launching Main window...", 1000)
        self.main.show()
        self.splash.close()

    # === Slot เรียกใช้ตอนต้องการอัปเดตเวอร์ชัน ===
    @Slot()
    def updateVersion(self):
        logger.info("🔁 เรียกตัวอัปเดตเวอร์ชันใหม่")
        run_auto_updater()
        logger.info("🔁 เรียก auto_updater.exe สำเร็จ")

# === ฟังก์ชันอ่านเวอร์ชันจากไฟล์ในเครื่อง ===
def get_local_version():
    try:
        base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
            )
        )
        version_path = os.path.join(base_dir, LOCAL_VERSION_FILE)
        logger.debug(f"อ่านเวอร์ชันจาก {version_path}")
        with open(version_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"


# === ฟังก์ชันโหลดเวอร์ชันล่าสุดจาก GitHub ===
def get_remote_version():
    try:
        logger.debug(f"เชื่อมต่อ {REMOTE_VERSION_URL} เพื่อตรวจสอบเวอร์ชันล่าสุด")
        with urllib.request.urlopen(REMOTE_VERSION_URL) as response:
            return response.read().decode().strip().replace("\ufeff", "")
    except Exception as e:
        logger.warning(f"⚠️ ไม่สามารถเช็กเวอร์ชันออนไลน์ได้: {e}")
        return None


# === ฟังก์ชันเรียกตัวอัปเดตโปรแกรมแบบเงียบ ===
def run_auto_updater():
    logger.info("🚀 เรียกใช้งาน auto_updater.exe")
    try:
        result = subprocess.run(
            [AUTO_UPDATER_SCRIPT], check=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ ไม่สามารถเรียก auto updater ได้: {e}")
        return False


# === ตรวจสอบว่าโปรเซสกำลังทำงานอยู่หรือไม่ ===
def is_app_running(app_name):
    try:
        result = subprocess.run(
            ["tasklist"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return app_name in result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ ไม่สามารถเรียก tasklist ได้: {e}")
        return False


# === ปิดโปรแกรม auto_updater.exe หากยังเปิดอยู่ ===
def kill_app():
    if is_app_running(APP_NAME):
        try:
            subprocess.run(
                ["taskkill", "/f", "/im", APP_NAME],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            logger.info(f"✅ ปิด {APP_NAME} เรียบร้อยแล้ว")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ปิด {APP_NAME} ไม่สำเร็จ: {e}")
    else:
        logger.info(f"🟢 ไม่พบ {APP_NAME} กำลังทำงาน ไม่ต้องปิด")


# === คลาสจัดการการล็อกอินและเชื่อมโยงกับ QML ===
class LoginHandler(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.auth = AuthService()

    # === Slot สำหรับให้ QML เรียกใช้งานฟังก์ชัน login ===
    @Slot(str, str)
    def login(self, username, password):
        logger.debug(f"login() called with user={username}")
        root = self.window.view.rootObject()

        # หยุด spinner ใน QML
        def stop_spinner():
            if root:
                root.hideSpinner()
                logger.warning("✅ หยุด spinner เรียบร้อย")
            else:
                logger.warning("❌ ไม่พบ spinner ใน root")

        # ตรวจสอบข้อมูลล็อกอิน
        if self.auth.authenticate_user(username, password):
            logger.info(f"✅ ล็อกอินสำเร็จ: {username}")
            stop_spinner()
            self.window.goto_main()
        else:
            logger.warning("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            stop_spinner()
            if root:
                root.showError("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")