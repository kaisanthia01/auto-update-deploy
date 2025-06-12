from collections import defaultdict
import logging

logger = logging.getLogger("CheckArrayTEMP")

class CheckArrayTEMP:
    def decodeArrayTEMP(self, TTAA, TTBB):
        # สร้าง dictionary เก็บข้อมูล
        data = {
            "temp1": TTAA,
            "temp2": TTBB,
        }

        # ใช้ defaultdict เพื่อป้องกัน KeyError
        new_data = defaultdict(list)
        added_levels = set()  # ใช้เซ็ตเก็บระดับที่ถูกเพิ่มไปแล้ว

        def extract_temp_values(temp_data):
            """ดึงข้อมูลจาก temp และเพิ่มลงใน new_data"""
            for level, items in temp_data.items():
                if level not in added_levels:  # ตรวจสอบว่าระดับนี้ยังไม่ถูกเพิ่ม
                    added_levels.add(level)  # เพิ่ม level ลงในเซ็ต
                    for item in items:
                        key, value = item.split(":")
                        if level == "1050":
                            new_data[level].append(f"{key}:{value}")
                        else:
                            new_data[level].append(value)

        # รวมข้อมูลจาก temp1 และ temp2
        extract_temp_values(data["temp1"])
        extract_temp_values(data["temp2"])

        # ฟังก์ชันช่วยจัดลำดับคีย์
        def custom_sort_key(key):
            if key.isdigit():
                return (-int(key), 0)  # เรียงจากมากไปน้อย
            elif key == "TP":
                return (float("inf"), 1)  # ให้ "TP" อยู่ถัดจากตัวเลข
            elif key == "MX":
                return (float("inf"), 2)  # ให้ "MX" อยู่ท้ายสุด
            return (float("inf"), 3)  # เผื่อกรณีมีคีย์พิเศษอื่น

        # เรียงลำดับตามเงื่อนไขที่กำหนด
        sorted_data_by_key = dict(
            sorted(new_data.items(), key=lambda item: custom_sort_key(item[0]))
        )

        return sorted_data_by_key
