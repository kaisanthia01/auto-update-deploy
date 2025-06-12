import fitz


class PlotLine:
    # ฟังก์ชันวาด PlotLine
    def plotLineDraw(self, page, width, height, point_data):
        try:
            # วนลูปผ่านคีย์ทั้งหมดใน point_data
            keys = sorted(
                point_data["point_x"].keys(), key=int
            )  # เรียงคีย์ให้เป็นลำดับจากน้อยไปมาก
            for i in range(len(keys) - 1):  # วนลูปผ่านคีย์ทั้งหมด ยกเว้นคีย์สุดท้าย
                key = keys[i]
                next_key = keys[i + 1]  # คีย์ถัดไป

                # เรียกใช้ค่าจาก point_data สำหรับคีย์ที่กำหนด
                point_x1 = point_data["point_x1"][key][0]
                point_x2 = point_data["point_x1"][next_key][
                    0
                ]  # ใช้คีย์ถัดไปเพื่อดึงค่า point_x
                point_y1 = point_data["point_y"][key][0]
                point_y2 = point_data["point_y"][next_key][0]  # ใช้คีย์ถัดไปเพื่อดึงค่า point_y

                # วาดเส้นปะจากจุด (x, y) ไปยังจุด (x1, y1) ใช้ฟังก์ชัน draw_dashed_line
                self.draw_dashed_line(
                    page, width, height, point_x1, point_x2, point_y1, point_y2
                )
                # ----------------------------------------------------------- #

                # เรียกใช้ค่าจาก point_data สำหรับคีย์ที่กำหนด
                point_x3 = point_data["point_x"][key][0]
                point_x4 = point_data["point_x"][next_key][0]  # ใช้คีย์ถัดไปเพื่อดึงค่า point_x
                point_y3 = point_data["point_y"][key][0]
                point_y4 = point_data["point_y"][next_key][0]  # ใช้คีย์ถัดไปเพื่อดึงค่า point_y

                # คำนวณตำแหน่ง x ตามสัดส่วนของหน้า PDF
                x3_pos = point_x3 * (page.rect.width / width)
                x4_pos = point_x4 * (page.rect.width / width)

                # คำนวณตำแหน่ง y ตามสัดส่วนของหน้า PDF
                y3_pos = point_y3 * (page.rect.height / height)
                y4_pos = point_y4 * (page.rect.height / height)

                # วาดเส้นปะจากจุด (x3, y3) ไปยังจุด (x4, y4)
                page.draw_line(
                    fitz.Point(x3_pos, y3_pos),  # จุดเริ่มต้น
                    fitz.Point(x4_pos, y4_pos),  # จุดสิ้นสุด
                    color=(1, 0, 0),  # สีของเส้น (สีดำ)
                    width=1,  # ความหนาของเส้น
                )
                # ----------------------------------------------------------- #

        except Exception as e:
            print(f"An error occurred: {e}")

    import fitz  # PyMuPDF

    def draw_dashed_line(
        self, page, width, height, point_x1, point_x2, point_y1, point_y2
    ):
        gap = 5  # ระยะห่างระหว่างเส้นแต่ละช่วง
        color = (0, 1, 0)  # สีเขียว
        line_width = 1  # ความหนาของเส้น

        # คำนวณระยะห่างระหว่างจุดเริ่มต้นและจุดสิ้นสุด
        delta_x = point_x2 - point_x1
        delta_y = point_y2 - point_y1
        length = (delta_x**2 + delta_y**2) ** 0.5  # ความยาวของเส้นทั้งหมด

        if length == 0:
            return  # ป้องกันหารด้วยศูนย์

        # กำหนดจำนวน segments ตามความยาวของเส้น
        if length < 50:
            segments = 2
        elif length > 150:
            segments = 5
        else:
            segments = 4

        # ปรับ segment_length ให้รวม gap เข้าไป
        segment_length = (length - (gap * (segments - 1))) / segments

        for i in range(segments):
            start_x = point_x1 + i * (segment_length + gap) * delta_x / length
            start_y = point_y1 + i * (segment_length + gap) * delta_y / length
            end_x = start_x + (segment_length * delta_x / length)
            end_y = start_y + (segment_length * delta_y / length)

            # แปลงค่าตำแหน่งให้เป็นสัดส่วนของหน้า PDF
            start_x = start_x * (page.rect.width / width)
            end_x = end_x * (page.rect.width / width)
            start_y = start_y * (page.rect.height / height)
            end_y = end_y * (page.rect.height / height)

            # วาดเส้นแต่ละส่วน
            page.draw_line(
                fitz.Point(start_x, start_y),
                fitz.Point(end_x, end_y),
                color=color,
                width=line_width,
            )
