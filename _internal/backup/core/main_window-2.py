import sys
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import Qt, QUrl, QDate, QPoint, QLocale, Slot, Signal, QObject
from PySide6.QtQml import QQmlError

from core.plot_manager import PlotManager
from core.splash_sequence_manager import SplashSequenceManager
from ui.views.splash_window import SplashBridge

logger = logging.getLogger("MainWindow")


class MainWindow(QMainWindow):
    imagePathChanged = Signal(str, str)  # (tab_name, file_url)
    fullscreenChanged = Signal(bool)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าหน้าต่าง fullscreen หรือไม่

    def __init__(self, splash_bridge: Optional[SplashBridge] = None):
        super().__init__()
        self._drag_pos: Optional[QPoint] = None
        self._splash_bridge = splash_bridge
        self.sequence: Optional[SplashSequenceManager] = None
        self.view: Optional[QQuickWidget] = None
        self.qml_interface = (
            self  # ให้ PlotManager ส่งกลับมาใช้ self.imagePathChanged.emit()
        )
        self.fullscreenChanged.emit(self.isFullScreen())
        self._setup_splash()
        self._initialize_app()

    def _initialize_app(self):
        try:
            self._setup_window()
            self._setup_qml_view()
            self._load_qml()
            self._start_sequence()
        except Exception as e:
            self._critical_error("Initialization Error", str(e))

    def _setup_splash(self):
        if self._splash_bridge:
            self.sequence = SplashSequenceManager(self._splash_bridge)
            self.sequence.add_step("🔧 Initializing UI...", 600)
        else:
            logger.warning("No SplashBridge provided. Skipping splash steps.")

    def _setup_window(self):
        self.setWindowTitle("Meteorological Plotting System")
        self.setMinimumSize(1470, 800)
        self.setGeometry(100, 100, 1470, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        logger.info("Window initialized")

        # === จัดให้อยู่กลางจอ ===
        screen = self.screen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

        logger.info("Window initialized and centered")

    def _setup_qml_view(self):
        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setClearColor(Qt.transparent)
        self.setCentralWidget(self.view)
        logger.info("QML View configured")
        if self.sequence:
            self.sequence.add_step("📦 QML View container ready...", 800)

    def _load_qml(self):
        qml_path = self._find_qml_file()
        if not qml_path:
            raise FileNotFoundError("MainWindow.qml not found in known paths")

        self._inject_context_properties()
        self.view.setSource(QUrl.fromLocalFile(str(qml_path)))

        if self.view.status() != QQuickWidget.Ready:
            self._log_qml_errors()
            raise RuntimeError("QML failed to load. Check logs.")

        logger.info("QML loaded from: %s", qml_path)

    def _find_qml_file(self) -> Optional[Path]:
        candidates = [
            Path(__file__).parent.parent / "qml" / "MainWindow.qml",
            Path(sys.executable).parent / "ui" / "qml" / "MainWindow.qml",
            Path("C:/Program Files/AWSS/ui/qml/MainWindow.qml"),
            Path("/usr/share/awss/ui/qml/MainWindow.qml"),
        ]
        for path in candidates:
            if path.exists():
                return path
        logger.error("Could not find MainWindow.qml in:")
        for p in candidates:
            logger.error(f" - {p}")
        return None

    def _inject_context_properties(self):
        ctx = self.view.rootContext()
        ctx.setContextProperty("rootWindow", self)
        ctx.setContextProperty("systemLocale", QLocale.system().name())
        ctx.setContextProperty("currentTab", "Surface")
        ctx.setContextProperty("selectedDate", QDate.currentDate())
        ctx.setContextProperty("isFullscreen", self.isFullScreen())
        logger.debug("Injected context properties into QML")

    def _log_qml_errors(self):
        for error in self.view.errors():
            msg = f"❌ Line {error.line()}: {error.description()}"
            if error.url().isValid():
                msg += f" (File: {error.url().toString()})"
            logger.error(msg)
        QMessageBox.critical(
            self, "QML Load Error", "ไม่สามารถโหลดหน้าหลักได้ กรุณาตรวจสอบถอบ QML"
        )

    def _start_sequence(self):
        if self.sequence:
            self.sequence.add_step("✅ UI Ready!", 600)
            self.sequence.start()

            # เรียก plot แผนที่พื้นผิวเริ่มต้น
            # self.plot_map_by_tab("Surface")
        else:
            logger.info("No splash sequence running.")

    def _critical_error(self, title: str, message: str):
        logger.critical(f"{title}: {message}")
        QMessageBox.critical(self, title, message)
        sys.exit(1)

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.LeftButton
            and not self.isFullScreen()
            and not self.isMaximized()
        ):
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if (
            event.buttons() & Qt.LeftButton
            and self._drag_pos
            and not self.isFullScreen()
            and not self.isMaximized()
        ):
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    @Slot(str)
    def updateCurrentTab(self, tab_name: str):
        self.view.rootContext().setContextProperty("currentTab", tab_name)
        logger.debug(f"Tab changed to: {tab_name}")

    @Slot(QDate)
    def updateSelectedDate(self, date: QDate):
        self.view.rootContext().setContextProperty("selectedDate", date)
        logger.debug(f"Selected date updated: {date.toString()}")

    @Slot()
    def minimize(self):
        self.showMinimized()

    @Slot(result=bool)
    def toggleFullscreen(self) -> bool:
        if self.isMaximized() or self.isFullScreen():
            # ✅ คืนค่าขนาดตำแหน่งเริ่มต้นแบบ manual
            self.setWindowState(Qt.WindowNoState)
            self.setGeometry(100, 100, 1470, 800)  # หรือ self._restore_geometry ถ้าเก็บไว้
            self.fullscreenChanged.emit(False)
            self.view.rootObject().setProperty("isFullscreen", False)

            # === จัดให้อยู่กลางจอ ===
            screen = self.screen().availableGeometry()
            size = self.geometry()
            x = (screen.width() - size.width()) // 2
            y = (screen.height() - size.height()) // 2
            self.move(x, y)

            logger.info("Window Normal Size and centered")
            return False
        else:
            # ✅ ขยายเต็มจอ (Maximized)
            self.showMaximized()
            self.fullscreenChanged.emit(True)
            self.view.rootObject().setProperty("isFullscreen", True)
            return True

    @Slot()
    def closeApp(self):
        self.close()  # 🟡 ดีกว่า sys.exit(1) เพื่อ cleanup GUI event loop

    @Slot(str)
    def buttonClicked(self, button_id: str):
        logger.info(f"🔔 Received signal from QML: {button_id}")
        self.append_debugger(f"🔔 Received signal from QML: {button_id}")

        if button_id.startswith("plot:"):
            tab_label = button_id.split("plot:")[1].strip()
            self.plot_map_by_tab(tab_label)
        elif button_id == "load":
            self.load_data()
        elif button_id == "table":
            self.open_table_view()
        elif button_id == "pdf":
            self.save_pdf()
        elif button_id == "png":
            self.save_png()
        elif button_id == "open":
            self.open_text_file()
        else:
            logger.warning(f"⚠️ Unrecognized button id: {button_id}")

    def plot_map_by_tab(self, tab_name: str):
        logger.info(f"Plotting map for tab: {tab_name}")
        # ✅ แจ้ง QML: เริ่ม plot
        self.append_debugger(f"⏳ Plotting {tab_name}...")

        pm = PlotManager(self)  # สร้างอ็อบเจกต์ PlotManager
        pm.plot_surface_and_update_qml()  # เรียก plot แผนที่พื้นผิว (blank version)

        self.append_debugger(f"✅ Plotting {tab_name} successfully.")

    def load_data(self):
        self.update_debugger("📦 Loading SYNOP data...")
        logger.info("🌏 Loading Data...")

    def open_table_view(self):
        logger.info("📊 Opening Table Viewer...")

    def save_pdf(self):
        logger.info("📅 Saving as PDF...")

    def save_png(self):
        logger.info("📸 Saving as PNG...")

    def open_text_file(self):
        logger.info("📂 Opening text file...")

    def update_debugger(self, message: str):
        if self.view and self.view.rootObject():
            self.view.rootObject().setProperty("debugText", message)

    def append_debugger(self, new_line: str):
        if not self.view or not self.view.rootObject():
            logger.warning("⚠️ QML view not ready, cannot append debugger text.")
            return

        root_obj = self.view.rootObject()
        debug_area = root_obj.findChild(QObject, "debugTextArea")

        if debug_area is None:
            logger.warning("⚠️ debugTextArea not found in QML.")
            return

        current = debug_area.property("text")
        combined = f"{current}\n{new_line}"
        debug_area.setProperty("text", combined)

    def update_image_source(self, tab_name: str, file_url: str):
        self.imagePathChanged.emit(tab_name, file_url)
