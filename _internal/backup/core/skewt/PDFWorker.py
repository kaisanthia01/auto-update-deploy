import os
import datetime
from PyQt6.QtCore import pyqtSignal, QThread
from controls.CheckOpenText import CheckOpenText  # นำเข้า Class จากโฟลเดอร์ CheckOpenText
from controls.CheckURLSkewT import CheckURLSkewT  # นำเข้า Class จากโฟลเดอร์ CheckURLSkewT
from controls.PlotText import PlotText  # นำเข้า Class จากโฟลเดอร์ PlotText
from controls.CheckCodeTTAA import CheckCodeTTAA  # นำเข้า Class จากโฟลเดอร์ CheckCodeTTAA
from controls.CheckCodeTTBB import CheckCodeTTBB  # นำเข้า Class จากโฟลเดอร์ CheckCodeTTBB
from controls.CheckArrayTEMP import (
    CheckArrayTEMP,
)  # นำเข้า Class จากโฟลเดอร์ CheckArrayTEMP
from controls.CheckArrayWND import CheckArrayWND  # นำเข้า Class จากโฟลเดอร์ CheckArrayWND
from controls.PlotMarker import PlotMarker  # นำเข้า Class จากโฟลเดอร์ PlotMarker
from controls.PlotLine import PlotLine  # นำเข้า Class จากโฟลเดอร์ PlotLine
from controls.PlotWnd import PlotWnd  # นำเข้า Class จากโฟลเดอร์ PlotWnd


class PDFWorker(QThread):
    text_update = pyqtSignal(str)  # สัญญาณที่ส่งข้อความไปยัง MainWindow
    load_pdf_signal = pyqtSignal(str)  # สัญญาณเพื่อบอกให้ PDFViewer โหลด PDF

    def __init__(
        self, pdf, page, width, height, station, time, date, string_plot, checkOpenText
    ):
        super().__init__()
        self.pdf = pdf
        self.doc = page
        self.station = station
        self.time = time
        self.date = date
        self.width = width
        self.height = height
        self.plot = string_plot
        self.checkOpenText = checkOpenText
        self.temp_file = None  # ตัวแปรสำหรับไฟล์ PDF ชั่วคราว

    def run(self):
        self.text_update.emit(
            f"🟡 Plotting Skew-T Log-P Diagram Processing... 0%"
        )  # ส่งข้อความไปยัง MainWindow
        """วาด marker บน PDF และบันทึกไฟล์ใน Temp"""
        if self.doc:
            self.text_update.emit(
                f"🟡 Plotting Skew-T Log-P Diagram Processing... 1%"
            )  # ส่งข้อความไปยัง MainWindow
            try:
                page = self.doc  # ดึงหน้าแรกของ PDF
                station_num = self.station[:5]
                station_name = self.station[7:11]
                time = self.time
                date = self.date
                image_width = self.width
                image_height = self.height
                plot = self.plot
                checkOpenText = self.checkOpenText
                self.text_update.emit(
                    f"🟡 Plotting Skew-T Log-P Diagram Processing... 2%"
                )  # ส่งข้อความไปยัง MainWindow

                if checkOpenText != None:
                    # การเรียกใช้งาน CheckOpenText
                    checkText = CheckOpenText()
                    resultURL = checkText.urlGetContent(station_num, checkOpenText)
                    self.text_update.emit(
                        f"🟡 CheckOpenText Upper-air Observations... 10%"
                    )  # ส่งข้อความไปยัง MainWindow
                else:
                    # การเรียกใช้งาน CheckURLSkewT
                    checkURLSkewT = CheckURLSkewT()
                    resultURL = checkURLSkewT.urlGetContent(station_num, time, date)
                    # print(resultURL)
                    # print("/*---------------------------------*/")
                    self.text_update.emit(
                        f"🟡 CheckURLSkewT Upper-air Observations... 10%"
                    )  # ส่งข้อความไปยัง MainWindow

                if "NIL" in resultURL["TTAA"] and "NIL" in resultURL["TTBB"]:
                    self.text_update.emit(
                        f"❌ Error: {station_num} {time} {date} NIL="
                    )  # ส่งข้อความไปยัง MainWindow
                    self.load_pdf_signal.emit(
                        "Skew-T-Log-P-BlackAndWhite.pdf"
                    )  # ส่ง path ของไฟล์ PDF
                    return

                # การเรียกใช้งาน CheckCodeTTAA
                checkCodeTTAA = CheckCodeTTAA()
                resultTTAA = checkCodeTTAA.decodeTTAA(resultURL["TTAA"])
                # print(resultTTAA)
                # print("/*---------------CheckCodeTTAA------------------*/")
                self.text_update.emit(
                    f"🟡 CheckCodeTTAA - Upper-air Observations... 30%"
                )  # ส่งข้อความไปยัง MainWindow

                # การเรียกใช้งาน CheckCodeTTBB
                checkCodeTTBB = CheckCodeTTBB()
                resultTTBB = checkCodeTTBB.decodeTTBB(resultURL["TTBB"])
                # print(resultTTBB)
                # print("/*---------------CheckCodeTTBB------------------*/")
                self.text_update.emit(
                    f"🟡 CheckCodeTTBB - Upper-air Observations... 40%"
                )  # ส่งข้อความไปยัง MainWindow

                # การเรียกใช้งาน CheckArrayTEMP
                checkArrayTEMP = CheckArrayTEMP()
                resultArrayTEMP = checkArrayTEMP.decodeArrayTEMP(
                    resultTTAA["temp"], resultTTBB["temp"]
                )
                # print(resultArrayTEMP)
                # print("/*---------------CheckArrayTEMP------------------*/")
                self.text_update.emit(
                    f"🟡 CheckArrayTEMP Plot Skew-T Log-P Diagram... 50%"
                )  # ส่งข้อความไปยัง MainWindow

                # การเรียกใช้งาน CheckArrayWND
                checkArrayWND = CheckArrayWND()
                resultArrayWND = checkArrayWND.decodeArrayWND(
                    resultTTAA["wnd"], resultTTBB["wnd"]
                )
                # print(resultArrayWND)
                # print("/*---------------CheckArrayWND------------------*/")
                self.text_update.emit(
                    f"🟡 CheckArrayWND - Upper-air Observations... 60%"
                )  # ส่งข้อความไปยัง MainWindow

                # การเรียกใช้งาน PlotText
                plotText = PlotText()
                plotText.plotNewsDraw(
                    page,
                    image_width,
                    image_height,
                    station_num,
                    station_name,
                    time,
                    date,
                    resultURL["TTAA"],
                    resultURL["TTBB"],
                )
                # print("/*---------------resultPlotText------------------*/")
                self.text_update.emit(
                    f"🟡 Plotting Text - Upper-air Observations... 70%"
                )  # ส่งข้อความไปยัง MainWindow

                # การเรียกใช้งาน PlotMarker
                plotMarker = PlotMarker()
                resultMarker = plotMarker.plotMakerDraw(
                    page,
                    image_width,
                    image_height,
                    plot,
                    resultArrayTEMP,
                )
                # print(resultMarker)
                # print("/*---------------PlotMarker------------------*/")
                self.text_update.emit(
                    f"🟡 Plotting Marker - Upper-air Observations... 80%"
                )  # ส่งข้อความไปยัง MainWindow

                # การเรียกใช้งาน PlotLine
                plotLine = PlotLine()
                plotLine.plotLineDraw(
                    page,
                    image_width,
                    image_height,
                    resultMarker,
                )
                # print("/*---------------PlotLine------------------*/")
                self.text_update.emit(
                    f"🟡 Plotting Line - Upper-air Observations... 90%"
                )  # ส่งข้อความไปยัง MainWindow

                # การเรียกใช้งาน PlotWnd
                plotWnd = PlotWnd()
                plotWnd.plotWndDraw(
                    page,
                    image_width,
                    image_height,
                    plot,
                    resultArrayWND,
                )
                # print("/*---------------PlotWnd------------------*/")
                self.text_update.emit(
                    f"🟡 Plotting Wind - Upper-air Observations... 100%"
                )  # ส่งข้อความไปยัง MainWindow

                # บันทึก PDF ใหม่
                user_profile = os.environ["USERPROFILE"]
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                temp_folder = os.path.join(user_profile, "AppData", "Local", "Temp")
                self.temp_file = os.path.join(
                    temp_folder,
                    f"Skew-T-Temp-{station_num}-{time[0:4]}-{timestamp}.pdf",
                )

                # บันทึก PDF ใหม่
                self.pdf.save(self.temp_file)
                # print(f"Saved PDF with markers to: {self.temp_file} ✔️")

                self.text_update.emit(
                    f"🟡 Success: {self.temp_file}"
                )  # ส่งข้อความไปยัง MainWindow

                # อัปเดตข้อความและโหลด PDF ใน PDFViewer
                self.text_update.emit("🟡 Processing complete, Loading PDF Files...")
                # ส่งสัญญาณไปยัง PDFViewer เพื่อโหลดไฟล์ PDF
                self.load_pdf_signal.emit(self.temp_file)  # ส่ง path ของไฟล์ PDF
                # print(f"Loaded PDF with markers from: {self.temp_file} ✔️")

            except Exception as e:
                # print(f"Error in _draw_markers_on_pdf: {e}") ❌
                self.text_update.emit(f"❌ Error: {e}")  # ส่งข้อความไปยัง MainWindow


# ---------------------------------------------------------------------------------------------------------------------------------#
