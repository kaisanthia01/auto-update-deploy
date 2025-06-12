import io
import os
import logging
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import Qt, QUrl, QTimer, Slot, QObject, Signal
from PySide6.QtGui import QColor

from core.auth_service import AuthService
from core.splash_sequence_manager import SplashSequenceManager
from ui.views.main_window import MainWindow
from ui.views.splash_window import SplashBridge, SplashWindow

logger = logging.getLogger("LoginWindow")


class LoginHandler(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.auth = AuthService()

    @Slot(str, str)
    def login(self, username, password):
        logger.debug(f"login() called with user={username}")
        root = self.window.view.rootObject()

        def stop_spinner():
            if root:
                root.hideSpinner()
                logger.warning("loadingSpinner stop.")
            else:
                logger.warning("loadingSpinner not found from root.")

        if self.auth.authenticate_user(username, password):
            logger.info(f"Login success: {username}")
            stop_spinner()
            self.window.goto_main()
        else:
            logger.warning("Invalid credentials")
            stop_spinner()
            if root:
                root.showError("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")


class LoginWindow(QMainWindow):
    versionLoader = Signal(str)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าเวอร์ชั่นโปรแกรม

    def __init__(self, vName: str = ""):
        super().__init__()
        self.setFixedSize(380, 420)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setClearColor(QColor(0, 0, 0, 0))
        self.setCentralWidget(self.view)

        # ✅ Register context properties
        self.handler = LoginHandler(self)
        ctx = self.view.rootContext()
        ctx.setContextProperty("loginHandler", self.handler)
        ctx.setContextProperty("loginWindow", self)
        ctx.setContextProperty("authService", AuthService())
        ctx.setContextProperty("splashWindow", self)

        self.view.setSource(QUrl.fromLocalFile("ui/qml/LoginWindow.qml"))

        if self.view.status() != QQuickWidget.Ready:
            logger.error(f"Failed to load QML: {"ui/qml/LoginWindow.qml"}")
            for err in self.view.errors():
                logger.error("QML Error: %s", err.toString())
            QMessageBox.critical(self, "QML Load Error", "ไม่สามารถโหลดหน้าล็อกอินได้")
            self.close()

        self.versionLoader.emit(vName)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าเวอร์ชั่นโปรแกรม
        self.vName = vName

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and hasattr(self, "_drag_pos"):
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def goto_main(self):
        logger.info("Launching splash window")
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
        # self.sequence.add_step("🚀 Preparing UI...", 1000)
        self.sequence.add_step(
            "📡 Connecting to Meteorological Plotting System...", 1000
        )
        # self.sequence.add_step("🔄 Fetching Data...", 1000)
        # self.sequence.add_step("✅ Almost Ready...", 1000)
        self.sequence.start(on_done=self._show_main)

    def _show_main(self):
        logger.info("Launching main window")
        self.main = MainWindow(self.splash_bridge, self.vName)
        self.sequence.add_step("🚀 Launching Main window...", 1000)
        self.main.show()
        self.splash.close()
