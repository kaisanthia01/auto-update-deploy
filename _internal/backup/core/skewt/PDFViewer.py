import fitz  # PyMuPDF สำหรับจัดการ PDF
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent, QWheelEvent, QTransform
from controls.PDFWorker import PDFWorker  # นำเข้า Class จากโฟลเดอร์ PDFWorker


class PDFViewer(QGraphicsView):
    """Widget สำหรับแสดงภาพ PDF และรองรับ Zoom In/Out + Mouse Drag"""

    def __init__(self, main_window, splash=None):
        super().__init__()
        self.main_window = main_window  # ✅ เชื่อม PDFViewer กับ MainWindow
        self.splash = splash
        self.scene = QGraphicsScene()  # สร้าง scene สำหรับแสดงภาพ
        self.setScene(self.scene)

        self.image_item = QGraphicsPixmapItem()  # สร้าง item สำหรับแสดงภาพ
        self.scene.addItem(self.image_item)

        self.scale_factor = 0.124  # ค่าซูมเริ่มต้น
        self.min_scale = 0.05  # ค่าซูมขั้นต่ำ
        self.max_scale = 5.0  # ค่าซูมสูงสุด

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.last_mouse_pos = None  # ตัวแปรสำหรับติดตามตำแหน่งเมาส์
        self.doc = None  # ตัวแปรสำหรับไฟล์ PDF
        self.temp_file = None  # ตัวแปรสำหรับไฟล์ PDF ชั่วคราว
        self.temp_file_old = None  # ตัวแปรสำหรับเก็บไฟล์เก่า

    def load_pdf(self, pdf_path):
        if self.splash:
            self.splash.label.setText("📄 Setting up PDF Files")
            QApplication.processEvents()
        
        """โหลดไฟล์ PDF และแสดงเป็นภาพ"""
        self.doc = fitz.open(pdf_path)  # เปิดไฟล์ PDF
        page = self.doc[0]  # โหลดหน้าแรกของ PDF
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
        self.image_item.setPixmap(pixmap)  # ตั้งค่าภาพที่จะแสดง
        self.image_item.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )
        self.scale_factor = 0.124  # รีเซ็ตค่าซูม
        self.resetTransform()
        self.scale(self.scale_factor, self.scale_factor)
        self.main_window.textarea.append(f"🟢 Success: {pdf_path}")

    def wheelEvent(self, event: QWheelEvent):
        """รองรับการซูมด้วย Scroll Mouse"""
        zoom_factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        new_scale = self.scale_factor * zoom_factor

        # จำกัดค่าซูมระหว่าง min_scale และ max_scale
        if self.min_scale <= new_scale <= self.max_scale:
            self.scale_factor = new_scale

            # Get the mouse position to zoom around it
            mouse_pos = event.position()
            scene_pos = self.mapToScene(mouse_pos.toPoint())

            # Apply the transformation to zoom the view
            self.resetTransform()  # Reset any previous transformations
            self.scale(self.scale_factor, self.scale_factor)  # Apply new scale

            # Adjust the view's position to zoom around the mouse position
            delta_x = scene_pos.x() - self.mapToScene(mouse_pos.toPoint()).x()
            delta_y = scene_pos.y() - self.mapToScene(mouse_pos.toPoint()).y()
            self.translate(delta_x, delta_y)

            # Optional: Provide feedback or trigger any action
            # self.main_window.status_left_label.setText(f"Zoom level: {new_scale:.2f}")

    def mousePressEvent(self, event):
        """เริ่มการลากภาพเมื่อกดเม้าส์ซ้าย"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)  # เปลี่ยน cursor เป็นมือกำ
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """ลากเม้าส์เพื่อเลื่อนภาพ"""
        if self.last_mouse_pos:
            delta = event.position() - self.last_mouse_pos
            self.last_mouse_pos = event.position()
            self.translate(delta.x(), delta.y())  # เลื่อนตำแหน่งภาพ
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """ปล่อยเม้าส์หยุดการลากภาพ"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)  # เปลี่ยน cursor กลับเป็นลูกศร
        super().mouseReleaseEvent(event)

    def save_pdf(self, output_path):
        """บันทึก PDF ใหม่ที่มีการแก้ไข"""
        if self.doc:
            # ใช้ฟังก์ชัน save ของ PyMuPDF เพื่อบันทึก PDF
            self.doc.save(output_path)
            return output_path
            # print(f"PDF saved to {output_path}")
        else:
            return None
            # print("No document loaded to save.")

    def _draw_markers_on_pdf(self, station, time, date, string_plot, checkOpenText):
        if checkOpenText != None:
            parts = checkOpenText.split()
            TYPE = parts[0]  # TTAA หรือ TTBB
            YYGGId = parts[1]  # ตัวเลขที่สอง
            IIiii = parts[2]  # สถานี (เช่น 48327)
            if IIiii == "48327":
                station = "48327| VTCC| Chiang Mai"

            elif IIiii == "48378":
                station = "48378| VTPS| Phitsanulok"

            elif IIiii == "48381":
                station = "48381| VTUK| Khon Kaen"

            elif IIiii == "48407":
                station = "48407| VTUU| Ubon Ratchathani"

            elif IIiii == "48431":
                station = "48431| VTUN| Nakhon Ratchasima"

            elif IIiii == "48453":
                station = "48453| VTBB| Bangna"

            elif IIiii == "48477":
                station = "48477| VTxx| Sattahip"

            elif IIiii == "48480":
                station = "48480| VTBC| Chanthaburi"

            elif IIiii == "48500":
                station = "48500| VTBP| Prachuap Khirikhan"

            elif IIiii == "48551":
                station = "48551| VTSB| Surat Thani"

            elif IIiii == "48565":
                station = "48565| VTSP| Phuket"

            elif IIiii == "48568":
                station = "48568| VTSH| Songkhla"

            else:
                station = "48xxx| VTxx| Unknow"

            if YYGGId[2:4] == "00":
                time = "0000 UTC | 0700 LST"
            elif YYGGId[2:4] == "06":
                time = "0600 UTC | 1300 LST"
            elif YYGGId[2:4] == "12":
                time = "1200 UTC | 1900 LST"
            elif YYGGId[2:4] == "18":
                time = "1800 UTC | 0100 LST"

        self.main_window.textarea.setText("")
        self.main_window.textarea.append(
            f"🟢 Plot Skew-T Log-P Diagram | Station {station} | Time: {time} | Date: {date} | Plot Begin: {string_plot}"
        )

        page = self.doc[0]  # ดึงหน้าแรกของ PDF
        image_width = self.image_item.pixmap().width()
        image_height = self.image_item.pixmap().height()

        # สร้าง pdf_worker สำหรับ PDFWorker
        self.pdf_worker = PDFWorker(
            self.doc,
            page,
            image_width,
            image_height,
            station,
            time,
            date,
            string_plot,
            checkOpenText,
        )
        # เชื่อมต่อ signal text_update กับ slot update_status_left
        self.pdf_worker.text_update.connect(
            self.main_window.textarea.append
        )  # ส่งข้อความไปยัง MainWindow
        self.pdf_worker.load_pdf_signal.connect(
            self.load_pdf
        )  # เชื่อมโยงสัญญาณ load_pdf_signal กับฟังก์ชัน load_pdf
        self.pdf_worker.start()  # เริ่มการประมวลผลใน pdf_worker


# ---------------------------------------------------------------------------------------------------------------------------------#
