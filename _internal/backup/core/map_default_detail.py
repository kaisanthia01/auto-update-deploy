import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import MultipleLocator
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from PIL import Image
import numpy as np
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import matplotlib.ticker as mticker
from cartopy.io import DownloadWarning
import warnings
import sys
import io
from matplotlib import font_manager as fm

# บังคับ stdout เป็น utf-8 (เฉพาะ Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
logo_path = os.path.join(script_dir, "../../images/icons/sfc-2.png")
output_file = os.path.join(script_dir, "../../output/detail.png")
output_file_2 = os.path.join(script_dir, "../../output/detail.pdf")

# ✅ เลือกขนาดกระดาษที่ต้องการใช้
paper_size = {"อต.ทอ.1003": (11.69, 16.54)}  # 420 × 297 mm

# === ขนาดภาพ ===
dpi = 300
dpi_2 = 600
# width_px = 3507
# height_px = 4962
# width_in = width_px / dpi
# height_in = height_px / dpi

# กำหนดชื่อกระดาษที่ต้องการใช้
paper_key = "อต.ทอ.1003"  # ตัวอย่าง: "อต.ทอ.1003"
print(f"📄 ขนาดกระดาษ: {paper_key}")

# ดึงขนาดกระดาษออกมา
if paper_key in paper_size:
    width_in, height_in = paper_size[paper_key]
    print(f"📏 ขนาดกระดาษ: {width_in} x {height_in} นิ้ว")
else:
    raise ValueError(f"❌ ไม่พบขนาดกระดาษ: {paper_key}")

# === เว้นขอบ ===
margin_in = 0.25
margin_x = margin_in / width_in
margin_y = margin_in / height_in

# === สร้างแผนที่ ===
fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)

ax = fig.add_axes(
    [margin_x, margin_y, 1 - 2 * margin_x, 1 - 2 * margin_y],
    projection=ccrs.PlateCarree(),
)

# === ขอบเขต
# ทิศเหนือ จรดเส้นรุ้ง -1.5 องศาเหนือ, ทิศใต้ จรดเส้นรุ้ง 24.5 องศาใต้, ทิศตะวันออก จรดเส้นแวง 111.2 องศาตะวันออก, ทิศตะวันตก จรดเส้นแวง 93 องศาตะวันออก
ax.set_extent([93.0, 111.2, -1.5, 24.5], crs=ccrs.PlateCarree())

# === เพิ่มฟีเจอร์
cartopy_data_path = None
if not cartopy_data_path:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
    cartopy_data_path = os.path.join(script_dir, "../../data/cartopy")

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
    print("ใช้ไฟล์แผนที่จากเครื่อง:", cartopy_data_path)
else:
    print("ไม่มีไฟล์แมพในเครื่อง → โหลดออนไลน์จาก Natural Earth")


# === ฟังก์ชันเสริม ===
def _add_map_features(ax, cartopy_data_path):
    """เพิ่มสีพื้นหลัง, เส้นพรมแดน, ชื่อประเทศ, และชื่อทะเลลงบนแผนที่"""
    boundary_path = os.path.join(
        cartopy_data_path, "ne_50m_admin_0_boundary_lines_land.shp"
    )
    coast_path = os.path.join(cartopy_data_path, "ne_50m_coastline.shp")
    countries_path = os.path.join(cartopy_data_path, "ne_110m_admin_0_countries.shp")
    marine_path = os.path.join(cartopy_data_path, "ne_10m_geography_marine_polys.shp")

    # ✅ สีพื้นหลังของแผนที่
    ax.add_feature(cfeature.LAND, facecolor="navajowhite", alpha=0.1)  # ✅ พื้นดิน (สีเนื้อ)
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


def _add_default_features(ax):
    # แจ้งว่ากำลังโหลดออนไลน์
    print("🌐 ไม่มีไฟล์แมพในเครื่อง → โหลดออนไลน์จาก Natural Earth (อาจใช้เวลาสักครู่...)")

    # ปิดแสดง warning ซ้ำ ๆ
    warnings.simplefilter("default", DownloadWarning)

    ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor="#a3a3a3")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.2, edgecolor="#a3a3a3")

    # ✅ สีพื้นหลังของแผนที่
    ax.add_feature(cfeature.LAND, facecolor="navajowhite")  # ✅ พื้นดิน (สีเนื้อ)
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue")  # ✅ พื้นน้ำ (เงินน้ำเงินอ่อน)


def _add_thailand_borderline_only(ax, cartopy_data_path, linewidth=0.5):
    """เพิ่มเส้นพรมแดนประเทศไทยเท่านั้น (ไม่ใช้รูปร่าง polygon)"""
    # โหลด shapefile ของประเทศไทย
    shapefile_path = os.path.join(cartopy_data_path, "ne_50m_admin_0_countries.shp")

    # สีเส้นพรมแดน
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


def _add_inner_latlon_labels(ax, interval=5, color="black", fontsize=0.5):
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

    start = 0

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
                    lon + dx + 0.25,
                    y_pos - 0.25,
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
                    lat + 0.15,
                    label,
                    fontsize=fontsize,
                    color="#AAAAAA",
                    ha="left",
                    va="center",
                    transform=ccrs.PlateCarree(),
                    # bbox=dict(facecolor="white", alpha=1.0, edgecolor="none"),
                    zorder=10,
                )


# === แยกเพิ่มฟีเจอร์แมพตามเงื่อนไข
if shapefiles_found:
    _add_map_features(ax, cartopy_data_path)
else:
    _add_default_features(ax)

# === เพิ่มเส้นพรมแดนประเทศไทยเท่านั้น (ไม่ใช้รูปร่าง polygon)
_add_thailand_borderline_only(ax, cartopy_data_path, linewidth=0.5)

# === เพิ่มเส้นกริด lat/lon
_add_inner_latlon_labels(ax, interval=5, color="gray", fontsize=7)

font_path = "fonts/Noto_Sans_Thai/static/NotoSansThai-Regular.ttf"
print(f"📜 โหลดฟอนต์จาก: {font_path}")

font = fm.FontProperties(fname=font_path)
print("📛 ฟอนต์ชื่อว่า:", font.get_name())

# === ตัวอักษรบนแผนที่ ===
# แสดงข้อความที่ตำแหน่งลองจิจูด 93.325, ละติจูด -1.42
# ข้อความที่แสดง
ax.text(
    93.06,  # ลองจิจูด (Longitude)
    -1.44,  # ละติจูด (Latitude)
    f"Date: XX XXX XXXX Time: XXXX UTC | Detail Map",  # ข้อความ
    transform=ccrs.PlateCarree(),  # ใช้พิกัดบนแผนที่
    fontsize=5,  # ขนาดตัวอักษร
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
    zorder=11,
)

# === ตัวอักษรบนแผนที่ ===
# แสดงข้อความที่ตำแหน่งลองจิจูด 95.0, ละติจูด -29.75
ax.text(
    99.0,  # ลองจิจูด (Longitude)
    -2.0,  # ละติจูด (Latitude)
    "XX XXX XXXX",  # ข้อความ
    transform=ccrs.PlateCarree(),  # ใช้พิกัดบนแผนที่
    fontsize=32,  # ขนาดตัวอักษร
    fontweight="bold",  # ตัวหนา
    color="blue",  # สีข้อความ
    ha="center",  # จัดกึ่งกลางแนวนอน
    va="center",  # จัดกึ่งกลางแนวตั้ง
    zorder=11,
)

# === ตัวอักษรบนแผนที่ ===
# แสดงข้อความที่ตำแหน่งลองจิจูด 105.0, ละติจูด -29.75
ax.text(
    105.0,  # ลองจิจูด (Longitude)
    -2.0,  # ละติจูด (Latitude)
    "XXXX UTC",  # ข้อความ
    transform=ccrs.PlateCarree(),  # ใช้พิกัดบนแผนที่
    fontsize=32,  # ขนาดตัวอักษร
    fontweight="bold",  # ตัวหนา
    color="red",  # สีข้อความ
    ha="center",  # จัดกึ่งกลางแนวนอน
    va="center",  # จัดกึ่งกลางแนวตั้ง
    zorder=11,
)


# DPI สำหรับ export ชัด
plt.rcParams["savefig.dpi"] = 600

# === บันทึกเป็น PNG ===
plt.savefig(output_file, dpi=dpi, bbox_inches="tight")

# === บันทึกเป็น PDF คุณภาพสูง ===
plt.savefig(output_file_2, dpi=dpi_2, bbox_inches="tight")
plt.close()

# ตรวจสอบ
img = Image.open(output_file)
print(f"Dimensions: {img.size} px")
print(f"DPI: {img.info.get('dpi')}")
