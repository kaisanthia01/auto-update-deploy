import math
import fitz

from core.skewt.PointY import PointY


class PlotWnd:

    # ฟังก์ชันวาด Wind Barb
    def plotWndDraw(self, page, width, height, plot, Marker):
        # สร้างอ็อบเจ็กต์ของ PointY
        pointY = PointY()
        key_old = 1100

        for key, values in Marker.items():
            # ตรวจสอบว่า key เป็น 'TP' และ value เป็น ' /////' หรือไม่
            if key == "TP":
                if isinstance(values, list) and len(values) > 0:
                    values = values[0]  # ดึงค่าแรกของลิสต์มาใช้

                if ":" in values:
                    int_key, wnd = values.split(":")
                    int_key = int(int_key[2:5])
                    if int_key == 999:
                        continue
                    else:
                        values = [wnd + "TP"]  # แปลงเป็นลิสต์ที่มีค่าสตริงเดียว

            elif key == "MX":
                if isinstance(values, list) and len(values) > 0:
                    values = values[0]  # ดึงค่าแรกของลิสต์มาใช้

                if ":" in values:
                    int_key, wnd = values.split(":")
                    int_key = int(int_key[2:5])
                    if int_key == 999:
                        continue
                    else:
                        values = [wnd + "MX"]  # แปลงเป็นลิสต์ที่มีค่าสตริงเดียว
            else:
                try:
                    # แปลง key เป็น int เพื่อเปรียบเทียบ
                    int_key = int(key)
                except ValueError:
                    continue  # ถ้า key ไม่สามารถแปลงเป็น int ได้ (เช่น 'TP') จะข้ามไปยัง key ถัดไป

                if plot == "925mb":
                    if int_key > 925:
                        continue

                if (
                    int_key != 925
                    and int_key != 850
                    and int_key != 700
                    and int_key != 500
                    and int_key != 400
                    and int_key != 300
                    and int_key != 250
                    and int_key != 200
                    and int_key != 150
                    and int_key != 100
                ):
                    if key_old - int_key < 5:
                        continue

            for value in values:
                if value == "/////":
                    continue  # ข้ามค่า "/////"

                else:
                    # print(f"int_key: {int_key}")
                    # print(f"value: {value}")
                    # ตรวจสอบระดับความกดอากาศ
                    if int_key > 1000:  # ระดับ SFC
                        if ":" in value:
                            mb, wnd = value.split(":")

                            # ตรวจสอบลม Calm ไม่ต้อง Plot เฉพาะระดับ SFC
                            if wnd == "00000":
                                continue

                            mb = mb[2:5]
                            mb_num = int(mb)
                            # print(f"Key: {mb_num}, Value: {wnd}")
                            # ----------------------------------------------------------- #

                            if mb_num < 51:
                                mb_num += 1000

                            if mb_num < 1000:
                                mb_start, mb_end = 1000, 950
                            else:
                                mb_start, mb_end = 1050, 1000

                            # ดึงค่าจาก PointY
                            pointY_val = [
                                int(pointY.get_value(str(mb_start))),
                                int(pointY.get_value(str(mb_end))),
                            ]
                            # print(f"pointY_val: {pointY_val}")

                            # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                            int_key = mb_num
                            key_old = mb_num
                            value = wnd
                            # print(f"key_old: {key_old}")
                            # ----------------------------------------------------------- #

                    elif int_key > 950 and int_key <= 1000:  # ระดับ 950mb - 1000mb
                        mb_start, mb_end = 1000, 950
                        pointY_val = [
                            int(pointY.get_value("1000")),
                            int(pointY.get_value("950")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 900 and int_key <= 950:  # ระดับ 900mb - 950mb
                        mb_start, mb_end = 950, 900
                        pointY_val = [
                            int(pointY.get_value("950")),
                            int(pointY.get_value("900")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 850 and int_key <= 900:  # ระดับ 850mb - 900mb
                        mb_start, mb_end = 900, 850
                        pointY_val = [
                            int(pointY.get_value("900")),
                            int(pointY.get_value("850")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 800 and int_key <= 850:  # ระดับ 800mb - 850mb
                        mb_start, mb_end = 850, 800
                        pointY_val = [
                            int(pointY.get_value("850")),
                            int(pointY.get_value("800")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 750 and int_key <= 800:  # ระดับ 750mb - 800mb
                        mb_start, mb_end = 800, 750
                        pointY_val = [
                            int(pointY.get_value("800")),
                            int(pointY.get_value("750")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 700 and int_key <= 750:  # ระดับ 700mb - 750mb
                        mb_start, mb_end = 700, 750
                        pointY_val = [
                            int(pointY.get_value("750")),
                            int(pointY.get_value("700")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 650 and int_key <= 700:  # ระดับ 650mb - 700mb
                        mb_start, mb_end = 700, 650
                        pointY_val = [
                            int(pointY.get_value("700")),
                            int(pointY.get_value("650")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 600 and int_key <= 650:  # ระดับ 600mb - 650mb
                        mb_start, mb_end = 650, 600
                        pointY_val = [
                            int(pointY.get_value("650")),
                            int(pointY.get_value("600")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 550 and int_key <= 600:  # ระดับ 550mb - 600mb
                        mb_start, mb_end = 600, 550
                        pointY_val = [
                            int(pointY.get_value("600")),
                            int(pointY.get_value("550")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 500 and int_key <= 550:  # ระดับ 500mb - 550mb
                        mb_start, mb_end = 550, 500
                        pointY_val = [
                            int(pointY.get_value("550")),
                            int(pointY.get_value("500")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 450 and int_key <= 500:  # ระดับ 450mb - 500mb
                        mb_start, mb_end = 500, 450
                        pointY_val = [
                            int(pointY.get_value("500")),
                            int(pointY.get_value("450")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 400 and int_key <= 450:  # ระดับ 400mb - 450mb
                        mb_start, mb_end = 450, 400
                        pointY_val = [
                            int(pointY.get_value("450")),
                            int(pointY.get_value("400")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 350 and int_key <= 400:  # ระดับ 350mb - 400mb
                        mb_start, mb_end = 400, 350
                        pointY_val = [
                            int(pointY.get_value("400")),
                            int(pointY.get_value("350")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 300 and int_key <= 350:  # ระดับ 300mb - 350mb
                        mb_start, mb_end = 350, 300
                        pointY_val = [
                            int(pointY.get_value("350")),
                            int(pointY.get_value("300")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 250 and int_key <= 300:  # ระดับ 250mb - 300mb
                        mb_start, mb_end = 300, 250
                        pointY_val = [
                            int(pointY.get_value("300")),
                            int(pointY.get_value("250")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 200 and int_key <= 250:  # ระดับ 200mb - 250mb
                        mb_start, mb_end = 250, 200
                        pointY_val = [
                            int(pointY.get_value("250")),
                            int(pointY.get_value("200")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key > 150 and int_key <= 200:  # ระดับ 150mb - 200mb
                        mb_start, mb_end = 200, 150
                        pointY_val = [
                            int(pointY.get_value("200")),
                            int(pointY.get_value("150")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    elif int_key >= 100 and int_key <= 150:  # ระดับ 100mb - 150mb
                        mb_start, mb_end = 150, 100
                        pointY_val = [
                            int(pointY.get_value("150")),
                            int(pointY.get_value("100")),
                        ]
                        # print(f"pointY_val: {pointY_val}")

                        # ตั้งค่า key_old เพื่อใช้ตรวจสอบรอบต่อไป
                        key_old = int_key
                        # print(f"key_old: {key_old}")

                    else:
                        continue

                    # เรียกใช้ฟังก์ชันคำนวณค่าตำแหน่ง X และ Y
                    self.plot_marker(
                        page,
                        width,
                        height,
                        int_key,
                        value,
                        mb_start,
                        mb_end,
                        pointY_val,
                    )
                    # ----------------------------------------------------------- #

    def plot_marker(self, page, width, height, mb, wnd, mb_start, mb_end, pointY):
        # หาตำแหน่ง แกน Y ที่ mb_num = 976
        # สูตรคำนวณเส้นแก่น y = y1+(P-P1)/(P2-P1)*(y2-y1)
        # โดยที่
        # 𝑃1​ =1000mb
        # 𝑦1=5616y - (ระดับความสูงที่ 1000 mb)
        # 𝑃2=950mb
        # 𝑦2=5502 (ระดับความสูงที่ 950 mb)
        # ตัวอย่าง 𝑃=976 mb (ค่าความกดอากาศที่ต้องการหา y)
        # สรุปที่ ความกดอากาศ 976 mb ระดับความสูง y ≈ 5561
        y = pointY[0] + (mb - mb_start) / (mb_end - mb_start) * (pointY[1] - pointY[0])
        y = y * (page.rect.height / height)
        # print(f"y_pos: {y}")

        if (
            mb == 925
            or mb == 850
            or mb == 700
            or mb == 500
            or mb == 400
            or mb == 300
            or mb == 250
            or mb == 200
            or mb == 150
            or mb == 100
        ):
            x = 6427 * (page.rect.width / width)  # แกน X ลมระดับหลัก

            if ":" in wnd:
                mbTxt, wnd = wnd.split(":")
                mbTxt = mbTxt[2:5]
                if mb == 925 or mb == 850 or mb == 700:
                    x_num = 6620 * (page.rect.width / width)  # แกน X_num ลมระดับหลัก
                    text_x = x_num + 5
                    text_y = y
                else:
                    x_num = 6440 * (page.rect.width / width)  # แกน X_num ลมระดับหลัก
                    text_x = x_num + 5
                    text_y = y

                if mb == 925:
                    mbTxt = mbTxt
                elif mb == 850:
                    mbTxt = "1" + mbTxt
                elif mb == 700:
                    mbTxt = "3" + mbTxt
                elif mb == 500:
                    mbTxt = "5" + mbTxt
                elif mb == 300 or mb == 400:
                    mbTxt = mbTxt + "0"
                else:
                    mbTxt = "1" + mbTxt + "0"

                if 80 <= int(wnd[:3]) <= 90:
                    text_y = y + 10

                # เขียนคำ "ตัวเลขระดับลม"
                page.insert_text(
                    fitz.Point(text_x, text_y),
                    f"{mbTxt}",
                    fontsize=8,
                    color=(0, 0, 1),
                )

        else:
            x = 6203 * (page.rect.width / width)  # แกน X ลมระดับรอง
        # print(f"y_pos: {x}")

        wind_direction = int(wnd[:3])
        # print(f"wind_direction: {wind_direction}")

        windMax = "NIL"
        if "TP" in wnd:
            wind_speed = int(wnd[3:5])
            windMax = "TP"
            x = 6427 * (page.rect.width / width)  # แกน X ลมระดับหลัก

        elif "MX" in wnd:
            wind_speed = int(wnd[3:5])
            windMax = "MX"
            x = 6427 * (page.rect.width / width)  # แกน X ลมระดับหลัก

        else:
            wind_speed = int(wnd[3:])
        # print(f"wind_speed: {wind_speed}")

        """วาดสัญลักษณ์ Wind Barb บน PDF"""
        # ถ้าความเร็วลมเป็น 0, ให้ใส่วงกลมโปร่งใส
        if wind_direction == 0 or wind_speed == 0:
            page.draw_circle((x, y), 3, color=(0, 0, 0), fill=None, width=1)
            page.draw_circle((x, y), 5, color=(0, 0, 0), fill=None, width=1)
            return  # ไม่มีขีดลมให้วาดต่อ

        rad = math.radians((360 + wind_direction) - 90)  # หมุนตามเข็มนาฬิกาให้ตรงทิศ
        shaft_length = 40  # ความยาวของเส้นหลัก
        barb_length = 15  # ความยาวของ barb แต่ละอัน
        barb_spacing = 5  # ระยะห่างระหว่าง barb

        # คำนวณตำแหน่งปลายของ shaft (เส้นหลัก)
        x_end = x + shaft_length * math.cos(rad)
        y_end = y + shaft_length * math.sin(rad)

        # วาดจุดฐานของ Wind Barb
        page.draw_circle((x, y), 2, color=(0, 0, 0), fill=(0, 0, 0))

        if windMax == "TP":
            shaft_length = 50  # ความยาวของเส้นหลัก

            # กำหนดทิศทางย้อนกลับตามเงื่อนไข
            if 0 <= wind_direction < 180:
                angle = 180  # ถ้าทิศลม 0-179 ให้ย้อนกลับไปทางซ้าย (270°)
            else:  # ถ้าทิศลม 180-360 ให้ย้อนกลับไปทางบน (90°)
                angle = 0

            # คำนวณตำแหน่งปลายของเส้นย้อนกลับ
            x_new = x - shaft_length * math.cos(math.radians(angle))
            y_new = y - shaft_length * math.sin(math.radians(angle))

            # วาดเส้นหลัก (จาก x ไป x_end)
            page.draw_line(
                fitz.Point(x, y), fitz.Point(x_end, y_end), color=(0, 0, 0), width=2
            )

            # วาดเส้นย้อนกลับไปตามทิศที่กำหนด
            page.draw_line(
                fitz.Point(x, y),
                fitz.Point(x_new, y_new),
                color=(0, 0, 0),  # ใช้สีแดงเพื่อให้เห็นชัด
                width=2,
            )

            # กำหนดตำแหน่งข้อความ "Tropopause"
            text_offset_x = 5  # ระยะห่างของข้อความจากปลายเส้นหลัก

            # ตำแหน่งข้อความขึ้นกับทิศทางลม
            if 0 <= wind_direction < 180:
                text_offset_y = -2
            else:
                text_offset_y = 2

            text_x = x + text_offset_x
            text_y = y + text_offset_y

            # เขียนคำ "Tropopause"
            page.insert_text(
                fitz.Point(text_x, text_y),
                "TROPOPAUSE",
                fontsize=8,
                color=(0, 0, 0),
            )

        elif windMax == "MX":
            arrow_size = 10
            shaft_length = 40  # ความยาวของเส้นหลัก

            # คำนวณตำแหน่งปลายของเส้นใหม่ (ย้อนทิศทาง)
            x_new = x - shaft_length * math.cos(rad)
            y_new = y - shaft_length * math.sin(rad)

            # วาดเส้นหลัก (จาก x ไป x_end)
            page.draw_line(
                fitz.Point(x, y), fitz.Point(x_end, y_end), color=(0, 0, 0), width=2
            )

            # วาดเส้นใหม่ที่ชี้ไปทิศตรงข้าม
            page.draw_line(
                fitz.Point(x, y),
                fitz.Point(x_new, y_new),
                color=(0, 0, 0),
                width=2,  # สีแดงเพื่อให้เห็นชัด
            )

            # คำนวณมุมของลูกศร (แต่ชี้กลับไปยัง x, y)
            angle = rad + math.pi  # หมุนกลับ 180 องศา

            # คำนวณจุดปลายของหัวลูกศร (สองข้าง)
            left_x = x_new - arrow_size * math.cos(angle - math.pi / 6)
            left_y = y_new - arrow_size * math.sin(angle - math.pi / 6)

            right_x = x_new - arrow_size * math.cos(angle + math.pi / 6)
            right_y = y_new - arrow_size * math.sin(angle + math.pi / 6)

            # วาดหัวลูกศร
            page.draw_line(
                fitz.Point(x_new, y_new),
                fitz.Point(left_x, left_y),
                color=(0, 0, 0),
                width=2,
            )
            page.draw_line(
                fitz.Point(x_new, y_new),
                fitz.Point(right_x, right_y),
                color=(0, 0, 0),
                width=2,
            )

            # เขียนคำ "MAX WNDS" บนเส้นลูกศร
            # คำนวณตำแหน่งข้อความ (ห่างจากเส้นลูกศร 5 หน่วย)
            text_offset_x = 5  # ระยะห่างของข้อความจากปลายเส้นหลัก

            # กำหนด text_offset_y ตามทิศทางของลม
            if wind_direction == 360 or (
                wind_direction >= 271 and wind_direction <= 359
            ):
                text_offset_y = -10
            elif wind_direction == 270 or (
                wind_direction >= 181 and wind_direction <= 269
            ):
                text_offset_y = 10
            elif wind_direction == 180 or (
                wind_direction >= 1 and wind_direction <= 89
            ):
                text_offset_y = 10
            else:
                text_offset_y = -10

            text_x = x + text_offset_x
            text_y = y + text_offset_y

            # เขียนคำ "MAX WNDS" เอียงขนานกับเส้น และห่างจากเส้น 5 หน่วย
            page.insert_text(
                fitz.Point(text_x, text_y),
                "MAX WNDS",
                fontsize=8,
                color=(0, 0, 0),
            )

        else:
            # วาดเส้นหลัก
            page.draw_line(
                fitz.Point(x, y), fitz.Point(x_end, y_end), color=(0, 0, 0), width=2
            )

        # แปลงเป็น string เพื่อใช้ len() และการ substring
        wind_direction_str = str(wind_direction)
        # เช็คความยาวของ wind_direction_str
        if len(wind_direction_str) > 2:
            substring = wind_direction_str[1:2]  # ดึงเลขตัวที่ 2
        else:
            substring = wind_direction_str[0:1]  # ดึงเลขตัวที่ 1

        # ปรับตำแหน่งข้อความให้ตรงปลายเส้นหลัก (ปลายเส้นอยู่ที่ x_end, y_end)
        # และปรับการเลื่อนตำแหน่งข้อความให้เหมาะสม
        # ใช้มุม rad เพื่อหมุนข้อความให้ตรงกับทิศทางของเส้นหลัก
        text_offset_x = 0  # ระยะห่างของข้อความจากปลายเส้นหลัก
        text_offset_y = 0  # ระยะห่างของข้อความจากปลายเส้นหลัก

        if wind_direction == 360:
            text_offset_y = 10  # ระยะห่างของข้อความจากปลายเส้นหลัก
        elif wind_direction == 270:
            text_offset_x = 15  # ระยะห่างของข้อความจากปลายเส้นหลัก
            text_offset_y = -25  # ระยะห่างของข้อความจากปลายเส้นหลัก
        elif wind_direction == 180:
            text_offset_y = 15  # ระยะห่างของข้อความจากปลายเส้นหลัก
        elif wind_direction >= 1 and wind_direction <= 89:
            text_offset_x = 5  # ระยะห่างของข้อความจากปลายเส้นหลัก
            text_offset_y = 7  # ระยะห่างของข้อความจากปลายเส้นหลัก
        elif wind_direction >= 181 and wind_direction <= 269:
            text_offset_x = 15  # ระยะห่างของข้อความจากปลายเส้นหลัก
            text_offset_y = 15  # ระยะห่างของข้อความจากปลายเส้นหลัก
        elif wind_direction >= 271 and wind_direction <= 359:
            text_offset_x = 15  # ระยะห่างของข้อความจากปลายเส้นหลัก
            text_offset_y = 5  # ระยะห่างของข้อความจากปลายเส้นหลัก
        else:
            text_offset_x = 10  # ระยะห่างของข้อความจากปลายเส้นหลัก
            text_offset_y = 10  # ระยะห่างของข้อความจากปลายเส้นหลัก

        text_x = x_end + text_offset_x * math.cos(rad)
        text_y = y_end + text_offset_y * math.sin(rad)

        # วาดข้อความที่ปลายเส้นหลัก
        page.insert_text(
            fitz.Point(text_x, text_y), f"{substring}", fontsize=10, color=(0, 0, 0)
        )

        # จุดเริ่มต้นของ barb (วาดจากปลาย shaft ลงไป)
        xb = x_end
        yb = y_end
        flag_wnd = 0
        # วาดธง (50 knots or more)
        while wind_speed >= 50:
            flag_wnd = 1
            rad_barb = rad + math.pi / 2 - math.radians(30)  # เปลี่ยนทิศให้หันเข้าหา shaft

            # กำหนดความกว้างฐานของสามเหลี่ยม
            barb_width = barb_length * 0.5

            # คำนวณจุดฐานของสามเหลี่ยมบนเส้นหลัก (shaft)
            xb1 = xb + (barb_width / 2) * math.cos(rad)
            yb1 = yb + (barb_width / 2) * math.sin(rad)
            xb2 = xb - (barb_width / 2) * math.cos(rad)
            yb2 = yb - (barb_width / 2) * math.sin(rad)

            # คำนวณจุดยอดของสามเหลี่ยม (ให้ชี้เข้าหา shaft)
            xt = xb + barb_length * math.cos(rad_barb)
            yt = yb + barb_length * math.sin(rad_barb)

            # วาดสามเหลี่ยม (เชื่อม 3 จุด)
            page.draw_line(
                fitz.Point(xb1, yb1), fitz.Point(xt, yt), color=(0, 0, 0), width=2
            )
            page.draw_line(
                fitz.Point(xt, yt), fitz.Point(xb2, yb2), color=(0, 0, 0), width=2
            )
            page.draw_line(
                fitz.Point(xb2, yb2), fitz.Point(xb1, yb1), color=(0, 0, 0), width=2
            )

            # คำนวณจุดฐานของสามเหลี่ยมบนเส้นหลัก (shaft)
            xb1 = xb + (barb_width / 4) * math.cos(rad)
            yb1 = yb + (barb_width / 4) * math.sin(rad)
            xb2 = xb - (barb_width / 4) * math.cos(rad)
            yb2 = yb - (barb_width / 4) * math.sin(rad)

            # คำนวณจุดยอดของสามเหลี่ยม (ให้ชี้เข้าหา shaft)
            xt = xb + (barb_length / 1.3) * math.cos(rad_barb)
            yt = yb + (barb_length / 1.3) * math.sin(rad_barb)
            # เติมพื้นที่ภายในสามเหลี่ยม (วาดเส้นเชื่อมกลับไปที่จุดแรก)
            page.draw_line(
                fitz.Point(xb2, yb2), fitz.Point(xt, yt), color=(0, 0, 0), width=2
            )
            page.draw_line(
                fitz.Point(xt, yt), fitz.Point(xb1, yb1), color=(0, 0, 0), width=2
            )

            xb1 = xb + (barb_width / 8) * math.cos(rad)
            yb1 = yb + (barb_width / 8) * math.sin(rad)
            page.draw_line(
                fitz.Point(xt, yt), fitz.Point(xb1, yb1), color=(0, 0, 0), width=2
            )

            xb1 = xb + (barb_width / 12) * math.cos(rad)
            yb1 = yb + (barb_width / 12) * math.sin(rad)
            page.draw_line(
                fitz.Point(xt, yt), fitz.Point(xb1, yb1), color=(0, 0, 0), width=3
            )

            # ขยับตำแหน่งลงไปตามแนว shaft
            barb_spacing += 3
            xb -= barb_spacing * math.cos(rad)
            yb -= barb_spacing * math.sin(rad)

            # ลดความเร็วลมลง
            wind_speed -= 50
            # ถ้าความเร็วลมต่ำกว่า 50 knots จะหยุดวาดธง
            if wind_speed < 50:
                break

        # วาดขีดใหญ่ (8-12 knots)
        while wind_speed >= 8:
            flag_wnd = 1
            # ปรับมุมของ barb ให้เอียงเพิ่มอีก 20 องศา
            rad_barb = rad - math.pi / 2 + math.radians(-30)

            # คำนวณปลายของ barb โดยให้อยู่บนเส้นหลัก
            xb2 = xb - barb_length * math.cos(rad_barb)
            yb2 = yb - barb_length * math.sin(rad_barb)

            # วาด barb
            page.draw_line(
                fitz.Point(xb, yb), fitz.Point(xb2, yb2), color=(0, 0, 0), width=2
            )

            # ขยับตำแหน่งลงไปตามแนว shaft
            xb -= barb_spacing * math.cos(rad)
            yb -= barb_spacing * math.sin(rad)

            # ลดความเร็วลมลง 12 knots ต่อขีดใหญ่
            wind_speed -= 10

            # ถ้าความเร็วลมต่ำกว่า 8 knots จะหยุดวาดขีดใหญ่
            if wind_speed < 8:
                break

        # วาดขีดเล็ก (3-7 knots)
        if wind_speed > 2:
            rad_barb = rad - math.pi / 2 + math.radians(-30)  # เอียงเพิ่มอีก 20 องศา

            if flag_wnd == 1:
                xb2 = xb - (barb_length / 2) * math.cos(rad_barb)
                yb2 = yb - (barb_length / 2) * math.sin(rad_barb)
            else:
                xb -= (barb_spacing + 5) * math.cos(rad)
                yb -= (barb_spacing + 5) * math.sin(rad)
                xb2 = xb - (barb_length / 2) * math.cos(rad_barb)
                yb2 = yb - (barb_length / 2) * math.sin(rad_barb)
            page.draw_line(
                fitz.Point(xb, yb), fitz.Point(xb2, yb2), color=(0, 0, 0), width=2
            )
