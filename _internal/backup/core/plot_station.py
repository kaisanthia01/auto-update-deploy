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
from PyQt6.QtWidgets import QApplication
from cartopy.geodesic import Geodesic
from cartopy.feature import ShapelyFeature
import matplotlib.ticker as mticker
import re
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from datetime import datetime

# ตั้งค่าฟอนต์ภาษาไทย
script_dir = os.path.dirname(os.path.realpath(__file__))
fonts_data_path = os.path.join(script_dir, "..", "fonts")
font_path = os.path.join(fonts_data_path, "THSarabun.ttf")
font_bold_path = os.path.join(fonts_data_path, "THSarabun-Bold.ttf")
prop = (
    fm.FontProperties(fname=font_path, size=10) if os.path.exists(font_path) else None
)
prop_bold = (
    fm.FontProperties(fname=font_bold_path, size=10)
    if os.path.exists(font_bold_path)
    else None
)


class PlotStation:
    def __init__(self, main_window, splash=None):
        self.figure = None
        self.ax = None
        self.main_window = main_window
        self.splash = splash

        base_dir = os.path.join(script_dir, "..")
        # ไฟล์ข้อมูล สถานีตรวจอากาศ
        self.json_station_world_file = os.path.join(
            base_dir, "json", "synop_station_world_list.json"
        )

        # ไฟล์ข้อมูลสำหรับใช้ในการ Plot
        self.json_data_surface_file = os.path.join(
            base_dir, "json", "synop_data_surface.json"
        )
        self.json_data_pressure_file = os.path.join(
            base_dir, "json", "synop_data_pressure.json"
        )
        self.json_data_detail_file = os.path.join(
            base_dir, "json", "synop_data_detail.json"
        )
        self.json_data_upperwind_file = os.path.join(
            base_dir, "json", "synop_data_upperwind.json"
        )

        # ไฟล์ข้อมูลเปรียบเทียบสถานีแล้ว
        self.json_data_plot_surface_file = os.path.join(
            base_dir, "json", "synop_data_plot_surface.json"
        )
        self.json_data_plot_pressure_file = os.path.join(
            base_dir, "json", "synop_data_plot_pressure.json"
        )
        self.json_data_plot_detail_file = os.path.join(
            base_dir, "json", "synop_data_plot_detail.json"
        )
        self.json_data_plot_upperwind1_file = os.path.join(
            base_dir, "json", "synop_data_plot_upperwind1.json"
        )
        self.json_data_plot_upperwind2_file = os.path.join(
            base_dir, "json", "synop_data_plot_upperwind2.json"
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

    def create_map(self, type_map, cartopy_data_path=None):
        if not cartopy_data_path:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cartopy_data_path = os.path.join(script_dir, "..", "cartopy")

        # ✅ ตรวจสอบว่าโฟลเดอร์มีไฟล์ shapefile หรือยัง
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
            print("✅ ใช้ไฟล์แผนที่จากเครื่อง:", cartopy_data_path)
        else:
            print("🌐 ไม่มีไฟล์แมพในเครื่อง → โหลดออนไลน์จาก Natural Earth")

        # DPI สำหรับ export ชัด
        plt.rcParams["savefig.dpi"] = 600

        # ✅ เลือกขนาดกระดาษที่ต้องการใช้
        paper_size = {
            "อต.ทอ. 1001": (38.58, 29.92),  # 980 × 760 mm
            "อต.ทอ. 1002": (27.36, 16.54),  # 695 × 420 mm
            "อต.ทอ. 1010": (25.39, 17.52),  # 645 × 445 mm
            "อต.ทอ. 1013": (29.53, 18.90),  # 750 × 480 mm
        }

        # 🔹 ตั้งค่ากระดาษที่ต้องการ (เปลี่ยนค่าได้ตามกระดาษที่ต้องการใช้)
        selected_paper = "อต.ทอ. 1001"  # เลือกกระดาษขนาด 980 × 760 mm
        fig_width, fig_height = paper_size[selected_paper]

        # ✅ สร้าง figure อย่างถูกต้อง
        self.figure, ax = plt.subplots(
            # figsize=(980 / 25.4, 760 / 25.4),  # กำหนดขนาดตรงนี้เลย ไม่ต้องใช้ set_size_inches()
            figsize=(fig_width, fig_height),  # ✅ ใช้ขนาดที่คำนวณได้
            subplot_kw={"projection": ccrs.PlateCarree()},
            facecolor="#F0F7FF",
            # constrained_layout=False,
            constrained_layout=True,  # ✅ ใช้ constrained_layout อย่างเดียว
        )

        # พื้นที่กราฟหลังหัก 0.5 นิ้ว รอบขอบ
        # ✅ เผื่อขอบ 0.5 นิ้ว (ทั้ง 4 ด้าน)
        # fig_width = self.figure.get_figwidth()
        # fig_height = self.figure.get_figheight()
        # ax.set_position(
        #    [
        #        0.5 / fig_width,  # left
        #        0.5 / fig_height,  # bottom
        #        (fig_width - 1.0)
        #        / fig_width,  # width after removing 0.5 inch from left+right
        #        (fig_height - 1.0) / fig_height,  # height after removing top+bottom
        #    ]
        # )

        self.ax = ax  # ตั้งค่าให้ self.ax เพื่อให้ฟังก์ชันอื่นเรียกใช้ได้

        self._set_map_extent(ax, type_map)

        # ✅ แยกเพิ่มฟีเจอร์แมพตามเงื่อนไข
        if shapefiles_found:
            self._add_map_features(ax, cartopy_data_path, type_map)
        else:
            self._add_default_features(ax, type_map)

        # ✅ เพิ่มเส้นพรมแดนประเทศไทยเท่านั้น (ไม่ใช้รูปร่าง polygon)
        self._add_thailand_borderline_only(
            ax, cartopy_data_path, type_map, linewidth=0.5
        )

        # ✅ เพิ่มเส้นกริด
        self._add_inner_latlon_labels(
            ax, type_map, interval=5, color="gray", fontsize=7
        )

        self.add_logo(
            self.ax, os.path.join(script_dir, "..", "icons", "sfc-2.png"), type_map
        )

        return self.figure, ax

    def create_upperwind_combined_map(self, type_map):
        # กำหนดค่า DPI สำหรับการแสดงผลกราฟ เพื่อให้ข้อความชัดเจน
        plt.rcParams["savefig.dpi"] = 600

        # ✅ สร้าง figure ขนาด A4 แนวนอน
        fig_combined, axes = plt.subplots(
            2,
            3,
            figsize=(11.7, 8.3),  # A4 landscape
            subplot_kw={"projection": ccrs.PlateCarree()},
            facecolor="#F0F7FF",
            constrained_layout=True,
        )

        level_labels = [
            "850 hPa",
            "500 hPa",
            "300 hPa",
            "700 hPa",
            "400 hPa",
            "200 hPa",
        ]

        level_labels_2 = [
            "2000 ft.",
            "5000 ft.",
            "10000 ft.",
            "7000 ft.",
            "15000 ft.",
            "20000 ft.",
        ]

        cartopy_data_path = os.path.join(os.path.dirname(__file__), "..", "cartopy")

        # 🔎 ตรวจสอบว่ามี shapefile ในเครื่องหรือไม่
        shapefiles_found = (
            any(
                fname.endswith((".shp", ".dbf", ".shx"))
                for fname in os.listdir(cartopy_data_path)
            )
            if os.path.isdir(cartopy_data_path)
            else False
        )

        if shapefiles_found:
            print("✅ ใช้ไฟล์แผนที่จากเครื่อง:", cartopy_data_path)
        else:
            print("🌐 ไม่มีไฟล์แมพในเครื่อง → โหลดออนไลน์จาก Natural Earth")

        for i, ax in enumerate(axes.flat):
            self._set_map_extent(ax, type_map)
            ax.set_title("", fontsize=10)

            # 🔀 ใช้ฟังก์ชันที่เหมาะสมกับสถานการณ์
            if shapefiles_found:
                self._add_map_features(ax, cartopy_data_path, type_map)
            else:
                self._add_default_features(ax, type_map)

            # ✅ เพิ่มเส้นพรมแดนประเทศไทยเท่านั้น (ไม่ใช้รูปร่าง polygon)
            self._add_thailand_borderline_only(
                ax, cartopy_data_path, type_map, linewidth=0.5
            )

            # ✅ เพิ่มเส้นกริด
            self._add_inner_latlon_labels(
                ax, type_map, interval=5, color="gray", fontsize=7
            )

            self.add_logo(
                ax, os.path.join(script_dir, "..", "icons", "wind-2.png"), type_map
            )

            if type_map == 4:
                west, east, south, north = ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.170
                y_text = south + (north - south) * 0.130
                ax.text(
                    x_text,
                    y_text,
                    level_labels[i],
                    fontsize=7,
                    fontweight="bold",
                    color="blue",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )
            else:
                west, east, south, north = ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.170
                y_text = south + (north - south) * 0.130
                ax.text(
                    x_text,
                    y_text,
                    level_labels_2[i],
                    fontsize=7,
                    fontweight="bold",
                    color="blue",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

        return fig_combined, axes.flatten().tolist()

    def _set_map_extent(self, ax, type_map):
        if self.splash:
            self.splash.label.setText("🗺️ Setting up Latitude and Longitude")
            QApplication.processEvents()

        if type_map in [1, 2]:  # ผิวพื้น และความกดอากาศ
            # ทิศเหนือ จรดเส้นรุ้ง 50 องศาเหนือ, ทิศใต้ จรดเส้นรุ้ง -31 องศาใต้, ทิศตะวันออก จรดเส้นแวง 160 องศาตะวันออก, ทิศตะวันตก จรดเส้นแวง 45 องศาตะวันออก
            ax.set_extent([45.0, 160.0, 50.0, -30.0], crs=ccrs.PlateCarree())
        elif type_map == 4:  # ลมระดับหลัก
            # ทิศเหนือ จรดเส้นรุ้ง 45 องศาเหนือ, ทิศใต้ จรดเส้นรุ้ง -15 องศาใต้, ทิศตะวันออก จรดเส้นแวง 145 องศาตะวันออก, ทิศตะวันตก จรดเส้นแวง 60 องศาตะวันออก
            ax.set_extent([60.0, 145.0, 45.0, -15.0], crs=ccrs.PlateCarree())
        elif type_map == 5:  # ลมระดับรอง
            # ทิศเหนือ จรดเส้นรุ้ง 25 องศาเหนือ, ทิศใต้ จรดเส้นรุ้ง 5 องศาใต้, ทิศตะวันออก จรดเส้นแวง 125 องศาตะวันออก, ทิศตะวันตก จรดเส้นแวง 85 องศาตะวันออก
            ax.set_extent([85.0, 125.0, 25.0, -5.0], crs=ccrs.PlateCarree())
        else:  # ประเทศไทย
            # ทิศเหนือ จรดเส้นรุ้ง -1.5 องศาเหนือ, ทิศใต้ จรดเส้นรุ้ง 24.5 องศาใต้, ทิศตะวันออก จรดเส้นแวง 111.2 องศาตะวันออก, ทิศตะวันตก จรดเส้นแวง 93 องศาตะวันออก
            ax.set_extent([93.0, 111.2, -1.5, 24.5], crs=ccrs.PlateCarree())

    def _add_map_features(self, ax, cartopy_data_path, type_map):
        """เพิ่มสีพื้นหลัง, เส้นพรมแดน, ชื่อประเทศ, และชื่อทะเลลงบนแผนที่"""

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

        # ✅ อัปเดต Splash Screen
        if self.splash:
            self.splash.label.setText("🗺️ Downloading Map Features...")
            QApplication.processEvents()

        # ✅ สีพื้นหลังของแผนที่
        if type_map == 1:
            ax.add_feature(
                cfeature.LAND, facecolor="navajowhite", alpha=0.1
            )  # ✅ พื้นดิน (สีเนื้อ)
            ax.add_feature(
                cfeature.OCEAN,
                facecolor="lightblue",
                alpha=0.1,
            )  # ✅ พื้นน้ำ (เงินน้ำเงินอ่อน)

        try:
            # ✅ พล็อตเส้นพรมแดน (BORDERS)
            if os.path.exists(boundary_path):
                borders = shpreader.Reader(boundary_path)
                ax.add_geometries(
                    borders.geometries(),
                    crs=ccrs.PlateCarree(),
                    edgecolor="#a3a3a3",
                    facecolor="none",
                    linewidth=0.2,
                )
            else:
                ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor="#a3a3a3")

        except Exception as e:
            print(f"❌ Failed to add borders: {e}")

        try:
            # ✅ พล็อตแนวชายฝั่ง (COASTLINE)
            if os.path.exists(coast_path):
                coast = shpreader.Reader(coast_path)
                ax.add_geometries(
                    coast.geometries(),
                    crs=ccrs.PlateCarree(),
                    edgecolor="#a3a3a3",
                    facecolor="none",
                    linewidth=0.2,
                )
            else:
                ax.add_feature(cfeature.COASTLINE, linewidth=0.2, edgecolor="#a3a3a3")

        except Exception as e:
            print(f"❌ Failed to add coastline: {e}")

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
            print(f"❌ Failed to add country names: {e}")

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
            print(f"❌ Failed to add sea names: {e}")

    def _add_default_features(self, ax, type_map):
        if self.splash:
            self.splash.label.setText("🌐 Downloading Online Natural Earth")
            QApplication.processEvents()

        # แจ้งว่ากำลังโหลดออนไลน์
        print("🌐 ไม่มีไฟล์แมพในเครื่อง → โหลดออนไลน์จาก Natural Earth (อาจใช้เวลาสักครู่...)")

        # ปิดแสดง warning ซ้ำ ๆ
        warnings.simplefilter("default", DownloadWarning)

        ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor="#a3a3a3")
        ax.add_feature(cfeature.COASTLINE, linewidth=0.2, edgecolor="#a3a3a3")

        # ✅ สีพื้นหลังของแผนที่
        if type_map == 1:
            ax.add_feature(cfeature.LAND, facecolor="navajowhite")  # ✅ พื้นดิน (สีเนื้อ)
            ax.add_feature(
                cfeature.OCEAN, facecolor="lightblue"
            )  # ✅ พื้นน้ำ (เงินน้ำเงินอ่อน)

        # ax.add_feature(cfeature.LAND, facecolor="navajowhite")
        # ax.add_feature(cfeature.OCEAN, facecolor="lightblue")
        # ax.add_feature(cfeature.LAKES, facecolor="aliceblue")
        # ax.add_feature(cfeature.RIVERS, edgecolor="lightblue", linewidth=0.4)
        # ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", linestyle="--")

    def _add_thailand_borderline_only(
        self, ax, cartopy_data_path, type_map, linewidth=0.5
    ):
        shapefile_path = os.path.join(cartopy_data_path, "ne_50m_admin_0_countries.shp")

        if type_map in [1, 4, 5]:
            color = "darkred"
        elif type_map == 2:
            color = "black"
        else:
            color = "darkgreen"

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
                print("⚠️ ไม่พบเส้นพรมแดนของประเทศไทยใน shapefile นี้")

        except Exception as e:
            print(f"❌ ไม่สามารถวาดเส้นพรมแดนประเทศไทย: {e}")

    def _add_inner_latlon_labels(
        self, ax, type_map, interval=5, color="black", fontsize=0.5
    ):
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

        if type_map == 3:
            start = 0
        else:
            start = 1

        # วาด label ลองจิจูด (แนวนอนล่างในกรอบ)
        for lon in lon_ticks[start:-1]:
            if west <= lon <= east:
                y_pos = south + dy
                if south < y_pos < north:
                    if type_map in [4, 5]:
                        if int(round(lon)) % 10 == 0:
                            label = (
                                f"{abs(int(round(lon)))}°E"
                                if lon >= 0
                                else f"{abs(int(round(lon)))}°W"
                            )
                            ax.text(
                                lon,
                                y_pos,
                                label,
                                fontsize=3,
                                color="#AAAAAA",
                                ha="center",
                                va="bottom",
                                transform=ccrs.PlateCarree(),
                                # bbox=dict(
                                #    facecolor="grey",
                                #    alpha=0.2,
                                #    edgecolor="none",
                                #    boxstyle="round,pad=0.2",
                                # ),
                                zorder=10,
                            )
                    else:
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
                            fontproperties=prop_bold,
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
                    if type_map in [4, 5]:
                        if int(round(lat)) % 10 == 0:
                            label = (
                                f"{abs(int(round(lat)))}°N"
                                if lat >= 0
                                else f"{abs(int(round(lat)))}°S"
                            )
                            ax.text(
                                x_pos + 0.5,
                                lat,
                                label,
                                fontsize=3,
                                color="#AAAAAA",
                                ha="left",
                                va="center",
                                transform=ccrs.PlateCarree(),
                                # bbox=dict(
                                #    facecolor="grey",
                                #    alpha=0.2,
                                #    edgecolor="none",
                                #    boxstyle="round,pad=0.2",
                                # ),
                                zorder=10,
                            )
                    else:
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
                            fontproperties=prop_bold,
                            color="#AAAAAA",
                            ha="left",
                            va="center",
                            transform=ccrs.PlateCarree(),
                            # bbox=dict(facecolor="white", alpha=1.0, edgecolor="none"),
                            zorder=10,
                        )

    def add_logo(self, ax, logo_path, type_map, zoom=0.03):
        """แสดงโลโก้ที่มุมล่างซ้ายของแผนที่"""
        try:
            if type_map == 3:
                zoom = 0.02
            elif type_map in [3, 4, 5]:
                zoom = 0.015

            img = Image.open(logo_path)
            imagebox = OffsetImage(img, zoom=zoom, dpi_cor=True)

            # ดึงขอบเขตพิกัดแผนที่
            extent = ax.get_extent(ccrs.PlateCarree())
            west, east, south, north = extent

            # วางไว้มุมล่างซ้าย (ขยับเข้าในเล็กน้อย)
            x = west + (east - west) * 0.1
            y = south + (north - south) * 0.1

            ab = AnnotationBbox(
                imagebox,
                (x, y),
                frameon=False,
                transform=ccrs.PlateCarree(),
                box_alignment=(0, 0),  # ซ้ายล่างของภาพเกาะกับตำแหน่ง
                zorder=20,
            )
            ax.add_artist(ab)

        except Exception as e:
            print(f"❌ Failed to add logo: {e}")

    def _add_station_map(self, ax, type_map):
        # ✅ ดึงขอบเขตของแผนที่
        west, east, south, north = ax.get_extent(ccrs.PlateCarree())

        # ✅ พล็อตจุดสถานีตรวจอากาศ - โหลดข้อมูลจากไฟล์ JSON
        data = self.load_json(self.json_station_world_file)

        # ✅ พล็อตสถานีตรวจอากาศจากข้อมูลใน JSON
        for station in data:  # ✅ วนลูปทีละสถานี
            lat = float(station["location"]["latitude"])  # ✅ แปลงเป็น float
            lon = float(station["location"]["longitude"])  # ✅ แปลงเป็น float
            # ✅ กรองเฉพาะชื่อประเทศที่อยู่ภายในขอบเขตแผนที่
            if west <= lon <= east and south <= lat <= north:
                # ✅ พล็อตจุดสถานีตรวจอากาศแบบวงกลมเปล่า
                ax.scatter(
                    lon,
                    lat,
                    marker="o",  # ✅ ใช้เครื่องหมายวงกลม
                    edgecolor="black",  # ✅ สีขอบของ Marker
                    facecolors="none",  # ✅ ทำให้เป็นวงกลมโปร่งใส
                    s=0.8,  # ✅ ใช้ s แทน markersize
                    linewidths=0.05,  # ✅ ลดความหนาของเส้นขอบให้เล็กที่สุด
                    alpha=0.5,
                    label="Station",
                )

                # ✅ เพิ่ม label แสดง station_id ใกล้กับจุดที่พล็อต
                ax.text(
                    lon + 0.0,  # ✅ ขยับตำแหน่งเล็กน้อยทางขวา
                    lat + 0.075,  # ✅ ขยับตำแหน่งเล็กน้อยขึ้นด้านบน
                    station["station_id"],  # ✅ ข้อความที่ต้องการแสดง
                    fontsize=0.5,  # ✅ ปรับขนาดตัวอักษรให้เล็ก
                    color="blue",  # ✅ กำหนดสีข้อความ
                    ha="center",  # ✅ จัดให้อยู่ตรงกลางแนวตั้ง
                    va="bottom",  # ✅ จัดให้อยู่ด้านล่างแนวนอน
                    transform=ccrs.PlateCarree(),
                    alpha=0.5,
                    fontproperties=prop_bold,
                    zorder=15,  # ✅ ให้ข้อความอยู่ด้านบนสุด
                )

    def plot_surface(self, date, time, limit):
        try:
            self.main_window.textarea.setText("🟡 Plot Surface() Called")
            if not self.ax or not self.figure:
                self.main_window.textarea.append("❌ Map not initialized")
                return

            # โหลดข้อมูล JSON เฉพาะ surface เท่านั้น
            data_synop = self.load_json(self.json_data_surface_file)
            self.main_window.textarea.append(
                f"📄 Loaded parsed surface data: {len(data_synop)} entries"
            )

            data_station = self.load_json(self.json_station_world_file)
            self.main_window.textarea.append(
                f"📄 Loaded stations: {len(data_station)} entries"
            )

            if not data_synop or not data_station:
                self.main_window.textarea.append("❌ Missing data file(s)")
                return self.figure, self.ax

            # ✅ ดึงวันที่ทั้งหมดจากข้อมูล synop และเรียงล่าสุดก่อน
            dates = sorted(
                {r.get("date") for r in data_synop if r.get("date")}, reverse=True
            )

            if len(dates) > 0:
                latest_date = dates[0]
                self.main_window.textarea.append(f"📆 Date: {latest_date}")
            else:
                self.main_window.textarea.append("❌ ต้องการข้อมูลอย่างน้อย 1 วัน")
                return self.figure, self.ax

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
                    info_weather = main.get("7wwW1W2", "00000")
                    info_cloud = main.get("8NhClCmCH", "00000")

                    if info_pres[0:2] != "40":
                        continue

                    ff_raw = self.safe_slice_int(info_nddff, 3, 5)
                    dd = (
                        self.safe_slice_int(info_nddff, 1, 3) * 10 if ff_raw >= 3 else 0
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
                            "TTT": self.safe_slice_float(info_temp, 2, 5, scale=0.1),
                            "nd": self.safe_slice_int(info_dewp, 1, 2),
                            "DDD": self.safe_slice_float(info_dewp, 2, 5, scale=0.1),
                            "pppp": self.safe_slice_int(info_pres, 1, 5),
                            "ww": self.safe_slice_int(info_weather, 1, 3),
                            "Nh": self.safe_slice_int(info_cloud, 1, 2),
                            "Cl": self.safe_slice_int(info_cloud, 2, 3),
                            "Cm": self.safe_slice_int(info_cloud, 3, 4),
                            "Ch": self.safe_slice_int(info_cloud, 4, 5),
                        }
                    )
                except Exception as e:
                    self.main_window.textarea.append(
                        f"⚠️ Parse error for station {record['station_id']}: {e}"
                    )
                    continue

            # ✅ ย้ายมาที่นี่
            self.write_json(self.json_data_plot_surface_file, stations)
            self.main_window.textarea.append(f"✅ Parsed {len(stations)} stations")

            if not stations:
                self.main_window.textarea.append("❌ No stations to plot")
                return self.figure, self.ax

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
            mask = reduce_point_density(
                point_locs * units.meter, 150000.0 * units.meter
            )
            df = df[mask]

            # ▶️ กรองขอบเขตแผนที่
            df = df[
                (df["lon"] >= 46.5)
                & (df["lon"] <= 159.5)
                & (df["lat"] >= -30.5)
                & (df["lat"] <= 48.8)
            ]

            if df.empty:
                self.main_window.textarea.append("❌ No stations to plot")
                return self.figure, self.ax

            try:
                self.main_window.textarea.append("▶️ Plot Surface สถานีด้วย MetPy")
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
                        fontproperties=prop_bold,
                        fontsize=2,
                        zorder=10,
                    )
                    plot_obj.plot_parameter(
                        "SW",
                        df_part["DDD"],
                        formatter=lambda v: f"{v:.1f}",
                        fontproperties=prop_bold,
                        fontsize=2,
                        zorder=10,
                    )
                    plot_obj.plot_parameter(
                        "W2",
                        df_part["vv"],
                        fontproperties=prop_bold,
                        fontsize=2,
                        zorder=10,
                    )
                    plot_obj.plot_parameter(
                        "SE",
                        df_part["Nh"].where(df_part["Nh"] != 0),
                        fontproperties=prop_bold,
                        fontsize=2,
                        zorder=10,
                    )
                    plot_obj.plot_parameter(
                        (1.3, 1),
                        df_part["pppp"],
                        formatter=lambda v: f"{int(v):03d}",
                        fontproperties=prop_bold,
                        fontsize=2,
                        color="red",
                        zorder=10,
                    )

                    # ▶️ Symbols
                    def clip_symbol(data, min_val, max_val):
                        return (
                            pd.Series(
                                np.where(
                                    (data >= min_val) & (data <= max_val), data, np.nan
                                )
                            )
                            .dropna()
                            .astype(int)
                        )

                    plot_obj.plot_symbol(
                        "W",
                        clip_symbol(df_part["ww"].astype(float), 0, 99),
                        current_weather,
                        fontproperties=prop_bold,
                        fontsize=2,
                        zorder=10,
                        # color="red",
                    )
                    plot_obj.plot_symbol(
                        "C",
                        clip_symbol(df_part["n"].astype(float), 0, 9),
                        sky_cover,
                        fontproperties=prop_bold,
                        fontsize=2.0,
                        zorder=10,
                    )
                    plot_obj.plot_symbol(
                        "S",
                        clip_symbol(df_part["Cl"].astype(float), 0, 9),
                        low_clouds,
                        fontproperties=prop_bold,
                        fontsize=2,
                        zorder=10,
                    )
                    plot_obj.plot_symbol(
                        "N",
                        clip_symbol(df_part["Cm"].astype(float), 0, 9),
                        mid_clouds,
                        fontproperties=prop_bold,
                        fontsize=2,
                    )
                    plot_obj.plot_symbol(
                        "N2",
                        clip_symbol(df_part["Ch"].astype(float), 0, 9),
                        high_clouds,
                        fontproperties=prop_bold,
                        fontsize=2,
                        zorder=10,
                    )

                    # ▶️ ชื่อสถานี
                    plot_obj.plot_text(
                        (0, 1.5),
                        df_part["station_id"],
                        fontproperties=prop_bold,
                        fontsize=2,
                        color="blue",
                        zorder=5,
                        alpha=0.5,
                    )

                # ✅ ตั้งค่าขนาดเริ่มต้นสำหรับ wind barb (ใช้ร่วมกันทั้งซีกโลกเหนือและใต้)
                barb_defaults = {"sizes": {"emptybarb": 0.2}}

                # ▶️ ซีกโลกเหนือ
                if not df_north.empty:
                    u_n = -df_north["ff"] * np.sin(np.radians(df_north["dd"]))
                    v_n = -df_north["ff"] * np.cos(np.radians(df_north["dd"]))

                    plot_n = StationPlot(
                        self.ax,
                        df_north["lon"].values,
                        df_north["lat"].values,
                        transform=ccrs.PlateCarree(),
                        fontsize=1.4,
                        spacing=1.5,
                        zorder=5,
                    )
                    plot_station_surface(plot_n, df_north)

                    plot_n.plot_barb(
                        np.nan_to_num(u_n),
                        np.nan_to_num(v_n),
                        flip_barb=False,
                        linewidth=0.1,
                        length=2.5,  # ✅ ให้เท่ากับซีกโลกใต้
                        zorder=10,
                        sizes=barb_defaults["sizes"],  # ✅ เพิ่ม sizes เพื่อให้ใช้ค่าที่กำหนด
                    )

                # ▶️ ซีกโลกใต้
                if not df_south.empty:
                    u_s = -df_south["ff"] * np.sin(np.radians(df_south["dd"]))
                    v_s = -df_south["ff"] * np.cos(np.radians(df_south["dd"]))

                    plot_s = StationPlot(
                        self.ax,
                        df_south["lon"].values,
                        df_south["lat"].values,
                        transform=ccrs.PlateCarree(),
                        fontsize=1.4,
                        spacing=1.5,
                        zorder=5,
                    )
                    plot_station_surface(plot_s, df_south)

                    plot_s.plot_barb(
                        np.nan_to_num(u_s),
                        np.nan_to_num(v_s),
                        flip_barb=True,
                        linewidth=0.1,
                        length=2.5,
                        zorder=10,
                        sizes=barb_defaults["sizes"],  # ✅ ใช้ค่าขนาดเดียวกัน
                    )

                # ▶️ Label
                date = re.sub("-", " ", date)
                west, east, south, north = self.ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.16125
                y_text = south + (north - south) * 0.1485
                self.ax.text(
                    x_text,
                    y_text,
                    f"{date}".upper(),
                    fontsize=10,
                    fontweight="bold",
                    color="blue",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                x_text = west + (east - west) * 0.160
                y_text = south + (north - south) * 0.140
                self.ax.text(
                    x_text,
                    y_text - 1.0,
                    f"{time}",
                    fontsize=10,
                    fontweight="bold",
                    color="red",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                x_text = west + (east - west) * 0.160
                y_text = south + (north - south) * 0.110
                self.ax.text(
                    x_text,
                    y_text,
                    "อต.ทอ. 1001",
                    fontsize=8,
                    fontproperties=prop_bold,
                    color="black",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                self.main_window.textarea.append("✅ Plot Surface สถานีด้วย MetPy")
            except Exception as e:
                self.main_window.textarea.append(f"❌ Plot Surface Error: {e}")
        except Exception as e:
            self.main_window.textarea.append(
                f"❌ Unexpected error in Plot Surface: {e}"
            )

        return self.figure, self.ax

    def plot_pressure(self, date, time, limit):
        try:
            self.main_window.textarea.setText("🟡 Plot Pressure() Called")
            if not self.ax or not self.figure:
                self.main_window.textarea.append("❌ Map not initialized")
                return

            # โหลดข้อมูล JSON เฉพาะ pressure เท่านั้น
            data_synop = self.load_json(self.json_data_pressure_file)
            self.main_window.textarea.append(
                f"📄 Loaded parsed pressure data: {len(data_synop)} entries"
            )

            data_station = self.load_json(self.json_station_world_file)
            self.main_window.textarea.append(
                f"📄 Loaded stations: {len(data_station)} entries"
            )

            if not data_synop or not data_station:
                self.main_window.textarea.append("❌ Missing data file(s)")
                return self.figure, self.ax

            # ✅ ดึงวันที่ทั้งหมดจากข้อมูล synop และเรียงล่าสุดก่อน
            all_dates = sorted(
                {r.get("date") for r in data_synop if r.get("date")}, reverse=True
            )

            if len(all_dates) < 2:
                self.main_window.textarea.append(
                    "❌ ต้องการข้อมูลอย่างน้อย 2 วันเพื่อเปรียบเทียบ"
                )
                return self.figure, self.ax

            latest_date = all_dates[0]
            previous_date = all_dates[1]
            self.main_window.textarea.append(
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

            self.write_json(self.json_data_plot_pressure_file, stations)
            self.main_window.textarea.append(f"✅ Parsed {len(stations)} stations")

            if not stations:
                self.main_window.textarea.append("❌ No stations to plot")
                return self.figure, self.ax

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
            mask = reduce_point_density(point_locs * units.meter, 50000.0 * units.meter)
            df = df[mask]

            # ▶️ กรองขอบเขตแผนที่
            df = df[
                (df["lon"] >= 46.5)
                & (df["lon"] <= 159.5)
                & (df["lat"] >= -30.5)
                & (df["lat"] <= 48.8)
            ]

            try:
                self.main_window.textarea.append("▶️ Plot Pressure สถานีด้วย MetPy")
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
                        self.ax,
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
                        fontproperties=prop_bold,
                        fontsize=3,
                        zorder=10,
                    )

                # ▶️ Label
                date = re.sub("-", " ", date)
                west, east, south, north = self.ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.16125
                y_text = south + (north - south) * 0.1485
                self.ax.text(
                    x_text,
                    y_text,
                    f"{date}".upper(),
                    fontsize=10,
                    fontweight="bold",
                    color="blue",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                x_text = west + (east - west) * 0.160
                y_text = south + (north - south) * 0.140
                self.ax.text(
                    x_text,
                    y_text - 1.0,
                    f"{time}",
                    fontsize=10,
                    fontweight="bold",
                    color="red",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                west, east, south, north = self.ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.160
                y_text = south + (north - south) * 0.110
                self.ax.text(
                    x_text,
                    y_text,
                    "อต.ทอ. 1010",
                    fontsize=8,
                    fontproperties=prop_bold,
                    color="black",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                self.main_window.textarea.append("✅ Plot Pressure สถานีด้วย MetPy")
            except Exception as e:
                self.main_window.textarea.append(f"❌ Plot Pressure Error: {e}")

        except Exception as e:
            self.main_window.textarea.append(
                f"❌ Unexpected error in Plot Pressure: {e}"
            )

        return self.figure, self.ax

    def plot_detail(self, date, time, limit):
        try:
            self.main_window.textarea.setText("🟡 Plot Detail() Called")
            if not self.ax or not self.figure:
                self.main_window.textarea.append("❌ Map not initialized")
                return

            # โหลดข้อมูล JSON เฉพาะ detail เท่านั้น
            data_synop = self.load_json(self.json_data_detail_file)
            self.main_window.textarea.append(
                f"📄 Loaded parsed detail data: {len(data_synop)} entries"
            )

            data_station = self.load_json(self.json_station_world_file)
            self.main_window.textarea.append(
                f"📄 Loaded stations: {len(data_station)} entries"
            )

            if not data_synop or not data_station:
                self.main_window.textarea.append("❌ Missing data file(s)")
                return self.figure, self.ax

            # ✅ ดึงวันที่ทั้งหมดจากข้อมูล synop และเรียงล่าสุดก่อน
            dates = sorted(
                {r.get("date") for r in data_synop if r.get("date")}, reverse=True
            )

            if len(dates) > 0:
                latest_date = dates[0]
                self.main_window.textarea.append(f"📆 Date: {latest_date}")
            else:
                self.main_window.textarea.append("❌ ต้องการข้อมูลอย่างน้อย 1 วัน")
                return self.figure, self.ax

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
                    info_weather = main.get("7wwW1W2", "00000")
                    info_cloud = main.get("8NhClCmCH", "00000")

                    if info_pres[0:2] != "40":
                        continue

                    ff_raw = self.safe_slice_int(info_nddff, 3, 5)
                    dd = (
                        self.safe_slice_int(info_nddff, 1, 3) * 10 if ff_raw >= 3 else 0
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
                            "TTT": self.safe_slice_float(info_temp, 2, 5, scale=0.1),
                            "nd": self.safe_slice_int(info_dewp, 1, 2),
                            "DDD": self.safe_slice_float(info_dewp, 2, 5, scale=0.1),
                            "pppp": self.safe_slice_int(info_pres, 1, 5),
                            "ww": self.safe_slice_int(info_weather, 1, 3),
                            "Nh": self.safe_slice_int(info_cloud, 1, 2),
                            "Cl": self.safe_slice_int(info_cloud, 2, 3),
                            "Cm": self.safe_slice_int(info_cloud, 3, 4),
                            "Ch": self.safe_slice_int(info_cloud, 4, 5),
                        }
                    )
                except Exception as e:
                    self.main_window.textarea.append(
                        f"⚠️ Parse error for station {record['station_id']}: {e}"
                    )
                    continue

            # ✅ ย้ายมาที่นี่
            self.write_json(self.json_data_plot_detail_file, stations)
            self.main_window.textarea.append(f"✅ Parsed {len(stations)} stations")

            if not stations:
                self.main_window.textarea.append("❌ No stations to plot")
                return self.figure, self.ax

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
            mask = reduce_point_density(point_locs * units.meter, 80000.0 * units.meter)
            df = df[mask]

            # ▶️ กรองขอบเขตแผนที่
            df = df[
                (df["lon"] >= 93)
                & (df["lon"] <= 111.2)
                & (df["lat"] >= -1.5)
                & (df["lat"] <= 24.5)
            ]

            if df.empty:
                self.main_window.textarea.append("❌ No stations to plot")
                return self.figure, self.ax

            try:
                self.main_window.textarea.append("▶️ Plot Detail สถานีด้วย MetPy")
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
                        fontproperties=prop_bold,
                        fontsize=1,
                        zorder=30,
                    )
                    plot_obj.plot_parameter(
                        "SW",
                        df_part["DDD"],
                        formatter=lambda v: f"{v:.1f}",
                        fontproperties=prop_bold,
                        fontsize=1,
                        zorder=30,
                    )
                    plot_obj.plot_parameter(
                        "W2",
                        df_part["vv"],
                        fontproperties=prop_bold,
                        fontsize=1,
                        zorder=30,
                    )
                    plot_obj.plot_parameter(
                        "SE",
                        df_part["Nh"].where(df_part["Nh"] != 0),
                        fontproperties=prop_bold,
                        fontsize=1,
                        zorder=30,
                    )
                    plot_obj.plot_parameter(
                        (1.5, 1),
                        df_part["pppp"],
                        formatter=lambda v: f"{int(v):03d}",
                        fontproperties=prop_bold,
                        fontsize=2,
                        color="red",
                        zorder=30,
                    )

                    # ▶️ Symbols
                    def clip_symbol(data, min_val, max_val):
                        return (
                            pd.Series(
                                np.where(
                                    (data >= min_val) & (data <= max_val), data, np.nan
                                )
                            )
                            .dropna()
                            .astype(int)
                        )

                    plot_obj.plot_symbol(
                        "W",
                        clip_symbol(df_part["ww"].astype(float), 0, 99),
                        current_weather,
                        fontproperties=prop_bold,
                        fontsize=1,
                        zorder=30,
                    )
                    plot_obj.plot_symbol(
                        "C",
                        clip_symbol(df_part["n"].astype(float), 0, 9),
                        sky_cover,
                        fontproperties=prop_bold,
                        fontsize=1.0,
                        zorder=30,
                    )
                    plot_obj.plot_symbol(
                        "S",
                        clip_symbol(df_part["Cl"].astype(float), 0, 9),
                        low_clouds,
                        fontproperties=prop_bold,
                        fontsize=1,
                        zorder=30,
                    )
                    plot_obj.plot_symbol(
                        "N",
                        clip_symbol(df_part["Cm"].astype(float), 0, 9),
                        mid_clouds,
                        fontproperties=prop_bold,
                        fontsize=1,
                    )
                    plot_obj.plot_symbol(
                        "N2",
                        clip_symbol(df_part["Ch"].astype(float), 0, 9),
                        high_clouds,
                        fontproperties=prop_bold,
                        fontsize=1,
                        zorder=30,
                    )

                # ✅ ตั้งค่าขนาดเริ่มต้นสำหรับ wind barb (ใช้ร่วมกันทั้งซีกโลกเหนือและใต้)
                barb_defaults = {"sizes": {"emptybarb": 0.2}}

                # ▶️ ซีกโลกเหนือ
                if not df_north.empty:
                    u_n = -df_north["ff"] * np.sin(np.radians(df_north["dd"]))
                    v_n = -df_north["ff"] * np.cos(np.radians(df_north["dd"]))

                    plot_n = StationPlot(
                        self.ax,
                        df_north["lon"].values,
                        df_north["lat"].values,
                        transform=ccrs.PlateCarree(),
                        fontsize=0.7,
                        spacing=1.0,
                        zorder=30,
                    )
                    plot_station_surface(plot_n, df_north)

                    plot_n.plot_barb(
                        np.nan_to_num(u_n),
                        np.nan_to_num(v_n),
                        flip_barb=False,
                        linewidth=0.1,
                        length=2.5,  # ✅ ให้เท่ากับซีกโลกใต้
                        zorder=30,
                        sizes=barb_defaults["sizes"],  # ✅ เพิ่ม sizes เพื่อให้ใช้ค่าที่กำหนด
                    )

                # ▶️ ซีกโลกใต้
                if not df_south.empty:
                    u_s = -df_south["ff"] * np.sin(np.radians(df_south["dd"]))
                    v_s = -df_south["ff"] * np.cos(np.radians(df_south["dd"]))

                    plot_s = StationPlot(
                        self.ax,
                        df_south["lon"].values,
                        df_south["lat"].values,
                        transform=ccrs.PlateCarree(),
                        fontsize=0.7,
                        spacing=1.0,
                        zorder=30,
                    )
                    plot_station_surface(plot_s, df_south)

                    plot_s.plot_barb(
                        np.nan_to_num(u_s),
                        np.nan_to_num(v_s),
                        flip_barb=True,
                        linewidth=0.1,
                        length=2.5,
                        zorder=30,
                        sizes=barb_defaults["sizes"],  # ✅ ใช้ค่าขนาดเดียวกัน
                    )

                # ▶️ Label
                date = re.sub("-", " ", date)
                west, east, south, north = self.ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.180
                y_text = south + (north - south) * 0.130
                self.ax.text(
                    x_text,
                    y_text,
                    f"{date}".upper(),
                    fontsize=5,
                    fontweight="bold",
                    color="blue",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                west, east, south, north = self.ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.180
                y_text = south + (north - south) * 0.155
                self.ax.text(
                    x_text,
                    y_text - 1.0,
                    f"{time}",
                    fontsize=5,
                    fontweight="bold",
                    color="red",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                west, east, south, north = self.ax.get_extent(ccrs.PlateCarree())
                x_text = west + (east - west) * 0.180
                y_text = south + (north - south) * 0.107
                self.ax.text(
                    x_text,
                    y_text,
                    "อต.ทอ. 1003",
                    fontsize=5,
                    fontproperties=prop_bold,
                    color="black",
                    ha="center",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    zorder=30,
                )

                self.main_window.textarea.append("✅ Plot Detail สถานีด้วย MetPy")
            except Exception as e:
                self.main_window.textarea.append(f"❌ Plot Detail Error: {e}")
        except Exception as e:
            self.main_window.textarea.append(f"❌ Unexpected error in Plot Detail: {e}")

        return self.figure, self.ax

    def plot_upperwind1(self, date: str, time: str, limit: int, index_pressure: int):
        try:
            self.main_window.textarea.setText("🟡 Plot UpperWind1() Called")

            if not self.ax or not self.figure:
                self.main_window.textarea.append("❌ Map not initialized")
                return

            # ✅ กำหนดระดับแรงดันอากาศตามลำดับที่ต้องการ
            levels_target = [850, 500, 300, 700, 400, 200]
            level_labels = [
                "850 hPa",
                "500 hPa",
                "300 hPa",
                "700 hPa",
                "400 hPa",
                "200 hPa",
            ]

            # ✅ ตรวจสอบว่า index_pressure อยู่ในระดับที่ต้องการ
            if index_pressure not in levels_target:
                self.main_window.textarea.append(
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
                self.main_window.textarea.append("❌ Missing data file(s)")
                return self.figure, self.ax

            # ✅ ตรวจสอบวันที่
            try:
                date_obj = datetime.strptime(date, "%d-%b-%Y")
                json_date = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                self.main_window.textarea.append("❌ Invalid date format")
                return self.figure, self.ax

            if isinstance(data_all, dict) and json_date in data_all:
                data_synop = data_all[json_date]
                self.main_window.textarea.append(f"📆 Date: {json_date}")
            else:
                self.main_window.textarea.append("❌ No data entries available in JSON")
                return self.figure, self.ax

            # ✅ จัดเก็บข้อมูลสถานี
            station_dict = {s["station_id"]: s for s in data_station}

            stations = []
            for station_id, record in data_synop.items():
                if station_id not in station_dict:
                    continue

                for entry in record.get("TTAA", []) + record.get("PPAA", []):
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
            mask = reduce_point_density(point_locs * units.meter, 5000.0 * units.meter)
            df = df[mask]

            # ▶️ กรองขอบเขตแผนที่
            df = df[
                (df["lon"] >= 60.0)
                & (df["lon"] <= 145.0)
                & (df["lat"] >= -15.0)
                & (df["lat"] <= 45.0)
            ]

            if df.empty:
                self.main_window.textarea.append("❌ No stations to plot")
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
                self.main_window.textarea.append(
                    f"▶️ Plot UpperWind - {pressure_label} ด้วย MetPy"
                )
                plot = StationPlot(
                    self.ax,
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
                    fontproperties=prop_bold,
                    fontsize=1.5,
                    color="red",
                    zorder=30,
                )

                # ▶️ ชื่อสถานี
                plot.plot_text(
                    "NW",
                    df["station_id"],
                    fontproperties=prop_bold,
                    fontsize=0.5,
                    color="blue",
                    zorder=10,
                )

                self.main_window.textarea.append(
                    f"✅ Plot UpperWind - {pressure_label} สำเร็จ"
                )

            except Exception as e:
                self.main_window.textarea.append(f"❌ Plot UpperWind - 1 Error: {e}")

        except Exception as e:
            self.main_window.textarea.append(f"❌ Error in plot_upperwind1: {e}")

        return self.figure, self.ax

    def plot_upperwind2(self, date: str, time: str, limit: int):
        try:
            self.main_window.textarea.setText("🟡 Plot UpperWind2() Called")

            if not self.ax or not self.figure:
                self.main_window.textarea.append("❌ Map not initialized")
                return

            # แปลงรูปแบบวันที่
            try:
                date_obj = datetime.strptime(date, "%d-%b-%Y")  # "26-Mar-2025"
                json_date = date_obj.strftime("%Y-%m-%d")  # "2025-03-26"
            except ValueError:
                self.main_window.textarea.append("❌ Invalid date format")
                return self.figure, self.ax

            # โหลดข้อมูล JSON เฉพาะ upperwind เท่านั้น
            data_all = self.load_json(self.json_data_upperwind_file)
            self.main_window.textarea.append(
                f"📄 Loaded parsed upperwind data: {len(data_all)} entries"
            )

            data_station = self.load_json(self.json_station_world_file)
            self.main_window.textarea.append(
                f"📄 Loaded stations: {len(data_station)} entries"
            )

            if not data_all or not data_station:
                self.main_window.textarea.append("❌ Missing data file(s)")
                return self.figure, self.ax

            # ✅ ดึงวันที่ทั้งหมดจากข้อมูล synop และเรียงล่าสุดก่อน
            if isinstance(data_all, dict):
                if json_date in data_all:
                    data_synop = data_all[json_date]
                    self.main_window.textarea.append(f"📆 Date: {json_date}")
                else:
                    available_dates = sorted(data_all.keys(), reverse=True)
                    if available_dates:
                        latest_date = available_dates[0]
                        data_synop = data_all[latest_date]
                        self.main_window.textarea.append(
                            f"⚠️ Using latest available data: {latest_date}"
                        )
                    else:
                        self.main_window.textarea.append(
                            "❌ No data entries available in JSON"
                        )
                        return self.figure, self.ax
            else:
                self.main_window.textarea.append(
                    "❌ JSON structure is not a dictionary"
                )
                return self.figure, self.ax

            station_dict = {s["station_id"]: s for s in data_station}
            levels_target = [2000, 5000, 7000, 10000, 15000, 20000]

            stations = []
            for station_id, record in data_synop.items():
                if station_id not in station_dict:
                    continue

                for entry in record.get("PPBB", []):
                    pressure = entry.get("hPa./ft.")
                    if pressure not in levels_target:
                        continue

                    wind_dir = entry.get("wind_dir")
                    wind_speed = entry.get("wind_speed")
                    if wind_dir is None or wind_speed is None:
                        continue

                    if not (0 <= wind_dir <= 360):
                        self.main_window.textarea.append(
                            f"⚠️ Invalid wind_dir: {wind_dir} at {station_id}"
                        )
                        continue

                    if wind_speed == 0:
                        self.main_window.textarea.append(
                            f"ℹ️ Calm wind at {station_id}, skipping"
                        )
                        continue

                    station_info = station_dict[station_id]
                    stations.append(
                        {
                            "station_id": station_id,
                            "lat": float(station_info["location"]["latitude"]),
                            "lon": float(station_info["location"]["longitude"]),
                            "dd": wind_dir,
                            "ff": wind_speed,
                        }
                    )

            # ✅ ย้ายมาที่นี่
            self.write_json(self.json_data_plot_upperwind2_file, stations)
            self.main_window.textarea.append(f"✅ Parsed {len(stations)} stations")

            if not stations:
                self.main_window.textarea.append("❌ No valid station data to plot")
                return self.figure, self.ax

            # ▶️ สร้าง DataFrame และแปลงพิกัด
            df = pd.DataFrame(stations)

            # Coordinate transformation
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
            mask = reduce_point_density(point_locs * units.meter, 10000.0 * units.meter)
            df = df[mask]

            # ▶️ กรองขอบเขตแผนที่
            df = df[
                (df["lon"] >= 85.0)
                & (df["lon"] <= 125.0)
                & (df["lat"] >= -5.0)
                & (df["lat"] <= 25.0)
            ]

            if df.empty:
                self.main_window.textarea.append("❌ No stations to plot")
                return self.figure, self.ax

            # Convert direction and speed to vector
            angle_rad = np.radians(df["dd"])
            arrow_length = 0.5
            u_fixed = -np.sin(angle_rad) * arrow_length
            v_fixed = -np.cos(angle_rad) * arrow_length

            # ▶️ สร้างข้อความรหัสลมแบบ 5 หลัก เช่น 24515
            df["wnd"] = df.apply(
                lambda row: f"{int(row['dd']):03d}{int(row['ff']):02d}", axis=1
            )

            try:
                self.main_window.textarea.append("▶️ Plot UpperWind - 2 สถานีด้วย MetPy")
                plot = StationPlot(
                    self.ax,
                    df["lon"].values,
                    df["lat"].values,
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
                    # zorder=10,
                )

                # ▶️ ความเร็วลม
                plot.plot_text(
                    "S",
                    df["wnd"],
                    fontproperties=prop_bold,
                    fontsize=1.5,
                    color="red",
                    zorder=30,
                )

                self.main_window.textarea.append("✅ Plot UpperWind - 2 สถานีด้วย MetPy")
            except Exception as e:
                self.main_window.textarea.append(f"❌ Plot UpperWind - 2 Error: {e}")
        except Exception as e:
            self.main_window.textarea.append(
                f"❌ Error in plot_uppePlot UpperWind - 2: {e}"
            )

        return self.figure, self.ax

    def save_pdf(self, figure, ax, output_file_path, dpi=400):
        try:
            # ✅ กำหนดขนาดกระดาษ
            original_size = figure.get_size_inches()  # ✅ บันทึกขนาดเดิมก่อน

            # ✅ ตั้งค่าให้ตรงกับขนาดกระดาษพิมพ์
            # figure.set_size_inches(980 / 25.4, 760 / 25.4)  # แปลงจาก mm → นิ้ว

            # ✅ เผื่อขอบ 0.5 นิ้ว (ทั้ง 4 ด้าน)
            # fig_width = figure.get_figwidth()
            # fig_height = figure.get_figheight()
            #
            # ax.set_position(
            #    [
            #        0.5 / fig_width,  # left
            #        0.5 / fig_height,  # bottom
            #        (fig_width - 1.0)
            #        / fig_width,  # width after removing 0.5 inch from left+right
            #        (fig_height - 0.0) / fig_height,  # height after removing top+bottom
            #    ]
            # )

            figure.savefig(
                output_file_path,
                transparent=True,
                format="pdf",
                dpi=dpi,
                bbox_inches=None,  # ✅ ใช้ None เพื่อคงขนาดกระดาษ
                metadata={"Creator": "KRiT KAi", "Title": f"แผนที่ขนาด อต.ทอ. 1001"},
            )

            # figure.set_size_inches(original_size)  # ✅ คืนค่าขนาดเดิมหลังจาก save

            # figure.savefig(
            #    output_file_path,
            #    format="pdf",
            #    dpi=400,  # ✅ ความละเอียดสูง
            #    transparent=True,
            #    bbox_inches=None,  # ✅ คงขนาดกระดาษ
            #    metadata={
            #        "Title": "แผนที่ อต.ทอ. 1001",
            #        "Creator": "PlotStation",
            #    },
            # )

            return output_file_path
        except Exception as e:
            self.main_window.textarea.append(f"Error saving PDF: {e}")
            return e

    def save_png(self, figure, output_file_path, dpi=400):
        """
        บันทึกแผนที่เป็นไฟล์ PNG พร้อมกำหนดขนาดและความละเอียดสูงสำหรับการพิมพ์
        """
        try:
            # ✅ กำหนดขนาดภาพ
            # original_size = figure.get_size_inches()  # ✅ บันทึกขนาดเดิมก่อน
            #
            ## ✅ ตั้งค่าให้ตรงกับขนาดกระดาษพิมพ์
            # figure.set_size_inches(980 / 25.4, 760 / 25.4)  # แปลงจาก mm → นิ้ว
            #
            ## ✅ บันทึกไฟล์ภาพ
            # figure.savefig(
            #    output_file_path,
            #    format="png",
            #    dpi=dpi,
            #    bbox_inches=None,  # ✅ ใช้ None เพื่อคงขนาดกระดาษ
            #    transparent=True,  # ✅ PNG รองรับความโปร่งใส
            # )
            # figure.set_size_inches(original_size)  # ✅ คืนค่าขนาดเดิมหลังจาก save

            figure.savefig(
                output_file_path,
                format="png",
                dpi=400,  # ✅ DPI สูงสำหรับพิมพ์
                transparent=True,
                bbox_inches=None,  # ✅ ต้องเป็น None เพื่อไม่ให้ตัดขอบ
            )

            return output_file_path
        except Exception as e:
            self.main_window.textarea.append(f"❌ Error saving PNG: {e}")
            return e

    def load_json(self, path):
        if not os.path.exists(path):
            self.main_window.textarea.append(f"⚠️ File not found: {path}")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.main_window.textarea.append(f"⚠️ Failed to load JSON: {e}")
            return []

    def write_json(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.main_window.textarea.append(f"✅ JSON saved successfully: {path}")
            return True
        except Exception as e:
            self.main_window.textarea.append(f"❌ Failed to write JSON: {e}")
            return False
