import os
from datetime import datetime
import logging
from PySide6.QtCore import QUrl

from core.map_surface import MapSurface  # ✅ Import MapSurface
from core.map_pressure import MapPressure  # ✅ Import MapPressure
from core.map_detail import MapDetail  # ✅ Import MapDetail
from core.map_wind_1 import MapWind_1  # ✅ Import MapWind_1
from core.map_wind_2 import MapWind_2  # ✅ Import MapWind_2
from core.map_skewt import MapSkewT  # ✅ Import MapSkewT

logger = logging.getLogger("PlotManager")


class PlotManager:
    def __init__(self, main_window):
        self.main_window = main_window  # ✅ เก็บไว้ใช้ใน class

    def plot_surface_and_update_qml(self, date, time, limit, check_cloud):
        logger.info("✍ PlotManager: MapSurface()")
        self.main_window.append_debugger("✍ PlotManager: MapSurface()")

        self.mapSurface = MapSurface()
        self.mapSurface.text_update.connect(self.main_window.append_debugger)

        # ✅ เชื่อม finished -> เรียกอัปเดตภาพ
        self.mapSurface.finished.connect(self.update_surface_image)

        self.mapSurface.run(
            date, time, limit, check_cloud
        )  # run() เพื่อให้ทำงานแยก thread จริง ๆ

    def update_surface_image(self, output_file):
        file_url = QUrl.fromLocalFile(output_file).toString()
        self.main_window.update_image_source("surface", file_url)  # ส่งสัญญาณไป QML
        self.main_window.append_debugger(
            f"📸 PlotManager: update_surface_image() {file_url}"
        )
        logger.info(f"📸 PlotManager: update_surface_image() {file_url}")
        self.mapSurface.finished.disconnect(self.update_surface_image)
        self.mapSurface.text_update.disconnect(self.main_window.append_debugger)
        self.mapSurface = None

    def plot_pressure_and_update_qml(self, date, time, limit):
        logger.info("✍ PlotManager: MapPressure()")
        self.main_window.append_debugger("✍ PlotManager: MapPressure()")

        self.mapPressure = MapPressure()
        self.mapPressure.text_update.connect(self.main_window.append_debugger)

        # ✅ เชื่อม finished -> เรียกอัปเดตภาพ
        self.mapPressure.finished.connect(self.update_pressure_image)

        self.mapPressure.run(date, time, limit)  # run() เพื่อให้ทำงานแยก thread จริง ๆ

    def update_pressure_image(self, output_file):
        file_url = QUrl.fromLocalFile(output_file).toString()
        self.main_window.update_image_source("pressure", file_url)  # ส่งสัญญาณไป QML
        self.main_window.append_debugger(
            f"📸 PlotManager: update_pressure_image() {file_url}"
        )
        logger.info(f"📸 PlotManager: update_pressure_image() {file_url}")
        self.mapPressure.finished.disconnect(self.update_pressure_image)
        self.mapPressure.text_update.disconnect(self.main_window.append_debugger)
        self.mapPressure = None

    def plot_detail_and_update_qml(self, date, time, limit, check_cloud):
        logger.info("✍ PlotManager: MapDetail()")
        self.main_window.append_debugger("✍ PlotManager: MapDetail()")

        self.mapDetail = MapDetail()
        self.mapDetail.text_update.connect(self.main_window.append_debugger)

        # ✅ เชื่อม finished -> เรียกอัปเดตภาพ
        self.mapDetail.finished.connect(self.update_detail_image)

        self.mapDetail.run(
            date, time, limit, check_cloud
        )  # run() เพื่อให้ทำงานแยก thread จริง ๆ

    def update_detail_image(self, output_file):
        file_url = QUrl.fromLocalFile(output_file).toString()
        self.main_window.update_image_source("detail", file_url)  # ส่งสัญญาณไป QML
        self.main_window.append_debugger(
            f"📸 PlotManager: update_detail_image() {file_url}"
        )
        logger.info(f"📸 PlotManager: update_detail_image() {file_url}")
        self.mapDetail.finished.disconnect(self.update_detail_image)
        self.mapDetail.text_update.disconnect(self.main_window.append_debugger)
        self.mapDetail = None

    def plot_wind_1_and_update_qml(self, date, time, limit):
        logger.info("✍ PlotManager: MapWind_1()")
        self.main_window.append_debugger("✍ PlotManager: MapWind_1()")

        self.MapWind_1 = MapWind_1()
        self.MapWind_1.text_update.connect(self.main_window.append_debugger)

        # ✅ เชื่อม finished -> เรียกอัปเดตภาพ
        self.MapWind_1.finished.connect(self.update_wind_1_image)

        self.MapWind_1.run(date, time, limit)  # run() เพื่อให้ทำงานแยก thread จริง ๆ

    def update_wind_1_image(self, output_file):
        file_url = QUrl.fromLocalFile(output_file).toString()
        self.main_window.update_image_source("wind_1", file_url)  # ส่งสัญญาณไป QML
        self.main_window.append_debugger(
            f"📸 PlotManager: update_wind_1_image() {file_url}"
        )
        logger.info(f"📸 PlotManager: update_wind_1_image() {file_url}")
        self.MapWind_1.finished.disconnect(self.update_wind_1_image)
        self.MapWind_1.text_update.disconnect(self.main_window.append_debugger)
        self.MapWind_1 = None

    def plot_wind_2_and_update_qml(self, date, time, limit):
        logger.info("✍ PlotManager: MapWind_2()")
        self.main_window.append_debugger("✍ PlotManager: MapWind_2()")

        self.MapWind_2 = MapWind_2()
        self.MapWind_2.text_update.connect(self.main_window.append_debugger)

        # ✅ เชื่อม finished -> เรียกอัปเดตภาพ
        self.MapWind_2.finished.connect(self.update_wind_2_image)

        self.MapWind_2.run(date, time, limit)  # run() เพื่อให้ทำงานแยก thread จริง ๆ

    def update_wind_2_image(self, output_file):
        file_url = QUrl.fromLocalFile(output_file).toString()
        self.main_window.update_image_source("wind_2", file_url)  # ส่งสัญญาณไป QML
        self.main_window.append_debugger(
            f"📸 PlotManager: update_wind_2_image() {file_url}"
        )
        logger.info(f"📸 PlotManager: update_wind_2_image() {file_url}")
        self.MapWind_2.finished.disconnect(self.update_wind_2_image)
        self.MapWind_2.text_update.disconnect(self.main_window.append_debugger)
        self.MapWind_2 = None

    def plot_skewt_and_update_qml(self, date, time, station, level):
        logger.info("✍ PlotManager: MapSkewT()")
        self.main_window.append_debugger("✍ PlotManager: MapSkewT()")

        self.MapSkewT = MapSkewT()
        self.MapSkewT.text_update.connect(self.main_window.append_debugger)

        # ✅ เชื่อม finished -> เรียกอัปเดตภาพ
        self.MapSkewT.finished.connect(self.update_skewt_image)

        self.MapSkewT.run(
            date, time, station, level
        )  # run() เพื่อให้ทำงานแยก thread จริง ๆ

    def update_skewt_image(self, output_file):
        file_url = QUrl.fromLocalFile(output_file).toString()
        self.main_window.update_image_source("skewt", file_url)  # ส่งสัญญาณไป QML
        self.main_window.append_debugger(
            f"📸 PlotManager: update_skewt_image() {file_url}"
        )
        logger.info(f"📸 PlotManager: update_skewt_image() {file_url}")
        self.MapSkewT.finished.disconnect(self.update_skewt_image)
        self.MapSkewT.text_update.disconnect(self.main_window.append_debugger)
        self.MapSkewT = None
