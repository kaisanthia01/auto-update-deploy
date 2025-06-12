import re
from collections import defaultdict
import logging

logger = logging.getLogger("CheckCodeTTBB")


class CheckCodeTTBB:
    def decodeTTBB(self, TTBB):
        # สร้าง dictionary เก็บข้อมูล (ใช้ defaultdict เพื่อป้องกัน KeyError)
        data = {
            "temp": defaultdict(list),
            "wnd": defaultdict(list),
        }

        text = TTBB[16:].lstrip()  # ลบช่องว่างด้านหน้า

        # ตรวจสอบข่าว TTBB NIL
        if "NIL" in text:
            return data  # คืนค่า data เปล่าๆ

        # ค้นหาตำแหน่ง 21212 และ 31313
        match_21212 = re.search(r"\b21212\b", text)
        match_31313 = re.search(r"\b31313\b", text)

        # ถ้าไม่มี 21212 ให้กำหนดค่า wnd เป็น defaultdict(list) เปล่าๆ
        if not match_21212:
            data["wnd"] = defaultdict(list)

        # ถ้ามี "//END PART 01//="
        position = text.find("//END PART 01//=")
        if position != -1:
            text_temp = text[:position].rstrip()
            text_wnd = ""
        else:
            text_temp = text[: match_21212.start()].rstrip() if match_21212 else ""
            text_wnd = text[match_21212.end() : match_31313.start()].lstrip() if match_31313 else ""

        # ฟังก์ชันช่วยดึงข้อมูล temp และ wind
        def extract_values(data_dict, text):
            matches = re.findall(r"\b\d{5} \S{5}\b", text)  # ค้นหาข้อมูลรูปแบบ "XXXXX YYYYY"
            for match in matches:
                key, value = match.split()
                extracted_key = key[2:5]  # ดึงตัวเลขช่วง 2-4
                data_dict[extracted_key].append(f"{key}:{value}")

        # ดึงค่าจาก temp และ wind
        extract_values(data["temp"], text_temp)
        extract_values(data["wnd"], text_wnd)

        return data
