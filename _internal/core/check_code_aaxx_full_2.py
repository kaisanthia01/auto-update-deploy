import os
import json
import sys
import logging

logger = logging.getLogger("CheckCodeAAXXFull2")

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")


class CheckCodeAAXXFull2:
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

    def decodeAAXX(self, synop_data: dict, index: int = 0, save_to_file=True) -> list:
        all_data = []

        for date_str, synop_text in synop_data.items():
            lines = synop_text.strip().splitlines()

            for line in lines:
                if "NIL" in line or len(line.strip()) < 5:
                    continue

                try:
                    parts = line.replace("=", "").strip().split()
                    if len(parts) < 3:
                        continue

                    station_id = parts[0]
                    data = {
                        "station_id": station_id,
                        "date": date_str,
                        "raw": line.strip(),
                        "main": {k: "/////" for k in self.main_fields},
                        "222": {k: "/////" for k in self.section_222_fields},
                        "333": {k: "/////" for k in self.section_333_fields},
                        "validation_errors": [],
                    }

                    # ✅ ตำแหน่งแน่นอน
                    data["main"]["IrIxhVV"] = parts[1]
                    data["main"]["Nddff"] = parts[2]

                    section = "main"
                    group_index = 0
                    i = 3  # เริ่มจากหลัง Nddff

                    key_map = {
                        "1": "1SnTTT",
                        "2": "2SnTdTdTd",
                        "3": "3P0P0P0",
                        "4": "4PPPP",
                        "5": "5appp",
                        "6": "6RRRtr",
                        "7": "7wwW1W2",
                        "8": "8NhClCmCH",
                        "9": "9GGgg",
                    }

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

                        if section == "main":
                            if group and group[0] in key_map:
                                key = key_map[group[0]]
                                if data["main"][key] == "/////":
                                    data["main"][key] = group
                                    if not self._validate_group(group, key):
                                        data["validation_errors"].append(
                                            f"main:{key}='{group}'"
                                        )

                        elif section == "222":
                            if group_index < len(self.section_222_fields):
                                key = self.section_222_fields[group_index]
                                data["222"][key] = group
                                if not self._validate_group(group, key):
                                    data["validation_errors"].append(
                                        f"222:{key}='{group}'"
                                    )
                                group_index += 1

                        elif section == "333":
                            if group_index < len(self.section_333_fields):
                                key = self.section_333_fields[group_index]
                                data["333"][key] = group
                                if not self._validate_group(group, key):
                                    data["validation_errors"].append(
                                        f"333:{key}='{group}'"
                                    )
                                group_index += 1

                        i += 1

                    all_data.append(data)

                except Exception as e:
                    logger.error(f"❌ Decode error: {line[:30]} | {e}")
                    continue

        all_data = self._deduplicate_by_station(all_data)

        if save_to_file:
            self._save_to_json(all_data, index)

        return all_data

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
                return group[1:].replace("/", "0").isdigit()
            elif key in ["6RRRtr", "6RRRt"]:
                return group[:3].replace("/", "0").isdigit()
            elif key == "7wwW1W2":
                return group[1:3].replace("/", "0").isdigit()
            elif key == "8NhClCmCH":
                return group[1:].replace("/", "0").isdigit()
            elif key == "9GGgg":
                GG = int(group[1:3].replace("/", "0"))
                gg = int(group[3:5].replace("/", "0"))
                return 0 <= GG <= 23 and 0 <= gg <= 59
        except:
            return False
        return True

    def _deduplicate_by_station(self, data_list: list) -> list:
        station_map = {}
        for entry in data_list:
            key = (entry["date"], entry["station_id"])
            station_map[key] = entry
        return list(station_map.values())

    def _save_to_json(self, data: list, index: int):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, "../data/json/synop_data_pressure.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"✅ บันทึกไฟล์: {json_path}")
        except Exception as e:
            logger.error(f"❌ บันทึกไฟล์ไม่สำเร็จ: {e}")
