import requests
import sys
import re
import datetime
import json
import os
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("CheckURLSurface")

# ตั้งค่ารองรับ UTF-8 สำหรับ Windows Terminal
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")


class CheckURLSurface:
    def __init__(self, config_path=None):
        """กำหนดตำแหน่ง config.json (สามารถกำหนดเองได้หรือใช้ default)"""
        if config_path:
            self.config_file_path = config_path
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
            self.config_file_path = os.path.join(script_dir, "../data/json/config.json")

    def _load_config(self):
        """โหลดข้อมูลจากไฟล์ config.json"""
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as file:
                config_data = json.load(file)
            return config_data
        except Exception as e:
            raise FileNotFoundError(f"ไม่สามารถโหลด config.json: {e}")

    def _format_date_components(self, date_str, time_str):
        """แปลงวันที่และเวลาให้เป็นรูปแบบที่ใช้ใน URL"""
        try:
            date_parts = date_str.split("-")
            day = date_parts[2]
            month = datetime.date(1900, int(date_parts[1]), 1).strftime("%b")
            year = date_parts[0][2:4]
            ythai = str(int(date_parts[0]) + 543)
            hour = time_str[:2]
            return day, month, year, ythai, hour
        except Exception as e:
            raise ValueError(f"รูปแบบวันที่หรือเวลาไม่ถูกต้อง: {e}")

    def _build_url(self, template_url, day, month, year, ythai, hour):
        """สร้าง URL จาก template"""
        return (
            template_url.replace("{ythai}", ythai)
            .replace("{day}", day)
            .replace("{month}", month)
            .replace("{year}", year)
            .replace("{time}", hour)
        )

    def _fetch_html(self, url):
        """ดึงข้อมูล HTML จาก URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

    def _extract_synop_text(self, html_text):
        """แยกข้อมูล SYNOP รายสถานีจาก HTML โดยเก็บเฉพาะสถานีล่าสุด"""

        soup = BeautifulSoup(html_text, "html.parser")
        raw_text = soup.get_text(separator="\n", strip=True)

        # ✅ ล้างสัญลักษณ์ตกแต่ง
        cleaned_text = re.sub(r"\*-*-*", "", raw_text)

        # ✅ ตรวจข้อความ NIL
        if "ไม่พบข้อมูลที่ท่านเรียกในขณะนี้" in cleaned_text:
            return None, "ไม่พบข้อมูลที่ท่านเรียกในขณะนี้"

        buffer = ""
        combined_lines = []

        # ✅ รวมหลายบรรทัดของ SYNOP เข้าด้วยกัน
        for line in cleaned_text.splitlines():
            line = line.strip()
            if not line or "NIL" in line:
                continue

            if line[:1].isdigit():
                if "=" in line:
                    buffer += line.replace("=", "").strip()
                    combined_lines.append(buffer.strip() + "=")  # เก็บพร้อมเครื่องหมาย '='
                    buffer = ""
                else:
                    buffer += line + " "

        # ✅ เก็บเฉพาะสถานีล่าสุด (ใช้ station_id เป็น key)
        unique = {}
        for entry in combined_lines:
            if len(entry) >= 5 and entry[:5].isdigit():
                station_id = entry[:5]
                unique[station_id] = entry.strip()  # override ถ้าซ้ำ

        # ✅ แปลงเป็นข้อความเดียว และแทรกบรรทัดใหม่หลังแต่ละรหัส
        formatted_text = "\n".join(unique[k] for k in sorted(unique.keys()))

        return (
            formatted_text.strip(),
            "Complete SYNOPTIC (Surface Synoptic Observations)",
        )

    def urlGetContent(self, time, date, html_text=None):
        """ดึงข้อมูล SYNOP แบบละเอียดตามเวลาและวันที่ที่กำหนด"""
        try:
            config = self._load_config()
            url_template = config["settings"]["url"]
            day, month, year, ythai, hour = self._format_date_components(date, time)
            url = self._build_url(url_template, day, month, year, ythai, hour)
            logger.info(f"✅ URL: {url}")

            if html_text is not None:
                # ถ้ามี HTML ที่ส่งมา ให้ใช้ HTML นั้นแทนการดึงใหม่
                html_text = html_text
            else:
                html_text = self._fetch_html(url)

            result, status = self._extract_synop_text(html_text)
            if result is None:
                logger.warning("❌ ไม่พบข้อมูล SYNOP ใน HTML")
                return "NIL", status

            # ✅ บันทึกแบบ dict[date] = result
            self._save_to_json(result, date)

            return result, status
        except Exception as e:
            logger.error(f"❌ Exception in urlGetContent: {e}")
            return "NIL", str(e)

    def _save_to_json(self, synop_text: str, date: str):
        """บันทึกข้อมูล SYNOP ลงในไฟล์ JSON"""
        # กำหนดตำแหน่งไฟล์ JSON
        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
        json_path = os.path.join(script_dir, "../data/json/synop_url_surface.json")

        # ตรวจสอบว่ามีโฟลเดอร์ data/json หรือไม่
        if not os.path.exists(os.path.dirname(json_path)):
            # ✅ สร้างโฟลเดอร์ถ้ายังไม่มี
            os.makedirs(os.path.dirname(json_path))
            logger.info(f"✅ Created directory: {os.path.dirname(json_path)}")

        try:
            # ✅ บันทึกลง dict ตามวันที่
            existing = {}
            existing[date] = synop_text

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=4, ensure_ascii=False)
            logger.info(f"✅ Saved JSON to {json_path}")

        except Exception as e:
            logger.error(f"❌ Failed to save JSON: {e}")
