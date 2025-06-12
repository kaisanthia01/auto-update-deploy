import os
import re
import json
import sys
import logging

logger = logging.getLogger("CheckCodeAAXXFull")

# ตั้งค่ารองรับ UTF-8 สำหรับ Windows Terminal
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")


class CheckCodeAAXXFull:
    def __init__(self):
        self.main_fields = [
            "IrIxhVV",
            "Nddff",
            "1SnTTT",
            "2SnTdTdTd",
            "3P0P0P0",
            "4PPPP",
            "5appp",
            "6RRRtr",
            "7wwW1W2",
            "8NhClCmCH",
            "9GGgg",
        ]
        self.section_222_fields = [
            "Dv",
            "0sTTT",
            "1PPHH",
            "2PPHH",
            "3dddd",
            "4PPHH",
            "5PPHH",
            "6IEER",
            "70HHH",
            "8aTTT",
        ]
        self.section_333_fields = [
            "0::::",
            "1sTTT",
            "2sTTT",
            "3Ejjj",
            "4Esss",
            "5jjjjj",
            "6RRRt",
            "7RRRR",
            "8Nchh",
            "9SSss",
        ]

    def decodeAAXX(self, synop_data: dict, index: int, save_to_file=True) -> list:
        all_data = []

        for date_str, synop_text in synop_data.items():
            lines = synop_text.strip().splitlines()

            for line in lines:
                if "NIL" in line or len(line.strip()) < 5:
                    continue

                try:
                    station_id = line[:5]
                    parts = self.preprocess_synop_line(line)

                    data = {
                        "station_id": station_id,
                        "date": date_str,
                        "raw": line.strip(),
                        "main": {k: "/////" for k in self.main_fields},
                        "222": {k: "/////" for k in self.section_222_fields},
                        "333": {k: "/////" for k in self.section_333_fields},
                        "validation_errors": [],
                    }

                    section = "main"
                    group_index = 0
                    i = 0

                    while i < len(parts):
                        group = parts[i]

                        if group == "222":
                            section = "222"
                            group_index = 0
                            i += 1
                            continue
                        elif group == "333":
                            section = "333"
                            group_index = 0
                            i += 1
                            continue

                        key = None
                        if section == "main" and group_index < len(self.main_fields):
                            key = self.main_fields[group_index]
                        elif section == "222" and group_index < len(
                            self.section_222_fields
                        ):
                            key = self.section_222_fields[group_index]
                        elif section == "333" and group_index < len(
                            self.section_333_fields
                        ):
                            key = self.section_333_fields[group_index]
                        else:
                            i += 1
                            continue

                        if key == "3P0P0P0" and group.startswith("40"):
                            data["main"]["4PPPP"] = group
                            if not self._validate_group(group, "4PPPP"):
                                data["validation_errors"].append(
                                    f"main:4PPPP='{group}'"
                                )
                            group_index += 1
                            i += 1
                            continue

                        data[section][key] = group
                        if not self._validate_group(group, key):
                            data["validation_errors"].append(
                                f"{section}:{key}='{group}'"
                            )

                        group_index += 1
                        i += 1

                    all_data.append(data)

                except Exception as e:
                    logger.error(f"❌ Decode error at line: {line[:30]} | {e}")
                    continue

        all_data = self._deduplicate_by_station(all_data)

        if save_to_file:
            self._save_to_json(all_data, index)

        return all_data

    def preprocess_synop_line(self, line: str) -> list:
        parts = line[5:].replace("=", "").strip().split()

        result = []
        current_section = "main"

        for token in parts:
            if token in ["222", "333"]:
                result.append(token)
                current_section = token
                continue

            if len(token) == 5:
                result.append(token)
            else:
                chunks = [token[i : i + 5] for i in range(0, len(token), 5)]
                result.extend(chunks)

        return result

    def _validate_group(self, group: str, key: str) -> bool:
        if group == "/////" or len(group) != 5:
            return True

        try:
            if key in ["1SnTTT", "2SnTdTdTd", "1sTTT", "2sTTT"]:
                return group[1:].isdigit()

            elif key in ["3P0P0P0", "4PPPP"]:
                sub = group[2:5].replace("/", "0")
                return sub.isdigit() and 850 <= (1000 + int(sub) / 10.0) <= 1100

            elif key == "5appp":
                return group[1:].isdigit()

            elif key in ["6RRRtr", "6RRRt"]:
                return group[:3].replace("/", "0").isdigit()

            elif key == "7wwW1W2":
                return group[1:3].isdigit()

            elif key == "8NhClCmCH":
                return group[1:].replace("/", "0").isdigit()

            elif key == "9GGgg":
                GG = int(group[1:3])
                gg = int(group[3:5])
                return 0 <= GG <= 23 and 0 <= gg <= 59

        except:
            return False

        return True

    def _deduplicate_by_station(self, data_list: list) -> list:
        station_map = {}
        for entry in data_list:
            station_id = entry.get("station_id")
            date = entry.get("date")
            if station_id and date:
                key = (date, station_id)
                station_map[key] = entry
        return list(station_map.values())

    def _save_to_json(self, data: list, index: int):
        """บันทึกข้อมูล SYNOP ลงในไฟล์ JSON"""
        # กำหนดตำแหน่งไฟล์ JSON
        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
        filename = "synop_data_surface.json" if index == 0 else "synop_data_detail.json"
        json_path = os.path.join(script_dir, "../data/json/", filename)

        # ตรวจสอบว่ามีโฟลเดอร์ data/json หรือไม่
        if not os.path.exists(os.path.dirname(json_path)):
            # ✅ สร้างโฟลเดอร์ถ้ายังไม่มี
            os.makedirs(os.path.dirname(json_path))
            logger.info(f"✅ Created directory: {os.path.dirname(json_path)}")

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"✅ บันทึกไฟล์: {json_path}")
        except Exception as e:
            logger.error(f"❌ บันทึกไฟล์ไม่สำเร็จ: {e}")
