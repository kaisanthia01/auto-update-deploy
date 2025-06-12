import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches as patches

# === ขนาดกระดาษ: A3 แนวตั้ง x 3 (297 × 1260 mm) ===
fig = plt.figure(figsize=(11.69, 49.61), dpi=300)

# === Layout: 2 แถว × 3 คอลัมน์ ===
nrows, ncols = 2, 3

# === Margin & Spacing (อิงสัดส่วน) ===
margin_x = 0.05
margin_y = 0.03
spacing_x = 0.02
spacing_y = 0.02

# === คำนวณขนาดช่องแผนที่ ===
cell_width = (1.0 - 2 * margin_x - (ncols - 1) * spacing_x) / ncols
cell_height = (1.0 - 2 * margin_y - (nrows - 1) * spacing_y) / nrows

levels = ["850", "700", "500", "400", "300", "200"]

# === วาดแผนที่ 6 ช่อง ===
for idx, level in enumerate(levels):
    row = idx // ncols
    col = idx % ncols

    left = margin_x + col * (cell_width + spacing_x)
    bottom = 1.0 - margin_y - (row + 1) * cell_height - row * spacing_y  # 🔁 เรียงบนลงล่าง

    ax = fig.add_axes(
        [left, bottom, cell_width, cell_height],
        projection=ccrs.PlateCarree()
    )

    ax.coastlines()
    ax.set_title(f"{level} hPa", fontsize=10)

    # กรอบ debug
    ax.add_patch(patches.Rectangle(
        (0, 0), 1, 1,
        transform=ax.transAxes,
        linewidth=1.5,
        edgecolor="red",
        facecolor="none"
    ))

# === หัวเรื่องด้านบน ===
fig.text(0.5, 0.99, "04 JUN 2025", ha="center", va="top", fontsize=28, color="blue", weight="bold")
fig.text(0.5, 0.965, "0000 UTC", ha="center", va="top", fontsize=24, color="red", weight="bold")

# === Export
plt.savefig("upperwind_grid_3x2_A3x3_300dpi.png", dpi=300)
plt.show()
