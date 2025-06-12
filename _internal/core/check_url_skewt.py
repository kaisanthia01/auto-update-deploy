import requests
import sys
import re
import datetime
import json
from pathlib import Path
from bs4 import BeautifulSoup
import os
import logging

logger = logging.getLogger("CheckURLSkewT")

# รองรับ UTF-8 ใน Windows Terminal
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")


class CheckURLSkewT:
    def __init__(self, config_path=None):
        """กำหนดตำแหน่ง config.json (สามารถกำหนดเองได้หรือใช้ default)"""
        script_dir = Path(__file__).resolve().parent  # ✅ ใช้ Path
        if config_path:
            self.config_file_path = Path(config_path)
        else:
            self.config_file_path = script_dir / "../data/json/config.json"

    def _load_config(self):
        if not self.config_file_path.exists():
            raise FileNotFoundError(f"ไม่พบ config.json ที่: {self.config_file_path}")
        with self.config_file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _format_date(self, date_str, time_str):
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return {
                "day": dt.strftime("%d"),
                "month": dt.strftime("%b"),
                "year": dt.strftime("%y"),
                "ythai": str(dt.year + 543),
                "time": time_str[:2],
            }
        except Exception as e:
            raise ValueError(f"รูปแบบวันที่ไม่ถูกต้อง: {e}")

    def _build_url(self, template_url, date_parts):
        for key, val in date_parts.items():
            template_url = template_url.replace(f"{{{key}}}", val)
        return template_url

    def _fetch_html(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.RequestException as e:
            raise ConnectionError(f"ดึงข้อมูลล้มเหลว: {e}")

    def _extract_wind_text(self, html_text, station_filter=None):
        soup = BeautifulSoup(html_text, "html.parser")
        raw_text = soup.get_text(separator="\n", strip=True)

        if "ไม่พบข้อมูลที่ท่านเรียกในขณะนี้" in raw_text:
            return None, "ไม่พบข้อมูลที่ท่านเรียกในขณะนี้"

        cleaned = re.sub(r"\*-+\*?", "", raw_text)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        full_text = " ".join(lines)
        full_text = re.sub(r"=", "=\n", full_text)
        full_text = re.sub(r"\*-*-*", "", full_text)
        lines = full_text.splitlines()

        data_by_station = {}

        for line in lines:
            for code_type in ["TTAA", "TTBB", "PPAA", "PPBB"]:
                if code_type in line:
                    start = line.find(code_type)
                    end = line.find("=", start)
                    if end != -1:
                        raw = line[start : end + 1].strip()
                        parts = raw.split()
                        if len(parts) >= 3:
                            station = parts[2]
                            if station_filter and station not in station_filter:
                                continue  # ✅ ข้ามสถานีที่ไม่ได้กรองไว้

                            if station not in data_by_station:
                                data_by_station[station] = {}

                            raw = " ".join(raw.split())
                            raw = re.sub(r"\=", "", raw)
                            data_by_station[station][code_type] = raw

        if not data_by_station:
            return None, "ไม่พบรหัส TTAA/PPAA/PPBB ที่สามารถแยกได้"

        return (
            data_by_station,
            f"พบข้อมูล {len(data_by_station)} สถานี จาก Upper-Air Report",
        )

    def _save_to_json(self, data_by_station: dict, date: str):
        """
        บันทึกข้อมูลหลายสถานี ครบ TTAA/TTBB/PPAA/PPBB
        """
        script_dir = Path(__file__).resolve().parent
        output_path = script_dir / "../data/json/synop_url_skewt.json"
        output_path = output_path.resolve()

        # สร้างโฟลเดอร์หากยังไม่มี
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Directory OK: {output_path.parent}")

        try:
            all_data = {date: {}}
            for station, report_dict in data_by_station.items():
                all_data[date][station] = {
                    code_type: report_dict.get(code_type, "NIL")
                    for code_type in ["TTAA", "TTBB", "PPAA", "PPBB"]
                }

            with output_path.open("w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ บันทึกไฟล์ใหม่แล้ว: {output_path}")

        except Exception as e:
            logger.error(f"❌ บันทึกไม่สำเร็จ: {e}")
            raise IOError(f"เกิดข้อผิดพลาดในการบันทึกไฟล์ JSON: {e}")

    def urlGetContent(
        self,
        time: str,
        date: str,
        station_filter: list[str] = None,
        html_text: str = None,
    ):
        try:
            config = self._load_config()
            url_template = config["settings"]["url_wind"]
            date_parts = self._format_date(date, time)
            url = self._build_url(url_template, date_parts)
            logger.info(f"✅ URL: {url}")

            if html_text is not None:
                # ถ้ามี HTML ที่ส่งมา ให้ใช้ HTML นั้นแทนการดึงใหม่
                html = html_text
            else:
                html = self._fetch_html(url)

            result, status = self._extract_wind_text(html, station_filter)

            if not result:
                logger.warning("❌ ไม่พบข้อมูล SYNOP ใน HTML")
                return "NIL", status

            self._save_to_json(result, date)
            return result, f"{status} ({len(result)} สถานี)"
        except Exception as e:
            logger.error(f"❌ Exception in urlGetContent: {e}")
            return "NIL", f"ERROR: {e}"


## ทดสอบดึงข้อมูลของวันที่ 2025-03-25 เวลา 00 UTC
# checker = CheckURLSkewT()
# result, status = checker.urlGetContent(time="00", date="2025-03-28", station_filter="48407")
#
## แสดงผลลัพธ์
# print(status)
# if result != "NIL":
#   for station, report in result.items():
#       print(f"\n📍 สถานี: {station}")
#       for code_type, text in report.items():
#           print(f"  ➤ {code_type}: {text}")
