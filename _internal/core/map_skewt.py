import datetime
import os
import json
from PIL import Image
from PySide6.QtCore import Qt, Signal, QThread
import fitz  # PyMuPDF สำหรับจัดการ PDF
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPixmap, QImage
from matplotlib import font_manager as fm

import logging

from core.skewt.PlotLine import PlotLine
from core.skewt.PlotMarker import PlotMarker
from core.skewt.PlotText import PlotText
from core.skewt.PlotWnd import PlotWnd

logger = logging.getLogger("MapSkewT")


class MapSkewT(QThread):
    text_update = Signal(str)  # สัญญาณที่ส่งข้อความไปยัง MainWindow
    finished = Signal(str)  # ✅ เพิ่ม signal finished พร้อมส่ง path รูป

    def __init__(self):
        super(MapSkewT, self).__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py

        # ไฟล์ข้อมูลสำหรับใช้ในการ Plot
        self.json_url_skewt_file = os.path.join(
            script_dir, "../data/json/synop_url_skewt.json"
        )

        self.json_data_skewt_file = os.path.join(
            script_dir, "../data/json/synop_data_skewt.json"
        )

        self.skewt_file = os.path.join(script_dir, "../data/pdf/Skew-T-Log-P-Color.pdf")
        self.doc = None  # ตัวแปรสำหรับไฟล์ PDF
        self.temp_file = None  # ตัวแปรสำหรับไฟล์ PDF ชั่วคราว
        self.temp_file_old = None  # ตัวแปรสำหรับเก็บไฟล์เก่า
        self.width = None  # กำหนดความกว้างของภาพ
        self.height = None  # กำหนดความสูงของภาพ
        self.point_marker = None  # ตัวแปรสำหรับเก็บจุด marker

    def run(self, date=None, time=None, station=None, level=None):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py

            # กำหนดชื่อไฟล์ที่ต้องการบันทึก
            output_file = os.path.join(script_dir, "../output/map/skewt.png")
            output_file_2 = os.path.join(script_dir, "../output/map/skewt-600dpi.png")
            output_file_3 = os.path.join(script_dir, "../output/map/pdf/skewt.pdf")

            # โหลดฟอนต์ที่ต้องการใช้
            # กำหนด path สำหรับโหลดฟอนต์ภาษาไทย
            font_path = os.path.join(
                script_dir,
                "../fonts/Noto_Sans_Thai/static/NotoSansThai-Regular.ttf",
            )
            logger.info(f"📜 โหลดฟอนต์จาก: {font_path}")

            font = fm.FontProperties(fname=font_path)
            logger.info(f"📛 ฟอนต์ชื่อว่า:{font.get_name()}")

            """โหลดไฟล์ PDF และแสดงเป็นภาพ"""
            if not self.skewt_file or not os.path.exists(self.skewt_file):
                raise FileNotFoundError(f"ไม่พบไฟล์ skewt: {self.skewt_file}")

            self.doc = fitz.open(self.skewt_file)  # เปิดไฟล์ PDF
            page = self.doc[0]  # โหลดหน้าแรกของ PDF
            self.text_update.emit(f"📄 เปิดไฟล์ PDF: {self.skewt_file}")
            logger.info(f"📄 เปิดไฟล์ PDF: {self.skewt_file}")

            # แปลงหน้า PDF เป็นภาพ
            self.image_item = QGraphicsPixmapItem()  # สร้าง item สำหรับแสดงภาพ

            # สร้างภาพจาก PDF ด้วย DPI สูง (300)
            pix = page.get_pixmap(dpi=300)
            image = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(image)

            self.text_update.emit(f"📸 แปลงหน้า PDF เป็นภาพ: {self.skewt_file}")
            logger.info(f"📸 แปลงหน้า PDF เป็นภาพ: {self.skewt_file}")

            # === บันทึกภาพเป็นไฟล์ PNG ===
            self.image_item.setPixmap(pixmap)  # ตั้งค่าภาพที่จะแสดง
            self.image_item.setTransformationMode(
                Qt.TransformationMode.SmoothTransformation
            )

            self.width = self.image_item.pixmap().width()
            self.height = self.image_item.pixmap().height()

            station_num = station[:5]
            station_name = station[7:11]

            try:
                # แปลงรูปแบบวันที่
                date_obj = datetime.datetime.strptime(date, "%d %b %Y")
                date_key = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                self.text_update.emit(f"❌ รูปแบบวันที่ไม่ถูกต้อง: {date}")
                return

            # โหลดข้อมูล JSON เฉพาะ skewt เท่านั้น
            json_url_skewt_file = self.load_json(self.json_url_skewt_file)
            if not json_url_skewt_file:
                self.text_update.emit("⚠️ ไม่พบข้อมูล URL skewt")
                logger.warning("⚠️ ไม่พบข้อมูล URL skewt")
                return

            data_url = json_url_skewt_file[date_key][station[:5]]

            # โหลดข้อมูล JSON เฉพาะ skewt เท่านั้น
            json_data_skewt_file = self.load_json(self.json_data_skewt_file)
            if not json_data_skewt_file:
                self.text_update.emit("⚠️ ไม่พบข้อมูล skewt")
                logger.warning("⚠️ ไม่พบข้อมูล skewt")
                return

            data_skewt = json_data_skewt_file[date_key][station[:5]]
            try:
                # การเรียกใช้งาน CheckArrayWND
                plotText = PlotText()
                plotText.plotNewsDraw(
                    page,
                    self.width,
                    self.height,
                    station[:5],
                    station[7:11],
                    time,
                    date,
                    data_url["TTAA"],
                    data_url["TTBB"],
                )

                self.text_update.emit(f"✅ PlotText Decoded Successfully")
                logger.info(f"✅ PlotText Decoded Successfully")
            except Exception as e:
                self.append_debugger(f"❌ PlotText Decode Error: {e}")
                logger.error(f"❌ PlotText Decode Error: {e}")
                return

            try:
                # การเรียกใช้งาน PlotMarker
                plotMarker = PlotMarker()
                self.point_marker = plotMarker.plotMakerDraw(
                    page,
                    self.width,
                    self.height,
                    level,
                    data_skewt["TEMP"],
                )

                self.text_update.emit(f"✅ PlotMarker Decoded Successfully")
                logger.info(f"✅ PlotMarker Decoded Successfully")
            except Exception as e:
                self.append_debugger(f"❌ PlotMarker Decode Error: {e}")
                logger.error(f"❌ PlotMarker Decode Error: {e}")
                return

            try:
                # การเรียกใช้งาน PlotLine
                plotLine = PlotLine()
                plotLine.plotLineDraw(
                    page,
                    self.width,
                    self.height,
                    self.point_marker,
                )

                self.text_update.emit(f"✅ PlotLine Decoded Successfully")
                logger.info(f"✅ PlotLine Decoded Successfully")
            except Exception as e:
                self.append_debugger(f"❌ PlotLine Decode Error: {e}")
                logger.error(f"❌ PlotLine Decode Error: {e}")
                return

            try:
                # การเรียกใช้งาน PlotWnd
                plotWnd = PlotWnd()
                plotWnd.plotWndDraw(
                    page,
                    self.width,
                    self.height,
                    level,
                    data_skewt["WIND"],
                )

                self.text_update.emit(f"✅ PlotWnd Decoded Successfully")
                logger.info(f"✅ PlotWnd Decoded Successfully")
            except Exception as e:
                self.append_debugger(f"❌ PlotWnd Decode Error: {e}")
                logger.error(f"❌ PlotWnd Decode Error: {e}")
                return

            # บันทึก PDF ใหม่
            user_profile = os.environ["USERPROFILE"]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            temp_folder = os.path.join(user_profile, "AppData", "Local", "Temp")
            self.temp_file = os.path.join(
                temp_folder,
                f"Skew-T-Temp-{station_num}-{time[0:4]}-{timestamp}.pdf",
            )

            # === บันทึกไฟล์ PNG ที่ DPI 300 ===
            pix_300 = page.get_pixmap(dpi=300)
            pix_300.save(output_file)  # ไม่มี "PNG" เป็น argument, แค่ใส่นามสกุลใน path
            self.text_update.emit(f"🖼️ บันทึกภาพ PNG ที่ 300 DPI สำเร็จ: {output_file}")
            logger.info(f"🖼️ บันทึกภาพ PNG ที่ 300 DPI สำเร็จ: {output_file}")

            # === บันทึกไฟล์ PNG ที่ DPI 600 ===
            # pix_600 = page.get_pixmap(dpi=600)
            # pix_600.save(output_file_2)
            # self.text_update.emit(f"🖼️ บันทึกภาพ PNG ที่ 600 DPI สำเร็จ: {output_file_2}")
            # logger.info(f"🖼️ บันทึกภาพ PNG ที่ 600 DPI สำเร็จ: {output_file_2}")

            # บันทึกไฟล์ PDF
            self.doc.save(output_file_3)
            self.doc.save(self.temp_file)
            self.doc.close()  # ปิดไฟล์ PDF หลังจากบันทึก
            self.text_update.emit(f"📄 บันทึก PDF ใหม่สำเร็จ: {self.temp_file}")
            logger.info(f"📄 บันทึก PDF ใหม่สำเร็จ: {self.temp_file}")

            # ตรวจสอบ
            img = Image.open(output_file)
            logger.info(f"🖼️ Dimensions: {img.size} px")
            logger.info(f"🖼️ DPI: {img.info.get('dpi')}")

            self.finished.emit(output_file)  # ✅ ส่ง path ไฟล์ออกไป
        except Exception as e:
            self.text_update.emit(f"❌ Error during map creation: {e}")
            logger.exception("Error during map creation")

    # === ฟังก์ชันเสริม ===
    def load_json(self, path):
        if not os.path.exists(path):
            self.text_update.emit(f"⚠️ File not found: {path}")
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.text_update.emit(f"⚠️ Failed to load JSON: {e}")
            return {}

    def write_json(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.text_update.emit(f"✅ JSON saved successfully: {path}")
            return True
        except Exception as e:
            self.text_update.emit(f"❌ Failed to write JSON: {e}")
            return False
