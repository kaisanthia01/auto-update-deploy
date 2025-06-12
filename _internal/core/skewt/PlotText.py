import fitz


class PlotText:
    # ฟังก์ชันวาด PlotNews
    def plotNewsDraw(self, page, width, height, station_num, station_name, time, date, TTAA, TTBB):
        # วาดข้อความ Station ID
        time = time[:8]
        # เปลี่ยนพิกัด x, y จากขนาดภาพเป็นขนาดของ PDF
        x_pos = 7210 * (page.rect.width / width)
        y_pos = 5500 * (page.rect.height / height)
        page.insert_text(
            fitz.Point(x_pos, y_pos),
            f"{station_num}",
            fontsize=12,
            color=(0, 0, 1),
        )

        # วาดข้อความ Station Name
        # เปลี่ยนพิกัด x, y จากขนาดภาพเป็นขนาดของ PDF
        x_pos = 7900 * (page.rect.width / width)
        y_pos = 5500 * (page.rect.height / height)
        page.insert_text(
            fitz.Point(x_pos, y_pos),
            f"{station_name}",
            fontsize=12,
            color=(0, 0, 1),
        )

        # วาดข้อความ Time
        # เปลี่ยนพิกัด x, y จากขนาดภาพเป็นขนาดของ PDF
        x_pos = 7180 * (page.rect.width / width)
        y_pos = 5700 * (page.rect.height / height)
        page.insert_text(
            fitz.Point(x_pos, y_pos),
            f"{time}",
            fontsize=12,
            color=(0, 0, 1),
        )

        # วาดข้อความ Date
        # เปลี่ยนพิกัด x, y จากขนาดภาพเป็นขนาดของ PDF
        x_pos = 7835 * (page.rect.width / width)
        y_pos = 5700 * (page.rect.height / height)
        page.insert_text(
            fitz.Point(x_pos, y_pos),
            f"{date}",
            fontsize=12,
            color=(0, 0, 1),
        )

        # กำหนดพิกัดของสี่เหลี่ยม (x0, y0, x1, y1)
        rect = fitz.Rect(
            0 * (page.rect.width / width),
            4950 * (page.rect.height / height),
            1200 * (page.rect.width / width),
            5950 * (page.rect.height / height),
        )

        # วาดสี่เหลี่ยม พื้นหลังสีขาว ขอบสีดำ
        page.draw_rect(rect, color=(0, 0, 0), fill=(1, 1, 1), width=2)
        # ข้อความที่ต้องการใส่ในกล่อง
        text = (f"{TTAA}\n{TTBB}")
        # เพิ่ม padding (ขยับขอบเขตข้อความเข้ามา)
        padding = 5
        text_rect = fitz.Rect(
            rect.x0 + padding,
            rect.y0 + padding,
            rect.x1 - padding,
            rect.y1 - padding,
        )

        # ใส่ข้อความลงในกรอบของพื้นที่วาดสี่เหลี่ยม พร้อม text wrapping
        page.insert_textbox(
            text_rect, text, fontsize=8, color=(0, 0, 0), align=0
        )  # align=2 คือจัดกลาง
        
        #return station, time, date
