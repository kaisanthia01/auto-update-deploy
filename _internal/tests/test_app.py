from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLocale
from PySide6.QtGui import QFontDatabase, QFont
from ui.views.login_window import LoginWindow
from ui.views.main_window import MainWindow

# ✅ Logging setup
import io
import sys
import logging


class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        # Use utf-8 wrapper around stdout
        super().__init__(
            stream or io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        )


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


def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Meteorological Plotting System")
        app.setOrganizationName("AWSS-MPS")

        # ✅ Load Thai font globally
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

        # ✅ Launch login window
        #logger.info("Launching login window")
        #login = LoginWindow("ui/qml/LoginWindow.qml")
        #login.show()

        main = MainWindow()
        main.show()

        sys.exit(app.exec())

    except Exception as e:
        logger.exception("Fatal error occurred")
        QMessageBox.critical(None, "Fatal Error", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
