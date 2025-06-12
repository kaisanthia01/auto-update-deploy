import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger("CheckCodeSkewT")


class CheckCodeSkewT:
    def __init__(self, json_path: Optional[str] = None):
        """
        โหลดข้อมูลจากไฟล์ JSON ที่เก็บรหัสลมชั้นบน เช่น TTAA, TTBB, PPAA, PPBB
        """
        self.json_file = (
            Path(json_path)
            if json_path
            else Path(__file__).resolve().parent
            / ".."
            / "data"
            / "json"
            / "synop_url_skewt.json"
        )
        if not self.json_file.exists():
            raise FileNotFoundError(f"ไม่พบไฟล์: {self.json_file}")

        with self.json_file.open("r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.output_json = (
            Path(__file__).resolve().parent
            / ".."
            / "data"
            / "json"
            / "synop_data_skewt.json"
        )
        self.supported_codes = ["TTAA", "TTBB", "PPAA", "PPBB"]

    def decode_all(
        self, content: Dict[str, Dict[str, str]], date: str
    ) -> Dict[str, Dict[str, List[Dict]]]:
        print(f"📦 เริ่มถอดรหัสสำหรับวันที่: {date}")
        if date not in self.data:
            raise KeyError(f"ไม่มีข้อมูลวันที่ {date}")

        return self.decode_from_dict(content, date)

    def decode_from_dict(
        self, content: Dict[str, Dict[str, str]], time: str, date: str
    ) -> Dict[str, Dict[str, List[Dict]]]:
        """
        ถอดรหัสจาก dict ข้อมูลลม พร้อมระบุเวลา และเพิ่ม timestamp ให้ทุก record
        """
        result = {}
        # timestamp = self._build_timestamp(date, time)  # ✅ สร้าง timestamp เดียวเลย
        timestamp = datetime.now().isoformat() + "LST"
        for station, code_data in content.items():
            result[station] = {}
            for code_type in self.supported_codes:
                raw = code_data.get(code_type, "NIL")
                if raw == "NIL":
                    result[station][code_type] = []
                else:
                    if code_type == "TTAA":
                        decoded = self._decode_ttaa(raw)
                    elif code_type == "TTBB":
                        decoded = self._decode_ttbb(raw)
                    elif code_type == "PPAA":
                        decoded = self._decode_ppaa(raw)
                    elif code_type == "PPBB":
                        decoded = self._decode_ppbb(raw)

                    # ✅ เพิ่ม time และ timestamp
                    for row in decoded:
                        row["time"] = time
                        row["timestamp"] = timestamp

                    result[station][code_type] = decoded

        # ✅ บันทึกผลลัพธ์ลงไฟล์ JSON
        #self.save_decoded_to_json(result, time, date)
        return result

    def _decode_ttaa(self, text: str) -> List[Dict]:
        """
        ถอดรหัสลมจาก TTAA หรือ TTBB โดยแยกกลุ่ม ddfff ต่อจากรหัสระดับความกดอากาศ
        """
        groups = text.replace("\n", " ").split()
        speed_factor = self._check_speed_factor(groups[1])
        result = []
        i = 0
        while i + 5 < len(groups):  # ใช้ดูแค่ g1 และ g2
            g1, g2 = groups[i + 3], groups[i + 5]
            # print(f"TTAA groups[i], groups[i + 2]: {g1} {g2}")

            if re.fullmatch(r"\d{5}", g1) and re.fullmatch(r"\d{5}", g2):
                prefix = g1[:2]
                pressure = self._map_pressure(prefix)
                if pressure is not None:
                    wind_dir = int(g2[:3])
                    wind_speed = int(g2[3:]) * speed_factor
                    result.append(
                        {
                            "hPa./ft.": pressure,
                            "wind_dir": wind_dir,
                            "wind_speed": wind_speed,
                        }
                    )

            i += 3  # ต้องอยู่ด้านนอกเสมอ ไม่ว่า if จะเข้าเงื่อนไขหรือไม่

        return result

    def _decode_ttbb(self, text: str) -> List[Dict]:
        """
        ถอดรหัสลมจาก TTAA หรือ TTBB โดยแยกกลุ่ม ddfff ต่อจากรหัสระดับความกดอากาศ
        """
        groups = text.replace("\n", " ").split()
        speed_factor = self._check_speed_factor(groups[1])

        # ค้นหาตำแหน่ง 21212 และ 31313
        match_21212 = re.search(r"\b21212\b", text)
        match_31313 = re.search(r"\b31313\b", text)

        text_new = ""
        if match_21212:
            start = match_21212.end()
            end = match_31313.start() if match_31313 else len(text)
            text_new = text[start:end].lstrip()

        groups = text_new.replace("\n", " ").split()
        result = []
        i = 0
        while i + 2 < len(groups):  # ต้องแน่ใจว่า g1, g2 อยู่ใน index ที่ปลอดภัย
            g1, g2 = groups[i], groups[i + 1]
            # print(f"TTBB groups[i], groups[i + 1]: {g1} {g2}")
            if re.fullmatch(r"\d{5}", g1) and re.fullmatch(r"\d{5}", g2):
                prefix = g1[2:]  # ใช้หลักสุดท้าย 3 ตัวเป็น prefix เช่น "50123" → "123"
                pressure = self._map_pressure(prefix)
                if pressure is not None:
                    wind_dir = int(g2[:3])
                    wind_speed = int(g2[3:]) * speed_factor
                    result.append(
                        {
                            "hPa./ft.": pressure,
                            "wind_dir": wind_dir,
                            "wind_speed": wind_speed,
                        }
                    )
            # ไม่ว่าจะเข้าเงื่อนไขหรือไม่ ต้องเพิ่ม i เสมอ
            i += 2

        return result

    def _decode_ppaa(self, text: str) -> List[Dict]:
        """
        ถอดรหัสลมจาก PPAA โดยเริ่มจาก groups[3]
        หยุดทันทีเมื่อพบระดับ 200 hPa ในข้อมูล
        """
        groups = text.replace("\n", " ").split()
        speed_factor = self._check_speed_factor(groups[1])
        result = []
        i = 3  # เริ่มจากข้อมูลหลัง PPAA YYGGa4 IIiii

        while i < len(groups):
            g = groups[i]

            # เฉพาะกลุ่ม 55nP1P1 ที่ถูกต้อง ไม่มี /
            if re.fullmatch(r"55\d{3}", g):
                n = int(g[2])  # จำนวนระดับ
                base_code = g[3:]  # P1P1 เช่น "85"
                base_pressure = self._map_pressure(base_code)

                if base_pressure and i + n < len(groups):
                    for j in range(1, n + 1):
                        ddfff = groups[i + j]
                        if re.fullmatch(r"\d{5}", ddfff):
                            pressure = self._nth_pressure(base_pressure, j - 1)
                            wind_dir = int(ddfff[:3])
                            wind_speed = int(ddfff[3:]) * speed_factor
                            result.append(
                                {
                                    "hPa./ft.": pressure,
                                    "wind_dir": wind_dir,
                                    "wind_speed": wind_speed,
                                }
                            )

                            # ✅ หยุดทั้งหมดทันทีถ้าเจอ 200 hPa
                            if pressure == 200:
                                return result

                    i += n + 1
                else:
                    i += 1
            else:
                i += 1

        return result

    def _decode_ppbb(self, text: str) -> List[Dict]:
        groups = text.replace("\n", " ").split()
        if len(groups) < 2:
            return []

        speed_factor = self._check_speed_factor(groups[1])
        result, i = [], 3
        slash_seen_once = False

        def get_level_ft(block: str, h: str) -> Optional[int]:
            table = {
                "90": {"2": 2000, "5": 5000, "7": 7000},
                "91": {"0": 10000, "5": 15000},
                "92": {"0": 20000},
            }
            return table.get(block, {}).get(h)

        while i < len(groups):
            g = groups[i]
            if not re.fullmatch(r"9[\d/]{4}", g):
                i += 1
                continue

            block_group = g[:2]
            height_codes = list(g[2:5])
            slash_count = height_codes.count("/")
            adjust = 4

            for idx, h in enumerate(height_codes):
                level_ft = get_level_ft(block_group, h)
                if not level_ft:
                    continue
                ddfff_index = i + 1 + idx
                if ddfff_index >= len(groups) or not re.fullmatch(
                    r"\d{5}", groups[ddfff_index]
                ):
                    continue
                ddfff = groups[ddfff_index]
                wind_dir = int(ddfff[:3])
                wind_speed = int(ddfff[3:]) * speed_factor
                result.append(
                    {
                        "hPa./ft.": level_ft,
                        "wind_dir": wind_dir,
                        "wind_speed": wind_speed,
                        # "block_group": block_group,
                    }
                )

                if level_ft == 20000:
                    return result

            if block_group == "90" and not slash_seen_once:
                if slash_count > 0:
                    slash_seen_once = True
                    adjust = 4 if slash_count == 1 else 4 - (slash_count - 1)
            elif slash_seen_once:
                adjust = 4 - slash_count

            i += adjust

        return result

    def _map_pressure(self, prefix: str) -> Optional[int]:
        table = {
            "85": 850,
            "70": 700,
            "50": 500,
            "40": 400,
            "30": 300,
            "20": 200,
        }
        return table.get(prefix)

    def _nth_pressure(self, start: int, offset: int) -> int:
        order = [850, 700, 500, 400, 300, 200]
        if start in order:
            idx = order.index(start) + offset
            return order[idx] if idx < len(order) else start
        return start

    def _check_speed_factor(self, group: str) -> int:
        """
        ถ้า YY (วันในกลุ่มแรก) < 50 → ความเร็วเป็น m/s → คูณ 2
        ถ้า ≥ 50 → เป็นนอต → ไม่ต้องคูณ
        """
        try:
            day = int(group[:2])  # ดึง 2 ตัวแรกมาเป็นตัวเลข
            return 2 if day < 50 else 1
        except ValueError:
            return 1  # fallback: ไม่สามารถแปลงได้ → ถือว่าเป็น knots

    def save_decoded_to_json(
        self, decoded: Dict[str, Dict[str, List[Dict]]], time_str: str, date: str
    ):
        """
        บันทึกผลลัพธ์การถอดรหัสลงไฟล์ JSON
        รูปแบบ:
        {
          "2025-03-27": {
            "time": "...",
            "timestamp": "...",
            "43014": { "TTAA": [...], ... }
          }
        }
        """
        try:
            output_path = self.output_json
            timestamp_str = datetime.now().isoformat() + "LST"

            # โหลดข้อมูลเดิม
            #if output_path.exists():
            #    with output_path.open("r", encoding="utf-8") as f:
            #        all_data = json.load(f)
            #else:
            #    all_data = {}

            all_data = {}
            # สร้าง entry สำหรับวันนั้น
            if date not in all_data:
                all_data[date] = {"time": time_str, "timestamp": timestamp_str}

            for station, report in decoded.items():
                all_data[date][station] = {
                    code: report.get(code, "NIL") for code in self.supported_codes
                }

            # เขียนกลับลงไฟล์
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ บันทึกไฟล์พร้อมเวลา: {output_path}")

        except Exception as e:
            logger.error(f"❌ บันทึกไม่สำเร็จ: {e}")
            raise IOError(f"เกิดข้อผิดพลาดในการบันทึกไฟล์ JSON: {e}")

    def _build_timestamp(self, date: str, time_str: str, use_utc=True) -> str:
        try:
            utc_part, lst_part = time_str.split("|")
            utc_time = utc_part.strip().replace("UTC", "").strip()
            lst_time = lst_part.strip().replace("LST", "").strip()
            hhmm = utc_time if use_utc else lst_time
            dt = datetime.strptime(f"{date} {hhmm}", "%Y-%m-%d %H%M")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            logger.info(f"⚠️ แปลง timestamp ไม่สำเร็จ: {e}")
            return f"{date}T00:00:00Z"


# ถอดรหัสทุกสถานีในวันที่ 2025-03-25
# try:
#    decoder = CheckCodeUpperWind()
#    decoded = decoder.decode_all("2025-03-25")
# except Exception as e:
#    print(f"❌ ไม่สามารถบันทึกไฟล์: {e}")
