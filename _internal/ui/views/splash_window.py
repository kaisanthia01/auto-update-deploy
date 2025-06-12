# ui/views/splash_window.py
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QUrl, Qt
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import QObject, Signal, Property
import logging

logger = logging.getLogger("MPS")


class SplashWindow(QMainWindow):
    def __init__(self, qml_file, bridge):  # ✅ เพิ่ม bridge
        super().__init__()
        self.setFixedSize(380, 420)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self.view.setClearColor(Qt.transparent)
        self.setCentralWidget(self.view)

        self.bridge = bridge  # ✅ ต้องเซ็ตตรงนี้ก่อน
        ctx = self.view.rootContext()
        ctx.setContextProperty("splashBridge", self.bridge)

        self.view.setSource(
            QUrl.fromLocalFile(qml_file)
        )  # โหลด QML หลัง setContextProperty

        if self.view.status() != QQuickWidget.Status.Ready:
            print("QML load failed:")
            for err in self.view.errors():
                print(f"{err.toString()}")
            self.close()  # ❗ ปิด splash ถ้าโหลด QML ไม่สำเร็จ

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, "_drag_pos"):
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = event.globalPosition().toPoint()


class SplashBridge(QObject):
    def __init__(self):
        super().__init__()
        self._message = ""

    def getMessage(self):
        return self._message

    def setMessage(self, msg):
        if self._message != msg:
            self._message = msg
            self.messageChanged.emit()

    messageChanged = Signal()
    message = Property(str, getMessage, setMessage, notify=messageChanged)
