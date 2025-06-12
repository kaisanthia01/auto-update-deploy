import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cartopy.crs as ccrs

# === กำหนดจำนวนแถวและคอลัมน์ ===
nrows, ncols = 2, 3
fig = plt.figure(figsize=(8, 12))  # ปรับขนาดหน้ากระดาษ

# === Margin และ Spacing ===
margin_x = 0.05
margin_y = 0.05
spacing_x = 0.02
spacing_y = 0.02

# === คำนวณขนาดช่องย่อย ===
cell_width = (1.0 - 2 * margin_x - (ncols - 1) * spacing_x) / ncols
cell_height = (1.0 - 2 * margin_y - (nrows - 1) * spacing_y) / nrows

axes = []

for row in range(nrows):
    for col in range(ncols):
        left = margin_x + col * (cell_width + spacing_x)
        bottom = margin_y + row * (cell_height + spacing_y)
        bottom_flipped = 1.0 - bottom - cell_height  # 📌 บนลงล่าง

        ax = fig.add_axes(
            [left, bottom_flipped, cell_width, cell_height],
            projection=ccrs.PlateCarree()
        )

        # === เส้นกรอบสีแดงรอบแต่ละแผนที่ ===
        rect = patches.Rectangle(
            (0, 0), 1, 1,
            transform=ax.transAxes,
            linewidth=2,
            edgecolor="red",
            facecolor="none"
        )
        ax.add_patch(rect)

        # === ตกแต่งพื้นฐาน ===
        ax.set_title(f"Row {row + 1}, Col {col + 1}")
        ax.coastlines()
        axes.append(ax)

plt.show()
