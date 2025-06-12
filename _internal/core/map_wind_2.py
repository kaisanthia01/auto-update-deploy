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

logger = logging.getLogger("MapWind_2")


class MapWind_2(QThread):
    text_update = Signal(str)  # สัญญาณที่ส่งข้อความไปยัง MainWindow
    finished = Signal(str)  # ✅ เพิ่ม signal finished พร้อมส่ง path รูป

    def __init__(self):
        super(MapWind_2, self).__init__()
        self.figure = None
        self.ax = None
        self.font = None

        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
        # ไฟล์ข้อมูล สถานีตรวจอากาศ
        self.json_station_world_file = os.path.join(
            script_dir, "../data/json/synop_station_world_list.json"
        )

        # ไฟล์ข้อมูลสำหรับใช้ในการ Plot
        self.json_data_upperwind_file = os.path.join(
            script_dir, "../data/json/synop_data_upperwind_2.json"
        )

        # ไฟล์ข้อมูลเปรียบเทียบสถานีแล้ว
        self.json_data_plot_upperwind_file = os.path.join(
            script_dir, "../data/json/synop_data_plot_upperwind_2.json"
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
            map_name = "upperwind2"
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
                script_dir, "../output/map/" + map_name + "_749x459mm_300dpi.png"
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
            paper_size = {"อต.ทอ.1002": (35.08, 16.54)}  # 749 × 459 mm in inches

            # === ขนาดภาพ ===
            dpi = 300
            dpi_2 = 600
            dpi_3 = 600
            width_px = 10524
            height_px = 5550  # 4961
            width_in = width_px / dpi
            height_in = height_px / dpi

            # กำหนดชื่อกระดาษที่ต้องการใช้
            paper_key = "อต.ทอ.1002"  # ตัวอย่าง: "อต.ทอ.1003"
            logger.info(f"📄 ขนาดกระดาษ: {paper_key}")

            # ดึงขนาดกระดาษออกมา
            # if paper_key in paper_size:
            #    width_in, height_in = paper_size[paper_key]
            #    logger.info(f"📏 ขนาดกระดาษ: {width_in} x {height_in} นิ้ว")
            # else:
            #    logger.error(f"❌ ไม่พบขนาดกระดาษ: {paper_key}")
            #    raise ValueError(f"❌ ไม่พบขนาดกระดาษ: {paper_key}")

            # === สร้างแผนที่ ===
            fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)

            # ✅ คำนวณ
            ncols = 3
            nrows = 2

            axes = []  # เก็บ ax ทั้งหมด

            # === กำหนดขอบรอบข้างและ spacing
            margin_x = 0.005  # ขอบซ้ายและขวา (5 พิกเซลใน 1000 จะเท่ากับ 0.5%)
            margin_y = 0.001  # ขอบบนและล่าง (0.1%)
            spacing_x = 0.005  # ระยะห่างระหว่างคอลัมน์ (0.5%)
            spacing_y = 0.001  # ระยะห่างระหว่างแถว (0.1%)

            # === คำนวณพื้นที่ว่างที่เหลือ
            available_width = 1 - 2 * margin_x
            available_height = 1 - 2 * margin_y

            # === เอา spacing มาคิดด้วย
            cell_width = (available_width - (ncols - 1) * spacing_x) / ncols
            cell_height = (available_height - (nrows - 1) * spacing_y) / nrows

            for row in range(nrows):
                for col in range(ncols):
                    left = margin_x + col * (cell_width + spacing_x)
                    bottom = margin_y + (nrows - 1 - row) * (
                        cell_height + spacing_y
                    )  # 🛑 ตรงนี้สำคัญ
                    ax = fig.add_axes(
                        [left, bottom, cell_width, cell_height],
                        projection=ccrs.PlateCarree(),
                    )
                    axes.append(ax)

            levels_target = [2000, 5000, 7000, 10000, 15000, 20000]
            level_labels = [
                "2000 ft.",
                "5000 ft.",
                "10000 ft.",
                "7000 ft.",
                "15000 ft.",
                "20000 ft.",
            ]

            # ✅ ทดสอบเขียนชื่อแต่ละช่อง
            for idx, ax in enumerate(axes):
                # === ขอบเขตแผนที่ลมระดับรอง
                # ทิศเหนือ จรดเส้นรุ้ง 25 องศาเหนือ, ทิศใต้ จรดเส้นรุ้ง 5 องศาใต้, ทิศตะวันออก จรดเส้นแวง 125 องศาตะวันออก, ทิศตะวันตก จรดเส้นแวง 85 องศาตะวันออก
                ax.set_extent([85.0, 125.0, 25.0, -5.0], crs=ccrs.PlateCarree())

                # กำหนดชื่อแผนที่ตามระดับความกดอากาศ
                if idx < 3:
                    if idx == 1:
                        ax.set_title("     ", fontsize=32)
                else:
                    ax.set_title("", fontsize=0)

                # === เพิ่มฟีเจอร์
                cartopy_data_path = None
                if not cartopy_data_path:
                    script_dir = os.path.dirname(
                        os.path.abspath(__file__)
                    )  # ตำแหน่งไฟล์ .py
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
                    logger.info(
                        f"🔎 ใช้ไฟล์แผนที่จากเครื่อง: {cartopy_data_path} | {level_labels[idx]}"
                    )
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
                self._add_obs_map(ax, date, time, limit, levels_target[idx])

                # === วางโลโก้ภายในแผนที่ ด้วย ax.imshow()
                logo_img = Image.open(logo_path)

                # ปรับขนาดโลโก้ ~1 นิ้ว กว้าง
                logo_width_in = 1.0
                logo_width_px = int(logo_width_in * dpi)
                logo_height_px = int(logo_img.height * (logo_width_px / logo_img.width))
                logo_resized = logo_img.resize((logo_width_px, logo_height_px))
                logo_array = np.asarray(logo_resized)

                # พิกัดแผนที่ที่คุณอยากวาง (มุมล่างซ้าย)
                logo_lon = 86.5  # ตำแหน่งโลโก้ในพิกัดลองจิจูด
                logo_lat = -3.5  # ตำแหน่งโลโก้ในพิกัดละติจูด

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
                    interpolation="antialiased",
                )

                # === ตัวอักษรบนแผนที่ลมระดับรอง ===
                ax.text(
                    88.5,
                    -3.0,
                    f"{level_labels[idx]}",
                    transform=ccrs.PlateCarree(),
                    fontsize=10,
                    fontweight="bold",
                    color="blue",
                    ha="center",
                    va="bottom",
                    zorder=11,
                )

            # === เพิ่มตัวอักษรบนแผนที่ ===
            ax.text(
                -0.7,
                2.08,  # ตำแหน่งตรงกลางด้านบน (x=0.5 คือกลาง, y>1 คือเหนือ plot)
                f"{date}",
                transform=ax.transAxes,  # พิกัดตามแกน Axes (ไม่ใช่พิกัดทางภูมิศาสตร์)
                fontsize=32,
                fontweight="bold",
                color="blue",
                ha="center",
                va="bottom",
            )

            ax.text(
                -0.3,
                2.08,  # ตำแหน่งตรงกลางด้านบน (x=0.5 คือกลาง, y>1 คือเหนือ plot)
                f"{time[0:4]} UTC",
                transform=ax.transAxes,  # พิกัดตามแกน Axes (ไม่ใช่พิกัดทางภูมิศาสตร์)
                fontsize=32,
                fontweight="bold",
                color="red",
                ha="center",
                va="bottom",
            )

            # กำหนดค่า DPI สำหรับการบันทึกไฟล์
            plt.rcParams["savefig.dpi"] = 600

            # === บันทึกเป็น PNG 300 dpi ===
            plt.savefig(output_file, dpi=dpi, bbox_inches="tight")

            # === บันทึกเป็น PNG คุณภาพสูง 600 dpi ===
            # plt.savefig(output_file_2, dpi=dpi_2, bbox_inches="tight")

            # === บันทึกเป็น PDF คุณภาพสูง 600 dpi ===
            # plt.savefig(output_file_3, dpi=dpi_3, bbox_inches="tight")
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

            # ขนาดเป้าหมาย (749 x 459 mm ที่ 300 DPI)
            target_size = (8846, 5420)

            # ขยายแบบคุณภาพสูง
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)

            # บันทึกเป็น PNG พร้อม DPI 300
            resized_img.save(output_file_4, dpi=(300, 300))

            self.finished.emit(output_file)  # ✅ ส่ง path ไฟล์ออกไป
        except Exception as e:
            self.text_update.emit(f"❌ Error during map creation: {e}")

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
        ax.add_feature(
            cfeature.LAND, facecolor="none", alpha=0.1
        )  # ✅ พื้นดิน (สีเนื้อ)
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
                    linewidth=linewidth,
                    zorder=6,
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

    def _add_obs_map(self, ax, date=None, time=None, limit=None, index_pressure=0):
        try:
            self.text_update.emit(f"🟡 Plot UpperWind2() Called - {index_pressure} ft.")
            if not ax:
                self.text_update.emit("❌ Map not initialized")
                return

            # โหลดข้อมูล JSON เฉพาะ upperwind เท่านั้น
            data_synop = self.load_json(self.json_data_upperwind_file)
            self.text_update.emit(
                f"📄 Loaded parsed upperwind data: {len(data_synop)} entries"
            )
            logger.info(f"📄 Loaded parsed upperwind data: {len(data_synop)} entries")

            data_station = self.load_json(self.json_station_world_file)
            self.text_update.emit(f"📄 Loaded stations: {len(data_station)} entries")
            logger.info(f"📄 Loaded stations: {len(data_station)} entries")

            if not data_synop or not data_station:
                self.text_update.emit("❌ Missing data file(s)")
                return ax

            # ✅ กำหนดระดับแรงดันอากาศตามลำดับที่ต้องการ
            levels_target = [2000, 5000, 7000, 10000, 15000, 20000]
            level_labels = [
                "2000 ft.",
                "5000 ft.",
                "10000 ft.",
                "7000 ft.",
                "15000 ft.",
                "20000 ft.",
            ]

            # ✅ ตรวจสอบว่า index_pressure อยู่ในระดับที่ต้องการ
            if index_pressure not in levels_target:
                self.text_update.emit(
                    f"❌ index_pressure {index_pressure} ไม่อยู่ในระดับที่รองรับ: {levels_target}"
                )
                logger.error(
                    f"❌ index_pressure {index_pressure} ไม่อยู่ในระดับที่รองรับ: {levels_target}"
                )
                return self.figure, self.ax  # 🛑 หยุดการทำงาน

            # ✅ หาลำดับของ index_pressure
            pressure_index = levels_target.index(index_pressure)
            pressure_label = level_labels[pressure_index]

            # ✅ โหลดข้อมูล JSON
            data_all = self.load_json(self.json_data_upperwind_file)
            data_station = self.load_json(self.json_station_world_file)

            if not data_all or not data_station:
                self.text_update.emit("❌ Missing data file(s)")
                logger.error("❌ Missing data file(s)")
                return self.figure, self.ax

            # ✅ ตรวจสอบวันที่
            try:
                date_obj = datetime.strptime(date, "%d %b %Y")
                json_date = date_obj.strftime("%Y-%m-%d")
                # self.text_update.emit(f"📆 Date Format: {json_date}")
                logger.info(f"📆 Date: {json_date}")

            except ValueError:
                self.text_update.emit("❌ Invalid date format")
                logger.error("❌ Invalid date format")
                return self.figure, self.ax

            if isinstance(data_all, dict) and json_date in data_all:
                data_synop = data_all[json_date]
                self.text_update.emit(f"📆 Date Json: {json_date}")
                logger.info(f"📆 Date: {json_date}")
            else:
                self.text_update.emit("❌ No data entries available in JSON")
                logger.error("❌ No data entries available in JSON")
                return self.figure, self.ax

            # ✅ จัดเก็บข้อมูลสถานี
            station_dict = {s["station_id"]: s for s in data_station}

            stations = []
            for station_id, record in data_synop.items():
                if station_id not in station_dict:
                    continue

                for entry in record.get("PPBB", []):
                    pressure = entry.get("hPa./ft.")
                    if pressure != index_pressure:  # ✅ ใช้ index_pressure เท่านั้น
                        continue

                    wind_dir = entry.get("wind_dir")
                    wind_speed = entry.get("wind_speed")
                    if wind_dir is None or wind_speed is None:
                        continue

                    station_info = station_dict[station_id]
                    stations.append(
                        {
                            "station_id": station_id,
                            "lat": float(station_info["location"]["latitude"]),
                            "lon": float(station_info["location"]["longitude"]),
                            "pressure": pressure,
                            "dd": wind_dir,
                            "ff": wind_speed,
                        }
                    )

            # ✅ Save parsed data to JSON file
            self.write_json(self.json_data_plot_upperwind_file, stations)
            self.text_update.emit(f"✅ Parsed {len(stations)} stations")
            logger.info(f"✅ Parsed {len(stations)} stations")

            # ✅ แปลงข้อมูลเป็น DataFrame
            df = pd.DataFrame(stations)

            # ✅ กำหนดให้คอลัมน์ "pressure" เป็นลำดับที่กำหนด
            pressure_order = pd.CategoricalDtype(levels_target, ordered=True)
            df["pressure"] = df["pressure"].astype(pressure_order)

            # ✅ เรียงข้อมูลตามระดับความกดอากาศที่กำหนด
            df = df.sort_values(by="pressure")

            # ✅ แปลงพิกัดให้อยู่ในรูปแบบที่ถูกต้อง
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
            df["x_meter"], df["y_meter"] = transformer.transform(
                df["lon"].values, df["lat"].values
            )

            # ✅ ลดความหนาแน่นของจุด
            point_locs = xr.DataArray(
                np.stack([df["x_meter"], df["y_meter"]], axis=-1),
                dims=("points", "space"),
                attrs={"crs": ccrs.PlateCarree()},
            )

            # ลดความหนาแน่นจุด
            limit = 5000.0 * ((100 - limit) / 30.0) * units.meter
            self.text_update.emit(f"▶️ ลดความหนาแน่นจุด: {limit:.0f}")
            logger.info(f"▶️ ลดความหนาแน่นจุด: {limit:.0f}")

            # แปลงจากพิกัดละติจูด/ลองจิจูด (WGS84) → พิกัดเมตร (Web Mercator)
            mask = reduce_point_density(point_locs * units.meter, limit)

            # mask = reduce_point_density(
            #    point_locs * units.meter, 5000.0 * units.meter
            # )
            df = df[mask]

            # ▶️ กรองขอบเขตแผนที่
            df = df[
                (df["lon"] >= 85.0)
                & (df["lon"] <= 125.0)
                & (df["lat"] >= -5.0)
                & (df["lat"] <= 25.0)
            ]

            if df.empty:
                self.text_update.emit("❌ No stations to plot")
                logger.error("❌ No stations to plot")
                return self.figure, self.ax

            # ✅ คำนวณทิศทางและขนาดลูกศรลม
            angle_rad = np.radians(df["dd"])
            arrow_length = 0.5
            u_fixed = -np.sin(angle_rad) * arrow_length
            v_fixed = -np.cos(angle_rad) * arrow_length

            # ✅ สร้างข้อความรหัสลมแบบ 5 หลัก เช่น 24515
            df["wnd"] = df.apply(
                lambda row: f"{int(row['dd']):03d}{int(row['ff']):02d}", axis=1
            )

            try:
                self.text_update.emit(f"▶️ Plot UpperWind - {pressure_label} ด้วย MetPy")
                logger.info(f"▶️ Plot UpperWind - {pressure_label} ด้วย MetPy")

                # ▶️ สร้าง StationPlot
                plot = StationPlot(
                    ax,
                    df["lon"].values,
                    df["lat"].values,
                    clip_on=True,
                    transform=ccrs.PlateCarree(),
                    fontsize=1.5,
                    spacing=0.5,
                    zorder=10,
                )

                # ▶️ ลูกศรลม
                plot.plot_arrow(
                    np.nan_to_num(u_fixed.values),
                    np.nan_to_num(v_fixed.values),
                    scale=1.0,
                    scale_units="xy",
                    width=0.0005,
                    pivot="tail",
                    color="red",
                    zorder=30,
                )

                # ▶️ ความเร็วลม
                plot.plot_text(
                    "S",
                    df["wnd"],
                    fontproperties=self.font,
                    fontsize=1.5,
                    color="red",
                    zorder=30,
                )

                # ▶️ ชื่อสถานี
                plot.plot_text(
                    "NW",
                    df["station_id"],
                    fontproperties=self.font,
                    fontsize=0.5,
                    color="blue",
                    zorder=10,
                )

                self.text_update.emit("✅ Plot UpperWind2 สถานีด้วย MetPy")
                logger.info("✅ Plot UpperWind2 สถานีด้วย MetPy")

            except Exception as e:
                self.text_update.emit(f"❌ Plot UpperWind2 Error: {e}")
                logger.error(f"❌ Plot UpperWind2 Error: {e}")

        except Exception as e:
            self.text_update.emit(f"❌ Unexpected error in Plot UpperWind2: {e}")
            logger.error(f"❌ Unexpected error in Plot UpperWind2: {e}")

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
