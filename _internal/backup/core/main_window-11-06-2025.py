import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import (
    Qt,
    QUrl,
    QDate,
    QPoint,
    QLocale,
    Slot,
    Signal,
    QObject,
    QCoreApplication,
    QTimer,
    QEvent,
)
from PySide6.QtQml import QQmlError

from core.check_array_temp import CheckArrayTEMP
from core.check_array_wind import CheckArrayWND
from core.check_code_aaxx_full import CheckCodeAAXXFull
from core.check_code_aaxx_full_2 import CheckCodeAAXXFull2
from core.check_code_ttaa import CheckCodeTTAA
from core.check_code_ttbb import CheckCodeTTBB
from core.check_code_upper_wind import CheckCodeUpperWind
from core.check_url_detail import CheckURLDetail
from core.check_url_pressure import CheckURLPressure
from core.check_url_skewt import CheckURLSkewT
from core.check_url_surface import CheckURLSurface
from core.check_url_upper_wind import CheckURLUpperWind
from core.plot_manager import PlotManager
from core.splash_sequence_manager import SplashSequenceManager
from core.table_view_skewt import TableViewSkewT
from core.table_view_synoptic import TableViewSynoptic
from core.table_view_upper_wind import TableViewUpperWind
from ui.views.splash_window import SplashBridge
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

import shutil
import os
import json
from datetime import datetime
from PIL import Image
import logging

# ✅ กำหนดค่าเริ่มต้นสำหรับการบันทึก log
logger = logging.getLogger("MainWindow")


class MainWindow(QMainWindow):
    imagePathChanged = Signal(str, str)  # (tab_name, file_url)
    dataCheckURL = Signal(bool)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าอินเทอร์เน็ตเสร็จสิ้นแล้ว
    dataLoadedChanged = Signal(bool)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าข้อมูลโหลดเสร็จแล้ว
    fullscreenChanged = Signal(bool)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าหน้าต่าง fullscreen หรือไม่
    versionLoader = Signal(str)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าเวอร์ชั่นโปรแกรม
    convertA3 = Signal(bool)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าเวอร์ชั่นโปรแกรม

    def __init__(self, splash_bridge: Optional[SplashBridge] = None, vName: str = ""):
        super().__init__()

        # === กำหนดค่าเริ่มต้น ===
        self.surface_data = {}  # เก็บข้อมูลแผนที่พื้นผิว
        self.detail_data = {}  # เก็บข้อมูลแผนที่รายละเอียด
        self.pressure_data = {}  # เก็บข้อมูลแผนที่ความดัน
        self.upperwind1_data = {}  # เก็บข้อมูลแผนที่ลมระดับหลัก
        self.upperwind2_data = {}  # เก็บข้อมูลแผนที่ลมระดับรอง
        self.skewt_data = {}  # เก็บข้อมูลแผนที่เทอร์โมไดนามิก
        self.table_window = None  # เก็บหน้าต่าง TableView

        self._restore_geometry = None  # เก็บตำแหน่งหน้าต่างก่อนขยายเต็มจอ
        self.date_text = ""  # ค่าเริ่มต้นสำหรับ date_text
        self.time_text = ""  # ค่าเริ่มต้นสำหรับ time_text
        self.value_index = 0  # ค่าเริ่มต้นสำหรับ value_index
        self.station_id = ""  # ค่าเริ่มต้นสำหรับ station_id
        self.pressure_level = ""  # ค่าเริ่มต้นสำหรับ pressure_level

        self.surface_text = ""  # ค่าเริ่มต้นสำหรับ surface_text
        self.detail_text = ""  # ค่าเริ่มต้นสำหรับ detail_text
        self.pressure_text = ""  # ค่าเริ่มต้นสำหรับ pressure_text
        self.upperwind1_text = ""  # ค่าเริ่มต้นสำหรับ upperwind1_text
        self.upperwind2_text = ""  # ค่าเริ่มต้นสำหรับ upperwind2_text
        self.skewt_text = ""  # ค่าเริ่มต้นสำหรับ skewt_text

        self.check_open_file_surface = False  # ตัวนับการเปิดไฟล์แผนที่พื้นผิว
        self.check_open_file_detail = False  # ตัวนับการเปิดไฟล์แผนที่รายละเอียด
        self.check_open_file_pressure = False  # ตัวนับการเปิดไฟล์แผนที่ความดัน
        self.check_open_file_upperwind1 = False  # ตัวนับการเปิดไฟล์แผนที่ลมระดับหลัก
        self.check_open_file_upperwind2 = False  # ตัวนับการเปิดไฟล์แผนที่ลมระดับรอง
        self.check_open_file_skewt = False  # ตัวนับการเปิดไฟล์แผนที่เทอร์โมไดนามิก

        self._drag_pos: Optional[QPoint] = None  # ตำแหน่งที่คลิกเมาส์สำหรับลากหน้าต่าง
        self._splash_bridge = splash_bridge  # ใช้สำหรับ splash screen
        self.sequence: Optional[SplashSequenceManager] = (
            None  # ใช้สำหรับจัดการ splash sequence
        )
        self.view: Optional[QQuickWidget] = None  # QML view container
        self.qml_interface = (
            self  # ให้ PlotManager ส่งกลับมาใช้ self.imagePathChanged.emit()
        )
        self.fullscreenChanged.emit(self.isFullScreen())  # เริ่มต้น emit สถานะ fullscreen
        self._setup_splash()  # เริ่มต้น splash sequence ถ้ามี
        self._initialize_app()  # เรียกใช้ฟังก์ชันเริ่มต้นแอปพลิเคชัน

        # ✅ สร้าง QNetworkAccessManager ก่อนใช้
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self._on_connection_checked)

        # ✅ เรียกตรวจสอบการเชื่อมต่อ
        self.check_connection()

        # ✅ ส่งสัญญาณเวอร์ชั่นโปรแกรมให้ QML ทราบ
        self.versionLoader.emit(vName)  # 🔔 ส่งสัญญาณให้ QML รู้ว่าเวอร์ชั่นโปรแกรม
        self.vName = vName

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
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # === ขนาดหน้าต่างพื้นฐาน ===
        base_width = 1470
        base_height = 800

        # === ดึงขนาดหน้าจอที่เปิดโปรแกรมอยู่
        screen = self.screen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        logger.info(f"🖥 Screen size: {screen_width}x{screen_height}")

        # === คำนวณ Scale (ลดขนาดถ้าจอเล็ก)
        scale_factor = 1.0

        if screen_width < 1600 or screen_height < 900:
            scale_factor = (
                min(screen_width / base_width, screen_height / base_height) * 0.95
            )  # ลดลงอีก 5% เผื่อ margin

        new_width = int(base_width * scale_factor)
        new_height = int(base_height * scale_factor)

        # === Set ขนาดหน้าต่างที่ปรับแล้ว
        self.resize(new_width, new_height)

        # === จัดให้อยู่กลางจอ
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        self.move(x, y)

        logger.info(
            f"🪟 Window size: {new_width}x{new_height} (scale factor: {scale_factor:.2f})"
        )

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

    @Slot(str, str, int, str, str, str)
    def plot_map_by_tab(
        self,
        date_text: str = "",
        time_text: str = "",
        value_index: int = 0,
        station_id: str = "",
        pressure_level: str = "",
        tab_name: str = "",
    ):
        self.date_text = QDate.fromString(date_text, "yyyy-MM-dd")
        formatted_date = self.date_text.toString("dd MMM yyyy")  # เช่น "15-May-2025"
        self.date_text = formatted_date
        self.time_text = time_text
        self.value_index = value_index
        self.station_id = station_id
        self.pressure_level = pressure_level

        # ✅ แสดง debug ข้อมูลที่ใช้ plot
        if tab_name == "📈 Skew-T Log-P - อต.ทอ. 1011":
            self.append_debugger(
                f"📅 Date: {self.date_text} | 🕖 Time: {self.time_text} | "
                f"🆔 Station ID: {self.station_id} | "
                f"📏 Pressure Level: {self.pressure_level} | "
                f"📊 Value Index: {self.value_index}"
            )
            logger.info(
                f"📅 Date: {self.date_text} | 🕖 Time: {self.time_text} | "
                f"🆔 Station ID: {self.station_id} | "
                f"📏 Pressure Level: {self.pressure_level} | "
                f"📊 Value Index: {self.value_index}"
            )
        else:
            self.append_debugger(
                f"📅 Date: {self.date_text} | 🕖 Time: {self.time_text} | 📊 Value Index: {self.value_index}"
            )
            logger.info(
                f"📅 Date: {self.date_text} | 🕖 Time: {self.time_text} | 📊 Value Index: {self.value_index}"
            )

        # ✅ ตรวจสอบ tab_name ว่าตรงกับชื่อแท็บที่ต้องการ plot หรือไม่
        self.append_debugger(f"⏳ Plotting {tab_name}...")
        logger.info(f"Plotting map for tab: {tab_name}")

        pm = PlotManager(self)  # สร้างอ็อบเจกต์ PlotManager
        if tab_name == "🗺️ Surface อต.ทอ. 1001":
            pm.plot_surface_and_update_qml(
                self.date_text, self.time_text, self.value_index
            )  # เรียก plot แผนที่พื้นผิว (blank version)

        elif tab_name == "🗺️ Pressure Change อต.ทอ. 1010":
            pm.plot_pressure_and_update_qml(
                self.date_text, self.time_text, self.value_index
            )  # เรียก plot แผนที่ความดัน (blank version)

        elif tab_name == "🗺️ Detail อต.ทอ. 1003":
            pm.plot_detail_and_update_qml(
                self.date_text, self.time_text, self.value_index
            )  # เรียก plot แผนที่ประเทศไทย (blank version)

        elif tab_name == "🗺️ Upper Wind Air - 1 อต.ทอ. 1002":
            pm.plot_wind_1_and_update_qml(
                self.date_text, self.time_text, self.value_index
            )  # เรียก plot แผนที่ลมระดับหลัก (blank version)

        elif tab_name == "🗺️ Upper Wind Air - 2 อต.ทอ. 1013":
            pm.plot_wind_2_and_update_qml(
                self.date_text, self.time_text, self.value_index
            )  # เรียก plot แผนที่ลมระดับรอง (blank version)

        elif tab_name == "📈 Skew-T Log-P - อต.ทอ. 1011":
            pm.plot_skewt_and_update_qml(
                self.date_text, self.time_text, self.station_id, self.pressure_level
            )  # เรียก plot แผนที่เทอร์โมไดนามิก (blank version)

        else:
            logger.warning(f"⚠️ Unrecognized tab name: {tab_name}")
            self.append_debugger(f"⚠️ Unrecognized tab name: {tab_name}")
            return

        # ✅ แจ้ง QML: plot เสร็จแล้ว
        self.append_debugger(f"✅ Plotting {tab_name} successfully.")

    @Slot(str, str, str, int)
    def load_data(
        self,
        date_text: str = "",
        time_text: str = "",
        station_filter: str = "",
        tab_index: int = 0,
    ):
        # ✅ ล้าง debug ก่อน
        self.update_debugger("")
        self.update_debugger(
            f"📦 Loading SYNOP Data by 📅Date: {date_text}|🕖Time: {time_text}"
        )
        logger.info(f"🌏 Loading Data by 📅Date: {date_text}|🕖Time: {time_text}")

        # ✅ เก็บค่า date_text, time_text, value_index
        self.date_text = QDate.fromString(date_text, "yyyy-MM-dd")
        formatted_date = self.date_text.toString("dd MMM yyyy")  # เช่น "15-May-2025"
        self.date_text = formatted_date
        self.time_text = time_text[0:8]

        tab_index = int(tab_index)
        logger.info(f"🗂 Tab index: {tab_index}")

        content = None  # กำหนดค่าเริ่มต้นให้ content เป็น None
        msg = ""  # กำหนดค่าเริ่มต้นให้ msg เป็น string ว่าง

        # ✅ ตรวจสอบว่า tab_index เป็น 0, 1 หรือ 2
        if tab_index == 0:
            self.surface_data = {}
            index = tab_index

            try:
                self.append_debugger(
                    "🔄 Loading surface data from file."
                    if self.check_open_file_surface
                    else "🔄 Loading surface data from URL."
                )
                logger.info(
                    "🔄 Loading surface data from file."
                    if self.check_open_file_surface
                    else "🔄 Loading surface data from URL."
                )

                check = CheckURLSurface()
                content, msg = check.urlGetContent(
                    time_text[0:4],
                    date_text,
                    self.surface_text if self.check_open_file_surface else None,
                )

                self.append_debugger("🟢 CheckURLSurface Complete")
                logger.info("🟢 CheckURLSurface Complete")

            except Exception as e:
                self.append_debugger(f"❌ Error while loading surface data:\n{e}")
                logger.error(f"❌ Error while loading surface data:\n{e}")
                return

            if content != "NIL":
                # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล surface
                Path("data/json/synop_data_surface.json").write_text(
                    "{}", encoding="utf-8"
                )

                decoder = CheckCodeAAXXFull()
                try:
                    if isinstance(content, dict):
                        for d, text in content.items():
                            decoded = decoder.decodeAAXX(text, index, d)
                            self.surface_data[d] = decoded
                    else:
                        # ✅ ห่อให้เป็น dict ก่อนส่งเข้า decode
                        decoded = decoder.decodeAAXX(
                            {date_text: content}, index, save_to_file=True
                        )
                        self.surface_data[date_text] = decoded

                except Exception as e:
                    self.append_debugger(f"❌ Decode Error: {e}")
                    logger.error(f"❌ Decode Error: {e}")
                    return

                # ✅ แสดงผลอย่างปลอดภัย
                self.append_debugger("----------------------------------------")
                if isinstance(content, dict):
                    for d, text in content.items():
                        self.append_debugger(f"📅 {d}\n{text}")
                else:
                    self.append_debugger(content)

                self.append_debugger("----------------------------------------")
                self.append_debugger(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.info(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )

                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดสำเร็จ
                # self.view.rootObject().setProperty("isDataLoaded", True)
                self.dataLoadedChanged.emit(True)

            else:
                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดล้มเหลว
                # self.view.rootObject().setProperty("isDataLoaded", False)
                self.dataLoadedChanged.emit(False)

                self.append_debugger(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.error(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                return

        elif tab_index == 1:
            self.pressure_data = {}
            index = tab_index

            try:
                self.append_debugger(
                    "🔄 Loading pressure data from file."
                    if self.check_open_file_pressure
                    else "🔄 Loading surface data from URL."
                )
                logger.info(
                    "🔄 Loading pressure data from file."
                    if self.check_open_file_pressure
                    else "🔄 Loading pressure data from URL."
                )

                check = CheckURLPressure()
                content, msg = check.urlGetContent(
                    time_text[0:4],
                    date_text,
                    self.pressure_text if self.check_open_file_pressure else None,
                )

                self.append_debugger(f"🟢 CheckURLPressure Complete")
                logger.info(f"🟢 CheckURLPressure Complete")

            except Exception as e:
                self.append_debugger(f"❌ Error while loading pressure data:\n{e}")
                logger.error(f"❌ Error while loading pressure data:\n{e}")
                return

            if content != "NIL":
                # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล pressure
                Path("data/json/synop_data_pressure.json").write_text(
                    "{}", encoding="utf-8"
                )

                decoder = CheckCodeAAXXFull2()

                try:
                    # ✅ ห่อ content เป็น dict เสมอ (เพื่อรองรับทั้ง dict และ str)
                    if not isinstance(content, dict):
                        content = {date_text: content}

                    decoded = decoder.decodeAAXX(content, index, save_to_file=True)
                    # self.pressure_data.update({d["date"]: d for d in decoded})
                    for d in decoded:
                        date = d["date"]
                        if date not in self.pressure_data:
                            self.pressure_data[date] = []
                        self.pressure_data[date].append(d)

                except Exception as e:
                    self.append_debugger(f"❌ Decode Error: {e}")
                    logger.error(f"❌ Decode Error: {e}")
                    return

                # ✅ แสดงผลอย่างปลอดภัย
                self.append_debugger("----------------------------------------")
                if isinstance(content, dict):
                    for d, text in content.items():
                        self.append_debugger(f"📅 {d} >>>>>>>>>>>>>>>>>>\n{text}")
                else:
                    self.append_debugger(content)

                self.append_debugger("----------------------------------------")
                self.append_debugger(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.info(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )

                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดสำเร็จ
                # self.view.rootObject().setProperty("isDataLoaded", True)
                self.dataLoadedChanged.emit(True)

            else:
                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดล้มเหลว
                # self.view.rootObject().setProperty("isDataLoaded", False)
                self.dataLoadedChanged.emit(False)

                self.append_debugger(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.error(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                return

        elif tab_index == 2:
            self.detail_data = {}
            index = tab_index

            try:
                self.append_debugger(
                    "🔄 Loading detail data from file."
                    if self.check_open_file_detail
                    else "🔄 Loading detail data from URL."
                )
                logger.info(
                    "🔄 Loading detail data from file."
                    if self.check_open_file_detail
                    else "🔄 Loading detail data from URL."
                )

                check = CheckURLDetail()
                content, msg = check.urlGetContent(
                    time_text[0:4],
                    date_text,
                    self.detail_text if self.check_open_file_detail else None,
                )

                self.append_debugger(f"🟢 CheckURLDetail Complete")
                logger.info(f"🟢 CheckURLDetail Complete")

            except Exception as e:
                self.append_debugger(f"❌ Error while loading detail data:\n{e}")
                logger.error(f"❌ Error while loading detail data:\n{e}")
                return

            if content != "NIL":
                # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล detail
                Path("data/json/synop_data_detail.json").write_text(
                    "{}", encoding="utf-8"
                )

                decoder = CheckCodeAAXXFull()

                try:
                    if isinstance(content, dict):
                        for d, text in content.items():
                            decoded = decoder.decodeAAXX(text, index, d)
                            self.detail_data[d] = decoded
                    else:
                        # ✅ ห่อให้เป็น dict ก่อนส่งเข้า decode
                        decoded = decoder.decodeAAXX(
                            {date_text: content}, index, save_to_file=True
                        )
                        self.detail_data[date_text] = decoded

                except Exception as e:
                    self.append_debugger(f"❌ Decode Error: {e}")
                    logger.error(f"❌ Decode Error: {e}")
                    return

                # ✅ แสดงผลอย่างปลอดภัย
                self.append_debugger("----------------------------------------")
                if isinstance(content, dict):
                    for d, text in content.items():
                        self.append_debugger(f"📅 {d}\n{text}")
                else:
                    self.append_debugger(content)

                self.append_debugger("----------------------------------------")
                self.append_debugger(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.info(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )

                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดสำเร็จ
                # self.view.rootObject().setProperty("isDataLoaded", True)
                self.dataLoadedChanged.emit(True)

            else:
                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดล้มเหลว
                # self.view.rootObject().setProperty("isDataLoaded", False)
                self.dataLoadedChanged.emit(False)

                self.append_debugger(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.error(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                return

        elif tab_index == 3:
            self.upperwind1_data = {}
            index = tab_index

            try:
                self.append_debugger(
                    "🔄 Loading upperwind1 data from file."
                    if self.check_open_file_upperwind1
                    else "🔄 Loading upperwind1 data from URL."
                )
                logger.info(
                    "🔄 Loading upperwind1 data from file."
                    if self.check_open_file_upperwind1
                    else "🔄 Loading upperwind1 data from URL."
                )

                check = CheckURLUpperWind()
                content, msg = check.urlGetContent(
                    time_text[0:4],
                    date_text,
                    self.upperwind1_text if self.check_open_file_upperwind1 else None,
                )

                self.append_debugger(f"🟢 CheckURLUpperWind Complete")
                logger.info(f"🟢 CheckURLUpperWind Complete")

            except Exception as e:
                self.append_debugger(f"❌ Error while loading upperwind data:\n{e}")
                logger.error(f"❌ Error while loading upperwind data:\n{e}")
                return

            if content != "NIL":
                # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล upperwind1
                Path("data/json/synop_data_upperwind_1.json").write_text(
                    "{}", encoding="utf-8"
                )

                decoder = CheckCodeUpperWind()

                try:
                    decoded = decoder.decode_from_dict(
                        content, time=time_text, date=date_text
                    )
                    self.upperwind1_data[date_text] = decoded

                    # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล upperwind1
                    with open(
                        "data/json/synop_data_upperwind_1.json", "w", encoding="utf-8"
                    ) as f:
                        json.dump(self.upperwind1_data, f, ensure_ascii=False, indent=2)

                    # decoder.save_decoded_to_json(
                    #    {date_text: decoded}, time_text, date_text
                    # )

                except Exception as e:
                    self.append_debugger(f"❌ Decode Error: {e}")
                    logger.error(f"❌ Decode Error: {e}")

                # ✅ แสดงผลอย่างปลอดภัย
                self.append_debugger("----------------------------------------")
                if isinstance(content, dict):
                    for d, text in content.items():
                        self.append_debugger(f"🆔 {d}\n{text}")
                else:
                    self.append_debugger(content)

                self.append_debugger("----------------------------------------")
                self.append_debugger(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.info(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )

                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดสำเร็จ
                # self.view.rootObject().setProperty("isDataLoaded", True)
                self.dataLoadedChanged.emit(True)

            else:
                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดล้มเหลว
                # self.view.rootObject().setProperty("isDataLoaded", False)
                self.dataLoadedChanged.emit(False)

                self.append_debugger(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.error(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                return

        elif tab_index == 4:
            self.upperwind2_data = {}
            index = tab_index

            try:
                self.append_debugger(
                    "🔄 Loading upperwind2 data from file."
                    if self.check_open_file_upperwind2
                    else "🔄 Loading upperwind2 data from URL."
                )
                logger.info(
                    "🔄 Loading upperwind2 data from file."
                    if self.check_open_file_upperwind2
                    else "🔄 Loading upperwind2 data from URL."
                )

                check = CheckURLUpperWind()
                content, msg = check.urlGetContent(
                    time_text[0:4],
                    date_text,
                    self.upperwind2_text if self.check_open_file_upperwind2 else None,
                )
                self.append_debugger(f"🟢 CheckURLUpperWind Complete")
                logger.info(f"🟢 CheckURLUpperWind Complete")

            except Exception as e:
                self.append_debugger(f"❌ Error while loading detail data:\n{e}")
                logger.error(f"❌ Error while loading detail data:\n{e}")
                return

            if content != "NIL":
                # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล upperwind2
                Path("data/json/synop_data_upperwind_2.json").write_text(
                    "{}", encoding="utf-8"
                )

                # ✅ การเรียกใช้งาน CheckCodeUpperWind
                decoder = CheckCodeUpperWind()

                try:
                    decoded = decoder.decode_from_dict(
                        content, time=time_text, date=date_text
                    )
                    self.upperwind2_data[date_text] = decoded
                    # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล upperwind2
                    with open(
                        "data/json/synop_data_upperwind_2.json", "w", encoding="utf-8"
                    ) as f:
                        json.dump(self.upperwind2_data, f, ensure_ascii=False, indent=2)

                    # ✅ Save JSON สำหรับกรณีแค่วันเดียว
                    # decoder.save_decoded_to_json(
                    #    {date_text: decoded}, time_text, date_text
                    # )

                except Exception as e:
                    self.append_debugger(f"❌ Decode Error: {e}")
                    logger.error(f"❌ Decode Error: {e}")

                # ✅ แสดงผลอย่างปลอดภัย
                self.append_debugger("----------------------------------------")
                if isinstance(content, dict):
                    for d, text in content.items():
                        self.append_debugger(f"🆔 {d}\n{text}")
                else:
                    self.append_debugger(content)

                self.append_debugger("----------------------------------------")
                self.append_debugger(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.info(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )

                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดสำเร็จ
                # self.view.rootObject().setProperty("isDataLoaded", True)
                self.dataLoadedChanged.emit(True)

            else:
                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดล้มเหลว
                # self.view.rootObject().setProperty("isDataLoaded", False)
                self.dataLoadedChanged.emit(False)

                self.append_debugger(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.error(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                return

        elif tab_index == 5:
            self.skewt_data = {}
            index = tab_index

            try:
                self.append_debugger(
                    "🔄 Loading skewt data from file."
                    if self.check_open_file_skewt
                    else "🔄 Loading skewt data from URL."
                )
                logger.info(
                    "🔄 Loading skewt data from file."
                    if self.check_open_file_skewt
                    else "🔄 Loading skewt data from URL."
                )

                check = CheckURLSkewT()
                content, msg = check.urlGetContent(
                    time_text[0:4],
                    date_text,
                    station_filter[0:5],
                    self.skewt_text if self.check_open_file_skewt else None,
                )

                # logger.info(f"🌐 DEBUG: content={content}")
                self.append_debugger(f"🟢 CheckURLUpperWind Complete")
                logger.info(f"🟢 CheckURLUpperWind Complete")

            except Exception as e:
                self.append_debugger(f"❌ Error while loading detail data:\n{e}")
                logger.error(f"❌ Error while loading detail data:\n{e}")
                return

            if content != "NIL":
                # ✅ สร้างไฟล์ JSON สำหรับเก็บข้อมูล skewt
                Path("data/json/synop_data_skewt.json").write_text(
                    "{}", encoding="utf-8"
                )

                try:
                    # การเรียกใช้งาน CheckCodeTTAA
                    decode_ttaa = CheckCodeTTAA()
                    resultTTAA = decode_ttaa.decodeTTAA(
                        content[station_filter[0:5]]["TTAA"]
                    )
                    # logger.info(f"✅ TTAA Decoded: {resultTTAA}")

                except Exception as e:
                    self.append_debugger(f"❌ TTAA Decode Error: {e}")
                    logger.error(f"❌ TTAA Decode Error: {e}")
                    return

                try:
                    # การเรียกใช้งาน CheckCodeTTBB
                    decode_ttbb = CheckCodeTTBB()
                    resultTTBB = decode_ttbb.decodeTTBB(
                        content[station_filter[0:5]]["TTBB"]
                    )
                    # logger.info(f"✅ TTBB Decoded: {resultTTBB}")

                except Exception as e:
                    self.append_debugger(f"❌ TTBB Decode Error: {e}")
                    logger.error(f"❌ TTBB Decode Error: {e}")
                    return

                try:
                    # การเรียกใช้งาน CheckArrayTEMP
                    decode_temp = CheckArrayTEMP()
                    resultArrayTEMP = decode_temp.decodeArrayTEMP(
                        resultTTAA["temp"], resultTTBB["temp"]
                    )
                    # logger.info(f"✅ TEMP Decoded: {resultArrayTEMP}")

                except Exception as e:
                    self.append_debugger(f"❌ TEMP Decode Error: {e}")
                    logger.error(f"❌ TEMP Decode Error: {e}")
                    return

                try:
                    # การเรียกใช้งาน CheckArrayWND
                    decode_wnd = CheckArrayWND()
                    resultArrayWND = decode_wnd.decodeArrayWND(
                        resultTTAA["wnd"], resultTTBB["wnd"]
                    )
                    # logger.info(f"✅ WIND Decoded: {resultArrayWND}")

                except Exception as e:
                    self.append_debugger(f"❌ WIND Decode Error: {e}")
                    logger.error(f"❌ WIND Decode Error: {e}")
                    return

                try:
                    # ข้อมูลทั่วไป
                    station_id = station_filter[0:5]
                    date_str = date_text
                    time_str = time_text
                    timestamp = f"{datetime.now().isoformat()}LST"

                    # สร้างโครงสร้าง JSON
                    output_json = {
                        date_str: {
                            "time": time_str,
                            "timestamp": timestamp,
                            station_id: {
                                "TEMP": resultArrayTEMP,
                                "WIND": resultArrayWND,
                            },
                        }
                    }

                    self.skewt_data = output_json
                    # logger.info(f"✅ Skew-T Data: {output_json}")

                    # ✅ บันทึกลงไฟล์ JSON
                    script_dir = os.path.dirname(
                        os.path.abspath(__file__)
                    )  # ตำแหน่งไฟล์ .py
                    output_path = os.path.join(
                        script_dir, "../../data/json/synop_data_skewt.json"
                    )

                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(output_json, f, indent=2, ensure_ascii=False)

                    self.append_debugger(f"✅ JSON saved to {output_path}")
                    logger.info(f"✅ JSON saved to {output_path}")

                except Exception as e:
                    self.append_debugger(f"❌ JSON Save Error: {e}")
                    logger.error(f"❌ JSON Save Error: {e}")
                    return

                # ✅ แสดงผลอย่างปลอดภัย
                self.append_debugger("----------------------------------------")
                if isinstance(content, dict):
                    for d, text in content.items():
                        self.append_debugger(f"🆔 {d}\n{text}")
                else:
                    self.append_debugger(content)

                self.append_debugger("----------------------------------------")
                self.append_debugger(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.info(
                    f"🟢 Checking synoptic data: {date_text} | {time_text}: {msg}"
                )

                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดสำเร็จ
                # self.view.rootObject().setProperty("isDataLoaded", True)
                self.dataLoadedChanged.emit(True)

            else:
                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # เมื่อโหลดล้มเหลว
                # self.view.rootObject().setProperty("isDataLoaded", False)
                self.dataLoadedChanged.emit(False)

                self.append_debugger(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                logger.error(
                    f"❌ Checking synoptic data: {date_text} | {time_text}: {msg}"
                )
                return

        else:
            self.view.rootObject().setProperty("isDataLoaded", False)
            self.append_debugger(f"❌ Error: Invalid tab index {tab_index}.")
            logger.error(f"❌ Error: Invalid tab index {tab_index}.")
            return

    @Slot(int)
    def table_view(self, tab_index: int = 0):
        # 🟡 เปิดหน้าต่าง Table Viewer
        index = tab_index
        tab_names = [
            "Surface อต.ทอ. 1001",
            "Pressure Change อต.ทอ. 1010",
            "Detail อต.ทอ. 1003",
            "Upper Wind Air - 1 อต.ทอ. 1002",
            "Upper Wind Air - 2 อต.ทอ. 1013",
            "Skew-T Log-P Diagram - อต.ทอ. 1011",
        ]

        self.append_debugger(f"📊 Opening Table Viewer: {tab_names[index]}")
        logger.info(f"📊 Opening Table Viewer: {tab_names[index]}")

        data_sources = [
            getattr(self, "surface_data", {}),
            getattr(self, "pressure_data", {}),
            getattr(self, "detail_data", {}),
            getattr(self, "upperwind1_data", {}),
            getattr(self, "upperwind2_data", {}),
            getattr(self, "skewt_data", {}),
        ]

        try:
            raw_data = data_sources[index]
            tab_name = tab_names[index]

            if index in [0, 1, 2]:  # Surface / Pressure / Detail
                data = self._flatten_by_date(raw_data)
                self.table_window = TableViewSynoptic(tab_name=tab_name, data=data)

            elif index in [3, 4]:  # Upper Wind
                self.table_window = TableViewUpperWind(tab_name=tab_name, data=raw_data)
                # print("🌐 DEBUG:", raw_data)
            elif index == 5:  # Skew-T
                self.table_window = TableViewSkewT(tab_name=tab_name, data=raw_data)
            #    return

            self.table_window.show()

        except Exception as e:
            self.append_debugger(f"❌ TableView Error: {e}")
            logger.error(f"❌ TableView Error: {e}")
            return

    def _flatten_by_date(self, raw_data: dict) -> list:
        """
        แปลงข้อมูล dict[date] => list[dict พร้อม date]
        """
        data = []
        for date_str, entries in raw_data.items():
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict):
                        row = entry.copy()
                        row["date"] = date_str
                        data.append(row)
                    else:
                        logger.warning(
                            f"⚠️ Invalid entry type: {type(entry)} for {date_str}"
                        )
            else:
                logger.warning(f"⚠️ Expected list, got {type(entries)} at {date_str}")
        return data

    @Slot(str, str, str, int)
    def save_pdf(
        self,
        date_text: str = "",
        time_text: str = "",
        station_id: str = "",
        tab_index: int = 0,
    ):
        # 🟡 บันทึกเป็น PNG
        index = tab_index
        tab_names = [
            "Surface Map",
            "Pressure Change Map",
            "Detail Map",
            "Upper Wind Air - 1 Map",
            "Upper Wind Air - 2 Map",
            "Skew-T Log-P Diagram Map",
        ]

        self.append_debugger(f"📄 Saving as PDF: {tab_names[index]}")
        logger.info(f"📄 Saving as PDF: {tab_names[index]}")

        # 📍 เปิด dialog ให้ผู้ใช้เลือก path สำหรับบันทึกไฟล์
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Save PDF - {tab_names[index]}",
            f"{tab_names[index].replace(' ', '_')}_{station_id[0:5]}_{date_text}_{time_text[0:4]}UTC.pdf",
            "PDF Files (*.pdf)",
        )

        if not file_path:  # ตรวจสอบว่าผู้ใช้เลือกไฟล์หรือไม่
            self.append_debugger("❌ การบันทึกถูกยกเลิก")
            logger.info("❌ การบันทึกถูกยกเลิก")
            return

        if index in [0, 1, 2, 3, 4]:
            self.append_debugger("❌ SkewT ไม่สามารถบันทึกเป็นไฟล์ PDF")
            logger.info("❌ SkewT ไม่สามารถบันทึกเป็นไฟล์ PDF")
            return
        else:
            # 🔸 สำหรับแท็บอื่น
            # 📍 หา path ปัจจุบันของไฟล์ .py นี้
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # logger.info(f"📂 Current script directory: {script_dir}")

            # ✅ สร้างรายการ path สำหรับไฟล์ปลายทาง
            destination_files = [
                os.path.join(script_dir, "../../output/map/pdf/surface.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/pressure.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/detail.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/upperwind1.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/upperwind2.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/skewt.pdf"),
            ]
            # logger.info(f"📂 Destination files: {destination_files}")

            source_file = destination_files[index]
            if os.path.exists(source_file):
                try:
                    shutil.copy(source_file, file_path)
                    self.append_debugger(f"📄 Saving as PDF: {file_path}")
                    logger.info(f"📄 Saving as PDF: {file_path}")
                except Exception as e:
                    self.append_debugger(f"❌ เกิดข้อผิดพลาดในการบันทึก PDF: {e}")
                    logger.error(f"❌ เกิดข้อผิดพลาดในการบันทึก PDF: {e}")
            else:
                self.append_debugger(f"❌ ไม่พบไฟล์ต้นฉบับสำหรับแท็บ {tab_names[index]}")
                logger.error(f"❌ ไม่พบไฟล์ต้นฉบับสำหรับแท็บ {tab_names[index]}")
                return

    @Slot(str, str, int)
    def save_png(
        self,
        date_text: str = "",
        time_text: str = "",
        tab_index: int = 0,
    ):
        # 🟡 บันทึกเป็น PNG
        index = tab_index
        tab_names = [
            "Surface Map",
            "Pressure Change Map",
            "Detail Map",
            "Upper Wind Air - 1 Map",
            "Upper Wind Air - 2 Map",
            "Skew-T Log-P Diagram Map",
        ]

        self.append_debugger(f"📸 Saving as PNG: {tab_names[index]}")
        logger.info(f"📸 Saving as PNG: {tab_names[index]}")

        # 📍 เปิด dialog ให้ผู้ใช้เลือก path สำหรับบันทึกไฟล์
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Save PNG - {tab_names[index]}",
            f"{tab_names[index].replace(' ', '_')}_{date_text}_{time_text[0:4]}UTC.png",
            "PNG Files (*.png)",
        )

        if not file_path:  # ตรวจสอบว่าผู้ใช้เลือกไฟล์หรือไม่
            self.append_debugger("❌ การบันทึกถูกยกเลิก")
            logger.info("❌ การบันทึกถูกยกเลิก")
            return

        if index == 5:
            self.append_debugger("❌ SkewT ไม่สามารถบันทึกเป็นรูปภาพ")
            logger.info("❌ SkewT ไม่สามารถบันทึกเป็นรูปภาพ")
            return
        else:
            # 🔸 สำหรับแท็บอื่น
            # 📍 หา path ปัจจุบันของไฟล์ .py นี้
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # logger.info(f"📂 Current script directory: {script_dir}")

            # ✅ สร้างรายการ path สำหรับไฟล์ปลายทาง
            destination_files = [
                os.path.join(script_dir, "../../output/map/surface.png"),
                os.path.join(script_dir, "../../output/map/pressure.png"),
                os.path.join(script_dir, "../../output/map/detail.png"),
                os.path.join(script_dir, "../../output/map/upperwind1.png"),
                os.path.join(script_dir, "../../output/map/upperwind2.png"),
                os.path.join(script_dir, "../../output/map/skewt.png"),
            ]
            # logger.info(f"📂 Destination files: {destination_files}")

            source_file = destination_files[index]
            if os.path.exists(source_file):
                try:
                    shutil.copy(source_file, file_path)
                    self.append_debugger(f"📸 Saving as PNG: {file_path}")
                    logger.info(f"📸 Saving as PNG: {file_path}")
                except Exception as e:
                    self.append_debugger(f"❌ เกิดข้อผิดพลาดในการบันทึก PNG: {e}")
                    logger.error(f"❌ เกิดข้อผิดพลาดในการบันทึก PNG: {e}")
            else:
                self.append_debugger(f"❌ ไม่พบไฟล์ต้นฉบับสำหรับแท็บ {tab_names[index]}")
                logger.error(f"❌ ไม่พบไฟล์ต้นฉบับสำหรับแท็บ {tab_names[index]}")
                return

    @Slot(int)
    def open_text_file(self, tab_index: int = 0):
        # 🟡 เปิดไฟล์ข้อความ
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt)"
        )

        if not file_path:  # ตรวจสอบว่าผู้ใช้เลือกไฟล์หรือไม่
            self.append_debugger("❌ การบันทึกถูกยกเลิก")
            logger.info("❌ การบันทึกถูกยกเลิก")
            return

        self.append_debugger(f"📂 Opening text file: {file_path}")
        logger.info(f"📂 Opening text file: {file_path}")

        content = ""
        index = tab_index

        # ✅ ตรวจสอบว่า tab_index เป็น int และอยู่ในช่วงที่ถูกต้อง
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()  # ✅ อ่านเนื้อหาไฟล์จริง ๆ

                if not content.strip():  # ✅ ตรวจสอบว่าไฟล์ไม่ว่างเปล่า
                    self.append_debugger("❌ ไฟล์ว่างเปล่า")
                    logger.error("❌ ไฟล์ว่างเปล่า")

                else:
                    # แยกเก็บข้อมูลตามแท็บ
                    if index == 0:
                        self.surface_text = content
                        self.check_open_file_surface = True
                    elif index == 1:
                        self.pressure_text = content
                        self.check_open_file_pressure = True
                    elif index == 2:
                        self.detail_text = content
                        self.check_open_file_detail = True
                    elif index == 3:
                        self.upperwind1_text = content
                        self.check_open_file_upperwind1 = True
                    elif index == 4:
                        self.upperwind2_text = content
                        self.check_open_file_upperwind2 = True
                    elif index == 5:
                        self.skewt_text = content
                        self.check_open_file_skewt = True

                self.update_debugger(f"📂 Opened: {file_path}\n-----------\n{content}")
                logger.info(f"📂 Opened: {file_path}")

                # ✅ อัปเดต QML ว่าข้อมูลโหลดเสร็จแล้ว
                # self.view.rootObject().setProperty("dataCheckURL", True)
                self.dataCheckURL.emit(True)

            except Exception as e:
                self.append_debugger(f"❌ Error reading file: {e}")
                logger.error(f"❌ Error reading file: {e}")

    def update_debugger(self, message: str):
        # 🟡 อัปเดตข้อความใน debugger
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
        # ✅ ถ้า current ไม่มีข้อความ → ใช้ข้อความใหม่เลย
        if not current or current.strip() == "":
            combined = new_line
        else:
            combined = f"{current}\n{new_line}"

        # ✅ อัปเดตข้อความใน QML
        debug_area.setProperty("text", combined)

    def update_image_source(self, tab_name: str, file_url: str):
        self.imagePathChanged.emit(tab_name, file_url)

    @Slot()
    def check_connection(self):
        url = QUrl("http://www.gts.tmd.go.th/")
        request = QNetworkRequest(url)
        self.append_debugger("🌐 Checking connection to TMD website...")
        self.manager.head(request)  # ไม่ต้องเก็บ reply ไว้ตรงนี้

    @Slot(QNetworkReply)
    def _on_connection_checked(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            self.append_debugger(
                "🟢 Connection successful to TMD website: http://www.gts.tmd.go.th/"
            )
            logger.info(
                "🟢 Connection successfuly to TMD website: http://www.gts.tmd.go.th/"
            )
            self.dataCheckURL.emit(True)

        else:
            self.append_debugger(f"❌ Connection failed: {reply.errorString()}")
            logger.error(f"❌ Connection failed: {reply.errorString()}")
            self.dataCheckURL.emit(False)

        reply.deleteLater()

    @Slot(int)
    def convert_a3(self, tab_index: int = 0):
        # 🟡 Convert to PDF A3
        index = tab_index
        tab_names = [
            "Surface Map",
            "Pressure Change Map",
            "Detail Map",
            "Upper Wind Air - 1 Map",
            "Upper Wind Air - 2 Map",
            "Skew-T Log-P Diagram Map",
        ]

        self.append_debugger(f"⏳ Convert A3: {tab_names[index]}")
        logger.info(f"⏳ Convert A3: {tab_names[index]}")

        map_name = ""
        if index == 3:
            map_name = "upperwind1"
        elif index == 4:
            map_name = "upperwind2"
        else:
            map_name = "unknow"

        # ตำแหน่งไฟล์ .py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, "../../output/map/" + map_name + ".png")
        output_file_1 = os.path.join(
            script_dir, "../../output/map/pdf/" + map_name + ".pdf"
        )
        output_file_2 = os.path.join(
            script_dir, "../../output/map/" + map_name + "_891x420mm_300dpi.png"
        )

        # 🔧 กำหนดไฟล์ภาพต้นฉบับ
        img = Image.open(output_file)
        if not os.path.exists(output_file):
            self.append_debugger(f"❌ ไม่พบไฟล์ภาพ: {output_file}")
            logger.error(f"❌ ไม่พบไฟล์ภาพ: {output_file}")
            return

        # ขนาด A3 แนวตั้ง × 3 แผ่น "mm": (891, 420), "inch": (35.08, 16.54), "px_300dpi": (10524, 4961) ที่ 300 DPI
        target_size_a3 = (10524, 4961)

        # ขยายแบบคุณภาพสูง
        resized_img_a3 = img.resize(target_size_a3, Image.Resampling.LANCZOS)

        # บันทึกเป็น PNG พร้อม DPI 300
        resized_img_a3.save(output_file_2, dpi=(300, 300))

        # 🔧 กำหนดไฟล์ภาพต้นฉบับ (ควรมีขนาดสูงประมาณ 14,883 px สำหรับ 3 หน้า A3 แนวตั้ง)
        img_a3 = Image.open(output_file_2)

        # === ขนาด A3 แนวตั้งที่ 300 DPI ===
        page_width = 3508
        page_height = 4961

        # ตรวจสอบขนาดภาพ
        width, height = img_a3.size
        self.append_debugger(f"✅ Original size 891x420mm: {img_a3.size}")
        logger.info(
            f"✅ Original size 891x420mm: {img_a3.size}"
        )  # ตัวอย่าง: (3508, 14883)

        # ตรวจสอบก่อนว่าความกว้างพอสำหรับตัด 3 หน้า
        pages = []  # ✅ กำหนดล่วงหน้า
        if width < page_width * 3:
            self.append_debugger("❌ ความกว้างของภาพไม่พอสำหรับ 3 หน้าแนวตั้ง")
            logger.info("❌ ความกว้างของภาพไม่พอสำหรับ 3 หน้าแนวตั้ง")
            return

        else:
            # === ตัดออกเป็น 3 ส่วนแนวตั้ง (ปลอดภัยต่อภาพไม่ครบ)
            for i in range(3):
                left = i * page_width
                right = min(left + page_width, width)
                self.append_debugger(f"🔪 Cutting page {i+1}: {left}px to {right}px")
                logger.info(f"🔪 Cutting page {i+1}: {left}px to {right}px")

                cropped = img_a3.crop((left, 0, right, height))
                cropped = cropped.resize(
                    (page_width, page_height)
                )  # ✅ ปรับให้เท่ากันทุกหน้า
                # cropped.save(f"page_{i+1}.png")
                pages.append(cropped.convert("RGB"))

            # === รวมเป็น PDF 3 หน้า
            if pages:
                pages[0].save(output_file_1, save_all=True, append_images=pages[1:])
                self.convertA3.emit(True)
                self.append_debugger(f"✅ PDF created: {output_file_1}")
                logger.info(f"✅ PDF created: {output_file_1}")
            else:
                self.convertA3.emit(False)
                self.append_debugger("❌ No valid pages to save!")
                logger.error("❌ No valid pages to save!")
                return

    @Slot(str, str, int)
    def save_a3(self, date_text: str = "", time_text: str = "", tab_index: int = 0):
        # 🟡 Convert to PDF A3
        index = tab_index
        tab_names = [
            "Surface Map",
            "Pressure Change Map",
            "Detail Map",
            "Upper Wind Air - 1 Map",
            "Upper Wind Air - 2 Map",
            "Skew-T Log-P Diagram Map",
        ]

        self.append_debugger(f"⏳ Save File PDF A3: {tab_names[index]}")
        logger.info(f"⏳ Save File PDF A3: {tab_names[index]}")

        # 📍 เปิด dialog ให้ผู้ใช้เลือก path สำหรับบันทึกไฟล์
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Save PDF A3 - {tab_names[index]}",
            f"{tab_names[index].replace(' ', '_')}_{date_text}_{time_text[0:4]}UTC_A3.pdf",
            "PDF Files (*.pdf)",
        )

        if not file_path:  # ตรวจสอบว่าผู้ใช้เลือกไฟล์หรือไม่
            self.append_debugger("❌ การบันทึกถูกยกเลิก")
            logger.info("❌ การบันทึกถูกยกเลิก")
            return

        else:
            # 🔸 สำหรับแท็บอื่น
            # 📍 หา path ปัจจุบันของไฟล์ .py นี้
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # logger.info(f"📂 Current script directory: {script_dir}")

            # ✅ สร้างรายการ path สำหรับไฟล์ปลายทาง
            destination_files = [
                os.path.join(script_dir, "../../output/map/pdf/surface.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/pressure.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/detail.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/upperwind1.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/upperwind2.pdf"),
                os.path.join(script_dir, "../../output/map/pdf/skewt.pdf"),
            ]
            # logger.info(f"📂 Destination files: {destination_files}")

            source_file = destination_files[index]
            if os.path.exists(source_file):
                try:
                    shutil.copy(source_file, file_path)
                    self.append_debugger(f"📄 Saving as PDF: {file_path}")
                    logger.info(f"📄 Saving as PDF: {file_path}")
                except Exception as e:
                    self.append_debugger(f"❌ เกิดข้อผิดพลาดในการบันทึก PDF: {e}")
                    logger.error(f"❌ เกิดข้อผิดพลาดในการบันทึก PDF: {e}")
                    return
            else:
                self.append_debugger(f"❌ ไม่พบไฟล์ต้นฉบับสำหรับแท็บ {tab_names[index]}")
                logger.error(f"❌ ไม่พบไฟล์ต้นฉบับสำหรับแท็บ {tab_names[index]}")
                return
