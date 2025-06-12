import os
from datetime import datetime
import logging

logger = logging.getLogger("PlotManager")


class PlotManager:
    def __init__(self, main_window):
        self.main_window = main_window  # ✅ เก็บไว้ใช้ใน class

    def plot_surface_and_update_qml(self):
        from core.map_surface import MapSurface  # สมมุติว่าใช้คลาสนี้

        logger.info("✍ PlotManager: MapSurface()")
        self.main_window.append_debugger("✍ PlotManager: MapSurface()")

        mapSurface = MapSurface(self.main_window)  # ✅ ส่งต่อ
        mapSurface.create_map()

    def plot_pressure_and_update_qml(
        self, qml_interface, date: str, time: str, limit: int = 100
    ):
        fig, ax = self.plotter.create_map(2)
        fig, ax = self.plotter.plot_pressure(date, time, limit)
        self._save_plot_and_update(fig, "pressure", qml_interface)

    def plot_detail_and_update_qml(
        self, qml_interface, date: str, time: str, limit: int = 100
    ):
        fig, ax = self.plotter.create_map(3)
        fig, ax = self.plotter.plot_detail(date, time, limit)
        self._save_plot_and_update(fig, "detail", qml_interface)

    def plot_upperwind1_and_update_qml(
        self, qml_interface, date: str, time: str, limit: int = 100, index_pressure=850
    ):
        fig, ax = self.plotter.create_map(4)
        fig, ax = self.plotter.plot_upperwind1(date, time, limit, index_pressure)
        self._save_plot_and_update(fig, "wind1", qml_interface)

    def plot_upperwind2_and_update_qml(
        self, qml_interface, date: str, time: str, limit: int = 100
    ):
        fig, ax = self.plotter.create_map(5)
        fig, ax = self.plotter.plot_upperwind2(date, time, limit)
        self._save_plot_and_update(fig, "wind2", qml_interface)

    def plot_skewt_and_update_qml(
        self, qml_interface, date: str, time: str, station_id="48455"
    ):
        fig = self.plotter.plot_skewt(date, time, station_id)
        self._save_plot_and_update(fig, "skewt", qml_interface)
