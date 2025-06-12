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
    pressure_tendency,
    wx_symbol_font,
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

logger = logging.getLogger("MapSurface")


class MapSurface(QThread):
    text_update = Signal(str)  # สัญญาณที่ส่งข้อความไปยัง MainWindow
    finished = Signal(str)  # ✅ เพิ่ม signal finished พร้อมส่ง path รูป

    def __init__(self):
        super(MapSurface, self).__init__()
        self.figure = None
        self.ax = None

        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
        # ไฟล์ข้อมูล สถานีตรวจอากาศ
        self.json_station_world_file = os.path.join(
            script_dir, "../data/json/synop_station_world_list.json"
        )

        # ไฟล์ข้อมูลสำหรับใช้ในการ Plot
        self.json_data_surface_file = os.path.join(
            script_dir, "../data/json/synop_data_surface.json"
        )

        self.json_data_surface2day_file = os.path.join(
            script_dir, "../data/json/synop_data_surface2day.json"
        )

        # ไฟล์ข้อมูลเปรียบเทียบสถานีแล้ว
        self.json_data_plot_surface_file = os.path.join(
            script_dir, "../data/json/synop_data_plot_surface.json"
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

    def run(self, date=None, time=None, limit=None, check_cloud=1):
        try:
            map_name = "surface"
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
                script_dir, "../output/map/" + map_name + "_980x760mm_300dpi.png"
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

            # ขนาดกระดาษที่ต้องการใช้
            paper_size = {"อต.ทอ.1001": (38.58, 29.92)}  # 980 × 760 mm

            # === ขนาดภาพ ===
            dpi = 300
            dpi_2 = 600
            dpi_3 = 600
            width_px = 8000  # 11574
            height_px = 6000  # 8976
            width_in = width_px / dpi
            height_in = height_px / dpi

            # กำหนดชื่อกระดาษที่ต้องการใช้
            paper_key = "อต.ทอ.1001"  # ตัวอย่าง: "อต.ทอ.1003"
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
            fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor="white")

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
            self._add_obs_map(ax, date, time, limit, check_cloud)

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
                -25.5,  # ละติจูด (Latitude)
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
                -27.5,  # ละติจูด (Latitude)
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
                45.10,  # ลองจิจูด (Longitude)
                -29.90,  # ละติจูด (Latitude)
                f"Date: {date} Time: {time[0:8]} | Surface Map",  # ข้อความ
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

            # ขนาดเป้าหมาย (980 x 760 mm ที่ 300 DPI)
            target_size = (5787, 4488)

            # ขยายแบบคุณภาพสูง
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)

            # บันทึกเป็น PNG พร้อม DPI 300
            resized_img.save(output_file_4, dpi=(600, 600))

            self.finished.emit(output_file)  # ✅ ส่ง path ไฟล์ออกไป
        except Exception as e:
            self.text_update.emit(f"❌ Error during map creation: {e}")
            logger.error(f"❌ Error during map creation: {e}")

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
        color = "darkred"

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

    def _add_obs_map(self, ax, date=None, time=None, limit=None, check_cloud=1):
        if check_cloud == 1:
            try:
                self.text_update.emit("🟡 Plot Surface() Called")
                if not ax:
                    self.text_update.emit("❌ Map not initialized")
                    return

                # โหลดข้อมูล JSON เฉพาะ surface เท่านั้น
                data_synop = self.load_json(self.json_data_surface_file)
                self.text_update.emit(
                    f"📄 Loaded parsed surface data: {len(data_synop)} entries"
                )

                data_station = self.load_json(self.json_station_world_file)
                self.text_update.emit(
                    f"📄 Loaded stations: {len(data_station)} entries"
                )

                if not data_synop or not data_station:
                    self.text_update.emit("❌ Missing data file(s)")
                    return ax

                # ✅ ดึงวันที่ทั้งหมดจากข้อมูล synop และเรียงล่าสุดก่อน
                dates = sorted(
                    {r.get("date") for r in data_synop if r.get("date")}, reverse=True
                )

                if len(dates) > 0:
                    latest_date = dates[0]
                    self.text_update.emit(f"📆 Date: {latest_date}")
                else:
                    self.text_update.emit("❌ ต้องการข้อมูลอย่างน้อย 1 วัน")
                    return ax

                stations = []
                for record in data_synop:
                    station_info = next(
                        (
                            s
                            for s in data_station
                            if s["station_id"] == record["station_id"]
                        ),
                        None,
                    )
                    if not station_info:
                        continue

                    try:
                        main = record.get("main", {})

                        info_irix = main.get("IrIxhVV", "00000")
                        info_nddff = main.get("Nddff", "00000")
                        info_temp = main.get("1SnTTT", "00000")
                        info_dewp = main.get("2SnTdTdTd", "00000")
                        info_pres = main.get("4PPPP", "00000")
                        info_pres_tend = main.get("5appp", "00000")
                        info_weather = main.get("7wwW1W2", "00000")
                        info_cloud = main.get("8NhClCmCH", "00000")

                        if info_pres[0:2] != "40":
                            continue

                        ff_raw = self.safe_slice_int(info_nddff, 3, 5)
                        dd = (
                            self.safe_slice_int(info_nddff, 1, 3) * 10
                            if ff_raw >= 3
                            else 0
                        )
                        ff = ff_raw if ff_raw >= 3 else 0

                        stations.append(
                            {
                                "station_id": record["station_id"],
                                "lat": float(station_info["location"]["latitude"]),
                                "lon": float(station_info["location"]["longitude"]),
                                "h": info_irix[2:3],
                                "vv": self.safe_slice_int(info_irix, 3, 5),
                                "n": (
                                    0
                                    if info_nddff[0:1] == "/"
                                    else self.safe_slice_int(info_nddff, 0, 1)
                                ),
                                "dd": dd,
                                "ff": ff,
                                "nt": self.safe_slice_int(info_temp, 1, 2),
                                "TTT": self.safe_slice_float(
                                    info_temp, 2, 5, scale=0.1
                                ),
                                "nd": self.safe_slice_int(info_dewp, 1, 2),
                                "DDD": self.safe_slice_float(
                                    info_dewp, 2, 5, scale=0.1
                                ),
                                "pppp": self.safe_slice_int(info_pres, 1, 5),
                                "ap": self.safe_slice_int(info_pres_tend, 1, 2),
                                "appp": self.safe_slice_int(info_pres_tend, 2, 5),
                                "ww": self.safe_slice_int(info_weather, 1, 3),
                                "Nh": self.safe_slice_int(info_cloud, 1, 2),
                                "Cl": self.safe_slice_int(info_cloud, 2, 3),
                                "Cm": self.safe_slice_int(info_cloud, 3, 4),
                                "Ch": self.safe_slice_int(info_cloud, 4, 5),
                            }
                        )
                    except Exception as e:
                        self.text_update.emit(
                            f"⚠️ Parse error for station {record['station_id']}: {e}"
                        )
                        continue

                # ✅ ย้ายมาที่นี่
                self.write_json(self.json_data_plot_surface_file, stations)
                self.text_update.emit(f"✅ Parsed {len(stations)} stations")

                if not stations:
                    self.text_update.emit("❌ No stations to plot")
                    return ax

                # ▶️ สร้าง DataFrame และแปลงพิกัด
                df = pd.DataFrame(stations)

                transformer = Transformer.from_crs(
                    "EPSG:4326", "EPSG:3857", always_xy=True
                )
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
                limit = 150000.0 * ((100 - limit) / 30.0) * units.meter
                self.text_update.emit(f"▶️ ลดความหนาแน่นจุด: {limit:.0f}")

                # แปลงจากพิกัดละติจูด/ลองจิจูด (WGS84) → พิกัดเมตร (Web Mercator)
                mask = reduce_point_density(point_locs * units.meter, limit)

                # mask = reduce_point_density(
                #    point_locs * units.meter, 150000.0 * units.meter
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
                    self.text_update.emit("▶️ Plot Surface สถานีด้วย MetPy")
                    df_north = df[df["lat"] >= 0]
                    df_south = df[df["lat"] < 0]

                    # ▶️ ฟังก์ชัน plot ทุกอย่างที่ไม่ใช่ลม (ใช้ร่วมได้)
                    def plot_station_surface(plot_obj, df_part):
                        df_part.loc[df_part["nt"] == 1, "TTT"] *= -1
                        df_part.loc[df_part["nd"] == 1, "DDD"] *= -1
                        plot_obj.plot_parameter(
                            "NW",
                            df_part["TTT"],
                            formatter=lambda v: f"{v:.1f}",
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "SW",
                            df_part["DDD"],
                            formatter=lambda v: f"{v:.1f}",
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "W2",
                            df_part["vv"],
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "SE",
                            df_part["Nh"].where(df_part["Nh"] != 0),
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            (1.3, 1),
                            df_part["pppp"],
                            formatter=lambda v: f"{int(v):03d}",
                            fontsize=10,
                            # color="red",
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "E",
                            df_part["appp"].where(
                                ~df_part["ap"].isin(["/", 9])
                            ),  # ✅ ตัด / และ 9 ออก
                            formatter=lambda v, ap=None: (
                                (
                                    ("-" if ap in [5, 6, 7, 8] else "+")
                                    if ap in [0, 1, 2, 3, 5, 6, 7, 8]
                                    else ""
                                )
                                + format(10 * abs(v), "02.0f")
                            ),
                            fontsize=10,
                            zorder=10,
                        )

                        # ▶️ Symbols
                        def clip_symbol(data, min_val, max_val):
                            return (
                                pd.Series(
                                    np.where(
                                        (data >= min_val) & (data <= max_val),
                                        data,
                                        np.nan,
                                    )
                                )
                                .dropna()
                                .astype(int)
                            )

                        # plot_obj.plot_symbol(
                        #    "W",
                        #    clip_symbol(df_part["ww"].astype(float), 0, 99),
                        #    current_weather,
                        #    fontsize=2,
                        #    zorder=10,
                        #    # color="red",
                        # )
                        plot_obj.plot_symbol(
                            "C",
                            clip_symbol(df_part["n"].astype(float), 0, 9),
                            sky_cover,
                            fontsize=10,
                            zorder=10,
                        )
                        plot_obj.plot_symbol(
                            "S",
                            clip_symbol(df_part["Cl"].astype(float), 0, 9),
                            low_clouds,
                            fontsize=10,
                            zorder=10,
                        )
                        plot_obj.plot_symbol(
                            "N",
                            clip_symbol(df_part["Cm"].astype(float), 0, 9),
                            mid_clouds,
                            fontsize=10,
                        )
                        plot_obj.plot_symbol(
                            "N2",
                            clip_symbol(df_part["Ch"].astype(float), 0, 9),
                            high_clouds,
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_symbol(
                            "E2",
                            clip_symbol(df_part["ap"].astype(float), 0, 9),
                            pressure_tendency,
                            fontsize=10,
                            zorder=10,
                        )

                        # ▶️ ชื่อสถานี
                        plot_obj.plot_text(
                            "NNE",
                            # (0, 1.5),
                            df_part["station_id"],
                            fontsize=8,
                            color="blue",
                            zorder=5,
                            alpha=0.5,
                        )

                    def plot_current_weather_symbols(ax, df_part):
                        # ✅ สีตามรหัส ww (0–99)
                        ww_color_map = {
                            **dict.fromkeys(range(0, 10), "saddlebrown"),
                            **dict.fromkeys(range(10, 20), "gold"),
                            **dict.fromkeys(range(20, 30), "red"),
                            **dict.fromkeys(range(30, 40), "sienna"),
                            **dict.fromkeys(range(40, 50), "orange"),
                            **dict.fromkeys(range(50, 60), "green"),
                            **dict.fromkeys(range(60, 70), "forestgreen"),
                            **dict.fromkeys(range(70, 80), "deepskyblue"),
                            **dict.fromkeys(range(80, 90), "darkviolet"),
                            **dict.fromkeys(range(90, 100), "firebrick"),
                        }

                        # ✅ คัดกรองเฉพาะค่าที่ valid
                        valid_mask = df_part["ww"].between(0, 99)
                        ww_codes = df_part.loc[valid_mask, "ww"].astype(int)
                        lons = df_part.loc[valid_mask, "lon"]
                        lats = df_part.loc[valid_mask, "lat"]

                        # ✅ วาดรายจุด
                        for lon, lat, ww_code in zip(lons, lats, ww_codes):
                            color = ww_color_map.get(ww_code, "black")
                            plot = StationPlot(
                                ax,
                                [lon],
                                [lat],
                                transform=ccrs.PlateCarree(),
                                fontsize=10,
                                spacing=13,
                                zorder=10,
                            )
                            plot.plot_symbol(
                                "W",
                                [ww_code],
                                current_weather,  # ต้อง import มาก่อนจาก metpy.plots
                                fontsize=10,
                                zorder=10,
                                color=color,
                            )

                    # ✅ ตั้งค่าขนาดเริ่มต้นสำหรับ wind barb (ใช้ร่วมกันทั้งซีกโลกเหนือและใต้)
                    barb_defaults = {"sizes": {"emptybarb": 0.2}}

                    # ▶️ ซีกโลกเหนือ
                    if not df_north.empty:
                        u_n = -df_north["ff"] * np.sin(np.radians(df_north["dd"]))
                        v_n = -df_north["ff"] * np.cos(np.radians(df_north["dd"]))

                        plot_n = StationPlot(
                            ax,
                            df_north["lon"].values,
                            df_north["lat"].values,
                            transform=ccrs.PlateCarree(),
                            fontsize=5,
                            spacing=13,
                            zorder=5,
                        )

                        plot_station_surface(plot_n, df_north)
                        plot_current_weather_symbols(ax, df_north)

                        plot_n.plot_barb(
                            np.nan_to_num(u_n),
                            np.nan_to_num(v_n),
                            flip_barb=False,
                            linewidth=0.8,
                            length=8,  # ✅ ให้เท่ากับซีกโลกใต้
                            zorder=10,
                            fill_empty=False,
                            sizes=barb_defaults[
                                "sizes"
                            ],  # ✅ เพิ่ม sizes เพื่อให้ใช้ค่าที่กำหนด
                        )

                    # ▶️ ซีกโลกใต้
                    if not df_south.empty:
                        u_s = -df_south["ff"] * np.sin(np.radians(df_south["dd"]))
                        v_s = -df_south["ff"] * np.cos(np.radians(df_south["dd"]))

                        plot_s = StationPlot(
                            ax,
                            df_south["lon"].values,
                            df_south["lat"].values,
                            transform=ccrs.PlateCarree(),
                            fontsize=5,
                            spacing=13,
                            zorder=5,
                        )

                        plot_station_surface(plot_s, df_south)
                        plot_current_weather_symbols(ax, df_south)

                        plot_s.plot_barb(
                            np.nan_to_num(u_s),
                            np.nan_to_num(v_s),
                            flip_barb=True,
                            linewidth=0.8,
                            length=8,
                            zorder=10,
                            fill_empty=False,
                            sizes=barb_defaults["sizes"],  # ✅ ใช้ค่าขนาดเดียวกัน
                        )

                    self.text_update.emit("✅ Plot Surface สถานีด้วย MetPy")
                except Exception as e:
                    self.text_update.emit(f"❌ Plot Surface Error: {e}")
            except Exception as e:
                self.text_update.emit(f"❌ Unexpected error in Plot Surface: {e}")

        else:
            try:
                self.text_update.emit("🟡 Plot Suface Colors() Called")
                logger.info("🟡 Plot Suface Colors() Called")

                if not ax:
                    self.text_update.emit("❌ Map not initialized")
                    logger.error("❌ Map not initialized")
                    return

                # โหลดข้อมูล JSON เฉพาะ surface 2 day เท่านั้น
                data_synop = self.load_json(self.json_data_surface2day_file)
                self.text_update.emit(
                    f"📄 Loaded parsed surface 2 day data: {len(data_synop)} entries"
                )

                data_station = self.load_json(self.json_station_world_file)
                self.text_update.emit(
                    f"📄 Loaded stations: {len(data_station)} entries"
                )

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
                data_previous = [
                    r for r in data_synop if r.get("date") == previous_date
                ]
                data_previous_dict = {r["station_id"]: r for r in data_previous}

                stations = []
                for record_today in data_latest:
                    station_id = record_today.get("station_id")
                    record_yesterday = data_previous_dict.get(station_id)

                    station_info = next(
                        (s for s in data_station if s["station_id"] == station_id), None
                    )
                    if not station_info:
                        continue

                    try:
                        info_irix = record_today.get("main", {}).get("IrIxhVV", "00000")
                        info_nddff = record_today.get("main", {}).get("Nddff", "00000")
                        info_temp = record_today.get("main", {}).get("1SnTTT", "00000")
                        info_dewp = record_today.get("main", {}).get(
                            "2SnTdTdTd", "00000"
                        )

                        pres_today = record_today.get("main", {}).get("4PPPP", "")

                        info_pres_tend = record_today.get("main", {}).get(
                            "5appp", "00000"
                        )
                        info_weather = record_today.get("main", {}).get(
                            "7wwW1W2", "00000"
                        )
                        info_cloud = record_today.get("main", {}).get(
                            "8NhClCmCH", "00000"
                        )

                        if not pres_today.startswith("40"):
                            continue

                        if not record_yesterday:
                            delta_p = round(p_today, 1)

                        else:
                            pres_yesterday = record_yesterday.get("main", {}).get(
                                "4PPPP", ""
                            )

                            def parse_pressure(p_str):
                                sub = p_str[2:5].replace("/", "0")
                                return (
                                    1000.0 + (int(sub) / 10.0)
                                    if sub.isdigit()
                                    else None
                                )

                            p_today = parse_pressure(pres_today)
                            p_yesterday = parse_pressure(pres_yesterday)
                            delta_p = round(p_today - p_yesterday, 1)

                        ff_raw = self.safe_slice_int(info_nddff, 3, 5)
                        dd = (
                            self.safe_slice_int(info_nddff, 1, 3) * 10
                            if ff_raw >= 3
                            else 0
                        )
                        ff = ff_raw if ff_raw >= 3 else 0

                        stations.append(
                            {
                                "station_id": station_id,
                                "lat": float(station_info["location"]["latitude"]),
                                "lon": float(station_info["location"]["longitude"]),
                                "h": info_irix[2:3],
                                "vv": self.safe_slice_int(info_irix, 3, 5),
                                "n": (
                                    0
                                    if info_nddff[0:1] == "/"
                                    else self.safe_slice_int(info_nddff, 0, 1)
                                ),
                                "dd": dd,
                                "ff": ff,
                                "nt": self.safe_slice_int(info_temp, 1, 2),
                                "TTT": self.safe_slice_float(
                                    info_temp, 2, 5, scale=0.1
                                ),
                                "nd": self.safe_slice_int(info_dewp, 1, 2),
                                "DDD": self.safe_slice_float(
                                    info_dewp, 2, 5, scale=0.1
                                ),
                                "cc": delta_p,
                                "pppp": self.safe_slice_int(pres_today, 1, 5),
                                "ap": self.safe_slice_int(info_pres_tend, 1, 2),
                                "appp": self.safe_slice_int(info_pres_tend, 2, 5),
                                "ww": self.safe_slice_int(info_weather, 1, 3),
                                "Nh": self.safe_slice_int(info_cloud, 1, 2),
                                "Cl": self.safe_slice_int(info_cloud, 2, 3),
                                "Cm": self.safe_slice_int(info_cloud, 3, 4),
                                "Ch": self.safe_slice_int(info_cloud, 4, 5),
                            }
                        )
                    except Exception as e:
                        self.main_window.textarea.append(
                            f"⚠️ Parse error for station {station_id}: {e}"
                        )
                        continue

                # ✅ ย้ายมาที่นี่
                self.write_json(self.json_data_plot_surface_file, stations)
                self.text_update.emit(f"✅ Parsed {len(stations)} stations")
                logger.info(f"✅ Parsed {len(stations)} stations")

                if not stations:
                    self.text_update.emit("❌ No stations to plot")
                    logger.error("❌ No stations to plot")
                    return ax

                # ▶️ สร้าง DataFrame และแปลงพิกัด
                df = pd.DataFrame(stations)

                transformer = Transformer.from_crs(
                    "EPSG:4326", "EPSG:3857", always_xy=True
                )
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
                limit = 80000.0 * ((100 - limit) / 30.0) * units.meter
                self.text_update.emit(f"▶️ ลดความหนาแน่นจุด: {limit:.0f}")
                logger.info(f"▶️ ลดความหนาแน่นจุด: {limit:.0f}")

                # แปลงจากพิกัดละติจูด/ลองจิจูด (WGS84) → พิกัดเมตร (Web Mercator)
                mask = reduce_point_density(point_locs * units.meter, limit)

                # mask = reduce_point_density(
                #    point_locs * units.meter, 80000.0 * units.meter
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
                    logger.error("❌ No stations to plot")
                    return ax

                try:
                    self.text_update.emit("▶️ Plot Surface Colors สถานีด้วย MetPy")
                    logger.info("▶️ Plot Surface Colors สถานีด้วย MetPy")

                    df_north = df[df["lat"] >= 0]
                    df_south = df[df["lat"] < 0]

                    # ▶️ ฟังก์ชัน plot ทุกอย่างที่ไม่ใช่ลม (ใช้ร่วมได้)
                    def plot_station_detail(plot_obj, df_part):
                        df_part.loc[df_part["nt"] == 1, "TTT"] *= -1
                        df_part.loc[df_part["nd"] == 1, "DDD"] *= -1
                        plot_obj.plot_parameter(
                            "NW",
                            df_part["TTT"],
                            formatter=lambda v: f"{v:.1f}",
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "SW",
                            df_part["DDD"],
                            formatter=lambda v: f"{v:.1f}",
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "W2",
                            df_part["vv"],
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "SE",
                            df_part["Nh"].where(df_part["Nh"] != 0),
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            (1.3, 1),
                            df_part["pppp"],
                            formatter=lambda v: f"{int(v):03d}",
                            fontsize=10,
                            # color="red",
                            zorder=10,
                        )

                        plot_obj.plot_parameter(
                            "E",
                            df_part["appp"].where(
                                ~df_part["ap"].isin(["/", 9])
                            ),  # ✅ ตัด / และ 9 ออก
                            formatter=lambda v, ap=None: (
                                (
                                    ("-" if ap in [5, 6, 7, 8] else "+")
                                    if ap in [0, 1, 2, 3, 5, 6, 7, 8]
                                    else ""
                                )
                                + format(10 * abs(v), "02.0f")
                            ),
                            fontsize=10,
                            zorder=10,
                        )

                        # ▶️ Symbols
                        def clip_symbol(data, min_val, max_val):
                            return (
                                pd.Series(
                                    np.where(
                                        (data >= min_val) & (data <= max_val),
                                        data,
                                        np.nan,
                                    )
                                )
                                .dropna()
                                .astype(int)
                            )

                        # plot_obj.plot_symbol(
                        #    "W",
                        #    clip_symbol(df_part["ww"].astype(float), 0, 99),
                        #    current_weather,
                        #    fontsize=4,
                        #    zorder=10,
                        #    # color="red",
                        # )
                        # plot_obj.plot_symbol(
                        #    "C",
                        #    clip_symbol(df_part["n"].astype(float), 0, 9),
                        #    sky_cover,
                        #    fontsize=10,
                        #    zorder=10,
                        # )
                        plot_obj.plot_symbol(
                            "S",
                            clip_symbol(df_part["Cl"].astype(float), 0, 9),
                            low_clouds,
                            fontsize=10,
                            zorder=10,
                        )
                        plot_obj.plot_symbol(
                            "N",
                            clip_symbol(df_part["Cm"].astype(float), 0, 9),
                            mid_clouds,
                            fontsize=10,
                        )
                        plot_obj.plot_symbol(
                            "N2",
                            clip_symbol(df_part["Ch"].astype(float), 0, 9),
                            high_clouds,
                            fontsize=10,
                            zorder=10,
                        )

                        plot_obj.plot_symbol(
                            "E2",
                            clip_symbol(df_part["ap"].astype(float), 0, 9),
                            pressure_tendency,
                            fontsize=10,
                            zorder=10,
                        )

                        # ▶️ ชื่อสถานี
                        plot_obj.plot_text(
                            "NNE",
                            # (0, 1.5),
                            df_part["station_id"],
                            fontsize=8,
                            color="blue",
                            zorder=5,
                            alpha=0.5,
                        )

                    def plot_current_weather_symbols(ax, df_part):
                        # ✅ สีตามรหัส ww (0–99)
                        ww_color_map = {
                            **dict.fromkeys(range(0, 10), "saddlebrown"),
                            **dict.fromkeys(range(10, 20), "gold"),
                            **dict.fromkeys(range(20, 30), "red"),
                            **dict.fromkeys(range(30, 40), "sienna"),
                            **dict.fromkeys(range(40, 50), "orange"),
                            **dict.fromkeys(range(50, 60), "green"),
                            **dict.fromkeys(range(60, 70), "forestgreen"),
                            **dict.fromkeys(range(70, 80), "deepskyblue"),
                            **dict.fromkeys(range(80, 90), "darkviolet"),
                            **dict.fromkeys(range(90, 100), "firebrick"),
                        }

                        # ✅ คัดกรองเฉพาะค่าที่ valid
                        valid_mask = df_part["ww"].between(0, 99)
                        ww_codes = df_part.loc[valid_mask, "ww"].astype(int)
                        lons = df_part.loc[valid_mask, "lon"]
                        lats = df_part.loc[valid_mask, "lat"]

                        # ▶️ Symbols
                        def clip_symbol(data, min_val, max_val):
                            return (
                                pd.Series(
                                    np.where(
                                        (data >= min_val) & (data <= max_val),
                                        data,
                                        np.nan,
                                    )
                                )
                                .dropna()
                                .astype(int)
                            )

                        # ✅ วาดรายจุด
                        for lon, lat, ww_code, cc in zip(
                            lons, lats, ww_codes, df_part.loc[valid_mask, "cc"]
                        ):
                            color = ww_color_map.get(ww_code, "black")
                            plot = StationPlot(
                                ax,
                                [lon],
                                [lat],
                                transform=ccrs.PlateCarree(),
                                fontsize=10,
                                spacing=13,
                                zorder=10,
                            )

                            # กำหนดสีตามการเปลี่ยนแปลงของความกดอากาศ + สีน้ำเงิน - สีแดง = สีดำ
                            if pd.isna(cc) or cc == 0:
                                color = "black"
                            elif cc < 0:
                                color = "red"
                            else:
                                color = "blue"

                            # plot เมฆปกคลุมท้องฟ้า
                            plot.plot_symbol(
                                "C",
                                clip_symbol(df_part["n"].astype(float), 0, 9),
                                sky_cover,
                                fontsize=10,
                                zorder=10,
                                color=color,
                            )

                            # plot สภาพอากาศ
                            plot.plot_symbol(
                                "W",
                                [ww_code],
                                current_weather,  # ต้อง import มาก่อนจาก metpy.plots
                                fontsize=10,
                                zorder=10,
                                color=color,
                            )

                    # ✅ ตั้งค่าขนาดเริ่มต้นสำหรับ wind barb (ใช้ร่วมกันทั้งซีกโลกเหนือและใต้)
                    barb_defaults = {"sizes": {"emptybarb": 0.2}}

                    # ▶️ ซีกโลกเหนือ
                    if not df_north.empty:
                        u_n = -df_north["ff"] * np.sin(np.radians(df_north["dd"]))
                        v_n = -df_north["ff"] * np.cos(np.radians(df_north["dd"]))

                        plot_n = StationPlot(
                            ax,
                            df_north["lon"].values,
                            df_north["lat"].values,
                            transform=ccrs.PlateCarree(),
                            fontsize=5,
                            spacing=13,
                            zorder=5,
                        )

                        plot_station_detail(plot_n, df_north)
                        plot_current_weather_symbols(ax, df_north)

                        plot_n.plot_barb(
                            np.nan_to_num(u_n),
                            np.nan_to_num(v_n),
                            flip_barb=False,
                            linewidth=0.8,
                            length=8,  # ✅ ให้เท่ากับซีกโลกใต้
                            zorder=10,
                            fill_empty=False,
                            sizes=barb_defaults[
                                "sizes"
                            ],  # ✅ เพิ่ม sizes เพื่อให้ใช้ค่าที่กำหนด
                        )

                    # ▶️ ซีกโลกใต้
                    if not df_south.empty:
                        u_s = -df_south["ff"] * np.sin(np.radians(df_south["dd"]))
                        v_s = -df_south["ff"] * np.cos(np.radians(df_south["dd"]))

                        plot_s = StationPlot(
                            ax,
                            df_south["lon"].values,
                            df_south["lat"].values,
                            transform=ccrs.PlateCarree(),
                            fontsize=5,
                            spacing=13,
                            zorder=5,
                        )
                        plot_station_detail(plot_s, df_south)
                        plot_current_weather_symbols(ax, df_south)

                        plot_s.plot_barb(
                            np.nan_to_num(u_s),
                            np.nan_to_num(v_s),
                            flip_barb=True,
                            linewidth=0.8,
                            length=8,
                            zorder=10,
                            fill_empty=False,
                            sizes=barb_defaults["sizes"],  # ✅ ใช้ค่าขนาดเดียวกัน
                        )

                    self.text_update.emit("✅ Plot Surface Colors สถานีด้วย MetPy")
                    logger.info("✅ Plot Surface Colors สถานีด้วย MetPy")
                except Exception as e:
                    self.text_update.emit(f"❌ Plot Surface Colors Error: {e}")
                    logger.error(f"❌ Plot Surface Colors Error: {e}")
            except Exception as e:
                self.text_update.emit(
                    f"❌ Unexpected error in Plot Surface Colors: {e}"
                )
                logger.exception("❌ Unexpected error in Plot Surface Colors")

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
            logger.info(f"✅ JSON saved successfully: {path}")
            return True
        except Exception as e:
            self.text_update.emit(f"❌ Failed to write JSON: {e}")
            logger.error(f"❌ Failed to write JSON: {e}")
            return False
