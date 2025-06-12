import os
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import xarray as xr
import pandas as pd
import cartopy.io.shapereader as shpreader
import warnings
from cartopy.io import DownloadWarning
from metpy.plots import StationPlot
from metpy.calc import reduce_point_density
from metpy.plots.wx_symbols import (
    current_weather,
    sky_cover,
    low_clouds,
    mid_clouds,
    high_clouds,
)
from metpy.units import units  # 🔥 สำคัญ!
from pyproj import Transformer
from PySide6.QtCore import Signal, QThread
from cartopy.geodesic import Geodesic
from cartopy.feature import ShapelyFeature
import matplotlib.ticker as mticker
import re
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from datetime import datetime
import logging

logger = logging.getLogger("MapPressure")


class MapPressure(QThread):
    text_update = Signal(str)  # สัญญาณที่ส่งข้อความไปยัง MainWindow
    finished = Signal(str)  # ✅ เพิ่ม signal finished พร้อมส่ง path รูป

    def __init__(self):
        super(MapPressure, self).__init__()
        self.figure = None
        self.ax = None
        self.font = None

        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
        # ไฟล์ข้อมูล สถานีตรวจอากาศ
        self.json_station_world_file = os.path.join(
            script_dir, "../data/json/synop_station_world_list.json"
        )

        # ไฟล์ข้อมูลสำหรับใช้ในการ Plot
        self.json_data_pressure_file = os.path.join(
            script_dir, "../data/json/synop_data_pressure.json"
        )

        # ไฟล์ข้อมูลเปรียบเทียบสถานีแล้ว
        self.json_data_plot_pressure_file = os.path.join(
            script_dir, "../data/json/synop_data_plot_pressure.json"
        )

    @staticmethod
    def safe_slice_int(s: str, start: int, end: int, default: int = 0) -> int:
        try:
            return int(s[start:end])
        except (ValueError, TypeError, IndexError):
            return default

    @staticmethod
    def safe_slice_float(
        s: str, start: int, end: int, scale: float = 1.0, default: float = 0.0
    ) -> float:
        try:
            return float(s[start:end]) * scale
        except (ValueError, TypeError, IndexError):
            return default

    def run(self, date=None, time=None, limit=None):
        try:
            map_name = "pressure"
            script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
            logo_path = os.path.join(script_dir, "../images/icons/sfc-2.png")
            output_file = os.path.join(script_dir, "../output/map/" + map_name + ".png")
            output_file_2 = os.path.join(
                script_dir, "../output/map/" + map_name + "-600dpi.png"
            )
            output_file_3 = os.path.join(
                script_dir, "../output/map/pdf/" + map_name + ".pdf"
            )
            output_file_4 = os.path.join(
                script_dir, "../output/map/" + map_name + "_645x505mm_300dpi.png"
            )

            # โหลดฟอนต์ที่ต้องการใช้
            # กำหนด path สำหรับโหลดฟอนต์ภาษาไทย
            font_path = os.path.join(
                script_dir,
                "../fonts/Noto_Sans_Thai/static/NotoSansThai-Regular.ttf",
            )
            logger.info(f"📜 โหลดฟอนต์จาก: {font_path}")

            font = fm.FontProperties(fname=font_path)
            logger.info(f"📛 ฟอนต์ชื่อว่า: {font.get_name()}")
            self.font = font  # เก็บไว้ใช้ใน class

            # ขนาดกระดาษที่ต้องการใช้
            paper_size = {"อต.ทอ.1010": (25.59, 20.47)}  # 650 × 520 mm

            # === ขนาดภาพ ===
            dpi = 300
            dpi_2 = 600
            dpi_3 = 600
            width_px = 8000  # 7617
            height_px = 6000  # 5964
            width_in = width_px / dpi
            height_in = height_px / dpi

            # กำหนดชื่อกระดาษที่ต้องการใช้
            paper_key = "อต.ทอ.1010"  # ตัวอย่าง: "อต.ทอ.1003"
            logger.info(f"📄 ขนาดกระดาษ: {paper_key}")

            # ดึงขนาดกระดาษออกมา
            # if paper_key in paper_size:
            #    width_in, height_in = paper_size[paper_key]
            #    logger.info(f"📏 ขนาดกระดาษ: {width_in} x {height_in} นิ้ว")
            # else:
            #    logger.error(f"❌ ไม่พบขนาดกระดาษ: {paper_key}")
            #    raise ValueError(f"❌ ไม่พบขนาดกระดาษ: {paper_key}")

            # === เว้นขอบ ===
            margin_in = 0.15
            margin_x = margin_in / width_in
            margin_y = margin_in / height_in

            # === สร้างแผนที่ ===
            fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)

            ax = fig.add_axes(
                [margin_x, margin_y, 1 - 2 * margin_x, 1 - 2 * margin_y],
                projection=ccrs.PlateCarree(),
            )

            # === ขอบเขตแผนที่ผิวพื้น และความกดอากาศ
            # ทิศเหนือ จรดเส้นรุ้ง 50 องศาเหนือ, ทิศใต้ จรดเส้นรุ้ง -31 องศาใต้, ทิศตะวันออก จรดเส้นแวง 160 องศาตะวันออก, ทิศตะวันตก จรดเส้นแวง 45 องศาตะวันออก
            ax.set_extent([45.0, 160.0, -30.0, 50.0], crs=ccrs.PlateCarree())

            # === เพิ่มฟีเจอร์
            cartopy_data_path = None
            if not cartopy_data_path:
                script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
                cartopy_data_path = os.path.join(script_dir, "../data/cartopy")

            # === ตรวจสอบว่าโฟลเดอร์มีไฟล์ shapefile หรือยัง
            shapefiles_found = (
                any(
                    fname.endswith((".shp", ".dbf", ".shx"))
                    for fname in os.listdir(cartopy_data_path)
                )
                if os.path.isdir(cartopy_data_path)
                else False
            )

            # 🔧 ตั้งค่า environment เฉพาะถ้ามี
            if shapefiles_found:
                os.environ["CARTOPY_USER_BACKGROUNDS"] = cartopy_data_path
                os.environ["CARTOPY_USER_SHAPEFILES"] = cartopy_data_path
                logger.info(f"🔎 ใช้ไฟล์แผนที่จากเครื่อง: {cartopy_data_path}")
            else:
                logger.info("🔎 ไม่มีไฟล์แมพในเครื่อง → โหลดออนไลน์จาก Natural Earth")

            # === แยกเพิ่มฟีเจอร์แมพตามเงื่อนไข
            if shapefiles_found:
                self._add_map_features(ax, cartopy_data_path)
            else:
                self._add_default_features(ax)

            # === เพิ่มเส้นพรมแดนประเทศไทยเท่านั้น (ไม่ใช้รูปร่าง polygon)
            self._add_thailand_borderline_only(ax, cartopy_data_path)

            # === เพิ่มเส้นกริด lat/lon
            self._add_inner_latlon_labels(ax)

            # === เพิ่มข้อมูล Synoptic
            self._add_obs_map(ax, date, time, limit)

            # === วางโลโก้ภายในแผนที่ ด้วย ax.imshow()
            logo_img = Image.open(logo_path)

            # ปรับขนาดโลโก้ ~1 นิ้ว กว้าง
            logo_width_in = 1.0
            logo_width_px = int(logo_width_in * dpi)
            logo_height_px = int(logo_img.height * (logo_width_px / logo_img.width))
            logo_resized = logo_img.resize((logo_width_px, logo_height_px))
            logo_array = np.asarray(logo_resized)

            # พิกัดแผนที่ที่คุณอยากวาง (มุมล่างซ้าย)
            logo_lon = 53.0
            logo_lat = -23.5

            # ขนาดโลโก้ในหน่วยองศา (คร่าว ๆ)
            logo_width_deg = 4  # เดิม 8 → เหลือครึ่ง
            logo_height_deg = logo_width_deg * (
                logo_resized.height / logo_resized.width
            )

            # วางโลโก้บนแกนแผนที่
            ax.imshow(
                logo_array,
                extent=[
                    logo_lon,
                    logo_lon + logo_width_deg,
                    logo_lat,
                    logo_lat + logo_height_deg,
                ],
                transform=ccrs.PlateCarree(),
                zorder=10,
                interpolation="bicubic",
            )

            # === กำหนดฟอนต์สำหรับข้อความบนแผนที่ ===
            ax.text(
                55.0,  # ลองจิจูด (Longitude)
                -26.0,  # ละติจูด (Latitude)
                f"{date.upper()}",  # วันที่
                transform=ccrs.PlateCarree(),  # ใช้พิกัดบนแผนที่
                fontsize=32,
                fontweight="bold",
                color="blue",
                ha="center",
                va="bottom",
                zorder=11,
            )

            # === กำหนดฟอนต์สำหรับข้อความบนแผนที่ ===
            ax.text(
                55.0,  # ลองจิจูด (Longitude)
                -28.0,  # ละติจูด (Latitude)
                f"{time[0:8]}",  # เวลา
                transform=ccrs.PlateCarree(),  # ใช้พิกัดบนแผนที่
                fontsize=32,
                fontweight="bold",
                color="red",
                ha="center",
                va="bottom",
                zorder=11,
            )

            # === เพิ่มตัวอักษรบนแผนที่ ===
            # แสดงข้อความที่ตำแหน่งลองจิจูด 53.0, ละติจูด -29.75
            ax.text(
                45.09,  # ลองจิจูด (Longitude)
                -29.91,  # ละติจูด (Latitude)
                f"Date: {date} Time: {time[0:8]} | Pressure Change Map",  # ข้อความ
                transform=ccrs.PlateCarree(),  # ใช้พิกัดบนแผนที่
                fontsize=3,  # ขนาดตัวอักษร
                fontweight="bold",  # ตัวหนา
                color="black",  # สีข้อความ
                ha="left",  # จัดกึ่งกลางแนวนอน
                va="bottom",  # จัดกึ่งกลางแนวตั้ง
                bbox=dict(
                    facecolor="white",
                    edgecolor="black",
                    linewidth=0.8,
                    alpha=1,
                    boxstyle="square,pad=0.5",
                ),  # กล่องรอบข้อความ
            )

            # กำหนดค่า DPI สำหรับการบันทึกไฟล์
            plt.rcParams["savefig.dpi"] = 600

            # === บันทึกเป็น PNG 300 dpi ===
            plt.savefig(output_file, dpi=dpi, bbox_inches="tight")

            # === บันทึกเป็น PNG คุณภาพสูง 600 dpi ===
            # plt.savefig(output_file_2, dpi=dpi_2, bbox_inches="tight")

            # === บันทึกเป็น PDF คุณภาพสูง 600 dpi ===
            plt.savefig(output_file_3, dpi=dpi_3, bbox_inches="tight")
            plt.close()

            self.text_update.emit(f"🖼️ {output_file}")
            # self.text_update.emit(f"📄 {output_file_3}")

            logger.info("📸 Map saved successfully")
            logger.info(f"🖼️ {output_file}")
            # logger.info(f"🖼️ {output_file_2}")
            # logger.info(f"📜 {output_file_3}")

            # ตรวจสอบ
            img = Image.open(output_file)
            logger.info(f"🖼️ Dimensions: {img.size} px")
            logger.info(f"🖼️ DPI: {img.info.get('dpi')}")

            # ขนาดเป้าหมาย (645 x 505 mm ที่ 300 DPI)
            target_size = (7617, 5964)

            # ขยายแบบคุณภาพสูง
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)

            # บันทึกเป็น PNG พร้อม DPI 300
            resized_img.save(output_file_4, dpi=(300, 300))

            self.finished.emit(output_file)  # ✅ ส่ง path ไฟล์ออกไป
        except Exception as e:
            self.text_update.emit(f"❌ Error during map creation: {e}")

    # === ฟังก์ชันเสริม ===
    def _add_map_features(self, ax, cartopy_data_path):
        """เพิ่มสีพื้นหลัง, เส้นพรมแดน, ชื่อประเทศ, และชื่อทะเลลงบนแผนที่"""
        self.text_update.emit("🗺️ Downloading Map Features in local")
        boundary_path = os.path.join(
            cartopy_data_path, "ne_50m_admin_0_boundary_lines_land.shp"
        )
        coast_path = os.path.join(cartopy_data_path, "ne_50m_coastline.shp")
        countries_path = os.path.join(
            cartopy_data_path, "ne_110m_admin_0_countries.shp"
        )
        marine_path = os.path.join(
            cartopy_data_path, "ne_10m_geography_marine_polys.shp"
        )

        # ✅ สีพื้นหลังของแผนที่
        ax.add_feature(cfeature.LAND, facecolor="none", alpha=0.1)  # ✅ พื้นดิน (สีเนื้อ)
        ax.add_feature(
            cfeature.OCEAN,
            facecolor="none",
            alpha=0.1,
        )  # ✅ พื้นน้ำ (เงินน้ำเงินอ่อน)

        try:
            # ✅ พล็อตเส้นพรมแดน (BORDERS)
            if os.path.exists(boundary_path):
                borders = shpreader.Reader(boundary_path)
                ax.add_geometries(
                    borders.geometries(),
                    crs=ccrs.PlateCarree(),
                    edgecolor="#5f5f5f",
                    facecolor="none",
                    linewidth=2,
                    alpha=0.8,
                )
            else:
                ax.add_feature(
                    cfeature.BORDERS, linewidth=2, edgecolor="#5f5f5f", alpha=0.8
                )

        except Exception as e:
            logger.error(f"❌ Failed to add borders: {e}")

        try:
            # ✅ พล็อตแนวชายฝั่ง (COASTLINE)
            if os.path.exists(coast_path):
                coast = shpreader.Reader(coast_path)
                ax.add_geometries(
                    coast.geometries(),
                    crs=ccrs.PlateCarree(),
                    edgecolor="#5f5f5f",
                    facecolor="none",
                    linewidth=2,
                    alpha=0.8,
                )
            else:
                ax.add_feature(
                    cfeature.COASTLINE, linewidth=2, edgecolor="#5f5f5f", alpha=0.8
                )

        except Exception as e:
            logger.error(f"❌ Failed to add coastline: {e}")

        try:
            # ✅ ดึงขอบเขตของแผนที่
            west, east, south, north = ax.get_extent(ccrs.PlateCarree())

            # ✅ โหลดข้อมูลชื่อประเทศ (เฉพาะที่อยู่ในขอบเขตแผนที่)
            if os.path.exists(countries_path):
                reader = shpreader.Reader(countries_path)
                for country in reader.records():
                    lon, lat = country.geometry.centroid.coords[0]
                    name = country.attributes["NAME"]

                    # ✅ กรองเฉพาะชื่อประเทศที่อยู่ภายในขอบเขตแผนที่
                    if west + 2 <= lon <= east - 2 and south <= lat <= north:
                        ax.text(
                            lon,
                            lat,
                            name,
                            fontsize=5,
                            ha="center",
                            clip_on=True,  # ✅ ป้องกันการเลยขอบแผนที่
                            transform=ccrs.PlateCarree(),
                            color="grey",
                            alpha=0.5,
                        )

        except Exception as e:
            logger.error(f"❌ Failed to add country names: {e}")

        try:
            # ✅ ดึงขอบเขตแผนที่
            west, east, south, north = ax.get_extent(ccrs.PlateCarree())

            # ✅ โหลดข้อมูลชื่อทะเล, อ่าว, และมหาสมุทร
            if os.path.exists(marine_path):
                reader = shpreader.Reader(marine_path)
                for marine in reader.records():
                    lon, lat = marine.geometry.centroid.coords[0]

                    # ✅ ลองพิมพ์ keys ทั้งหมดดู
                    # print(marine.attributes.keys())

                    # ✅ ลองใช้ key อื่นที่อาจเก็บชื่อทะเล/อ่าว
                    name = marine.attributes.get("NAME", "") or marine.attributes.get(
                        "name", ""
                    )

                    if name and west <= lon <= east and south <= lat <= north:
                        ax.text(
                            lon,
                            lat,
                            name,
                            fontsize=1.5,
                            alpha=0.3,
                            color="darkblue",
                            ha="center",
                            clip_on=True,  # ✅ ป้องกันข้อความล้นขอบแผนที่
                            transform=ccrs.PlateCarree(),
                        )

        except Exception as e:
            logger.error(f"❌ Failed to add sea names: {e}")

    def _add_default_features(self, ax):
        self.text_update.emit("🌐 Downloading Online Natural Earth")

        # แจ้งว่ากำลังโหลดออนไลน์
        logger.info(
            "🌐 ไม่มีไฟล์แมพในเครื่อง → โหลดออนไลน์จาก Natural Earth (อาจใช้เวลาสักครู่...)"
        )

        # ปิดแสดง warning ซ้ำ ๆ
        warnings.simplefilter("default", DownloadWarning)

        ax.add_feature(cfeature.BORDERS, linewidth=2, edgecolor="#5f5f5f", alpha=0.8)
        ax.add_feature(cfeature.COASTLINE, linewidth=2, edgecolor="#5f5f5f", alpha=0.8)

        # ✅ สีพื้นหลังของแผนที่
        ax.add_feature(cfeature.LAND, facecolor="none")  # ✅ พื้นดิน (สีเนื้อ)
        ax.add_feature(cfeature.OCEAN, facecolor="none")  # ✅ พื้นน้ำ (เงินน้ำเงินอ่อน)

    def _add_thailand_borderline_only(self, ax, cartopy_data_path):
        """เพิ่มเส้นพรมแดนประเทศไทยเท่านั้น (ไม่ใช้รูปร่าง polygon)"""
        # โหลด shapefile ของประเทศไทย
        shapefile_path = os.path.join(cartopy_data_path, "ne_50m_admin_0_countries.shp")

        # สีเส้นพรมแดน
        color = "black"

        try:
            reader = shpreader.Reader(shapefile_path)

            thailand_shape = [
                record.geometry
                for record in reader.records()
                if record.attributes.get("NAME") == "Thailand"
            ]

            if thailand_shape:
                border = ShapelyFeature(
                    thailand_shape,
                    ccrs.PlateCarree(),
                    edgecolor=color,
                    facecolor="none",
                    linewidth=4,
                    zorder=6,
                    alpha=1,
                )
                ax.add_feature(border)
            else:
                logger.warning("⚠️ ไม่พบเส้นพรมแดนของประเทศไทยใน shapefile นี้")

        except Exception as e:
            logger.error(f"❌ ไม่สามารถวาดเส้นพรมแดนประเทศไทย: {e}")

    def _add_inner_latlon_labels(self, ax):
        interval = 5
        color = "gray"
        fontsize = 7

        # วาดเส้นกริด (ไม่มีตัวเลขอัตโนมัติ)
        gl = ax.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=False,
            linewidth=0.5,
            color=color,
            alpha=0.5,
            linestyle="--",
            zorder=4,
        )
        gl.xlocator = mticker.MultipleLocator(interval)
        gl.ylocator = mticker.MultipleLocator(interval)

        # ดึงขอบเขตแผนที่
        extent = ax.get_extent(ccrs.PlateCarree())
        west, east, south, north = extent

        # ปัดค่าขึ้นให้หาร interval ลงตัว
        def next_divisible_by(x, base):
            return x if x % base == 0 else x + (base - (x % base))

        lon_start = next_divisible_by(np.floor(west), interval)
        lat_start = next_divisible_by(np.floor(south), interval)

        lon_ticks = np.arange(lon_start, np.ceil(east) + interval, interval)
        lat_ticks = np.arange(lat_start, np.ceil(north) + interval, interval)

        # ระยะขยับข้อความเข้าด้านในกรอบ
        dx = (east - west) * 0.005
        dy = (north - south) * 0.015

        start = 1

        # วาด label ลองจิจูด (แนวนอนล่างในกรอบ)
        for lon in lon_ticks[start:-1]:
            if west <= lon <= east:
                y_pos = south + dy
                if south < y_pos < north:
                    label = (
                        f"{abs(int(round(lon)))}°E"
                        if lon >= 0
                        else f"{abs(int(round(lon)))}°W"
                    )
                    ax.text(
                        lon,
                        y_pos,
                        label,
                        fontsize=fontsize,
                        color="#AAAAAA",
                        ha="center",
                        va="bottom",
                        transform=ccrs.PlateCarree(),
                        # bbox=dict(facecolor="white", alpha=1.0, edgecolor="none"),
                        zorder=10,
                    )

        # วาด label ละติจูด (แนวตั้งซ้ายในกรอบ)
        for lat in lat_ticks[start:-1]:
            if south <= lat <= north:
                x_pos = west + dx
                if west < x_pos < east:
                    label = (
                        f"{abs(int(round(lat)))}°N"
                        if lat >= 0
                        else f"{abs(int(round(lat)))}°S"
                    )
                    ax.text(
                        x_pos,
                        lat,
                        label,
                        fontsize=fontsize,
                        color="#AAAAAA",
                        ha="left",
                        va="center",
                        transform=ccrs.PlateCarree(),
                        # bbox=dict(facecolor="white", alpha=1.0, edgecolor="none"),
                        zorder=10,
                    )

    def _add_obs_map(self, ax, date=None, time=None, limit=None):
        try:
            self.text_update.emit("🟡 Plot Pressure() Called")
            if not ax:
                self.text_update.emit("❌ Map not initialized")
                return

            # โหลดข้อมูล JSON เฉพาะ pressure เท่านั้น
            data_synop = self.load_json(self.json_data_pressure_file)
            self.text_update.emit(
                f"📄 Loaded parsed pressure data: {len(data_synop)} entries"
            )

            data_station = self.load_json(self.json_station_world_file)
            self.text_update.emit(f"📄 Loaded stations: {len(data_station)} entries")

            if not data_synop or not data_station:
                self.text_update.emit("❌ Missing data file(s)")
                return ax

            # ✅ ดึงวันที่ทั้งหมดจากข้อมูล synop และเรียงล่าสุดก่อน
            dates = sorted(
                {r.get("date") for r in data_synop if r.get("date")}, reverse=True
            )

            if len(dates) < 2:
                self.text_update.emit("❌ ต้องการข้อมูลอย่างน้อย 2 วัน")
                return ax

            latest_date = dates[0]
            previous_date = dates[1]
            self.text_update.emit(
                f"📆 Latest: {latest_date}, Previous: {previous_date}"
            )

            data_latest = [r for r in data_synop if r.get("date") == latest_date]
            data_previous = [r for r in data_synop if r.get("date") == previous_date]
            data_previous_dict = {r["station_id"]: r for r in data_previous}

            stations = []
            for record_today in data_latest:
                station_id = record_today.get("station_id")
                record_yesterday = data_previous_dict.get(station_id)
                if not record_yesterday:
                    continue

                station_info = next(
                    (s for s in data_station if s["station_id"] == station_id), None
                )
                if not station_info:
                    continue

                try:
                    pres_today = record_today.get("main", {}).get("4PPPP", "")
                    pres_yesterday = record_yesterday.get("main", {}).get("4PPPP", "")

                    if not (
                        pres_today.startswith("40") and pres_yesterday.startswith("40")
                    ):
                        continue

                    if len(pres_today) < 5 or len(pres_yesterday) < 5:
                        continue

                    def parse_pressure(p_str):
                        sub = p_str[2:5].replace("/", "0")
                        return 1000.0 + (int(sub) / 10.0) if sub.isdigit() else None

                    p_today = parse_pressure(pres_today)
                    p_yesterday = parse_pressure(pres_yesterday)

                    if p_today is None or p_yesterday is None:
                        continue

                    delta_p = round(p_today - p_yesterday, 1)

                    stations.append(
                        {
                            "station_id": station_id,
                            "lat": float(station_info["location"]["latitude"]),
                            "lon": float(station_info["location"]["longitude"]),
                            "pppp": delta_p,
                        }
                    )
                except Exception as e:
                    self.main_window.textarea.append(
                        f"⚠️ Parse error for station {station_id}: {e}"
                    )
                    continue

            # ✅ ย้ายมาที่นี่
            self.write_json(self.json_data_plot_pressure_file, stations)
            self.text_update.emit(f"✅ Parsed {len(stations)} stations")

            if not stations:
                self.text_update.emit("❌ No stations to plot")
                return ax

            # ▶️ สร้าง DataFrame และแปลงพิกัด
            df = pd.DataFrame(stations)
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
            df["x_meter"], df["y_meter"] = transformer.transform(
                df["lon"].values, df["lat"].values
            )

            # ▶️ ลดความหนาแน่นจุด
            point_locs = xr.DataArray(
                np.stack([df["x_meter"], df["y_meter"]], axis=-1),
                dims=("points", "space"),
                attrs={"crs": ccrs.PlateCarree()},
            )

            # ลดความหนาแน่นจุด
            limit = 50000.0 * ((100 - limit) / 30.0) * units.meter
            self.text_update.emit(f"▶️ ลดความหนาแน่นจุด: {limit:.0f}")

            # แปลงจากพิกัดละติจูด/ลองจิจูด (WGS84) → พิกัดเมตร (Web Mercator)
            mask = reduce_point_density(point_locs * units.meter, limit)

            # mask = reduce_point_density(
            #    point_locs * units.meter, 50000.0 * units.meter
            # )
            df = df[mask]

            # ▶️ กรองขอบเขตแผนที่
            df = df[
                (df["lon"] >= 46.5)
                & (df["lon"] <= 159.5)
                & (df["lat"] >= -29.0)
                & (df["lat"] <= 48.8)
            ]

            if df.empty:
                self.text_update.emit("❌ No stations to plot")
                return ax

            try:
                self.text_update.emit("▶️ Plot pressure สถานีด้วย MetPy")
                for i, row in df.iterrows():
                    value = row["pppp"]
                    color = (
                        "green"
                        if value == 0 or pd.isna(value)
                        else "red" if value < 0 else "blue"
                    )

                    text = f"{abs(value):.1f}" if pd.notna(value) else ""

                    # สร้าง StationPlot ใหม่เฉพาะจุดนี้
                    single_plot = StationPlot(
                        ax,
                        [row["lon"]],
                        [row["lat"]],
                        transform=ccrs.PlateCarree(),
                        fontsize=5,
                        spacing=5.5,
                        zorder=10,
                    )

                    single_plot.plot_text(
                        "C",  # หรือกำหนดตำแหน่งเอง เช่น (1, -1)
                        [text],
                        color=color,
                        fontweight="bold",
                        fontproperties=self.font,
                        fontsize=6,
                        zorder=10,
                    )

                self.text_update.emit("✅ Plot Pressure สถานีด้วย MetPy")
            except Exception as e:
                self.text_update.emit(f"❌ Plot Pressure Error: {e}")
        except Exception as e:
            self.text_update.emit(f"❌ Unexpected error in Plot Pressure: {e}")

    def load_json(self, path):
        if not os.path.exists(path):
            self.text_update.emit(f"⚠️ File not found: {path}")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.text_update.emit(f"⚠️ Failed to load JSON: {e}")
            return []

    def write_json(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.text_update.emit(f"✅ JSON saved successfully: {path}")
            return True
        except Exception as e:
            self.text_update.emit(f"❌ Failed to write JSON: {e}")
            return False
