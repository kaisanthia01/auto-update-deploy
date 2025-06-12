import os
import sys
import json
import re
import datetime
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("CheckURLSurface2day")

# รองรับ UTF-8
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")


class CheckURLSurface2day:
    def __init__(self, config_path=None):
        """กำหนดตำแหน่ง config.json (สามารถกำหนดเองได้หรือใช้ default)"""
        if config_path:
            self.config_file_path = config_path
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
            self.config_file_path = os.path.join(script_dir, "../data/json/config.json")

        self.config = self._load_config()
        self.base_url = self.config["settings"].get("url", "")

    def _load_config(self):
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ ไม่สามารถโหลด config.json: {e}")
            return {"settings": {"url": ""}}

    def _format_date(self, date_obj, time_str):
        day = f"{date_obj.day:02d}"
        month = date_obj.strftime("%b")
        year = str(date_obj.year)[2:4]
        ythai = str(date_obj.year + 543)
        hour = time_str[:2]
        return day, month, year, ythai, hour

    def _build_url(self, day, month, year, ythai, hour):
        return (
            self.base_url.replace("{ythai}", ythai)
            .replace("{day}", day)
            .replace("{month}", month)
            .replace("{year}", year)
            .replace("{time}", hour)
        )

    def _fetch_html(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            raise ConnectionError(f"❌ ดึงข้อมูลล้มเหลว: {e}")

    def _extract_synop(self, raw_text):
        if "ไม่พบข้อมูลที่ท่านเรียกในขณะนี้" in raw_text:
            return "NIL"

        raw_text = re.sub(r"\*-*-*", "", raw_text)
        lines = []
        buffer = ""

        for line in raw_text.splitlines():
            if "NIL" in line:
                continue
            if line[:1].isdigit():
                if "=" in line:
                    buffer += line.strip()
                    lines.append(buffer)
                    buffer = ""
                else:
                    buffer += line.strip() + " "

        # ✅ เก็บเฉพาะสถานีล่าสุด (override ด้วย station_id)
        unique = {}
        for entry in lines:
            if len(entry) >= 5 and entry[:5].isdigit():
                station_id = entry[:5]
                unique[station_id] = entry  # override ถ้าซ้ำ

        return "\n".join(unique.values())

    def urlGetContent(
        self, time_str: str, date_str: str, html_text: str = None, save=True
    ):
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return {}, "❌ รูปแบบวันที่ไม่ถูกต้อง (เช่น 2025-03-25)"

        date_list = [date_obj - datetime.timedelta(days=1), date_obj]
        result = {}

        for d in date_list:
            try:
                day, month, year, ythai, hour = self._format_date(d, time_str)
                url = self._build_url(day, month, year, ythai, hour)
                logger.info(f"🔗 URL: {url}")

                # ✅ ใช้ html_text เฉพาะกับวันที่ตรงกับ date_str
                if html_text is not None and d == date_obj:
                    html = html_text
                    logger.info("📄 Using provided HTML content for target date.")
                else:
                    html = self._fetch_html(url)

                synop = self._extract_synop(html)
                result[d.strftime("%Y-%m-%d")] = synop if synop else "NIL"

            except Exception as e:
                result[d.strftime("%Y-%m-%d")] = f"NIL ({e})"

        if all(v.startswith("NIL") for v in result.values()):
            logger.error("❌ ไม่พบข้อมูลทั้ง 2 วัน")
            return result, "❌ ไม่พบข้อมูลทั้ง 2 วัน"

        if save:
            self.save_json(result)

        return result, "Complete SYNOPTIC (Surface Synoptic Observations)"

    def save_json(self, data: list):
        # กำหนดตำแหน่งไฟล์ JSON
        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
        output_path = os.path.join(script_dir, "../data/json/synop_url_surface2day.json")

        # ตรวจสอบว่ามีโฟลเดอร์ data/json หรือไม่
        if not os.path.exists(os.path.dirname(output_path)):
            # ✅ สร้างโฟลเดอร์ถ้ายังไม่มี
            os.makedirs(os.path.dirname(output_path))
            logger.info(f"✅ Created directory: {os.path.dirname(output_path)}")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"✅ บันทึกไฟล์แล้ว: {output_path}")
        except Exception as e:
            logger.error(f"❌ ไม่สามารถบันทึกไฟล์: {e}")
