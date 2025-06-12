from collections import defaultdict
import logging

logger = logging.getLogger("CheckArrayWND")

class CheckArrayWND:
    def decodeArrayWND(self, TTAA, TTBB):
        # สร้าง dictionary เก็บข้อมูล
        data = {
            "wnd1": TTAA,
            "wnd2": TTBB,
        }

        # ใช้ defaultdict เพื่อป้องกัน KeyError
        new_data = {}
        
        def extract_wnd_values(wnd_data):
            """ดึงข้อมูลจาก wnd และเพิ่มลงใน new_data"""
            for level, items in wnd_data.items():
                for item in items:
                    key, value = item.split(":")
                    
                    if level not in new_data:  
                        # ถ้ายังไม่มี level นี้ ให้เพิ่มค่าใหม่เข้าไป
                        if level in ["1050", "925", "850", "700", "500", "400", "300", "250", "200", "150", "100", "TP", "MX"]:
                            new_data[level] = [f"{key}:{value}"]
                        else:
                            new_data[level] = [value]
                    else:
                        # ถ้า level ซ้ำกัน ให้เช็คค่าก่อน
                        existing_value = new_data[level][0]  # ดึงค่าปัจจุบันที่บันทึกไว้
                        if existing_value == "00000" and value != "00000":
                            # ถ้าค่าเดิมเป็น "00000" และค่าใหม่ไม่ใช่ "00000" ให้แทนที่
                            if level in ["1050", "925", "850", "700", "500", "400", "300", "250", "200", "150", "100", "TP", "MX"]:
                                new_data[level] = [f"{key}:{value}"]
                            else:
                                new_data[level] = [value]

        # รวมข้อมูลจาก wnd1 และ wnd2
        extract_wnd_values(data["wnd1"])
        extract_wnd_values(data["wnd2"])

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
