import fitz

from core.skewt.PointX import PointX
from core.skewt.PointY import PointY


class PlotMarker:
    # ฟังก์ชันวาด PlotMarker
    def plotMakerDraw(self, page, width, height, plot, Marker):
        # สร้างอ็อบเจ็กต์ของ Point_x_x1_y
        point_data = {"point_x": {}, "point_x1": {}, "point_y": {}}
        key_old = 1100
        # สร้างอ็อบเจ็กต์ของ PointY
        pointY = PointY()

        for key, values in Marker.items():
            # ตรวจสอบว่า key เป็น 'TP' และ value เป็น ' /////' หรือไม่
            if key == "TP" and "/////" in values:
                break  # ถ้าเจอ "TP" และค่า "/////" ก็หยุดการวนลูป

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
                    # ตรวจสอบระดับความกดอากาศ
                    if int_key > 1000:  # ระดับ SFC
                        if ":" in value:
                            mb, temp = value.split(":")
                            mb = mb[2:5]
                            mb_num = int(mb)
                            # print(f"Key: {mb_num}, Value: {temp}")
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
                            value = temp
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
                    marker_x, marker_x1, marker_y = self.plot_marker(
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

                    # หากยังไม่มี key นี้ใน dictionary ให้สร้าง list ว่างก่อน
                    if f"{int_key}" not in point_data["point_x"]:
                        point_data["point_x"][f"{int_key}"] = []
                    if f"{int_key}" not in point_data["point_x1"]:
                        point_data["point_x1"][f"{int_key}"] = []
                    if f"{int_key}" not in point_data["point_y"]:
                        point_data["point_y"][f"{int_key}"] = []

                    # เพิ่มค่า marker_x, marker_x1, marker_y ในแต่ละ key
                    point_data["point_x"][f"{int_key}"].append(marker_x)
                    point_data["point_x1"][f"{int_key}"].append(marker_x1)
                    point_data["point_y"][f"{int_key}"].append(marker_y)

        return point_data
        # ----------------------------------------------------------- #

    def plot_marker(self, page, width, height, mb, temp, mb_start, mb_end, pointY):
        # print(f"mb: {mb}")
        # print(f"temp: {temp}")
        # หาตำแหน่ง แกน Y ที่ mb_num = 976
        # สูตรคำนวณเส้นแก่น y = y1+(P-P1)/(P2-P1)*(y2-y1)
        # โดยที่
        # 𝑃1​ =1000mb
        # 𝑦1=5616y - (ระดับความสูงที่ 1000 mb)
        # 𝑃2=950mb
        # 𝑦2=5502 (ระดับความสูงที่ 950 mb)
        # ตัวอย่าง 𝑃=976 mb (ค่าความกดอากาศที่ต้องการหา y)
        # สรุปที่ ความกดอากาศ 976 mb ระดับความสูง y ≈ 5561
        y_pos = pointY[0] + (mb - mb_start) / (mb_end - mb_start) * (
            pointY[1] - pointY[0]
        )
        marker_y = y_pos
        # print(f"y_pos: {y_pos}")
        # ----------------------------------------------------------- #

        # หาตำแหน่ง แกน X ที่ temp = 24258
        # สูตรคำนวณเส้นแก่น x =x1−x=5006−4689=317/5=63.4
        # 317 คือห่าง 5 องศา และ 63.4 คือห่าง 1 องศา
        # โดยที่
        # x = 4689 - (ตำแหน่งอุณหภูมิ +20 องศา)
        # x1 = 5006 - (ตำแหน่งอุณหภูมิ +25 องศา)
        # สรุปที่ x อุณหภูมิ 20.6 ≈ 63.4×0.6 = 38.04
        # ปรับค่า x1 ให้เอียง 47 องศา
        # tan(47)=Δy/Δx​
        # Δx=Δy​/tan(47∘)
        # tan(47)≈ 1.0724
        # Δy=5616−5561.28=54.72
        # Δx=54.72​/1.0724≈51.03
        # ถ้าไปทางซ้าย ( 𝑥 x ลดลง): 𝑥 1 = 4689 − 51.03 = 4637.97 | x1=4689−51.03=4637.97
        # ถ้าไปทางขวา ( 𝑥 x เพิ่มขึ้น): 𝑥 1 = 4689 + 51.03 = 4740.03 | x1=4689+51.03=4740.0

        # ดึงตัวเลขที่ตำแหน่งที่ 3 จาก temp แล้วเช็คว่าเป็นเลขคู่หรือคี่
        temp_even = int(temp[2:3])
        if temp_even % 2 == 0:
            temp_even = 1
        else:
            temp_even = -1
        # print(f"temp_even: {temp_even}")

        # คำนวณ temp_int โดยการใช้เลข 2 หลักแรกจาก temp และคูณด้วย temp_even
        temp_int = int((int(temp[:2]) // 5) * 5)

        # คำนวณ temp_float โดยการเอาค่าหมายเลข 1 ถึง 2 คูณกับ 0.1
        temp_float = float(temp[0:3]) * 0.1 - temp_int

        # คำนวณ temp_dif โดยการเอาค่าหมายเลขหลังตำแหน่งที่ 3-5 แล้วลบ 50
        temp_dif = int(temp[3:])
        # print(f"temp_dif: {temp_dif}")
        if temp_dif > 55:
            if (temp_dif - 50) > 6:
                temp_dif = float(temp_dif - 50)

            else:
                temp_dif = float((temp_dif - 50) * 0.1)

        else:
            temp_dif = float(temp_dif * 0.1)

        # print(f"temp_int: {temp_int}")
        # print(f"temp_float: {temp_float}")
        # print(f"temp_dif: {temp_dif}")

        # สร้างอ็อบเจ็กต์ของ TempX
        pointX = PointX()

        # เรียกใช้งานเพื่อดึงค่าจาก tempX
        pointX_val = pointX.get_value(f"{mb_start}", f"{(temp_int* temp_even)}")
        pointX_val = int(pointX_val)
        # print(f"pointX_val: {pointX_val}")

        # คำนวณค่า tan
        # คำนวณค่า tan
        tan = round((float(pointY[0]) - y_pos) / 1.0724, 2)
        # print(f"tan: {tan}")

        # คำนวณตำแหน่ง x_pos
        if temp_even > 0:
            x_pos = (pointX_val + tan) + (63.4 * temp_float)
        else:
            x_pos = (pointX_val + tan) - (63.4 * temp_float)

        marker_x = x_pos
        # print(f"x_pos: {x_pos}")

        # คำนวณตำแหน่ง x1_pos
        x1_pos = x_pos - (63.4 * temp_dif)
        marker_x1 = x1_pos
        # print(f"x1_pos: {x1_pos}")
        # ----------------------------------------------------------- #

        # คำนวณตำแหน่ง x ตามสัดส่วนของหน้า PDF
        x_pos = x_pos * (page.rect.width / width)
        x1_pos = x1_pos * (page.rect.width / width)

        # คำนวณตำแหน่ง y ตามสัดส่วนของหน้า PDF
        y_pos = y_pos * (page.rect.height / height)
        # print(f"y_pos: {y_pos}")
        y1_pos = y_pos
        # print(f"y1_pos: {y1_pos}")
        # ----------------------------------------------------------- #

        # Plot Marker ตามตำแหน่ง x และ y ที่คำนวณแล้ว
        # จุด Temp 1
        page.draw_circle(
            fitz.Point(x_pos, y_pos),
            1,
            color=(1, 0, 0),
            fill=(1, 0, 0),
            width=0,
        )
        
        # วงกลมรอบจุด Temp 1
        page.draw_circle((x_pos, y_pos), 2, color=(1, 0, 0), fill=None, width=1)

        # จุด Temp 2
        page.draw_circle(
            fitz.Point(x1_pos, y1_pos),
            1,
            color=(0, 1, 0),
            fill=(0, 1, 0),
            width=0,
        )
        
        # วงกลมรอบจุด Temp 2
        page.draw_circle((x1_pos, y1_pos), 2, color=(0, 1, 0), fill=None, width=1)
        # ----------------------------------------------------------- #
        return [marker_x, marker_x1, marker_y]
