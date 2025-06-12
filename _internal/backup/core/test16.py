import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import MultipleLocator
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from PIL import Image
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
logo_path = os.path.join(script_dir, "../images/icons/sfc-2.png")
output_file = os.path.join(script_dir, "../output/pressure.png")
output_file_2 = os.path.join(script_dir, "../output/pressure.pdf")

# ✅ เลือกขนาดกระดาษที่ต้องการใช้
paper_size = {
    "อต.ทอ. 1001": (38.58, 29.92),  # 980 × 760 mm
    "อต.ทอ. 1002": (27.36, 16.54),  # 695 × 420 mm
    "อต.ทอ. 1010": (25.39, 17.52),  # 645 × 445 mm
    "อต.ทอ. 1013": (29.53, 18.90),  # 750 × 480 mm
}

# === ขนาดภาพ ===
dpi = 300
dpi_2 = 600
#width_px = 4612
#height_px = 3210
#width_in = width_px / dpi
#height_in = height_px / dpi

width_in = 27.36
height_in = 16.54

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

# === ขอบเขต
ax.set_extent([45.0, 160.0, -30.0, 50.0], crs=ccrs.PlateCarree())

# === เพิ่มฟีเจอร์
ax.add_feature(cfeature.LAND, facecolor="#f4f1dc")
ax.add_feature(cfeature.OCEAN, facecolor="#a3c9f1")
ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
ax.add_feature(cfeature.BORDERS, linewidth=0.8)

# === เพิ่มเส้นกริด lat/lon
#gl = ax.gridlines(
#    draw_labels=True,
#    crs=ccrs.PlateCarree(),
#    linewidth=0.6,
#    color="gray",
#    alpha=0.6,
#    linestyle="--",
#)
#gl.xlocator = MultipleLocator(5)
#gl.ylocator = MultipleLocator(5)
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
#gl.xlabel_style = {"size": 10}
#gl.ylabel_style = {"size": 10}
#gl.top_labels = False
#gl.right_labels = False
#
## === เส้นกริดย่อย
#minor_x = MultipleLocator(1)
#minor_y = MultipleLocator(1)
#ax.xaxis.set_minor_locator(minor_x)
#ax.yaxis.set_minor_locator(minor_y)

# === วางโลโก้ภายในแผนที่ ด้วย ax.imshow()
logo_img = Image.open(logo_path)

# ปรับขนาดโลโก้ ~1 นิ้ว กว้าง
logo_width_in = 1.0
logo_width_px = int(logo_width_in * dpi)
logo_height_px = int(logo_img.height * (logo_width_px / logo_img.width))
logo_resized = logo_img.resize((logo_width_px, logo_height_px))
logo_array = np.asarray(logo_resized)

# พิกัดแผนที่ที่คุณอยากวาง (มุมล่างซ้าย)
logo_lon = 48
logo_lat = -28

# ขนาดโลโก้ในหน่วยองศา (คร่าว ๆ)
logo_width_deg = 8
logo_height_deg = 8 * (logo_resized.height / logo_resized.width)

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
